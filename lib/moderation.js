/**
 * Tribe — AI Content Moderation Client
 * 
 * Calls the Python moderation microservice (GPT-4o-mini via Emergent).
 * Falls back to keyword filter if service is unavailable.
 */

const MODERATION_URL = process.env.MODERATION_SERVICE_URL || 'http://localhost:8002'

const FALLBACK_KEYWORDS = [
  'kill yourself', 'kys', 'bomb threat', 'school shooting',
  'child porn', 'csam', 'cp links',
  'rape threat', 'death threat', 'suicide', 'self harm',
]

export async function moderateContent(text) {
  if (!text || text.trim().length === 0) {
    return { flagged: false, action: 'PASS', categories: [], scores: {}, model: 'none', error: null }
  }

  try {
    const controller = new AbortController()
    const timeout = setTimeout(() => controller.abort(), 10000)

    const res = await fetch(`${MODERATION_URL}/moderate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
      signal: controller.signal,
    })
    clearTimeout(timeout)

    if (res.ok) {
      return await res.json()
    }
    throw new Error(`Moderation service returned ${res.status}`)
  } catch (err) {
    console.error('[Moderation] Service error, using keyword fallback:', err.message)
    return keywordFallback(text, err.message)
  }
}

function keywordFallback(text, error) {
  const lower = text.toLowerCase()
  const matched = FALLBACK_KEYWORDS.filter(kw => lower.includes(kw))

  if (matched.length > 0) {
    return {
      flagged: true,
      action: 'ESCALATE',
      categories: ['keyword_match'],
      scores: { keyword_match: 0.7 },
      model: 'keyword_fallback',
      error: `AI unavailable: ${error}`,
    }
  }

  return {
    flagged: false,
    action: 'PASS',
    categories: [],
    scores: {},
    model: 'keyword_fallback',
    error: `AI unavailable: ${error}`,
  }
}

export async function getModerationConfig() {
  try {
    const res = await fetch(`${MODERATION_URL}/config`, { signal: AbortSignal.timeout(3000) })
    if (res.ok) return await res.json()
  } catch {}

  return {
    thresholds: { AUTO_REJECT: 0.85, ESCALATE: 0.50 },
    criticalCategories: ['sexual_minors', 'self_harm'],
    fallbackKeywords: FALLBACK_KEYWORDS.length,
    apiAvailable: false,
    model: 'keyword_fallback (service unavailable)',
    categories: ['harassment', 'hate', 'self_harm', 'sexual', 'sexual_minors', 'violence', 'spam', 'impersonation'],
  }
}
