# Tribe — System Architecture Deep Dive

> Complete architecture reference for the Tribe social media backend.
> Total codebase: 26,000+ lines across 22 handlers, 6 services, and core libraries.

---

## Table of Contents
1. [High-Level Architecture](#1-high-level-architecture)
2. [Request Lifecycle](#2-request-lifecycle)
3. [Directory Structure](#3-directory-structure)
4. [Handler Layer](#4-handler-layer)
5. [Service Layer](#5-service-layer)
6. [Database Layer](#6-database-layer)
7. [Cache Layer](#7-cache-layer)
8. [Real-Time Layer (SSE)](#8-real-time-layer-sse)
9. [Media Pipeline](#9-media-pipeline)
10. [Authentication Middleware](#10-authentication-middleware)
11. [Error Handling Architecture](#11-error-handling-architecture)
12. [Scalability Design](#12-scalability-design)

---

## 1. High-Level Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    CLIENT (Android/iOS/Web)               │
└─────────────────────────┬────────────────────────────────┘
                          │ HTTPS + Bearer Token
                          ▼
┌──────────────────────────────────────────────────────────┐
│                  NEXT.JS API ROUTES                       │
│            /app/api/[[...path]]/route.js                  │
│                   (Central Router)                        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────┐   │
│  │  Auth   │ │ Content │ │  Feed   │ │   Social    │   │
│  │ Handler │ │ Handler │ │ Handler │ │   Handler   │   │
│  └────┬────┘ └────┬────┘ └────┬────┘ └──────┬──────┘   │
│       │           │           │              │          │
│  ┌────┴────┐ ┌────┴────┐ ┌────┴────┐ ┌──────┴──────┐   │
│  │ Stories │ │  Reels  │ │  Pages  │ │   Events    │   │
│  │ Handler │ │ Handler │ │ Handler │ │   Handler   │   │
│  └────┬────┘ └────┬────┘ └────┬────┘ └──────┬──────┘   │
│       │           │           │              │          │
│  ┌────┴────┐ ┌────┴────┐ ┌────┴────┐ ┌──────┴──────┐   │
│  │ Tribes  │ │ Search  │ │ Admin   │ │   +14 more  │   │
│  │ Handler │ │ Handler │ │ Handler │ │   Handlers  │   │
│  └─────────┘ └─────────┘ └─────────┘ └─────────────┘   │
│                          │                               │
├──────────────────────────┼───────────────────────────────┤
│                  SERVICE LAYER                            │
│  ┌───────────┐ ┌────────────┐ ┌───────────────────┐     │
│  │   Feed    │ │   Story    │ │    Anti-Abuse     │     │
│  │  Ranking  │ │  Service   │ │     Service       │     │
│  └───────────┘ └────────────┘ └───────────────────┘     │
│  ┌───────────┐ ┌────────────┐ ┌───────────────────┐     │
│  │  Scoring  │ │   Cache    │ │    Realtime       │     │
│  │  Engine   │ │   Utils    │ │    (SSE/Redis)    │     │
│  └───────────┘ └────────────┘ └───────────────────┘     │
├──────────────────────────────────────────────────────────┤
│                  DATA LAYER                               │
│  ┌───────────┐ ┌────────────┐ ┌───────────────────┐     │
│  │  MongoDB  │ │   Redis    │ │     Supabase      │     │
│  │  (95 col) │ │  (Cache)   │ │    (Media CDN)    │     │
│  └───────────┘ └────────────┘ └───────────────────┘     │
└──────────────────────────────────────────────────────────┘
```

### Tech Stack
| Component | Technology | Purpose |
|-----------|-----------|----------|
| Runtime | Next.js 14 (Node.js) | API routes, server-side logic |
| Database | MongoDB | Primary data store (95 collections) |
| Cache | Redis (ioredis) | Query caching, rate limiting, real-time pub/sub |
| Media Storage | Supabase Storage | Image/video CDN with signed URLs |
| Video Processing | FFmpeg | HLS adaptive bitrate transcoding |
| Testing | pytest (Python) | 121 regression tests |

---

## 2. Request Lifecycle

```
Client Request
  │
  ▼
1. Next.js Route Handler (/app/api/[[...path]]/route.js)
  │
  ▼
2. Parse path segments: /api/{resource}/{id?}/{action?}
  │
  ▼
3. Authentication Check
   ├── Extract Bearer token from Authorization header
   ├── Validate token against sessions collection
   ├── Attach user object to request context
   └── If 401: Return error (unless public endpoint)
  │
  ▼
4. Route Delegation
   ├── Match first path segment to handler file
   │   e.g., /api/stories/... → stories.js handler
   ├── Handler matches sub-route + HTTP method
   └── Execute business logic
  │
  ▼
5. Cache Check (for read paths)
   ├── Redis GET with namespace key
   ├── If HIT: Return cached response
   └── If MISS: Continue to database
  │
  ▼
6. Database Query
   ├── MongoDB query/aggregation
   ├── Populate cache on read
   └── Invalidate cache on write
  │
  ▼
7. Response Enrichment
   ├── Sanitize user objects (remove pinHash, etc.)
   ├── Add viewer-specific flags (viewerHasLiked, etc.)
   └── Add pagination metadata
  │
  ▼
8. Response Headers
   ├── x-contract-version: v2
   ├── x-request-id: <uuid>
   └── Content-Type: application/json
  │
  ▼
Client Response
```

---

## 3. Directory Structure

```
/app/
├── app/
│   └── api/
│       └── [[...path]]/
│           └── route.js          ← Central router (702 lines)
├── lib/
│   ├── handlers/                 ← 22 handler files
│   │   ├── auth.js               (544 lines) — Auth, sessions, PIN
│   │   ├── onboarding.js         (153 lines) — Onboarding flow
│   │   ├── users.js              (531 lines) — Profiles, settings
│   │   ├── content.js            (750 lines) — Posts, polls, threads
│   │   ├── feed.js               (823 lines) — All feed types
│   │   ├── social.js             (887 lines) — Like, follow, share
│   │   ├── stories.js            (2017 lines) — Stories system
│   │   ├── reels.js              (2156 lines) — Reels system
│   │   ├── pages.js              (1296 lines) — Pages system
│   │   ├── events.js             (934 lines) — Events system
│   │   ├── tribes.js             (1235 lines) — Tribes system
│   │   ├── tribe-contests.js     (1500+ lines) — Contest lifecycle
│   │   ├── search.js             (421 lines) — Search & autocomplete
│   │   ├── notifications.js      (500+ lines) — Notifications
│   │   ├── follow-requests.js    (400+ lines) — Private account flow
│   │   ├── analytics.js          (550+ lines) — Creator analytics
│   │   ├── media.js              (400+ lines) — Upload pipeline
│   │   ├── media-cleanup.js      (300+ lines) — Orphan cleanup
│   │   ├── transcode.js          (500+ lines) — Video transcoding
│   │   ├── discovery.js          (300+ lines) — Colleges, houses
│   │   ├── admin.js              (600+ lines) — Admin tools
│   │   ├── board-notices.js      (700+ lines) — Notices + tags
│   │   ├── governance.js         (500+ lines) — Board governance
│   │   ├── stages.js             (2800+ lines) — Claims, distribution, resources
│   │   ├── quality.js            (300+ lines) — Quality scoring
│   │   ├── recommendations.js    (300+ lines) — Content recommendations
│   │   ├── activity.js           (250+ lines) — Activity status
│   │   └── suggestions.js        (250+ lines) — Smart suggestions
│   ├── services/
│   │   ├── feed-ranking.js       (331 lines) — Smart Feed Algorithm
│   │   ├── story-service.js      (479 lines) — Story business logic
│   │   ├── scoring.js            (267 lines) — Tribe engagement scoring
│   │   ├── anti-abuse-service.js (227 lines) — Anti-abuse detection
│   │   ├── notification-publisher.js — Notification dispatch
│   │   └── event-publisher.js    — SSE event publishing
│   ├── auth-utils.js             (472 lines) — Token management, sanitization
│   ├── constants.js              (308 lines) — Houses, roles, categories
│   ├── tribe-constants.js        (273 lines) — 21 tribes data
│   ├── realtime.js               (177 lines) — SSE infrastructure
│   ├── cache.js                  (340 lines) — Redis cache layer
│   └── page-permissions.js       (78 lines) — Page RBAC
├── backend/
│   └── tests/                    ← 19 test files, 121 tests
├── docs/                         ← This documentation suite
├── API_DOCS.md                   ← API reference (4,439 lines)
├── DATA_MODELS.md                ← Schema reference (1,082 lines)
├── ANDROID_GUIDE.md              ← Mobile guide (905 lines)
├── CONSTANTS_REFERENCE.md        ← Enums reference (754 lines)
└── FEATURE_SPECS.md              ← Business logic (625 lines)
```

---

## 4. Handler Layer

Each handler file exports a single `handle(req, db, user)` function that:
1. Receives the parsed request (method, path segments, body, query params)
2. Has access to the MongoDB database instance
3. Has the authenticated user (or null for public endpoints)
4. Returns `{ body, status }` or `null` (if route doesn't match)

### Handler Pattern
```javascript
export default async function handle({ method, path, body, query }, db, user) {
  // Route: POST /stories
  if (path.length === 0 && method === 'POST') {
    // Validate
    if (!user) return { body: { error: 'Unauthorized' }, status: 401 }
    // Business logic
    const story = await createStory(db, user, body)
    // Return
    return { body: { story }, status: 201 }
  }

  // Route: GET /stories/:id
  if (path.length === 1 && method === 'GET') {
    const story = await getStory(db, path[0], user)
    return { body: { story }, status: 200 }
  }

  return null // Not handled
}
```

### Route Resolution Order
The central router (`route.js`) tries handlers in this order:
1. Infrastructure routes (healthz, readyz, cache/stats)
2. Auth routes (/auth/*)
3. Feature routes (alphabetical: activity, admin, analytics, ...)
4. 404 fallback

---

## 5. Service Layer

Services contain reusable business logic extracted from handlers:

| Service | File | Purpose |
|---------|------|---------|
| Feed Ranking | `feed-ranking.js` | Multi-signal scoring algorithm |
| Story Service | `story-service.js` | Privacy, stickers, story rail |
| Scoring Engine | `scoring.js` | Tribe engagement scoring |
| Anti-Abuse | `anti-abuse-service.js` | Rate limiting, fraud detection |
| Cache | `cache.js` | Redis wrapper with fallback |
| Realtime | `realtime.js` | SSE event broadcasting |

---

## 6. Database Layer

### Connection
```javascript
import { MongoClient } from 'mongodb'
const client = new MongoClient(process.env.MONGO_URL)
const db = client.db(process.env.DB_NAME)
```

### Index Strategy
- **Unique indexes**: phone, username, token, refreshToken
- **Compound indexes**: { authorId, createdAt: -1 } for feed queries
- **Text indexes**: users, content_items, pages, tribes for search
- **TTL indexes**: sessions.expiresAt (auto-cleanup)

### Write Patterns
- **Denormalization**: Counters (likeCount, followerCount) stored on documents
- **Atomic updates**: `$inc` for counters, `$set` for state changes
- **Upsert**: Used for saves, reactions (idempotent actions)

---

## 7. Cache Layer

### Architecture
```
┌──────────┐    ┌──────────┐    ┌──────────┐
│  Handler  │───>│  cache   │───>│  Redis   │
│           │    │  .get()  │    │          │
└──────────┘    └──────────┘    └──────────┘
                     │ miss          │ hit
                     ▼               │
                ┌──────────┐        │
                │  MongoDB  │───────┘
                │  query    │  cache.set()
                └──────────┘
```

### Cache Key Naming
```
{namespace}:{identifier}:{params}

Examples:
feed:public:limit=20:cursor=null
story:detail:abc-123
tribe:list:all
search:q=iit:type=users
```

### Fallback Strategy
- Primary: Redis (distributed, persistent)
- Fallback: In-memory Map (single-instance, ephemeral)
- Automatic failover: no manual intervention

---

## 8. Real-Time Layer (SSE)

### Architecture
```
┌──────────┐    ┌──────────┐    ┌──────────┐
│  Client  │◄───│  SSE     │◄───│  Redis   │
│  (App)   │    │  Stream  │    │  Pub/Sub │
└──────────┘    └──────────┘    └──────────┘
                                     ▲
                                     │ publish
                                ┌──────────┐
                                │  Handler  │
                                │  (write)  │
                                └──────────┘
```

### SSE Endpoints
| Endpoint | Events |
|----------|---------|
| `/api/stories/events/stream` | story.viewed, story.reacted, story.replied, story.expired |
| `/api/tribe-contests/live-feed` | entry_submitted, vote_cast, rank_change |
| `/api/tribe-contests/:id/live` | Single contest scoreboard |
| `/api/tribe-contests/seasons/:id/live-standings` | Season standings |

### SSE Protocol
```
GET /api/stories/events/stream?token={accessToken}

Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

event: connected
data: {"userId":"...","connectedAt":"..."}

: heartbeat 2025-01-15T10:30:00.000Z

event: story_event
data: {"type":"story.viewed","storyId":"...","viewerId":"..."}

retry: 3000
```

---

## 9. Media Pipeline

```
┌──────────┐    ┌──────────┐    ┌──────────┐
│  Client  │───>│ API Init │───>│ Supabase │
│  Upload  │    │ Signed   │    │ Storage  │
│          │    │ URL      │    │          │
└──────────┘    └──────────┘    └──────────┘
      │                              │
      │         Direct Upload        │
      └─────────────────────────────>│
                                     │
┌──────────┐    ┌──────────┐        │
│  Client  │───>│ Complete │◄───────┘
│  Confirm │    │ API      │
└──────────┘    └──────────┘
                     │
              ┌──────┴──────┐
              │  If Video:  │
              │  FFmpeg     │
              │  Transcode  │
              │  → HLS      │
              └─────────────┘
```

---

## 10. Authentication Middleware

### Token Validation
```javascript
async function authenticateRequest(req, db) {
  const authHeader = req.headers.get('authorization')
  if (!authHeader?.startsWith('Bearer ')) return null
  
  const token = authHeader.slice(7)
  const session = await db.collection('sessions').findOne({ token })
  
  if (!session) return null
  if (new Date(session.accessTokenExpiresAt) < new Date()) {
    return { error: 'ACCESS_TOKEN_EXPIRED', status: 401 }
  }
  
  const user = await db.collection('users').findOne({ id: session.userId })
  return user
}
```

### User Sanitization
Before returning any user object to client, sensitive fields are stripped:
```javascript
function sanitizeUser(user) {
  const { _id, pinHash, pinSalt, ...safe } = user
  return safe
}
```

---

## 11. Error Handling Architecture

### Standard Error Response
```json
{
  "error": "Human-readable message",
  "code": "MACHINE_CODE"
}
```

### Error Codes by Layer
| Layer | Errors |
|-------|--------|
| Router | 404 NOT_FOUND, 405 METHOD_NOT_ALLOWED |
| Auth | 401 UNAUTHORIZED, ACCESS_TOKEN_EXPIRED, REFRESH_TOKEN_REUSED |
| Validation | 400 VALIDATION_ERROR |
| Business | 403 FORBIDDEN, 409 CONFLICT, 410 EXPIRED, 422 CONTENT_REJECTED |
| Rate Limit | 429 RATE_LIMITED (with Retry-After header) |
| Server | 500 INTERNAL_ERROR |

---

## 12. Scalability Design

### Current Bottlenecks & Solutions
| Bottleneck | Current Solution | Future Path |
|-----------|-----------------|-------------|
| Feed queries | Redis cache (15s TTL) | Read replicas |
| Story rail | In-memory story rail builder | Pre-computed rails |
| Search | MongoDB text indexes | Elasticsearch |
| Transcoding | In-process FFmpeg | Queue + workers |
| SSE connections | Redis Pub/Sub | Dedicated WebSocket service |

### Horizontal Scaling Ready
- Stateless handlers (no in-process state except anti-abuse windows)
- Redis for distributed cache and pub/sub
- MongoDB supports replica sets
- Supabase handles media CDN scaling

---

*Architecture v3.0.0 — 26,000+ lines of backend code*
