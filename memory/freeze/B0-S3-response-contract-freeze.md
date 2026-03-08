# B0-S3 — Response Contract Freeze

**Status**: FROZEN  
**Freeze Date**: 2026-02-XX  
**Rule**: Every response shape, field name, nullability, and envelope is locked. Android parses these with zero guesswork.

---

## 1. Global Response Standards

### 1.1 Success Envelope

All successful responses wrap data in a top-level key. The key name varies by entity:

```
Single entity:  { "user": {...} }
                { "post": {...} }
                { "event": {...} }
                { "contest": {...} }

List (cursor):  { "items": [...], "nextCursor": "ISO_date | id | null" }
List (page):    { "items": [...], "page": 1, "limit": 20, "total": 200 }
List (named):   { "users": [...], "total": 42 }
                { "events": [...], "nextCursor": "..." }
                { "notices": [...] }
```

### 1.2 Pagination Standards

**TWO CANONICAL PATTERNS. No mixing within a single endpoint.**

#### Pattern A: Cursor-Based (preferred for infinite scroll)
```json
{
  "items": [...],
  "nextCursor": "2025-01-15T12:00:00.000Z"
}
```
- `nextCursor` = ISO date string OR entity id. `null` when no more pages.
- Client sends `?cursor={nextCursor}&limit=20`

**Used by**: feeds, stories feed, comments, salute history, events search, resources search, story replies, reel comments, my events, my resources

#### Pattern B: Page-Based (for contests, admin lists)
```json
{
  "items": [...],
  "page": 1,
  "limit": 20,
  "total": 200
}
```
- Client sends `?page=1&limit=20`
- `total` is authoritative count

**Used by**: tribe-contests list, contest entries, admin contest list, admin resources

#### Pattern C: Offset-Based (for follower/following lists)
```json
{
  "users": [...],
  "total": 42
}
```
- Client sends `?limit=20&offset=0`

**Used by**: followers, following, college members, tribe members, event attendees

### 1.3 Error Response (universal)
```json
{
  "error": "Human-readable message",
  "code": "ERROR_CODE"
}
```
HTTP status is always set. `code` is a machine-parseable constant.

### 1.4 Timestamp Format
All timestamps are **ISO 8601 strings** when returned in JSON: `"2025-01-15T12:00:00.000Z"`

### 1.5 ID Format
All entity IDs are **UUID v4 strings**: `"a1b2c3d4-e5f6-7890-abcd-ef1234567890"`  
Exception: MongoDB `_id` is NEVER exposed.

### 1.6 Null vs Missing
- A field is present with `null` if the concept applies but has no value yet (e.g., `collegeId: null`)
- A field is absent/omitted only if it structurally doesn't apply to the response variant
- Android should treat missing and `null` identically for optional fields

---

## 2. Entity Contracts

### 2.1 User Object (sanitized)

Returned from: `/auth/me`, `/auth/register`, `/auth/login`, `/users/{id}`, embedded in posts/comments/etc.

```json
{
  "id": "uuid",
  "phone": "9876543210",
  "displayName": "Rahul",
  "username": "rahul.dev | null",
  "bio": "string | null",
  "avatarMediaId": "uuid | null",
  "ageStatus": "ADULT | CHILD | UNKNOWN",
  "birthYear": 2002,
  "role": "USER | MODERATOR | ADMIN | SUPER_ADMIN",
  "collegeId": "uuid | null",
  "collegeName": "string | null",
  "collegeVerified": true,
  "houseId": "uuid | null",
  "houseSlug": "string | null",
  "houseName": "string | null",
  "isBanned": false,
  "isVerified": false,
  "suspendedUntil": "ISO date | null",
  "strikeCount": 0,
  "consentVersion": "string | null",
  "consentAcceptedAt": "ISO date | null",
  "personalizedFeed": true,
  "targetedAds": true,
  "followersCount": 42,
  "followingCount": 15,
  "postsCount": 7,
  "onboardingComplete": true,
  "onboardingStep": "DONE | AGE | COLLEGE | CONSENT",
  "lastActiveAt": "ISO date",
  "createdAt": "ISO date",
  "updatedAt": "ISO date"
}
```

**NEVER PRESENT**: `_id`, `pinHash`, `pinSalt`

### 2.2 Post / Content Item Object

