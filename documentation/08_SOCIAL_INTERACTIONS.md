# 08 — Social Interactions

## Overview

The social interactions layer handles **likes, dislikes, saves, comments, shares/reposts, follows, blocks, mutes, pins, hides**, and **reports** across all content types. It is centralized in `lib/handlers/social.js` (887 lines) with support from `lib/access-policy.js` (block/mute filtering).

---

## Content Reactions

### Like / Dislike System

Reactions are stored in the `reactions` collection with type `LIKE` or `DISLIKE`. Switching between them atomically decrements the old counter and increments the new one.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/content/:id/like` | Like content |
| `POST` | `/api/content/:id/dislike` | Dislike (internal signal, not visible to author) |
| `DELETE` | `/api/content/:id/reaction` | Remove reaction |

**Anti-abuse**: All reactions pass through `checkEngagementAbuse()` before processing.

**Notifications**: Likes trigger notifications to the content author. Dislikes do NOT generate notifications (internal ranking signal only). For page-authored content, notifications go to page OWNER + ADMIN members.

**Response**:
```json
{ "likeCount": 42, "viewerHasLiked": true, "viewerHasDisliked": false }
```

### Save / Unsave

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/content/:id/save` | Save content |
| `DELETE` | `/api/content/:id/save` | Unsave content |

Saves increment `saveCount` on the content item. Anti-abuse checked.

---

## Comments

### Create Comment

`POST /api/content/:id/comments`

```json
{
  "body": "Great post!",
  "parentId": null  // null = top-level, string = reply
}
```

Accepts both `body` and `text` fields (canonical precedence: `body || text`).

**Moderation**: Every comment passes through the `moderateCreateContent` pipeline. If content is rejected, returns 400 with `CONTENT_REJECTED_BY_MODERATION`.

**Comment schema**:
```javascript
{
  id: UUID,
  contentId: String,
  authorId: String,
  parentId: String | null,
  body: String,        // Max Config.MAX_COMMENT_LENGTH
  text: String,        // Alias of body
  likeCount: Number,
  moderation: {
    action: String,
    provider: String,
    confidence: Number,
    flaggedCategories: [String],
    reviewTicketId: String | null
  },
  createdAt: Date
}
```

### List Comments

`GET /api/content/:id/comments?parentId=&cursor=&limit=20`

- Top-level comments: `parentId=null` (default)
- Replies: `parentId=<commentId>`
- Blocked user comments are filtered via `filterBlockedComments()`
- Returns both `items` and `comments` (backward-compat alias)

### Comment Actions

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/content/:postId/comments/:commentId/like` | Like comment |
| `DELETE` | `/api/content/:postId/comments/:commentId/like` | Unlike comment |
| `POST` | `/api/content/:id/comments/:cid/reply` | Reply (max 500 chars) |
| `PATCH` | `/api/content/:id/comments/:cid` | Edit comment (author only) |
| `DELETE` | `/api/content/:id/comments/:cid` | Delete (author, post author, or admin) |
| `POST` | `/api/content/:id/comments/:cid/pin` | Pin comment (post author only, max 1) |
| `POST` | `/api/content/:id/comments/:cid/report` | Report comment |

---

## Shares / Reposts

`POST /api/content/:id/share`

Creates a new `content_items` document with `isRepost: true` and `originalContentId` referencing the source. Rules:
- Cannot repost a repost (only original content)
- One repost per user per original
- Optional `caption` for quote-repost
- Anti-abuse checked
- Increments `shareCount` on original

For page-authored content, share notifications go to page OWNER + ADMIN members.

**List shares**: `GET /api/content/:id/shares` returns repost authors and captions.

---

## Follow System

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/follow/:userId` | Follow user |
| `DELETE` | `/api/follow/:userId` | Unfollow user |

**Follow mechanics**:
- Self-follow returns 409
- Anti-abuse velocity check
- Atomically increments `followingCount` / `followersCount` on both users
- Sends FOLLOW notification to target
- Idempotent: re-following returns `"Already following"`

**Response fields**: `isFollowing`, `viewerIsFollowing` (both included for client compatibility)

---

## Content Visibility Actions

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/content/:id/archive` | Archive own post |
| `POST` | `/api/content/:id/unarchive` | Restore archived post |
| `POST` | `/api/content/:id/pin` | Pin to profile (max 1, unpins previous) |
| `DELETE` | `/api/content/:id/pin` | Unpin from profile |
| `POST` | `/api/content/:id/hide` | Hide from your feed |
| `DELETE` | `/api/content/:id/hide` | Unhide |

---

## Content Reporting

`POST /api/content/:id/report`

```json
{
  "reason": "SPAM",
  "details": "This is a promotional spam post"
}
```

- Cannot report own content
- Deduplicated per user per target
- Stored in `reports` collection with `targetType: 'CONTENT'`
- Audit trail via `writeAudit()`

---

## Story Interaction Guards

All social interactions check for expired stories before processing:

```javascript
function isExpiredStory(post) {
  return post.kind === 'STORY' && 
    (!post.expiresAt || new Date(post.expiresAt) <= new Date())
}
```

Expired stories return `410 Gone` with `code: 'EXPIRED'`.

---

## Block & Access Policy Integration

The `access-policy.js` module enforces:

- **`canViewContent(post, viewerId, viewerRole)`**: Checks visibility, REMOVED status, and admin override
- **`canViewComments(parentContent, viewerId, viewerRole)`**: Blocks comment access if parent is hidden/removed
- **`isBlocked(db, userA, userB)`**: Bidirectional block check
- **`filterBlockedComments(db, viewerId, comments)`**: Removes comments from blocked users
- **`filterBlockedNotifications(db, userId, notifications)`**: Removes notifications from blocked actors

Block checks happen at every social interaction entry point. If a block exists between the acting user and the content author, the API returns `404 Not Found` (not 403) to prevent information leakage.

---

## Distribution Auto-Evaluation

After likes and comments, the system fires `triggerAutoEval(db, contentId)` from `handlers/stages.js`. This evaluates whether the content should be promoted to the next distribution stage based on engagement velocity.

---

## Supporting Collections

| Collection | Purpose | Key Fields |
|------------|---------|------------|
| `reactions` | Like/dislike tracking | `{userId, contentId, type}` |
| `saves` | Bookmark tracking | `{userId, contentId}` |
| `comments` | Comment tree | `{contentId, authorId, parentId}` |
| `comment_likes` | Comment like tracking | `{userId, commentId}` unique |
| `follows` | Follow relationships | `{followerId, followeeId}` |
| `hidden_content` | Feed hides | `{userId, contentId}` |
| `reports` | Content/comment reports | `{reporterId, targetId, targetType}` |
| `blocks` | Bidirectional blocks | `{blockerId, blockedId}` |

---

## Android Integration Notes

### Optimistic UI Pattern

For likes/saves, update the UI immediately and revert on failure:

```kotlin
// Optimistic update
viewModel.toggleLike(contentId)

try {
    api.post("/api/content/$contentId/like")
} catch (e: Exception) {
    viewModel.toggleLike(contentId) // Revert
}
```

### Pagination Pattern for Comments

```kotlin
var cursor: String? = null

suspend fun loadComments(contentId: String): List<Comment> {
    val response = api.get("/api/content/$contentId/comments", mapOf(
        "limit" to "20",
        "cursor" to (cursor ?: "")
    ))
    cursor = response.pagination.nextCursor
    return response.items
}
```
