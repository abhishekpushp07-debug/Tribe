# 25 — API Quick Reference (All Endpoints)

**Version**: 3.0.0 | **Total Endpoints**: 464+ | **Base**: `/api`

All endpoints require `Content-Type: application/json`. Auth endpoints require `Authorization: Bearer <accessToken>`.

---

## Legend

| Symbol | Meaning |
|--------|---------|
| 🔓 | Public (no auth) |
| 🔑 | Auth required |
| 🛡️ | Admin/Moderator only |
| 📡 | SSE stream |
| `?cursor` | Cursor-based pagination |
| `?limit&offset` | Offset pagination |

---

## 1. Authentication & Sessions

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/auth/register` | 🔓 | Register with phone + PIN + displayName |
| `POST` | `/api/auth/login` | 🔓 | Login → accessToken + refreshToken |
| `POST` | `/api/auth/refresh` | 🔓 | Rotate refresh token → new token pair |
| `POST` | `/api/auth/logout` | 🔑 | Revoke current session |
| `GET` | `/api/auth/me` | 🔑 | Get current user profile |
| `GET` | `/api/auth/sessions` | 🔑 | List active sessions |
| `DELETE` | `/api/auth/sessions` | 🔑 | Revoke ALL sessions |
| `DELETE` | `/api/auth/sessions/:id` | 🔑 | Revoke one session by ID |
| `PATCH` | `/api/auth/pin` | 🔑 | Change PIN (re-auth, revokes other sessions) |

---

## 2. Onboarding

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `PATCH` | `/api/me/profile` | 🔑 | Update displayName, username, bio, avatar |
| `PATCH` | `/api/me/age` | 🔑 | Set birth year → age status (CHILD/ADULT) |
| `PATCH` | `/api/me/college` | 🔑 | Link/unlink college |
| `PATCH` | `/api/me/onboarding` | 🔑 | Mark onboarding complete |

---

## 3. User Profiles & Settings

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/me` | 🔑 | Own profile with stats |
| `GET` | `/api/me/stats` | 🔑 | Dashboard statistics |
| `GET` | `/api/me/activity` | 🔑 | Activity summary (`?period=7d`) |
| `GET` | `/api/me/settings` | 🔑 | All settings (privacy, notifications, profile) |
| `PATCH` | `/api/me/settings` | 🔑 | Update settings (bulk) |
| `GET` | `/api/me/privacy` | 🔑 | Privacy settings |
| `PATCH` | `/api/me/privacy` | 🔑 | Update privacy (isPrivate, allowTagging, etc.) |
| `GET` | `/api/me/interests` | 🔑 | Get interests array |
| `POST` | `/api/me/interests` | 🔑 | Set interests |
| `GET` | `/api/me/bookmarks` | 🔑 | Saved content (`?type=post\|reel`) |
| `GET` | `/api/me/login-activity` | 🔑 | Recent login sessions |
| `POST` | `/api/me/deactivate` | 🔑 | Deactivate account |
| `GET` | `/api/users/:id` | 🔓 | User profile |
| `GET` | `/api/users/:id/posts` | 🔓 | User's posts (`?kind=POST\|STORY\|REEL`) |
| `GET` | `/api/users/:id/followers` | 🔓 | Follower list |
| `GET` | `/api/users/:id/following` | 🔓 | Following list |
| `GET` | `/api/users/:id/saved` | 🔑 | Saved items (own only) |
| `GET` | `/api/users/:id/mutual-followers` | 🔑 | Mutual followers with user |

---

## 4. Content (Posts, Polls, Threads, Carousels)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/content/posts` | 🔑 | Create post/poll/thread/carousel/scheduled |
| `GET` | `/api/content/:id` | 🔓 | Get single content item |
| `PATCH` | `/api/content/:id` | 🔑 | Edit caption |
| `DELETE` | `/api/content/:id` | 🔑 | Soft delete (author or mod) |
| `GET` | `/api/content/drafts` | 🔑 | List user's drafts |
| `GET` | `/api/content/scheduled` | 🔑 | List user's scheduled posts |
| `POST` | `/api/content/:id/publish` | 🔑 | Publish a draft immediately |
| `PATCH` | `/api/content/:id/schedule` | 🔑 | Update schedule for a draft |
| `POST` | `/api/content/:id/vote` | 🔑 | Vote on a poll |
| `GET` | `/api/content/:id/poll-results` | 🔓 | Get poll results + viewer vote |
| `GET` | `/api/content/:id/thread` | 🔓 | Get full thread view |

---

