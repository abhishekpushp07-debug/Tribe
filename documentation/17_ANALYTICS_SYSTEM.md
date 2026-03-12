# 17 — Analytics System

**Source**: `/app/lib/handlers/analytics.js`

---

## 1. Overview

Creator-facing analytics with 9 endpoints covering account overview, content performance, audience demographics, reach metrics, story analytics, profile visits, and reel analytics.

---

## 2. Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/analytics/track` | 🔑 | Track impression/view/profile-visit |
| `GET` | `/api/analytics/overview` | 🔑 | Overall account analytics |
| `GET` | `/api/analytics/content` | 🔑 | Content performance |
| `GET` | `/api/analytics/content/:id` | 🔑 | Single content deep analytics |
| `GET` | `/api/analytics/audience` | 🔑 | Audience demographics & growth |
| `GET` | `/api/analytics/reach` | 🔑 | Reach & impressions time series |
| `GET` | `/api/analytics/stories` | 🔑 | Story performance |
| `GET` | `/api/analytics/profile-visits` | 🔑 | Profile visit details |
| `GET` | `/api/analytics/reels` | 🔑 | Reel performance |

---

## 3. Event Tracking

`POST /api/analytics/track`

```json
{
  "eventType": "IMPRESSION | VIEW | PROFILE_VISIT | LINK_CLICK",
  "targetType": "POST | REEL | STORY | PROFILE | PAGE",
  "targetId": "content-uuid",
  "metadata": {
    "source": "feed | explore | profile | search",
    "duration": 5.2
  }
}
```

Stored in `analytics_events` collection with user ID, timestamp, and metadata.

---

## 4. Overview Analytics

`GET /api/analytics/overview?period=7d`

Returns:
```json
{
  "period": "7d",
  "accounts": {
    "reached": 1250,
    "engaged": 340,
    "profileVisits": 89,
    "newFollowers": 23,
    "unfollows": 3
  },
  "content": {
    "totalPosts": 12,
    "totalReels": 3,
    "totalStories": 8,
    "totalEngagement": 890,
    "avgEngagementRate": 4.2
  },
  "topPerformingPost": { ... },
  "growthTrend": "GROWING | STABLE | DECLINING"
}
```

---

## 5. Content Analytics

`GET /api/analytics/content?period=30d&sort=engagement`

Returns paginated list of content with performance metrics:
```json
{
  "items": [
    {
      "contentId": "...",
      "kind": "POST",
      "caption": "...",
      "metrics": {
        "impressions": 5400,
        "reach": 3200,
        "likes": 120,
        "comments": 45,
        "saves": 23,
        "shares": 8,
        "engagementRate": 3.6
      },
      "createdAt": "..."
    }
  ]
}
```

### Single Content Deep Analytics

`GET /api/analytics/content/:id`

Returns detailed breakdown:
```json
{
  "content": { ... },
  "metrics": {
    "impressions": 5400,
    "reach": 3200,
    "uniqueViews": 2800,
    "likes": 120,
    "comments": 45,
    "saves": 23,
    "shares": 8,
    "engagementRate": 3.6,
    "clickThroughRate": 1.2
  },
  "audience": {
    "topColleges": [...],
    "topTribes": [...]
  },
  "timeline": {
    "hourly": [{ "hour": 0, "impressions": 12, "engagement": 3 }, ...]
  }
}
```

---

## 6. Audience Analytics

`GET /api/analytics/audience?period=30d`

```json
{
  "followers": {
    "total": 2400,
    "gained": 145,
    "lost": 12,
    "netGrowth": 133,
    "growthRate": 5.8
  },
  "demographics": {
    "colleges": [
      { "collegeId": "...", "collegeName": "IIT Delhi", "count": 340 }
    ],
    "tribes": [
      { "tribeCode": "SHAURYA", "tribeName": "Shaurya", "count": 120 }
    ],
    "ageDistribution": {
      "18-20": 45,
      "21-23": 38,
      "24+": 17
    }
  },
  "activeHours": [
    { "hour": 9, "activity": 0.8 },
    { "hour": 21, "activity": 0.95 }
  ]
}
```

---

## 7. Reach Analytics

`GET /api/analytics/reach?period=14d`

```json
{
  "timeSeries": [
    { "date": "2026-03-01", "impressions": 1200, "reach": 800, "engagement": 45 },
    { "date": "2026-03-02", "impressions": 1500, "reach": 950, "engagement": 62 }
  ],
  "totals": {
    "impressions": 18500,
    "reach": 12300,
    "engagement": 890
  },
  "sources": {
    "feed": 45,
    "explore": 30,
    "profile": 15,
    "search": 10
  }
}
```

---

## 8. Story Analytics

`GET /api/analytics/stories?period=7d`

```json
{
  "stories": [
    {
      "storyId": "...",
      "viewCount": 340,
      "reactionCount": 23,
      "replyCount": 5,
      "completionRate": 0.78,
      "stickers": [
        { "type": "POLL", "responseCount": 120 }
      ]
    }
  ],
  "summary": {
    "totalStories": 8,
    "avgViews": 280,
    "avgCompletionRate": 0.72,
    "totalReactions": 45
  }
}
```

---

## 9. Profile Visit Analytics

`GET /api/analytics/profile-visits?period=7d`

```json
{
  "totalVisits": 89,
  "uniqueVisitors": 67,
  "sources": {
    "feed": 40,
    "search": 25,
    "profile_link": 15,
    "other": 9
  },
  "timeline": [
    { "date": "2026-03-01", "visits": 12 }
  ]
}
```

---

## 10. Reel Analytics

`GET /api/analytics/reels?period=30d`

```json
{
  "reels": [
    {
      "reelId": "...",
      "viewCount": 12000,
      "likeCount": 450,
      "commentCount": 89,
      "shareCount": 34,
      "saveCount": 67,
      "avgWatchTime": 12.5,
      "completionRate": 0.65
    }
  ],
  "summary": {
    "totalReels": 5,
    "totalViews": 45000,
    "avgEngagementRate": 4.8
  }
}
```

---

## 11. Android Integration

### Analytics Dashboard Screen
```kotlin
val overview = api.get("/api/analytics/overview?period=7d")
val audience = api.get("/api/analytics/audience?period=30d")
val reach = api.get("/api/analytics/reach?period=14d")
```

### Track Events
```kotlin
api.post("/api/analytics/track", mapOf(
    "eventType" to "VIEW",
    "targetType" to "POST",
    "targetId" to contentId,
    "metadata" to mapOf("source" to "feed")
))
```
