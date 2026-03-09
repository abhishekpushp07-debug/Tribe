import { v4 as uuidv4 } from 'uuid'
import { requireAuth, writeAudit, parsePagination } from '../auth-utils.js'
import { ErrorCode } from '../constants.js'
import { invalidateOnEvent } from '../cache.js'

/**
 * House Points System
 * 
 * Points are awarded for actions (posting, getting likes, etc.) and tracked
 * in the house_ledger collection. Each house's totalPoints is kept in the
 * houses collection for fast leaderboard reads.
 * 
 * Earning mechanics:
 *   POST_CREATED  → +5 points
 *   REEL_CREATED  → +10 points
 *   LIKE_RECEIVED → +2 points
 *   COMMENT_RECEIVED → +3 points
 *   FOLLOW_GAINED → +1 point
 *   ADMIN_AWARD   → variable (manual)
 *   ADMIN_DEDUCT  → variable (manual, negative)
 */

const POINT_VALUES = {
  POST_CREATED: 5,
  REEL_CREATED: 10,
  STORY_CREATED: 3,
  LIKE_RECEIVED: 2,
  COMMENT_RECEIVED: 3,
  FOLLOW_GAINED: 1,
  ADMIN_AWARD: 0,   // variable
  ADMIN_DEDUCT: 0,  // variable
}

// Award points (internal helper, also exported for use by other handlers)
export async function awardHousePoints(db, userId, houseId, reason, points, context = {}) {
  if (!houseId || !points) return null

  // Idempotency: generate a deterministic key from userId + reason + context
  const idempotencyKey = `${userId}:${reason}:${context.contentId || context.adminId || ''}`

  // Check for duplicate award within last 5 seconds (race-condition window)
  const recent = await db.collection('house_ledger').findOne({
    idempotencyKey,
    createdAt: { $gt: new Date(Date.now() - 5000) },
  })
  if (recent) return null // already awarded

  const entry = {
    id: uuidv4(),
    userId,
    houseId,
    reason,
    points,
    context,
    idempotencyKey,
    createdAt: new Date(),
  }

  await db.collection('house_ledger').insertOne(entry)
  await db.collection('houses').updateOne(
    { id: houseId },
    { $inc: { totalPoints: points } }
  )

  await invalidateOnEvent('HOUSE_POINTS_CHANGED')

  const { _id, ...clean } = entry
  return clean
}

