import { NextResponse } from 'next/server'
import { getDb } from '@/lib/db'
import { cache } from '@/lib/cache'
import { applyFreezeHeaders } from '@/lib/freeze-registry'
import { applySecurityHeaders, getEndpointTier, checkTieredRateLimit, extractIP, checkPayloadSize, deepSanitizeStrings } from '@/lib/security'
import logger from '@/lib/logger'
import metrics from '@/lib/metrics'
import { checkLiveness, checkReadiness, checkDeepHealth } from '@/lib/health'
import { requestContext } from '@/lib/request-context'
import { handleModerationRoutes } from '@/lib/moderation/routes/moderation.routes'
import { dispatchRoute } from '@/lib/route-dispatch'

// ========== CORS ==========
function cors(response) {
  response.headers.set('Access-Control-Allow-Origin', process.env.CORS_ORIGINS || '*')
  response.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS')
  response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization')
  response.headers.set('Access-Control-Allow-Credentials', 'true')
  return response
}

// ========== RESPONSE BUILDERS ==========
function jsonOk(data, status = 200) {
  const resp = cors(NextResponse.json(data, { status }))
  resp.headers.set('x-contract-version', 'v2')
  applySecurityHeaders(resp)
  return resp
}

function jsonErr(message, code, status = 400, extraHeaders = {}) {
  const resp = cors(NextResponse.json({ error: message, code }, { status }))
  resp.headers.set('x-contract-version', 'v2')
  applySecurityHeaders(resp)
  for (const [k, v] of Object.entries(extraHeaders)) {
    resp.headers.set(k, v)
  }
  return resp
}

// ========== ADMIN AUTH HELPER ==========
async function requireAdmin(request, db, reqCtx, roles = ['ADMIN', 'SUPER_ADMIN']) {
  try {
    const { requireAuth } = await import('@/lib/auth-utils')
    const user = await requireAuth(request, db)
    if (!roles.includes(user.role)) {
      reqCtx.errorCode = 'FORBIDDEN'
      return { err: jsonErr(`${roles[0]} access required`, 'FORBIDDEN', 403) }
    }
    return { user }
  } catch (e) {
    if (e.status) { reqCtx.errorCode = e.code; return { err: jsonErr(e.message, e.code, e.status) } }
    reqCtx.errorCode = 'UNAUTHORIZED'
    return { err: jsonErr('Authentication required', 'UNAUTHORIZED', 401) }
  }
}

// ========== OPTIONS ==========
export async function OPTIONS(request, context) {
  const requestId = crypto.randomUUID()
  const startTime = Date.now()
  const { path = [] } = context.params
  const route = `/${path.join('/')}`
  const ip = extractIP(request)

  const resp = cors(new NextResponse(null, { status: 200 }))
  applySecurityHeaders(resp)
  resp.headers.set('x-request-id', requestId)
  applyFreezeHeaders(resp, route, 'OPTIONS')

  const latencyMs = Date.now() - startTime
  logger.info('HTTP', 'request_completed', { requestId, method: 'OPTIONS', route, statusCode: 200, latencyMs, ip })
  metrics.recordRequest(route, 'OPTIONS', 200, latencyMs)
  return resp
}

// ========== OPS ENDPOINTS ==========
async function handleOpsEndpoints(route, method, request, db, reqCtx) {
  if (route === '/ops/health' && method === 'GET') {
    const { err } = await requireAdmin(request, db, reqCtx)
    if (err) return err
    return jsonOk(await checkDeepHealth(db))
  }

  if (route === '/ops/metrics' && method === 'GET') {
    const { err } = await requireAdmin(request, db, reqCtx)
    if (err) return err
    const [userCount, postCount, activeSessionCount, reportCount, grievanceCount] = await Promise.all([
      db.collection('users').countDocuments(),
      db.collection('content_items').countDocuments(),
      db.collection('sessions').countDocuments({ expiresAt: { $gt: new Date() } }),
      db.collection('reports').countDocuments({ status: 'OPEN' }),
      db.collection('grievance_tickets').countDocuments({ status: 'OPEN' }),
    ])
    const cacheStats = await cache.getStats()
    return jsonOk({
      ...metrics.getMetrics(),
      business: {
        users: userCount, posts: postCount, activeSessions: activeSessionCount,
        openReports: reportCount, openGrievances: grievanceCount,
        cache: { hitRate: cacheStats.hitRate, redisStatus: cacheStats.redis.status },
      },
    })
  }

  if (route === '/ops/slis' && method === 'GET') {
    const { err } = await requireAdmin(request, db, reqCtx)
    if (err) return err
    return jsonOk(metrics.getSLIs())
  }

  if (route === '/ops/backup-check' && method === 'GET') {
    const { err } = await requireAdmin(request, db, reqCtx)
    if (err) return err
    const collections = await db.listCollections().toArray()
    const sizes = await Promise.all(collections.map(async (c) => {
      const count = await db.collection(c.name).countDocuments()
      return { name: c.name, docs: count }
    }))
    return jsonOk({
      backupReady: true, collections: sizes.length,
      totalDocuments: sizes.reduce((s, c) => s + c.docs, 0),
      collectionDetails: sizes,
      backupCommand: 'mongodump --db=your_database_name --out=/backup/$(date +%Y%m%d_%H%M%S)',
      restoreCommand: 'mongorestore --db=your_database_name /backup/<timestamp>/',
      timestamp: new Date().toISOString(),
    })
  }

  return null // Not an ops endpoint
}

