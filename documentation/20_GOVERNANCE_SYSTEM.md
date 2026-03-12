# 20 — Governance System

**Source**: `/app/lib/handlers/governance.js`

---

## 1. Overview

Democratic governance for college communities. Each college has an 11-member board. Users can apply for seats, vote on applications, and create/vote on proposals.

---

## 2. Board Structure

- **Board size**: 11 seats per college
- **Application window**: 7 days
- **Proposal voting period**: 3 days

---

## 3. Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/governance/college/:collegeId/board` | 🔓 | Current board members |
| `POST` | `/api/governance/college/:collegeId/apply` | 🔑 | Apply for board seat |
| `GET` | `/api/governance/college/:collegeId/applications` | 🔓 | Pending applications |
| `POST` | `/api/governance/applications/:appId/vote` | 🔑 | Vote on application |
| `POST` | `/api/governance/college/:collegeId/proposals` | 🔑 | Create proposal |
| `GET` | `/api/governance/college/:collegeId/proposals` | 🔓 | List proposals |
| `POST` | `/api/governance/proposals/:proposalId/vote` | 🔑 | Vote on proposal |
| `POST` | `/api/governance/college/:collegeId/seed-board` | 🛡️ | Seed initial board |

---

## 4. Board Seats (Collection: `board_seats`)

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Seat ID |
| `collegeId` | string | College |
| `userId` | string | Seated member |
| `seatNumber` | number | Seat number (1-11) |
| `status` | enum | `ACTIVE`, `RESIGNED`, `REMOVED` |
| `appointedAt` | Date | When seated |

---

## 5. Applications (Collection: `board_applications`)

### Apply for Seat
`POST /api/governance/college/:collegeId/apply`

```json
{
  "statement": "I want to contribute to our college community by..."
}
```

**Requirements**:
- Must be a member of the college
- Cannot already be on board
- Cannot have a pending application
- Must have vacant seats

### Application Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Application ID |
| `collegeId` | string | College |
| `userId` | string | Applicant |
| `statement` | string | Application statement (max 500) |
| `status` | enum | `PENDING`, `APPROVED`, `REJECTED` |
| `votes` | object | `{ approve: number, reject: number }` |
| `voters` | string[] | User IDs who voted |
| `expiresAt` | Date | Auto-expire after 7 days |

### Vote on Application
`POST /api/governance/applications/:appId/vote`

```json
{
  "vote": "APPROVE | REJECT"
}
```

**Rules**:
- Must be a board member to vote
- One vote per member per application
- Majority vote (>50% of board) auto-approves/rejects

---

## 6. Proposals (Collection: `board_proposals`)

### Create Proposal
`POST /api/governance/college/:collegeId/proposals`

```json
{
  "title": "Weekly Movie Night",
  "description": "Proposal to host weekly movie screenings...",
  "type": "EVENT | RULE_CHANGE | BUDGET | OTHER"
}
```

**Requirements**:
- Must be a board member of the college

### Proposal Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Proposal ID |
| `collegeId` | string | College |
| `authorId` | string | Proposer |
| `title` | string | Title |
| `description` | string | Details |
| `type` | enum | Proposal type |
| `status` | enum | `OPEN`, `PASSED`, `REJECTED`, `EXPIRED` |
| `votes` | object | `{ for: number, against: number, abstain: number }` |
| `voters` | string[] | User IDs who voted |
| `votingEndsAt` | Date | Auto-close after 3 days |

### Vote on Proposal
`POST /api/governance/proposals/:proposalId/vote`

```json
{
  "vote": "FOR | AGAINST | ABSTAIN"
}
```

**Rules**:
- Any college member can vote (not just board members)
- One vote per member
- Simple majority (FOR > AGAINST) passes proposal

---

## 7. Board Seeding

`POST /api/governance/college/:collegeId/seed-board` (Admin only)

Seeds the initial board with specified users. Used for bootstrapping new college communities.

```json
{
  "members": ["user-id-1", "user-id-2", ...]
}
```

---

## 8. Android Integration

### Board View
```kotlin
val board = api.get("/api/governance/college/$collegeId/board")
// Display: board members with seat numbers, names, avatars
// Show: totalSeats (11), filledSeats, vacantSeats
```

### Apply for Seat
```kotlin
api.post("/api/governance/college/$collegeId/apply", 
    mapOf("statement" to "My application..."))
```

### Proposals
```kotlin
val proposals = api.get("/api/governance/college/$collegeId/proposals")
api.post("/api/governance/proposals/$id/vote", mapOf("vote" to "FOR"))
```
