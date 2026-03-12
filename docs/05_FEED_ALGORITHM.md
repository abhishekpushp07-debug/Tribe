# Tribe — Smart Feed Ranking Algorithm

> Mathematical deep dive into the Instagram-level feed ranking engine.
> 331 lines of scoring logic with 9 signals.

---

## 1. Overview

The Smart Feed Algorithm ranks content on the first page of feeds using a multi-signal scoring model. Subsequent pages use chronological ordering.

```
feedScore = recency × (1 + engagement) × affinity × quality × viralityBoost × typeBoost
```

---

## 2. Signal Breakdown

### Signal 1: Recency (Exponential Decay)

```
recency = e^(-ln(2) × ageMs / halfLifeMs)

half-life: 6 hours (posts) | 12 hours (reels)
```

| Age | Recency Score (Posts) | Recency Score (Reels) |
|-----|----------------------|----------------------|
| 0 min | 1.000 | 1.000 |
| 30 min | 0.944 | 0.971 |
| 1 hour | 0.891 | 0.944 |
| 3 hours | 0.707 | 0.841 |
| 6 hours | 0.500 | 0.707 |
| 12 hours | 0.250 | 0.500 |
| 24 hours | 0.063 | 0.250 |
| 48 hours | 0.004 | 0.063 |
| 72 hours | 0.000 | 0.016 |

---

### Signal 2: Engagement Velocity (Log-Scaled)

```
engagementRaw = (likes × 1) + (comments × 3) + (saves × 5) + (shares × 2)
velocity = engagementRaw / ageInHours
engagement = log2(1 + velocity)
```

| Velocity | Engagement Score |
|----------|------------------|
| 0 | 0.000 |
| 1 | 1.000 |
| 5 | 2.585 |
| 10 | 3.459 |
| 50 | 5.672 |
| 100 | 6.658 |
| 500 | 8.966 |

**Interpretation**: A post with 50 likes + 10 comments + 5 saves in 1 hour:
```
engagementRaw = (50×1) + (10×3) + (5×5) + (0×2) = 105
velocity = 105 / 1 = 105
engagement = log2(106) = 6.73
```

---

### Signal 3: Virality Detection

```
if (postVelocity > 2 × avgFeedVelocity) → viralityBoost = 1.20
else → viralityBoost = 1.00
```

Detects posts gaining engagement 2× faster than average.

---

### Signal 4: Author Affinity (0.0 to ~2.8)

```
affinity = 1.0 (base)
  + 0.5 (if viewer follows author)
  + 0.3 (if same tribe)
  + 0.0-1.0 (per-author interaction history)
```

### Interaction History Calculation
```
Last 30 days:
  rawScore = (likeCount × 1) + (commentCount × 3) + (saveCount × 5)
  normalized = rawScore / maxScoreAcrossAllAuthors  (0.0 to 1.0)
```

---

### Signal 5: Content Type Affinity

```
For each content type (text, image, video, carousel, poll, thread, link):
  typeWeight = 0.8 + (typeCount / totalLikes) × 0.6
```

| User likes 80% images | Image typeWeight | Text typeWeight |
|-----------------------|------------------|------------------|
| Result | 1.28 | 0.92 |

---

### Signal 6: Quality Signals

```
quality = 1.0 (base)
  × 1.15 (if has media)
  × 1.05 (if carousel/multi-media)
  × 1.05 (if caption 50-500 chars)
  × 1.30 (if unseen + from followed user)
  × 0.50 (if reportCount > 3)
```

---

### Signal 7: Diversity Penalty

Prevents same author from dominating:
```
Post #1 from author A: no penalty
Post #2 from author A: score × 0.70
Post #3+ from author A: score × 0.40

Same content type 3+ in a row: score × 0.85
```

---

### Signal 8: Negative Signals

```
Muted author:  score = 0.01 (near-zero, not removed)
Hidden post:   score = 0 (completely removed)
Reported (3+): quality × 0.5
```

---

### Signal 9: Unseen Boost

```
if (viewer follows author AND viewer hasn't seen this post):
  quality × 1.30 (30% boost)
```

---

## 3. Complete Scoring Example

### Scenario
Post by user B, 3 hours old, 50 likes, 10 comments, 5 saves.
Viewer follows B, same tribe, has liked 8 of B's posts before.

```
1. Recency:
   ageMs = 3 hours = 10,800,000 ms
   recency = e^(-ln(2) × 10800000 / 21600000) = 0.707

2. Engagement:
   raw = (50×1) + (10×3) + (5×5) = 105
   velocity = 105 / 3 = 35
   engagement = log2(36) = 5.17

3. Virality:
   avgVelocity = 10 (feed average)
   35 > 20 (2×10) → viralityBoost = 1.20

4. Affinity:
   base = 1.0
   + 0.5 (follows)
   + 0.3 (same tribe)
   + 0.65 (interaction: 8 likes normalized)
   = 2.45

5. Content Type:
   typeBoost = 1.15 (viewer likes images, this is image)

6. Quality:
   1.0 × 1.15 (has media) × 1.05 (good caption) × 1.30 (unseen) = 1.57

7. FINAL SCORE:
   0.707 × (1 + 5.17) × 2.45 × 1.57 × 1.20 × 1.15
   = 0.707 × 6.17 × 2.45 × 1.57 × 1.20 × 1.15
   = 0.707 × 6.17 × 2.45 × 1.57 × 1.38
   = 23.15
```

---

## 4. Feed Debug Endpoint

```
GET /api/feed/debug?limit=20
```

Returns scoring breakdown for each post:
```json
{
  "algorithm": "smart_feed_v2",
  "posts": [
    {
      "postId": "...",
      "totalScore": 23.15,
      "breakdown": {
        "recency": 0.707,
        "engagement": 5.17,
        "affinity": 2.45,
        "quality": 1.57,
        "virality": 1.20,
        "typeBoost": 1.15,
        "diversityPenalty": 1.0
      }
    }
  ]
}
```

---

## 5. Pagination Strategy

| Page | Ranking | Method |
|------|---------|--------|
| First page (no cursor) | Smart Feed Algorithm | Ranked by score |
| Subsequent pages (with cursor) | Chronological | Sorted by createdAt desc |

This prevents:
- Re-ranking causing posts to appear/disappear
- Infinite scroll inconsistencies
- Heavy computation on every page

---

*Feed Algorithm v3.0.0 — 9 signals, production-grade ranking*