// ========== SPECIAL INLINE ENDPOINTS ==========
async function handleInlineEndpoints(route, method, path, request, db, reqCtx) {
  // Cache stats
  if (route === '/cache/stats' && method === 'GET') {
    const { err } = await requireAdmin(request, db, reqCtx)
    if (err) return err
    return jsonOk(await cache.getStats())
  }

  // Moderation config & check
  if ((route === '/moderation/config' && method === 'GET') || (route === '/moderation/check' && method === 'POST')) {
    const { err } = await requireAdmin(request, db, reqCtx, ['MODERATOR', 'ADMIN', 'SUPER_ADMIN'])
    if (err) return err
    const modResult = await handleModerationRoutes(path, method, request, db)
    if (modResult) {
      if (modResult.error) { reqCtx.errorCode = modResult.code; return jsonErr(modResult.error, modResult.code || 'ERROR', modResult.status || 400) }
      return jsonOk(modResult.data, modResult.status || 200)
    }
  }

  return null
}

// ========== MAIN ROUTER CORE ==========
async function handleRouteCore(request, { params }, reqCtx) {
  const { path = [] } = params
  const route = `/${path.join('/')}`
  const method = request.method
  const ip = extractIP(request)

  // Liveness probe: runs BEFORE everything (must always work)
  if (route === '/healthz' && method === 'GET') {
    return jsonOk(await checkLiveness())
  }

  // Tiered rate limiting — Phase 1: Per-IP
  const tier = getEndpointTier(route, method)
  const ipRateResult = await checkTieredRateLimit(ip, null, tier)
  if (!ipRateResult.allowed) {
    reqCtx.rateLimited = true
    reqCtx.errorCode = 'RATE_LIMITED'
    return jsonErr(`Rate limit exceeded (${tier.name}). Try again later.`, 'RATE_LIMITED', 429, { 'Retry-After': String(ipRateResult.retryAfter) })
  }

  // Payload size check (non-media routes)
  if (['POST', 'PUT', 'PATCH'].includes(method) && !route.startsWith('/media')) {
    if (!checkPayloadSize(request)) {
      reqCtx.errorCode = 'PAYLOAD_TOO_LARGE'
      return jsonErr('Request payload too large', 'PAYLOAD_TOO_LARGE', 413)
    }
  }

  // Input sanitization for JSON bodies
  if (['POST', 'PUT', 'PATCH'].includes(method) && !route.startsWith('/media')) {
    const contentType = request.headers.get('content-type')
    if (contentType?.includes('application/json')) {
      try {
        const rawBodyText = await request.text()
        if (rawBodyText) {
          const parsed = JSON.parse(rawBodyText)
          const sanitized = deepSanitizeStrings(parsed)
          request = new Request(request.url, {
            method: request.method,
            headers: request.headers,
            body: JSON.stringify(sanitized),
          })
        }
      } catch (e) {
        logger.warn('HTTP', 'body_parse_failed', { requestId: reqCtx.requestId, route, method, error: e.message })
      }
    }
  }

  try {
    const db = await getDb()

    // Per-user rate limiting — Phase 2 (post-DB)
    let authUserId = null
    try {
      const authHeader = request.headers.get('authorization')
      if (authHeader?.startsWith('Bearer ')) {
        const tkn = authHeader.slice(7)
        if (tkn.length > 10) {
          const sess = await db.collection('sessions').findOne({ token: tkn }, { projection: { userId: 1, _id: 0 } })
          if (sess) {
            authUserId = sess.userId
            reqCtx.userId = sess.userId
            const ctx = requestContext.getStore()
            if (ctx) ctx.userId = sess.userId
          }
        }
      }
    } catch (e) {
      logger.debug('HTTP', 'userid_extraction_failed', { requestId: reqCtx.requestId, error: e.message })
    }

    if (authUserId) {
      const userRateResult = await checkTieredRateLimit(null, authUserId, tier)
      if (!userRateResult.allowed) {
        reqCtx.rateLimited = true
        reqCtx.errorCode = 'RATE_LIMITED'
        return jsonErr(`Rate limit exceeded (${tier.name}). Try again later.`, 'RATE_LIMITED', 429, { 'Retry-After': String(userRateResult.retryAfter) })
      }
    }

    // Readiness probe
    if (route === '/readyz' && method === 'GET') {
      const readiness = await checkReadiness(db)
      if (!readiness.ready) return jsonErr('Service not ready', 'NOT_READY', 503)
      return jsonOk(readiness)
    }

    // API root info
    if (route === '/' && method === 'GET') {
      return jsonOk({
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
        },
      })
    }

    // Ops endpoints (admin-authed)
    const opsResult = await handleOpsEndpoints(route, method, request, db, reqCtx)
    if (opsResult) return opsResult

    // Special inline endpoints (cache stats, moderation)
    const inlineResult = await handleInlineEndpoints(route, method, path, request, db, reqCtx)
    if (inlineResult) return inlineResult

    // ---- Route dispatch via registry ----
    const result = await dispatchRoute(path, method, request, db)

    if (result === null) {
      reqCtx.errorCode = 'NOT_FOUND'
      return jsonErr(`Route ${route} [${method}] not found`, 'NOT_FOUND', 404)
    }

    if (result.raw) {
      const rawResp = cors(result.raw)
      applySecurityHeaders(rawResp)
      return rawResp
    }

    if (result.error) {
      reqCtx.errorCode = result.code || 'ERROR'
      return jsonErr(result.error, result.code || 'ERROR', result.status || 400, result.headers || {})
    }

    const resp = jsonOk(result.data, result.status || 200)
    if (result.headers) {
      for (const [key, value] of Object.entries(result.headers)) {
        resp.headers.set(key, value)
      }
    }
    return resp

  } catch (error) {
    if (error.status && error.code) {
      reqCtx.errorCode = error.code
      return jsonErr(error.message, error.code, error.status)
    }
    reqCtx.errorCode = 'INTERNAL_ERROR'
    logger.error('HTTP', 'unhandled_error', {
      requestId: reqCtx.requestId,
      route: `/${(params?.path || []).join('/')}`,
      method: request.method,
      error: error.message,
      stack: error.stack?.split('\n').slice(0, 5).join(' | '),
    })
    return jsonErr('Internal server error', 'INTERNAL_ERROR', 500)
  }
}

