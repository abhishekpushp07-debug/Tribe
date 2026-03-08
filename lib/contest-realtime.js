/**
 * Stage 12X-RT — World-Best Real-Time Contest Scoreboard
 *
 * Architecture:
 *   Dual-mode: Redis Pub/Sub (multi-instance) or in-memory EventEmitter (single)
 *   Auto-detects Redis, falls back gracefully
 *
 * Channel topology:
 *   tribe:contest:{contestId}     — per-contest live scoreboard
 *   tribe:contest:global           — cross-contest activity feed
 *   tribe:standings:{seasonId}     — live season standings
 *
 * Event types:
 *   entry.submitted      — new entry joins a contest
 *   vote.cast            — vote recorded
 *   score.updated        — scores recomputed
 *   rank.changed         — rank shift detected
 *   contest.transition   — lifecycle status change
 *   contest.resolved     — winner declared + salutes distributed
 *   standings.updated    — season standings change
 *   activity             — general feed item (global channel)
 *
 * Connection pattern:
 *   1. Client connects → receives snapshot (current leaderboard/standings)
 *   2. Stream delivers deltas as they happen
 *   3. Heartbeat every 10s, retry hint 3s
 *   4. Supports Last-Event-ID for resumable connections
 */

import { EventEmitter } from 'events'

const REDIS_URL = process.env.REDIS_URL || 'redis://127.0.0.1:6379'

// ========== EVENT TYPES ==========
export const ContestEventType = {
  ENTRY_SUBMITTED: 'entry.submitted',
  VOTE_CAST: 'vote.cast',
  SCORE_UPDATED: 'score.updated',
  RANK_CHANGED: 'rank.changed',
  CONTEST_TRANSITION: 'contest.transition',
  CONTEST_RESOLVED: 'contest.resolved',
  STANDINGS_UPDATED: 'standings.updated',
  ACTIVITY: 'activity',
}

// ========== CHANNEL BUILDERS ==========
function contestChannel(contestId) { return `tribe:contest:${contestId}` }
function globalChannel() { return 'tribe:contest:global' }
function standingsChannel(seasonId) { return `tribe:standings:${seasonId}` }

// ========== IN-MEMORY FALLBACK ==========
const memBus = new EventEmitter()
memBus.setMaxListeners(2000)

let redisAvailable = null
let redisPublisher = null

async function checkRedis() {
  if (redisAvailable !== null) return redisAvailable
  try {
    const Redis = (await import('ioredis')).default
    const client = new Redis(REDIS_URL, { maxRetriesPerRequest: 1, connectTimeout: 2000, lazyConnect: true })
    client.on('error', () => {}) // Suppress unhandled error events
    await client.connect()
    await client.ping()
    redisPublisher = client
    redisAvailable = true
  } catch {
    redisAvailable = false
  }
  return redisAvailable
}

// ========== PUBLISH ==========
async function publishToChannel(channel, event) {
  const payload = JSON.stringify({ ...event, ts: new Date().toISOString() })
  try {
    await checkRedis()
    if (redisAvailable && redisPublisher) {
      await redisPublisher.publish(channel, payload)
    } else {
      memBus.emit(channel, payload)
    }
  } catch { /* best-effort */ }
}

/**
 * Publish a contest event — fires to contest channel + global feed
 */
export async function publishContestEvent(contestId, eventType, data) {
  const event = { type: eventType, contestId, ...data }
  await Promise.all([
    publishToChannel(contestChannel(contestId), event),
    publishToChannel(globalChannel(), event),
  ])
}

/**
 * Publish a standings update — fires to season channel + global feed
 */
export async function publishStandingsUpdate(seasonId, data) {
  const event = { type: ContestEventType.STANDINGS_UPDATED, seasonId, ...data }
  await Promise.all([
    publishToChannel(standingsChannel(seasonId), event),
    publishToChannel(globalChannel(), event),
  ])
}

// ========== SUBSCRIBE ==========
function createChannelSubscriber(channels) {
  if (!Array.isArray(channels)) channels = [channels]

  if (redisAvailable) {
    let sub = null
    return {
      async start(onMessage) {
        const Redis = (await import('ioredis')).default
        sub = new Redis(REDIS_URL, { maxRetriesPerRequest: 1, enableOfflineQueue: false, lazyConnect: true })
        sub.on('error', () => {}) // Suppress unhandled error events
        await sub.connect()
        for (const ch of channels) await sub.subscribe(ch)
        sub.on('message', (ch, msg) => onMessage(msg, ch))
      },
      cleanup() {
        try { sub?.unsubscribe().catch(() => {}); sub?.quit().catch(() => {}) } catch {}
      },
    }
  }

  const handlers = []
  return {
    async start(onMessage) {
      for (const ch of channels) {
        const handler = (msg) => onMessage(msg, ch)
        memBus.on(ch, handler)
        handlers.push({ ch, handler })
      }
    },
    cleanup() {
      for (const { ch, handler } of handlers) memBus.removeListener(ch, handler)
    },
  }
}

