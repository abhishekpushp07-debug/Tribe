/**
 * Tribe — Ops & Admin Endpoints Handler
 * 
 * Handles: /ops/*, /cache/stats, /ws/stats, /healthz, /readyz, /
 * Extracted from route.js for clean separation.
 */

import { cache } from '../cache.js'
import metrics from '../metrics.js'
import { checkLiveness, checkReadiness, checkDeepHealth } from '../health.js'
import { requireAuth } from '../auth-utils.js'
import { handleModerationRoutes } from '../moderation/routes/moderation.routes.js'

// Check admin role
async function requireAdmin(request, db, roles = ['ADMIN', 'SUPER_ADMIN']) {
  const user = await requireAuth(request, db)
  if (!roles.includes(user.role)) {
    return { err: { error: `${roles[0]} access required`, code: 'FORBIDDEN', status: 403 } }
  }
  return { user }
}

export async function handleOps(path, method, request, db) {
  const route = path.join('/')

  // ===== PUBLIC PROBES =====

  if (route === 'healthz' && method === 'GET') {
    return { data: await checkLiveness() }
  }

  if (route === 'readyz' && method === 'GET') {
    const readiness = await checkReadiness(db)
    if (!readiness.ready) return { error: 'Service not ready', code: 'NOT_READY', status: 503 }
    return { data: readiness }
  }

  // API root info
  if (path.length === 0 && method === 'GET') {
    return { data: {
      name: 'Tribe API', version: '3.0.0', status: 'running',
      timestamp: new Date().toISOString(),
      stages: 'Stages 1-9 complete',
      endpoints: {
        auth: '/api/auth/*', profile: '/api/me/*', users: '/api/users/*',
        content: '/api/content/*', feed: '/api/feed/*',
        social: '/api/follow/*, /api/content/*/like|save|comments',
        colleges: '/api/colleges/*', media: '/api/media/*',
        search: '/api/search', notifications: '/api/notifications',
        health: '/api/healthz, /api/readyz, /api/ops/health, /api/ops/metrics',
        websocket: 'ws://host:3001?token=<auth_token>',
      },
    }}
  }

  // ===== ADMIN OPS ENDPOINTS =====

  if (route === 'ops/health' && method === 'GET') {
    const { err } = await requireAdmin(request, db)
    if (err) return err
    return { data: await checkDeepHealth(db) }
  }

  if (route === 'ops/metrics' && method === 'GET') {
    const { err } = await requireAdmin(request, db)
    if (err) return err
    const [userCount, postCount, activeSessionCount, reportCount, grievanceCount] = await Promise.all([
      db.collection('users').countDocuments(),
      db.collection('content_items').countDocuments(),
      db.collection('sessions').countDocuments({ expiresAt: { $gt: new Date() } }),
      db.collection('reports').countDocuments({ status: 'OPEN' }),
      db.collection('grievance_tickets').countDocuments({ status: 'OPEN' }),
    ])
    const cacheStats = await cache.getStats()
    return { data: {
      ...metrics.getMetrics(),
      business: {
        users: userCount, posts: postCount, activeSessions: activeSessionCount,
        openReports: reportCount, openGrievances: grievanceCount,
        cache: { hitRate: cacheStats.hitRate, redisStatus: cacheStats.redis.status },
      },
    }}
  }

  if (route === 'ops/slis' && method === 'GET') {
    const { err } = await requireAdmin(request, db)
    if (err) return err
    return { data: metrics.getSLIs() }
  }

  if (route === 'ops/backup-check' && method === 'GET') {
    const { err } = await requireAdmin(request, db)
    if (err) return err
    const collections = await db.listCollections().toArray()
    const sizes = await Promise.all(collections.map(async (c) => {
      const count = await db.collection(c.name).countDocuments()
      return { name: c.name, docs: count }
    }))
    return { data: {
      backupReady: true, collections: sizes.length,
      totalDocuments: sizes.reduce((s, c) => s + c.docs, 0),
      collectionDetails: sizes,
      backupCommand: 'mongodump --db=your_database_name --out=/backup/$(date +%Y%m%d_%H%M%S)',
      restoreCommand: 'mongorestore --db=your_database_name /backup/<timestamp>/',
      timestamp: new Date().toISOString(),
    }}
  }

  // ===== CACHE STATS =====

  if (route === 'cache/stats' && method === 'GET') {
    const { err } = await requireAdmin(request, db)
    if (err) return err
    return { data: await cache.getStats() }
  }

  // ===== WEBSOCKET STATS =====

  if (route === 'ws/stats' && method === 'GET') {
    const { err } = await requireAdmin(request, db)
    if (err) return err
    // Read WS stats from Redis (set by WS server)
    try {
      const { getRedis } = await import('../cache.js')
      const redis = getRedis()
      if (redis) {
        const stats = await redis.get('tribe:ws:stats')
        if (stats) return { data: JSON.parse(stats) }
      }
    } catch {}
    return { data: { totalConnections: 0, uniqueUsers: 0, redisMode: false, note: 'WS server stats unavailable' } }
  }

  // ===== MODERATION CONFIG & CHECK =====

  if ((route === 'moderation/config' && method === 'GET') || (route === 'moderation/check' && method === 'POST')) {
    const { err } = await requireAdmin(request, db, ['MODERATOR', 'ADMIN', 'SUPER_ADMIN'])
    if (err) return err
    const modResult = await handleModerationRoutes(path, method, request, db)
    if (modResult) {
      if (modResult.error) return { error: modResult.error, code: modResult.code || 'ERROR', status: modResult.status || 400 }
      return { data: modResult.data, status: modResult.status || 200 }
    }
  }

  return null
}
