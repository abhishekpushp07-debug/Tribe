# 12 — Tribes & Houses System

**Source**: `/app/lib/handlers/tribes.js`, `/app/lib/tribe-constants.js`, `/app/lib/services/scoring.js`

---

## 1. Overview

Tribe is the **core identity unit** of the platform. Every user belongs to exactly one of 21 tribes, each named after an Indian military hero. The system replaces the legacy "Houses" concept with a richer governance, contest, and fund model.

---

## 2. The 21 Tribes

Tribes are auto-assigned at registration using a deterministic hash of the user's UUID (`assignTribeV3`).

Each tribe has:
- `tribeCode` — e.g., `SHAURYA`, `VEER`, `AGNI`
- `tribeName` — Display name
- `heroName` — Named Indian military hero
- `paramVirChakraName` — Linked award recipient
- `animalIcon` — Visual mascot
- `primaryColor`, `secondaryColor` — Branding
- `quote` — Inspirational motto
- `sortOrder` — Display ranking

### Tribe Schema (Collection: `tribes`)

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Tribe ID |
| `tribeCode` | string | Unique code |
| `tribeName` | string | Display name |
| `heroName` | string | Military hero |
| `animalIcon` | string | Mascot icon |
| `primaryColor` | string | Hex color |
| `membersCount` | number | Total members |
| `totalSalutes` | number | Cumulative salutes |
| `isActive` | boolean | Active status |

---

## 3. Tribe Assignment

### At Registration
```
POST /api/auth/register
→ assignTribeV3(userId)
→ Deterministic hash → one of 21 tribes
→ Records in `user_tribe_memberships` + updates user document
```

### Membership Schema (Collection: `user_tribe_memberships`)

| Field | Type | Description |
|-------|------|-------------|
| `userId` | string | User ID |
| `tribeId` | string | Tribe ID |
| `tribeCode` | string | Tribe code |
| `assignmentMethod` | enum | `SIGNUP_AUTO_V3`, `ADMIN_REASSIGN`, `MIGRATION` |
| `isPrimary` | boolean | Always `true` for current |
| `status` | enum | `ACTIVE`, `LEFT`, `MIGRATED` |
| `reassignmentCount` | number | Number of reassigns |

---

## 4. API Endpoints

### Public

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/tribes` | List all 21 tribes |
| `GET` | `/api/tribes/leaderboard` | Engagement-ranked leaderboard |
| `GET` | `/api/tribes/standings/current` | Current season standings |
| `GET` | `/api/tribes/:id` | Tribe detail (enriched with season rank) |
| `GET` | `/api/tribes/:id/members` | Member list (paginated) |
| `GET` | `/api/tribes/:id/board` | Tribe board governance |
| `GET` | `/api/tribes/:id/fund` | Fund info |
| `GET` | `/api/tribes/:id/salutes` | Salute history |
| `GET` | `/api/tribes/:id/feed` | Tribe content feed |
| `GET` | `/api/tribes/:id/events` | Tribe events |
| `GET` | `/api/tribes/:id/stats` | Engagement statistics |

### Authenticated

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/me/tribe` | My tribe info + membership |
| `GET` | `/api/users/:id/tribe` | Another user's tribe |
| `POST` | `/api/tribes/:id/join` | Join a tribe |
| `POST` | `/api/tribes/:id/leave` | Leave a tribe |
| `POST` | `/api/tribes/:id/cheer` | Cheer for your tribe |

### Admin

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/admin/tribes/distribution` | Distribution analytics |
| `POST` | `/api/admin/tribes/reassign` | Reassign user |
| `POST` | `/api/admin/tribes/migrate` | House→Tribe migration |
| `POST` | `/api/admin/tribes/boards` | Create/update board |
| `POST` | `/api/admin/tribe-seasons` | Create/manage season |
| `GET` | `/api/admin/tribe-seasons` | List seasons |

---

## 5. Tribe Board Governance

Each tribe has board roles:
```
CAPTAIN, VICE_CAPTAIN, WELFARE_LEAD, EVENTS_LEAD,
FINANCE_LEAD, DISCIPLINE_LEAD, COMMUNITY_LEAD
```

Board data is accessible via `GET /api/tribes/:id/board`.

---

## 6. Seasons

Seasons are time-bounded competition periods.

### Season Schema (Collection: `tribe_seasons`)

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Season ID |
| `name` | string | Season name |
| `year` | number | Year |
| `startAt` | Date | Start date |
| `endAt` | Date | End date |
| `status` | enum | `DRAFT`, `ACTIVE`, `COMPLETED` |
| `prizePool` | number | Total prize (INR) |

### Standings

`GET /api/tribes/standings/current` returns all 21 tribes ranked by salute count within the active season.

---

## 7. Leaderboard & Scoring

### Engagement Leaderboard
`GET /api/tribes/leaderboard` — Tribes ranked by a composite engagement score:
- Total salutes
- Member count  
- Content volume
- Contest wins

Computed by `computeLeaderboard()` in `/app/lib/services/scoring.js`.

### Cache Strategy
- Leaderboard cached with `CacheNS.HOUSES_LIST` / `CacheNS.HOUSE_LEADERBOARD`
- TTL: Short (30s–60s)
- Invalidated on salute events

---

## 8. Legacy House System (Bridge)

The houses system (`/api/houses/*`) is still accessible but reads from the same underlying data. The mapping from old house IDs to new tribe IDs is handled by `HOUSE_TO_TRIBE_MAP` in `tribe-constants.js`.

| Legacy Route | Status | Maps To |
|--------------|--------|---------|
| `GET /houses` | Active | Returns tribes as houses |
| `GET /houses/leaderboard` | Active | Tribe leaderboard |
| `GET /houses/:idOrSlug` | Active | Tribe by ID/slug |
| `GET /houses/:idOrSlug/members` | Active | Tribe members |
| `GET /feed/house/:houseId` | Active | Tribe feed |

---

## 9. Tribe Stats (`GET /api/tribes/:id/stats`)

Returns comprehensive statistics:
```json
{
  "tribe": { ... },
  "members": { "total": 1200, "active30d": 890 },
  "content": { "postsThisWeek": 340, "reelsThisWeek": 45 },
  "engagement": { "likesThisWeek": 5200, "commentsThisWeek": 1100 },
  "contests": { "wins": 8, "entriesThisSeason": 120 },
  "salutes": { "total": 2400, "thisMonth": 180 }
}
```

---

## Android Implementation

### Tribe Profile Screen
```kotlin
val tribe = api.get("/api/tribes/$tribeId")
// Display: tribeName, heroName, animalIcon, primaryColor, membersCount, totalSalutes
```

### Leaderboard Screen
```kotlin
val leaderboard = api.get("/api/tribes/leaderboard")
// items: ranked list with { tribeName, totalSalutes, rank, membersCount }
```

### User's Tribe Badge
```kotlin
val myTribe = api.get("/api/me/tribe")
// Show tribe badge on profile: tribeCode, tribeName, animalIcon, primaryColor
```