// ========== OBSERVABILITY WRAPPER ==========
async function handleRoute(request, context) {
  const requestId = crypto.randomUUID()
  const startTime = Date.now()
  const { path = [] } = context.params
  const route = `/${path.join('/')}`
  const method = request.method
  const ip = extractIP(request)

  const reqCtx = { requestId, userId: null, rateLimited: false, errorCode: null }
  const correlationStore = { requestId, ip, method, route, userId: null }

  const response = await requestContext.run(correlationStore, () =>
    handleRouteCore(request, context, reqCtx)
  )

  const statusCode = response.status
  const latencyMs = Date.now() - startTime

  // Observability headers
  response.headers.set('x-request-id', requestId)
  response.headers.set('x-latency-ms', String(latencyMs))
  applyFreezeHeaders(response, route, method)

  // Cache-Control for GET 200s
  if (method === 'GET' && statusCode === 200) {
    if (route.includes('/feed') || route.includes('/reels/feed') || route.includes('/discover')) {
      response.headers.set('Cache-Control', 'public, max-age=10, s-maxage=15, stale-while-revalidate=30')
    } else if (route.includes('/tribes') || route.includes('/tribe-contests') || route.includes('/tribe-rivalries')) {
      response.headers.set('Cache-Control', 'public, max-age=30, s-maxage=60, stale-while-revalidate=120')
    } else if (route.includes('/media/') && !route.includes('/upload')) {
      response.headers.set('Cache-Control', 'public, max-age=3600, s-maxage=86400, immutable')
    } else if (route.includes('/search') || route.includes('/hashtags')) {
      response.headers.set('Cache-Control', 'public, max-age=15, s-maxage=20, stale-while-revalidate=60')
    } else {
      response.headers.set('Cache-Control', 'private, max-age=5, stale-while-revalidate=15')
    }
  }

  logger.info('HTTP', 'request_completed', {
    requestId, method, route, statusCode, latencyMs, ip,
    userId: reqCtx.userId, rateLimited: reqCtx.rateLimited, errorCode: reqCtx.errorCode,
  })

  metrics.recordRequest(route, method, statusCode, latencyMs)
  if (reqCtx.errorCode) metrics.recordError(reqCtx.errorCode)

  return response
}

export const GET = handleRoute
export const POST = handleRoute
export const PUT = handleRoute
export const DELETE = handleRoute
export const PATCH = handleRoute
