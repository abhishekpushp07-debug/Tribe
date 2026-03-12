# 07 — Reels System

## Overview

The Reels system is an **Instagram-grade short-form video backend** powering 39 endpoints across 12 MongoDB collections with 36 indexes. It supports the full lifecycle of short-form video: creation, processing, feeds, social interactions, watch metrics, moderation, creator tools, and remix/series features.

**Source**: `lib/handlers/reels.js` (2,156 lines) + `lib/services/reel-service.js` + `lib/services/reel-processing-worker.js`

---

## Constants & Limits

| Constant | Value | Description |
|----------|-------|-------------|
| `REEL_MAX_DURATION_MS` | 90,000 (90s) | Maximum reel duration |
| `REEL_MAX_CAPTION_LEN` | 2,200 | Characters allowed in caption |
| `REEL_MAX_HASHTAGS` | 30 | Maximum hashtags per reel |
| `REEL_MAX_MENTIONS` | 20 | Maximum @mentions per reel |
| `REEL_CREATE_RATE_LIMIT` | 20/hr | Reels created per hour per user |
| `REEL_COMMENT_RATE_LIMIT` | 60/hr | Comments per hour per user |
| `REEL_REPORT_AUTO_HOLD` | 3 | Reports before auto-hold |
| `REEL_FEED_LIMIT` | 20 | Default items per feed page |
| `REEL_FEED_MAX` | 200 | Max items per request |

---

## State Machines

### Reel Status Lifecycle

```
  DRAFT ──publish──► PUBLISHED ──archive──► ARCHIVED
    │                    │                      │
    │                    │ (moderation)          │ restore
    │                    ▼                      ▼
    │                  HELD                  PUBLISHED
    │                    │
    │                    │ (admin remove)
    │                    ▼
    └──delete──────► REMOVED
```

Allowed statuses: `DRAFT`, `PUBLISHED`, `ARCHIVED`, `REMOVED`, `HELD`

### Media Processing Status

```
UPLOADING → PROCESSING → READY
                       └→ FAILED
```

### Moderation Status

`PENDING` → `APPROVED` | `HELD` | `REMOVED`

---

## Data Model — `reels` Collection

```javascript
{
  id: UUID,
  creatorId: String,           // User who created the reel
  collegeId: String | null,    // Creator's college
  tribeId: String | null,      // Creator's tribe
  caption: String | null,      // Max 2200 chars
  hashtags: [String],          // Lowercase, no # prefix, max 30
  mentions: [String],          // Max 20 user IDs
  audioMeta: {                 // Audio track metadata
    audioId: String,
    title: String,
    artist: String
  } | null,
  durationMs: Number | null,   // 1000 – 90000
  mediaStatus: 'UPLOADING' | 'PROCESSING' | 'READY' | 'FAILED',
  mediaId: String | null,      // References media_assets collection
  playbackUrl: String | null,  // CDN URL or /api/media/:id
  thumbnailUrl: String | null,
  posterFrameUrl: String | null,
  variants: [],                // HLS variants if transcoded
  visibility: 'PUBLIC' | 'FOLLOWERS' | 'PRIVATE',
  moderationStatus: 'PENDING' | 'APPROVED' | 'HELD' | 'REMOVED',
  syntheticDeclaration: Boolean,  // AI-generated content flag
  brandedContent: Boolean,     // Paid partnership flag
  status: 'DRAFT' | 'PUBLISHED' | 'ARCHIVED' | 'REMOVED' | 'HELD',
  remixOf: {                   // If remix/duet/stitch
    reelId: String,
    type: 'REMIX' | 'DUET' | 'STITCH'
  } | null,
  collabCreators: [String],    // Collaborator user IDs
  seriesId: String | null,     // Belongs to a reel series
  seriesOrder: Number | null,
  pinnedToProfile: Boolean,    // Max 3 pinned reels per user
  // Engagement counters (denormalized for performance)
  likeCount: Number,
  commentCount: Number,
  saveCount: Number,
  shareCount: Number,
  viewCount: Number,
  uniqueViewerCount: Number,
  impressionCount: Number,
  completionCount: Number,     // Full watch-throughs
  avgWatchTimeMs: Number,      // Rolling average
  replayCount: Number,
  reportCount: Number,
  score: Number,               // Ranking score for feed
  // Timestamps
  createdAt: Date,
  updatedAt: Date,
  publishedAt: Date | null,
  removedAt: Date | null,
  heldAt: Date | null,
  archivedAt: Date | null
}
```

