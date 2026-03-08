# B0-S6 — Real-Time SSE Contract Freeze

**Status**: FROZEN  
**Freeze Date**: 2026-02-XX  
**Rule**: Every SSE endpoint, event name, payload shape, and reconnect behavior is locked. Android live UI builds on this exact contract.

---

## 1. SSE Architecture Overview

### Transport
- **Primary**: Redis Pub/Sub (multi-instance capable)
- **Fallback**: In-memory EventEmitter (single-instance, auto-detected)
- Client is unaware of transport — same SSE protocol either way

### Channel Topology
| Channel Pattern | Purpose |
|-----------------|---------|
| `tribe:contest:{contestId}` | Per-contest live scoreboard |
| `tribe:contest:global` | Cross-contest activity feed |
| `tribe:standings:{seasonId}` | Per-season live standings |
| `tribe:story:{userId}` | Per-user story events |

### Connection Protocol
```
1. Client connects via EventSource
2. Server sends `connected` event (metadata)
3. Server sends `snapshot` event (current full state)
4. Server streams delta events as they happen
5. Heartbeat every 10-15 seconds (comment line)
6. Auto-refresh snapshot at intervals (stale-client protection)
7. On disconnect: client reconnects using retry hint
```

---

## 2. SSE Response Headers (all endpoints)

```http
Content-Type: text/event-stream
Cache-Control: no-cache, no-transform
Connection: keep-alive
X-Accel-Buffering: no
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
retry: 3000
```

---

## 3. SSE Message Format

All SSE messages follow this wire format:
```
id: {incrementing_integer}
event: {event_name}
data: {JSON_payload}

```

Heartbeats are SSE comments:
```
: heartbeat 2025-01-15T12:00:00.000Z

```

---

## 4. SSE Endpoint Contracts

### 4.1 Contest Live Scoreboard

**Endpoint**: `GET /api/tribe-contests/{contestId}/live`  
**Auth**: None required (public)  
**Snapshot refresh**: Every 30 seconds  
**Heartbeat**: Every 10 seconds

#### `connected` event (first message)
```json
{
  "contestId": "uuid",
  "mode": "redis | memory",
  "connectedAt": "ISO date"
}
```

#### `snapshot` event (immediately after connected, then every 30s)
```json
{
  "contest": {
    "id": "uuid",
    "contestName": "string",
    "status": "ENTRY_OPEN | EVALUATING | LOCKED | RESOLVED",
    "contestType": "reel_creative",
    "contestEndAt": "ISO date | null",
    "votingEnabled": true
  },
  "entryCount": 42,
  "voteCount": 350,
  "leaderboard": [
    {
      "rank": 1,
      "entryId": "uuid",
      "tribeId": "uuid",
      "userId": "uuid",
      "finalScore": 92.5,
      "judgeScore": 8.5,
      "engagementScore": 85.0,
      "tribe": {
        "id": "uuid",
        "tribeName": "Somnath Tribe",
        "tribeCode": "SOMNATH",
        "primaryColor": "#B71C1C",
        "animalIcon": "lion"
      }
    }
  ],
  "tribeRanking": [
    {
      "rank": 1,
      "tribeId": "uuid",
      "totalScore": 250.0,
      "entries": 5,
      "tribe": { /* same tribe summary */ }
    }
  ],
  "snapshotAt": "ISO date"
}
```

#### Delta Events (streamed in real-time)

##### `entry.submitted`
```json
{
  "type": "entry.submitted",
  "contestId": "uuid",
  "entryId": "uuid",
  "userId": "uuid",
  "tribeId": "uuid",
  "entryType": "reel | post | manual",
  "ts": "ISO date"
}
```

##### `vote.cast`
```json
{
  "type": "vote.cast",
  "contestId": "uuid",
  "entryId": "uuid",
  "voterUserId": "uuid",
  "voterTribeId": "uuid",
  "voteType": "upvote | support",
  "ts": "ISO date"
}
```

##### `score.updated`
```json
{
  "type": "score.updated",
  "contestId": "uuid",
  "entryId": "uuid",
  "tribeId": "uuid",
  "userId": "uuid",
  "oldScore": 80.0,
  "newScore": 85.0,
  "oldRank": 3,
  "newRank": 2,
  "ts": "ISO date"
}
```

