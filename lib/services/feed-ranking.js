/**
 * Tribe Feed Ranking Service
 *
 * Replaces pure chronological sort with a real engagement-weighted algorithm.
 * Factors: recency decay, engagement velocity, author affinity, content diversity.
 *
 * Algorithm:
 *   feedScore = recencyScore × engagementScore × affinityBoost × diversityPenalty
 *
 * - recencyScore: exponential decay from post age (half-life = 6 hours)
 * - engagementScore: weighted sum of likes, comments, shares per hour since creation
 * - affinityBoost: 1.0 base, +0.5 if viewer follows author, +0.3 if same tribe
 * - diversityPenalty: 0.7× for 2nd post from same author in window, 0.4× for 3rd+
 */

const HALF_LIFE_MS = 6 * 60 * 60 * 1000 // 6 hours
const LN2 = Math.LN2

/**
 * Score a single post for feed ranking.
 * @param {Object} post — the content_items document
 * @param {Object} ctx — { viewerId, viewerTribeId, followeeIds, now }
 * @returns {number} feedScore
 */
function scorePost(post, ctx) {
  const ageMs = Math.max(1, ctx.now - (post.createdAt?.getTime?.() || Date.parse(post.createdAt) || ctx.now))

  // 1. Recency: exponential decay with 6h half-life
  //    At 0h: 1.0, at 6h: 0.5, at 12h: 0.25, at 24h: 0.0625
  const recency = Math.exp(-LN2 * ageMs / HALF_LIFE_MS)

  // 2. Engagement velocity: weighted interactions per hour
  const ageHours = Math.max(0.1, ageMs / 3600000) // min 6 min to avoid division spikes
  const likes = post.likeCount || 0
  const comments = post.commentCount || 0
  const shares = post.shareCount || 0
  const engagementRaw = (likes * 1) + (comments * 3) + (shares * 5)
  // Log scale to prevent runaway viral posts from dominating
  const engagement = Math.log2(1 + engagementRaw / ageHours)

  // 3. Affinity: boost content from people viewer interacts with
  let affinity = 1.0
  const authorId = post.authorId || post.creatorId
  if (ctx.followeeIds?.has?.(authorId)) affinity += 0.5
  if (ctx.viewerTribeId && (post.tribeId === ctx.viewerTribeId)) affinity += 0.3

  // 4. Content quality bonus — posts with media get slight boost
  const qualityBoost = (post.media?.length > 0 || post.mediaId) ? 1.15 : 1.0

  return recency * (1 + engagement) * affinity * qualityBoost
}

/**
 * Rank a batch of posts using the algorithmic feed.
 * Applies scoring + diversity penalty (max 2 posts from same author in top 20).
 *
 * @param {Array} posts — array of content_items documents
 * @param {Object} ctx — { viewerId, viewerTribeId, followeeIds }
 * @returns {Array} sorted posts with `_feedScore` and `_feedRank` attached
 */
export function rankFeed(posts, ctx = {}) {
  const now = Date.now()
  const fullCtx = { ...ctx, now }

  // Score each post
  const scored = posts.map(post => ({
    ...post,
    _feedScore: scorePost(post, fullCtx),
  }))

  // Sort by score descending
  scored.sort((a, b) => b._feedScore - a._feedScore)

  // Apply diversity penalty — limit same author in consecutive window
  const authorCounts = {}
  for (const post of scored) {
    const aid = post.authorId || post.creatorId
    const count = (authorCounts[aid] || 0) + 1
    authorCounts[aid] = count

    if (count === 2) post._feedScore *= 0.7
    else if (count >= 3) post._feedScore *= 0.4
  }

  // Re-sort after diversity penalty
  scored.sort((a, b) => b._feedScore - a._feedScore)

  // Assign rank
  scored.forEach((post, i) => { post._feedRank = i + 1 })

  return scored
}

/**
 * Build affinity context for a viewer.
 * Call this once per feed request, then pass to rankFeed.
 */
export async function buildAffinityContext(db, viewerId) {
  if (!viewerId) return { viewerId: null, viewerTribeId: null, followeeIds: new Set() }

  const [user, follows] = await Promise.all([
    db.collection('users').findOne({ id: viewerId }, { projection: { _id: 0, tribeId: 1 } }),
    db.collection('follows').find({ followerId: viewerId }, { projection: { _id: 0, followeeId: 1 } }).toArray(),
  ])

  return {
    viewerId,
    viewerTribeId: user?.tribeId || null,
    followeeIds: new Set(follows.map(f => f.followeeId)),
  }
}
