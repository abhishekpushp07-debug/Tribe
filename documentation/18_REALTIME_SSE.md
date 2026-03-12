# 18 — Real-Time SSE System

**Source**: `/app/lib/realtime.js`, `/app/lib/contest-realtime.js`

---

## 1. Overview

Server-Sent Events (SSE) for real-time updates. Two subsystems:
1. **Story/Reel Events** (`realtime.js`) — Story lifecycle events
2. **Contest Events** (`contest-realtime.js`) — Live contest activity, scores, standings

No WebSocket dependency — pure HTTP/1.1 SSE streams.

---

## 2. SSE Endpoints

| Endpoint | Auth | Description |
|----------|------|-------------|
| `GET /api/stories/events/stream` | Token (query/header) | Story lifecycle events |
| `GET /api/tribe-contests/live-feed` | 🔓 | Global contest activity |
| `GET /api/tribe-contests/:id/live` | 🔓 | Contest-specific scoreboard |
| `GET /api/tribe-contests/seasons/:id/live-standings` | 🔓 | Season standings changes |

---

## 3. Story SSE Stream

### Connection
```javascript
// Browser EventSource
const es = new EventSource('/api/stories/events/stream?token=ACCESS_TOKEN');

// Android (OkHttp)
val request = Request.Builder()
    .url("$baseUrl/api/stories/events/stream?token=$token")
    .header("Accept", "text/event-stream")
    .build()
```

### Event Types

| Event | Data | Trigger |
|-------|------|---------|
| `story.created` | `{ storyId, authorId, authorName }` | New story by followed user |
| `story.viewed` | `{ storyId, viewerId, viewerName }` | Someone viewed your story |
| `story.reacted` | `{ storyId, reaction, reactorId }` | Emoji reaction on story |
| `story.expired` | `{ storyId }` | Story expired (24h) |
| `story.replied` | `{ storyId, replyId, replierName }` | Story reply received |

### Authentication
Token passed as:
- Query param: `?token=<accessToken>` (required for EventSource)
- Header: `Authorization: Bearer <accessToken>`

### Connection Lifecycle
- Server sends `:keepalive` comments every 30 seconds
- Client should implement auto-reconnect with exponential backoff
- Connection closed on invalid/expired token

---

## 4. Contest SSE Streams

### Global Activity Feed
```
GET /api/tribe-contests/live-feed
```

Events broadcast across ALL active contests:
| Event | Data |
|-------|------|
| `entry.submitted` | `{ contestId, entryId, userId, tribeId }` |
| `vote.cast` | `{ contestId, entryId, voteCount }` |
| `score.updated` | `{ contestId, entryId, newScore, rank }` |
| `contest.resolved` | `{ contestId, winners: [...] }` |
| `contest.status_changed` | `{ contestId, from, to }` |

### Contest-Specific Scoreboard
```
GET /api/tribe-contests/:id/live
```

Real-time updates for a single contest:
| Event | Data |
|-------|------|
| `leaderboard.update` | `{ entries: [{ entryId, rank, score, delta }] }` |
| `entry.new` | `{ entry: { ... } }` |
| `vote.update` | `{ entryId, voteCount, rankChange }` |

### Season Standings
```
GET /api/tribe-contests/seasons/:id/live-standings
```

| Event | Data |
|-------|------|
| `standings.update` | `{ tribes: [{ tribeId, salutes, rank, delta }] }` |
| `salute.awarded` | `{ tribeId, amount, reason, contestId }` |

---

## 5. Implementation Details

### Publisher Functions

```javascript
// Story events (realtime.js)
publishStoryEvent(userId, eventData)

// Contest events (contest-realtime.js)
publishContestEvent(contestId, eventType, data)
publishStandingsUpdate(seasonId, standingsData)
```

### Stream Builders

```javascript
// Story stream - filtered per user (only followed users' events)
buildSSEStream(request, userId, db)

// Contest streams
buildContestLiveStream(request, contestId)
buildStandingsLiveStream(request, seasonId)
buildGlobalLiveStream(request)
```

### In-Memory Channel Architecture
Current implementation uses in-memory event channels (no Redis Pub/Sub in production yet). This means SSE events are per-process — if the app runs multiple instances, each instance only sees events generated within that process.

---

## 6. SSE Response Format

```
event: story.created
data: {"storyId":"abc123","authorId":"user456","authorName":"Priya"}

event: story.viewed
data: {"storyId":"abc123","viewerId":"user789","viewerName":"Rahul"}

:keepalive

event: story.reacted
data: {"storyId":"abc123","reaction":"❤️","reactorId":"user101"}
```

### Headers
```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
X-Accel-Buffering: no
```

---

## 7. Android Integration

### Using OkHttp SSE
```kotlin
val client = OkHttpClient.Builder()
    .readTimeout(0, TimeUnit.SECONDS) // No timeout for SSE
    .build()

val request = Request.Builder()
    .url("$baseUrl/api/stories/events/stream?token=$accessToken")
    .header("Accept", "text/event-stream")
    .build()

val eventSource = EventSources.createFactory(client)
    .newEventSource(request, object : EventSourceListener() {
        override fun onEvent(es: EventSource, id: String?, type: String?, data: String) {
            when (type) {
                "story.created" -> handleNewStory(data)
                "story.viewed" -> handleStoryView(data)
                "story.reacted" -> handleReaction(data)
            }
        }
        override fun onFailure(es: EventSource, t: Throwable?, response: Response?) {
            // Reconnect with exponential backoff
            reconnectWithBackoff()
        }
    })
```

### Reconnection Strategy
```kotlin
private var retryDelay = 1000L // Start at 1 second

fun reconnectWithBackoff() {
    handler.postDelayed({
        connectSSE()
        retryDelay = minOf(retryDelay * 2, 30000L) // Max 30 seconds
    }, retryDelay)
}

// Reset delay on successful connection
fun onConnected() {
    retryDelay = 1000L
}
```

---

## 8. Error Handling

| Scenario | Behavior |
|----------|----------|
| Invalid token | 401 JSON error (not SSE) |
| Expired token | Stream closes, client should refresh token and reconnect |
| Server restart | Stream closes, auto-reconnect |
| Network error | EventSource auto-retries (browser); manual retry (Android) |
