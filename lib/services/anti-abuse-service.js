/**
 * Anti-Abuse Service — Engagement Integrity Layer
 *
 * Phase C: Detects and flags suspicious engagement patterns.
 * Provides velocity checks, burst detection, and audit logging.
 *
 * NOT a full ML anti-cheat system — an honest, production-useful
 * foundational layer for engagement integrity.
 */

// ========== THRESHOLDS ==========
const ABUSE_THRESHOLDS = {
  // Max actions per user per time window
  LIKES_PER_MINUTE: 30,
  LIKES_PER_HOUR: 200,
  COMMENTS_PER_MINUTE: 10,
  COMMENTS_PER_HOUR: 60,
  SHARES_PER_MINUTE: 10,
  SHARES_PER_HOUR: 50,
  SAVES_PER_MINUTE: 15,
  SAVES_PER_HOUR: 100,
  VIEWS_PER_MINUTE: 60,
  STORY_REACTIONS_PER_MINUTE: 20,

  // Burst detection: N same-action on same target within window
  SAME_TARGET_LIKES_WINDOW_MS: 5_000, // 5 likes on same content in 5s = bot
  SAME_AUTHOR_LIKES_WINDOW_MS: 60_000, // Rapid likes on same author's content

  // Velocity: actions per second (sustained)
  SUSPICIOUS_VELOCITY: 3, // 3+ actions/second sustained for 10s
  VELOCITY_WINDOW_MS: 10_000,
}

// ========== ACTION TYPES ==========
const ActionType = {
  LIKE: 'LIKE',
  COMMENT: 'COMMENT',
  SHARE: 'SHARE',
  SAVE: 'SAVE',
  VIEW: 'VIEW',
  STORY_REACTION: 'STORY_REACTION',
  FOLLOW: 'FOLLOW',
  VOTE: 'VOTE',
}

// In-memory sliding window for velocity detection (per userId)
// Key: userId, Value: { actions: [{ type, targetId, ts }], flagCount }
const userActionWindows = new Map()
const WINDOW_CLEANUP_INTERVAL = 5 * 60 * 1000 // 5 min

// Periodic cleanup of stale windows
setInterval(() => {
  const cutoff = Date.now() - 60_000 // Remove users inactive for 60s
  for (const [userId, window] of userActionWindows.entries()) {
    if (window.actions.length === 0 || window.actions[window.actions.length - 1].ts < cutoff) {
      userActionWindows.delete(userId)
    }
  }
}, WINDOW_CLEANUP_INTERVAL)

/**
 * Record an engagement action and check for abuse.
 * Returns { allowed, reason, flagged } where:
 * - allowed: true if action should proceed
 * - reason: why it was blocked (if not allowed)
 * - flagged: true if suspicious but still allowed (soft flag for audit)
 */
