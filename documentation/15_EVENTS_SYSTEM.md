# 15 — Events System

**Source**: `/app/lib/handlers/events.js`

---

## 1. Overview

Full-lifecycle event management: creation, discovery, RSVP with capacity/waitlist, reminders, reports with auto-hold, organizer tools, and admin moderation. ~21 endpoints.

---

## 2. Event Schema (Collection: `events`)

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Event ID |
| `creatorId` | string | Organizer user ID |
| `title` | string | Title (max 200) |
| `description` | string | Description (max 5000) |
| `category` | enum | `ACADEMIC`, `CULTURAL`, `SPORTS`, `SOCIAL`, `WORKSHOP`, `PLACEMENT`, `OTHER` |
| `visibility` | enum | `PUBLIC`, `COLLEGE`, `PRIVATE` |
| `status` | enum | `DRAFT`, `PUBLISHED`, `CANCELLED`, `ARCHIVED`, `HELD`, `REMOVED` |
| `startAt` | Date | Event start time |
| `endAt` | Date | Event end time |
| `location` | string | Location text (max 300) |
| `locationUrl` | string? | Maps/virtual link |
| `coverMediaId` | string? | Cover image |
| `collegeId` | string? | College scope |
| `capacity` | number? | Max attendees (null = unlimited) |
| `goingCount` | number | RSVP GOING count |
| `interestedCount` | number | RSVP INTERESTED count |
| `waitlistCount` | number | Waitlist count |
| `reportCount` | number | Report count (auto-hold at 3) |
| `tags` | string[] | Searchable tags |

---

## 3. API Endpoints

### Public

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/events/feed` | Discovery feed (score-ranked, upcoming) |
| `GET` | `/api/events/search` | Search events (`?q=&category=&visibility=&startAfter=&startBefore=`) |
| `GET` | `/api/events/college/:collegeId` | College-scoped events |
| `GET` | `/api/events/:id` | Event detail (enriched with RSVP status) |
| `GET` | `/api/events/:id/attendees` | RSVP list (`?type=GOING\|INTERESTED\|WAITLIST`) |

### Authenticated

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/events` | Create event |
| `PATCH` | `/api/events/:id` | Edit event (organizer) |
| `DELETE` | `/api/events/:id` | Soft delete |
| `POST` | `/api/events/:id/publish` | Publish draft |
| `POST` | `/api/events/:id/cancel` | Cancel event |
| `POST` | `/api/events/:id/archive` | Archive past event |
| `POST` | `/api/events/:id/rsvp` | RSVP (`type=GOING\|INTERESTED`) |
| `DELETE` | `/api/events/:id/rsvp` | Cancel RSVP |
| `POST` | `/api/events/:id/report` | Report event |
| `POST` | `/api/events/:id/remind` | Set reminder |
| `DELETE` | `/api/events/:id/remind` | Remove reminder |
| `GET` | `/api/me/events` | My created events |
| `GET` | `/api/me/events/rsvps` | Events I've RSVP'd to |

### Admin

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/admin/events` | Moderation queue |
| `PATCH` | `/api/admin/events/:id/moderate` | Moderate event |
| `GET` | `/api/admin/events/analytics` | Platform analytics |
| `POST` | `/api/admin/events/:id/recompute-counters` | Recompute counters |

---

## 4. Creating an Event

```json
POST /api/events
{
  "title": "Inter-College Hackathon 2026",
  "description": "48-hour coding challenge...",
  "category": "ACADEMIC",
  "visibility": "PUBLIC",
  "startAt": "2026-04-15T09:00:00.000Z",
  "endAt": "2026-04-17T09:00:00.000Z",
  "location": "Main Auditorium, IIT Delhi",
  "locationUrl": "https://maps.google.com/...",
  "capacity": 200,
  "tags": ["hackathon", "coding", "tech"]
}
```

**Rate limit**: 10 events per hour per user.

---

## 5. RSVP System

### RSVP Flow
```json
POST /api/events/:id/rsvp
{ "type": "GOING" }
```

**Capacity handling**:
1. If `goingCount < capacity` → RSVP accepted as GOING
2. If at capacity → Added to WAITLIST
3. When someone cancels → First waitlisted user promoted to GOING

### RSVP Data (Collection: `event_rsvps`)

| Field | Type | Description |
|-------|------|-------------|
| `eventId` | string | Event ID |
| `userId` | string | User ID |
| `type` | enum | `GOING`, `INTERESTED`, `WAITLIST` |
| `waitlistPosition` | number? | Position in waitlist |

---

## 6. Event Scoring (Discovery Feed)

`GET /api/events/feed` uses a scoring algorithm (`computeEventScore`):

```
score = urgency * 50 + popularity * 50 - reportPenalty * 10

Where:
  urgency = 1 / (1 + hoursUntilStart / 48)  [closer events score higher]
  popularity = (going * 2 + interested) / (total + 1)
  reportPenalty = reportCount * 0.15
```

Events are sorted by this score, ensuring upcoming popular events surface first.

---

## 7. Reports & Auto-Hold

When `reportCount >= 3`, the event is automatically moved to `HELD` status and removed from public feeds.

Admin reviews held events at `GET /api/admin/events` and can:
- **Approve**: Restore to PUBLISHED
- **Remove**: Permanent removal

---

## 8. Reminders

```json
POST /api/events/:id/remind
```

Creates a reminder entry (Collection: `event_reminders`). The reminder system is designed for push notification integration — when `startAt` approaches, the notification system can query upcoming reminders and send push.

---

## 9. Block Integration

- Blocked users cannot see each other's events
- RSVP lists filter out blocked users
- Block check is bidirectional

---

## 10. Android Integration

### Event Discovery
```kotlin
val feed = api.get("/api/events/feed?limit=20")
// Items sorted by relevance score (upcoming + popular first)
```

### RSVP
```kotlin
api.post("/api/events/$id/rsvp", mapOf("type" to "GOING"))
// Check response for waitlist status
```

### My Events
```kotlin
val created = api.get("/api/me/events")
val rsvps = api.get("/api/me/events/rsvps")
```

### College Events
```kotlin
val events = api.get("/api/events/college/$collegeId")
```
