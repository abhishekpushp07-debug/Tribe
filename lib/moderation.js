/**
 * Tribe — AI Content Moderation Service
 * 
 * Uses OpenAI Moderation API to automatically screen user-generated content.
 * 
 * Flow:
 * 1. User creates content (post, comment, etc.)
 * 2. Text is sent to OpenAI moderation endpoint
 * 3. If flagged → content goes to HELD state, enters moderation queue
 * 4. If clean → content published normally
 * 5. Fallback: if API fails → manual keyword filter + auto-publish with audit flag
 * 
 * Categories checked:
 * - harassment, hate, self-harm, sexual, violence, illicit
 * 
 * Thresholds:
 * - AUTO_REJECT: score >= 0.85 → auto-hold, admin must review
 * - ESCALATE: score >= 0.50 → auto-hold, flagged for review
 * - PASS: score < 0.50 → auto-publish
 */

import OpenAI from 'openai'

const EMERGENT_KEY = process.env.EMERGENT_LLM_KEY

// Confidence thresholds
const THRESHOLDS = {
  AUTO_REJECT: 0.85,  // Very high confidence → auto-hold
  ESCALATE: 0.50,     // Moderate confidence → hold for review
}

// Critical categories that should never pass
const CRITICAL_CATEGORIES = [
  'sexual/minors',
  'self-harm/instructions',
  'hate/threatening',
  'harassment/threatening',
  'illicit/violent',
]

// Keyword-based fallback filter (when API is unavailable)
const FALLBACK_KEYWORDS = [
  'kill yourself', 'kys', 'bomb threat', 'school shooting',
  'child porn', 'csam', 'cp links',
  'rape threat', 'death threat',
]

let openaiClient = null

function getClient() {
  if (!openaiClient && EMERGENT_KEY) {
    openaiClient = new OpenAI({ apiKey: EMERGENT_KEY })
  }
  return openaiClient
}

/**
 * Moderate text content using OpenAI Moderation API
 * 
 * @param {string} text - Content to moderate
 * @returns {object} { flagged, action, categories, scores, model, error }
 */
export async function moderateContent(text) {
  if (!text || text.trim().length === 0) {
    return { flagged: false, action: 'PASS', categories: [], scores: {}, model: 'none' }
  }

  const client = getClient()

  // Try OpenAI moderation API
  if (client) {
    try {
      const response = await client.moderations.create({
        input: text,
        model: 'omni-moderation-latest',
      })

      const result = response.results[0]
      const scores = result.category_scores
      const categories = result.categories

      // Find flagged categories with scores
      const flaggedCategories = []
      const categoryScores = {}

      for (const [category, isFlagged] of Object.entries(categories)) {
        const normalizedCategory = category.replace(/_/g, '/')
        const score = scores[category] || 0
        categoryScores[normalizedCategory] = score

        if (isFlagged || score >= THRESHOLDS.ESCALATE) {
          flaggedCategories.push({ category: normalizedCategory, score })
        }
      }

      // Determine action
      let action = 'PASS'
      let hasCritical = false

      for (const fc of flaggedCategories) {
        if (CRITICAL_CATEGORIES.includes(fc.category)) {
          hasCritical = true
        }
        if (fc.score >= THRESHOLDS.AUTO_REJECT) {
          action = 'AUTO_REJECT'
          break
        }
        if (fc.score >= THRESHOLDS.ESCALATE) {
          action = 'ESCALATE'
        }
      }

      // Critical categories always auto-reject regardless of score
      if (hasCritical && action !== 'AUTO_REJECT') {
        action = 'AUTO_REJECT'
      }

      return {
        flagged: result.flagged || action !== 'PASS',
        action,
        categories: flaggedCategories.map(fc => fc.category),
        scores: categoryScores,
        model: response.model || 'omni-moderation-latest',
        error: null,
      }
    } catch (err) {
      console.error('[Moderation] OpenAI API error, falling back to keyword filter:', err.message)
      // Fall through to keyword filter
    }
  }

  // Fallback: keyword-based filter
  return keywordFilter(text)
}

function keywordFilter(text) {
  const lower = text.toLowerCase()
  const matched = FALLBACK_KEYWORDS.filter(kw => lower.includes(kw))

  if (matched.length > 0) {
    return {
      flagged: true,
      action: 'ESCALATE',
      categories: ['keyword_match'],
      scores: { keyword_match: 0.7 },
      model: 'keyword_fallback',
      error: 'OpenAI unavailable, used keyword filter',
      matchedKeywords: matched,
    }
  }

  return {
    flagged: false,
    action: 'PASS',
    categories: [],
    scores: {},
    model: 'keyword_fallback',
    error: 'OpenAI unavailable, used keyword filter',
  }
}

/**
 * Get moderation thresholds and configuration
 */
export function getModerationConfig() {
  return {
    thresholds: THRESHOLDS,
    criticalCategories: CRITICAL_CATEGORIES,
    fallbackKeywords: FALLBACK_KEYWORDS.length,
    apiAvailable: !!getClient(),
    model: 'omni-moderation-latest',
    categories: [
      'harassment', 'harassment/threatening',
      'hate', 'hate/threatening',
      'illicit', 'illicit/violent',
      'self-harm', 'self-harm/instructions', 'self-harm/intent',
      'sexual', 'sexual/minors',
      'violence', 'violence/graphic',
    ],
  }
}
