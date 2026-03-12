# Tribe — Reels System Complete Reference

> 2,156 lines of handler code. TikTok/Instagram Reels-grade short video platform.
> Full creator tools, remix/duet, audio tracking, watch analytics.

---

## 1. Reel Lifecycle

```
Upload Video → Create Reel (DRAFT or PUBLISHED)
                    │
     ┌──────────────┼──────────────┐
     ▼              ▼              ▼
┌─────────┐  ┌───────────┐  ┌─────────┐
│  DRAFT  │  │ PUBLISHED │  │  HELD   │
└────┬────┘  └─────┬─────┘  └────┬────┘
     │ publish     │ archive     │ mod action
     ▼             ▼             ▼
┌───────────┐ ┌──────────┐ ┌─────────┐
│ PUBLISHED │ │ ARCHIVED │ │ REMOVED │
└───────────┘ └──────────┘ └─────────┘
                  │ restore
                  ▼
              PUBLISHED
```

---

## 2. Reel Creation

### Required Fields
| Field | Type | Required | Limits |
|-------|------|----------|--------|
| mediaId | string | Yes | Valid video media |
| caption | string | No | Max 2200 chars |
| hashtags | string[] | No | Max 30 |
| mentions | string[] | No | Max 20 user IDs |
| visibility | enum | No | PUBLIC, FOLLOWERS, PRIVATE |
| status | enum | No | DRAFT, PUBLISHED |
| durationMs | int | No | Max 90000 (90 seconds) |
| audioId | string | No | Audio track reference |
| remixOf | string | No | Original reel ID |
| seriesId | string | No | Reel series |
| seriesOrder | int | No | Order in series |

---

## 3. Feed Types

| Feed | Endpoint | Ranking | Description |
|------|----------|---------|-------------|
| Discovery | GET /reels/feed | Smart Ranking | All public reels |
| Following | GET /reels/following | Chronological | From followed users |
| Trending | GET /reels/trending | Viral score | Highest engagement velocity |
| Personalized | GET /reels/personalized | ML-like | User-aware ranking |
| Audio | GET /reels/audio/:id | Chronological | Reels using same audio |
| User | GET /users/:id/reels | Chronological | User's reels |