---

## Ranking Algorithm

Reels are ranked by a composite `score` field:

```javascript
function computeReelScore(reel) {
  const hoursSincePublish = (Date.now() - publishedAt) / 3_600_000
  const freshness = 1 / (1 + hoursSincePublish / 24)
  const views = Math.max(viewCount, 1)
  const engagement = (likes*1 + saves*2 + comments*1.5 + shares*3) / views
  const completionRate = completionCount / views
  const replayRate = replayCount / views
  const quality = completionRate * 0.5 + replayRate * 0.3
  const penalty = reportCount * 0.1
  return freshness*40 + engagement*30 + quality*30 - penalty*10
}
```

**Signal weights**:
- Freshness: 40% (24-hour half-life decay)
- Engagement: 30% (shares weighted 3x, saves 2x, comments 1.5x, likes 1x)
- Quality: 30% (completion + replay rates)
- Penalty: -10 per report

First-page results get additional smart ranking via `rankReels()` from `feed-ranking.js` using user affinity context.

---

## API Endpoints

### Creation & Lifecycle

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/reels` | Required | Create reel (draft or publish) |
| `PATCH` | `/api/reels/:id` | Owner/Admin | Edit metadata |
| `DELETE` | `/api/reels/:id` | Owner/Admin | Soft-delete (REMOVED) |
| `POST` | `/api/reels/:id/publish` | Owner | Publish a draft |
| `POST` | `/api/reels/:id/archive` | Owner | Archive reel |
| `POST` | `/api/reels/:id/restore` | Owner | Restore from archive |
| `POST` | `/api/reels/:id/pin` | Owner | Pin to profile (max 3) |
| `DELETE` | `/api/reels/:id/pin` | Owner | Unpin from profile |

### Feeds

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/reels/feed` | Required | Personalized discovery feed |
| `GET` | `/api/reels/following` | Required | Reels from followed users |
| `GET` | `/api/users/:userId/reels` | Optional | Creator's profile reels |
| `GET` | `/api/reels/:id` | Optional | Reel detail + auto-view tracking |
| `GET` | `/api/reels/audio/:audioId` | Optional | Reels using specific audio |
| `GET` | `/api/reels/:id/remixes` | Optional | Remixes/duets of a reel |

### Social Interactions

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/reels/:id/like` | Required | Like (anti-abuse checked) |
| `DELETE` | `/api/reels/:id/like` | Required | Unlike |
| `POST` | `/api/reels/:id/save` | Required | Save (anti-abuse checked) |
| `DELETE` | `/api/reels/:id/save` | Required | Unsave |
| `POST` | `/api/reels/:id/comment` | Required | Comment (moderated) |
| `GET` | `/api/reels/:id/comments` | Optional | List comments |
| `POST` | `/api/reels/:id/share` | Required | Track share |
| `POST` | `/api/reels/:id/report` | Required | Report reel |
| `POST` | `/api/reels/:id/hide` | Required | Hide from feed |
| `POST` | `/api/reels/:id/not-interested` | Required | Not interested signal |

### Watch Metrics

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/reels/:id/watch` | Required | Track watch duration/completion |
| `POST` | `/api/reels/:id/view` | Required | Track impression (not deduplicated) |

