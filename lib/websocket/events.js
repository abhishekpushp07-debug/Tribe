/**
 * Tribe — WebSocket Event Types & Helpers
 *
 * Shared event type constants used by both the WS server
 * and the REST API handlers that push notifications.
 *
 * Import this in social.js, content.js, etc. to push real-time events
 * without importing the full WS server.
 */

// ========== EVENT TYPES ==========
export const WsEvent = {
  // Social interactions (server → client)
  LIKE: 'like',
  UNLIKE: 'unlike',
  COMMENT: 'comment',
  FOLLOW: 'follow',
  UNFOLLOW: 'unfollow',
  MENTION: 'mention',

  // Content updates
  NEW_POST: 'new_post',
  POST_DELETED: 'post_deleted',
  STORY_POSTED: 'story_posted',
  REEL_POSTED: 'reel_posted',

  // Real-time interactions (client ↔ server)
  TYPING: 'typing',
  TYPING_STOP: 'typing_stop',
  CONTENT_VIEWED: 'content_viewed',
  MARK_READ: 'mark_read',

  // Presence
  PRESENCE: 'presence',
  PRESENCE_QUERY: 'presence_query',
  PRESENCE_RESULT: 'presence_result',

  // System
  AUTHENTICATED: 'authenticated',
  ERROR: 'error',
  PING: 'ping',
  PONG: 'pong',
}

/**
 * Push a real-time event to a user via WebSocket.
 * Safe to call even if WS server is not running — errors are silently swallowed.
 *
 * @param {string} targetUserId - User to notify
 * @param {string} eventType - One of WsEvent constants
 * @param {Object} data - Event payload
 */
export async function pushWsEvent(targetUserId, eventType, data) {
  if (!targetUserId) return
  try {
    // Try Redis pub/sub (works cross-process)
    const Redis = (await import('ioredis')).default
    const REDIS_URL = process.env.REDIS_URL || 'redis://127.0.0.1:6379'
    const pub = new Redis(REDIS_URL, { maxRetriesPerRequest: 1, connectTimeout: 1000, lazyConnect: true })
    pub.on('error', () => {})
    await pub.connect()
    await pub.publish('tribe:ws:broadcast', JSON.stringify({
      type: eventType,
      targetUserId,
      data,
      timestamp: new Date().toISOString(),
    }))
    await pub.quit()
  } catch {
    // WS server not running or Redis unavailable — silently skip
  }
}