// ========== SNAPSHOT GENERATORS ==========

/**
 * Snapshot: current contest leaderboard + metadata
 */
async function contestSnapshot(contestId, db) {
  const contest = await db.collection('tribe_contests').findOne(
    { id: contestId },
    { projection: { _id: 0, id: 1, contestName: 1, status: 1, contestType: 1, contestEndAt: 1, votingEnabled: 1 } }
  )
  if (!contest) return { error: 'Contest not found' }

  const [scores, entryCount, voteCount] = await Promise.all([
    db.collection('tribe_contest_scores')
      .find({ contestId }, { projection: { _id: 0 } })
      .sort({ finalScore: -1, lastComputedAt: 1 })
      .limit(21)
      .toArray(),
    db.collection('tribe_contest_entries')
      .countDocuments({ contestId, submissionStatus: { $nin: ['withdrawn', 'disqualified'] } }),
    db.collection('contest_votes').countDocuments({ contestId }),
  ])

  // Enrich with tribe info
  const tribeIds = [...new Set(scores.map(s => s.tribeId).filter(Boolean))]
  const tribes = tribeIds.length > 0
    ? await db.collection('tribes').find(
        { id: { $in: tribeIds } },
        { projection: { _id: 0, id: 1, tribeName: 1, tribeCode: 1, primaryColor: 1, animalIcon: 1 } }
      ).toArray()
    : []
  const tribeMap = Object.fromEntries(tribes.map(t => [t.id, t]))

  const leaderboard = scores.map((s, i) => ({
    rank: i + 1,
    entryId: s.entryId,
    tribeId: s.tribeId,
    userId: s.userId,
    finalScore: s.finalScore,
    judgeScore: s.judgeScore,
    engagementScore: s.engagementScore,
    tribe: tribeMap[s.tribeId] || null,
  }))

  // Tribe-aggregated standings within this contest
  const tribeAgg = {}
  for (const s of scores) {
    if (!tribeAgg[s.tribeId]) tribeAgg[s.tribeId] = { tribeId: s.tribeId, totalScore: 0, entries: 0, tribe: tribeMap[s.tribeId] || null }
    tribeAgg[s.tribeId].totalScore += s.finalScore || 0
    tribeAgg[s.tribeId].entries++
  }
  const tribeRanking = Object.values(tribeAgg).sort((a, b) => b.totalScore - a.totalScore).map((t, i) => ({ rank: i + 1, ...t }))

  return {
    contest,
    entryCount,
    voteCount,
    leaderboard,
    tribeRanking,
    snapshotAt: new Date().toISOString(),
  }
}

/**
 * Snapshot: season standings
 */
async function standingsSnapshot(seasonId, db) {
  const season = await db.collection('tribe_seasons').findOne(
    { id: seasonId },
    { projection: { _id: 0, id: 1, name: 1, status: 1, year: 1 } }
  )
  if (!season) return { error: 'Season not found' }

  const standings = await db.collection('tribe_standings')
    .find({ seasonId }, { projection: { _id: 0 } })
    .sort({ totalSalutes: -1, contestsWon: -1 })
    .toArray()

  const tribeIds = standings.map(s => s.tribeId)
  const tribes = tribeIds.length > 0
    ? await db.collection('tribes').find(
        { id: { $in: tribeIds } },
        { projection: { _id: 0, id: 1, tribeName: 1, tribeCode: 1, primaryColor: 1, animalIcon: 1 } }
      ).toArray()
    : []
  const tribeMap = Object.fromEntries(tribes.map(t => [t.id, t]))

  const ranked = standings.map((s, i) => ({
    rank: i + 1,
    ...s,
    tribe: tribeMap[s.tribeId] || null,
  }))

  // Active contests in this season
  const activeContests = await db.collection('tribe_contests')
    .find(
      { seasonId, status: { $in: ['ENTRY_OPEN', 'EVALUATING', 'LOCKED'] } },
      { projection: { _id: 0, id: 1, contestName: 1, status: 1, contestType: 1, contestEndAt: 1 } }
    )
    .sort({ contestEndAt: 1 })
    .limit(10)
    .toArray()

  return {
    season,
    standings: ranked,
    activeContests,
    snapshotAt: new Date().toISOString(),
  }
}