## 5. Social Interactions

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/follow/:userId` | 🔑 | Follow user |
| `DELETE` | `/api/follow/:userId` | 🔑 | Unfollow user |
| `POST` | `/api/content/:id/like` | 🔑 | Like content |
| `POST` | `/api/content/:id/dislike` | 🔑 | Dislike (internal signal) |
| `DELETE` | `/api/content/:id/reaction` | 🔑 | Remove like/dislike |
| `POST` | `/api/content/:id/save` | 🔑 | Save/bookmark content |
| `DELETE` | `/api/content/:id/save` | 🔑 | Unsave content |
| `POST` | `/api/content/:id/share` | 🔑 | Repost/share content |
| `POST` | `/api/content/:id/report` | 🔑 | Report content |
| `POST` | `/api/content/:id/archive` | 🔑 | Archive own post |
| `POST` | `/api/content/:id/unarchive` | 🔑 | Restore archived post |
| `POST` | `/api/content/:id/pin` | 🔑 | Pin post to profile |
| `DELETE` | `/api/content/:id/pin` | 🔑 | Unpin post |
| `POST` | `/api/content/:id/hide` | 🔑 | Hide post from feed |
| `DELETE` | `/api/content/:id/hide` | 🔑 | Unhide post |
| `GET` | `/api/content/:id/likers` | 🔓 | Who liked a post |
| `GET` | `/api/content/:id/shares` | 🔓 | Who shared a post |

---

## 6. Comments

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/content/:id/comments` | 🔑 | Create comment |
| `GET` | `/api/content/:id/comments` | 🔓 | List comments (`?parentId=` for replies) |
| `DELETE` | `/api/content/:id/comments/:cid` | 🔑 | Delete comment |
| `PATCH` | `/api/content/:id/comments/:cid` | 🔑 | Edit comment |
| `POST` | `/api/content/:id/comments/:cid/reply` | 🔑 | Reply to comment |
| `POST` | `/api/content/:postId/comments/:cid/like` | 🔑 | Like comment |
| `DELETE` | `/api/content/:postId/comments/:cid/like` | 🔑 | Unlike comment |
| `POST` | `/api/content/:id/comments/:cid/pin` | 🔑 | Pin comment (post author) |
| `POST` | `/api/content/:id/comments/:cid/report` | 🔑 | Report comment |

---

## 7. Follow Requests (Private Accounts)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/me/follow-requests` | 🔑 | Pending requests received |
| `GET` | `/api/me/follow-requests/sent` | 🔑 | Requests you've sent |
| `GET` | `/api/me/follow-requests/count` | 🔑 | Pending count (badge) |
| `POST` | `/api/follow-requests/:id/accept` | 🔑 | Accept a follow request |
| `POST` | `/api/follow-requests/:id/reject` | 🔑 | Reject a follow request |
| `DELETE` | `/api/follow-requests/:id` | 🔑 | Cancel a sent request |
| `POST` | `/api/follow-requests/accept-all` | 🔑 | Accept all pending |

---

## 8. Blocks & Mutes

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/me/blocks/:userId` | 🔑 | Block a user |
| `DELETE` | `/api/me/blocks/:userId` | 🔑 | Unblock a user |
| `GET` | `/api/me/blocks` | 🔑 | List blocked users |

---

## 9. Feeds & Explore

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/feed` | 🔓 | Home feed (ranked) `?cursor` |
| `GET` | `/api/feed/public` | 🔓 | Public feed (ranked) `?cursor` |
| `GET` | `/api/feed/following` | 🔑 | Following feed (users + pages) `?cursor` |
| `GET` | `/api/feed/college/:collegeId` | 🔓 | College feed `?cursor` |
| `GET` | `/api/feed/tribe/:tribeId` | 🔓 | Tribe feed `?cursor` |
| `GET` | `/api/feed/stories` | 🔑 | Story rail (grouped by author) |
| `GET` | `/api/feed/reels` | 🔓 | Reels feed `?cursor` |
| `GET` | `/api/feed/mixed` | 🔓 | Posts + reels interleaved |
| `GET` | `/api/feed/personalized` | 🔑 | ML-like personalized feed `?cursor` |
| `GET` | `/api/feed/debug` | 🔑 | Algorithm debug (score breakdown) |
| `GET` | `/api/explore` | 🔓 | Explore page (trending posts + reels + hashtags) |
| `GET` | `/api/explore/creators` | 🔓 | Top/suggested creators |
| `GET` | `/api/explore/reels` | 🔓 | Trending reels `?cursor` |
| `GET` | `/api/trending/topics` | 🔓 | Trending hashtags (`?period=24h\|7d\|30d`) |

---

