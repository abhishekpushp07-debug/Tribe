# Tribe — Data Models & Database Schema Reference

> **Database**: MongoDB | **Collections**: 95 | **Version**: 3.0.0
> All IDs are UUIDs (v4 string), not MongoDB ObjectIds. `_id` is excluded from all API responses.

---

## Table of Contents
1. [Core User System](#1-core-user-system)
2. [Authentication & Sessions](#2-authentication--sessions)
3. [Content System](#3-content-system)
4. [Social Graph](#4-social-graph)
5. [Reactions & Engagement](#5-reactions--engagement)
6. [Comments](#6-comments)
7. [Stories](#7-stories)
8. [Reels](#8-reels)
9. [Pages](#9-pages)
10. [Events](#10-events)
11. [Tribes](#11-tribes)
12. [Tribe Contests](#12-tribe-contests)
13. [Search & Discovery](#13-search--discovery)
14. [Notifications](#14-notifications)
15. [Moderation & Reports](#15-moderation--reports)
16. [Media & Transcoding](#16-media--transcoding)
17. [Resources](#17-resources)
18. [Governance](#18-governance)
19. [Board Notices & Authenticity](#19-board-notices--authenticity)
20. [Analytics](#20-analytics)
21. [Anti-Abuse](#21-anti-abuse)
22. [Collection Index Summary](#22-collection-index-summary)

---

## 1. Core User System

### `users`
Primary user account.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string (UUID) | Primary key |
| `phone` | string | 10-digit phone (unique) |
| `pinHash` | string | PBKDF2 hashed PIN |
| `pinSalt` | string | Random salt |
| `displayName` | string | 2-50 chars |
| `username` | string | 3-30 chars, unique, `[a-z0-9._]` |
| `bio` | string | Max 500 chars |
| `avatarMediaId` | string | Media asset reference |
| `birthYear` | int | Birth year |
| `ageStatus` | enum | `UNKNOWN`, `ADULT`, `CHILD` |
| `role` | enum | `USER`, `MODERATOR`, `ADMIN`, `SUPER_ADMIN` |
| `collegeId` | string | Linked college |
| `collegeName` | string | Denormalized name |
| `tribeId` | string | Assigned tribe (permanent) |
| `tribeCode` | string | Tribe code (e.g., `BATRA`) |
| `tribeName` | string | Denormalized tribe name |
| `houseId` | string | Legacy house (deprecated) |
| `houseSlug` | string | Legacy house slug |
| `followersCount` | int | Denormalized counter |
| `followingCount` | int | Denormalized counter |
| `postsCount` | int | Denormalized counter |
| `onboardingComplete` | bool | Onboarding finished |
| `onboardingStep` | string | `AGE`, `COLLEGE`, `PROFILE`, `DONE` |
| `interests` | string[] | Max 20 interest tags |
| `isPrivate` | bool | Private account mode |
| `showActivityStatus` | bool | Show online status |
| `allowTagging` | enum | `EVERYONE`, `FOLLOWERS`, `NONE` |
| `allowMentions` | enum | `EVERYONE`, `FOLLOWERS`, `NONE` |
| `hideOnlineStatus` | bool | Hide activity |
| `isBanned` | bool | Account banned |
| `isSuspended` | bool | Account suspended |
| `isDeactivated` | bool | Self-deactivated |
| `strikeCount` | int | Total strikes |
| `lastActiveAt` | Date | Last activity |
| `lastLoginAt` | Date | Last login |
| `createdAt` | Date | Registration date |
| `updatedAt` | Date | Last update |

**Indexes**: `{ phone: 1 }` (unique), `{ id: 1 }` (unique), `{ username: 1 }` (unique, sparse), `{ collegeId: 1 }`, `{ tribeId: 1 }`, `{ displayName: 'text', username: 'text', bio: 'text' }`

---

### `user_tribe_memberships`
Tracks tribe membership history.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Primary key |
| `userId` | string | User reference |
| `tribeId` | string | Tribe reference |
| `tribeCode` | string | Tribe code |
| `isPrimary` | bool | Current active tribe |
| `method` | string | Assignment method |
| `assignedBy` | string | Who assigned (null = system) |
| `migrationSource` | string | Legacy migration source |
| `joinedAt` | Date | Join date |
| `leftAt` | Date | Leave date (null = active) |
| `createdAt` | Date | Record creation |

---

## 2. Authentication & Sessions

### `sessions`
Active user sessions with access + refresh token split.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Session UUID |
| `userId` | string | User reference |
| `token` | string | Access token (`at_...`) |
| `accessTokenExpiresAt` | Date | 15 min TTL |
| `refreshToken` | string | Refresh token (`rt_...`) |
| `refreshTokenFamily` | string | Family ID for rotation chain |
| `refreshTokenVersion` | int | Rotation counter |
| `refreshTokenExpiresAt` | Date | 30 day TTL |
| `refreshTokenUsed` | bool | Reuse detection flag |
| `ipAddress` | string | Client IP |
| `deviceInfo` | string | User-Agent |
| `lastAccessedAt` | Date | Last API call |
| `lastRefreshedAt` | Date | Last token refresh |
| `expiresAt` | Date | Session expiry |
| `createdAt` | Date | Session start |

**Indexes**: `{ token: 1 }` (unique), `{ refreshToken: 1 }` (unique), `{ userId: 1, createdAt: -1 }`, `{ expiresAt: 1 }` (TTL)

---

### `consent_notices` / `consent_acceptances`
Legal consent tracking.

---

## 3. Content System

### `content_items`
Posts, polls, threads, carousels. The universal content table.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Primary key |
| `authorId` | string | Creator user ID |
| `authorType` | enum | `USER` or `PAGE` |
| `pageId` | string | If page-authored |
| `kind` | enum | `POST`, `REEL`, `STORY` |
| `caption` | string | Max 2200 chars |
| `hashtags` | string[] | Extracted hashtags |
| `mentions` | string[] | Mentioned user IDs |
| `media` | array | `[{ id, url, type, width, height }]` |
| `mediaIds` | string[] | Media asset references |
| `visibility` | enum | `PUBLIC`, `LIMITED`, `SHADOW_LIMITED`, `HELD_FOR_REVIEW`, `REMOVED` |
| `status` | string | `PUBLISHED`, `DRAFT`, `SCHEDULED`, `ARCHIVED` |
| `publishAt` | Date | Scheduled publish time |
| `postSubType` | string | `STANDARD`, `POLL`, `THREAD_HEAD`, `THREAD_PART`, `LINK`, `CAROUSEL` |
| `poll` | object | `{ options: [{ id, text, voteCount }], expiresAt, allowMultipleVotes, totalVotes }` |
| `threadParentId` | string | Parent thread ID |
| `threadPartIndex` | int | Order in thread |
| `carousel` | object | `{ order, coverIndex, aspectRatio }` |
| `linkUrl` | string | Link preview URL |
| `syntheticDeclaration` | bool | AI-generated flag |
| `originalContentId` | string | If repost/share |
| `isRepost` | bool | Repost flag |
| `likeCount` | int | Denormalized |
| `dislikeCount` | int | Denormalized |
| `commentCount` | int | Denormalized |
| `saveCount` | int | Denormalized |
| `shareCount` | int | Denormalized |
| `viewCount` | int | Denormalized |
| `reportCount` | int | Auto-hold at threshold |
| `pinnedCommentId` | string | Pinned comment |
| `isPinned` | bool | Pinned to profile |
| `isArchived` | bool | Archived by author |
| `isDeleted` | bool | Soft deleted |
| `tribeId` | string | Author's tribe |
| `collegeId` | string | Author's college |
| `distributionStage` | int | Content distribution stage (0-2) |
| `qualityScore` | float | Quality scoring (0-100) |
| `qualityTier` | string | `LOW`, `MEDIUM`, `HIGH`, `EXCEPTIONAL` |
| `createdAt` | Date | Creation time |
| `updatedAt` | Date | Last edit |
| `editedAt` | Date | Last caption edit |

**Indexes**: `{ id: 1 }` (unique), `{ authorId: 1, createdAt: -1 }`, `{ visibility: 1, kind: 1, createdAt: -1 }`, `{ hashtags: 1, createdAt: -1 }`, `{ caption: 'text', hashtags: 'text' }`, `{ authorType: 1, pageId: 1, createdAt: -1 }`

---

### `poll_votes`

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Primary key |
| `contentId` | string | Poll content reference |
| `userId` | string | Voter |
| `optionId` | string | Selected option |
| `createdAt` | Date | Vote time |

**Index**: `{ contentId: 1, userId: 1 }` (unique)

---

## 4. Social Graph

### `follows`

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Primary key |
| `followerId` | string | Who follows |
| `followeeId` | string | Who is followed |
| `createdAt` | Date | Follow time |

**Indexes**: `{ followerId: 1, followeeId: 1 }` (unique), `{ followeeId: 1, createdAt: -1 }`, `{ followerId: 1, createdAt: -1 }`

---

### `follow_requests`
For private accounts.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Primary key |
| `fromUserId` | string | Requester |
| `toUserId` | string | Target (private account) |
| `status` | enum | `PENDING`, `ACCEPTED`, `REJECTED` |
| `createdAt` | Date | Request time |
| `respondedAt` | Date | Decision time |

---

### `blocks`

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Primary key |
| `blockerId` | string | Who blocked |
| `blockedId` | string | Who is blocked |
| `createdAt` | Date | Block time |

**Indexes**: `{ blockerId: 1, blockedId: 1 }` (unique), bidirectional query support

---

### `mutes`

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Primary key |
| `muterId` | string | Who muted |
| `mutedId` | string | Who is muted |
| `createdAt` | Date | Mute time |

---

### `hidden_content`

| Field | Type | Description |
|-------|------|-------------|
| `userId` | string | Who hid |
| `contentId` | string | Hidden content |
| `createdAt` | Date | Hide time |

---

## 5. Reactions & Engagement

### `reactions`
Like/dislike on content items.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Primary key |
| `contentId` | string | Content reference |
| `userId` | string | Reactor |
| `type` | enum | `LIKE`, `DISLIKE` |
| `contentAuthorId` | string | Denormalized for feed ranking |
| `createdAt` | Date | Reaction time |

**Index**: `{ contentId: 1, userId: 1 }` (unique)

---

### `saves`
Bookmarked content.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Primary key |
| `contentId` | string | Content reference |
| `userId` | string | Who saved |
| `contentAuthorId` | string | For feed ranking |
| `createdAt` | Date | Save time |

**Index**: `{ contentId: 1, userId: 1 }` (unique)

---

### `likes` (legacy alias)
Some older code uses `likes` collection — maps to `reactions` with type=LIKE.

---

## 6. Comments

### `comments`

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Primary key |
| `contentId` | string | Post reference |
| `authorId` | string | Commenter |
| `text` | string | Comment body (max 1000 chars) |
| `body` | string | Alias for text |
| `parentId` | string | Parent comment (for threads) |
| `parentCommentId` | string | Alias |
| `depth` | int | Nesting depth |
| `likeCount` | int | Comment likes |
| `isPinned` | bool | Pinned by post author |
| `isEdited` | bool | Edited flag |
| `isDeleted` | bool | Soft deleted |
| `contentAuthorId` | string | Denormalized |
| `createdAt` | Date | Creation time |
| `updatedAt` | Date | Edit time |

**Indexes**: `{ contentId: 1, createdAt: -1 }`, `{ authorId: 1, createdAt: -1 }`

---

### `comment_likes`

| Field | Type | Description |
|-------|------|-------------|
| `userId` | string | Who liked |
| `commentId` | string | Comment reference |
| `createdAt` | Date | Like time |

**Index**: `{ userId: 1, commentId: 1 }` (unique)

---

## 7. Stories

### `stories`

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Primary key |
| `authorId` | string | Creator |
| `creatorId` | string | Alias |
| `type` | enum | `IMAGE`, `VIDEO`, `TEXT` |
| `mediaId` | string | Media reference |
| `mediaUrl` | string | CDN URL |
| `caption` | string | Max 2200 chars |
| `textContent` | string | Text story content |
| `backgroundColor` | string | CSS color |
| `fontStyle` | string | Font family |
| `backgroundType` | string | `SOLID`, `GRADIENT`, `IMAGE` |
| `privacy` | enum | `EVERYONE`, `FOLLOWERS`, `CLOSE_FRIENDS` |
| `stickers` | array | Interactive sticker objects (see below) |
| `status` | enum | `ACTIVE`, `EXPIRED`, `REMOVED`, `HELD` |
| `viewCount` | int | Total views |
| `reactionCount` | int | Total reactions |
| `replyCount` | int | Total replies |
| `reportCount` | int | Report count |
| `expiresAt` | Date | Auto-expiry (24h from creation) |
| `isArchived` | bool | Auto-archived on expiry |
| `isDeleted` | bool | Soft deleted |
| `createdAt` | Date | Creation time |

**Sticker object shape:**
```json
{
  "id": "sticker-uuid",
  "type": "POLL|QUESTION|QUIZ|EMOJI_SLIDER|MENTION|LOCATION|HASHTAG|LINK|COUNTDOWN|MUSIC",
  "position": { "x": 50, "y": 60 },
  "question": "...",
  "options": ["A", "B"],
  "correctIndex": 1,
  "emoji": "🔥",
  "userId": "...",
  "name": "...",
  "tag": "...",
  "url": "...",
  "label": "...",
  "endAt": "ISO date",
  "trackId": "...",
  "trackName": "..."
}
```

---

### `story_views`

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Primary key |
| `storyId` | string | Story reference |
| `viewerId` | string | Who viewed |
| `viewedAt` | Date | View timestamp |

**Index**: `{ storyId: 1, viewerId: 1 }` (unique — deduplication)

---

### `story_reactions`

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Primary key |
| `storyId` | string | Story reference |
| `userId` | string | Reactor |
| `emoji` | string | One of: `❤️`, `🔥`, `😂`, `😮`, `😢`, `👏` |
| `createdAt` | Date | Reaction time |

---

### `story_replies`

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Primary key |
| `storyId` | string | Story reference |
| `authorId` | string | Replier |
| `text` | string | Max 1000 chars |
| `createdAt` | Date | Reply time |

---

### `story_sticker_responses`

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Primary key |
| `storyId` | string | Story reference |
| `stickerId` | string | Sticker reference |
| `userId` | string | Responder |
| `optionIndex` | int | For polls/quizzes |
| `text` | string | For question stickers |
| `value` | float | For emoji sliders (0-1) |
| `isCorrect` | bool | For quizzes |
| `createdAt` | Date | Response time |

---

### `story_view_durations`

| Field | Type | Description |
|-------|------|-------------|
| `storyId` | string | Story reference |
| `userId` | string | Viewer |
| `durationMs` | int | View duration |
| `createdAt` | Date | Timestamp |

---

### `story_highlights`

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Primary key |
| `userId` | string | Owner |
| `title` | string | Max 50 chars |
| `coverMediaId` | string | Cover image |
| `createdAt` | Date | Creation time |
| `updatedAt` | Date | Last update |

---

### `story_highlight_items`

| Field | Type | Description |
|-------|------|-------------|
| `highlightId` | string | Highlight reference |
| `storyId` | string | Story reference |
| `addedAt` | Date | When added |

---

### `close_friends`

| Field | Type | Description |
|-------|------|-------------|
| `userId` | string | Owner |
| `friendId` | string | Close friend |
| `createdAt` | Date | Added time |

**Index**: `{ userId: 1, friendId: 1 }` (unique)

---

### `story_settings`

| Field | Type | Description |
|-------|------|-------------|
| `userId` | string | Owner (unique) |
| `allowReplies` | enum | `EVERYONE`, `FOLLOWERS`, `CLOSE_FRIENDS`, `OFF` |
| `allowSharing` | bool | Allow story sharing |
| `hideStoryFrom` | string[] | Hidden from these users |
| `closeFriendsOnly` | bool | Default to close friends |

---

### `story_mutes`

| Field | Type | Description |
|-------|------|-------------|
| `userId` | string | Who muted |
| `mutedUserId` | string | Whose stories are muted |
| `createdAt` | Date | Mute time |

---

## 8. Reels

### `reels`

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Primary key |
| `creatorId` | string | Creator user ID |
| `caption` | string | Max 2200 chars |
| `hashtags` | string[] | Max 30 |
| `mentions` | string[] | Max 20 user IDs |
| `mediaId` | string | Video media reference |
| `mediaUrl` | string | CDN URL |
| `mediaStatus` | enum | `UPLOADING`, `PROCESSING`, `READY`, `FAILED` |
| `audioId` | string | Audio track reference |
| `audioName` | string | Track name |
| `durationMs` | int | Duration (max 90000) |
| `visibility` | enum | `PUBLIC`, `FOLLOWERS`, `PRIVATE` |
| `status` | enum | `DRAFT`, `PUBLISHED`, `ARCHIVED`, `REMOVED`, `HELD` |
| `remixOf` | string | Original reel if remix |
| `seriesId` | string | Reel series reference |
| `seriesOrder` | int | Order in series |
| `likeCount` | int | Denormalized |
| `commentCount` | int | Denormalized |
| `saveCount` | int | Denormalized |
| `shareCount` | int | Denormalized |
| `viewCount` | int | Denormalized |
| `completionCount` | int | Watched to end |
| `totalWatchTimeMs` | int | Total watch time |
| `reportCount` | int | Report count |
| `isPinned` | bool | Pinned to profile |
| `isDeleted` | bool | Soft deleted |
| `tribeId` | string | Creator's tribe |
| `collegeId` | string | Creator's college |
| `createdAt` | Date | Creation time |
| `updatedAt` | Date | Last update |
| `publishedAt` | Date | Publish time |

---

### Related Reel Collections:
| Collection | Unique Index | Fields |
|------------|-------------|--------|
| `reel_likes` | `{ reelId, userId }` | reelId, userId, createdAt |
| `reel_saves` | `{ reelId, userId }` | reelId, userId, createdAt |
| `reel_comments` | — | id, reelId, authorId, text, parentId, likeCount, createdAt |
| `reel_shares` | — | id, reelId, userId, platform, createdAt |
| `reel_views` | `{ reelId, userId }` | reelId, userId, viewedAt |
| `reel_watch_events` | — | reelId, userId, watchDurationMs, completionRate, isReplay, createdAt |
| `reel_reports` | `{ reelId, userId }` | reelId, userId, reason, details, createdAt |
| `reel_hidden` | — | reelId, userId, createdAt |
| `reel_not_interested` | — | reelId, userId, createdAt |
| `reel_processing_jobs` | — | id, reelId, status, progress, createdAt |
| `reel_series` | — | id, creatorId, title, description, createdAt |

---

## 9. Pages

### `pages`

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Primary key |
| `slug` | string | URL slug (unique) |
| `name` | string | Page name |
| `description` | string | Description |
| `category` | enum | See Page Categories |
| `status` | enum | `DRAFT`, `ACTIVE`, `ARCHIVED`, `SUSPENDED` |
| `isOfficial` | bool | Official entity page |
| `linkedEntityType` | enum | `COLLEGE`, `TRIBE`, `CLUB`, etc. |
| `linkedEntityId` | string | Entity reference |
| `verificationStatus` | enum | `NONE`, `PENDING`, `VERIFIED`, `REJECTED` |
| `coverMediaId` | string | Cover image |
| `avatarMediaId` | string | Avatar |
| `followerCount` | int | Denormalized |
| `postCount` | int | Denormalized |
| `createdByUserId` | string | Creator |
| `createdAt` | Date | Creation time |
| `updatedAt` | Date | Last update |

**Page Categories**: `COLLEGE_OFFICIAL`, `DEPARTMENT`, `CLUB`, `TRIBE_OFFICIAL`, `FEST`, `MEME`, `STUDY_GROUP`, `HOSTEL`, `STUDENT_COUNCIL`, `ALUMNI_CELL`, `PLACEMENT_CELL`, `OTHER`

---

### `page_members`

| Field | Type | Description |
|-------|------|-------------|
| `pageId` | string | Page reference |
| `userId` | string | Member |
| `role` | enum | `OWNER`, `ADMIN`, `EDITOR`, `MODERATOR` |
| `status` | enum | `ACTIVE`, `INVITED`, `REMOVED` |
| `invitedBy` | string | Who invited |
| `createdAt` | Date | Join date |

**Role Hierarchy**: OWNER(4) > ADMIN(3) > EDITOR(2) > MODERATOR(1)

---

### `page_follows`

| Field | Type | Description |
|-------|------|-------------|
| `pageId` | string | Page reference |
| `userId` | string | Follower |
| `createdAt` | Date | Follow time |

---

## 10. Events

### `events`

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Primary key |
| `creatorId` | string | Organizer |
| `title` | string | Max 200 chars |
| `description` | string | Max 5000 chars |
| `category` | enum | `ACADEMIC`, `CULTURAL`, `SPORTS`, `SOCIAL`, `WORKSHOP`, `PLACEMENT`, `OTHER` |
| `visibility` | enum | `PUBLIC`, `COLLEGE`, `PRIVATE` |
| `status` | enum | `DRAFT`, `PUBLISHED`, `CANCELLED`, `ARCHIVED`, `HELD`, `REMOVED` |
| `startAt` | Date | Event start |
| `endAt` | Date | Event end |
| `location` | string | Max 300 chars |
| `capacity` | int | Max attendees |
| `coverMediaId` | string | Cover image |
| `collegeId` | string | College filter |
| `goingCount` | int | RSVP going |
| `interestedCount` | int | RSVP interested |
| `reportCount` | int | Report count |
| `createdAt` | Date | Creation time |

---

### `event_rsvps`

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Primary key |
| `eventId` | string | Event reference |
| `userId` | string | Attendee |
| `status` | enum | `GOING`, `INTERESTED` |
| `createdAt` | Date | RSVP time |

---

### `event_reminders` / `event_reports`
Track reminders and reports per event per user.

---

## 11. Tribes

### `tribes`
The 21 Param Vir Chakra tribes.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Primary key |
| `tribeCode` | string | Short code (e.g., `BATRA`) |
| `tribeName` | string | Full name |
| `heroName` | string | Param Vir Chakra awardee |
| `paramVirChakraName` | string | Full hero name |
| `animalIcon` | string | Animal mascot |
| `primaryColor` | string | Hex color |
| `secondaryColor` | string | Hex color |
| `quote` | string | Tribe motto |
| `sortOrder` | int | Display order (1-21) |
| `isActive` | bool | Active flag |
| `membersCount` | int | Denormalized |
| `totalSalutes` | int | Total salute points |
| `createdAt` | Date | Seed time |

---

### `tribe_salute_ledger`
Point history (immutable audit trail).

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Primary key |
| `tribeId` | string | Tribe reference |
| `amount` | int | Points (positive or negative) |
| `reason` | enum | `CONTEST_WIN`, `CONTEST_RUNNER_UP`, `CONTENT_BONUS`, `ADMIN_AWARD`, `ADMIN_DEDUCT`, `REVERSAL`, `MIGRATION_CARRYOVER`, `WEEKLY_BONUS` |
| `description` | string | Human description |
| `awardedBy` | string | Admin user ID |
| `seasonId` | string | Season reference |
| `contestId` | string | Contest reference |
| `createdAt` | Date | Award time |

---

### Other Tribe Collections:
| Collection | Purpose |
|------------|---------|
| `tribe_seasons` | Season definitions (start/end dates, status) |
| `tribe_standings` | Per-season tribe standings snapshot |
| `tribe_boards` | Tribe board governance structure |
| `tribe_board_members` | Board seat assignments |
| `tribe_cheers` | Per-user cheer actions |
| `tribe_fund_accounts` | Tribe prize fund balances |
| `tribe_fund_ledger` | Fund transaction history |
| `tribe_awards` | Annual award records |
| `tribe_assignment_events` | Assignment audit trail |

---

## 12. Tribe Contests

### `tribe_contests`

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Primary key |
| `title` | string | Contest title |
| `description` | string | Contest description |
| `type` | string | Contest type |
| `seasonId` | string | Season reference |
| `status` | enum | `DRAFT`, `PUBLISHED`, `ENTRY_OPEN`, `ENTRY_CLOSED`, `EVALUATING`, `LOCKED`, `RESOLVED`, `CANCELLED` |
| `maxEntriesPerTribe` | int | Entry limit per tribe |
| `maxEntriesTotal` | int | Total entry limit |
| `votingEnabled` | bool | Public voting |
| `votingWeight` | float | Vote weight in scoring |
| `judgeWeight` | float | Judge score weight |
| `prizes` | array | Prize definitions |
| `rules` | array | Contest rules |
| `entryCount` | int | Denormalized |
| `voteCount` | int | Denormalized |
| `createdBy` | string | Admin who created |
| `createdAt` | Date | Creation time |
| `publishedAt` | Date | Publish time |
| `entriesOpenAt` | Date | Entry open time |
| `entriesCloseAt` | Date | Entry close time |
| `resolvedAt` | Date | Resolution time |

---

### Related Contest Collections:
| Collection | Purpose |
|------------|---------|
| `tribe_contest_entries` | Submitted entries |
| `contest_votes` | Public votes (unique per user per entry) |
| `contest_judge_scores` | Judge scores |
| `tribe_contest_scores` | Computed final scores |
| `tribe_contest_results` | Official results with rankings |
| `tribe_contest_rules` | Versioned contest rules |
| `tribe_contest_standings` | Per-season contest standings |

---

## 13. Search & Discovery

### `colleges`

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Primary key |
| `name` | string | College name |
| `state` | string | State |
| `city` | string | City |
| `type` | string | IIT, NIT, IIIT, etc. |
| `domain` | string | Email domain |
| `membersCount` | int | Student count |
| `createdAt` | Date | Seed time |

---

### `hashtags`

| Field | Type | Description |
|-------|------|-------------|
| `tag` | string | Hashtag text (unique) |
| `postCount` | int | Usage count |
| `weeklyCount` | int | Last 7 days |
| `lastUsedAt` | Date | Last usage |
| `createdAt` | Date | First usage |

---

### `recent_searches`

| Field | Type | Description |
|-------|------|-------------|
| `userId` | string | Searcher |
| `query` | string | Search text |
| `searchedAt` | Date | Search time |

---

## 14. Notifications

### `notifications`

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Primary key |
| `userId` | string | Recipient |
| `type` | enum | See Notification Types |
| `message` | string | Display text |
| `actorId` | string | Who triggered |
| `targetType` | string | `CONTENT`, `REEL`, `STORY`, `USER`, `EVENT`, `PAGE` |
| `targetId` | string | Target reference |
| `read` | bool | Read status |
| `createdAt` | Date | Creation time |

**Notification Types**: `FOLLOW`, `LIKE`, `COMMENT`, `COMMENT_LIKE`, `SHARE`, `MENTION`, `REPORT_RESOLVED`, `STRIKE_ISSUED`, `APPEAL_DECIDED`, `HOUSE_POINTS`, `REEL_LIKE`, `REEL_COMMENT`, `REEL_SHARE`, `STORY_REACTION`, `STORY_REPLY`, `STORY_REMOVED`

---

### `notification_preferences`

| Field | Type | Description |
|-------|------|-------------|
| `userId` | string | Owner (unique) |
| `likes` | bool | Like notifications |
| `comments` | bool | Comment notifications |
| `follows` | bool | Follow notifications |
| `mentions` | bool | Mention notifications |
| `stories` | bool | Story notifications |
| `reels` | bool | Reel notifications |

---

### `device_tokens`

| Field | Type | Description |
|-------|------|-------------|
| `userId` | string | Owner |
| `token` | string | FCM/APNs token |
| `platform` | string | `android`, `ios`, `web` |
| `isActive` | bool | Active flag |
| `createdAt` | Date | Registration time |

---

## 15. Moderation & Reports

### `reports`

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Primary key |
| `reporterId` | string | Who reported |
| `targetId` | string | Reported entity |
| `targetType` | string | `CONTENT`, `USER`, `COMMENT`, `REEL`, `STORY`, `EVENT`, `PAGE` |
| `reason` | string | `SPAM`, `HARASSMENT`, `INAPPROPRIATE`, `HATE_SPEECH`, `VIOLENCE`, `MISINFORMATION`, `OTHER` |
| `details` | string | Additional context |
| `status` | enum | `OPEN`, `REVIEWING`, `RESOLVED`, `DISMISSED` |
| `resolvedBy` | string | Moderator ID |
| `resolution` | string | Action taken |
| `createdAt` | Date | Report time |
| `resolvedAt` | Date | Resolution time |

---

### `appeals`

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Primary key |
| `userId` | string | Appellant |
| `contentId` | string | Moderated content |
| `reason` | string | Appeal reason |
| `status` | enum | `PENDING`, `REVIEWING`, `APPROVED`, `DENIED` |
| `decidedBy` | string | Moderator ID |
| `decision` | string | Decision reason |
| `createdAt` | Date | Appeal time |
| `decidedAt` | Date | Decision time |

---

### `strikes` / `suspensions`
Track user strikes and suspension records.

### `moderation_events`
Audit trail of all moderation actions.

### `audit_logs`
System-wide audit trail.

### `grievance_tickets`
User grievance submissions.

---

## 16. Media & Transcoding

### `media_assets`

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Primary key |
| `uploaderId` | string | Who uploaded |
| `filename` | string | Original filename |
| `mimeType` | string | MIME type |
| `fileSize` | int | Bytes |
| `type` | string | `IMAGE`, `VIDEO`, `AUDIO`, `DOCUMENT` |
| `status` | enum | `PENDING`, `UPLOADING`, `PROCESSING`, `READY`, `FAILED`, `DELETED` |
| `storagePath` | string | Supabase path |
| `publicUrl` | string | CDN URL |
| `width` | int | Image/video width |
| `height` | int | Image/video height |
| `durationMs` | int | Video duration |
| `thumbnailUrl` | string | Video thumbnail |
| `createdAt` | Date | Upload time |

---

### `transcode_jobs`

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Job UUID |
| `mediaId` | string | Media reference |
| `status` | enum | `QUEUED`, `PROCESSING`, `COMPLETED`, `FAILED`, `CANCELLED` |
| `progress` | int | 0-100 |
| `inputPath` | string | Source file |
| `outputPath` | string | HLS output |
| `variants` | array | `[{ resolution, bitrate, path }]` |
| `thumbnails` | array | Generated thumbnails |
| `error` | string | Error message if failed |
| `createdAt` | Date | Job creation |
| `completedAt` | Date | Completion time |

---

## 17. Resources

### `resources`

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Primary key |
| `authorId` | string | Uploader |
| `title` | string | 3-200 chars |
| `description` | string | Max 2000 chars |
| `kind` | enum | `NOTE`, `PYQ`, `ASSIGNMENT`, `SYLLABUS`, `LAB_FILE` |
| `status` | enum | `PUBLIC`, `HELD`, `UNDER_REVIEW`, `REMOVED` |
| `tags` | string[] | Search tags |
| `collegeId` | string | College filter |
| `subject` | string | Subject |
| `semester` | int | Semester number |
| `year` | int | Academic year |
| `mediaIds` | string[] | Attached files |
| `upvoteCount` | int | Upvotes |
| `downvoteCount` | int | Downvotes |
| `downloadCount` | int | Downloads |
| `reportCount` | int | Reports |
| `createdAt` | Date | Upload time |

---

### `resource_votes` / `resource_downloads`
Track votes and download events per resource per user.

---

## 18. Governance

### `board_seats`
College board seat definitions.

### `board_applications`
Applications for board positions.

### `board_proposals`
Governance proposals for voting.

---

## 19. Board Notices & Authenticity

### `board_notices`

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Primary key |
| `authorId` | string | Board member who created |
| `collegeId` | string | College scope |
| `title` | string | Notice title |
| `body` | string | Notice content |
| `priority` | string | `LOW`, `NORMAL`, `HIGH`, `URGENT` |
| `status` | enum | `PENDING`, `APPROVED`, `REJECTED`, `PUBLISHED` |
| `isPinned` | bool | Pinned notice |
| `acknowledgeCount` | int | Acknowledgment count |
| `createdAt` | Date | Creation time |

### `notice_acknowledgments`
Track who acknowledged each notice.

### `authenticity_tags`
Verification tags on content/users by board members.

---

## 20. Analytics

### `analytics_events`
Raw event tracking (impressions, views, profile visits).

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Primary key |
| `userId` | string | Who generated |
| `eventType` | string | `IMPRESSION`, `VIEW`, `PROFILE_VISIT`, `CONTENT_VIEW` |
| `targetType` | string | Entity type |
| `targetId` | string | Entity reference |
| `metadata` | object | Additional data |
| `createdAt` | Date | Event time |

### `profile_visits`
Dedicated profile visit tracking with viewer info.

---

## 21. Anti-Abuse

### `abuse_audit_log`
Logs flagged suspicious engagement patterns.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Primary key |
| `userId` | string | Flagged user |
| `actionType` | string | `LIKE`, `COMMENT`, `SHARE`, `SAVE`, `VIEW`, `FOLLOW`, `VOTE` |
| `reason` | string | Why flagged |
| `velocity` | float | Actions per second |
| `windowMs` | int | Detection window |
| `isSuspicious` | bool | Suspicious flag |
| `createdAt` | Date | Detection time |

---

## 22. Collection Index Summary

### Critical Unique Indexes
| Collection | Index |
|------------|-------|
| `users` | `{ phone: 1 }`, `{ id: 1 }`, `{ username: 1 }` (sparse) |
| `sessions` | `{ token: 1 }`, `{ refreshToken: 1 }` |
| `follows` | `{ followerId: 1, followeeId: 1 }` |
| `blocks` | `{ blockerId: 1, blockedId: 1 }` |
| `reactions` | `{ contentId: 1, userId: 1 }` |
| `saves` | `{ contentId: 1, userId: 1 }` |
| `poll_votes` | `{ contentId: 1, userId: 1 }` |
| `comment_likes` | `{ userId: 1, commentId: 1 }` |
| `story_views` | `{ storyId: 1, viewerId: 1 }` |
| `close_friends` | `{ userId: 1, friendId: 1 }` |
| `reel_likes` | `{ reelId: 1, userId: 1 }` |
| `reel_saves` | `{ reelId: 1, userId: 1 }` |
| `reel_views` | `{ reelId: 1, userId: 1 }` |
| `pages` | `{ slug: 1 }`, `{ id: 1 }` |
| `page_members` | `{ pageId: 1, userId: 1 }` |
| `page_follows` | `{ pageId: 1, userId: 1 }` |
| `contest_votes` | `{ contestId: 1, userId: 1, entryId: 1 }` |

### Text Search Indexes
| Collection | Fields | Weights |
|------------|--------|---------|
| `users` | displayName, username, bio | 10, 8, 2 |
| `content_items` | caption, hashtags | 3, 5 |
| `reels` | caption, hashtags | 3, 5 |
| `pages` | name, description, category | 10, 2, 5 |
| `tribes` | tribeName, tribeCode | 10, 5 |

---

*95 MongoDB collections. All IDs are UUIDs. `_id` excluded from all responses.*