##### `rank.changed`
```json
{
  "type": "rank.changed",
  "contestId": "uuid",
  "changes": [
    { "entryId": "uuid", "tribeId": "uuid", "oldRank": 2, "newRank": 1 },
    { "entryId": "uuid", "tribeId": "uuid", "oldRank": 1, "newRank": 2 }
  ],
  "ts": "ISO date"
}
```

##### `contest.transition`
```json
{
  "type": "contest.transition",
  "contestId": "uuid",
  "from": "ENTRY_OPEN",
  "to": "ENTRY_CLOSED",
  "contestName": "string",
  "ts": "ISO date"
}
```

##### `contest.resolved`
```json
{
  "type": "contest.resolved",
  "contestId": "uuid",
  "winnerType": "entry | tribe",
  "topPositions": [
    { "rank": 1, "tribeId": "uuid", "finalScore": 92.5 }
  ],
  "totalSalutesAwarded": 2000,
  "contestName": "string",
  "ts": "ISO date"
}
```

---

### 4.2 Season Live Standings

**Endpoint**: `GET /api/tribe-contests/seasons/{seasonId}/live-standings`  
**Auth**: None required (public)  
**Snapshot refresh**: Every 60 seconds  
**Heartbeat**: Every 10 seconds

#### `connected` event
```json
{
  "seasonId": "uuid",
  "mode": "redis | memory"
}
```

#### `snapshot` event
```json
{
  "season": {
    "id": "uuid",
    "name": "Spring 2025",
    "status": "active",
    "year": 2025
  },
  "standings": [
    {
      "rank": 1,
      "seasonId": "uuid",
      "tribeId": "uuid",
      "totalSalutes": 15000,
      "contestsWon": 3,
      "contestsParticipated": 7,
      "tribe": {
        "id": "uuid",
        "tribeName": "Somnath Tribe",
        "tribeCode": "SOMNATH",
        "primaryColor": "#B71C1C",
        "animalIcon": "lion"
      }
    }
  ],
  "activeContests": [
    {
      "id": "uuid",
      "contestName": "string",
      "status": "ENTRY_OPEN",
      "contestType": "reel_creative",
      "contestEndAt": "ISO date | null"
    }
  ],
  "snapshotAt": "ISO date"
}
```

#### Delta Event

##### `standings.updated`
```json
{
  "type": "standings.updated",
  "seasonId": "uuid",
  "tribeId": "uuid",
  "oldSalutes": 14500,
  "newSalutes": 15000,
  "oldRank": 2,
  "newRank": 1,
  "reason": "contest_win | admin_adjust",
  "ts": "ISO date"
}
```

---

### 4.3 Global Contest Activity Feed

**Endpoint**: `GET /api/tribe-contests/live-feed`  
**Auth**: None required (public)  
**Snapshot refresh**: None (initial only)  
**Heartbeat**: Every 10 seconds

#### `connected` event
```json
{
  "channel": "global",
  "mode": "redis | memory"
}
```

#### `snapshot` event
```json
{
  "liveContests": [
    {
      "id": "uuid",
      "contestName": "string",
      "status": "ENTRY_OPEN",
      "contestType": "reel_creative",
      "contestEndAt": "ISO date | null",
      "seasonId": "uuid"
    }
  ],
  "recentEntries": [
    {
      "id": "uuid",
      "contestId": "uuid",
      "tribeId": "uuid",
      "userId": "uuid",
      "submittedAt": "ISO date",
      "entryType": "reel"
    }
  ],
  "recentResults": [
    {
      "id": "uuid",
      "contestId": "uuid",
      "winnerTribeId": "uuid",
      "resolvedAt": "ISO date"
    }
  ],
  "snapshotAt": "ISO date"
}
```

#### Delta Events
All contest events from ALL contests are forwarded to this stream. Same payload shapes as Section 4.1 deltas: `entry.submitted`, `vote.cast`, `score.updated`, `rank.changed`, `contest.transition`, `contest.resolved`, `standings.updated`.

---

### 4.4 Story Events Stream

**Endpoint**: `GET /api/stories/events/stream`  
**Auth**: Required (bearer token)  
**Heartbeat**: Every 15 seconds

