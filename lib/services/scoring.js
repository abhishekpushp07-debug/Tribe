/**
 * Tribe Scoring Service
 *
 * Single source of truth for all tribe engagement scoring.
 * Handles: leaderboard computation, tiered viral bonuses,
 * anti-cheat upload caps, and per-period caching.
 *
 * Extracted from tribes.js handler to enforce separation of concerns.
 */

// ========== SCORING RULES (immutable, version-tagged) ==========
const SCORING_VERSION = 'v3'
const SCORING_WEIGHTS = {
  upload: 100,        // per post/reel/story
  like: 10,           // per like received
  comment: 20,        // per comment received
  share: 50,          // per share received
  storyReaction: 15,  // per story reaction received
  storyReply: 25,     // per story reply received
}

// Tiered viral bonuses — each tier is cumulative on ONE reel
// A reel with 12K likes earns: 1000 + 3000 + 5000 = 9000 bonus
const VIRAL_TIERS = [
  { threshold: 1000,  bonus: 1000,  label: 'viral' },
  { threshold: 5000,  bonus: 3000,  label: 'super_viral' },
  { threshold: 10000, bonus: 5000,  label: 'mega_viral' },
]

// Anti-cheat caps per period
const UPLOAD_CAPS = { '7d': 350, '30d': 1500, '90d': 4500, all: 50000 }

// ========== CACHE ==========
const CACHE_TTL_MS = 10 * 60 * 1000 // 10 minutes
const cache = {}

function getCached(key) {
  const entry = cache[key]
  if (entry && (Date.now() - entry.ts) < CACHE_TTL_MS) return entry.data
  return null
}

function setCache(key, data) {
  cache[key] = { data, ts: Date.now() }
}

export function invalidateLeaderboardCache() {
  for (const key of Object.keys(cache)) delete cache[key]
}

// ========== CORE ==========

/**
 * Compute the full tribe leaderboard.
 * Returns sorted, ranked array of tribe entries with metrics + score breakdown.
 */