export async function handleHousePoints(path, method, request, db) {
  const route = path.join('/')

  // ========================
  // GET /house-points/config — Point value config
  // ========================
  if (route === 'house-points/config' && method === 'GET') {
    return { data: { pointValues: POINT_VALUES } }
  }

  // ========================
  // GET /house-points/ledger — User's own point history
  // ========================
  if (route === 'house-points/ledger' && method === 'GET') {
    const user = await requireAuth(request, db)
    const url = new URL(request.url)
    const { limit, cursor } = parsePagination(url)

    const query = { userId: user.id }
    if (cursor) query.createdAt = { $lt: new Date(cursor) }

    const entries = await db.collection('house_ledger')
      .find(query)
      .sort({ createdAt: -1 })
      .limit(limit + 1)
      .toArray()

    const hasMore = entries.length > limit
    const items = entries.slice(0, limit).map(e => { const { _id, ...rest } = e; return rest })

    // Calculate user's total contribution
    const totalPoints = await db.collection('house_ledger')
      .aggregate([
        { $match: { userId: user.id } },
        { $group: { _id: null, total: { $sum: '$points' } } },
      ])
      .toArray()

    return {
      data: {
        items,
        entries: items,
        totalPoints: totalPoints[0]?.total || 0,
        pagination: {
          nextCursor: hasMore ? items[items.length - 1].createdAt : null,
          hasMore,
        },
        nextCursor: hasMore ? items[items.length - 1].createdAt : null,
      },
    }
  }

  // ========================
  // GET /house-points/house/:houseId — House point history
  // ========================
  if (path[0] === 'house-points' && path[1] === 'house' && path.length === 3 && method === 'GET') {
    const houseId = path[2]
    const url = new URL(request.url)
    const { limit, cursor } = parsePagination(url)

    const query = { houseId }
    if (cursor) query.createdAt = { $lt: new Date(cursor) }

    const entries = await db.collection('house_ledger')
      .find(query)
      .sort({ createdAt: -1 })
      .limit(limit + 1)
      .toArray()

    const hasMore = entries.length > limit
    const items = entries.slice(0, limit).map(e => { const { _id, ...rest } = e; return rest })

    // Top contributors for this house
    const topContributors = await db.collection('house_ledger')
      .aggregate([
        { $match: { houseId } },
        { $group: { _id: '$userId', totalPoints: { $sum: '$points' } } },
        { $sort: { totalPoints: -1 } },
        { $limit: 10 },
      ])
      .toArray()

    // Enrich contributors with user info
    const userIds = topContributors.map(c => c._id)
    const users = await db.collection('users').find({ id: { $in: userIds } }).toArray()
    const userMap = Object.fromEntries(users.map(u => {
      const { _id, pinHash, pinSalt, ...safe } = u
      return [u.id, safe]
    }))

    const enrichedContributors = topContributors.map(c => ({
      userId: c._id,
      totalPoints: c.totalPoints,
      user: userMap[c._id] || null,
    }))

    return {
      data: {
        items,
        entries: items,
        topContributors: enrichedContributors,
        pagination: {
          nextCursor: hasMore ? items[items.length - 1].createdAt : null,
          hasMore,
        },
        nextCursor: hasMore ? items[items.length - 1].createdAt : null,
      },
    }
  }

  // ========================
  // POST /house-points/award — Admin awards points
  // ========================
  if (route === 'house-points/award' && method === 'POST') {
    const user = await requireAuth(request, db)
    if (!['ADMIN', 'SUPER_ADMIN'].includes(user.role)) {
      return { error: 'Admin access required', code: ErrorCode.FORBIDDEN, status: 403 }
    }

    const body = await request.json()
    const { userId, points, reason } = body

    if (!userId || !points || !reason) {
      return { error: 'userId, points, and reason are required', code: ErrorCode.VALIDATION, status: 400 }
    }

    const targetUser = await db.collection('users').findOne({ id: userId })
    if (!targetUser) return { error: 'User not found', code: ErrorCode.NOT_FOUND, status: 404 }
    if (!targetUser.houseId) return { error: 'User has no house assigned', code: ErrorCode.VALIDATION, status: 400 }

    const entry = await awardHousePoints(db, userId, targetUser.houseId, points > 0 ? 'ADMIN_AWARD' : 'ADMIN_DEDUCT', points, { adminId: user.id, reason })

    await writeAudit(db, 'HOUSE_POINTS_AWARDED', user.id, 'USER', userId, { points, reason, houseId: targetUser.houseId })

    return { data: { entry }, status: 201 }
  }

  // ========================
  // GET /house-points/leaderboard — Extended leaderboard with point breakdown
  // ========================
  if (route === 'house-points/leaderboard' && method === 'GET') {
    const houses = await db.collection('houses').find({}).sort({ totalPoints: -1 }).toArray()

    const leaderboard = await Promise.all(houses.map(async (h, rank) => {
      const { _id, ...rest } = h

      const memberCount = await db.collection('users').countDocuments({ houseId: h.id })
      const recentActivity = await db.collection('house_ledger')
        .find({ houseId: h.id })
        .sort({ createdAt: -1 })
        .limit(5)
        .toArray()

      return {
        ...rest,
        rank: rank + 1,
        memberCount,
        pointsPerMember: memberCount > 0 ? Math.round((h.totalPoints || 0) / memberCount * 10) / 10 : 0,
        recentActivity: recentActivity.map(a => { const { _id: rid, ...aRest } = a; return aRest }),
      }
    }))

    return { data: { items: leaderboard, leaderboard, count: leaderboard.length } }
  }

  return null
}
