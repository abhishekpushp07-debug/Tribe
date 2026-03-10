# Tribe — Serializer Contracts (Frozen v2.1)
**Verified from actual backend code + live API responses**
**Last verified**: 2026-03-10 (Post B4 + FH1-U)

---

## CRITICAL: Dual Author System (B3)

Every content item now has `authorType`. The `author` field shape depends on this:

```
if (post.authorType === "USER") → post.author is UserSnippet
if (post.authorType === "PAGE") → post.author is PageSnippet
```

These two shapes have DIFFERENT fields. Frontend MUST check `authorType` before accessing author fields.

---

## UserSnippet
**Used in**: post.author (when USER), comment.author, notification actor, follower/following cards, search results

```json
{
  "id": "095b8201-6b7f-41cc-bea8-c8b1494d23b0",
  "displayName": "UserA_Author",
  "username": null,
  "avatarUrl": null,
  "avatarMediaId": null,
  "avatar": null,
  "role": "USER",
  "collegeId": null,
  "collegeName": null,
  "houseId": "dbc4e3ef-f9c8-4f3f-a528-8ef0ee5a5df0",
  "houseName": "Saraswati",
  "tribeId": null,
  "tribeCode": null
}
```

**Nullable fields**: `displayName`, `username`, `avatarUrl`, `avatarMediaId`, `avatar`, `collegeId`, `collegeName`, `houseId`, `houseName`, `tribeId`, `tribeCode`

**`avatar` is DEPRECATED** — same as `avatarMediaId`. Use `avatarUrl` for display.

**Frontend rendering**:
- Display name: `author.displayName || author.username || "Anonymous"`
- Avatar: `author.avatarUrl || defaultAvatarPlaceholder`
- Tap → navigate to `/profile/${author.id}`

---

## PageSnippet
**Used in**: post.author (when PAGE), search results, page list

```json
{
  "id": "page-uuid",
  "slug": "meme-lords",
  "name": "Meme Lords",
  "avatarUrl": "/api/media/xxx",
  "avatarMediaId": "xxx",
  "category": "MEME",
  "isOfficial": false,
  "verificationStatus": "NONE",
  "linkedEntityType": null,
  "linkedEntityId": null,
  "collegeId": null,
  "tribeId": null,
  "status": "ACTIVE"
}
```

**KEY DIFFERENCES from UserSnippet**:
- Has `slug`, `name`, `category`, `isOfficial`, `verificationStatus` → NOT in UserSnippet
- Does NOT have `username`, `displayName` → these are in UserSnippet only
- Has `status` (ACTIVE/ARCHIVED/SUSPENDED)

**Frontend rendering**:
- Display name: `author.name` (NOT displayName!)
- Avatar: `author.avatarUrl || defaultPagePlaceholder`
- Show verification badge if `verificationStatus === "VERIFIED"`
- Tap → navigate to `/page/${author.slug}` (NOT /profile/)

---

## PageProfile (Full Detail)
**Returned by**: `GET /pages/:idOrSlug`

```json
{
  "id": "page-uuid",
  "slug": "meme-lords",
  "name": "Meme Lords",
  "avatarUrl": "/api/media/xxx",
  "avatarMediaId": "xxx",
  "category": "MEME",
  "isOfficial": false,
  "verificationStatus": "NONE",
  "linkedEntityType": null,
  "linkedEntityId": null,
  "collegeId": null,
  "tribeId": null,
  "status": "ACTIVE",
  "bio": "Best memes on campus",
  "subcategory": "",
  "coverUrl": null,
  "coverMediaId": null,
  "followerCount": 42,
  "memberCount": 3,
  "postCount": 15,
  "createdAt": "2026-03-10T...",
  "updatedAt": "2026-03-10T...",
  "viewerIsFollowing": true,
  "viewerRole": "EDITOR"
}
```

**`viewerRole`**: null (outsider), "MODERATOR", "EDITOR", "ADMIN", "OWNER"
**`viewerIsFollowing`**: boolean — use for Follow/Unfollow button state

---

## UserProfile (Full Detail)
**Returned by**: `GET /auth/me`, `GET /auth/login`, `GET /auth/register`, `GET /users/:id`

```json
{
  "id": "user-uuid",
  "displayName": "Cool User",
  "username": "cooluser",
  "phone": "7777000001",
  "bio": "Hello world",
  "avatarUrl": "/api/media/xxx",
  "avatarMediaId": "xxx",
  "avatar": "xxx",
  "role": "USER",
  "ageStatus": "ADULT",
  "collegeId": "college-uuid",
  "collegeName": "IIT Delhi",
  "houseId": "house-uuid",
  "houseName": "Saraswati",
  "tribeId": "tribe-uuid",
  "tribeCode": "PHOENIX",
  "followerCount": 120,
  "followingCount": 85,
  "postCount": 30,
  "onboardingStep": null,
  "createdAt": "2026-01-15T...",
  "updatedAt": "2026-03-10T..."
}
```