```json
{
  "id": "uuid",
  "kind": "POST | REEL | STORY",
  "authorId": "uuid",
  "caption": "string | null",
  "media": [{ "id": "uuid", "url": "string", "type": "IMAGE | VIDEO", "width": 1080, "height": 1920 }],
  "mediaIds": ["uuid"],
  "visibility": "PUBLIC | LIMITED | SHADOW_LIMITED | HELD_FOR_REVIEW | REMOVED",
  "distributionStage": 0,
  "likeCount": 10,
  "dislikeCount": 2,
  "commentCount": 5,
  "viewCount": 100,
  "syntheticDeclaration": false,
  "moderationStatus": "CLEAN | FLAGGED | HELD | REMOVED",
  "collegeId": "uuid | null",
  "houseId": "uuid | null",
  "createdAt": "ISO date",
  "updatedAt": "ISO date",
  "expiresAt": "ISO date | null",
  "author": { /* sanitized user object */ },
  "viewerHasLiked": true,
  "viewerHasDisliked": false,
  "viewerHasSaved": false
}
```

**Notes**: `author`, `viewerHasLiked`, `viewerHasDisliked`, `viewerHasSaved` are enrichment fields — present on detail/feed views, not on raw writes.

### 2.3 Comment Object

```json
{
  "id": "uuid",
  "contentId": "uuid",
  "authorId": "uuid",
  "body": "string",
  "text": "string",
  "parentId": "uuid | null",
  "moderationStatus": "CLEAN | FLAGGED | HELD | REMOVED",
  "createdAt": "ISO date",
  "author": { /* sanitized user object */ }
}
```

### 2.4 Story Object

```json
{
  "id": "uuid",
  "authorId": "uuid",
  "type": "IMAGE | VIDEO | TEXT",
  "status": "ACTIVE | EXPIRED | DELETED | MODERATED",
  "caption": "string | null",
  "media": [{ "id": "uuid", "url": "string", "type": "IMAGE | VIDEO" }],
  "mediaIds": ["uuid"],
  "privacy": "EVERYONE | FOLLOWERS | CLOSE_FRIENDS",
  "replyPrivacy": "EVERYONE | FOLLOWERS | CLOSE_FRIENDS | OFF",
  "stickers": [{
    "id": "uuid",
    "type": "POLL | QUESTION | QUIZ | EMOJI_SLIDER | MENTION | LOCATION | HASHTAG | LINK | COUNTDOWN | MUSIC",
    "question": "string | null",
    "options": ["string"] | null,
    "correctIndex": 0 | null,
    "emoji": "string | null"
  }],
  "backgroundType": "SOLID | GRADIENT | IMAGE | null",
  "backgroundColor": "#hex | null",
  "gradientColors": ["#hex"] | null,
  "textFont": "string | null",
  "textAlign": "string | null",
  "viewCount": 5,
  "reactionCount": 2,
  "replyCount": 1,
  "collegeId": "uuid | null",
  "expiresAt": "ISO date",
  "createdAt": "ISO date",
  "updatedAt": "ISO date",
  "author": { /* sanitized user */ },
  "viewerReaction": "emoji | null",
  "viewerStickerResponses": {},
  "isViewerCloseFriend": false
}
```

### 2.5 Story Feed Rail Response

```json
{
  "storyRail": [
    {
      "author": { /* sanitized user */ },
      "stories": [{ /* story objects */ }],
      "latestAt": "ISO date",
      "seenAll": false,
      "seenStoryIds": ["uuid"]
    }
  ]
}
```
**Ordering**: Own stories first, then by `latestAt` descending.

### 2.6 Reel Object

```json
{
  "id": "uuid",
  "creatorId": "uuid",
  "status": "DRAFT | PROCESSING | PUBLISHED | ARCHIVED | REMOVED | FAILED",
  "moderationStatus": "PENDING | CLEAN | FLAGGED | REMOVED",
  "mediaStatus": "PENDING | PROCESSING | READY | FAILED",
  "visibility": "PUBLIC | FOLLOWERS | PRIVATE",
  "caption": "string | null",
  "hashtags": ["string"],
  "mentions": ["uuid"],
  "mediaId": "uuid",
  "mediaUrl": "string | null",
  "thumbnailUrl": "string | null",
  "duration": 15000,
  "width": 1080,
  "height": 1920,
  "audioMeta": { "audioId": "uuid | null", "title": "string | null" } | null,
  "remixOf": { "reelId": "uuid", "creatorId": "uuid" } | null,
  "seriesId": "uuid | null",
  "seriesOrder": 0,
  "isDraft": false,
  "pinnedToProfile": false,
  "likeCount": 50,
  "commentCount": 10,
  "saveCount": 5,
  "shareCount": 3,
  "viewCount": 1000,
  "avgWatchPercent": 72.5,
  "score": 85.3,
  "collegeId": "uuid | null",
  "publishedAt": "ISO date | null",
  "createdAt": "ISO date",
  "updatedAt": "ISO date",
  "creator": { /* sanitized user */ },
  "viewerLiked": false,
  "viewerSaved": false
}
```