## 10. Search & Discovery

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/search` | 🔓 | Unified search (`?q=&type=all\|users\|posts\|pages\|hashtags\|colleges\|houses`) |
| `GET` | `/api/search/autocomplete` | 🔓 | Quick suggestions (`?q=`) |
| `GET` | `/api/search/users` | 🔓 | Search users |
| `GET` | `/api/search/hashtags` | 🔓 | Search hashtags |
| `GET` | `/api/search/content` | 🔓 | Search posts |
| `GET` | `/api/search/recent` | 🔑 | Recent searches |
| `DELETE` | `/api/search/recent` | 🔑 | Clear recent searches |
| `GET` | `/api/hashtags/trending` | 🔓 | Top hashtags by usage |
| `GET` | `/api/hashtags/:tag` | 🔓 | Hashtag detail + stats |
| `GET` | `/api/hashtags/:tag/feed` | 🔓 | Content feed for hashtag `?cursor` |

---

## 11. Stories

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/stories` | 🔑 | Create story (image/video/text + stickers) |
| `GET` | `/api/stories` | 🔑 | Story rail |
| `GET` | `/api/stories/feed` | 🔑 | Story rail with seen/unseen |
| `GET` | `/api/stories/events/stream` | 📡 | Real-time SSE for story events |
| `GET` | `/api/stories/:id` | 🔑 | View story (tracks view) |
| `DELETE` | `/api/stories/:id` | 🔑 | Delete story |
| `GET` | `/api/stories/:id/views` | 🔑 | Viewers list (owner/admin) |
| `POST` | `/api/stories/:id/react` | 🔑 | Emoji reaction |
| `DELETE` | `/api/stories/:id/react` | 🔑 | Remove reaction |
| `POST` | `/api/stories/:id/reply` | 🔑 | Reply to story |
| `GET` | `/api/stories/:id/replies` | 🔑 | Story replies (owner) |
| `POST` | `/api/stories/:id/sticker/:stickerId/respond` | 🔑 | Respond to interactive sticker |
| `GET` | `/api/stories/:id/sticker/:stickerId/results` | 🔓 | Sticker results |
| `GET` | `/api/stories/:id/sticker/:stickerId/responses` | 🔑 | All responses (owner/admin) |
| `POST` | `/api/stories/:id/report` | 🔑 | Report a story |
| `GET` | `/api/me/stories/archive` | 🔑 | Archived/expired stories |
| `GET` | `/api/users/:userId/stories` | 🔑 | User's active stories |

### Close Friends

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/me/close-friends` | 🔑 | List close friends |
| `POST` | `/api/me/close-friends/:userId` | 🔑 | Add to close friends |
| `DELETE` | `/api/me/close-friends/:userId` | 🔑 | Remove from close friends |

### Highlights

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/me/highlights` | 🔑 | Create highlight |
| `GET` | `/api/users/:userId/highlights` | 🔓 | User's highlights |
| `PATCH` | `/api/me/highlights/:id` | 🔑 | Edit highlight |
| `DELETE` | `/api/me/highlights/:id` | 🔑 | Delete highlight |

### Story Settings

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/me/story-settings` | 🔑 | Get story privacy settings |
| `PATCH` | `/api/me/story-settings` | 🔑 | Update story settings |

### Story Mutes

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/me/story-mutes` | 🔑 | List muted story authors |

### Admin Stories

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/admin/stories/analytics` | 🛡️ | Story analytics |
| `GET` | `/api/admin/stories` | 🛡️ | Moderation queue |
| `PATCH` | `/api/admin/stories/:id/moderate` | 🛡️ | Moderate a story |
| `POST` | `/api/admin/stories/:id/recompute-counters` | 🛡️ | Recompute counters |

---

## 12. Reels

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/reels` | 🔑 | Create reel (draft or publish) |
| `GET` | `/api/reels/feed` | 🔓 | Discovery feed (ranked) `?cursor` |
| `GET` | `/api/reels/following` | 🔑 | Following feed `?cursor` |
| `GET` | `/api/reels/trending` | 🔓 | Trending/viral reels `?cursor` |
| `GET` | `/api/reels/personalized` | 🔑 | Personalized feed `?cursor` |
| `GET` | `/api/reels/:id` | 🔓 | Reel detail |
| `PATCH` | `/api/reels/:id` | 🔑 | Edit reel metadata |
| `DELETE` | `/api/reels/:id` | 🔑 | Soft delete |
| `POST` | `/api/reels/:id/publish` | 🔑 | Publish a draft |
| `POST` | `/api/reels/:id/archive` | 🔑 | Archive reel |
| `POST` | `/api/reels/:id/restore` | 🔑 | Restore from archive |
| `POST` | `/api/reels/:id/pin` | 🔑 | Pin to profile |
| `DELETE` | `/api/reels/:id/pin` | 🔑 | Unpin |
| `POST` | `/api/reels/:id/like` | 🔑 | Like reel |
| `DELETE` | `/api/reels/:id/like` | 🔑 | Unlike reel |
| `POST` | `/api/reels/:id/save` | 🔑 | Save reel |
| `DELETE` | `/api/reels/:id/save` | 🔑 | Unsave reel |
| `POST` | `/api/reels/:id/comment` | 🔑 | Comment on reel |
| `GET` | `/api/reels/:id/comments` | 🔓 | List reel comments `?cursor` |
| `POST` | `/api/reels/:id/report` | 🔑 | Report reel |
| `POST` | `/api/reels/:id/hide` | 🔑 | Hide from feed |
| `POST` | `/api/reels/:id/not-interested` | 🔑 | Mark not interested |
| `POST` | `/api/reels/:id/share` | 🔑 | Track share |
| `POST` | `/api/reels/:id/watch` | 🔑 | Track watch event (duration, completion) |
| `POST` | `/api/reels/:id/view` | 🔑 | Track impression |
| `GET` | `/api/reels/:id/likers` | 🔓 | Who liked |
| `GET` | `/api/reels/:id/remixes` | 🔓 | Remixes of a reel |
| `POST` | `/api/reels/:id/duet` | 🔑 | Create duet reference |
| `GET` | `/api/reels/audio/:audioId` | 🔓 | Reels using this audio |
| `GET` | `/api/reels/sounds/popular` | 🔓 | Popular sounds |
| `GET` | `/api/users/:userId/reels` | 🔓 | Creator profile reels `?cursor` |

