# 11 — Monetization & Virtual Goods

**Status**: No direct monetization layer exists in the current codebase. The system uses a **virtual points economy** (Salutes) and a **fund accounting** model tied to the Tribe Contest system.

---

## 1. Salute Ledger (Virtual Currency)

Salutes are the platform's engagement points, awarded to tribes (not individuals) for contest wins, content bonuses, and admin awards.

### Schema: `tribe_salute_ledger`

| Field | Type | Description |
|-------|------|-------------|
| `id` | string (UUID) | Ledger entry ID |
| `tribeId` | string | Tribe receiving salutes |
| `amount` | number | Positive = credit, negative = debit |
| `reason` | enum | `CONTEST_WIN`, `CONTEST_RUNNER_UP`, `CONTENT_BONUS`, `ADMIN_AWARD`, `ADMIN_DEDUCT`, `REVERSAL`, `MIGRATION_CARRYOVER`, `WEEKLY_BONUS` |
| `contestId` | string? | Linked contest |
| `seasonId` | string? | Linked season |
| `awardedBy` | string | User ID or `SYSTEM` |
| `note` | string? | Free-text explanation |
| `createdAt` | Date | Timestamp |

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/tribes/:id/salutes` | Salute history for tribe |
| `POST` | `/api/admin/tribe-salutes/adjust` | Manual salute adjustment |
| `GET` | `/api/tribes/:id/fund` | Tribe fund info |

### Salute Distribution (Contest Resolution)

When a contest is resolved (`POST /admin/tribe-contests/:id/resolve`):

```
Default Distribution:
  1st place: 100 salutes
  2nd place: 60 salutes
  3rd place: 30 salutes
  Participation: 5 salutes each
```

Distribution is configurable per-contest via the `saluteDistribution` field.

---

## 2. Tribe Fund Accounting

Each tribe has a virtual fund tracked in the `tribes` collection.

### Fund Fields on Tribe

| Field | Type | Description |
|-------|------|-------------|
| `totalSalutes` | number | Cumulative salute count |
| `fundBalance` | number | Current fund balance (INR) |
| `fundTarget` | number | Target (default: ₹10,00,000) |

### Annual Award Resolution

`POST /api/admin/tribe-awards/resolve` — Resolves the annual tribe award, distributing the prize fund based on final standings.

---

## 3. House Points (Deprecated)

The legacy `house-points` system at `/api/house-points/*` returns HTTP 410 GONE with:
```json
{
  "error": "House points system deprecated. Use tribe salutes via /tribe-contests",
  "code": "DEPRECATED"
}
```

**Migration**: All house point data was carried over to tribe salutes via `MIGRATION_CARRYOVER` ledger entries during the house→tribe migration.

---

## 4. Future Monetization Hooks

While no payment processing exists today, the architecture supports:

- **Contest entry fees** → `tribe_contests.entryFee` field (currently unused)
- **Page monetization** → Pages support `category: BUSINESS` with analytics
- **Resource downloads** → Download tracking via `POST /resources/:id/download` provides usage data for future freemium gating

---

## Android Integration Notes

**Salutes display**: Use `GET /api/tribes/:id` → `totalSalutes` for tribe profile.

**Fund display**: Use `GET /api/tribes/:id/fund` for fund balance and target.

**Leaderboard**: Use `GET /api/tribes/leaderboard` for ranked tribe list with salute counts.

**No payment SDK integration needed** — all virtual currency operations are server-side.