### 2.7 Resource Object

```json
{
  "id": "uuid",
  "kind": "NOTE | PYQ | ASSIGNMENT | SYLLABUS | LAB_FILE",
  "collegeId": "uuid",
  "uploaderId": "uuid",
  "title": "string",
  "description": "string | null",
  "branch": "string | null",
  "subject": "string | null",
  "semester": 3,
  "year": 2024,
  "fileAssetId": "uuid | null",
  "status": "PUBLIC | HELD | UNDER_REVIEW | REMOVED",
  "voteScore": 15,
  "trustedVoteScore": 12,
  "voteCount": 20,
  "downloadCount": 100,
  "reportCount": 0,
  "moderatedBy": "uuid | null",
  "moderatedAt": "ISO date | null",
  "createdAt": "ISO date",
  "updatedAt": "ISO date",
  "uploader": { /* sanitized user */ },
  "viewerVote": "UP | DOWN | null"
}
```

### 2.8 Event Object

```json
{
  "id": "uuid",
  "collegeId": "uuid | null",
  "createdByUserId": "uuid",
  "title": "string",
  "description": "string | null",
  "category": "ACADEMIC | CULTURAL | SPORTS | SOCIAL | WORKSHOP | PLACEMENT | OTHER",
  "visibility": "PUBLIC | COLLEGE | PRIVATE",
  "status": "PUBLIC | CANCELLED | ARCHIVED | HELD",
  "startAt": "ISO date",
  "endAt": "ISO date | null",
  "locationText": "string | null",
  "locationUrl": "string | null",
  "organizerText": "string | null",
  "capacity": 200 | null,
  "isDraft": false,
  "coverImageUrl": "string | null",
  "tags": ["string"],
  "rsvpCount": { "going": 50, "interested": 30 },
  "reportCount": 0,
  "authenticityTags": [{ /* authenticity tag objects */ }],
  "createdAt": "ISO date",
  "updatedAt": "ISO date",
  "creator": { /* sanitized user */ },
  "viewerRsvp": "GOING | INTERESTED | null",
  "viewerReminder": true | null
}
```

### 2.9 Notice Object

```json
{
  "id": "uuid",
  "collegeId": "uuid",
  "createdByUserId": "uuid",
  "title": "string",
  "body": "string",
  "category": "ACADEMIC | ADMINISTRATIVE | EXAMINATION | PLACEMENT | CULTURAL | GENERAL",
  "priority": "URGENT | IMPORTANT | NORMAL | FYI",
  "status": "PENDING_REVIEW | PUBLISHED | REJECTED",
  "isDraft": false,
  "pinnedToBoard": false,
  "attachments": [{ "name": "string", "url": "string", "type": "string" }],
  "acknowledgmentCount": 10,
  "publishedAt": "ISO date | null",
  "expiresAt": "ISO date | null",
  "createdAt": "ISO date",
  "updatedAt": "ISO date",
  "creator": { /* sanitized user */ },
  "acknowledgedByMe": false
}
```

### 2.10 Tribe Object

```json
{
  "id": "uuid",
  "tribeCode": "SOMNATH",
  "tribeName": "Somnath Tribe",
  "heroName": "Major Somnath Sharma",
  "quote": "Stand first. Stand firm. Stand for all.",
  "animalIcon": "lion",
  "primaryColor": "#B71C1C",
  "secondaryColor": "#D32F2F",
  "sortOrder": 1,
  "isActive": true,
  "membersCount": 500,
  "totalSalutes": 15000,
  "createdAt": "ISO date"
}
```

### 2.11 Tribe Membership (on `/me/tribe`)

```json
{
  "tribe": { /* tribe object */ },
  "membership": {
    "userId": "uuid",
    "tribeId": "uuid",
    "tribeCode": "SOMNATH",
    "isPrimary": true,
    "status": "active",
    "assignedAt": "ISO date",
    "assignmentMethod": "deterministic_hash | admin_assign | migration"
  }
}
```

### 2.12 Season Object

```json
{
  "id": "uuid",
  "name": "Spring 2025",
  "year": 2025,
  "status": "active | completed | upcoming",
  "startAt": "ISO date | null",
  "endAt": "ISO date | null",
  "createdAt": "ISO date"
}
```

### 2.13 Contest Object