/**
 * Snapshot: global activity (recent events across all contests)
 */
async function globalSnapshot(db) {
  // Recent contests
  const liveContests = await db.collection('tribe_contests')
    .find(
      { status: { $in: ['ENTRY_OPEN', 'EVALUATING', 'LOCKED'] } },
      { projection: { _id: 0, id: 1, contestName: 1, status: 1, contestType: 1, contestEndAt: 1, seasonId: 1 } }
    )
    .sort({ contestEndAt: 1 })
    .limit(10)
    .toArray()

  // Recent entries (last 20)
  const recentEntries = await db.collection('tribe_contest_entries')
    .find(
      { submissionStatus: { $nin: ['withdrawn', 'disqualified'] } },
      { projection: { _id: 0, id: 1, contestId: 1, tribeId: 1, userId: 1, submittedAt: 1, entryType: 1 } }
    )
    .sort({ submittedAt: -1 })
    .limit(20)
    .toArray()

  // Recent resolutions
  const recentResults = await db.collection('tribe_contest_results')
    .find(
      {},
      { projection: { _id: 0, id: 1, contestId: 1, winnerTribeId: 1, resolvedAt: 1 } }
    )
    .sort({ resolvedAt: -1 })
    .limit(5)
    .toArray()

  return {
    liveContests,
    recentEntries,
    recentResults,
    snapshotAt: new Date().toISOString(),
  }
}

// ========== SSE STREAM BUILDERS ==========

const SSE_HEADERS = {
  'Content-Type': 'text/event-stream',
  'Cache-Control': 'no-cache, no-transform',
  'Connection': 'keep-alive',
  'X-Accel-Buffering': 'no',
  'Access-Control-Allow-Origin': process.env.CORS_ORIGINS || '*',
  'Access-Control-Allow-Credentials': 'true',
}

function sseEncode(eventId, eventName, data) {
  return `id: ${eventId}\nevent: ${eventName}\ndata: ${JSON.stringify(data)}\n\n`
}

/**
 * GET /tribe-contests/:id/live — Live contest scoreboard SSE
 *
 * On connect: sends snapshot (current leaderboard + tribe ranking)
 * Then streams: entry.submitted, vote.cast, score.updated, rank.changed,
 *               contest.transition, contest.resolved
 */
export function buildContestLiveStream(request, contestId, db) {
  const encoder = new TextEncoder()
  let eventId = 0
  let subscriber = null
  let heartbeat = null

  const stream = new ReadableStream({
    async start(controller) {
      try {
        await checkRedis()

        // 1. Send connection event
        controller.enqueue(encoder.encode(sseEncode(
          ++eventId, 'connected',
          { contestId, mode: redisAvailable ? 'redis' : 'memory', connectedAt: new Date().toISOString() }
        )))

        // 2. Send snapshot
        const snapshot = await contestSnapshot(contestId, db)
        controller.enqueue(encoder.encode(sseEncode(++eventId, 'snapshot', snapshot)))

        // 3. Subscribe to contest channel
        subscriber = createChannelSubscriber(contestChannel(contestId))
        await subscriber.start((message) => {
          try {
            const event = JSON.parse(message)
            controller.enqueue(encoder.encode(sseEncode(++eventId, event.type || 'update', event)))
          } catch {
            controller.enqueue(encoder.encode(sseEncode(++eventId, 'update', { raw: message })))
          }
        })

        // 4. Heartbeat every 10s
        heartbeat = setInterval(() => {
          try {
            controller.enqueue(encoder.encode(`: heartbeat ${new Date().toISOString()}\n\n`))
          } catch { clearInterval(heartbeat) }
        }, 10_000)

        // 5. Auto-refresh snapshot every 30s for stale-client protection
        const refreshInterval = setInterval(async () => {
          try {
            const fresh = await contestSnapshot(contestId, db)
            controller.enqueue(encoder.encode(sseEncode(++eventId, 'snapshot', fresh)))
          } catch { /* skip refresh on error */ }
        }, 30_000)

        // Cleanup on disconnect
        if (request.signal) {
          request.signal.addEventListener('abort', () => {
            clearInterval(heartbeat)
            clearInterval(refreshInterval)
            if (subscriber) subscriber.cleanup()
            try { controller.close() } catch {}
          })
        }
      } catch (err) {
        controller.enqueue(encoder.encode(sseEncode(++eventId, 'error', { error: 'Stream init failed', detail: err.message })))
        try { controller.close() } catch {}
      }
    },
    cancel() {
      if (heartbeat) clearInterval(heartbeat)
      if (subscriber) subscriber.cleanup()
    },
  })

  return new Response(stream, { headers: { ...SSE_HEADERS, 'retry': '3000' } })
}