### Reel Ranking Algorithm
Same as post ranking but with:
- **Longer half-life**: 12 hours (vs 6 for posts)
- **View weight**: 0.1 per view (posts don't weight views)
- **Completion boost**: 0.8 + (completionRate × 0.4)
- **Replay detection**: Replays count as stronger engagement

---

## 4. Watch Analytics

### Events to Track
| Event | Trigger | Data |
|-------|---------|------|
| Impression | Reel appears on screen | POST /reels/:id/view |
| Watch | User scrolls away | POST /reels/:id/watch |

### Watch Event Payload
```json
{
  "watchDurationMs": 45000,
  "completionRate": 0.85,
  "isReplay": false
}
```

### How Completion Rate Affects Ranking
```
completionBoost = 0.8 + (avgCompletionRate × 0.4)

Examples:
  0% completion → 0.80 (penalty)
  50% completion → 1.00 (neutral)
  100% completion → 1.20 (20% boost)
```

---

## 5. Interactions

| Action | Endpoint | Idempotent |
|--------|----------|------------|
| Like | POST /reels/:id/like | Yes (upsert) |
| Unlike | DELETE /reels/:id/like | Yes |
| Save | POST /reels/:id/save | Yes |
| Unsave | DELETE /reels/:id/save | Yes |
| Comment | POST /reels/:id/comment | No |
| Share | POST /reels/:id/share | No (tracks) |
| Report | POST /reels/:id/report | Yes (per user) |
| Hide | POST /reels/:id/hide | Yes |
| Not Interested | POST /reels/:id/not-interested | Yes |

---

## 6. Creator Tools

### Reel Series
```
POST /api/me/reels/series → Create series
GET /api/users/:id/reels/series → View series
```
Series group related reels (tutorials, episodes).

### Creator Analytics
```
GET /api/me/reels/analytics → Summary stats
GET /api/me/reels/analytics/detailed → Per-reel breakdown
```

Returns:
```json
{
  "totalReels": 15,
  "totalViews": 45000,
  "totalLikes": 3200,
  "totalComments": 450,
  "avgCompletionRate": 0.72,
  "topReels": [ /* top 5 by views */ ]
}
```

---

## 7. Remix & Duet

### Remix
Create a new reel referencing another:
```json
{ "mediaId": "new-video", "remixOf": "original-reel-id" }
```
GET /reels/:id/remixes → All remixes of a reel

### Duet
```
POST /api/reels/:id/duet → Create duet reference
```

---

## 8. Audio System

### Popular Sounds
```
GET /api/reels/sounds/popular → Top audio tracks
GET /api/reels/audio/:audioId → Reels using this audio
```

---

## 9. Video Transcoding

After upload, trigger transcoding for HLS adaptive bitrate:

```
POST /api/transcode/:mediaId → Start transcoding
GET /api/transcode/:jobId/status → Poll progress

Output:
  360p (600kbps)
  480p (1200kbps)
  720p (2500kbps)
  1080p (5000kbps) — if source ≥ 1080p
  + Thumbnails every 2 seconds
  + HLS master playlist
```

---

## 10. Complete API Endpoints (43 total)

| # | Method | Path | Description |
|---|--------|------|-----------|
| 1 | POST | /reels | Create reel |
| 2 | GET | /reels/feed | Discovery feed |
| 3 | GET | /reels/following | Following feed |
| 4 | GET | /reels/trending | Trending feed |
| 5 | GET | /reels/personalized | Personalized feed |
| 6 | GET | /reels/:id | Reel detail |
| 7 | PATCH | /reels/:id | Edit reel |
| 8 | DELETE | /reels/:id | Delete reel |
| 9 | POST | /reels/:id/publish | Publish draft |
| 10 | POST | /reels/:id/archive | Archive |
| 11 | POST | /reels/:id/restore | Restore |
| 12 | POST | /reels/:id/pin | Pin to profile |
| 13 | DELETE | /reels/:id/pin | Unpin |
| 14 | POST | /reels/:id/like | Like |
| 15 | DELETE | /reels/:id/like | Unlike |
| 16 | POST | /reels/:id/save | Save |
| 17 | DELETE | /reels/:id/save | Unsave |
| 18 | POST | /reels/:id/comment | Comment |
| 19 | GET | /reels/:id/comments | List comments |
| 20 | POST | /reels/:id/report | Report |
| 21 | POST | /reels/:id/hide | Hide |
| 22 | POST | /reels/:id/not-interested | Not interested |
| 23 | POST | /reels/:id/share | Share |
| 24 | POST | /reels/:id/watch | Watch event |
| 25 | POST | /reels/:id/view | View event |
| 26 | GET | /reels/:id/likers | Who liked |
| 27 | GET | /reels/:id/remixes | Remixes |
| 28 | POST | /reels/:id/duet | Duet |
| 29 | GET | /reels/audio/:id | Audio reels |
| 30 | GET | /reels/sounds/popular | Popular sounds |
| 31 | GET | /users/:id/reels | User's reels |
| 32 | GET | /users/:id/reels/series | User's series |
| 33 | POST | /me/reels/series | Create series |
| 34 | GET | /me/reels/archive | Archived |
| 35 | GET | /me/reels/saved | Saved reels |
| 36 | GET | /me/reels/analytics | Analytics |
| 37 | GET | /me/reels/analytics/detailed | Detailed analytics |
| 38 | POST | /reels/:id/processing | Update processing |
| 39 | GET | /reels/:id/processing | Processing status |
| 40-43 | Admin | /admin/reels/* | Moderation, analytics |

---

*Reels System v3.0.0 — 43 endpoints*