```json
{
  "id": "uuid",
  "seasonId": "uuid",
  "contestCode": "CONTEST_XXXXX_ABCD1234",
  "contestName": "Best Reel Challenge",
  "contestType": "reel_creative | tribe_battle | participation | judge | hybrid | seasonal",
  "contestFormat": "individual | team | tribe_vs_tribe",
  "status": "DRAFT | PUBLISHED | ENTRY_OPEN | ENTRY_CLOSED | EVALUATING | LOCKED | RESOLVED | CANCELLED",
  "description": "string | null",
  "rulesText": "string | null",
  "entryMode": "self_submit | admin_nominate | auto_detect",
  "audienceScope": "all_users | tribe_only | college_only",
  "eligibilityRules": { "mustHaveTribe": true },
  "maxEntriesPerUser": 1,
  "maxEntriesPerTribe": 50,
  "entryStartAt": "ISO date | null",
  "entryEndAt": "ISO date | null",
  "contestStartAt": "ISO date | null",
  "contestEndAt": "ISO date | null",
  "scoringModelId": "scoring_reel_hybrid_v1",
  "tieBreakPolicy": "string",
  "visibility": "public | tribe_only | admin_only",
  "saluteDistribution": {
    "rank_1": 1000,
    "rank_2": 600,
    "rank_3": 300,
    "finalist": 100,
    "participation": 25
  },
  "votingEnabled": true,
  "selfVoteBlocked": true,
  "maxVotesPerUser": 5,
  "winnerId": "uuid | null",
  "runnerUpId": "uuid | null",
  "resolvedAt": "ISO date | null",
  "resolvedBy": "uuid | null",
  "createdBy": "uuid",
  "createdAt": "ISO date",
  "updatedAt": "ISO date"
}
```

### 2.14 Contest Entry Object

```json
{
  "id": "uuid",
  "contestId": "uuid",
  "userId": "uuid",
  "tribeId": "uuid",
  "entryType": "reel | post | manual | tribe_team | live_event",
  "contentId": "uuid | null",
  "submissionData": {},
  "submissionStatus": "submitted | validated | locked | withdrawn | disqualified",
  "submittedAt": "ISO date",
  "validatedAt": "ISO date | null",
  "updatedAt": "ISO date"
}
```

### 2.15 Contest Vote Object

```json
{
  "id": "uuid",
  "contestId": "uuid",
  "entryId": "uuid",
  "voterUserId": "uuid",
  "voterTribeId": "uuid",
  "voteType": "upvote | support",
  "weight": 1,
  "createdAt": "ISO date"
}
```

### 2.16 Contest Score Object

```json
{
  "contestId": "uuid",
  "entryId": "uuid",
  "userId": "uuid",
  "tribeId": "uuid",
  "judgeScore": 8.5,
  "engagementScore": 72.3,
  "completionScore": 90.0,
  "finalScore": 85.0,
  "rank": 1,
  "scoringModelId": "scoring_reel_hybrid_v1",
  "breakdown": {
    "judge_weight": 0.35,
    "engagement_weight": 0.35,
    "completion_weight": 0.30
  },
  "lastComputedAt": "ISO date"
}
```

### 2.17 Contest Result Object

```json
{
  "id": "uuid",
  "contestId": "uuid",
  "seasonId": "uuid",
  "idempotencyKey": "string | null",
  "winnerType": "entry | tribe",
  "topPositions": [
    { "rank": 1, "tribeId": "uuid", "userId": "uuid | null", "entryId": "uuid | null", "finalScore": 85.0 }
  ],
  "salutesDistributed": [
    { "tribeId": "uuid", "amount": 1000, "rank": 1 }
  ],
  "totalSalutesAwarded": 2000,
  "resolutionMode": "automatic | manual",
  "notes": "string | null",
  "resolvedBy": "uuid",
  "resolvedAt": "ISO date"
}
```

### 2.18 Salute Ledger Entry

```json
{
  "id": "uuid",
  "tribeId": "uuid",
  "seasonId": "uuid | null",
  "contestId": "uuid | null",
  "amount": 1000,
  "reason": "CONTEST_WIN | CONTEST_RUNNER_UP | CONTEST_FINALIST | CONTEST_PARTICIPATION | ADMIN_AWARD | ADMIN_ADJUST | PENALTY | REVERSAL",
  "notes": "string | null",
  "grantedBy": "uuid",
  "reversalOf": "uuid | null",
  "createdAt": "ISO date"
}
```

### 2.19 Tribe Standing Object

```json
{
  "seasonId": "uuid",
  "tribeId": "uuid",
  "totalSalutes": 15000,
  "contestsWon": 3,
  "contestsParticipated": 7,
  "rank": 1,
  "tribe": { /* tribe summary: id, tribeName, tribeCode, primaryColor, animalIcon */ }
}
```

