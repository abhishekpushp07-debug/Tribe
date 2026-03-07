/**
 * Tribe — Production Cache Layer
 * 
 * In-memory cache with TTL, versioning, stampede protection, and event-driven invalidation.
 * Drop-in replacement path to Redis documented below.
 * 
 * REDIS MIGRATION PATH:
 * Replace CacheStore internals with ioredis client. Key format and invalidation
 * logic remain identical. See cache-policy-matrix.md for the full plan.
 */

// ========== CACHE STORE ==========
class CacheStore {
  constructor() {
    this.store = new Map()
    this.locks = new Map() // stampede protection
    this.stats = { hits: 0, misses: 0, sets: 0, invalidations: 0 }
    this.VERSION = 'v1' // cache key version prefix

    // Cleanup expired entries every 30s
    setInterval(() => this._cleanup(), 30_000)
  }

  _key(namespace, id) {
    return `${this.VERSION}:${namespace}:${id}`
  }

  get(namespace, id) {
    const key = this._key(namespace, id)
    const entry = this.store.get(key)
    if (!entry) {
      this.stats.misses++
      return null
    }
    if (Date.now() > entry.expiresAt) {
      this.store.delete(key)
      this.stats.misses++
      return null
    }
    this.stats.hits++
    return entry.value
  }

  set(namespace, id, value, ttlMs) {
    const key = this._key(namespace, id)
    this.store.set(key, {
      value,
      expiresAt: Date.now() + ttlMs,
      createdAt: Date.now(),
    })
    this.stats.sets++
  }

  // Stampede protection: only one caller computes, others wait
  async getOrCompute(namespace, id, computeFn, ttlMs) {
    const cached = this.get(namespace, id)
    if (cached !== null) return cached

    const key = this._key(namespace, id)

    // Check if someone else is already computing
    if (this.locks.has(key)) {
      return this.locks.get(key)
    }

    const promise = computeFn().then(result => {
      this.set(namespace, id, result, ttlMs)
      this.locks.delete(key)
      return result
    }).catch(err => {
      this.locks.delete(key)
      throw err
    })

    this.locks.set(key, promise)
    return promise
  }

  invalidate(namespace, id) {
    if (id) {
      this.store.delete(this._key(namespace, id))
    } else {
      // Invalidate all keys in namespace
      const prefix = `${this.VERSION}:${namespace}:`
      for (const key of this.store.keys()) {
        if (key.startsWith(prefix)) this.store.delete(key)
      }
    }
    this.stats.invalidations++
  }

  // Invalidate by pattern (e.g., all feeds for a college)
  invalidatePattern(pattern) {
    for (const key of this.store.keys()) {
      if (key.includes(pattern)) this.store.delete(key)
    }
    this.stats.invalidations++
  }

  getStats() {
    const total = this.stats.hits + this.stats.misses
    return {
      ...this.stats,
      hitRate: total > 0 ? (this.stats.hits / total * 100).toFixed(1) + '%' : '0%',
      size: this.store.size,
      locksActive: this.locks.size,
    }
  }

  _cleanup() {
    const now = Date.now()
    for (const [key, entry] of this.store) {
      if (now > entry.expiresAt) this.store.delete(key)
    }
  }
}

// Singleton cache instance
const cache = new CacheStore()

// ========== TTL CONSTANTS (ms) ==========
export const CacheTTL = {
  PUBLIC_FEED: 15_000,       // 15s — high write, short TTL
  COLLEGE_FEED: 30_000,      // 30s — medium write
  HOUSE_FEED: 30_000,        // 30s — medium write
  REELS_FEED: 30_000,        // 30s
  HOUSE_LEADERBOARD: 60_000, // 60s — recomputed on score change
  HOUSES_LIST: 300_000,      // 5min — rarely changes
  COLLEGE_SEARCH: 600_000,   // 10min — static data
  ADMIN_STATS: 30_000,       // 30s — dashboard polling
  USER_PROFILE: 60_000,      // 60s — user detail cache
  CONSENT_NOTICE: 3600_000,  // 1hr — rarely changes
}

// ========== CACHE NAMESPACES ==========
export const CacheNS = {
  PUBLIC_FEED: 'feed:public',
  COLLEGE_FEED: 'feed:college',
  HOUSE_FEED: 'feed:house',
  REELS_FEED: 'feed:reels',
  HOUSE_LEADERBOARD: 'house:leaderboard',
  HOUSES_LIST: 'house:list',
  COLLEGE_SEARCH: 'college:search',
  ADMIN_STATS: 'admin:stats',
  USER_PROFILE: 'user:profile',
  CONSENT_NOTICE: 'legal:consent',
}

// ========== EVENT-DRIVEN INVALIDATION ==========
export function invalidateOnEvent(event, context = {}) {
  switch (event) {
    case 'POST_CREATED':
    case 'POST_DELETED':
      cache.invalidate(CacheNS.PUBLIC_FEED)
      cache.invalidate(CacheNS.ADMIN_STATS)
      if (context.collegeId) cache.invalidate(CacheNS.COLLEGE_FEED, context.collegeId)
      if (context.houseId) cache.invalidate(CacheNS.HOUSE_FEED, context.houseId)
      if (context.kind === 'REEL') cache.invalidate(CacheNS.REELS_FEED)
      break

    case 'FOLLOW_CHANGED':
      // Following feed is per-user, not cached globally
      if (context.userId) cache.invalidate(CacheNS.USER_PROFILE, context.userId)
      if (context.targetId) cache.invalidate(CacheNS.USER_PROFILE, context.targetId)
      break

    case 'REACTION_CHANGED':
      // Individual post stats not cached; feed caches have short TTL
      break

    case 'COMMENT_CREATED':
    case 'COMMENT_DELETED':
      // Comments are per-post, not globally cached
      break

    case 'REPORT_CREATED':
    case 'MODERATION_ACTION':
      cache.invalidate(CacheNS.PUBLIC_FEED)
      cache.invalidate(CacheNS.ADMIN_STATS)
      break

    case 'STRIKE_ISSUED':
    case 'USER_SUSPENDED':
      if (context.userId) cache.invalidate(CacheNS.USER_PROFILE, context.userId)
      cache.invalidate(CacheNS.ADMIN_STATS)
      break

    case 'LEADERBOARD_CHANGED':
      cache.invalidate(CacheNS.HOUSE_LEADERBOARD)
      break

    case 'HOUSE_POINTS_CHANGED':
      cache.invalidate(CacheNS.HOUSE_LEADERBOARD)
      cache.invalidate(CacheNS.HOUSES_LIST)
      break
  }
}

// ========== EXPORTS ==========
export { cache }
export default cache
