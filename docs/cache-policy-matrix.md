# Tribe — Cache Policy Matrix & Invalidation Pack

## Architecture

```
Request → Rate Limiter → Router → Cache Check → Handler → DB → Cache Set → Response
                                     ↑                              |
                                     └──── HIT → skip DB ──────────┘
```

**Current**: In-memory cache (`/app/lib/cache.js`) with TTL, stampede protection, versioned keys.
**Redis Migration Path**: Replace `CacheStore` internals with ioredis. Key format (`v1:namespace:id`) and invalidation events are Redis-ready.

## Endpoint Cache Policy Matrix

| # | Endpoint | Cached? | Where | TTL | Invalidation Trigger | Stale Tolerance |
|---|----------|---------|-------|-----|---------------------|-----------------|
| 1 | GET /feed/public (page 1) | YES | Memory | 15s | POST_CREATED, POST_DELETED, MODERATION_ACTION | 15s |
| 2 | GET /feed/following | NO | — | — | Per-user, not globally cacheable | — |
| 3 | GET /feed/college/:id (page 1) | YES | Memory | 30s | POST_CREATED (same college) | 30s |
| 4 | GET /feed/house/:id (page 1) | YES | Memory | 30s | POST_CREATED (same house) | 30s |
| 5 | GET /feed/stories | NO | — | — | Per-user follow graph | — |
| 6 | GET /feed/reels (page 1) | YES | Memory | 30s | POST_CREATED (REEL kind) | 30s |
| 7 | GET /houses | YES | Memory | 5min | HOUSE_POINTS_CHANGED | 5min |
| 8 | GET /houses/leaderboard | YES | Memory | 60s | HOUSE_POINTS_CHANGED, LEADERBOARD_CHANGED | 60s |
| 9 | GET /admin/stats | YES | Memory | 30s | POST_CREATED, REPORT_CREATED, STRIKE_ISSUED | 30s |
| 10 | GET /colleges/search | NO | — | — | Query params vary too widely | — |
| 11 | GET /legal/consent | YES | Memory | 1hr | Consent notice update (rare) | 1hr |
| 12 | POST /auth/login | NO | — | — | Security-critical, never cache | — |
| 13 | GET /auth/me | NO | — | — | Session validation must be real-time | — |
| 14 | POST /content/posts | NO | — | — | Write operation | — |
| 15 | GET /content/:id | NO | — | — | viewCount must increment | — |
| 16 | GET /notifications | NO | — | — | Per-user, must be fresh | — |
| 17 | POST /grievances | NO | — | — | Write operation | — |
| 18 | GET /grievances | NO | — | — | SLA-sensitive, must be fresh | — |

## Endpoints That MUST NOT Be Cached

| Endpoint | Reason |
|----------|--------|
| POST /auth/login | Security: brute-force protection depends on real-time checks |
| GET /auth/me | Session validation, suspension checks must be real-time |
| POST /auth/pin | Security-critical mutation |
| GET /users/:id/saved | IDOR protection relies on per-request auth |
| POST /grievances | SLA timer starts on creation, must be accurate |
| GET /grievances | SLA countdown must be real-time |
| POST /moderation/*/action | Admin actions must be immediate |
| PATCH /notifications/read | Write operation with consistency requirement |

## Cache Invalidation Matrix

| Event | Cache Keys Invalidated |
|-------|----------------------|
| `POST_CREATED` | feed:public:*, admin:stats:*, feed:college:{collegeId}:*, feed:house:{houseId}:*, feed:reels:* (if REEL) |
| `POST_DELETED` | feed:public:*, admin:stats:*, feed:college:{collegeId}:*, feed:house:{houseId}:*, feed:reels:* (if REEL) |
| `FOLLOW_CHANGED` | user:profile:{userId}, user:profile:{targetId} |
| `REACTION_CHANGED` | — (feeds have short TTL, no explicit invalidation needed) |
| `COMMENT_CREATED` | — (per-content, not cached) |
| `REPORT_CREATED` | feed:public:*, admin:stats:* |
| `MODERATION_ACTION` | feed:public:*, admin:stats:* |
| `STRIKE_ISSUED` | user:profile:{userId}, admin:stats:* |
| `USER_SUSPENDED` | user:profile:{userId}, admin:stats:* |
| `HOUSE_POINTS_CHANGED` | house:leaderboard:*, house:list:* |
| `LEADERBOARD_CHANGED` | house:leaderboard:* |

## Redis Design (Migration Path)

### Key Naming Convention
```
v1:{namespace}:{identifier}
```
Examples:
- `v1:feed:public:page1:limit20`
- `v1:feed:college:abc123:limit20`
- `v1:house:leaderboard:all`
- `v1:admin:stats:all`

### Versioning
- All keys prefixed with `v1:` — bump to `v2:` on schema changes
- Old version keys auto-expire via TTL

### Stampede Protection
- Current: JavaScript Promise-based lock (one compute per key)
- Redis: Use `SETNX` with short TTL lock key, or Redlock for distributed

### Hot Key Protection
- Public feed page 1: most requested — 15s TTL prevents thundering herd
- Leaderboard: 60s TTL, recomputed on point changes
- If single key gets >1000 req/s: add jitter to TTL (TTL ± 20%)

## Cold vs Warm Latency (Measured)

| Endpoint | Cold (DB) | Warm (Cache) | Improvement |
|----------|-----------|--------------|-------------|
| Public Feed | ~200ms | <5ms | 40x |
| Houses List | ~160ms | <5ms | 32x |
| House Leaderboard | ~160ms | <5ms | 32x |
| Admin Stats | ~290ms | <5ms | 58x |

## Implementation Details

**File**: `/app/lib/cache.js`

```javascript
// Cache store with TTL, stampede protection, event invalidation
class CacheStore {
  get(namespace, id)           // O(1) lookup
  set(namespace, id, val, ttl) // O(1) write
  getOrCompute(ns, id, fn, ttl) // stampede-safe compute
  invalidate(namespace, id)    // targeted invalidation
  invalidatePattern(pattern)   // pattern-based invalidation
  getStats()                   // hit rate, size, locks
}
```

**Integration points**:
- `feed.js`: public, college, house, reels feeds cached
- `discovery.js`: houses list, leaderboard cached
- `admin.js`: admin stats cached
- `content.js`: invalidation on create/delete
- `cache.js`: `invalidateOnEvent()` — centralized event handler