export function checkEngagementAbuse(userId, actionType, targetId, targetAuthorId) {
  const now = Date.now()

  // Get or create user window
  if (!userActionWindows.has(userId)) {
    userActionWindows.set(userId, { actions: [], flagCount: 0, lastFlagged: 0 })
  }
  const window = userActionWindows.get(userId)

  // Trim old actions (keep last 5 minutes)
  const fiveMinAgo = now - 300_000
  window.actions = window.actions.filter(a => a.ts > fiveMinAgo)

  // Record this action
  window.actions.push({ type: actionType, targetId, targetAuthorId, ts: now })

  const recentActions = window.actions

  // ── CHECK 1: Per-minute velocity ──
  const oneMinAgo = now - 60_000
  const actionsLastMinute = recentActions.filter(a => a.ts > oneMinAgo && a.type === actionType)
  const minuteThreshold = getMinuteThreshold(actionType)

  if (actionsLastMinute.length > minuteThreshold) {
    window.flagCount++
    return {
      allowed: false,
      reason: `Rate limit: ${minuteThreshold} ${actionType.toLowerCase()}s per minute exceeded`,
      flagged: true,
      severity: 'HIGH',
    }
  }

  // ── CHECK 2: Same-target burst detection ──
  if (targetId) {
    const burstWindow = ABUSE_THRESHOLDS.SAME_TARGET_LIKES_WINDOW_MS
    const sameTargetRecent = recentActions.filter(
      a => a.ts > (now - burstWindow) && a.targetId === targetId && a.type === actionType
    )
    if (sameTargetRecent.length > 3) {
      window.flagCount++
      return {
        allowed: false,
        reason: `Burst detected: repeated ${actionType.toLowerCase()} on same content`,
        flagged: true,
        severity: 'HIGH',
      }
    }
  }

  // ── CHECK 3: Same-author concentration ──
  if (targetAuthorId) {
    const concentrationWindow = ABUSE_THRESHOLDS.SAME_AUTHOR_LIKES_WINDOW_MS
    const sameAuthorRecent = recentActions.filter(
      a => a.ts > (now - concentrationWindow) && a.targetAuthorId === targetAuthorId && a.type === actionType
    )
    if (sameAuthorRecent.length > 10) {
      window.flagCount++
      return {
        allowed: true, // Soft flag — don't block but flag
        reason: null,
        flagged: true,
        severity: 'MEDIUM',
        warning: `Concentrated ${actionType.toLowerCase()}s on single author`,
      }
    }
  }

  // ── CHECK 4: Sustained velocity ──
  const velocityWindow = ABUSE_THRESHOLDS.VELOCITY_WINDOW_MS
  const velocityActions = recentActions.filter(a => a.ts > (now - velocityWindow))
  const velocity = velocityActions.length / (velocityWindow / 1000) // actions per second

  if (velocity > ABUSE_THRESHOLDS.SUSPICIOUS_VELOCITY) {
    window.flagCount++
    return {
      allowed: true, // Soft flag
      reason: null,
      flagged: true,
      severity: 'MEDIUM',
      warning: `Sustained velocity: ${velocity.toFixed(1)} actions/sec`,
    }
  }

  // ── CHECK 5: Cumulative flag escalation ──
  if (window.flagCount > 10) {
    return {
      allowed: false,
      reason: 'Account temporarily restricted due to suspicious activity patterns',
      flagged: true,
      severity: 'CRITICAL',
    }
  }

  return { allowed: true, reason: null, flagged: false }
}

function getMinuteThreshold(actionType) {
  switch (actionType) {
    case ActionType.LIKE: return ABUSE_THRESHOLDS.LIKES_PER_MINUTE
    case ActionType.COMMENT: return ABUSE_THRESHOLDS.COMMENTS_PER_MINUTE
    case ActionType.SHARE: return ABUSE_THRESHOLDS.SHARES_PER_MINUTE
    case ActionType.SAVE: return ABUSE_THRESHOLDS.SAVES_PER_MINUTE
    case ActionType.VIEW: return ABUSE_THRESHOLDS.VIEWS_PER_MINUTE
    case ActionType.STORY_REACTION: return ABUSE_THRESHOLDS.STORY_REACTIONS_PER_MINUTE
    default: return 30
  }
}

/**
 * Log a suspicious action to audit_log for admin review.
 */
export async function logSuspiciousAction(db, userId, actionType, targetId, abuseResult) {
  if (!abuseResult.flagged) return

  await db.collection('abuse_audit_log').insertOne({
    userId,
    actionType,
    targetId,
    severity: abuseResult.severity,
    reason: abuseResult.reason || abuseResult.warning,
    blocked: !abuseResult.allowed,
    timestamp: new Date(),
  })
}

/**
 * Get abuse summary for admin dashboard.
 */
export async function getAbuseSummary(db, opts = {}) {
  const { hours = 24 } = opts
  const since = new Date(Date.now() - hours * 3600000)

  const [totalFlags, blockedActions, topOffenders, bySeverity] = await Promise.all([
    db.collection('abuse_audit_log').countDocuments({ timestamp: { $gte: since } }),
    db.collection('abuse_audit_log').countDocuments({ blocked: true, timestamp: { $gte: since } }),
    db.collection('abuse_audit_log').aggregate([
      { $match: { timestamp: { $gte: since } } },
      { $group: { _id: '$userId', flagCount: { $sum: 1 }, blockedCount: { $sum: { $cond: ['$blocked', 1, 0] } } } },
      { $sort: { flagCount: -1 } },
      { $limit: 10 },
    ]).toArray(),
    db.collection('abuse_audit_log').aggregate([
      { $match: { timestamp: { $gte: since } } },
      { $group: { _id: '$severity', count: { $sum: 1 } } },
    ]).toArray(),
  ])

  return {
    period: `${hours}h`,
    totalFlags,
    blockedActions,
    topOffenders: topOffenders.map(o => ({ userId: o._id, flags: o.flagCount, blocked: o.blockedCount })),
    bySeverity: Object.fromEntries(bySeverity.map(s => [s._id, s.count])),
    generatedAt: new Date().toISOString(),
  }
}

export { ActionType, ABUSE_THRESHOLDS }
