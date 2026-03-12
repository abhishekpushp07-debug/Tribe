# Tribe API — Complete Reference Documentation

> **Version**: 3.0.0 | **Base URL**: `/api` | **Content-Type**: `application/json`
> **Authentication**: Bearer token in `Authorization: Bearer <accessToken>` header
> **Rate Limiting**: Tiered per-IP and per-user. `429` responses include `Retry-After` header.

---

## Table of Contents

1. [Global Conventions](#1-global-conventions)
2. [Authentication & Sessions](#2-authentication--sessions)
3. [Onboarding & Profile Setup](#3-onboarding--profile-setup)
4. [User Profiles & Settings](#4-user-profiles--settings)
5. [Content (Posts, Polls, Threads, Carousels)](#5-content-posts-polls-threads-carousels)
6. [Feeds & Explore](#6-feeds--explore)
7. [Social Interactions](#7-social-interactions)
8. [Comments System](#8-comments-system)
9. [Stories](#9-stories)
10. [Story Stickers & Interactions](#10-story-stickers--interactions)
11. [Story Settings & Close Friends](#11-story-settings--close-friends)
12. [Story Highlights](#12-story-highlights)
13. [Reels](#13-reels)
14. [Reel Interactions & Metrics](#14-reel-interactions--metrics)
15. [Reel Creator Tools](#15-reel-creator-tools)
16. [Pages](#16-pages)
17. [Page Content & Analytics](#17-page-content--analytics)
18. [Events](#18-events)
19. [Tribes](#19-tribes)
20. [Tribe Contests](#20-tribe-contests)
21. [Search & Discovery](#21-search--discovery)
22. [Hashtags](#22-hashtags)
23. [Notifications](#23-notifications)
24. [Follow Requests (Private Accounts)](#24-follow-requests-private-accounts)
25. [Analytics](#25-analytics)
26. [Media Upload & Management](#26-media-upload--management)
27. [Video Transcoding](#27-video-transcoding)
28. [Board Notices](#28-board-notices)
29. [Authenticity Tags](#29-authenticity-tags)
30. [College Claims & Discovery](#30-college-claims--discovery)
31. [Governance](#31-governance)
32. [Resources](#32-resources)
33. [Content Distribution (Admin)](#33-content-distribution-admin)
34. [Reports, Moderation & Appeals](#34-reports-moderation--appeals)
35. [Content Quality Scoring](#35-content-quality-scoring)
36. [Content Recommendations](#36-content-recommendations)
37. [User Activity Status](#37-user-activity-status)
38. [Smart Suggestions](#38-smart-suggestions)
39. [Blocks & Mutes](#39-blocks--mutes)
40. [Admin & Ops](#40-admin--ops)
41. [Frontend Integration Notes](#41-frontend-integration-notes)

---

## 1. Global Conventions

### Authentication
Most endpoints require a Bearer token obtained from `/api/auth/login` or `/api/auth/register`.
```
Authorization: Bearer eyJhbGci...
```
- **Public** = No token needed
- **Auth** = Valid token required
- **Admin** = Token + role `ADMIN` or `SUPER_ADMIN`
- **Mod** = Token + role `MODERATOR`, `ADMIN`, or `SUPER_ADMIN`

### Pagination
All list endpoints accept:
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `limit` | int | 20 | Items per page (max 50) |
| `offset` | int | 0 | Skip N items (offset-based) |
| `cursor` | string | null | ISO date cursor (cursor-based) |

**Response pattern:**
```json
{
  "items": [...],
  "pagination": {
    "nextCursor": "2025-01-15T10:30:00.000Z",
    "hasMore": true
  }
}
```

### Error Format
```json
{
  "error": "Human-readable message",
  "code": "MACHINE_CODE"
}
```
Common codes: `VALIDATION`, `UNAUTHORIZED`, `FORBIDDEN`, `NOT_FOUND`, `CONFLICT`, `RATE_LIMITED`, `CONTENT_REJECTED`, `EXPIRED`, `INTERNAL_ERROR`

### Response Headers
Every response includes:
- `x-contract-version: v2`
- `x-request-id: <uuid>` (for debugging/support)

---

## 2. Authentication & Sessions

### `POST /api/auth/register`
Create a new account.

**Auth**: Public

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `phone` | string | Yes | Exactly 10 digits |
| `pin` | string | Yes | Exactly 4 digits |
| `displayName` | string | Yes | 2-50 characters |

```json
// Request
{ "phone": "7777099001", "pin": "1234", "displayName": "Aarav" }

// Response 201
{
  "accessToken": "eyJhbGci...",
  "refreshToken": "rt_abc123...",
  "expiresIn": 900,
  "token": "eyJhbGci...",
  "user": {
    "id": "uuid-1234",
    "phone": "7777099001",
    "displayName": "Aarav",
    "username": null,
    "bio": "",
    "avatarMediaId": null,
    "ageStatus": "UNKNOWN",
    "role": "USER",
    "collegeId": null,
    "tribeId": "tribe-uuid",
    "tribeCode": "SHIVAJI",
    "tribeName": "Shivaji",
    "followersCount": 0,
    "followingCount": 0,
    "postsCount": 0,
    "onboardingComplete": false,
    "onboardingStep": "AGE",
    "createdAt": "2025-01-15T10:00:00.000Z"
  }
}

// Error 409
{ "error": "Phone number already registered", "code": "CONFLICT" }
```

---

### `POST /api/auth/login`
Authenticate with phone + PIN.

**Auth**: Public

| Field | Type | Required |
|-------|------|----------|
| `phone` | string | Yes |
| `pin` | string | Yes |

```json
// Request
{ "phone": "7777099001", "pin": "1234" }

// Response 200
{
  "accessToken": "eyJhbGci...",
  "refreshToken": "rt_abc123...",
  "expiresIn": 900,
  "token": "eyJhbGci...",
  "user": { /* same as register */ }
}

// Error 401
{ "error": "Invalid phone or PIN", "code": "UNAUTHORIZED" }

// Error 429 (brute force protection)
{ "error": "Too many failed attempts. Try again in 300 seconds", "code": "RATE_LIMITED" }
```

---

### `POST /api/auth/refresh`
Rotate refresh token to get new access + refresh tokens.

**Auth**: Public (uses refresh token in body)

```json
// Request
{ "refreshToken": "rt_abc123..." }

// Response 200
{
  "accessToken": "new_access_token",
  "refreshToken": "new_refresh_token",
  "expiresIn": 900,
  "token": "new_access_token",
  "user": { /* sanitized user */ }
}

// Error 401 (reuse detected — all family sessions revoked)
{ "error": "Refresh token has been reused. All sessions in this family have been revoked for security.", "code": "REFRESH_TOKEN_REUSED" }
```

---

### `POST /api/auth/logout`
Invalidate current session.

**Auth**: Auth

```json
// Response 200
{ "message": "Logged out" }
```

---

### `GET /api/auth/me`
Get current authenticated user profile.

**Auth**: Auth

```json
// Response 200
{ "user": { /* sanitized user object */ } }
```

---

### `GET /api/auth/sessions`
List all active sessions for current user.

**Auth**: Auth

```json
// Response 200
{
  "sessions": [
    {
      "id": "session-uuid",
      "deviceInfo": "Mozilla/5.0...",
      "ipAddress": "192.168.1.1",
      "lastAccessedAt": "2025-01-15T10:00:00.000Z",
      "createdAt": "2025-01-14T09:00:00.000Z",
      "expiresAt": "2025-01-22T09:00:00.000Z",
      "isCurrent": true
    }
  ],
  "count": 1,
  "maxSessions": 5
}
```

---

### `DELETE /api/auth/sessions`
Revoke ALL sessions (force logout everywhere).

**Auth**: Auth

```json
// Response 200
{ "message": "All sessions revoked", "revokedCount": 3 }
```

---

### `DELETE /api/auth/sessions/:sessionId`
Revoke a single session by ID (cannot revoke current session).

**Auth**: Auth

```json
// Response 200
{ "message": "Session revoked", "sessionId": "session-uuid" }

// Error 400
{ "error": "Cannot revoke current session via this endpoint. Use POST /auth/logout instead.", "code": "VALIDATION" }
```

---

### `PATCH /api/auth/pin`
Change PIN. Re-authenticates with current PIN, revokes all other sessions, issues new tokens.

**Auth**: Auth

```json
// Request
{ "currentPin": "1234", "newPin": "5678" }

// Response 200
{
  "message": "PIN changed. All other sessions revoked. New tokens issued.",
  "accessToken": "new_access_token",
  "refreshToken": "new_refresh_token",
  "expiresIn": 900,
  "token": "new_access_token",
  "revokedSessionCount": 2
}
```

---

## 3. Onboarding & Profile Setup

### `PATCH /api/me/profile`
Update display name, username, bio, or avatar.

**Auth**: Auth

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `displayName` | string | No | 2-50 chars |
| `username` | string | No | 3-30 chars, `[a-z0-9._]`, unique |
| `bio` | string | No | Max 500 chars |
| `avatarMediaId` | string | No | Valid media ID |

```json
// Request
{ "username": "aarav.21", "bio": "IIT Delhi '25" }

// Response 200
{ "user": { /* updated sanitized user */ } }

// Error 409
{ "error": "Username already taken", "code": "CONFLICT" }
```

---

### `PATCH /api/me/age`
Set birth year (required during onboarding).

**Auth**: Auth

```json
// Request
{ "birthYear": 2003 }

// Response 200
{ "user": { "ageStatus": "ADULT", "onboardingStep": "COLLEGE", /* ... */ } }

// Error 403 (child→adult change blocked)
{ "error": "Age change from child to adult requires admin review", "code": "FORBIDDEN" }
```

---

### `PATCH /api/me/college`
Link or unlink a college.

**Auth**: Auth

```json
// Request — Link
{ "collegeId": "college-uuid" }

// Request — Unlink
{ "collegeId": null }

// Response 200
{ "user": { "collegeId": "college-uuid", "collegeName": "IIT Delhi", /* ... */ } }
```

---

### `PATCH /api/me/onboarding`
Mark onboarding as complete.

**Auth**: Auth

```json
// Response 200
{ "user": { "onboardingComplete": true, "onboardingStep": "DONE", /* ... */ } }
```

---

## 4. User Profiles & Settings

### `GET /api/me`
Get own profile with live stats (post/follower/following/reel/story counts).

**Auth**: Auth

```json
// Response 200
{
  "user": { /* sanitized user */ },
  "stats": {
    "postCount": 42,
    "followerCount": 1500,
    "followingCount": 300,
    "reelCount": 15,
    "storyCount": 8
  }
}
```

---

### `GET /api/users/:userId`
Get another user's public profile.

**Auth**: Optional (shows `isFollowing` if authenticated)

```json
// Response 200
{
  "user": { /* sanitized user */ },
  "isFollowing": true,
  "viewerIsFollowing": true
}

// Error 404 (user not found or blocked)
{ "error": "User not found", "code": "NOT_FOUND" }
```

---

### `GET /api/users/:userId/posts`
Get a user's posts.

**Auth**: Optional | **Params**: `limit`, `cursor`, `kind` (POST|STORY|REEL)

```json
// Response 200
{
  "items": [ /* enriched posts with author, viewerHasLiked, etc. */ ],
  "pagination": { "nextCursor": "2025-01-14T...", "hasMore": true }
}
```

---

### `GET /api/users/:userId/followers`
**Auth**: Optional | **Params**: `limit`, `offset`

```json
// Response 200
{
  "items": [ { "id": "...", "displayName": "...", /* sanitized user */ } ],
  "users": [ /* same as items (backward compat) */ ],
  "pagination": { "total": 1500, "limit": 20, "offset": 0, "hasMore": true },
  "total": 1500
}
```

---

### `GET /api/users/:userId/following`
**Auth**: Optional | **Params**: `limit`, `offset`

Same response shape as followers.

---

### `GET /api/users/:userId/saved`
Get saved items. Only viewable by the owner.

**Auth**: Auth (own ID only)

```json
// Response 200
{
  "items": [ /* enriched posts */ ],
  "pagination": { "nextCursor": "...", "hasMore": false }
}

// Error 403
{ "error": "Can only view your own saved items", "code": "FORBIDDEN" }
```

---

### `GET /api/users/:userId/mutual-followers`
Get mutual followers between you and another user.

**Auth**: Auth | **Params**: `limit` (max 50)

```json
// Response 200
{ "items": [ /* sanitized users */ ], "total": 12 }
```

---

### `GET /api/me/activity`
Activity summary for a time period.

**Auth**: Auth | **Params**: `period` (`24h`, `7d`, `30d`, `90d`)

```json
// Response 200
{
  "period": "7d",
  "periodDays": 7,
  "since": "2025-01-08T...",
  "content": { "postsCreated": 5, "storiesCreated": 12, "reelsCreated": 2 },
  "engagement": {
    "likesGiven": 45, "likesReceived": 320,
    "commentsGiven": 12, "commentsReceived": 88,
    "savesReceived": 15, "totalEngagement": 423
  },
  "avgEngagementPerDay": 60.4
}
```

---

### `GET /api/me/stats`
Dashboard-level statistics.

**Auth**: Auth

```json
// Response 200
{
  "posts": 42, "reels": 15, "stories": 8,
  "followers": 1500, "following": 300,
  "totalLikesReceived": 5400, "totalSavesReceived": 230,
  "pagesJoined": 3, "memberSince": "2024-06-01T..."
}
```

---

### `GET /api/me/bookmarks`
All saved content (posts + reels combined).

**Auth**: Auth | **Params**: `limit`, `cursor`, `type` (`post` or `reel`)

```json
// Response 200
{
  "items": [
    { "id": "...", "type": "POST", "caption": "...", "savedAt": "..." },
    { "id": "...", "type": "REEL", "creator": { /* ... */ }, "savedAt": "..." }
  ],
  "total": 2,
  "pagination": { "nextCursor": null, "hasMore": false }
}
```

---

### `GET /api/me/login-activity`
Recent login sessions.

**Auth**: Auth

```json
// Response 200
{
  "sessions": [
    { "id": "...", "createdAt": "...", "ipAddress": "...", "deviceInfo": "...", "isExpired": false }
  ],
  "totalActive": 2
}
```

---

### `GET /api/me/settings`
All user settings (privacy + notifications + profile + interests).

**Auth**: Auth

```json
// Response 200
{
  "privacy": {
    "isPrivate": false,
    "showActivityStatus": true,
    "allowTagging": "EVERYONE",
    "allowMentions": "EVERYONE",
    "hideOnlineStatus": false
  },
  "notifications": { /* notification preference object */ },
  "profile": { "displayName": "...", "username": "...", "bio": "...", "avatarMediaId": null },
  "interests": ["technology", "cricket"]
}
```

---

### `PATCH /api/me/settings`
Bulk update settings.

**Auth**: Auth

```json
// Request
{
  "privacy": { "isPrivate": true, "allowTagging": "FOLLOWERS" },
  "notifications": { "likes": true, "comments": true, "follows": false }
}

// Response 200
{ "message": "Settings updated" }
```

---

### `GET /api/me/privacy`
Get privacy settings.

**Auth**: Auth

```json
// Response 200
{
  "isPrivate": false,
  "showActivityStatus": true,
  "allowTagging": "EVERYONE",
  "allowMentions": "EVERYONE",
  "hideOnlineStatus": false
}
```

---

### `PATCH /api/me/privacy`
Update privacy settings.

**Auth**: Auth

| Field | Type | Values |
|-------|------|--------|
| `isPrivate` | bool | true/false |
| `showActivityStatus` | bool | true/false |
| `allowTagging` | string | `EVERYONE`, `FOLLOWERS`, `NONE` |
| `allowMentions` | string | `EVERYONE`, `FOLLOWERS`, `NONE` |
| `hideOnlineStatus` | bool | true/false |

---

### `POST /api/me/interests`
Set user interests (max 20).

**Auth**: Auth

```json
// Request
{ "interests": ["technology", "cricket", "photography"] }

// Response 200
{ "interests": ["technology", "cricket", "photography"] }
```

---

### `GET /api/me/interests`
**Auth**: Auth

```json
// Response 200
{ "interests": ["technology", "cricket"] }
```

---

### `POST /api/me/deactivate`
Deactivate account and revoke all sessions.

**Auth**: Auth

```json
// Response 200
{ "message": "Account deactivated. You can reactivate by logging in again." }
```

---

## 5. Content (Posts, Polls, Threads, Carousels)

### `POST /api/content/posts`
Create a post, poll, thread part, carousel, or scheduled post.

**Auth**: Auth (age verification required)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `caption` | string | Conditional | Required if no mediaIds |
| `mediaIds` | string[] | Conditional | Required for reels/stories |
| `kind` | string | No | `POST` (default), `REEL`, `STORY` |
| `syntheticDeclaration` | bool | No | AI-generated content flag |
| `poll` | object | No | Poll data (see below) |
| `linkUrl` | string | No | URL for link preview |
| `threadParentId` | string | No | ID of parent thread post |
| `carousel` | object | No | Carousel metadata |
| `status` | string | No | `DRAFT` to save as draft |
| `publishAt` | ISO string | No | Future date to schedule (max 30 days) |

**Poll object:**
```json
{
  "options": ["Option A", "Option B", "Option C"],
  "expiresIn": 24,
  "allowMultipleVotes": false
}
```

**Carousel object:**
```json
{ "order": [0, 1, 2], "coverIndex": 0, "aspectRatio": "MIXED" }
```

```json
// Request — Standard post
{ "caption": "Hello world! #firstpost", "mediaIds": ["media-uuid-1"] }

// Request — Poll
{
  "caption": "What's your favorite language?",
  "poll": { "options": ["JavaScript", "Python", "Rust"], "expiresIn": 48 }
}

// Request — Thread part
{ "caption": "Part 2 of my thread...", "threadParentId": "post-uuid-1" }

// Request — Scheduled post
{ "caption": "Coming tomorrow!", "publishAt": "2025-01-16T10:00:00.000Z" }

// Response 201
{
  "post": {
    "id": "content-uuid",
    "kind": "POST",
    "authorId": "user-uuid",
    "caption": "Hello world! #firstpost",
    "hashtags": ["firstpost"],
    "media": [{ "id": "...", "url": "/api/media/...", "type": "IMAGE" }],
    "visibility": "PUBLIC",
    "likeCount": 0,
    "commentCount": 0,
    "saveCount": 0,
    "shareCount": 0,
    "viewCount": 0,
    "postSubType": "STANDARD",
    "poll": null,
    "thread": null,
    "carousel": null,
    "isDraft": false,
    "createdAt": "2025-01-15T..."
  }
}

// Error 422 (moderation rejected)
{ "error": "Content rejected by moderation", "code": "CONTENT_REJECTED" }
```

---

### `GET /api/content/:contentId`
Get a single content item.

**Auth**: Optional (tracks view)

```json
// Response 200
{
  "post": {
    "id": "...",
    "kind": "POST",
    "caption": "...",
    "author": { /* sanitized user */ },
    "viewerHasLiked": false,
    "viewerHasDisliked": false,
    "viewerHasSaved": false,
    /* ... full enriched post */
  }
}
```

---

### `PATCH /api/content/:contentId`
Edit post caption (author or moderator).

**Auth**: Auth

```json
// Request
{ "caption": "Updated caption #edited" }

// Response 200
{ "post": { /* updated enriched post */ } }
```

---

### `DELETE /api/content/:contentId`
Soft-delete content (sets visibility to REMOVED).

**Auth**: Auth (author or moderator)

```json
// Response 200
{ "message": "Content removed" }
```

---

### `GET /api/content/drafts`
List user's draft posts.

**Auth**: Auth | **Params**: `limit`, `offset`

```json
// Response 200
{ "items": [ /* enriched drafts */ ], "drafts": [ /* same */ ], "pagination": { "total": 3 }, "total": 3 }
```

---

### `GET /api/content/scheduled`
List user's scheduled posts (future publish date).

**Auth**: Auth | **Params**: `limit`, `offset`

```json
// Response 200
{ "items": [ /* enriched scheduled posts */ ], "scheduled": [ /* same */ ], "pagination": { "total": 1 }, "total": 1 }
```

---

### `POST /api/content/:contentId/publish`
Publish a draft or scheduled post immediately.

**Auth**: Auth (author only)

```json
// Response 200
{ "post": { /* published enriched post */ }, "message": "Post published" }
```

---

### `PATCH /api/content/:contentId/schedule`
Update or remove schedule for a draft post.

**Auth**: Auth (author only)

```json
// Request — Update schedule
{ "publishAt": "2025-01-20T10:00:00.000Z" }

// Request — Remove schedule
{ "publishAt": null }

// Response 200
{ "message": "Schedule updated", "contentId": "..." }
```

---

### `POST /api/content/:contentId/vote`
Vote on a poll post.

**Auth**: Auth

```json
// Request
{ "optionId": "opt_1" }

// Response 200
{
  "voted": "opt_1",
  "poll": {
    "options": [
      { "id": "opt_0", "text": "JavaScript", "voteCount": 15 },
      { "id": "opt_1", "text": "Python", "voteCount": 23 },
      { "id": "opt_2", "text": "Rust", "voteCount": 8 }
    ],
    "totalVotes": 46,
    "expiresAt": "2025-01-17T..."
  }
}

// Error 410
{ "error": "Poll has expired", "code": "POLL_EXPIRED" }
```

---

### `GET /api/content/:contentId/poll-results`
Get poll results with viewer's vote.

**Auth**: Optional

```json
// Response 200
{
  "poll": {
    "options": [ /* { id, text, voteCount } */ ],
    "totalVotes": 46,
    "expiresAt": "...",
    "expired": false,
    "allowMultipleVotes": false
  },
  "viewerVote": "opt_1"
}
```

---

### `GET /api/content/:contentId/thread`
Get all parts of a thread.

**Auth**: Optional

```json
// Response 200
{
  "thread": [ /* array of enriched posts ordered by partIndex */ ],
  "isThread": true,
  "partCount": 5,
  "threadId": "thread-head-uuid"
}
```

---

## 6. Feeds & Explore

### `GET /api/feed`
Home feed (alias for public feed, with Smart Feed ranking for authenticated users).

**Auth**: Optional | **Params**: `limit`, `cursor`

```json
// Response 200
{
  "items": [ /* enriched posts */ ],
  "pagination": { "nextCursor": "2025-01-14T...", "hasMore": true },
  "nextCursor": "2025-01-14T...",
  "feedType": "home"
}
```

---

### `GET /api/feed/public`
All public posts. First page ranked by Smart Feed Algorithm; paginated pages are chronological.

**Auth**: Optional | **Params**: `limit`, `cursor`

```json
// Response 200
{
  "items": [ /* enriched posts */ ],
  "pagination": { "nextCursor": "...", "hasMore": true },
  "feedType": "public",
  "distributionFilter": "STAGE_2_ONLY",
  "rankingAlgorithm": "engagement_weighted_v1"
}
```

---

### `GET /api/feed/following`
Posts from users and pages you follow (+ your own posts).

**Auth**: Auth | **Params**: `limit`, `cursor`

```json
// Response 200
{
  "items": [ /* enriched posts */ ],
  "pagination": { "nextCursor": "...", "hasMore": true },
  "feedType": "following",
  "rankingAlgorithm": "engagement_weighted_v1"
}
```

---

### `GET /api/feed/college/:collegeId`
Posts from a specific college.

**Auth**: Optional | **Params**: `limit`, `cursor`

---

### `GET /api/feed/tribe/:tribeId`
Posts from a specific tribe (also supports legacy `/feed/house/:houseId`).

**Auth**: Optional | **Params**: `limit`, `cursor`

---

### `GET /api/feed/stories`
Story rail grouped by author (own stories first, then by recency).

**Auth**: Auth

```json
// Response 200
{
  "storyRail": [
    {
      "author": { "id": "...", "displayName": "..." },
      "stories": [
        { "id": "story-1", "mediaUrl": "...", "type": "IMAGE", "expiresAt": "...", "createdAt": "..." }
      ],
      "latestAt": "2025-01-15T..."
    }
  ]
}
```

---

### `GET /api/feed/reels`
Discovery reel feed (published, public, media-ready).

**Auth**: Optional | **Params**: `limit`, `cursor`

```json
// Response 200
{
  "items": [
    {
      "id": "reel-uuid", "caption": "...", "mediaUrl": "...",
      "likeCount": 500, "commentCount": 23, "viewCount": 12000,
      "creator": { "id": "...", "displayName": "..." }
    }
  ],
  "pagination": { "nextCursor": "...", "hasMore": true },
  "feedType": "reels"
}
```

---

### `GET /api/feed/mixed`
Mixed feed (posts + reels interleaved, every 4th item is a reel).

**Auth**: Optional | **Params**: `limit`

```json
// Response 200
{
  "items": [
    { "type": "POST", /* enriched post */ },
    { "type": "POST", /* enriched post */ },
    { "type": "POST", /* enriched post */ },
    { "type": "REEL", "creator": { /* ... */ }, /* reel data */ }
  ],
  "feedType": "mixed"
}
```

---

### `GET /api/feed/personalized`
ML-like personalized feed scoring (relationship + interests + engagement + recency + diversity).

**Auth**: Auth | **Params**: `limit`, `cursor`

```json
// Response 200
{
  "items": [ /* enriched posts */ ],
  "pagination": { "nextCursor": "...", "hasMore": true },
  "feedType": "personalized",
  "scoringFactors": ["relationship", "interests", "engagement_quality", "recency_decay", "content_diversity"]
}
```

---

### `GET /api/feed/debug`
Debug the Smart Feed ranking algorithm (shows scoring breakdown per post).

**Auth**: Auth | **Params**: `limit` (max 20)

```json
// Response 200
{
  "algorithm": "smart_feed_v2",
  "signals": ["recency_decay", "engagement_velocity", "author_affinity", "content_type_affinity", "quality_signals", "virality_detection", "diversity_penalty", "negative_signals", "unseen_boost"],
  "weights": { "like": 1, "comment": 3, "save": 5, "share": 2 },
  "halfLife": "6 hours",
  "context": {
    "viewerId": "...", "viewerTribeId": "...", "followingCount": 300, "trackedAuthors": 50
  },
  "posts": [
    {
      "postId": "...", "totalScore": 87.5,
      "breakdown": { "recency": 35.2, "engagement": 22.1, "affinity": 15.0, "quality": 10.0, "virality": 5.2 }
    }
  ]
}
```

---

### `GET /api/explore`
Explore page with trending posts, reels, and hashtags.

**Auth**: Optional | **Params**: `limit`

```json
// Response 200
{
  "posts": [ /* enriched trending posts */ ],
  "reels": [ { "type": "REEL", "creator": {...}, /* ... */ } ],
  "trendingHashtags": [
    { "tag": "iitdelhi", "count": 45 },
    { "tag": "placements", "count": 32 }
  ],
  "feedType": "explore"
}
```

---

### `GET /api/explore/creators`
Popular/suggested creators ranked by follower count.

**Auth**: Optional | **Params**: `limit`

```json
// Response 200
{
  "items": [
    { "user": { /* ... */ }, "followerCount": 5000, "postCount": 120, "isFollowing": false }
  ]
}
```

---

### `GET /api/explore/reels`
Trending reels feed (sorted by views + likes).

**Auth**: Optional | **Params**: `limit`, `cursor`

---

### `GET /api/trending/topics`
Trending hashtags/topics with engagement scoring.

**Auth**: Public | **Params**: `limit`, `period` (`24h`, `7d`, `30d`)

```json
// Response 200
{
  "items": [
    { "rank": 1, "hashtag": "placements", "postCount": 45, "totalEngagement": 1200, "score": 67.5 }
  ],
  "period": "7d"
}
```

---

## 7. Social Interactions

### `POST /api/follow/:userId`
Follow a user. Intercepts for private accounts (creates follow request instead).

**Auth**: Auth

```json
// Response 200
{ "message": "Followed", "isFollowing": true, "viewerIsFollowing": true }

// Response 200 (already following)
{ "message": "Already following", "isFollowing": true }

// Response 200 (private account — request sent)
{ "message": "Follow request sent", "status": "PENDING" }
```

---

### `DELETE /api/follow/:userId`
Unfollow a user.

**Auth**: Auth

```json
// Response 200
{ "message": "Unfollowed", "isFollowing": false, "viewerIsFollowing": false }
```

---

### `POST /api/content/:contentId/like`
Like a post. If previously disliked, switches to like. Anti-abuse protected.

**Auth**: Auth

```json
// Response 200
{ "likeCount": 43, "viewerHasLiked": true, "viewerHasDisliked": false }
```

---

### `POST /api/content/:contentId/dislike`
Internal dislike signal (not shown to author, used for feed ranking).

**Auth**: Auth

```json
// Response 200
{ "viewerHasLiked": false, "viewerHasDisliked": true }
```

---

### `DELETE /api/content/:contentId/reaction`
Remove any reaction (like or dislike) from a post.

**Auth**: Auth

```json
// Response 200
{ "viewerHasLiked": false, "viewerHasDisliked": false }
```

---

### `POST /api/content/:contentId/save`
Save/bookmark a post.

**Auth**: Auth

```json
// Response 200
{ "saved": true }
```

---

### `DELETE /api/content/:contentId/save`
Unsave/unbookmark a post.

**Auth**: Auth

```json
// Response 200
{ "saved": false }
```

---

### `POST /api/content/:contentId/share`
Repost/share content (creates a new post linked to original). Optionally add a quote caption.

**Auth**: Auth

```json
// Request (optional body)
{ "caption": "This is amazing!" }

// Response 201
{ "post": { "id": "repost-uuid", "isRepost": true, "originalContentId": "...", /* ... */ } }

// Error 400
{ "error": "Cannot repost a repost", "code": "VALIDATION" }

// Error 409
{ "error": "Already shared this content", "code": "DUPLICATE" }
```

---

### `POST /api/content/:contentId/report`
Report content.

**Auth**: Auth

```json
// Request
{ "reason": "SPAM", "details": "This is clearly spam content" }

// Response 201
{ "message": "Report submitted" }
```

---

### `POST /api/content/:contentId/archive`
Archive own post (hides from public, keeps data).

**Auth**: Auth (author only)

```json
// Response 200
{ "message": "Post archived" }
```

---

### `POST /api/content/:contentId/unarchive`
Restore archived post to public.

**Auth**: Auth (author only)

```json
// Response 200
{ "message": "Post restored" }
```

---

### `POST /api/content/:contentId/pin`
Pin a post to your profile (unpins any existing pinned post).

**Auth**: Auth (author only)

```json
// Response 200
{ "message": "Post pinned to profile" }
```

---

### `DELETE /api/content/:contentId/pin`
Unpin a post.

**Auth**: Auth (author only)

```json
// Response 200
{ "message": "Post unpinned" }
```

---

### `POST /api/content/:contentId/hide`
Hide a post from your feed.

**Auth**: Auth

```json
// Response 200
{ "message": "Post hidden from your feed", "contentId": "..." }
```

---

### `DELETE /api/content/:contentId/hide`
Unhide a post.

**Auth**: Auth

```json
// Response 200
{ "message": "Post unhidden", "contentId": "..." }
```

---

### `GET /api/content/:contentId/likers`
Who liked a post.

**Auth**: Public | **Params**: `limit`, `offset`

```json
// Response 200
{
  "items": [ /* sanitized users */ ],
  "total": 43,
  "pagination": { "limit": 20, "offset": 0, "hasMore": true }
}
```

---

### `GET /api/content/:contentId/shares`
Who shared/reposted a post.

**Auth**: Public | **Params**: `limit`

```json
// Response 200
{
  "items": [
    { "repostId": "...", "author": { /* ... */ }, "caption": "...", "createdAt": "..." }
  ],
  "total": 5
}
```

---

## 8. Comments System

### `POST /api/content/:contentId/comments`
Create a comment on a post. AI-moderated.

**Auth**: Auth

```json
// Request
{ "body": "Great post!", "parentId": null }

// Response 201
{
  "comment": {
    "id": "comment-uuid",
    "contentId": "...",
    "authorId": "...",
    "body": "Great post!",
    "text": "Great post!",
    "parentId": null,
    "likeCount": 0,
    "author": { /* sanitized user */ },
    "createdAt": "..."
  }
}
```

---

### `GET /api/content/:contentId/comments`
List comments for a post.

**Auth**: Optional | **Params**: `limit`, `cursor`, `parentId` (for nested replies)

```json
// Response 200
{
  "items": [
    {
      "id": "...", "body": "...", "text": "...",
      "likeCount": 5, "author": { /* ... */ },
      "parentId": null, "createdAt": "..."
    }
  ],
  "comments": [ /* same as items (backward compat) */ ],
  "pagination": { "nextCursor": "...", "hasMore": false }
}
```

---

### `POST /api/content/:postId/comments/:commentId/like`
Like a comment.

**Auth**: Auth

```json
// Response 200
{ "liked": true, "commentLikeCount": 6 }
```

---

### `DELETE /api/content/:postId/comments/:commentId/like`
Unlike a comment.

**Auth**: Auth

```json
// Response 200
{ "liked": false, "commentLikeCount": 5 }
```

---

### `DELETE /api/content/:contentId/comments/:commentId`
Delete a comment (author of comment, post author, or moderator).

**Auth**: Auth

```json
// Response 200
{ "message": "Comment deleted" }
```

---

### `POST /api/content/:contentId/comments/:commentId/reply`
Reply to a specific comment (threaded).

**Auth**: Auth

```json
// Request
{ "text": "Thanks!" }

// Response 201
{
  "comment": {
    "id": "reply-uuid", "contentId": "...", "authorId": "...",
    "text": "Thanks!", "parentCommentId": "comment-uuid", "depth": 1,
    "author": { /* ... */ }
  }
}
```

---

### `PATCH /api/content/:contentId/comments/:commentId`
Edit a comment (author only).

**Auth**: Auth

```json
// Request
{ "text": "Updated comment" }

// Response 200
{ "message": "Comment updated", "comment": { "text": "Updated comment", "isEdited": true, /* ... */ } }
```

---

### `POST /api/content/:contentId/comments/:commentId/pin`
Pin a comment (post author only, one pinned comment per post).

**Auth**: Auth (post author only)

```json
// Response 200
{ "message": "Comment pinned" }
```

---

### `POST /api/content/:contentId/comments/:commentId/report`
Report a comment.

**Auth**: Auth

```json
// Request
{ "reason": "HARASSMENT", "details": "This comment is abusive" }

// Response 201
{ "message": "Comment reported" }
```

---

## 9. Stories

### `POST /api/stories`
Create a story (24h auto-expiry, supports interactive stickers).

**Auth**: Auth (adults only)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `mediaId` | string | Yes | Media asset ID |
| `type` | string | No | `IMAGE`, `VIDEO`, `TEXT` |
| `caption` | string | No | Max 500 chars |
| `textContent` | string | No | For TEXT type stories |
| `backgroundColor` | string | No | For TEXT type |
| `fontStyle` | string | No | For TEXT type |
| `privacy` | string | No | `EVERYONE`, `CLOSE_FRIENDS`, `CUSTOM` |
| `stickers` | array | No | Interactive sticker definitions |

**Sticker types:**
```json
{
  "stickers": [
    { "type": "POLL", "question": "Coffee or Tea?", "options": ["Coffee", "Tea"], "position": { "x": 50, "y": 60 } },
    { "type": "QUESTION", "prompt": "Ask me anything!", "position": { "x": 50, "y": 80 } },
    { "type": "QUIZ", "question": "Capital of India?", "options": ["Mumbai", "Delhi", "Kolkata"], "correctIndex": 1 },
    { "type": "EMOJI_SLIDER", "emoji": "🔥", "question": "Rate this!" },
    { "type": "COUNTDOWN", "title": "New Year!", "endAt": "2026-01-01T00:00:00Z" },
    { "type": "MENTION", "userId": "user-uuid" },
    { "type": "LOCATION", "name": "IIT Delhi" },
    { "type": "HASHTAG", "tag": "#placement" },
    { "type": "LINK", "url": "https://example.com", "label": "Visit" },
    { "type": "MUSIC", "trackId": "track-1", "trackName": "Song" }
  ]
}
```

```json
// Response 201
{
  "story": {
    "id": "story-uuid",
    "authorId": "...",
    "mediaUrl": "...",
    "type": "IMAGE",
    "status": "ACTIVE",
    "privacy": "EVERYONE",
    "viewCount": 0,
    "reactionCount": 0,
    "stickers": [ /* ... */ ],
    "expiresAt": "2025-01-16T10:00:00.000Z",
    "createdAt": "2025-01-15T10:00:00.000Z"
  }
}
```

---

### `GET /api/stories`
Story rail (alias for `/stories/feed`).

**Auth**: Auth

---

### `GET /api/stories/feed`
Story rail with seen/unseen tracking.

**Auth**: Auth

---

### `GET /api/stories/:storyId`
View a single story (auto-tracks view, deduplicated).

**Auth**: Auth

```json
// Response 200
{
  "story": { /* story object */ },
  "viewerHasViewed": true,
  "viewerReaction": "❤️"
}

// Error 410
{ "error": "This story has expired", "code": "EXPIRED" }
```

---

### `DELETE /api/stories/:storyId`
Delete own story.

**Auth**: Auth (author or admin)

```json
// Response 200
{ "message": "Story deleted" }
```

---

### `PATCH /api/stories/:storyId`
Edit story metadata (caption, privacy, stickers).

**Auth**: Auth (author only)

```json
// Request
{ "caption": "Updated caption", "privacy": "CLOSE_FRIENDS" }

// Response 200
{ "story": { /* updated story */ } }
```

---

### `GET /api/stories/:storyId/views`
Viewers list (owner or admin only).

**Auth**: Auth (story owner or admin)

```json
// Response 200
{
  "viewers": [
    { "user": { /* ... */ }, "viewedAt": "...", "reaction": "🔥" }
  ],
  "totalViews": 150
}
```

---

### `POST /api/stories/:storyId/view`
Explicitly mark story as viewed.

**Auth**: Auth

```json
// Response 200
{ "viewed": true }
```

---

### `POST /api/stories/:storyId/view-duration`
Track view duration for analytics.

**Auth**: Auth

```json
// Request
{ "durationMs": 3500 }
```

---

### `GET /api/stories/:storyId/view-analytics`
View duration analytics (owner/admin only).

**Auth**: Auth (owner or admin)

---

### `POST /api/stories/:storyId/react`
React with emoji (6 quick reactions).

**Auth**: Auth

```json
// Request
{ "emoji": "🔥" }

// Response 200
{ "reaction": "🔥", "reactionCount": 23 }
```

---

### `DELETE /api/stories/:storyId/react`
Remove emoji reaction.

**Auth**: Auth

---

### `POST /api/stories/:storyId/reply`
Reply to a story (DM-like).

**Auth**: Auth

```json
// Request
{ "text": "This is amazing!" }

// Response 201
{ "reply": { "id": "...", "text": "...", "author": { /* ... */ } } }
```

---

### `GET /api/stories/:storyId/replies`
Get replies (story owner only).

**Auth**: Auth (owner only)

---

### `POST /api/stories/:storyId/report`
Report a story.

**Auth**: Auth

```json
// Request
{ "reason": "INAPPROPRIATE" }

// Response 201
{ "message": "Story reported" }
```

---

### `POST /api/stories/:storyId/share`
Share story as a post.

**Auth**: Auth

---

### `GET /api/users/:userId/stories`
Get a user's active (non-expired) stories.

**Auth**: Auth

---

### `GET /api/me/stories/archive`
My archived/expired stories.

**Auth**: Auth

---

### `GET /api/me/stories/insights`
Story insights (views, reactions, reach).

**Auth**: Auth

---

### `GET /api/stories/events/stream`
Real-time SSE stream for story events.

**Auth**: Auth (via query `?token=` or header)

---

## 10. Story Stickers & Interactions

### `POST /api/stories/:storyId/sticker/:stickerId/respond`
Respond to an interactive sticker (poll vote, question answer, quiz answer, emoji slider).

**Auth**: Auth

```json
// Request — Poll
{ "optionIndex": 0 }

// Request — Question
{ "text": "My answer to your question" }

// Request — Quiz
{ "optionIndex": 1 }

// Request — Emoji slider
{ "value": 0.85 }

// Response 200
{ "response": { "id": "...", "stickerId": "...", /* ... */ } }
```

---

### `GET /api/stories/:storyId/sticker/:stickerId/results`
Get aggregated sticker results (public).

**Auth**: Auth

```json
// Response 200 (Poll)
{
  "results": {
    "type": "POLL",
    "totalResponses": 45,
    "options": [
      { "text": "Coffee", "count": 28, "percentage": 62.2 },
      { "text": "Tea", "count": 17, "percentage": 37.8 }
    ]
  }
}
```

---

### `GET /api/stories/:storyId/sticker/:stickerId/responses`
Get all individual responses (story owner/admin only).

**Auth**: Auth (owner or admin)

---

## 11. Story Settings & Close Friends

### `GET /api/me/story-settings`
Get story privacy settings.

**Auth**: Auth

```json
// Response 200
{
  "allowReplies": "EVERYONE",
  "allowSharing": true,
  "hideStoryFrom": [],
  "closeFriendsOnly": false
}
```

---

### `PATCH /api/me/story-settings`
Update story settings.

**Auth**: Auth

```json
// Request
{ "allowReplies": "CLOSE_FRIENDS", "allowSharing": false }
```

---

### `GET /api/me/close-friends`
List close friends.

**Auth**: Auth

```json
// Response 200
{ "items": [ /* sanitized users */ ], "count": 15, "maxAllowed": 50 }
```

---

### `POST /api/me/close-friends/:userId`
Add user to close friends list.

**Auth**: Auth

```json
// Response 200
{ "message": "Added to close friends" }
```

---

### `DELETE /api/me/close-friends/:userId`
Remove from close friends.

**Auth**: Auth

---

## 12. Story Highlights

### `POST /api/me/highlights`
Create a highlight from stories.

**Auth**: Auth

```json
// Request
{ "title": "Travel 2024", "coverMediaId": "media-uuid", "storyIds": ["story-1", "story-2"] }

// Response 201
{ "highlight": { "id": "...", "title": "Travel 2024", "items": [...] } }
```

---

### `GET /api/users/:userId/highlights`
Get a user's highlights (batch optimized).

**Auth**: Optional

```json
// Response 200
{
  "highlights": [
    { "id": "...", "title": "Travel 2024", "coverUrl": "...", "itemCount": 5, "items": [...] }
  ]
}
```

---

### `PATCH /api/me/highlights/:highlightId`
Edit highlight (title, cover, add/remove stories).

**Auth**: Auth

---

### `DELETE /api/me/highlights/:highlightId`
Delete a highlight.

**Auth**: Auth

---

## 13. Reels

### `POST /api/reels`
Create a reel (draft or publish).

**Auth**: Auth (adults only)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `mediaId` | string | Yes | Video media asset |
| `caption` | string | No | Max 2200 chars |
| `hashtags` | string[] | No | Max 30 |
| `mentions` | string[] | No | Max 20 user IDs |
| `visibility` | string | No | `PUBLIC`, `FOLLOWERS`, `PRIVATE` |
| `status` | string | No | `DRAFT` or `PUBLISHED` |
| `audioId` | string | No | Audio track reference |
| `remixOf` | string | No | Reel ID being remixed |
| `seriesId` | string | No | Reel series reference |
| `seriesOrder` | int | No | Order in series |
| `durationMs` | int | No | Duration in ms (max 90000) |

```json
// Response 201
{
  "reel": {
    "id": "reel-uuid", "creatorId": "...", "caption": "...",
    "status": "PUBLISHED", "visibility": "PUBLIC",
    "mediaUrl": "...", "mediaStatus": "READY",
    "likeCount": 0, "commentCount": 0, "viewCount": 0,
    "createdAt": "..."
  }
}
```

---

### `GET /api/reels/feed`
Main discovery reel feed with Smart Ranking.

**Auth**: Optional | **Params**: `limit`, `cursor`

```json
// Response 200
{
  "items": [ { /* reel with creator */ } ],
  "pagination": { "nextCursor": "...", "hasMore": true },
  "feedType": "discovery"
}
```

---

### `GET /api/reels/following`
Reels from followed users.

**Auth**: Auth | **Params**: `limit`, `cursor`

---

### `GET /api/reels/trending`
Trending/viral reels feed.

**Auth**: Optional | **Params**: `limit`, `cursor`

---

### `GET /api/reels/personalized`
Personalized reel feed with user-aware ranking.

**Auth**: Auth | **Params**: `limit`, `cursor`

---

### `GET /api/reels/:reelId`
Reel detail view.

**Auth**: Optional

```json
// Response 200
{
  "reel": {
    "id": "...", "caption": "...", "creator": { /* ... */ },
    "likeCount": 500, "commentCount": 23, "viewCount": 12000,
    "viewerHasLiked": false, "viewerHasSaved": false,
    /* ... full reel object */
  }
}
```

---

### `PATCH /api/reels/:reelId`
Edit reel metadata (caption, hashtags, visibility).

**Auth**: Auth (creator only)

---

### `DELETE /api/reels/:reelId`
Soft delete reel.

**Auth**: Auth (creator or admin)

---

### `POST /api/reels/:reelId/publish`
Publish a draft reel.

**Auth**: Auth (creator only)

---

### `POST /api/reels/:reelId/archive`
Archive reel (hide from public).

**Auth**: Auth (creator only)

---

### `POST /api/reels/:reelId/restore`
Restore archived reel.

**Auth**: Auth (creator only)

---

### `POST /api/reels/:reelId/pin`
Pin reel to creator profile.

**Auth**: Auth (creator only)

---

### `DELETE /api/reels/:reelId/pin`
Unpin reel.

**Auth**: Auth (creator only)

---

### `GET /api/users/:userId/reels`
Get a user's reels.

**Auth**: Optional | **Params**: `limit`, `cursor`

---

### `GET /api/reels/audio/:audioId`
Reels using a specific audio track.

**Auth**: Optional | **Params**: `limit`, `cursor`

---

### `GET /api/reels/sounds/popular`
Popular audio tracks.

**Auth**: Optional | **Params**: `limit`

---

## 14. Reel Interactions & Metrics

### `POST /api/reels/:reelId/like`
Like a reel.

**Auth**: Auth

```json
// Response 200
{ "liked": true, "likeCount": 501 }
```

---

### `DELETE /api/reels/:reelId/like`
Unlike a reel.

**Auth**: Auth

---

### `POST /api/reels/:reelId/save`
Save/bookmark a reel.

**Auth**: Auth

---

### `DELETE /api/reels/:reelId/save`
Unsave a reel.

**Auth**: Auth

---

### `POST /api/reels/:reelId/comment`
Comment on a reel (AI-moderated).

**Auth**: Auth

```json
// Request
{ "text": "Amazing edit!" }

// Response 201
{ "comment": { "id": "...", "text": "...", "author": { /* ... */ } } }
```

---

### `GET /api/reels/:reelId/comments`
List reel comments.

**Auth**: Optional | **Params**: `limit`, `cursor`

---

### `POST /api/reels/:reelId/report`
Report a reel (auto-hold at 3+ reports).

**Auth**: Auth

```json
// Request
{ "reason": "INAPPROPRIATE", "details": "..." }
```

---

### `POST /api/reels/:reelId/hide`
Hide reel from your feed.

**Auth**: Auth

---

### `POST /api/reels/:reelId/not-interested`
Mark reel as not interested (affects recommendations).

**Auth**: Auth

---

### `POST /api/reels/:reelId/share`
Track share event.

**Auth**: Auth

---

### `POST /api/reels/:reelId/watch`
Track watch event with duration, completion, replay data.

**Auth**: Auth

```json
// Request
{ "watchDurationMs": 45000, "completionRate": 0.85, "isReplay": false }
```

---

### `POST /api/reels/:reelId/view`
Track impression/view.

**Auth**: Auth

---

### `GET /api/reels/:reelId/likers`
Who liked a reel.

**Auth**: Optional | **Params**: `limit`, `offset`

---

### `GET /api/reels/:reelId/remixes`
Get remixes of a reel.

**Auth**: Optional

---

### `POST /api/reels/:reelId/duet`
Create a duet reference.

**Auth**: Auth

---

## 15. Reel Creator Tools

### `POST /api/me/reels/series`
Create a reel series.

**Auth**: Auth

```json
// Request
{ "title": "Cooking 101", "description": "..." }

// Response 201
{ "series": { "id": "...", "title": "...", "creatorId": "..." } }
```

---

### `GET /api/users/:userId/reels/series`
Get user's reel series.

**Auth**: Optional

---

### `GET /api/me/reels/archive`
Creator's archived reels.

**Auth**: Auth

---

### `GET /api/me/reels/saved`
Saved reels list.

**Auth**: Auth

---

### `GET /api/me/reels/analytics`
Creator's own reel analytics.

**Auth**: Auth

```json
// Response 200
{
  "totalReels": 15, "totalViews": 45000,
  "totalLikes": 3200, "totalComments": 450,
  "avgCompletionRate": 0.72,
  "topReels": [ /* ... */ ]
}
```

---

### `GET /api/me/reels/analytics/detailed`
Deeper creator analytics (per-reel breakdown).

**Auth**: Auth

---

### `POST /api/reels/:reelId/processing`
Update processing status (internal/system use).

**Auth**: Auth

---

### `GET /api/reels/:reelId/processing`
Get processing status.

**Auth**: Auth

---

## 16. Pages

### `POST /api/pages`
Create a page.

**Auth**: Auth

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Page name |
| `slug` | string | No | Custom URL slug |
| `category` | string | Yes | See page categories |
| `description` | string | No | Page description |
| `isOfficial` | bool | No | Official entity page |
| `linkedEntityType` | string | No | `COLLEGE`, `TRIBE`, `CLUB` |
| `linkedEntityId` | string | No | Entity ID |

```json
// Response 201
{ "page": { "id": "...", "slug": "iit-delhi-official", "name": "...", "category": "...", /* ... */ } }
```

---

### `GET /api/pages`
Search/list pages.

**Auth**: Optional | **Params**: `q`, `category`, `limit`, `offset`

---

### `GET /api/pages/:idOrSlug`
Page detail (by ID or slug).

**Auth**: Optional

---

### `PATCH /api/pages/:pageId`
Update page (name, description, category, etc.).

**Auth**: Auth (page admin+ role)

---

### `DELETE /api/pages/:pageId`
Delete a page (owner/admin only).

**Auth**: Auth (owner or system admin)

---

### `POST /api/pages/:pageId/archive`
Archive a page.

**Auth**: Auth (page owner/admin)

---

### `POST /api/pages/:pageId/restore`
Restore archived page.

**Auth**: Auth (page owner/admin)

---

### `POST /api/pages/:pageId/follow`
Follow a page.

**Auth**: Auth

```json
// Response 200
{ "following": true, "followerCount": 501 }
```

---

### `DELETE /api/pages/:pageId/follow`
Unfollow a page.

**Auth**: Auth

---

### `GET /api/pages/:pageId/followers`
Page followers list (page owner/admin).

**Auth**: Auth (page admin)

---

### `GET /api/pages/:pageId/members`
List page team members and roles.

**Auth**: Optional

---

### `POST /api/pages/:pageId/members`
Add a member to page.

**Auth**: Auth (page owner/admin)

```json
// Request
{ "userId": "user-uuid", "role": "EDITOR" }
```

---

### `PATCH /api/pages/:pageId/members/:userId`
Change member role.

**Auth**: Auth (page owner)

```json
// Request
{ "role": "ADMIN" }
```

---

### `DELETE /api/pages/:pageId/members/:userId`
Remove member from page.

**Auth**: Auth (page owner/admin)

---

### `POST /api/pages/:pageId/transfer-ownership`
Transfer page ownership.

**Auth**: Auth (current owner only)

```json
// Request
{ "newOwnerId": "user-uuid" }
```

---

### `POST /api/pages/:pageId/invite`
Invite user to join page team.

**Auth**: Auth (page admin)

```json
// Request
{ "userId": "user-uuid", "role": "EDITOR" }
```

---

### `POST /api/pages/:pageId/report`
Report a page.

**Auth**: Auth

---

### `POST /api/pages/:pageId/request-verification`
Request page verification badge.

**Auth**: Auth (page owner)

---

### `GET /api/me/pages`
My managed pages.

**Auth**: Auth

---

## 17. Page Content & Analytics

### `GET /api/pages/:pageId/posts`
List page-authored posts.

**Auth**: Optional | **Params**: `limit`, `cursor`

---

### `POST /api/pages/:pageId/posts`
Create a post as a page.

**Auth**: Auth (page editor+ role)

```json
// Request
{ "caption": "Official announcement from our page", "mediaIds": ["..."] }

// Response 201
{ "post": { "authorType": "PAGE", "pageId": "...", /* enriched post */ } }
```

---

### `PATCH /api/pages/:pageId/posts/:postId`
Edit a page-authored post.

**Auth**: Auth (page editor+ role)

---

### `DELETE /api/pages/:pageId/posts/:postId`
Delete a page-authored post.

**Auth**: Auth (page editor+ role)

---

### `GET /api/pages/:pageId/analytics`
Page analytics dashboard.

**Auth**: Auth (page admin)

```json
// Response 200
{
  "followers": 5000, "totalPosts": 120,
  "totalLikes": 45000, "totalComments": 3200,
  "recentGrowth": { "followers": "+150", "engagement": "+12%" }
}
```

---

### `GET /api/admin/pages/verification-requests`
List page verification requests (admin only).

**Auth**: Admin

---

### `POST /api/admin/pages/verification-decide`
Approve or reject page verification.

**Auth**: Admin

```json
// Request
{ "pageId": "...", "decision": "APPROVED", "reason": "Verified official account" }
```

---

## 18. Events

### `POST /api/events`
Create an event.

**Auth**: Auth (adults only)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Max 200 chars |
| `description` | string | No | Max 5000 chars |
| `category` | string | No | `ACADEMIC`, `CULTURAL`, `SPORTS`, `SOCIAL`, `WORKSHOP`, `PLACEMENT`, `OTHER` |
| `visibility` | string | No | `PUBLIC`, `COLLEGE`, `PRIVATE` |
| `startAt` | ISO string | Yes | Event start time |
| `endAt` | ISO string | No | Event end time |
| `location` | string | No | Max 300 chars |
| `capacity` | int | No | Max attendees |
| `collegeId` | string | No | College filter |
| `coverMediaId` | string | No | Cover image |

```json
// Response 201
{ "event": { "id": "...", "title": "...", "status": "DRAFT", /* ... */ } }
```

---

### `GET /api/events/search`
Search events.

**Auth**: Optional | **Params**: `q`, `category`, `status`, `collegeId`, `limit`, `cursor`

---

### `GET /api/events/:eventId`
Event detail.

**Auth**: Optional

---

### `PATCH /api/events/:eventId`
Update event.

**Auth**: Auth (organizer or admin)

---

### `DELETE /api/events/:eventId`
Delete event.

**Auth**: Auth (organizer or admin)

---

### `POST /api/events/:eventId/publish`
Publish draft event.

**Auth**: Auth (organizer)

---

### `POST /api/events/:eventId/cancel`
Cancel event.

**Auth**: Auth (organizer or admin)

---

### `POST /api/events/:eventId/archive`
Archive past event.

**Auth**: Auth (organizer)

---

### `POST /api/events/:eventId/rsvp`
RSVP to event.

**Auth**: Auth

```json
// Request
{ "status": "GOING" }

// Response 200 or 201
{ "rsvp": { "userId": "...", "eventId": "...", "status": "GOING" } }
```

---

### `DELETE /api/events/:eventId/rsvp`
Cancel RSVP.

**Auth**: Auth

---

### `GET /api/events/:eventId/attendees`
RSVP list (going + interested).

**Auth**: Optional | **Params**: `limit`, `offset`, `status` (`GOING` or `INTERESTED`)

---

### `POST /api/events/:eventId/report`
Report event.

**Auth**: Auth

---

### `POST /api/events/:eventId/remind`
Set reminder for event.

**Auth**: Auth

---

### `DELETE /api/events/:eventId/remind`
Remove reminder.

**Auth**: Auth

---

### `GET /api/me/events`
My created events.

**Auth**: Auth

---

### `GET /api/me/events/rsvps`
Events I've RSVP'd to.

**Auth**: Auth

---

### Admin Endpoints:
- `GET /api/admin/events` — Moderation queue
- `PATCH /api/admin/events/:eventId/moderate` — Moderate event
- `GET /api/admin/events/analytics` — Platform event analytics
- `POST /api/admin/events/:eventId/recompute-counters` — Recompute counters

---

## 19. Tribes

### `GET /api/tribes`
List all 21 tribes (cached).

**Auth**: Public

```json
// Response 200
{
  "tribes": [
    {
      "id": "...", "tribeCode": "SHIVAJI", "tribeName": "Shivaji",
      "heroName": "Chhatrapati Shivaji Maharaj", "animalIcon": "🦁",
      "primaryColor": "#FF6B00", "membersCount": 12500, "totalSalutes": 45000
    }
  ]
}
```

---

### `GET /api/tribes/leaderboard`
Engagement-ranked tribe leaderboard.

**Auth**: Public

---

### `GET /api/tribes/standings/current`
Current season standings.

**Auth**: Public

---

### `GET /api/tribes/:tribeId`
Tribe detail with full info.

**Auth**: Public

---

### `GET /api/tribes/:tribeId/members`
Tribe members list.

**Auth**: Optional | **Params**: `limit`, `offset`

---

### `GET /api/tribes/:tribeId/board`
Tribe board governance (captain, vice-captain, leads).

**Auth**: Public

---

### `GET /api/tribes/:tribeId/fund`
Tribe fund info.

**Auth**: Public

---

### `GET /api/tribes/:tribeId/salutes`
Salute history for tribe.

**Auth**: Public | **Params**: `limit`, `cursor`

---

### `GET /api/tribes/:tribeId/feed`
Tribe content feed.

**Auth**: Optional | **Params**: `limit`, `cursor`

---

### `GET /api/tribes/:tribeId/events`
Tribe events.

**Auth**: Optional

---

### `GET /api/tribes/:tribeId/stats`
Tribe statistics.

**Auth**: Public

---

### `POST /api/tribes/:tribeId/join`
Join a tribe.

**Auth**: Auth

---

### `POST /api/tribes/:tribeId/leave`
Leave a tribe.

**Auth**: Auth

---

### `POST /api/tribes/:tribeId/cheer`
Cheer for your tribe (engagement action).

**Auth**: Auth

---

### `GET /api/me/tribe`
My tribe info.

**Auth**: Auth

---

### `GET /api/users/:userId/tribe`
Another user's tribe.

**Auth**: Optional

---

### Admin Tribe Endpoints:
- `GET /api/admin/tribes/distribution` — Distribution stats
- `POST /api/admin/tribes/reassign` — Reassign user to different tribe
- `POST /api/admin/tribes/migrate` — Migrate users from house to tribe
- `POST /api/admin/tribes/boards` — Create or update tribe board
- `POST /api/admin/tribe-seasons` — Create or manage season
- `GET /api/admin/tribe-seasons` — List seasons
- `POST /api/admin/tribe-salutes/adjust` — Manual salute adjustment
- `POST /api/admin/tribe-awards/resolve` — Resolve annual award

---

## 20. Tribe Contests

### Public Contest Endpoints:

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/tribe-contests` | List contests (filterable by status) |
| `GET` | `/api/tribe-contests/:id` | Contest detail |
| `GET` | `/api/tribe-contests/:id/entries` | List entries |
| `GET` | `/api/tribe-contests/:id/leaderboard` | Contest leaderboard |
| `GET` | `/api/tribe-contests/:id/results` | Official results |
| `POST` | `/api/tribe-contests/:id/enter` | Submit entry |
| `POST` | `/api/tribe-contests/:id/vote` | Vote on entry |
| `POST` | `/api/tribe-contests/:id/withdraw` | Withdraw own entry |
| `GET` | `/api/tribe-contests/seasons` | List seasons |
| `GET` | `/api/tribe-contests/seasons/:id/standings` | Season standings |

### Live SSE Streams:
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/tribe-contests/live-feed` | Global contest activity SSE |
| `GET` | `/api/tribe-contests/:id/live` | Live contest scoreboard SSE |
| `GET` | `/api/tribe-contests/seasons/:id/live-standings` | Live season standings SSE |

### Admin Contest Endpoints:

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/admin/tribe-contests` | Create contest |
| `GET` | `/api/admin/tribe-contests` | List all contests |
| `GET` | `/api/admin/tribe-contests/:id` | Admin contest detail |
| `GET` | `/api/admin/tribe-contests/dashboard` | Dashboard stats |
| `POST` | `/api/admin/tribe-contests/:id/publish` | DRAFT → PUBLISHED |
| `POST` | `/api/admin/tribe-contests/:id/open-entries` | PUBLISHED → ENTRY_OPEN |
| `POST` | `/api/admin/tribe-contests/:id/close-entries` | ENTRY_OPEN → ENTRY_CLOSED |
| `POST` | `/api/admin/tribe-contests/:id/lock` | EVALUATING → LOCKED |
| `POST` | `/api/admin/tribe-contests/:id/resolve` | LOCKED → RESOLVED |
| `POST` | `/api/admin/tribe-contests/:id/cancel` | Cancel contest |
| `POST` | `/api/admin/tribe-contests/:id/disqualify` | Disqualify entry |
| `POST` | `/api/admin/tribe-contests/:id/judge-score` | Submit judge score |
| `POST` | `/api/admin/tribe-contests/:id/compute-scores` | Compute/recompute scores |
| `POST` | `/api/admin/tribe-contests/:id/recompute-broadcast` | Compute + broadcast rank changes |
| `POST` | `/api/admin/tribe-contests/rules` | Add versioned rule |
| `POST` | `/api/admin/tribe-salutes/adjust` | Manual salute adjustment |

---

## 21. Search & Discovery

### `GET /api/search`
Unified search across users, posts, reels, hashtags, pages, tribes.

**Auth**: Optional | **Params**: `q` (required, min 1 char), `type` (`users`, `content`, `posts`, `reels`, `hashtags`, `pages`, `tribes`), `limit`

```json
// Response 200
{
  "users": [ { /* sanitized user + relevance */ } ],
  "posts": [ { /* enriched posts */ } ],
  "reels": [ { /* reels */ } ],
  "hashtags": [ { "tag": "...", "postCount": 45 } ],
  "pages": [ { /* page snippets */ } ],
  "tribes": [ { /* tribe info */ } ],
  "query": "iit delhi",
  "took": 45
}
```

---

### `GET /api/search/autocomplete`
Quick suggestions as you type.

**Auth**: Optional | **Params**: `q` (min 1 char), `limit`

```json
// Response 200
{
  "suggestions": [
    { "type": "user", "text": "aarav.21", "id": "..." },
    { "type": "hashtag", "text": "#iitdelhi", "count": 45 },
    { "type": "page", "text": "IIT Delhi Official", "id": "..." }
  ]
}
```

---

### `GET /api/search/users`
Search users specifically.

**Auth**: Optional | **Params**: `q`, `limit`

---

### `GET /api/search/content`
Search posts/content.

**Auth**: Optional | **Params**: `q`, `limit`

---

### `GET /api/search/hashtags`
Search and rank hashtags.

**Auth**: Optional | **Params**: `q`, `limit`

---

### `GET /api/search/recent`
Get recent searches.

**Auth**: Auth

```json
// Response 200
{ "items": [ { "query": "iit delhi", "searchedAt": "..." } ], "count": 5 }
```

---

### `DELETE /api/search/recent`
Clear recent searches.

**Auth**: Auth

---

## 22. Hashtags

### `GET /api/hashtags/:tag`
Hashtag detail + stats.

**Auth**: Optional

```json
// Response 200
{
  "hashtag": "iitdelhi",
  "postCount": 450,
  "weeklyGrowth": 12,
  "trending": true
}
```

---

### `GET /api/hashtags/trending`
Top trending hashtags.

**Auth**: Optional | **Params**: `limit`

---

### `GET /api/hashtags/:tag/feed`
Content feed for a hashtag.

**Auth**: Optional | **Params**: `limit`, `cursor`

---

## 23. Notifications

### `GET /api/notifications`
List notifications (supports grouped view).

**Auth**: Auth | **Params**: `limit`, `cursor`, `type` (filter by notification type)

```json
// Response 200
{
  "items": [
    {
      "id": "...", "type": "LIKE", "message": "Aarav liked your post",
      "actorId": "...", "targetType": "CONTENT", "targetId": "...",
      "read": false, "createdAt": "..."
    }
  ],
  "pagination": { "nextCursor": "...", "hasMore": true },
  "unreadCount": 12
}
```

---

### `GET /api/notifications/unread-count`
Lightweight unread count (for badge).

**Auth**: Auth

```json
// Response 200
{ "count": 12 }
```

---

### `PATCH /api/notifications/read`
Mark notifications as read (specific IDs or all).

**Auth**: Auth

```json
// Request — Specific
{ "ids": ["notif-1", "notif-2"] }

// Request — All
{ "all": true }

// Response 200
{ "updatedCount": 2 }
```

---

### `POST /api/notifications/read-all`
Mark all notifications as read.

**Auth**: Auth

---

### `DELETE /api/notifications/clear`
Clear all notifications.

**Auth**: Auth

---

### `GET /api/notifications/preferences`
Get notification preferences.

**Auth**: Auth

---

### `PATCH /api/notifications/preferences`
Update notification preferences.

**Auth**: Auth

```json
// Request
{ "likes": true, "comments": true, "follows": false, "mentions": true }
```

---

### `POST /api/notifications/register-device`
Register push notification device token.

**Auth**: Auth

```json
// Request
{ "token": "fcm-device-token", "platform": "android" }
```

---

### `DELETE /api/notifications/unregister-device`
Remove/deactivate device token.

**Auth**: Auth

---

## 24. Follow Requests (Private Accounts)

### `GET /api/me/follow-requests`
Pending follow requests received.

**Auth**: Auth | **Params**: `limit`, `cursor`

```json
// Response 200
{
  "items": [
    { "id": "req-uuid", "fromUser": { /* sanitized user */ }, "createdAt": "..." }
  ],
  "pagination": { "nextCursor": "...", "hasMore": false }
}
```

---

### `GET /api/me/follow-requests/sent`
Follow requests you've sent.

**Auth**: Auth

---

### `GET /api/me/follow-requests/count`
Pending request count (for badge).

**Auth**: Auth

```json
// Response 200
{ "count": 3 }
```

---

### `POST /api/follow-requests/:requestId/accept`
Accept a follow request.

**Auth**: Auth

```json
// Response 200
{ "message": "Follow request accepted" }
```

---

### `POST /api/follow-requests/:requestId/reject`
Reject a follow request.

**Auth**: Auth

---

### `DELETE /api/follow-requests/:requestId`
Cancel a sent request.

**Auth**: Auth

---

### `POST /api/follow-requests/accept-all`
Accept all pending follow requests.

**Auth**: Auth

---

## 25. Analytics

### `POST /api/analytics/track`
Track an impression/view/profile-visit event.

**Auth**: Auth

```json
// Request
{ "eventType": "PROFILE_VISIT", "targetId": "user-uuid", "metadata": {} }
```

---

### `GET /api/analytics/overview`
Overall account analytics.

**Auth**: Auth | **Params**: `period` (`7d`, `30d`, `90d`)

```json
// Response 200
{
  "period": "30d",
  "impressions": 45000,
  "reach": 12000,
  "profileVisits": 850,
  "engagement": {
    "likes": 3200, "comments": 450, "saves": 230, "shares": 89,
    "rate": 0.087
  },
  "growth": { "followers": "+150", "followersChange": 0.11 }
}
```

---

### `GET /api/analytics/content`
Content performance analytics (all posts).

**Auth**: Auth | **Params**: `period`, `limit`

---

### `GET /api/analytics/content/:contentId`
Single content deep analytics.

**Auth**: Auth

```json
// Response 200
{
  "content": { /* post data */ },
  "analytics": {
    "impressions": 5000, "reach": 2000,
    "likes": 320, "comments": 45, "saves": 23, "shares": 12,
    "engagementRate": 0.08,
    "hourlyBreakdown": [ /* { hour, impressions, likes } */ ]
  }
}
```

---

### `GET /api/analytics/audience`
Audience demographics & growth.

**Auth**: Auth | **Params**: `period`

---

### `GET /api/analytics/reach`
Reach & impressions time series.

**Auth**: Auth | **Params**: `period`

---

### `GET /api/analytics/stories`
Story performance analytics.

**Auth**: Auth | **Params**: `period`

---

### `GET /api/analytics/reels`
Reel performance analytics.

**Auth**: Auth | **Params**: `period`

---

### `GET /api/analytics/profile-visits`
Profile visit details.

**Auth**: Auth | **Params**: `period`

---

## 26. Media Upload & Management

### `POST /api/media/upload-init`
Get signed URL for direct-to-Supabase upload.

**Auth**: Auth

```json
// Request
{ "filename": "photo.jpg", "mimeType": "image/jpeg", "fileSize": 2048000 }

// Response 200
{
  "mediaId": "media-uuid",
  "uploadUrl": "https://supabase-storage-url/...",
  "expiresIn": 3600,
  "headers": { "Content-Type": "image/jpeg" }
}
```

---

### `POST /api/media/upload-complete`
Finalize upload after client uploads to Supabase.

**Auth**: Auth

```json
// Request
{ "mediaId": "media-uuid" }

// Response 200
{
  "media": {
    "id": "media-uuid", "publicUrl": "https://...", "type": "IMAGE",
    "mimeType": "image/jpeg", "status": "READY"
  }
}
```

---

### `GET /api/media/upload-status/:mediaId`
Check upload status.

**Auth**: Auth

```json
// Response 200
{ "mediaId": "...", "status": "READY", "publicUrl": "https://..." }
```

---

### `POST /api/media/upload`
Legacy base64 upload (backward compatibility).

**Auth**: Auth

```json
// Request
{ "data": "base64-encoded-data", "mimeType": "image/jpeg" }
```

---

### `GET /api/media/:mediaId`
Serve media (redirect to Supabase CDN or stream).

**Auth**: Public

---

### `DELETE /api/media/:mediaId`
Delete owned media.

**Auth**: Auth (owner only)

---

## 27. Video Transcoding

### `POST /api/transcode/:mediaId`
Trigger video transcoding (HLS adaptive bitrate).

**Auth**: Auth

```json
// Response 200
{ "jobId": "job-uuid", "mediaId": "...", "status": "QUEUED" }
```

---

### `GET /api/transcode/:jobId/status`
Check transcoding job status.

**Auth**: Auth

```json
// Response 200
{ "jobId": "...", "status": "PROCESSING", "progress": 45 }
```

---

### `GET /api/transcode/media/:mediaId`
Get transcode info for media.

**Auth**: Auth

---

### `GET /api/media/:mediaId/stream`
Get HLS master playlist info.

**Auth**: Public

---

### `GET /api/media/:mediaId/thumbnails`
Get generated thumbnails for a video.

**Auth**: Public

---

### `GET /api/transcode/queue`
View transcoding queue.

**Auth**: Auth

---

### `POST /api/transcode/:jobId/cancel`
Cancel a pending/processing job.

**Auth**: Auth

---

### `POST /api/transcode/:jobId/retry`
Retry a failed job.

**Auth**: Auth

---

## 28. Board Notices

### `POST /api/board/notices`
Create a board notice.

**Auth**: Auth (board member)

```json
// Request
{
  "title": "Important Update", "body": "...",
  "priority": "HIGH", "collegeId": "..."
}
```

---

### `GET /api/board/notices/:noticeId`
Notice detail.

**Auth**: Optional

---

### `PATCH /api/board/notices/:noticeId`
Edit notice.

**Auth**: Auth (author or admin)

---

### `DELETE /api/board/notices/:noticeId`
Delete notice.

**Auth**: Auth (author or admin)

---

### `POST /api/board/notices/:noticeId/pin`
Pin notice.

**Auth**: Auth (board member)

---

### `DELETE /api/board/notices/:noticeId/pin`
Unpin notice.

**Auth**: Auth (board member)

---

### `POST /api/board/notices/:noticeId/acknowledge`
Acknowledge a notice.

**Auth**: Auth

---

### `GET /api/board/notices/:noticeId/acknowledgments`
List acknowledgments.

**Auth**: Auth

---

### `GET /api/colleges/:collegeId/notices`
Public college notices (pinned first).

**Auth**: Public

---

### `GET /api/me/board/notices`
My created notices.

**Auth**: Auth

---

### `GET /api/moderation/board-notices`
Moderator review queue.

**Auth**: Mod

---

### `POST /api/moderation/board-notices/:noticeId/decide`
Approve or reject notice.

**Auth**: Mod

---

### `GET /api/admin/board-notices/analytics`
Board notice analytics.

**Auth**: Admin

---

## 29. Authenticity Tags

### `POST /api/authenticity/tag`
Create or update an authenticity tag (board member or moderator).

**Auth**: Auth (board member or mod)

```json
// Request
{ "targetType": "CONTENT", "targetId": "content-uuid", "status": "VERIFIED", "notes": "..." }
```

---

### `GET /api/authenticity/tags/:targetType/:targetId`
Get authenticity tags for an entity.

**Auth**: Public

---

### `DELETE /api/authenticity/tags/:tagId`
Remove a tag.

**Auth**: Auth (tag author or admin)

---

### `GET /api/admin/authenticity/stats`
Tag statistics.

**Auth**: Admin

---

## 30. College Claims & Discovery

### `GET /api/colleges/search`
Search colleges.

**Auth**: Public | **Params**: `q`, `state`, `type`, `limit`, `offset`

---

### `GET /api/colleges/states`
List all states.

**Auth**: Public

---

### `GET /api/colleges/types`
List college types.

**Auth**: Public

---

### `GET /api/colleges/:collegeId`
College detail.

**Auth**: Public

---

### `GET /api/colleges/:collegeId/members`
College members.

**Auth**: Public | **Params**: `limit`, `offset`

---

### `POST /api/colleges/:collegeId/claim`
Submit a college claim (verify you belong to this college).

**Auth**: Auth

```json
// Request
{ "enrollmentId": "2021CS101", "proof": "..." }
```

---

### `GET /api/me/college-claims`
User's own claims.

**Auth**: Auth

---

### `DELETE /api/me/college-claims/:claimId`
Withdraw pending claim.

**Auth**: Auth

---

### `GET /api/admin/college-claims`
Admin review queue.

**Auth**: Admin

---

### `GET /api/admin/college-claims/:claimId`
Admin claim detail.

**Auth**: Admin

---

### `PATCH /api/admin/college-claims/:claimId/decide`
Admin approve/reject.

**Auth**: Admin

```json
// Request
{ "decision": "APPROVED", "reason": "Documents verified" }
```

---

### `PATCH /api/admin/college-claims/:claimId/flag-fraud`
Move claim to FRAUD_REVIEW.

**Auth**: Admin

---

### `GET /api/houses`
List houses (legacy, maps to tribes).

**Auth**: Public

---

### `GET /api/houses/leaderboard`
House leaderboard.

**Auth**: Public

---

### `GET /api/houses/:idOrSlug`
House detail.

**Auth**: Public

---

### `GET /api/houses/:idOrSlug/members`
House members.

**Auth**: Public

---

## 31. Governance

### `GET /api/governance/college/:collegeId/board`
Current college board.

**Auth**: Public

---

### `POST /api/governance/college/:collegeId/apply`
Apply for a board seat.

**Auth**: Auth

---

### `GET /api/governance/college/:collegeId/applications`
Pending board applications.

**Auth**: Auth

---

### `POST /api/governance/applications/:appId/vote`
Vote on a board application.

**Auth**: Auth

---

### `POST /api/governance/college/:collegeId/proposals`
Create a governance proposal.

**Auth**: Auth (board member)

---

### `GET /api/governance/college/:collegeId/proposals`
List proposals.

**Auth**: Public

---

### `POST /api/governance/proposals/:proposalId/vote`
Vote on a proposal.

**Auth**: Auth

---

### `POST /api/governance/college/:collegeId/seed-board`
Seed initial board (admin only).

**Auth**: Admin

---

## 32. Resources

### `POST /api/resources`
Create a resource (study materials, notes, etc.).

**Auth**: Auth

```json
// Request
{
  "title": "Data Structures Notes",
  "description": "Complete DS notes for semester 3",
  "category": "NOTES",
  "tags": ["dsa", "algorithms"],
  "collegeId": "...",
  "mediaIds": ["media-uuid"]
}
```

---

### `GET /api/resources/search`
Faceted search + text search (Redis-cached).

**Auth**: Optional | **Params**: `q`, `category`, `tags`, `collegeId`, `limit`, `offset`

---

### `GET /api/resources/:resourceId`
Resource detail (cached).

**Auth**: Optional

---

### `PATCH /api/resources/:resourceId`
Update resource metadata (owner only).

**Auth**: Auth (owner)

---

### `DELETE /api/resources/:resourceId`
Soft remove (owner or mod).

**Auth**: Auth (owner or mod)

---

### `POST /api/resources/:resourceId/report`
Report resource (auto-hold at 3+ reports).

**Auth**: Auth

---

### `POST /api/resources/:resourceId/vote`
Upvote/downvote (helpfulness).

**Auth**: Auth

```json
// Request
{ "direction": "UP" }
```

---

### `DELETE /api/resources/:resourceId/vote`
Remove vote.

**Auth**: Auth

---

### `POST /api/resources/:resourceId/download`
Track download (auth required).

**Auth**: Auth

---

### `GET /api/me/resources`
My uploaded resources.

**Auth**: Auth

---

### Admin Resource Endpoints:
- `GET /api/admin/resources` — Review queue
- `PATCH /api/admin/resources/:resourceId/moderate` — Approve/Hold/Remove
- `POST /api/admin/resources/:resourceId/recompute-counters` — Recompute from source
- `POST /api/admin/resources/reconcile` — Bulk reconciliation

---

## 33. Content Distribution (Admin)

### `POST /api/admin/distribution/evaluate`
Batch evaluate all Stage 0/1 content for promotion.

**Auth**: Admin

---

### `POST /api/admin/distribution/evaluate/:contentId`
Single content evaluation.

**Auth**: Admin

---

### `GET /api/admin/distribution/config`
View distribution rules.

**Auth**: Admin

---

### `POST /api/admin/distribution/kill-switch`
Toggle auto-evaluation on/off.

**Auth**: Admin

---

### `GET /api/admin/distribution/inspect/:contentId`
View distribution detail for a content item.

**Auth**: Admin

---

### `POST /api/admin/distribution/override`
Manual distribution override (survives auto-eval).

**Auth**: Admin

```json
// Request
{ "contentId": "...", "stage": 2, "reason": "Editor's pick" }
```

---

### `DELETE /api/admin/distribution/override/:contentId`
Remove override (re-enable auto-eval).

**Auth**: Admin

---

## 34. Reports, Moderation & Appeals

### `POST /api/reports`
Submit a report.

**Auth**: Auth

```json
// Request
{ "targetId": "...", "targetType": "USER", "reason": "HARASSMENT", "details": "..." }
```

---

### `GET /api/moderation/queue`
Moderation review queue.

**Auth**: Mod

---

### `POST /api/moderation/:contentId/action`
Take moderation action on content.

**Auth**: Mod

```json
// Request
{ "action": "REMOVE", "reason": "Violates community guidelines" }
```

---

### `GET /api/moderation/config`
Moderation system configuration.

**Auth**: Mod

---

### `POST /api/moderation/check`
Run content through moderation check.

**Auth**: Mod

---

### `POST /api/appeals`
Submit an appeal against moderation action.

**Auth**: Auth

```json
// Request
{ "contentId": "...", "reason": "This was falsely flagged" }
```

---

### `GET /api/appeals`
User's own appeals.

**Auth**: Auth

---

### `PATCH /api/appeals/:appealId/decide`
Moderator decides on appeal.

**Auth**: Mod

```json
// Request
{ "decision": "UPHELD", "reason": "Content reinstated" }
```

---

### `GET /api/legal/consent`
Get current consent document.

**Auth**: Auth

---

### `POST /api/legal/accept`
Accept legal/consent terms.

**Auth**: Auth

---

### `POST /api/grievances`
Submit a grievance.

**Auth**: Auth

---

### `GET /api/grievances`
User's own grievances.

**Auth**: Auth

---

## 35. Content Quality Scoring

### `POST /api/quality/score`
Score a single post's quality.

**Auth**: Auth

```json
// Request
{ "contentId": "content-uuid" }

// Response 200
{
  "contentId": "...",
  "score": 78.5,
  "breakdown": {
    "captionQuality": 22, "mediaRichness": 20, "hashtagRelevance": 15,
    "engagementSignals": 12, "authorReputation": 9.5
  },
  "tier": "HIGH"
}
```

---

### `POST /api/quality/batch`
Batch score unscored content (admin only).

**Auth**: Admin

---

### `GET /api/quality/dashboard`
Quality overview dashboard (admin).

**Auth**: Admin

---

### `GET /api/quality/check/:contentId`
Check quality score for a specific post.

**Auth**: Auth

---

## 36. Content Recommendations

### `GET /api/recommendations/posts`
"Suggested Posts" personalized for you.

**Auth**: Auth | **Params**: `limit`

```json
// Response 200
{
  "items": [ /* enriched posts with recommendation reason */ ],
  "algorithm": "collaborative_filtering_v1",
  "signals": ["liked_authors", "interests", "tribe_affinity", "engagement_pattern"]
}
```

---

### `GET /api/recommendations/reels`
"Reels You May Like."

**Auth**: Auth | **Params**: `limit`

---

### `GET /api/recommendations/creators`
"Creators for you" suggestions.

**Auth**: Auth | **Params**: `limit`

---

## 37. User Activity Status

### `POST /api/activity/heartbeat`
Update "last seen" timestamp.

**Auth**: Auth

```json
// Response 200
{ "lastSeen": "2025-01-15T10:30:00.000Z", "status": "ONLINE" }
```

---

### `GET /api/activity/status/:userId`
Get a user's activity status.

**Auth**: Auth

```json
// Response 200
{
  "userId": "...",
  "status": "RECENTLY_ACTIVE",
  "lastSeen": "2025-01-15T10:25:00.000Z",
  "isOnline": false
}
```

---

### `GET /api/activity/friends`
Activity status of all followed users.

**Auth**: Auth

```json
// Response 200
{
  "online": [ { "user": { /* ... */ }, "lastSeen": "..." } ],
  "recentlyActive": [ /* ... */ ],
  "offline": [ /* ... */ ]
}
```

---

### `PUT /api/activity/settings`
Toggle activity status visibility.

**Auth**: Auth

```json
// Request
{ "showActivityStatus": false }
```

---

## 38. Smart Suggestions

### `GET /api/suggestions/people`
"People you may know" (mutual followers, same college/tribe, shared interests).

**Auth**: Auth | **Params**: `limit`

```json
// Response 200
{
  "items": [
    {
      "user": { /* sanitized user */ },
      "reasons": ["mutual_followers", "same_college"],
      "mutualCount": 5,
      "score": 87.5
    }
  ]
}
```

---

### `GET /api/suggestions/trending`
"Trending in your college."

**Auth**: Auth | **Params**: `limit`

---

### `GET /api/suggestions/tribes`
"Tribes for you" suggestions.

**Auth**: Auth | **Params**: `limit`

---

### `GET /api/suggestions/users`
Alternative user suggestion endpoint (in discovery handler).

**Auth**: Optional | **Params**: `limit`

---

## 39. Blocks & Mutes

### `POST /api/me/blocks/:userId`
Block a user (bidirectional hide).

**Auth**: Auth

```json
// Response 200
{ "message": "User blocked" }
```

---

### `DELETE /api/me/blocks/:userId`
Unblock a user.

**Auth**: Auth

```json
// Response 200
{ "message": "User unblocked" }
```

---

### `GET /api/me/blocks`
List blocked users.

**Auth**: Auth

```json
// Response 200
{ "items": [ { "user": { /* ... */ }, "blockedAt": "..." } ], "count": 3 }
```

---

### `POST /api/me/story-mutes/:userId`
Mute a user's stories (still follow, but hide their stories).

**Auth**: Auth

---

### `DELETE /api/me/story-mutes/:userId`
Unmute a user's stories.

**Auth**: Auth

---

### `GET /api/me/story-mutes`
List muted users.

**Auth**: Auth

---

## 40. Admin & Ops

### `POST /api/admin/colleges/seed`
Seed college database (admin only).

**Auth**: Admin

---

### `GET /api/admin/stats`
Platform-wide statistics.

**Auth**: Admin

```json
// Response 200
{
  "users": 125000, "posts": 450000,
  "activeSessions": 12000,
  "openReports": 45, "openGrievances": 12
}
```

---

### `GET /api/admin/abuse-dashboard`
Abuse & anti-gaming admin overview.

**Auth**: Admin

---

### `GET /api/admin/abuse-log`
Detailed abuse audit log entries.

**Auth**: Admin

---

### Admin Reel Endpoints:
- `GET /api/admin/reels` — Moderation queue
- `PATCH /api/admin/reels/:reelId/moderate` — Moderate reel
- `GET /api/admin/reels/analytics` — Platform reel analytics
- `POST /api/admin/reels/:reelId/recompute-counters` — Recompute counters

### Admin Story Endpoints:
- `GET /api/admin/stories` — Moderation queue
- `GET /api/admin/stories/analytics` — Story analytics
- `PATCH /api/admin/stories/:storyId/moderate` — Moderate story
- `POST /api/admin/stories/:storyId/recompute-counters` — Recompute counters
- `POST /api/admin/stories/cleanup` — Trigger story expiry cleanup
- `POST /api/admin/stories/bulk-moderate` — Batch moderate stories

### Admin Media Endpoints:
- `POST /api/admin/media/cleanup` — Trigger orphan cleanup
- `GET /api/admin/media/metrics` — Media lifecycle metrics
- `POST /api/admin/media/batch-seed` — Batch seed media records
- `POST /api/admin/media/backfill-legacy` — Backfill legacy records

### Health & Observability:
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/api/healthz` | Public | Liveness probe |
| `GET` | `/api/readyz` | Public | Readiness probe (checks DB) |
| `GET` | `/api/` | Public | API root info |
| `GET` | `/api/ops/health` | Admin | Deep health check |
| `GET` | `/api/ops/metrics` | Admin | Business + system metrics |
| `GET` | `/api/ops/slis` | Admin | Service Level Indicators |
| `GET` | `/api/ops/backup-check` | Admin | DB backup readiness check |
| `GET` | `/api/cache/stats` | Admin | Redis cache statistics |

---

## 41. Frontend Integration Notes

### Authentication Flow
1. Register or login → receive `accessToken` + `refreshToken`
2. Store `accessToken` (short-lived, ~15 min) and `refreshToken` (long-lived, ~7 days)
3. Include `Authorization: Bearer <accessToken>` on all requests
4. When `401` received, call `POST /api/auth/refresh` with `refreshToken`
5. If refresh fails with `REFRESH_TOKEN_REUSED`, force full logout (security breach)

### Token Storage
- `accessToken`: Memory or sessionStorage (never localStorage)
- `refreshToken`: httpOnly cookie (ideal) or secure storage

### Media Upload Flow
1. `POST /api/media/upload-init` → get signed URL + mediaId
2. Upload file directly to Supabase using signed URL
3. `POST /api/media/upload-complete` with mediaId → finalize
4. Use `mediaId` in content creation endpoints

### Pagination Pattern
- Use **cursor-based** pagination for feeds (infinite scroll)
- Use **offset-based** pagination for member lists (page numbers)
- Check `pagination.hasMore` before showing "Load More"

### Real-Time (SSE)
- Story events: `GET /api/stories/events/stream?token=<accessToken>`
- Contest live feed: `GET /api/tribe-contests/live-feed`
- Contest scoreboard: `GET /api/tribe-contests/:id/live`
- Season standings: `GET /api/tribe-contests/seasons/:id/live-standings`

### Enriched Post Object
Every post returned from feeds contains:
```json
{
  "id": "...",
  "kind": "POST",
  "authorId": "...",
  "author": { "id": "...", "displayName": "...", "username": "...", "avatarMediaId": "..." },
  "caption": "...",
  "hashtags": ["tag1"],
  "media": [{ "id": "...", "url": "...", "type": "IMAGE" }],
  "visibility": "PUBLIC",
  "likeCount": 42,
  "commentCount": 5,
  "saveCount": 3,
  "shareCount": 1,
  "viewCount": 1200,
  "viewerHasLiked": false,
  "viewerHasDisliked": false,
  "viewerHasSaved": false,
  "postSubType": "STANDARD",
  "poll": null,
  "thread": null,
  "carousel": null,
  "isDraft": false,
  "createdAt": "...",
  "updatedAt": "..."
}
```

### Error Handling Checklist
| Status | Action |
|--------|--------|
| `400` | Show validation error to user |
| `401` | Try token refresh, then redirect to login |
| `403` | Show "access denied" or feature restricted |
| `404` | Show "not found" |
| `409` | Show "already exists" or "duplicate" |
| `410` | Content expired (stories) |
| `422` | Content rejected by moderation |
| `429` | Show rate limit with `Retry-After` timer |
| `500` | Show generic error, log `x-request-id` |

### Smart Feed Algorithm
The home/public feed uses a multi-signal ranking algorithm on the first page:
- **Recency Decay**: Exponential decay with 6-hour half-life
- **Engagement Velocity**: Weighted likes (1x), comments (3x), saves (5x), shares (2x)
- **Author Affinity**: Based on viewer's interaction history with the author
- **Content Type Preference**: Adapts to what you engage with most
- **Virality Detection**: Boosts content with above-average engagement rate
- **Diversity Penalty**: Prevents same author from dominating
- **Unseen Boost**: Prioritizes content you haven't viewed

Paginated pages (cursor-based) fall back to chronological ordering.

### Test Credentials
- Phone: `7777099001` / PIN: `1234`
- Phone: `7777099002` / PIN: `1234`

---

*Generated for Tribe API v3.0.0 — 435+ endpoints across 41 sections*