### Creator Tools

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/me/reels/series` | 🔑 | Create reel series |
| `GET` | `/api/me/reels/archive` | 🔑 | Archived reels |
| `GET` | `/api/me/reels/analytics` | 🔑 | Creator analytics |
| `GET` | `/api/me/reels/analytics/detailed` | 🔑 | Detailed creator analytics |
| `GET` | `/api/me/reels/saved` | 🔑 | Saved reels list |

### Reel Processing

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/reels/:id/processing` | 🛡️ | Update processing status (internal) |
| `GET` | `/api/reels/:id/processing` | 🔑 | Get processing status |

### Admin Reels

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/admin/reels` | 🛡️ | Moderation queue |
| `PATCH` | `/api/admin/reels/:id/moderate` | 🛡️ | Moderate reel |
| `GET` | `/api/admin/reels/analytics` | 🛡️ | Platform analytics |
| `POST` | `/api/admin/reels/:id/recompute-counters` | 🛡️ | Recompute counters |

---

## 13. Pages

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/pages` | 🔑 | Create page |
| `GET` | `/api/pages` | 🔓 | List/search pages `?q=&category=` |
| `GET` | `/api/pages/:idOrSlug` | 🔓 | Page detail (by ID or slug) |
| `PATCH` | `/api/pages/:id` | 🔑 | Update page |
| `DELETE` | `/api/pages/:id` | 🔑 | Delete page (owner/admin) |
| `POST` | `/api/pages/:id/archive` | 🔑 | Archive page |
| `POST` | `/api/pages/:id/restore` | 🔑 | Restore archived page |
| `GET` | `/api/pages/:id/members` | 🔓 | List page members |
| `POST` | `/api/pages/:id/members` | 🔑 | Add member |
| `PATCH` | `/api/pages/:id/members/:userId` | 🔑 | Change member role |
| `DELETE` | `/api/pages/:id/members/:userId` | 🔑 | Remove member |
| `POST` | `/api/pages/:id/transfer-ownership` | 🔑 | Transfer ownership |
| `POST` | `/api/pages/:id/follow` | 🔑 | Follow page |
| `DELETE` | `/api/pages/:id/follow` | 🔑 | Unfollow page |
| `GET` | `/api/pages/:id/followers` | 🔑 | Page followers (owner/admin) |
| `GET` | `/api/pages/:id/posts` | 🔓 | Page-authored posts `?cursor` |
| `POST` | `/api/pages/:id/posts` | 🔑 | Create post as page |
| `PATCH` | `/api/pages/:id/posts/:postId` | 🔑 | Edit page post |
| `DELETE` | `/api/pages/:id/posts/:postId` | 🔑 | Delete page post |
| `POST` | `/api/pages/:id/request-verification` | 🔑 | Request page verification |
| `POST` | `/api/pages/:id/report` | 🔑 | Report a page |
| `POST` | `/api/pages/:id/invite` | 🔑 | Invite user to page |
| `GET` | `/api/pages/:id/analytics` | 🔑 | Page analytics dashboard |
| `GET` | `/api/me/pages` | 🔑 | My managed pages |

### Admin Pages

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/admin/pages/verification-requests` | 🛡️ | Verification request queue |
| `POST` | `/api/admin/pages/verification-decide` | 🛡️ | Approve/reject verification |

---

## 14. Events

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/events` | 🔑 | Create event |
| `GET` | `/api/events/feed` | 🔓 | Discovery feed (score-ranked) `?cursor` |
| `GET` | `/api/events/search` | 🔓 | Search events (`?q=&category=&visibility=`) |
| `GET` | `/api/events/college/:collegeId` | 🔓 | College-scoped events `?cursor` |
| `GET` | `/api/events/:id` | 🔓 | Event detail |
| `PATCH` | `/api/events/:id` | 🔑 | Edit event |
| `DELETE` | `/api/events/:id` | 🔑 | Soft delete |
| `POST` | `/api/events/:id/publish` | 🔑 | Publish draft |
| `POST` | `/api/events/:id/cancel` | 🔑 | Cancel event |
| `POST` | `/api/events/:id/archive` | 🔑 | Archive past event |
| `POST` | `/api/events/:id/rsvp` | 🔑 | RSVP (`type=GOING\|INTERESTED`) |
| `DELETE` | `/api/events/:id/rsvp` | 🔑 | Cancel RSVP |
| `GET` | `/api/events/:id/attendees` | 🔓 | RSVP list (`?type=GOING\|INTERESTED`) |
| `POST` | `/api/events/:id/report` | 🔑 | Report event |
| `POST` | `/api/events/:id/remind` | 🔑 | Set reminder |
| `DELETE` | `/api/events/:id/remind` | 🔑 | Remove reminder |
| `GET` | `/api/me/events` | 🔑 | My created events |
| `GET` | `/api/me/events/rsvps` | 🔑 | Events I've RSVP'd to |