#### Event Types

##### `story.viewed`
```json
{
  "type": "story.viewed",
  "storyId": "uuid",
  "viewerId": "uuid",
  "viewerName": "string",
  "ts": "ISO date"
}
```

##### `story.reacted`
```json
{
  "type": "story.reacted",
  "storyId": "uuid",
  "userId": "uuid",
  "emoji": "❤️ | 🔥 | 😂 | 😮 | 😢 | 👏",
  "ts": "ISO date"
}
```

##### `story.replied`
```json
{
  "type": "story.replied",
  "storyId": "uuid",
  "senderId": "uuid",
  "senderName": "string",
  "ts": "ISO date"
}
```

##### `story.sticker_responded`
```json
{
  "type": "story.sticker_responded",
  "storyId": "uuid",
  "stickerId": "uuid",
  "stickerType": "POLL | QUIZ | QUESTION | EMOJI_SLIDER",
  "responderId": "uuid",
  "ts": "ISO date"
}
```

##### `story.expired`
```json
{
  "type": "story.expired",
  "storyId": "uuid",
  "authorId": "uuid",
  "ts": "ISO date"
}
```

---

## 5. Client Implementation Rules

### 5.1 Connection
```kotlin
// Android EventSource pseudo-code
val source = EventSource.Builder(url)
    .reconnectTime(Duration.ofSeconds(3))
    .build()

source.addEventListener("connected") { ... }
source.addEventListener("snapshot") { ... }
source.addEventListener("entry.submitted") { ... }
source.addEventListener("vote.cast") { ... }
// etc.
```

### 5.2 Reconnect Behavior
- Server sends `retry: 3000` (3 seconds)
- Client should auto-reconnect on disconnect
- On reconnect, server sends fresh `snapshot` — client replaces entire state
- No need for Last-Event-ID differential recovery (snapshot is full state)

### 5.3 Stale-Client Protection
- Contest scoreboard: auto-refreshes snapshot every **30 seconds**
- Season standings: auto-refreshes snapshot every **60 seconds**
- Global feed: snapshot only on initial connect (deltas are sufficient)

### 5.4 Deduplication
- Use `event.ts` (ISO timestamp) + `event.type` + entity IDs for client-side dedup
- Snapshot events REPLACE entire local state (not merge)
- Delta events UPDATE/INSERT into local state

### 5.5 Heartbeat Handling
- Heartbeats are SSE comment lines (`:` prefix)
- If no heartbeat received in 30 seconds, assume connection dead → reconnect

### 5.6 Error Events
```json
{
  "type": "error",
  "error": "Stream init failed",
  "detail": "error message"
}
```
On error event: close connection, wait 3s, reconnect.

---

## 6. Event Name Registry (Complete)

| Event Name | Source | Channels |
|------------|--------|----------|
| `connected` | Server | All SSE endpoints |
| `snapshot` | Server | All SSE endpoints |
| `entry.submitted` | Write path | contest + global |
| `vote.cast` | Write path | contest + global |
| `score.updated` | Compute path | contest + global |
| `rank.changed` | Compute path | contest + global |
| `contest.transition` | Admin action | contest + global |
| `contest.resolved` | Admin resolve | contest + global |
| `standings.updated` | Resolve/adjust | standings + global |
| `activity` | Various | global only |
| `story.viewed` | View path | story stream |
| `story.reacted` | React path | story stream |
| `story.replied` | Reply path | story stream |
| `story.sticker_responded` | Sticker path | story stream |
| `story.expired` | Expiry worker | story stream |
| `error` | Server error | Any stream |

---

## PASS Gate Verification

- [x] Every SSE endpoint fully specified with connection protocol
- [x] Every event name frozen with exact payload shape
- [x] Snapshot shapes frozen (contest, standings, global)
- [x] Delta event shapes frozen
- [x] Reconnect behavior documented (retry: 3s, fresh snapshot)
- [x] Heartbeat cadence documented (10s contest, 15s story)
- [x] Stale-client refresh intervals documented (30s, 60s)
- [x] Dedup strategy documented
- [x] Error handling documented
- [x] Story SSE events included
- [x] Android can build exact EventSource listeners from this document

**B0-S6 STATUS: FROZEN**