### 2.20 Notification Object

```json
{
  "id": "uuid",
  "userId": "uuid",
  "type": "FOLLOW | LIKE | COMMENT | REPLY | MENTION | MODERATION | SYSTEM",
  "actorId": "uuid | null",
  "targetType": "POST | REEL | STORY | EVENT | CONTEST | USER",
  "targetId": "uuid | null",
  "message": "string",
  "read": false,
  "createdAt": "ISO date"
}
```

### 2.21 Media Asset Object

```json
{
  "id": "uuid",
  "url": "string",
  "type": "IMAGE | VIDEO",
  "mimeType": "image/jpeg",
  "size": 245000,
  "width": 1080,
  "height": 1920,
  "duration": 15,
  "storageType": "OBJECT_STORAGE | BASE64",
  "ownerId": "uuid",
  "createdAt": "ISO date"
}
```

### 2.22 College Claim Object

```json
{
  "id": "uuid",
  "userId": "uuid",
  "collegeId": "uuid",
  "claimType": "STUDENT_ID | EMAIL | DOCUMENT | ENROLLMENT_NUMBER",
  "evidence": "string",
  "status": "PENDING | APPROVED | REJECTED | WITHDRAWN | FRAUD_REVIEW",
  "reviewedBy": "uuid | null",
  "reviewedAt": "ISO date | null",
  "rejectionCooldownUntil": "ISO date | null",
  "reasonCodes": ["string"],
  "notes": "string | null",
  "createdAt": "ISO date",
  "updatedAt": "ISO date"
}
```

### 2.23 Authenticity Tag Object

```json
{
  "id": "uuid",
  "targetType": "RESOURCE | EVENT",
  "targetId": "uuid",
  "tag": "VERIFIED | USEFUL | OUTDATED | MISLEADING",
  "actorType": "MODERATOR | BOARD",
  "actorId": "uuid",
  "createdAt": "ISO date"
}
```

### 2.24 Highlight Object

```json
{
  "id": "uuid",
  "userId": "uuid",
  "name": "string",
  "coverStoryId": "uuid | null",
  "coverUrl": "string | null",
  "storyCount": 3,
  "stories": [{ /* story objects */ }],
  "createdAt": "ISO date",
  "updatedAt": "ISO date"
}
```

### 2.25 Appeal Object

```json
{
  "id": "uuid",
  "userId": "uuid",
  "targetId": "uuid",
  "targetType": "POST | COMMENT | REEL | STORY",
  "status": "PENDING | REVIEWING | APPROVED | DENIED | MORE_INFO_REQUESTED",
  "reason": "string",
  "decision": {
    "action": "APPROVE | REJECT | REQUEST_MORE_INFO",
    "reasonCodes": ["string"],
    "notes": "string | null"
  } | null,
  "decidedBy": "uuid | null",
  "decidedAt": "ISO date | null",
  "createdAt": "ISO date"
}
```

### 2.26 Grievance Object

```json
{
  "id": "uuid",
  "userId": "uuid",
  "subject": "string",
  "description": "string",
  "category": "string",
  "status": "OPEN | IN_PROGRESS | RESOLVED | CLOSED",
  "dueAt": "ISO date",
  "createdAt": "ISO date"
}
```

---

## 3. Enrichment Rules

Enrichment = extra fields added when returning data in context (feeds, details).

| Entity | Enrichment Fields | When Present |
|--------|------------------|--------------|
| Post | `author`, `viewerHasLiked`, `viewerHasDisliked`, `viewerHasSaved` | Feed + Detail |
| Story | `author`, `viewerReaction`, `viewerStickerResponses`, `isViewerCloseFriend` | View + Feed |
| Reel | `creator`, `viewerLiked`, `viewerSaved` | Feed + Detail |
| Comment | `author` | Always |
| Event | `creator`, `viewerRsvp`, `viewerReminder`, `authenticityTags` | Detail |
| Resource | `uploader`, `viewerVote` | Detail + Search |
| Contest | `seasonName`, `seasonYear` | List |
| Contest Detail | `season`, `rules`, `entryCount`, `tribeStrip`, `myEntry`, `result`, `scoringModel` | Detail only |

---

## PASS Gate Verification

- [x] Every entity has a frozen JSON shape
- [x] Every field has explicit nullability documented
- [x] Pagination patterns are consistent per endpoint type
- [x] Error format is universal
- [x] Timestamps are ISO 8601
- [x] IDs are UUID v4
- [x] No `_id` exposure
- [x] Enrichment rules clear
- [x] Android can generate Kotlin data classes from this document

**B0-S3 STATUS: FROZEN**