### Admin Events

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/admin/events` | 🛡️ | Moderation queue |
| `PATCH` | `/api/admin/events/:id/moderate` | 🛡️ | Moderate event |
| `GET` | `/api/admin/events/analytics` | 🛡️ | Platform analytics |
| `POST` | `/api/admin/events/:id/recompute-counters` | 🛡️ | Recompute counters |

---

## 15. Tribes & Houses

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/tribes` | 🔓 | List all 21 tribes |
| `GET` | `/api/tribes/leaderboard` | 🔓 | Engagement-ranked leaderboard |
| `GET` | `/api/tribes/standings/current` | 🔓 | Current season standings |
| `GET` | `/api/tribes/:id` | 🔓 | Tribe detail |
| `GET` | `/api/tribes/:id/members` | 🔓 | Tribe members `?limit&offset` |
| `GET` | `/api/tribes/:id/board` | 🔓 | Tribe board governance |
| `GET` | `/api/tribes/:id/fund` | 🔓 | Tribe fund info |
| `GET` | `/api/tribes/:id/salutes` | 🔓 | Salute history `?cursor` |
| `GET` | `/api/tribes/:id/feed` | 🔓 | Tribe content feed `?cursor` |
| `GET` | `/api/tribes/:id/events` | 🔓 | Tribe events `?cursor` |
| `GET` | `/api/tribes/:id/stats` | 🔓 | Tribe statistics |
| `POST` | `/api/tribes/:id/join` | 🔑 | Join a tribe |
| `POST` | `/api/tribes/:id/leave` | 🔑 | Leave a tribe |
| `POST` | `/api/tribes/:id/cheer` | 🔑 | Cheer for tribe |
| `GET` | `/api/me/tribe` | 🔑 | My tribe info |
| `GET` | `/api/users/:id/tribe` | 🔓 | Another user's tribe |

### Legacy Houses

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/houses` | 🔓 | List houses |
| `GET` | `/api/houses/leaderboard` | 🔓 | House leaderboard |
| `GET` | `/api/houses/:idOrSlug` | 🔓 | House detail |
| `GET` | `/api/houses/:idOrSlug/members` | 🔓 | House members |

### Admin Tribes

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/admin/tribes/distribution` | 🛡️ | Distribution stats |
| `POST` | `/api/admin/tribes/reassign` | 🛡️ | Reassign user to tribe |
| `POST` | `/api/admin/tribes/migrate` | 🛡️ | Migrate house → tribe |
| `POST` | `/api/admin/tribes/boards` | 🛡️ | Create/update tribe board |
| `POST` | `/api/admin/tribe-seasons` | 🛡️ | Create/manage season |
| `GET` | `/api/admin/tribe-seasons` | 🛡️ | List seasons |
| `POST` | `/api/admin/tribe-salutes/adjust` | 🛡️ | Manual salute adjustment |
| `POST` | `/api/admin/tribe-awards/resolve` | 🛡️ | Resolve annual award |

---

## 16. Tribe Contests

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/tribe-contests` | 🔓 | List contests `?status=&contest_type=&season_id=` |
| `GET` | `/api/tribe-contests/:id` | 🔓 | Contest detail |
| `POST` | `/api/tribe-contests/:id/enter` | 🔑 | Submit entry |
| `GET` | `/api/tribe-contests/:id/entries` | 🔓 | List entries `?page&limit` |
| `GET` | `/api/tribe-contests/:id/leaderboard` | 🔓 | Contest leaderboard |
| `GET` | `/api/tribe-contests/:id/results` | 🔓 | Official results |
| `POST` | `/api/tribe-contests/:id/vote` | 🔑 | Vote on entry |
| `POST` | `/api/tribe-contests/:id/withdraw` | 🔑 | Withdraw own entry |
| `GET` | `/api/tribe-contests/seasons` | 🔓 | List seasons |
| `GET` | `/api/tribe-contests/seasons/:id/standings` | 🔓 | Season standings |

### Contest SSE Streams

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/tribe-contests/live-feed` | 📡 | Global contest activity |
| `GET` | `/api/tribe-contests/:id/live` | 📡 | Live contest scoreboard |
| `GET` | `/api/tribe-contests/seasons/:id/live-standings` | 📡 | Live season standings |

