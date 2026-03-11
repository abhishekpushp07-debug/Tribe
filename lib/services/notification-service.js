/**
 * Tribe Notifications 2.0 — Service Layer (Gold-Proof)
 * Centralized notification creation with:
 *   - Atomic duplicate prevention (unique index + catch E11000)
 *   - Preference checking with force-deliver override
 *   - Block/self-notify suppression
 *   - Structured observability for all outcomes
 *   - Safe degradation for deleted/blocked actors and targets
 */

import { v4 as uuidv4 } from 'uuid'
import logger from '../logger.js'

const NOTIF_LOG = 'NOTIFICATION'

// Default preference state — all enabled
const DEFAULT_PREFERENCES = {
  FOLLOW: true,
  LIKE: true,
  COMMENT: true,
  COMMENT_LIKE: true,
  SHARE: true,
  MENTION: true,
  REEL_LIKE: true,
  REEL_COMMENT: true,
  REEL_SHARE: true,
  STORY_REACTION: true,
  STORY_REPLY: true,
  STORY_REMOVED: true,
  REPORT_RESOLVED: true,
  STRIKE_ISSUED: true,
  APPEAL_DECIDED: true,
  HOUSE_POINTS: true,
}

// Types that are always delivered regardless of preferences (system-critical)
const FORCE_DELIVER_TYPES = new Set([
  'REPORT_RESOLVED',
  'STRIKE_ISSUED',
  'APPEAL_DECIDED',
])

// Dedup window (5 minutes)
const DEDUP_WINDOW_MS = 5 * 60 * 1000

/**
 * Compute a deterministic dedup bucket key for atomic insert protection.
 * Bucket = floor(now / window). Two identical events in the same bucket share the same key.
 */
function computeDedupKey(userId, type, actorId, targetId) {
  const bucket = Math.floor(Date.now() / DEDUP_WINDOW_MS)
  return `${userId}:${type}:${actorId || 'none'}:${targetId || 'none'}:${bucket}`
}

/**
 * Get user's notification preferences with defaults
 */
export async function getUserPreferences(db, userId) {
  const doc = await db.collection('notification_preferences').findOne({ userId })
  if (!doc) return { ...DEFAULT_PREFERENCES }
  const { _id, userId: _, createdAt: _c, updatedAt: __, ...prefs } = doc
  return { ...DEFAULT_PREFERENCES, ...prefs }
}

/**
 * Check if a notification type is enabled for a user
 */
async function isTypeEnabled(db, userId, type) {
  if (FORCE_DELIVER_TYPES.has(type)) return true
  const prefs = await getUserPreferences(db, userId)
  return prefs[type] !== false
}

/**
 * Check if actor is blocked by recipient (bidirectional)
 */
async function isBlockedByRecipient(db, recipientId, actorId) {
  const block = await db.collection('blocks').findOne({
    $or: [
      { blockerId: recipientId, blockedId: actorId },
      { blockerId: actorId, blockedId: recipientId },
    ],
  })
  return !!block
}

/**
 * Create a notification with full delivery hygiene and atomic dedup.
 * Returns the notification doc if created, null if suppressed.
 */
export async function createNotificationV2(db, {
  userId,
  type,
  actorId,
  targetType,
  targetId,
  message,
}) {
  // Rule 1: No self-notification
  if (userId === actorId) {
    logger.debug(NOTIF_LOG, 'suppressed:self', { userId, type, actorId })
    return null
  }

  // Rule 2: Check preferences
  const enabled = await isTypeEnabled(db, userId, type)
  if (!enabled) {
    logger.info(NOTIF_LOG, 'suppressed:preference', { userId, type })
    return null
  }

  // Rule 3: Check block relationship
  if (actorId) {
    const blocked = await isBlockedByRecipient(db, userId, actorId)
    if (blocked) {
      logger.info(NOTIF_LOG, 'suppressed:block', { userId, type, actorId })
      return null
    }
  }

  // Rule 4: Atomic dedup — use dedupKey + unique index to prevent concurrent duplicates
  const dedupKey = computeDedupKey(userId, type, actorId, targetId)

  const notification = {
    id: uuidv4(),
    userId,
    type,
    actorId,
    targetType,
    targetId,
    message,
    read: false,
    dedupKey,
    createdAt: new Date(),
  }

  try {
    await db.collection('notifications').insertOne(notification)
    logger.info(NOTIF_LOG, 'created', { userId, type, actorId, targetType, targetId })
  } catch (err) {
    // E11000 = duplicate key error → dedup caught atomically
    if (err.code === 11000 && err.message?.includes('dedupKey')) {
      logger.info(NOTIF_LOG, 'suppressed:dedup_atomic', { userId, type, actorId, targetId, dedupKey })
      return null
    }
    // Re-throw unexpected errors
    logger.error(NOTIF_LOG, 'insert_failed', { userId, type, error: err.message })
    throw err
  }

  const { _id, ...clean } = notification
  return clean
}

/**
 * Group notifications by {type, targetId} for cleaner inbox display.
 * Returns grouped array where same-type same-target notifications are merged.
 *
 * Safety guarantees (Gold-proof):
 *   - Actors are deduplicated by actorId (no duplicate previews)
 *   - Null/deleted actors filtered from preview array
 *   - actorCount reflects unique actorIds from source notifications (truthful)
 *   - Blocked actors already filtered upstream by filterBlockedNotifications
 *   - read semantics: group.read === true only if ALL items are read
 */
export function groupNotifications(notifications) {
  if (!notifications || !notifications.length) return []

  const groupMap = new Map()

  for (const notif of notifications) {
    const key = `${notif.type}:${notif.targetId || 'none'}`

    if (groupMap.has(key)) {
      const group = groupMap.get(key)
      group.actorIds.add(notif.actorId)
      // Deduplicate actor objects by actorId — only add if not already seen
      if (notif.actor && !group.seenActorIds.has(notif.actorId)) {
        group.actors.push(notif.actor)
        group.seenActorIds.add(notif.actorId)
      }
      group.count++
      if (!notif.read) group.unreadCount++
      // Keep latest notification's data
      if (new Date(notif.createdAt) > new Date(group.latestAt)) {
        group.latestAt = notif.createdAt
        group.latestMessage = notif.message
        group.latestId = notif.id
      }
    } else {
      const seenActorIds = new Set()
      const actors = []
      if (notif.actor) {
        actors.push(notif.actor)
        seenActorIds.add(notif.actorId)
      }
      groupMap.set(key, {
        id: notif.id,
        type: notif.type,
        targetType: notif.targetType,
        targetId: notif.targetId,
        actorIds: new Set([notif.actorId]),
        seenActorIds,
        actors,
        count: 1,
        unreadCount: notif.read ? 0 : 1,
        latestAt: notif.createdAt,
        latestMessage: notif.message,
        latestId: notif.id,
        read: notif.read,
      })
    }
  }

  return Array.from(groupMap.values()).map(g => ({
    id: g.latestId,
    type: g.type,
    targetType: g.targetType,
    targetId: g.targetId,
    actorCount: g.actorIds.size,
    actors: g.actors.slice(0, 3), // Preview up to 3 unique, non-null actors
    count: g.count,
    unreadCount: g.unreadCount,
    message: g.actorIds.size > 1
      ? `${g.actors[0]?.displayName || 'Someone'} and ${g.actorIds.size - 1} others`
      : g.latestMessage,
    read: g.unreadCount === 0,
    createdAt: g.latestAt,
  }))
    .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
}

export { DEFAULT_PREFERENCES }