export async function computeLeaderboard(db, { period = '30d' } = {}) {
  const cacheKey = `lb_${period}_${SCORING_VERSION}`
  const cached = getCached(cacheKey)
  if (cached) return cached

  const now = new Date()
  let since = null
  if (period === '7d') since = new Date(now.getTime() - 7 * 86400000)
  else if (period === '30d') since = new Date(now.getTime() - 30 * 86400000)
  else if (period === '90d') since = new Date(now.getTime() - 90 * 86400000)

  const tribes = await db.collection('tribes').find({ isActive: true }).toArray()
  if (!tribes.length) return { items: [], period, scoringVersion: SCORING_VERSION }

  // 1. Fetch all non-banned tribe members — single query
  const allMembers = await db.collection('users')
    .find(
      { tribeId: { $ne: null }, isBanned: { $ne: true } },
      { projection: { _id: 0, id: 1, tribeId: 1 } }
    )
    .toArray()

  const tribeMemberMap = {}
  for (const m of allMembers) {
    if (!tribeMemberMap[m.tribeId]) tribeMemberMap[m.tribeId] = []
    tribeMemberMap[m.tribeId].push(m.id)
  }

  const dateFilter = since ? { createdAt: { $gte: since } } : {}

  // 2. Six aggregation queries total (across ALL tribes, not per-tribe)
  const [
    postsByUser, reelsByUser, storiesByUser,
    storyReactionsByUser, storyRepliesByUser,
    viralReelsByUser,
  ] = await Promise.all([
    db.collection('content_items').aggregate([
      { $match: { isDeleted: { $ne: true }, ...dateFilter } },
      { $group: {
        _id: '$authorId',
        count: { $sum: 1 },
        likes: { $sum: { $ifNull: ['$likeCount', 0] } },
        comments: { $sum: { $ifNull: ['$commentCount', 0] } },
        shares: { $sum: { $ifNull: ['$shareCount', 0] } },
      }},
    ]).toArray(),

    db.collection('reels').aggregate([
      { $match: { isDeleted: { $ne: true }, ...dateFilter } },
      { $group: {
        _id: '$creatorId',
        count: { $sum: 1 },
        likes: { $sum: { $ifNull: ['$likeCount', 0] } },
        comments: { $sum: { $ifNull: ['$commentCount', 0] } },
        shares: { $sum: { $ifNull: ['$shareCount', 0] } },
      }},
    ]).toArray(),

    db.collection('stories').aggregate([
      { $match: { isDeleted: { $ne: true }, ...dateFilter } },
      { $group: { _id: '$creatorId', count: { $sum: 1 } } },
    ]).toArray(),

    db.collection('story_reactions').aggregate([
      { $match: { ...dateFilter } },
      { $lookup: { from: 'stories', localField: 'storyId', foreignField: 'id', as: 's' } },
      { $unwind: '$s' },
      { $group: { _id: '$s.creatorId', count: { $sum: 1 } } },
    ]).toArray(),

    db.collection('story_replies').aggregate([
      { $match: { ...dateFilter } },
      { $lookup: { from: 'stories', localField: 'storyId', foreignField: 'id', as: 's' } },
      { $unwind: '$s' },
      { $group: { _id: '$s.creatorId', count: { $sum: 1 } } },
    ]).toArray(),

    // Per-reel like counts for tiered viral bonuses
    db.collection('reels').aggregate([
      { $match: { isDeleted: { $ne: true }, likeCount: { $gte: VIRAL_TIERS[0].threshold }, ...dateFilter } },
      { $project: { _id: 0, creatorId: 1, likeCount: 1 } },
    ]).toArray(),
  ])

  // 3. Build userId lookup maps
  const postMap = Object.fromEntries(postsByUser.map(p => [p._id, p]))
  const reelMap = Object.fromEntries(reelsByUser.map(r => [r._id, r]))
  const storyMap = Object.fromEntries(storiesByUser.map(s => [s._id, s]))
  const storyReactionMap = Object.fromEntries(storyReactionsByUser.map(s => [s._id, s.count]))
  const storyReplyMap = Object.fromEntries(storyRepliesByUser.map(s => [s._id, s.count]))

  // Build per-user viral reel data (for tiered bonuses)
  const viralByUser = {}
  for (const reel of viralReelsByUser) {
    if (!viralByUser[reel.creatorId]) viralByUser[reel.creatorId] = []
    viralByUser[reel.creatorId].push(reel.likeCount)
  }

  const uploadCap = UPLOAD_CAPS[period] || UPLOAD_CAPS['30d']

  // 4. Score each tribe
  const leaderboard = tribes.map(tribe => {
    const memberIds = tribeMemberMap[tribe.id] || []
    const empty = buildEmptyEntry(tribe)
    if (memberIds.length === 0) return empty

    let posts = 0, reels = 0, stories = 0
    let likes = 0, comments = 0, shares = 0
    let storyReactions = 0, storyReplies = 0
    let viralBonus = 0
    let viralCounts = { tier1: 0, tier2: 0, tier3: 0 }

    for (const uid of memberIds) {
      const p = postMap[uid]
      const r = reelMap[uid]
      const s = storyMap[uid]

      posts += p?.count || 0
      reels += r?.count || 0
      stories += s?.count || 0
      likes += (p?.likes || 0) + (r?.likes || 0)
      comments += (p?.comments || 0) + (r?.comments || 0)
      shares += (p?.shares || 0) + (r?.shares || 0)
      storyReactions += storyReactionMap[uid] || 0
      storyReplies += storyReplyMap[uid] || 0

      // Tiered viral bonus — computed PER REEL, not per user
      const userViralReels = viralByUser[uid] || []
      for (const likeCount of userViralReels) {
        for (const tier of VIRAL_TIERS) {
          if (likeCount >= tier.threshold) {
            viralBonus += tier.bonus
            if (tier.threshold === 1000) viralCounts.tier1++
            else if (tier.threshold === 5000) viralCounts.tier2++
            else if (tier.threshold === 10000) viralCounts.tier3++
          }
        }
      }
    }

    // Apply anti-cheat upload cap (total tribe cap = members × per-user cap)
    const totalUploads = posts + reels + stories
    const cappedUploads = Math.min(totalUploads, memberIds.length * uploadCap)

    const uploadPoints = cappedUploads * SCORING_WEIGHTS.upload
    const likePoints = likes * SCORING_WEIGHTS.like
    const commentPoints = comments * SCORING_WEIGHTS.comment
    const sharePoints = shares * SCORING_WEIGHTS.share
    const storyEngagementPoints =
      (storyReactions * SCORING_WEIGHTS.storyReaction) +
      (storyReplies * SCORING_WEIGHTS.storyReply)

    const engagementScore = uploadPoints + likePoints + commentPoints + sharePoints + storyEngagementPoints + viralBonus

    return {
      tribeId: tribe.id,
      tribeCode: tribe.tribeCode,
      tribeName: tribe.tribeName,
      primaryColor: tribe.primaryColor,
      secondaryColor: tribe.secondaryColor,
      animalIcon: tribe.animalIcon,
      quote: tribe.quote,
      membersCount: memberIds.length,
      metrics: {
        uploads: totalUploads, posts, reels, stories,
        likesReceived: likes, commentsReceived: comments, sharesReceived: shares,
        storyReactions, storyReplies,
        viralReels: viralCounts,
      },
      scoreBreakdown: {
        uploadPoints, likePoints, commentPoints, sharePoints,
        storyEngagementPoints, viralBonus,
      },
      engagementScore,
    }
  })

  // 5. Rank
  leaderboard.sort((a, b) => b.engagementScore - a.engagementScore)
  leaderboard.forEach((entry, i) => { entry.rank = i + 1 })

  const result = {
    items: leaderboard,
    leaderboard,
    count: leaderboard.length,
    period,
    scoringVersion: SCORING_VERSION,
    scoringRules: {
      ...SCORING_WEIGHTS,
      viralTiers: VIRAL_TIERS,
      uploadCapPerUser: uploadCap,
    },
    generatedAt: now.toISOString(),
  }

  setCache(cacheKey, result)
  return result
}

function buildEmptyEntry(tribe) {
  return {
    tribeId: tribe.id, tribeCode: tribe.tribeCode, tribeName: tribe.tribeName,
    primaryColor: tribe.primaryColor, secondaryColor: tribe.secondaryColor,
    animalIcon: tribe.animalIcon, quote: tribe.quote,
    membersCount: 0,
    metrics: { uploads: 0, posts: 0, reels: 0, stories: 0, likesReceived: 0, commentsReceived: 0, sharesReceived: 0, storyReactions: 0, storyReplies: 0, viralReels: { tier1: 0, tier2: 0, tier3: 0 } },
    scoreBreakdown: { uploadPoints: 0, likePoints: 0, commentPoints: 0, sharePoints: 0, storyEngagementPoints: 0, viralBonus: 0 },
    engagementScore: 0,
  }
}