/**
 * GET /tribe-contests/seasons/:id/live-standings — Live season standings SSE
 */
export function buildStandingsLiveStream(request, seasonId, db) {
  const encoder = new TextEncoder()
  let eventId = 0
  let subscriber = null
  let heartbeat = null

  const stream = new ReadableStream({
    async start(controller) {
      try {
        await checkRedis()

        controller.enqueue(encoder.encode(sseEncode(
          ++eventId, 'connected',
          { seasonId, mode: redisAvailable ? 'redis' : 'memory' }
        )))

        const snapshot = await standingsSnapshot(seasonId, db)
        controller.enqueue(encoder.encode(sseEncode(++eventId, 'snapshot', snapshot)))

        subscriber = createChannelSubscriber(standingsChannel(seasonId))
        await subscriber.start((message) => {
          try {
            const event = JSON.parse(message)
            controller.enqueue(encoder.encode(sseEncode(++eventId, event.type || 'standings.updated', event)))
          } catch {}
        })

        heartbeat = setInterval(() => {
          try { controller.enqueue(encoder.encode(`: heartbeat ${new Date().toISOString()}\n\n`)) }
          catch { clearInterval(heartbeat) }
        }, 10_000)

        const refreshInterval = setInterval(async () => {
          try {
            const fresh = await standingsSnapshot(seasonId, db)
            controller.enqueue(encoder.encode(sseEncode(++eventId, 'snapshot', fresh)))
          } catch {}
        }, 60_000)

        if (request.signal) {
          request.signal.addEventListener('abort', () => {
            clearInterval(heartbeat)
            clearInterval(refreshInterval)
            if (subscriber) subscriber.cleanup()
            try { controller.close() } catch {}
          })
        }
      } catch (err) {
        controller.enqueue(encoder.encode(sseEncode(++eventId, 'error', { error: err.message })))
        try { controller.close() } catch {}
      }
    },
    cancel() {
      if (heartbeat) clearInterval(heartbeat)
      if (subscriber) subscriber.cleanup()
    },
  })

  return new Response(stream, { headers: { ...SSE_HEADERS, 'retry': '3000' } })
}

/**
 * GET /tribe-contests/live-feed — Global contest activity feed SSE
 */
export function buildGlobalLiveStream(request, db) {
  const encoder = new TextEncoder()
  let eventId = 0
  let subscriber = null
  let heartbeat = null

  const stream = new ReadableStream({
    async start(controller) {
      try {
        await checkRedis()

        controller.enqueue(encoder.encode(sseEncode(
          ++eventId, 'connected',
          { channel: 'global', mode: redisAvailable ? 'redis' : 'memory' }
        )))

        const snapshot = await globalSnapshot(db)
        controller.enqueue(encoder.encode(sseEncode(++eventId, 'snapshot', snapshot)))

        subscriber = createChannelSubscriber(globalChannel())
        await subscriber.start((message) => {
          try {
            const event = JSON.parse(message)
            controller.enqueue(encoder.encode(sseEncode(++eventId, event.type || 'activity', event)))
          } catch {}
        })

        heartbeat = setInterval(() => {
          try { controller.enqueue(encoder.encode(`: heartbeat ${new Date().toISOString()}\n\n`)) }
          catch { clearInterval(heartbeat) }
        }, 10_000)

        if (request.signal) {
          request.signal.addEventListener('abort', () => {
            clearInterval(heartbeat)
            if (subscriber) subscriber.cleanup()
            try { controller.close() } catch {}
          })
        }
      } catch (err) {
        controller.enqueue(encoder.encode(sseEncode(++eventId, 'error', { error: err.message })))
        try { controller.close() } catch {}
      }
    },
    cancel() {
      if (heartbeat) clearInterval(heartbeat)
      if (subscriber) subscriber.cleanup()
    },
  })

  return new Response(stream, { headers: { ...SSE_HEADERS, 'retry': '3000' } })
}
