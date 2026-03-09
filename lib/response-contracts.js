/**
 * Tribe — Canonical Contract v2: Response Builders
 * 
 * RULES:
 * 1. Every list endpoint MUST use `items` as the collection key
 * 2. Cursor-paginated lists: { items, pagination: { nextCursor, hasMore } }
 * 3. Offset-paginated lists: { items, pagination: { total, limit, offset } }
 * 4. Single entity: { [entityName]: {...} }
 * 5. Mutation acknowledgement: { message, [entityName]?: {...} }
 * 6. Backward-compat aliases kept during v1→v2 migration window
 * 
 * CONTRACT VERSION: v2
 * STATUS: ENFORCED
 */

// ========== LIST RESPONSE: CURSOR PAGINATION ==========
/**
 * Standard cursor-paginated list response.
 * Used by: feeds, comments, notifications, stories, reels, events, notices
 * 
 * @param {Array} items - The list items
 * @param {string|null} nextCursor - Next page cursor (null if no more)
 * @param {Object} extra - Additional metadata (feedType, unreadCount, etc.)
 * @returns {Object} Canonical list response
 */
export function cursorList(items, nextCursor, extra = {}) {
  return {
    items,
    pagination: {
      nextCursor: nextCursor || null,
      hasMore: nextCursor !== null && nextCursor !== undefined,
    },
    ...extra,
  }
}

// ========== LIST RESPONSE: OFFSET PAGINATION ==========
/**
 * Standard offset-paginated list response.
 * Used by: followers, following, members, admin queues, search results
 * 
 * @param {Array} items - The list items
 * @param {number} total - Total count of matching documents
 * @param {number} limit - Current page size
 * @param {number} offset - Current offset
 * @param {Object} extra - Additional metadata
 * @returns {Object} Canonical list response
 */
export function offsetList(items, total, limit, offset, extra = {}) {
  return {
    items,
    pagination: {
      total,
      limit,
      offset,
      hasMore: offset + items.length < total,
    },
    ...extra,
  }
}

// ========== LIST RESPONSE: UNBOUNDED (no pagination) ==========
/**
 * For small, bounded lists that don't need pagination.
 * Used by: distinct values, enum lists, bounded queries
 * 
 * @param {Array} items
 * @param {Object} extra
 * @returns {Object}
 */
export function simpleList(items, extra = {}) {
  return {
    items,
    count: items.length,
    ...extra,
  }
}

// ========== MUTATION ACKNOWLEDGEMENT ==========
/**
 * Standard mutation response.
 * Used by: follow, like, save, delete, moderate, etc.
 * 
 * @param {string} message - Human-readable confirmation
 * @param {Object} extra - Additional state (isFollowing, saved, etc.)
 * @returns {Object}
 */
export function mutationOk(message, extra = {}) {
  return {
    message,
    ...extra,
  }
}

// ========== PAGINATION STANDARDS ==========
/**
 * Contract v2 pagination policy:
 * 
 * CURSOR (default for user-facing feeds):
 *   - feed/public, feed/following, feed/college/*, feed/reels
 *   - content/:id/comments
 *   - notifications
 *   - events/feed, events/search, events/college/*, me/events
 *   - colleges/:id/notices
 *   - stories/feed, stories/:id/replies
 *   - reels/feed, reels/following, reels/:id/comments
 *   - tribe-contests/:id/entries
 *   - users/:id/posts, users/:id/saved
 * 
 * OFFSET (admin/bounded lists):
 *   - users/:id/followers, users/:id/following
 *   - colleges/:id/members
 *   - colleges/search
 *   - events/:id/attendees
 *   - board/notices/:id/acknowledgments
 *   - moderation/queue
 *   - admin/* (all admin lists)
 * 
 * NONE (bounded queries, <50 items guaranteed):
 *   - colleges/states, colleges/types
 *   - houses, houses/leaderboard
 *   - tribes
 *   - suggestions/users
 *   - search (capped at 20 per type)
 *   - me/close-friends, me/blocks
 *   - governance/*/applications (board-only)
 *   - appeals, grievances (user's own, capped)
 */
export const PaginationPolicy = {
  CURSOR: 'cursor',
  OFFSET: 'offset',
  NONE: 'none',
}
