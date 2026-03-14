/**
 * Tribe — WebSocket Real-time Server
 *
 * Standalone WebSocket server for 2-way real-time communication.
 * Runs on port 3001 alongside the Next.js app (port 3000).
 *
 * Features:
 * - Token-based auth (same session tokens as REST API)
 * - Redis Pub/Sub for multi-instance broadcast
 * - In-memory fallback when Redis is unavailable
 * - Presence tracking (online/offline)
 * - Typed event system: likes, comments, follows, typing, presence
 * - Heartbeat + auto-reconnect
 * - Graceful shutdown
 */

import { WebSocketServer } from 'ws'
import { MongoClient } from 'mongodb'
import { EventEmitter } from 'events'

const WS_PORT = parseInt(process.env.WS_PORT || '3001', 10)
const MONGO_URL = process.env.MONGO_URL || 'mongodb://localhost:27017'
const DB_NAME = process.env.DB_NAME || 'your_database_name'
const REDIS_URL = process.env.REDIS_URL || 'redis://127.0.0.1:6379'
const HEARTBEAT_INTERVAL = 20_000 // 20s
const AUTH_TIMEOUT = 10_000 // 10s to authenticate after connecting

// ========== STATE ==========
let db = null
let redisPub = null
let redisSub = null
let redisReady = false
const memBus = new EventEmitter()
memBus.setMaxListeners(1000)

// userId → Set<ws> (one user can have multiple connections: phone + tablet)
const userConnections = new Map()
// ws → { userId, connectedAt, lastPing }
const connectionMeta = new WeakMap()

// ========== MONGO ==========
async function connectDb() {
  const client = new MongoClient(MONGO_URL)
  await client.connect()
  db = client.db(DB_NAME)
  console.log('[WS] MongoDB connected')
  return client
}

// ========== REDIS ==========
async function connectRedis() {
  try {
    const Redis = (await import('ioredis')).default
    redisPub = new Redis(REDIS_URL, { maxRetriesPerRequest: 2, connectTimeout: 3000, lazyConnect: true })
    redisSub = new Redis(REDIS_URL, { maxRetriesPerRequest: 2, connectTimeout: 3000, lazyConnect: true })
    redisPub.on('error', () => {})
    redisSub.on('error', () => {})
    await redisPub.connect()
    await redisSub.connect()
    await redisPub.ping()
    redisReady = true
    console.log('[WS] Redis Pub/Sub connected')

    // Subscribe to the broadcast channel
    await redisSub.subscribe('tribe:ws:broadcast')
    redisSub.on('message', (channel, message) => {
      if (channel === 'tribe:ws:broadcast') {
        try {
          const event = JSON.parse(message)
          deliverToUser(event.targetUserId, event)
        } catch {}
      }
    })
  } catch (err) {
    redisReady = false
    console.log('[WS] Redis unavailable, using in-memory Pub/Sub:', err.message)
    memBus.on('broadcast', (event) => {
      deliverToUser(event.targetUserId, event)
    })
  }
}

// ========== AUTH ==========
async function authenticateToken(token) {
  if (!token || token.length < 10) return null
  const session = await db.collection('sessions').findOne(
    { token, expiresAt: { $gt: new Date() } },
    { projection: { userId: 1, _id: 0 } }
  )
  if (!session) return null
  const user = await db.collection('users').findOne(
    { id: session.userId },
    { projection: { id: 1, displayName: 1, _id: 0 } }
  )
  return user || null
}

// ========== DELIVERY ==========
function deliverToUser(userId, event) {
  const conns = userConnections.get(userId)
  if (!conns || conns.size === 0) return
  const payload = JSON.stringify(event)
  for (const ws of conns) {
    if (ws.readyState === 1) { // OPEN
      try { ws.send(payload) } catch {}
    }
  }
}

// Publish event to a user (works cross-instance via Redis)
export function pushToUser(targetUserId, eventType, data) {
  const event = {
    type: eventType,
    targetUserId,
    data,
    timestamp: new Date().toISOString(),
  }

  if (redisReady && redisPub) {
    redisPub.publish('tribe:ws:broadcast', JSON.stringify(event)).catch(() => {})
  } else {
    memBus.emit('broadcast', event)
  }
}

// ========== PRESENCE ==========
function setPresence(userId, online) {
  if (!userId) return
  // Update DB (fire-and-forget)
  db?.collection('users').updateOne(
    { id: userId },
    { $set: { isOnline: online, lastSeen: new Date() } }
  ).catch(() => {})

  // Notify followers about presence change
  db?.collection('follows').find(
    { followingId: userId },
    { projection: { followerId: 1, _id: 0 } }
  ).limit(200).toArray().then(followers => {
    for (const f of followers) {
      pushToUser(f.followerId, 'presence', { userId, online, lastSeen: new Date().toISOString() })
    }
  }).catch(() => {})
}

// ========== MESSAGE HANDLERS ==========
const messageHandlers = {
  // Client sends typing indicator
  typing(ws, meta, data) {
    if (!data.targetUserId || !data.context) return
    pushToUser(data.targetUserId, 'typing', {
      userId: meta.userId,
      context: data.context, // 'comment' | 'dm' | 'reply'
      contentId: data.contentId || null,
    })
  },

  // Client marks notifications as read
  mark_read(ws, meta, data) {
    if (!data.notificationIds?.length) return
    db?.collection('notifications').updateMany(
      { id: { $in: data.notificationIds }, userId: meta.userId },
      { $set: { read: true, readAt: new Date() } }
    ).catch(() => {})
  },

  // Client sends read receipt for content
  content_viewed(ws, meta, data) {
    if (!data.contentId) return
    db?.collection('content_items').updateOne(
      { id: data.contentId },
      { $inc: { viewCount: 1 } }
    ).catch(() => {})
  },

  // Client requests online status of specific users
  presence_query(ws, meta, data) {
    if (!data.userIds?.length) return
    db?.collection('users').find(
      { id: { $in: data.userIds.slice(0, 50) } },
      { projection: { id: 1, isOnline: 1, lastSeen: 1, _id: 0 } }
    ).toArray().then(users => {
      if (ws.readyState === 1) {
        ws.send(JSON.stringify({
          type: 'presence_result',
          data: { users },
          timestamp: new Date().toISOString(),
        }))
      }
    }).catch(() => {})
  },

  // Ping
  ping(ws) {
    if (ws.readyState === 1) {
      ws.send(JSON.stringify({ type: 'pong', timestamp: new Date().toISOString() }))
    }
  },
}

