# 13 — Contests System

**Source**: `/app/lib/handlers/tribe-contests.js`, `/app/lib/services/contest-service.js`, `/app/lib/contest-realtime.js`

---

## 1. Overview

The Tribe Contest Engine is a full-lifecycle competition system supporting reel challenges, tribe battles, participation events, judged contests, and hybrid scoring.

**Golden Rule**: Like ≠ Vote ≠ Score ≠ Salute ≠ Fund

---

## 2. Contest Types & Formats

### Types
| Type | Description |
|------|-------------|
| `reel_creative` | Reel-based creative challenge |
| `tribe_battle` | Inter-tribe competition |
| `participation` | Everyone gets salutes |
| `judge` | Panel of judges scores entries |
| `hybrid` | Public votes + judge scores |
| `seasonal` | Season-long aggregate |

### Formats
| Format | Description |
|--------|-------------|
| `INDIVIDUAL` | Single participant entries |
| `TEAM` | Team entries |
| `TRIBE_VS_TRIBE` | Tribe-level competition |

---

## 3. Contest Lifecycle

```
DRAFT → PUBLISHED → ENTRY_OPEN → ENTRY_CLOSED → EVALUATING → LOCKED → RESOLVED
```

Each transition has validation rules enforced by `canTransition()`.

### Admin Lifecycle Endpoints

| Transition | Endpoint |
|-----------|----------|
| DRAFT → PUBLISHED | `POST /api/admin/tribe-contests/:id/publish` |
| PUBLISHED → ENTRY_OPEN | `POST /api/admin/tribe-contests/:id/open-entries` |
| ENTRY_OPEN → ENTRY_CLOSED | `POST /api/admin/tribe-contests/:id/close-entries` |
| EVALUATING → LOCKED | `POST /api/admin/tribe-contests/:id/lock` |
| LOCKED → RESOLVED | `POST /api/admin/tribe-contests/:id/resolve` |
| Any → CANCELLED | `POST /api/admin/tribe-contests/:id/cancel` |

---

## 4. Contest Schema (Collection: `tribe_contests`)

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Contest ID |
| `title` | string | Contest title |
| `description` | string | Full description |
| `contestType` | enum | `reel_creative`, `tribe_battle`, etc. |
| `format` | enum | `INDIVIDUAL`, `TEAM`, `TRIBE_VS_TRIBE` |
| `status` | enum | Lifecycle status |
| `seasonId` | string? | Linked season |
| `scoringModel` | enum | `VOTES_ONLY`, `JUDGE_ONLY`, `HYBRID`, `PARTICIPATION` |
| `contestStartAt` | Date | Entry open date |
| `contestEndAt` | Date | Entry close date |
| `entryTypes` | array | Allowed entry types |
| `maxEntriesPerUser` | number | Entry limit |
| `audienceScope` | enum | `ALL`, `TRIBE_ONLY`, `COLLEGE_ONLY` |
| `saluteDistribution` | object | Custom salute awards |
| `rules` | array | Contest rules (versioned) |
| `stats` | object | Entry count, vote count, etc. |

---

## 5. Entries

### Submit Entry
`POST /api/tribe-contests/:id/enter`

```json
{
  "entryType": "REEL",
  "contentId": "reel-uuid",
  "caption": "My entry",
  "tribeId": "my-tribe-id"
}
```

Validation includes:
- Contest status must be `ENTRY_OPEN`
- User hasn't exceeded `maxEntriesPerUser`
- Content exists and belongs to user
- Audience scope check

### Entry Schema (Collection: `tribe_contest_entries`)

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Entry ID |
| `contestId` | string | Parent contest |
| `userId` | string | Entrant |
| `tribeId` | string | Entrant's tribe |
| `entryType` | enum | `REEL`, `POST`, `TEXT`, etc. |
| `contentId` | string? | Linked content |
| `status` | enum | `SUBMITTED`, `APPROVED`, `DISQUALIFIED`, `WINNER` |
| `voteCount` | number | Public votes |
| `judgeScore` | number | Judge average |
| `finalScore` | number | Computed final |
| `rank` | number | Final rank |

---

## 6. Voting

`POST /api/tribe-contests/:id/vote`

```json
{
  "entryId": "entry-uuid",
  "voteType": "UP"
}
```

### Vote Types
- `UP` — Standard upvote
- `TRIBE_BOOST` — Extra weight from same tribe (configurable)

### Restrictions
- One vote per user per entry (configurable via `allowMultipleVotes`)
- Cannot vote on own entry
- Contest must be in voting-eligible state

---

## 7. Scoring Models

### VOTES_ONLY
Final score = public vote count

### JUDGE_ONLY
Final score = average of judge scores

### HYBRID
```
finalScore = (voteWeight * normalizedVotes) + (judgeWeight * normalizedJudgeScore)
```
Default: 40% votes, 60% judge

### PARTICIPATION
All valid entries receive fixed salutes

---

## 8. Judge Scoring

`POST /api/admin/tribe-contests/:id/judge-score`

```json
{
  "entryId": "entry-uuid",
  "judgeId": "judge-user-id",
  "score": 8.5,
  "criteria": {
    "creativity": 9,
    "execution": 8,
    "impact": 8.5
  },
  "feedback": "Excellent work"
}
```

Stored in `contest_judge_scores` collection.

---

## 9. Resolution

`POST /api/admin/tribe-contests/:id/resolve` — Idempotent operation:

1. Computes final scores for all entries
2. Ranks entries by score
3. Awards salutes to winning tribes
4. Creates ledger entries
5. Updates tribe `totalSalutes`
6. Broadcasts rank changes via SSE
7. Sets contest status to `RESOLVED`

---

## 10. Real-Time SSE Streams

### Global Activity Feed
```
GET /api/tribe-contests/live-feed
Events: entry.submitted, vote.cast, score.updated, contest.resolved
```

### Contest-Specific Scoreboard
```
GET /api/tribe-contests/:id/live
Events: Real-time score/rank changes for a specific contest
```

### Season Standings
```
GET /api/tribe-contests/seasons/:id/live-standings
Events: Tribe rank changes within season
```

---

## 11. Leaderboard

`GET /api/tribe-contests/:id/leaderboard`

Returns ranked entries with:
```json
{
  "items": [
    {
      "rank": 1,
      "entry": { ... },
      "user": { "displayName": "...", "tribeCode": "SHAURYA" },
      "voteCount": 342,
      "judgeScore": 9.2,
      "finalScore": 8.7
    }
  ]
}
```

---

## 12. Android Integration

### Contest List Screen
```kotlin
val contests = api.get("/api/tribe-contests?status=ENTRY_OPEN")
```

### Contest Detail + Entry
```kotlin
val detail = api.get("/api/tribe-contests/$id")
api.post("/api/tribe-contests/$id/enter", entryBody)
```

### Voting
```kotlin
api.post("/api/tribe-contests/$id/vote", mapOf("entryId" to eid, "voteType" to "UP"))
```

### Live SSE
```kotlin
val sseUrl = "$baseUrl/api/tribe-contests/$id/live?token=$accessToken"
// Use OkHttp SSE or EventSource library
```