### Creator Tools

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/me/reels/series` | Required | Create reel series |
| `GET` | `/api/users/:userId/reels/series` | Public | Get user's series |
| `GET` | `/api/me/reels/archive` | Required | Creator's archived reels |
| `GET` | `/api/me/reels/analytics` | Required | Creator analytics dashboard |

### Processing

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/reels/:id/processing` | Owner/Admin | Update processing status |
| `GET` | `/api/reels/:id/processing` | Owner/Admin | Get processing job status |

### Admin

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/admin/reels` | Moderator+ | Moderation queue |
| `PATCH` | `/api/admin/reels/:id` | Moderator+ | Admin moderate reel |

---

## Supporting Collections

| Collection | Purpose | Key Indexes |
|------------|---------|-------------|
| `reel_likes` | Like tracking | `{reelId, userId}` unique |
| `reel_saves` | Save tracking | `{reelId, userId}` unique |
| `reel_comments` | Comments/replies | `{reelId, parentId, createdAt}` |
| `reel_views` | Unique view tracking | `{reelId, viewerId}` upsert |
| `reel_watch_events` | Watch duration events | `{reelId, createdAt}` |
| `reel_shares` | Share tracking | `{reelId, userId}` |
| `reel_reports` | Report tracking | `{reelId, reporterId}` unique |
| `reel_hidden` | Hidden from feed | `{reelId, userId}` unique |
| `reel_not_interested` | Not interested signals | `{reelId, userId}` unique |
| `reel_processing_jobs` | Video processing queue | `{reelId}` |
| `reel_series` | Named series for creators | `{creatorId}` |

---

## Feed Cursor Pagination

The reel feed uses a **compound cursor** with score + ID tie-breaker to prevent duplicate/missing items:

```
GET /api/reels/feed?cursor=42.123|abc-uuid&limit=20
```

Cursor format: `{score}|{reelId}`

This ensures deterministic pagination even when multiple reels share the same score.

---

## Anti-Abuse Integration

All social actions (like, save, comment, share) are checked against the anti-abuse service:

```javascript
const abuseCheck = checkEngagementAbuse(userId, ActionType.LIKE, reelId, creatorId)
if (abuseCheck.flagged) await logSuspiciousAction(db, userId, ActionType.LIKE, reelId, abuseCheck)
if (!abuseCheck.allowed) return 429
```

This detects velocity anomalies (rapid-fire engagement) and ring patterns (mutual boosting).

---

## Block Integration

Blocked users are filtered from:
- Feed results (`creatorId: { $nin: blockedIds }`)
- Comment listings
- Audio browse results
- Remix browse results
- Reel detail access (returns 403)

---

## Remix & Duet System

Reels can reference an original via `remixOf`:

```json
{
  "remixOf": {
    "reelId": "original-uuid",
    "type": "REMIX"  // REMIX | DUET | STITCH
  }
}
```

The original reel must be `PUBLISHED`. Reel detail enriches with `remixSource` (original creator + caption).

---

## Content Moderation

Captions are moderated on creation and edit via the `moderateCreateContent` middleware. If escalated:
- `moderationStatus` → `HELD`
- `status` → `HELD`
- Reel becomes invisible in feeds but viewable by creator

Comments follow the same moderation pipeline.

---

## Android Integration Notes

### Create Reel Flow

```kotlin
// 1. Upload video via media pipeline
val mediaInit = api.post("/api/media/upload-init", MediaInitRequest(
    kind = "video", mimeType = "video/mp4", sizeBytes = file.length()
))
// 2. Upload to Supabase signed URL
supabaseUpload(mediaInit.uploadUrl, file)
// 3. Complete upload
api.post("/api/media/upload-complete", CompleteRequest(mediaId = mediaInit.mediaId))
// 4. Create reel
api.post("/api/reels", CreateReelRequest(
    mediaId = mediaInit.mediaId,
    caption = "My reel",
    visibility = "PUBLIC"
))
```

### Watch Tracking

Send watch events when user scrolls away or video loops:

```kotlin
api.post("/api/reels/$reelId/watch", WatchEvent(
    watchTimeMs = 15000,
    completed = true,
    replayed = false
))
```