### Admin Contests

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/admin/tribe-contests` | 🛡️ | Create contest |
| `GET` | `/api/admin/tribe-contests` | 🛡️ | List all contests |
| `GET` | `/api/admin/tribe-contests/:id` | 🛡️ | Admin contest detail |
| `POST` | `/api/admin/tribe-contests/:id/publish` | 🛡️ | DRAFT → PUBLISHED |
| `POST` | `/api/admin/tribe-contests/:id/open-entries` | 🛡️ | PUBLISHED → ENTRY_OPEN |
| `POST` | `/api/admin/tribe-contests/:id/close-entries` | 🛡️ | ENTRY_OPEN → ENTRY_CLOSED |
| `POST` | `/api/admin/tribe-contests/:id/lock` | 🛡️ | EVALUATING → LOCKED |
| `POST` | `/api/admin/tribe-contests/:id/resolve` | 🛡️ | LOCKED → RESOLVED |
| `POST` | `/api/admin/tribe-contests/:id/disqualify` | 🛡️ | Disqualify an entry |
| `POST` | `/api/admin/tribe-contests/:id/judge-score` | 🛡️ | Submit judge score |
| `POST` | `/api/admin/tribe-contests/:id/compute-scores` | 🛡️ | Compute/recompute scores |
| `POST` | `/api/admin/tribe-contests/:id/recompute-broadcast` | 🛡️ | Compute + broadcast rank changes |
| `POST` | `/api/admin/tribe-contests/:id/cancel` | 🛡️ | Cancel contest |
| `POST` | `/api/admin/tribe-contests/rules` | 🛡️ | Add versioned rule |
| `POST` | `/api/admin/tribe-salutes/adjust` | 🛡️ | Manual salute (contest module) |
| `GET` | `/api/admin/tribe-contests/dashboard` | 🛡️ | Contest dashboard stats |

---

## 17. Media Upload & Storage

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/media/upload-init` | 🔑 | Get signed URL for direct-to-Supabase upload |
| `POST` | `/api/media/initiate` | 🔑 | Alias for upload-init |
| `POST` | `/api/media/upload-complete` | 🔑 | Finalize upload after client uploads |
| `POST` | `/api/media/complete` | 🔑 | Alias for upload-complete |
| `GET` | `/api/media/upload-status/:mediaId` | 🔑 | Check upload/thumbnail status |
| `POST` | `/api/media/upload` | 🔑 | Legacy base64 upload |
| `GET` | `/api/media/:id` | 🔓 | Serve media (redirect to CDN or stream) |
| `DELETE` | `/api/media/:id` | 🔑 | Delete owned media (with attachment safety) |

### Transcoding

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/transcode/:mediaId` | 🔑 | Trigger HLS transcoding |
| `GET` | `/api/transcode/:jobId/status` | 🔑 | Check transcode job status |
| `GET` | `/api/transcode/media/:mediaId` | 🔑 | Get transcode info for media |
| `GET` | `/api/media/:id/stream` | 🔓 | Get HLS master playlist info |
| `GET` | `/api/media/:id/thumbnails` | 🔓 | Get thumbnails for media |

### Admin Media

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/admin/media` | 🛡️ | Media cleanup queue |

---

## 18. Notifications

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/notifications` | 🔑 | List notifications (`?grouped=true`) `?cursor` |
| `PATCH` | `/api/notifications/read` | 🔑 | Mark read (specific IDs or all) |
| `POST` | `/api/notifications/read-all` | 🔑 | Mark all as read |
| `GET` | `/api/notifications/unread-count` | 🔑 | Lightweight unread count |
| `POST` | `/api/notifications/register-device` | 🔑 | Register push device token |
| `DELETE` | `/api/notifications/unregister-device` | 🔑 | Deactivate device token |
| `GET` | `/api/notifications/preferences` | 🔑 | Get notification preferences |
| `PATCH` | `/api/notifications/preferences` | 🔑 | Update preferences |
| `DELETE` | `/api/notifications/clear` | 🔑 | Clear all notifications |

---

## 19. Analytics

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/analytics/track` | 🔑 | Track impression/view/profile-visit |
| `GET` | `/api/analytics/overview` | 🔑 | Overall account analytics |
| `GET` | `/api/analytics/content` | 🔑 | Content performance analytics |
| `GET` | `/api/analytics/content/:id` | 🔑 | Single content deep analytics |
| `GET` | `/api/analytics/audience` | 🔑 | Audience demographics & growth |
| `GET` | `/api/analytics/reach` | 🔑 | Reach & impressions time series |
| `GET` | `/api/analytics/stories` | 🔑 | Story performance analytics |
| `GET` | `/api/analytics/profile-visits` | 🔑 | Profile visit details |
| `GET` | `/api/analytics/reels` | 🔑 | Reel performance analytics |

---

## 20. Board Notices

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/board/notices` | 🔑 | Create notice (board member) |
| `GET` | `/api/board/notices/:id` | 🔓 | Notice detail |
| `PATCH` | `/api/board/notices/:id` | 🔑 | Edit notice |
| `DELETE` | `/api/board/notices/:id` | 🔑 | Delete notice |
| `POST` | `/api/board/notices/:id/pin` | 🔑 | Pin notice |
| `DELETE` | `/api/board/notices/:id/pin` | 🔑 | Unpin notice |
| `POST` | `/api/board/notices/:id/acknowledge` | 🔑 | Acknowledge notice |
| `GET` | `/api/board/notices/:id/acknowledgments` | 🔑 | Acknowledgment list |
| `GET` | `/api/colleges/:id/notices` | 🔓 | Public college notices |
| `GET` | `/api/me/board/notices` | 🔑 | My created notices |

### Admin Board Notices

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/moderation/board-notices` | 🛡️ | Moderator review queue |
| `POST` | `/api/moderation/board-notices/:id/decide` | 🛡️ | Approve/reject notice |

---

## 21. Authenticity Tags

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/authenticity/tag` | 🔑 | Tag content (board member/mod) |
| `GET` | `/api/authenticity/tags/:targetType/:targetId` | 🔓 | Get tags for entity |

---

## 22. College Discovery & Claims

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/colleges/search` | 🔓 | Search colleges (`?q=&state=&type=`) |
| `GET` | `/api/colleges/states` | 🔓 | All states |
| `GET` | `/api/colleges/types` | 🔓 | All college types |
| `GET` | `/api/colleges/:id` | 🔓 | College detail |
| `GET` | `/api/colleges/:id/members` | 🔓 | College members |
| `POST` | `/api/colleges/:id/claim` | 🔑 | Submit college claim |
| `GET` | `/api/me/college-claims` | 🔑 | My claims |
| `DELETE` | `/api/me/college-claims/:id` | 🔑 | Withdraw pending claim |

