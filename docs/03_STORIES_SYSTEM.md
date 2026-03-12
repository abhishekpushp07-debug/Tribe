# Tribe — Stories System Complete Reference

> 2,017 lines of handler code + 479 lines of service code = complete stories system.
> 10 sticker types, privacy controls, close friends, highlights, SSE events.

---

## 1. Story Lifecycle

```
Create Story
    │
    ▼
┌─────────┐    24 hours    ┌─────────┐
│  ACTIVE  │──────────────>│ EXPIRED │
└─────────┘                └─────────┘
    │                          │
    │ admin moderate           │ auto-archive
    ▼                          ▼
┌─────────┐              ┌──────────┐
│ REMOVED │              │ ARCHIVED │
└─────────┘              └──────────┘
    │ user delete
    ▼
  Soft Delete (isDeleted=true)
```

---

## 2. Story Types

### IMAGE Story
```json
{
  "mediaId": "media-uuid",
  "type": "IMAGE",
  "caption": "Beautiful sunset",
  "stickers": [...]
}
```

### VIDEO Story
```json
{
  "mediaId": "video-uuid",
  "type": "VIDEO",
  "caption": "Check this out"
}
```

### TEXT Story
```json
{
  "type": "TEXT",
  "textContent": "Feeling amazing today!",
  "backgroundColor": "#FF6B35",
  "backgroundType": "SOLID",
  "fontStyle": "serif"
}
```

---

## 3. Interactive Stickers (10 Types)

### Poll Sticker
```json
{
  "type": "POLL",
  "question": "Coffee or Tea?",
  "options": ["Coffee", "Tea"],
  "position": { "x": 0.5, "y": 0.6 }
}
```
**User responds**: `{ "optionIndex": 0 }`
**Results**: `{ totalVotes, options: [{ text, votes, percentage }] }`

### Quiz Sticker
```json
{
  "type": "QUIZ",
  "question": "Capital of India?",
  "options": ["Mumbai", "Delhi", "Kolkata"],
  "correctIndex": 1
}
```
**User responds**: `{ "optionIndex": 1 }`
**Response includes**: `{ correct: true }`
**Results**: `{ totalAnswers, correctCount, correctPercentage, options }`

### Question Sticker
```json
{
  "type": "QUESTION",
  "question": "Ask me anything!",
  "placeholder": "Type your answer..."
}
```
**User responds**: `{ "text": "What's your favorite food?" }`

### Emoji Slider
```json
{
  "type": "EMOJI_SLIDER",
  "question": "Rate this!",
  "emoji": "🔥"
}
```
**User responds**: `{ "value": 0.85 }` (0.0 to 1.0)
**Results**: `{ totalResponses, averageValue, emoji }`

### Mention Sticker
```json
{ "type": "MENTION", "userId": "user-uuid", "username": "aarav.21" }
```

### Location Sticker
```json
{ "type": "LOCATION", "locationName": "IIT Delhi", "lat": 28.5456, "lng": 77.1926 }
```

### Hashtag Sticker
```json
{ "type": "HASHTAG", "tag": "#placement" }
```

### Link Sticker
```json
{ "type": "LINK", "url": "https://example.com", "label": "Visit" }
```

### Countdown Sticker
```json
{ "type": "COUNTDOWN", "title": "New Year!", "endTime": "2026-01-01T00:00:00Z" }
```

### Music Sticker
```json
{ "type": "MUSIC", "trackName": "Song", "artist": "Artist", "previewUrl": "..." }
```

---

## 4. Privacy System

### Three Privacy Levels
| Level | Who Can See |
|-------|------------|
| EVERYONE | All non-blocked users |
| FOLLOWERS | Approved followers only |
| CLOSE_FRIENDS | Close friends list only |

### Additional Privacy Controls
- `hideStoryFrom`: Per-author list of excluded users
- `story_mutes`: Viewer-side muting (hides stories from muted users)
- `allowReplies`: EVERYONE / FOLLOWERS / CLOSE_FRIENDS / OFF
- `allowSharing`: true/false