**Security**: `pinHash`, `pinSalt`, `_id` are ALWAYS stripped. Never in response.

---

## PostObject (Enriched) — THE CORE CONTENT SHAPE

**Returned by**: all feeds, content detail, page posts, search results

### Normal User Post
```json
{
  "id": "ecb74bcf-48dc-4d07-8dd0-9eb750af92d3",
  "kind": "POST",
  "caption": "UserA public post for B2 test",
  "media": [],
  "mediaIds": [],
  "authorId": "095b8201-...",
  "authorType": "USER",
  "createdAs": "USER",
  "author": {
    "id": "095b8201-...",
    "displayName": "UserA_Author",
    "username": null,
    "avatarUrl": null,
    "avatarMediaId": null,
    "avatar": null,
    "role": "USER",
    "collegeId": null,
    "collegeName": null,
    "houseId": "dbc4e3ef-...",
    "houseName": "Saraswati",
    "tribeId": null,
    "tribeCode": null
  },
  "pageId": null,
  "actingUserId": "095b8201-...",
  "actingRole": null,
  "visibility": "PUBLIC",
  "likeCount": 0,
  "commentCount": 1,
  "saveCount": 0,
  "shareCount": 0,
  "viewCount": 0,
  "viewerHasLiked": false,
  "viewerHasDisliked": false,
  "viewerHasSaved": false,
  "editedAt": null,
  "collegeId": null,
  "houseId": "dbc4e3ef-...",
  "distributionStage": 2,
  "duration": null,
  "expiresAt": null,
  "createdAt": "2026-03-10T15:43:01.393Z",
  "updatedAt": "2026-03-10T15:43:01.393Z"
}
```
*This is a REAL response from the live API.*

### Page-Authored Post
Same shape, but:
```json
{
  "authorType": "PAGE",
  "authorId": "page-uuid",
  "pageId": "page-uuid",
  "actingUserId": "real-human-uuid",
  "actingRole": "OWNER",
  "createdAs": "PAGE",
  "author": {
    "id": "page-uuid",
    "slug": "meme-lords",
    "name": "Meme Lords",
    "avatarUrl": "/api/media/xxx",
    "avatarMediaId": "xxx",
    "category": "MEME",
    "isOfficial": false,
    "verificationStatus": "NONE",
    "status": "ACTIVE"
  }
}
```
**Note**: `actingUserId` is the real human who posted. NOT exposed publicly for rendering — only for audit. Frontend uses `author` object only.

### Repost (B4 NEW)
```json
{
  "id": "repost-uuid",
  "kind": "POST",
  "caption": "",
  "media": [],
  "authorId": "reposter-uuid",
  "authorType": "USER",
  "author": { /* reposter UserSnippet */ },
  "isRepost": true,
  "originalContentId": "original-post-uuid",
  "originalContent": {
    "id": "original-post-uuid",
    "caption": "Original text",
    "authorType": "USER",
    "author": { /* original author UserSnippet or PageSnippet */ },
    "media": [...],
    "likeCount": 42,
    "commentCount": 7,
    "shareCount": 3
  },
  "likeCount": 0,
  "commentCount": 0,
  "saveCount": 0,
  "shareCount": 0,
  "viewerHasLiked": false,
  "viewerHasSaved": false,
  "editedAt": null,
  "createdAt": "..."
}
```
**When original is deleted**: `originalContent` will be `null`.

### Edited Post (B4 NEW field)
Any post that has been edited will have:
```json
{
  "editedAt": "2026-03-10T17:30:00.000Z"
}
```
Normal posts have `editedAt: null`.

---

## CommentObject
**Returned by**: `GET /content/:postId/comments`

```json
{
  "id": "comment-uuid",
  "contentId": "post-uuid",
  "authorId": "user-uuid",
  "author": { /* UserSnippet */ },
  "text": "Great post!",
  "body": "Great post!",
  "likeCount": 3,
  "parentId": null,
  "moderation": null,
  "createdAt": "2026-03-10T..."
}
```
**`parentId`**: null = top-level comment, set = reply to another comment
**`likeCount`**: Available for display. Updated on comment like/unlike (B4).
**`text` and `body`**: Both present, same value. Use `text`.

---

## Comment Like Response (B4 NEW)
```json
{
  "liked": true,
  "commentLikeCount": 4
}
```

---

## MediaObject
**Embedded in**: PostObject.media array

```json
{
  "id": "media-uuid",
  "url": "/api/media/media-uuid",
  "type": "IMAGE",
  "thumbnailUrl": null,
  "width": 1080,
  "height": 1920,
  "duration": null,
  "mimeType": "image/jpeg",
  "size": 54321
}
```
**Rule**: When `media[].id` exists, `media[].url` is ALWAYS present.
**Types**: IMAGE, VIDEO, AUDIO, null

