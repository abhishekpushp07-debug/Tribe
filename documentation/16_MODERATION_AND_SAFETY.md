# 16 — Moderation & Safety

**Source**: `/app/lib/handlers/admin.js`, `/app/lib/moderation/`, `/app/lib/services/anti-abuse-service.js`

---

## 1. Overview

Multi-layered content safety system with:
- **AI-powered auto-moderation** (Provider-Adapter pattern)
- **User reports** with auto-hold threshold
- **Appeal system** with moderator decisions
- **Anti-abuse engine** (velocity checks, suspicious action logging)
- **Grievance system** for user complaints

---

## 2. Moderation Architecture

```
Content Creation
    │
    ▼
AI Moderation (Provider-Adapter)
    │
    ├── ALLOW → Published (distributionStage 2)
    ├── ESCALATE → Held (distributionStage 0, visibility: HELD)
    └── REJECT → 422 error returned to client
    
User Report
    │
    ├── reportCount < 3 → Status: PENDING
    └── reportCount >= 3 → Auto-hold (status: HELD)
```

### Provider-Adapter Pattern (`/app/lib/moderation/`)

```
moderation/
├── config.js          — Moderation thresholds
├── middleware/
│   └── moderate-create-content.js  — Entry point for all content moderation
├── provider.js        — Abstract provider interface
├── providers/         — Concrete implementations
├── repositories/      — Data access
├── routes/
│   └── moderation.routes.js — Moderation config & check routes
├── rules.js           — Moderation rules engine
└── services/          — Moderation service layer
```

---

## 3. AI Content Moderation

Applied automatically on:
- Post creation (`POST /content/posts`)
- Post editing (`PATCH /content/:id`)
- Comment creation (`POST /content/:id/comments`)
- Story creation (`POST /stories`)
- Reel creation (`POST /reels`)

### Moderation Decision Object
```json
{
  "action": "ALLOW | ESCALATE | REJECT",
  "provider": "rules_engine",
  "providerModel": "v1",
  "confidence": 0.95,
  "flaggedCategories": ["HATE_SPEECH", "VIOLENCE"],
  "reasons": ["Contains flagged keywords"]
}
```

### Content Moderation Fields (on `content_items`)
```json
{
  "moderation": {
    "action": "ALLOW",
    "provider": "rules_engine",
    "confidence": 0.85,
    "flaggedCategories": [],
    "reviewTicketId": null,
    "checkedAt": "2026-03-01T..."
  },
  "riskScore": 0.15,
  "policyReasons": []
}
```

---

## 4. User Reports

### Submit Report
`POST /api/reports`
```json
{
  "targetId": "content-uuid",
  "targetType": "CONTENT | USER | COMMENT | REEL | STORY | EVENT | PAGE | RESOURCE",
  "reason": "SPAM | HATE_SPEECH | NUDITY | HARASSMENT | MISINFORMATION | OTHER",
  "details": "Additional context..."
}
```

### Report Schema (Collection: `reports`)

| Field | Type | Description |
|-------|------|-------------|
| `reporterId` | string | Reporter user ID |
| `targetId` | string | Reported entity ID |
| `targetType` | enum | Entity type |
| `targetAuthorId` | string | Author of reported content |
| `reason` | enum | Report reason |
| `details` | string | Additional details (max 500) |
| `status` | enum | `PENDING`, `REVIEWED`, `RESOLVED`, `DISMISSED` |

---

## 5. Moderation Queue

`GET /api/moderation/queue` (Admin/Moderator)

Returns items pending review, sorted by report count and risk score.

`POST /api/moderation/:contentId/action` (Admin/Moderator)
```json
{
  "action": "APPROVE | REMOVE | HOLD",
  "reason": "explanation"
}
```

---

## 6. Appeals

### Submit Appeal
`POST /api/appeals`
```json
{
  "contentId": "removed-content-uuid",
  "reason": "My content was wrongly removed because..."
}
```

### Decide Appeal
`PATCH /api/appeals/:id/decide` (Moderator)
```json
{
  "decision": "APPROVED | REJECTED",
  "reason": "Explanation for decision"
}
```

If approved, content is restored to PUBLIC visibility.

---

## 7. Anti-Abuse Engine

**Source**: `/app/lib/services/anti-abuse-service.js`

### Velocity Checks
Applied to: Follow, Like, Comment, Save, Share actions

```javascript
checkEngagementAbuse(userId, actionType, targetId, targetAuthorId)
// Returns: { allowed: boolean, flagged: boolean, reason?: string }
```

### Action Types
| Action | Window | Limit | Description |
|--------|--------|-------|-------------|
| `FOLLOW` | 1 hour | 50 | Follow rate |
| `LIKE` | 1 min | 30 | Like rate |
| `COMMENT` | 1 min | 10 | Comment rate |
| `SAVE` | 1 min | 20 | Save rate |
| `SHARE` | 1 min | 10 | Share rate |

### Suspicious Action Logging
Flagged actions are logged to `abuse_log` collection for admin review.

### Admin Abuse Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/admin/abuse-dashboard` | Overview stats |
| `GET` | `/api/admin/abuse-log` | Detailed audit log |

---

## 8. Auto-Hold Rules

Content/entities are automatically held when:
- Report count reaches threshold (3 for events, resources, reels, stories)
- AI moderation flags as ESCALATE
- Abuse velocity check is triggered repeatedly

---

## 9. Grievance System

For users to escalate issues beyond content reports.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/grievances` | Submit grievance |
| `GET` | `/api/grievances` | My grievances |

### Grievance Schema (Collection: `grievance_tickets`)

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Ticket ID |
| `userId` | string | Submitter |
| `category` | string | Grievance type |
| `description` | string | Details |
| `status` | enum | `OPEN`, `IN_PROGRESS`, `RESOLVED`, `CLOSED` |

---

## 10. Android Integration

### Report Content
```kotlin
api.post("/api/content/$id/report", mapOf("reason" to "SPAM", "details" to "..."))
// Also: /api/stories/$id/report, /api/reels/$id/report, /api/events/$id/report
```

### Submit Appeal
```kotlin
api.post("/api/appeals", mapOf("contentId" to id, "reason" to "Wrongly removed"))
```

### Submit Grievance
```kotlin
api.post("/api/grievances", mapOf("category" to "HARASSMENT", "description" to "..."))
```