### Privacy Check Order
```
1. Is story ACTIVE and not expired? → If no: 410 EXPIRED
2. Is viewer blocked by author? → If yes: 404 NOT_FOUND
3. Is viewer in hideStoryFrom? → If yes: 404 NOT_FOUND
4. Check privacy level:
   - EVERYONE → allowed
   - FOLLOWERS → check follows collection
   - CLOSE_FRIENDS → check close_friends collection
```

---

## 5. Close Friends System

### Limits
- Max 500 close friends per user
- Adding is one-way (no notification to the friend)
- Close friends stories show GREEN ring in UI (vs GRADIENT for normal)

### API Flow
```
POST /api/me/close-friends/:userId  → Add
DELETE /api/me/close-friends/:userId → Remove
GET /api/me/close-friends → List all
```

---

## 6. Highlights System

### Lifecycle
```
Story expires → Moves to archive
User creates highlight → Selects archived stories
Highlight appears on profile → Permanent (doesn't expire)
```

### Limits
- Max 50 highlights per user
- Max 100 stories per highlight
- A story can exist in multiple highlights
- Highlight survives story deletion (keeps reference)

### API Flow
```
POST /api/me/highlights → Create
GET /api/users/:id/highlights → View user's highlights
PATCH /api/me/highlights/:id → Edit (title, cover, add/remove stories)
DELETE /api/me/highlights/:id → Delete
```

---

## 7. Story Rail Construction

The story rail (horizontal scroll at top of feed) is built as follows:

```
1. Fetch ALL active stories (not expired)
2. Filter out:
   - Blocked users (both directions)
   - Muted users (story_mutes)
   - hideStoryFrom exclusions
   - Privacy checks (FOLLOWERS, CLOSE_FRIENDS)
3. Group by author
4. Check seen/unseen for each story
5. Sort authors:
   a. Own stories FIRST
   b. Unseen stories before seen
   c. Within each group: by latestAt descending
6. Return grouped rail
```

### Rail Response Shape
```json
[
  {
    "author": { "id": "...", "displayName": "...", "avatarMediaId": "..." },
    "stories": [
      { "id": "...", "type": "IMAGE", "mediaUrl": "...", "seen": false, "expiresAt": "..." }
    ],
    "hasUnseen": true,
    "latestAt": "2025-01-15T10:00:00Z",
    "storyCount": 3
  }
]
```

---

## 8. View Tracking

### Deduplication
- Same viewer counted ONCE per story (unique index: storyId + viewerId)
- View tracking is automatic on GET /stories/:id
- Can also explicitly mark: POST /stories/:id/view

### View Duration
- POST /stories/:id/view-duration with `{ durationMs }` 
- Used for analytics (average view time per story)

### View Analytics (Owner Only)
- GET /stories/:id/view-analytics
- Shows duration distribution, peak view times

---

## 9. Reactions (6 Emojis)

Fixed set: `❤️` `🔥` `😂` `😮` `😢` `👏`

```
POST /api/stories/:id/react → { emoji: "🔥" }
DELETE /api/stories/:id/react → Remove reaction
```

- One reaction per user per story
- Changing emoji replaces previous reaction
- Owner sees all reactions in viewer list

---

## 10. Replies

```
POST /api/stories/:id/reply → { text: "Amazing!" }
GET /api/stories/:id/replies → Owner only
```

- Subject to replyPrivacy setting
- Max 1000 characters
- Only story owner can see replies

---

## 11. SSE Real-Time Events

```
GET /api/stories/events/stream?token={accessToken}

Events:
- story.viewed → { storyId, viewerId, viewedAt }
- story.reacted → { storyId, userId, emoji }
- story.replied → { storyId, userId, text }
- story.sticker_responded → { storyId, stickerId, userId }
- story.expired → { storyId }

Heartbeat every 15 seconds:
: heartbeat 2025-01-15T10:30:00.000Z

Auto-reconnect hint:
retry: 3000
```