// ========== CONNECTION HANDLER ==========
function handleConnection(ws, request) {
  let authenticated = false
  let meta = null

  // Auth timeout: must authenticate within 10s
  const authTimer = setTimeout(() => {
    if (!authenticated) {
      ws.send(JSON.stringify({ type: 'error', data: { message: 'Authentication timeout' } }))
      ws.close(4001, 'Auth timeout')
    }
  }, AUTH_TIMEOUT)

  // Extract token from query string: ws://host:3001?token=xxx
  const url = new URL(request.url, `http://localhost:${WS_PORT}`)
  const token = url.searchParams.get('token')

  if (token) {
    // Auto-auth from query param
    authenticateToken(token).then(user => {
      if (!user) {
        clearTimeout(authTimer)
        ws.send(JSON.stringify({ type: 'error', data: { message: 'Invalid token' } }))
        ws.close(4003, 'Invalid token')
        return
      }
      clearTimeout(authTimer)
      authenticated = true
      meta = { userId: user.id, displayName: user.displayName, connectedAt: new Date() }
      connectionMeta.set(ws, meta)

      // Track connection
      if (!userConnections.has(user.id)) userConnections.set(user.id, new Set())
      userConnections.get(user.id).add(ws)

      // Set online
      setPresence(user.id, true)

      ws.send(JSON.stringify({
        type: 'authenticated',
        data: { userId: user.id, displayName: user.displayName, serverTime: new Date().toISOString() },
      }))
    }).catch(() => {
      clearTimeout(authTimer)
      ws.close(4003, 'Auth failed')
    })
  }

  // Message handler
  ws.on('message', (raw) => {
    try {
      const msg = JSON.parse(raw.toString())

      // If not yet authenticated, only accept auth messages
      if (!authenticated) {
        if (msg.type === 'auth' && msg.token) {
          authenticateToken(msg.token).then(user => {
            if (!user) {
              ws.send(JSON.stringify({ type: 'error', data: { message: 'Invalid token' } }))
              ws.close(4003, 'Invalid token')
              return
            }
            clearTimeout(authTimer)
            authenticated = true
            meta = { userId: user.id, displayName: user.displayName, connectedAt: new Date() }
            connectionMeta.set(ws, meta)
            if (!userConnections.has(user.id)) userConnections.set(user.id, new Set())
            userConnections.get(user.id).add(ws)
            setPresence(user.id, true)
            ws.send(JSON.stringify({
              type: 'authenticated',
              data: { userId: user.id, displayName: user.displayName, serverTime: new Date().toISOString() },
            }))
          }).catch(() => ws.close(4003, 'Auth failed'))
        }
        return
      }

      // Dispatch to handler
      const handler = messageHandlers[msg.type]
      if (handler) {
        handler(ws, meta, msg.data || {})
      }
    } catch {}
  })

  // Close handler
  ws.on('close', () => {
    clearTimeout(authTimer)
    if (meta) {
      const conns = userConnections.get(meta.userId)
      if (conns) {
        conns.delete(ws)
        if (conns.size === 0) {
          userConnections.delete(meta.userId)
          setPresence(meta.userId, false)
        }
      }
    }
  })

  ws.on('error', () => {})
}

// ========== STATS ==========
function getStats() {
  return {
    totalConnections: [...userConnections.values()].reduce((s, set) => s + set.size, 0),
    uniqueUsers: userConnections.size,
    redisMode: redisReady,
    uptime: process.uptime(),
  }
}

// ========== MAIN ==========
async function main() {
  console.log('[WS] Starting WebSocket server...')
  const mongoClient = await connectDb()
  await connectRedis()

  const wss = new WebSocketServer({ port: WS_PORT })

  wss.on('connection', handleConnection)

  // Heartbeat: detect dead connections
  const heartbeatInterval = setInterval(() => {
    for (const ws of wss.clients) {
      if (ws.isAlive === false) { ws.terminate(); continue }
      ws.isAlive = false
      ws.ping()
    }
  }, HEARTBEAT_INTERVAL)

  wss.on('close', () => clearInterval(heartbeatInterval))

  // Track pong responses
  wss.on('connection', (ws) => {
    ws.isAlive = true
    ws.on('pong', () => { ws.isAlive = true })
  })

  console.log(`[WS] WebSocket server running on port ${WS_PORT}`)
  console.log(`[WS] Connect: ws://localhost:${WS_PORT}?token=<auth_token>`)

  // Graceful shutdown
  process.on('SIGTERM', () => {
    console.log('[WS] Shutting down...')
    clearInterval(heartbeatInterval)
    wss.close()
    redisPub?.quit().catch(() => {})
    redisSub?.quit().catch(() => {})
    mongoClient.close()
    process.exit(0)
  })

  process.on('SIGINT', () => process.emit('SIGTERM'))
}

// Export for programmatic use by REST API handlers
export { pushToUser as wsNotify, getStats as wsStats }

// Run if executed directly
main().catch(err => {
  console.error('[WS] Fatal:', err)
  process.exit(1)
})
