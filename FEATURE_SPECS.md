# Tribe — Feature Specifications & Business Logic

> Detailed business rules, state machines, and feature logic for every module.
> Use this to implement correct client-side behavior.

---

## Table of Contents
1. [Authentication & Security](#1-authentication--security)
2. [Onboarding Rules](#2-onboarding-rules)
3. [Content Pipeline](#3-content-pipeline)
4. [Feed Algorithm Deep Dive](#4-feed-algorithm-deep-dive)
5. [Social Graph Rules](#5-social-graph-rules)
6. [Stories Lifecycle](#6-stories-lifecycle)
7. [Reels Pipeline](#7-reels-pipeline)
8. [Pages System](#8-pages-system)
9. [Events System](#9-events-system)
10. [Tribe Engagement System](#10-tribe-engagement-system)
11. [Contest Lifecycle](#11-contest-lifecycle)
12. [Moderation Pipeline](#12-moderation-pipeline)
13. [Content Distribution Stages](#13-content-distribution-stages)
14. [Quality Scoring](#14-quality-scoring)
15. [Anti-Abuse System](#15-anti-abuse-system)
16. [Caching Architecture](#16-caching-architecture)

---

## 1. Authentication & Security

### Token Architecture (Access + Refresh Split)
```
Access Token (at_...)
├── TTL: 15 minutes
├── Used for: Every API call (Authorization header)
├── Storage: In-memory only (never persist)
└── On expiry: Use refresh token to get new pair

Refresh Token (rt_...)
├── TTL: 30 days
├── Used for: POST /auth/refresh only
├── Storage: Encrypted secure storage
├── Rotation: Each use invalidates old token, issues new pair
└── Family tracking: Reuse detection across rotation chain
```

### Refresh Token Rotation
```
Request 1: refreshToken_v0 → gets accessToken_new + refreshToken_v1
Request 2: refreshToken_v1 → gets accessToken_new + refreshToken_v2
Request X: refreshToken_v0 (reused!) → ALL sessions in family REVOKED
```

**Critical**: If `REFRESH_TOKEN_REUSED` is returned, the client MUST:
1. Clear all stored tokens
2. Navigate to login screen immediately
3. Show security alert to user

### Session Management
- Max 10 concurrent sessions per user
- When limit reached, oldest session auto-evicted
- Users can view all sessions: `GET /api/auth/sessions`
- Users can revoke individual sessions (except current)
- PIN change revokes all other sessions

### Brute Force Protection
- Rate limited per IP: 5 failed attempts → 300s cooldown
- Response includes `Retry-After` header
- Exponential backoff on repeated failures

---

## 2. Onboarding Rules

### Flow (4 steps, order enforced)
```
Register → AGE → COLLEGE → PROFILE → DONE
```

### Age Rules
| Birth Year | Age Status | Restrictions |
|-----------|-----------|-------------|
| ≤ current - 18 | ADULT | Full access |
| > current - 18 | CHILD | No content creation, limited social |
| Not set | UNKNOWN | Blocked from content creation |

- Age change from CHILD→ADULT blocked (requires admin review)
- Age change from ADULT→CHILD allowed (honesty-first)

### College Selection
- Search by name, state, or type
- Optional — can skip with `collegeId: null`
- Can change college later via `PATCH /me/college`
- College association affects: college feed, governance eligibility

---

## 3. Content Pipeline

### Content Creation Flow
```
1. Upload media → /api/media/upload-init → Supabase → /api/media/upload-complete
2. Create post → POST /api/content/posts (with mediaIds)
3. Moderation check (automatic)
4. If approved: visibility=PUBLIC, enters feed
5. If flagged: visibility=HELD_FOR_REVIEW
6. If rejected: visibility=REMOVED, notification sent
```

### Post Types & Validation

| Type | Required Fields | Validation |
|------|----------------|------------|
| Standard | caption OR mediaIds | Caption max 2200 chars |
| Poll | caption + poll.options | 2-4 options, expiresIn in hours |
| Thread Head | caption | Creates threadId |
| Thread Part | caption + threadParentId | Must be same author |
| Link | linkUrl | Valid URL |
| Carousel | mediaIds (2+) | Max media limit |
| Draft | any | status=DRAFT |
| Scheduled | publishAt | Max 30 days in future |

### Hashtag Extraction
- Auto-extracted from caption: `#word` → stored in `hashtags[]` array
- Hashtag counter updated on create/delete
- Trending calculated from 7-day usage

### Repost Rules
- Cannot repost a repost (depth=1 only)
- Only one repost per user per content
- Optional quote caption

---

## 4. Feed Algorithm Deep Dive

### Scoring Formula
```
feedScore = recency × (1 + engagement) × affinity × quality × viralityBoost × typeBoost
```

### Signal Calculation

**Recency (exponential decay)**
```
recency = exp(-ln(2) × ageMs / halfLifeMs)
halfLife = 6 hours (posts) | 12 hours (reels)

Age 0h  → 1.000
Age 3h  → 0.707
Age 6h  → 0.500
Age 12h → 0.250
Age 24h → 0.063
Age 48h → 0.004
```

**Engagement Velocity**
```
engagementRaw = (likes × 1) + (comments × 3) + (saves × 5) + (shares × 2)
velocity = engagementRaw / ageHours
engagement = log2(1 + velocity)
```

**Author Affinity (0 to ~2.8)**
```
base = 1.0
+ 0.5 if viewer follows author
+ 0.3 if same tribe
+ 0.0–1.0 based on interaction history (normalized)
```

**Interaction History**
```
Per author, last 30 days:
  likes = count × 1
  comments = count × 3
  saves = count × 5
Normalize to 0.0–1.0 scale
```

**Content Type Affinity**
```
Based on viewer's like history content types:
  typeWeight = 0.8 + (typeCount / totalLikes) × 0.6
  Range: 0.8 (rare type) to 1.4 (preferred type)
Types: text, image, video, carousel, poll, thread, link
```

**Diversity Penalty**
```
Same author 2nd post:  score × 0.70
Same author 3rd+ post: score × 0.40
Same type 3 in a row:  score × 0.85
```

### First Page vs Pagination
- **Page 1** (no cursor): Smart Feed Algorithm applied
- **Page 2+** (with cursor): Chronological order (fallback)

---

## 5. Social Graph Rules

### Follow
- Follow public account → instant
- Follow private account → creates follow_request (PENDING)
- Unfollow → removes from both sides
- Block → removes follow relationship both ways

### Block (Bidirectional)
When user A blocks user B:
- A cannot see B's content, profile, comments
- B cannot see A's content, profile, comments
- Existing follow relationship removed both ways
- B's comments on A's posts: hidden (not deleted)
- Search results: filtered out

### Private Account
When `isPrivate = true`:
- Follow becomes follow request
- Content visible only to approved followers
- Profile info still partially visible (name, avatar, bio)
- Stories: only visible to followers

---

## 6. Stories Lifecycle

### Lifecycle
```
Create → ACTIVE (24h TTL) → EXPIRED → Archive (permanent storage)
                ↓
           REMOVED (moderation) or DELETE (user)
```

### View Tracking
- Deduplicated: same viewer counted once per story
- Tracked separately: viewCount (unique), viewDuration (per session)
- Owner can see full viewer list with timestamps

### Sticker Interactions
| Sticker | User Action | Data Stored |
|---------|------------|-------------|
| Poll | Select option | optionIndex |
| Question | Type answer | text |
| Quiz | Select answer | optionIndex + isCorrect |
| Emoji Slider | Drag slider | value (0.0-1.0) |

### Privacy Cascade
```
Privacy=EVERYONE: visible to all non-blocked users
Privacy=FOLLOWERS: visible to approved followers only
Privacy=CLOSE_FRIENDS: visible to close friends list only
  + hideStoryFrom: additional per-user exclusions
  + story_mutes: viewer-side muting (still follows, hides stories)
```

### Close Friends
- Max 500 users
- Adding is one-way (no notification to the friend)
- Close friends stories show special green ring in UI

### Highlights
- Max 50 highlights per user
- Max 100 stories per highlight
- Stories can exist in multiple highlights
- Highlights survive after story expiration (archive reference)

---

## 7. Reels Pipeline

### Reel Creation Flow
```
1. Upload video → media upload pipeline
2. POST /api/reels → creates reel (DRAFT or PUBLISHED)
3. If video: POST /api/transcode/{mediaId} → HLS transcoding
4. Poll: GET /api/transcode/{jobId}/status until COMPLETED
5. POST /api/reels/{id}/publish (if draft)
```

### Transcoding Pipeline
```
Input: MP4/MOV → FFmpeg → HLS Output
  ├── 360p  (600kbps)
  ├── 480p  (1200kbps)
  ├── 720p  (2500kbps)
  └── 1080p (5000kbps, if source ≥ 1080p)
  + Thumbnails (every 2s)
  + Master playlist (adaptive bitrate)
```

### Watch Event Tracking
- `POST /reels/{id}/view` — on first appear (impression)
- `POST /reels/{id}/watch` — on scroll away (with durationMs, completionRate, isReplay)
- Completion rate affects reel ranking (higher = better)
- Replay flag tracks re-watches

### Reel Feed Ranking (differs from post feed)
- Longer half-life: 12 hours (vs 6 for posts)
- View count has weight (0.1 per view)
- Completion rate boost: 0.8 + (rate × 0.4) → 0.8 to 1.2
- Same diversity penalties as post feed

---

## 8. Pages System

### Role-Based Access Control
| Permission | OWNER | ADMIN | EDITOR | MODERATOR |
|-----------|-------|-------|--------|-----------|
| Edit page identity | Yes | Yes | No | No |
| Publish as page | Yes | Yes | Yes | No |
| Moderate comments | Yes | Yes | No | Yes |
| Manage members | Yes | Yes (lower only) | No | No |
| Change roles | Yes | Yes (lower only) | No | No |
| Archive/restore | Yes | No | No | No |
| Transfer ownership | Yes | No | No | No |

### Page-Authored Content
- Posts created via `POST /pages/{id}/posts`
- Shows `authorType: "PAGE"` and `pageId` in feed
- Page avatar shown instead of user avatar
- Credits the user who published in page analytics

### Verification Flow
```
Page owner → POST /pages/{id}/request-verification → PENDING
Admin → POST /admin/pages/verification-decide → VERIFIED or REJECTED
If VERIFIED: blue checkmark badge on page
```

---

## 9. Events System

### Event Status Flow
```
DRAFT → PUBLISHED → [active period] → ARCHIVED
                  ↘ CANCELLED
Moderation: → HELD → REMOVED
```

### RSVP Rules
- Two statuses: GOING, INTERESTED
- Capacity enforcement: if event has capacity, GOING capped at max
- Can change RSVP status (GOING ↔ INTERESTED)
- Can cancel RSVP (DELETE)
- Organizer sees full attendee list

### Reminder System
- Users can set reminders on events
- One reminder per user per event
- Removed on event cancellation

---

## 10. Tribe Engagement System

### Tribe Assignment
```
tribeIndex = parseInt(SHA256(userId).slice(0, 8), 16) % 21
```
- Deterministic: same userId always → same tribe
- Permanent: cannot be changed by user (admin can reassign)
- Even distribution: modulo 21

### Scoring Formula (v3)
```
engagementScore = 
  (uploads × 100) + 
  (likesReceived × 10) + 
  (commentsReceived × 20) + 
  (sharesReceived × 50) + 
  (storyReactions × 15) + 
  (storyReplies × 25) + 
  viralBonus
```

### Anti-Cheat
- Per-user upload caps per period (350/week, 1500/month)
- Total tribe uploads capped at members × perUserCap
- Scores cached for 10 minutes to prevent manipulation

### Salute System
- Points earned through contests, content, admin awards
- Immutable ledger (never edited, only new entries)
- Reasons: CONTEST_WIN, CONTENT_BONUS, ADMIN_AWARD, ADMIN_DEDUCT, REVERSAL

---

## 11. Contest Lifecycle

### State Machine
```
DRAFT ──publish──> PUBLISHED ──open──> ENTRY_OPEN ──close──> ENTRY_CLOSED
                       │                   │                      │
                       └── cancel ─────────┘── cancel ────────────┘
                                                                   │
                    CANCELLED <── cancel ── EVALUATING <──judge──┘
                       ▲                      │
                       └── cancel ── LOCKED <─┘
                                      │
                                   resolve
                                      │
                                   RESOLVED
```

### Entry Rules
- Must have tribe membership
- One entry per user per contest (configurable)
- Per-tribe entry caps
- Content duplication check (same mediaId blocked)
- Can withdraw own entry before ENTRY_CLOSED

### Scoring
```
finalScore = (judgeScore × judgeWeight) + (publicVoteScore × voteWeight)
```
- Judge score: 0-100, multiple judges averaged
- Public vote score: normalized 0-100 based on vote count
- Default weights: judge 0.7, public 0.3

### Live Feed (SSE)
- Real-time vote counts and rank changes broadcast via SSE
- Clients subscribe to specific contest or global feed
- Events: entry_submitted, vote_cast, score_update, rank_change

---

## 12. Moderation Pipeline

### Auto-Moderation
```
Content Created → Moderation Check:
  1. Text check (profanity, hate speech, spam)
  2. Image check (nudity, violence)
  3. Composite score: 0.0 to 1.0
  
  Score > 0.85 → AUTO-REJECT (CONTENT_REJECTED, 422)
  Score > 0.50 → HELD_FOR_REVIEW (manual queue)
  Score < 0.50 → APPROVED (PUBLIC)
```

### Report-Based Auto-Hold
- 3+ reports on same content → auto-hold for review
- 3+ reports on same event → auto-hold
- 3+ reports on same resource → auto-hold

### Strike System
```
Strike 1: Warning + 24h content creation cooldown
Strike 2: Warning + 72h content creation cooldown
Strike 3: 7-day suspension
Strike 4: 30-day suspension
Strike 5: Permanent ban
```

### Appeal Flow
```
Content removed → User submits appeal → PENDING
Moderator reviews → APPROVED (content restored) or DENIED
```

---

## 13. Content Distribution Stages

### Three-Stage Pipeline
```
Stage 0: Shadow (new/unverified content)
  - Visible in author's profile
  - Not in public feeds
  - Minimum engagement threshold to advance

Stage 1: Limited (emerging content)
  - Visible in college/tribe feeds
  - Not in global public feed
  - Must pass quality + engagement thresholds

Stage 2: Full Distribution
  - Visible in all feeds (public, explore, trending)
  - Eligible for recommendations
  - Can be featured
```

### Promotion Criteria
```
Stage 0 → 1:
  - At least 5 likes OR 2 comments
  - Author account age > 24 hours
  - No active reports

Stage 1 → 2:
  - At least 20 likes OR 10 comments
  - Quality score > 40
  - No active moderation holds
```

### Kill Switch
- Admin can disable auto-evaluation globally
- Manual overrides survive auto-evaluation
- Override reasons logged in audit trail

---

## 14. Quality Scoring

### Score Breakdown (0-100)
```
captionQuality (0-25):
  - Length: 50-500 chars optimal
  - Sentence structure
  - No excessive caps/special chars

mediaRichness (0-25):
  - Has media: +15
  - Multiple media (carousel): +5
  - Video content: +5

hashtagRelevance (0-20):
  - 1-5 hashtags: optimal
  - Matching trending topics: +bonus
  - Too many (>15): penalty

engagementSignals (0-20):
  - Early engagement velocity
  - Save-to-like ratio (saves indicate quality)
  - Comment-to-like ratio

authorReputation (0-10):
  - Account age
  - Follower count
  - Historical content quality average
  - Strike-free record
```

### Quality Tiers
| Score Range | Tier | Effect |
|-------------|------|--------|
| 0-25 | LOW | Stage 0 only |
| 26-50 | MEDIUM | Eligible for Stage 1 |
| 51-75 | HIGH | Fast-tracked to Stage 2 |
| 76-100 | EXCEPTIONAL | Featured candidate |

---

## 15. Anti-Abuse System

### Detection Layers
```
Layer 1: Rate Limiting (per IP + per user)
  - Auth: 5 failed logins → 300s cooldown
  - Content: 30 likes/min, 200 likes/hour
  - Stories: 30 creates/hour
  
Layer 2: Velocity Detection
  - 3+ actions/second sustained for 10s → flagged
  
Layer 3: Pattern Detection
  - Same-target burst (5 likes on same post in 5s)
  - Same-author rapid likes (multiple posts from one author in 60s)
  
Layer 4: Audit Logging
  - All suspicious actions logged with userId, action, velocity, window
  - Admin dashboard: GET /admin/abuse-dashboard
  - Detailed log: GET /admin/abuse-log
```

### Rate Limit Response
```json
HTTP 429
{
  "error": "Rate limit exceeded. Try again in 30 seconds",
  "code": "RATE_LIMITED",
  "retryAfter": 30
}
Header: Retry-After: 30
```

---

## 16. Caching Architecture

### Redis Cache Layer
```
┌─────────┐    ┌─────────┐    ┌──────────┐
│  Client  │───>│  API    │───>│  Redis   │
│ (App)    │    │ Handler  │    │  Cache   │
└─────────┘    └─────────┘    └──────────┘
                    │               │
                    │ (cache miss)  │
                    ▼               │
               ┌──────────┐        │
               │  MongoDB  │───────┘
               │ (source)  │  (populate cache)
               └──────────┘
```

### Cache Strategy
- **Read path**: Check Redis → if miss, query MongoDB, populate cache
- **Write path**: Write MongoDB → invalidate relevant cache keys
- **Stampede protection**: SETNX lock prevents multiple instances computing same key
- **TTL jitter**: ±20% to prevent thundering herd

### Event-Driven Invalidation
| Event | Invalidated Caches |
|-------|-------------------|
| `POST_CREATED` | public_feed, admin_stats, college_feed, tribe_feed |
| `POST_DELETED` | same as created |
| `FOLLOW_CHANGED` | user_profile (both users) |
| `REPORT_CREATED` | public_feed, admin_stats |
| `STORY_CHANGED` | story_feed, story_detail |
| `RESOURCE_CHANGED` | resource_search, resource_detail |
| `LEADERBOARD_CHANGED` | tribe_leaderboard, tribe_list |

### Fallback Strategy
```
Redis available → Use Redis (distributed, survives restarts)
Redis down → In-memory Map (single-instance, ephemeral)
  ↑ Automatic failover, no manual intervention
```

---

*Tribe Feature Specifications v3.0.0 — Complete business logic reference*