---

## NotificationObject
```json
{
  "id": "notif-uuid",
  "userId": "recipient-uuid",
  "type": "COMMENT_LIKE",
  "actorId": "actor-uuid",
  "targetType": "COMMENT",
  "targetId": "comment-uuid",
  "message": "B4User30001 liked your comment",
  "read": false,
  "createdAt": "2026-03-10T..."
}
```
**B4 NEW types**: `COMMENT_LIKE`, `SHARE`

---

## StoryObject
```json
{
  "id": "uuid",
  "authorId": "user-uuid",
  "type": "IMAGE|VIDEO|TEXT",
  "media": { "id": "...", "url": "...", "type": "IMAGE" },
  "text": "Story text|null",
  "caption": "Caption|null",
  "background": { "type": "solid|gradient", "colors": ["#fff"] } | null,
  "stickers": [...],
  "privacy": "PUBLIC|CLOSE_FRIENDS|COLLEGE_ONLY|HOUSE_ONLY",
  "replyPrivacy": "EVERYONE|CLOSE_FRIENDS|NOBODY",
  "status": "ACTIVE|EXPIRED|ARCHIVED",
  "viewCount": 42,
  "reactionCount": 5,
  "replyCount": 3,
  "expiresAt": "ISO...",
  "archived": false,
  "createdAt": "ISO..."
}
```

---

## ReelObject (DIFFERENT from PostObject!)
```json
{
  "id": "uuid",
  "creatorId": "user-uuid",
  "caption": "Check this out!|null",
  "hashtags": ["trending"],
  "mentions": [],
  "playbackUrl": "https://...|null",
  "thumbnailUrl": "https://...|null",
  "posterFrameUrl": "https://...|null",
  "mediaStatus": "READY|UPLOADING",
  "durationMs": 15000,
  "visibility": "PUBLIC|COLLEGE_ONLY|PRIVATE",
  "status": "PUBLISHED|DRAFT|ARCHIVED|HELD",
  "likeCount": 100,
  "commentCount": 20,
  "saveCount": 10,
  "shareCount": 5,
  "viewCount": 500,
  "uniqueViewerCount": 350,
  "pinnedToProfile": false,
  "remixOf": null,
  "seriesId": null,
  "audioMeta": null,
  "syntheticDeclaration": false,
  "brandedContent": false,
  "createdAt": "ISO..."
}
```
**CRITICAL**: Reels do NOT use MediaObject. They have inline `playbackUrl`/`thumbnailUrl`.

---

## Analytics Object (B3 NEW)
Returned by: `GET /pages/:id/analytics`
```json
{
  "pageId": "uuid",
  "pageName": "Meme Lords",
  "period": "30d",
  "daysBack": 30,
  "overview": {
    "followerCount": 42,
    "memberCount": 3,
    "totalPosts": 15,
    "engagementRate": 4.5
  },
  "lifetime": {
    "totalLikes": 120,
    "totalComments": 45,
    "totalSaves": 20,
    "totalShares": 8,
    "totalViews": 500
  },
  "periodMetrics": {
    "postsCreated": 5,
    "likes": 30,
    "comments": 12,
    "saves": 5,
    "shares": 2,
    "views": 150,
    "newFollowers": 8,
    "engagementRate": 5.2
  },
  "topPosts": [ /* PostObject[] */ ],
  "postTimeline": [ /* { date: "2026-03-01", count: 2 } */ ],
  "followerTimeline": [ /* { date: "2026-03-01", count: 5 } */ ],
  "membersByRole": { "OWNER": 1, "ADMIN": 1, "EDITOR": 1 }
}
```

---

## CollegeSnippet
```json
{
  "id": "uuid",
  "officialName": "Indian Institute of Technology Delhi",
  "shortName": "IIT Delhi",
  "city": "New Delhi",
  "state": "Delhi",
  "type": "IIT",
  "membersCount": 150
}
```

## TribeSnippet
```json
{
  "id": "uuid",
  "name": "Phoenix",
  "code": "PHOENIX",
  "awardee": null,
  "color": "#FF5722",
  "membersCount": 200
}
```

---

## Summary: How to Detect What's What

```javascript
// In PostCard component:
function renderPost(post) {
  // Step 1: Is it a repost?
  if (post.isRepost) {
    return <RepostCard reposter={post.author} original={post.originalContent} />
  }

  // Step 2: Who is the author?
  if (post.authorType === 'PAGE') {
    return <PostCard author={post.author} authorName={post.author.name} linkTo={`/page/${post.author.slug}`} />
  } else {
    return <PostCard author={post.author} authorName={post.author.displayName || post.author.username} linkTo={`/profile/${post.author.id}`} />
  }
}
```