### Admin College Claims

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/admin/college-claims` | 🛡️ | Review queue |
| `GET` | `/api/admin/college-claims/:id` | 🛡️ | Claim detail |
| `PATCH` | `/api/admin/college-claims/:id/flag-fraud` | 🛡️ | Move to FRAUD_REVIEW |
| `PATCH` | `/api/admin/college-claims/:id/decide` | 🛡️ | Approve/reject |

---

## 23. Governance (College Board)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/governance/college/:collegeId/board` | 🔓 | Current board |
| `POST` | `/api/governance/college/:collegeId/apply` | 🔑 | Apply for board seat |
| `GET` | `/api/governance/college/:collegeId/applications` | 🔓 | Pending applications |
| `POST` | `/api/governance/applications/:appId/vote` | 🔑 | Vote on application |
| `POST` | `/api/governance/college/:collegeId/proposals` | 🔑 | Create proposal |
| `GET` | `/api/governance/college/:collegeId/proposals` | 🔓 | List proposals |
| `POST` | `/api/governance/proposals/:proposalId/vote` | 🔑 | Vote on proposal |
| `POST` | `/api/governance/college/:collegeId/seed-board` | 🛡️ | Seed initial board |

---

## 24. Resources (Study Materials)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/resources` | 🔑 | Create resource |
| `GET` | `/api/resources/search` | 🔓 | Faceted search (`?q=&category=&college=`) |
| `GET` | `/api/resources/:id` | 🔓 | Resource detail |
| `PATCH` | `/api/resources/:id` | 🔑 | Update resource (owner) |
| `DELETE` | `/api/resources/:id` | 🔑 | Soft remove (owner/mod) |
| `POST` | `/api/resources/:id/report` | 🔑 | Report resource |
| `POST` | `/api/resources/:id/vote` | 🔑 | Upvote/downvote |
| `DELETE` | `/api/resources/:id/vote` | 🔑 | Remove vote |
| `POST` | `/api/resources/:id/download` | 🔑 | Track download |
| `GET` | `/api/me/resources` | 🔑 | My uploads |

### Admin Resources

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/admin/resources` | 🛡️ | Review queue |
| `PATCH` | `/api/admin/resources/:id/moderate` | 🛡️ | Approve/Hold/Remove |
| `POST` | `/api/admin/resources/:id/recompute-counters` | 🛡️ | Recompute counters |
| `POST` | `/api/admin/resources/reconcile` | 🛡️ | Bulk reconciliation |

---

## 25. Content Distribution Pipeline

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/admin/distribution/evaluate` | 🛡️ | Batch evaluate Stage 0/1 content |
| `POST` | `/api/admin/distribution/evaluate/:contentId` | 🛡️ | Single content evaluate |
| `GET` | `/api/admin/distribution/config` | 🛡️ | View distribution rules |
| `POST` | `/api/admin/distribution/kill-switch` | 🛡️ | Toggle auto-evaluation |
| `GET` | `/api/admin/distribution/inspect/:contentId` | 🛡️ | Distribution detail for content |
| `POST` | `/api/admin/distribution/override` | 🛡️ | Manual stage override |
| `DELETE` | `/api/admin/distribution/override/:contentId` | 🛡️ | Remove override |

---

## 26. Content Quality Scoring

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/quality/score` | 🔑 | Score a single post |
| `POST` | `/api/quality/batch` | 🛡️ | Batch score unscored content |
| `GET` | `/api/quality/dashboard` | 🛡️ | Quality overview dashboard |
| `GET` | `/api/quality/check/:contentId` | 🔑 | Check quality score |

---

## 27. Recommendations

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/recommendations/posts` | 🔑 | Suggested posts for you |
| `GET` | `/api/recommendations/reels` | 🔑 | Reels you may like |
| `GET` | `/api/recommendations/creators` | 🔑 | Creators for you |

---

## 28. Smart Suggestions

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/suggestions/people` | 🔑 | People you may know |
| `GET` | `/api/suggestions/trending` | 🔑 | Trending in your college |
| `GET` | `/api/suggestions/tribes` | 🔑 | Tribes for you |
| `GET` | `/api/suggestions/users` | 🔑 | User suggestions (legacy) |

---

## 29. Activity Status

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/activity/heartbeat` | 🔑 | Update "last seen" |
| `GET` | `/api/activity/status/:userId` | 🔑 | User's activity status |
| `GET` | `/api/activity/friends` | 🔑 | Activity status of followed users |
| `PUT` | `/api/activity/settings` | 🔑 | Toggle activity visibility |

---

