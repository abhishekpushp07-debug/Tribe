# 09 — Search System

## Overview

The search system provides **full-text search with autocomplete** across users, hashtags, content, reels, pages, and tribes. It uses MongoDB text indexes with weighted scoring, regex-based autocomplete, and Redis-cached results.

**Source**: `lib/handlers/search.js` (421 lines)

---

## Text Indexes

On first request, the system creates weighted text indexes:

| Collection | Fields | Weights |
|------------|--------|---------|
| `users` | `displayName`, `username`, `bio` | 10, 8, 2 |
| `content_items` | `caption`, `hashtags` | 3, 5 |
| `reels` | `caption`, `hashtags` | 3, 5 |
| `pages` | `name`, `description`, `category` | 10, 2, 5 |
| `tribes` | `tribeName`, `tribeCode` | 10, 5 |

Higher weights mean those fields contribute more to relevance ranking.

---

## API Endpoints

### Unified Search

`GET /api/search?q=<query>&type=<type>&limit=10`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | String | Yes | Search query (min 1 char) |
| `type` | String | No | Filter: `users`, `content`, `posts`, `reels`, `hashtags`, `pages`, `tribes` |
| `limit` | Number | No | Max 30, default 10 |

**Response**:
```json
{
  "query": "photography",
  "type": "all",
  "results": {
    "users": [...],
    "posts": [...],
    "reels": [...],
    "hashtags": [...],
    "pages": [...],
    "tribes": [...]
  },
  "totalResults": 42
}
```

Anonymous searches are cached in Redis. Authenticated searches are tracked in `recent_searches`.

### Autocomplete

`GET /api/search/autocomplete?q=<query>&limit=8`

Fast prefix matching using regex (`^query`). Returns suggestions from users, hashtags, and pages:

```json
{
  "suggestions": [
    { "type": "user", "id": "...", "text": "John Photography", "subtitle": "@johnphoto" },
    { "type": "hashtag", "text": "#photography", "count": 156 },
    { "type": "page", "id": "...", "text": "Photo Club", "subtitle": "ARTS" }
  ]
}
```

Cached in `CacheNS.SEARCH_AUTOCOMPLETE`.

### Type-Specific Search

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/search/users?q=&limit=20&offset=0` | Search users with follow status |
| `GET` | `/api/search/hashtags?q=&limit=20` | Search hashtags with post+reel counts |
| `GET` | `/api/search/content?q=&limit=20` | Search posts sorted by engagement |

### Hashtag Detail

`GET /api/hashtags/:tag?sort=top&limit=20`

| Parameter | Values | Description |
|-----------|--------|-------------|
| `sort` | `top` (default), `recent` | Sort by engagement or recency |

Returns:
- `totalPosts`: All-time post count for this hashtag
- `postsThisWeek`: Posts in the last 7 days
- `items`: Enriched posts with author info

### Recent Searches

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/search/recent` | Required | Get last 20 recent searches |
| `DELETE` | `/api/search/recent` | Required | Clear search history |

---

## Search Implementation Details

### User Search

Uses regex matching on `displayName`, `username`, `bio`. Excludes deactivated users. If authenticated, includes `isFollowing` status and `followerCount`.

### Hashtag Search

Uses MongoDB aggregation pipeline:
1. Match content_items with matching hashtags
2. Unwind hashtags array
3. Filter matching hashtags
4. Group by hashtag name, count posts, sum likes
5. Cross-reference with reels collection for reel counts

Returns: `{ hashtag, postCount, reelCount, totalCount, totalLikes }`

### Content Search

Matches against `caption` and `hashtags` in `content_items`. Only PUBLIC posts. Sorted by `likeCount` then `createdAt`. Enriched with author info.

### Reel Search

Matches against `caption` and `hashtags` in `reels`. Only PUBLISHED + PUBLIC. Sorted by `viewCount`. Enriched with creator info. Strips `_id` from results.

### Page Search

Matches `name` and `category` in `pages`. Excludes REMOVED pages. Strips `_id`.

### Tribe Search

Matches `tribeName` and `tribeCode` in `tribes`. Strips `_id`.

---

## Caching Strategy

| Cache Namespace | TTL | Description |
|----------------|-----|-------------|
| `CacheNS.SEARCH_RESULTS` | `CacheTTL.SEARCH_RESULTS` | Anonymous unified search |
| `CacheNS.SEARCH_AUTOCOMPLETE` | `CacheTTL.SEARCH_AUTOCOMPLETE` | Autocomplete suggestions |

Authenticated searches are NOT cached to ensure personalized follow status.

---

## Security Notes

- All regex inputs are escaped via `escapeRegex()` to prevent ReDoS
- Search queries have minimum 1 character requirement
- Type parameter is validated against whitelist
- Limit is capped at 30 (unified) or 50 (type-specific)

---

## Android Integration

```kotlin
// Autocomplete as user types
val suggestions = api.get("/api/search/autocomplete", mapOf("q" to query))

// Full search on submit
val results = api.get("/api/search", mapOf(
    "q" to query,
    "type" to "users",  // or null for all
    "limit" to "20"
))
```