---

## 12. Admin Controls

| Endpoint | Purpose |
|----------|---------|
| GET /admin/stories | Moderation queue |
| GET /admin/stories/analytics | Platform story analytics |
| PATCH /admin/stories/:id/moderate | Moderate (approve/remove/hold) |
| POST /admin/stories/:id/recompute-counters | Fix counter drift |
| POST /admin/stories/cleanup | Manual expiry trigger |
| POST /admin/stories/bulk-moderate | Batch moderate |

---

## 13. Expiry Worker

Background worker runs every 30 minutes:
1. Find all stories where `status=ACTIVE` and `expiresAt <= now`
2. For each: set `status=EXPIRED`
3. If user has `autoArchive=true` (default): set `archived=true`
4. Publish `story.expired` SSE event per author

---

## 14. Complete API Endpoints (39 total)

| # | Method | Path | Auth | Description |
|---|--------|------|------|-----------|
| 1 | POST | /stories | Auth | Create story |
| 2 | GET | /stories | Auth | Story rail |
| 3 | GET | /stories/feed | Auth | Story rail |
| 4 | GET | /stories/:id | Auth | View story |
| 5 | DELETE | /stories/:id | Auth | Delete story |
| 6 | PATCH | /stories/:id | Auth | Edit story |
| 7 | GET | /stories/:id/views | Auth | Viewer list |
| 8 | POST | /stories/:id/view | Auth | Mark viewed |
| 9 | POST | /stories/:id/view-duration | Auth | Track duration |
| 10 | GET | /stories/:id/view-analytics | Auth | Duration analytics |
| 11 | POST | /stories/:id/react | Auth | Emoji reaction |
| 12 | DELETE | /stories/:id/react | Auth | Remove reaction |
| 13 | POST | /stories/:id/reply | Auth | Reply |
| 14 | GET | /stories/:id/replies | Auth | List replies |
| 15 | POST | /stories/:id/sticker/:stickerId/respond | Auth | Respond to sticker |
| 16 | GET | /stories/:id/sticker/:stickerId/results | Auth | Sticker results |
| 17 | GET | /stories/:id/sticker/:stickerId/responses | Auth | Individual responses |
| 18 | POST | /stories/:id/report | Auth | Report story |
| 19 | POST | /stories/:id/share | Auth | Share as post |
| 20 | GET | /users/:id/stories | Auth | User's stories |
| 21 | GET | /me/stories/archive | Auth | My archive |
| 22 | GET | /me/stories/insights | Auth | My insights |
| 23 | GET | /me/story-settings | Auth | Settings |
| 24 | PATCH | /me/story-settings | Auth | Update settings |
| 25 | GET | /me/close-friends | Auth | Close friends list |
| 26 | POST | /me/close-friends/:userId | Auth | Add close friend |
| 27 | DELETE | /me/close-friends/:userId | Auth | Remove close friend |
| 28 | POST | /me/highlights | Auth | Create highlight |
| 29 | PATCH | /me/highlights/:id | Auth | Edit highlight |
| 30 | DELETE | /me/highlights/:id | Auth | Delete highlight |
| 31 | GET | /users/:id/highlights | Optional | User's highlights |
| 32 | POST | /me/story-mutes/:userId | Auth | Mute stories |
| 33 | DELETE | /me/story-mutes/:userId | Auth | Unmute stories |
| 34 | GET | /me/story-mutes | Auth | Muted list |
| 35 | POST | /me/blocks/:userId | Auth | Block user |
| 36 | DELETE | /me/blocks/:userId | Auth | Unblock user |
| 37 | GET | /me/blocks | Auth | Blocked list |
| 38 | GET | /stories/events/stream | Auth | SSE stream |
| 39 | Admin endpoints (6) | various | Admin | See section 12 |

---

*Stories System v3.0.0 — 39 endpoints, 10 sticker types, SSE real-time*