## 30. Reports, Moderation & Appeals

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/reports` | 🔑 | Submit report |
| `GET` | `/api/moderation/queue` | 🛡️ | Moderation queue |
| `POST` | `/api/moderation/:contentId/action` | 🛡️ | Take moderation action |
| `GET` | `/api/moderation/config` | 🛡️ | Moderation config |
| `POST` | `/api/moderation/check` | 🛡️ | Run moderation check |
| `POST` | `/api/appeals` | 🔑 | Submit appeal |
| `GET` | `/api/appeals` | 🔑 | My appeals |
| `PATCH` | `/api/appeals/:id/decide` | 🛡️ | Decide on appeal |

---

## 31. Legal & Consent

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/legal/consent` | 🔑 | Get consent info |
| `POST` | `/api/legal/accept` | 🔑 | Accept consent |

---

## 32. Grievances

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/grievances` | 🔑 | Submit grievance |
| `GET` | `/api/grievances` | 🔑 | My grievances |

---

## 33. Admin & Ops

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/admin/colleges/seed` | 🛡️ | Seed college data |
| `GET` | `/api/admin/stats` | 🛡️ | Platform stats |
| `GET` | `/api/admin/abuse-dashboard` | 🛡️ | Abuse overview |
| `GET` | `/api/admin/abuse-log` | 🛡️ | Detailed abuse log |

---

## 34. Health & Observability

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/healthz` | 🔓 | Liveness probe |
| `GET` | `/api/readyz` | 🔓 | Readiness probe |
| `GET` | `/api/ops/health` | 🛡️ | Deep health check |
| `GET` | `/api/ops/metrics` | 🛡️ | Application metrics |
| `GET` | `/api/ops/slis` | 🛡️ | SLI metrics |
| `GET` | `/api/ops/backup-check` | 🛡️ | Backup readiness |
| `GET` | `/api/cache/stats` | 🛡️ | Redis cache stats |
| `GET` | `/api/` | 🔓 | API root info |

---

## Pagination Patterns

### Cursor-Based (Feeds, Lists)
```
GET /api/feed/public?limit=20&cursor=2026-03-01T00:00:00.000Z

Response:
{
  "items": [...],
  "pagination": {
    "nextCursor": "2026-02-28T23:00:00.000Z",
    "hasMore": true
  }
}
```

### Offset-Based (Search, Members)
```
GET /api/colleges/search?q=delhi&limit=20&offset=0

Response:
{
  "items": [...],
  "pagination": {
    "total": 150,
    "limit": 20,
    "offset": 0,
    "hasMore": true
  }
}
```

---

## Authentication Flow

```
1. Register:  POST /api/auth/register → { accessToken, refreshToken }
2. Login:     POST /api/auth/login    → { accessToken, refreshToken }
3. Use:       Authorization: Bearer <accessToken>
4. Refresh:   POST /api/auth/refresh  → { accessToken, refreshToken }
5. Logout:    POST /api/auth/logout
```

---

## Error Response Format

```json
{
  "error": "Human-readable message",
  "code": "MACHINE_READABLE_CODE"
}
```

### Common Error Codes

| Code | HTTP | Meaning |
|------|------|---------|
| `VALIDATION` | 400 | Bad input |
| `UNAUTHORIZED` | 401 | Missing/invalid token |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Duplicate action |
| `EXPIRED` | 410 | Story/poll expired |
| `PAYLOAD_TOO_LARGE` | 413 | File too big |
| `CONTENT_REJECTED` | 422 | Content moderation rejection |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

---

## Rate Limiting

Tiered by endpoint sensitivity. Headers on 429 response:
```
Retry-After: <seconds>
```

| Tier | Window | Limit | Applies To |
|------|--------|-------|------------|
| AUTH | 15 min | 10 | Login, register |
| WRITE | 1 min | 30 | Create/update/delete |
| READ | 1 min | 120 | Feeds, profiles |
| SEARCH | 1 min | 60 | Search, autocomplete |
| MEDIA | 1 hour | 50 | Upload |

---

## Media Upload Flow (Supabase)

```
1. POST /api/media/upload-init
   Body: { kind: "image", mimeType: "image/jpeg", sizeBytes: 204800 }
   → { mediaId, uploadUrl, token, publicUrl }

2. PUT <uploadUrl> (direct upload to Supabase — NOT through API)
   Headers: Content-Type: image/jpeg

3. POST /api/media/upload-complete
   Body: { mediaId, width: 1080, height: 1080 }
   → { id, url, publicUrl, status: "READY" }

4. POST /api/content/posts
   Body: { caption: "Hello!", mediaIds: ["<mediaId>"] }
```

---

## SSE Streams

All SSE streams accept `token` as query param for EventSource authentication:

```javascript
const eventSource = new EventSource(
  '/api/stories/events/stream?token=<accessToken>'
);
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Handle: story.created, story.viewed, story.reacted, etc.
};
```

### Available Streams

| Stream | Endpoint | Events |
|--------|----------|--------|
| Stories | `/api/stories/events/stream` | `story.created`, `story.viewed`, `story.reacted`, `story.expired` |
| Contest Live | `/api/tribe-contests/:id/live` | `entry.submitted`, `vote.cast`, `score.updated` |
| Contest Global | `/api/tribe-contests/live-feed` | All contest activity |
| Season Standings | `/api/tribe-contests/seasons/:id/live-standings` | Rank changes |

---

*Last updated: Feb 2026 — Generated from source code at `/app/app/api/[[...path]]/route.js` and `/app/lib/handlers/`*
