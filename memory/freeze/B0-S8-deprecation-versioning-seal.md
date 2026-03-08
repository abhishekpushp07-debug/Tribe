# B0-S8 — Deprecation, Legacy & Versioning Seal

**Status**: FROZEN  
**Freeze Date**: 2026-02-XX  
**Rule**: Legacy boundaries are hard. Future changes follow strict versioning rules. Android v1 builds on canonical truth only.

---

## 1. Legacy Declaration

### Houses — LEGACY (Do Not Build On)

| Entity | Status | What Happens |
|--------|--------|-------------|
| `houses` collection | LEGACY | Still in DB, read-only |
| `house_ledger` collection | LEGACY | No new writes |
| `user.houseId` | LEGACY FIELD | Still present on user object, but informational only |
| `user.houseSlug` | LEGACY FIELD | Same |
| `user.houseName` | LEGACY FIELD | Same |
| `GET /api/houses` | LEGACY ENDPOINT | Works but returns static data |
| `GET /api/houses/leaderboard` | LEGACY ENDPOINT | Works but frozen state |
| `GET /api/houses/{idOrSlug}` | LEGACY ENDPOINT | Works but no updates |
| `GET /api/feed/house/{houseId}` | LEGACY ENDPOINT | Works but no new content |
| `POST /api/house-points` | **DEPRECATED (410)** | Returns HTTP 410 GONE |

### Android v1 Rules for Houses
- **DO NOT** build any house-related UI screens
- **DO NOT** use house-related fields for grouping/identity
- House fields on user object MAY be displayed as "legacy info" or ignored entirely
- **Tribe is the ONLY canonical identity group**

### Tribe — CANONICAL (Build Everything On This)

| Entity | Status |
|--------|--------|
| `tribes` collection | CANONICAL |
| `user_tribe_memberships` | CANONICAL |
| `tribe_salute_ledger` | CANONICAL |
| `tribe_standings` | CANONICAL |
| `tribe_seasons` | CANONICAL |
| `tribe_contests` | CANONICAL |
| All `/api/tribes/*` endpoints | CANONICAL |
| All `/api/tribe-contests/*` endpoints | CANONICAL |

---

## 2. Versioning Rules (Going Forward)

### Rule V1: No Breaking Changes Without Versioning
The following changes are **BREAKING** and require versioning:

| Change Type | Example | Required Action |
|------------|---------|----------------|
| Field rename | `userId` → `authorId` | New version OR new endpoint |
| Field removal | Removing `houseId` from user | Deprecation period first |
| Enum value meaning change | `PUBLISHED` meaning changes | New version |
| Response nesting change | `{ user: {...} }` → `{ data: { user: {...} } }` | New version |
| Status lifecycle change | Adding new required state | New version |
| Error code semantics change | `NOT_FOUND` meaning broadens | New error code |
| Pagination format change | cursor → page | New endpoint |
| Authentication change | Token format change | Migration period |

### Rule V2: Additive Changes Are Always Safe
The following changes are **NON-BREAKING** and require NO versioning:

| Change Type | Example |
|------------|---------|
| New optional field in response | Adding `tribeCode` to user |
| New endpoint | `GET /api/tribes/{id}/activity` |
| New enum value | New contest type `quiz_battle` |
| New query parameter (optional) | `?includeArchived=true` |
| New event type in SSE | `entry.flagged` |
| New analytics surface | `/api/admin/tribes/insights` |
| Performance improvement | Faster feed loading |

### Rule V3: Deprecation Protocol
When removing a feature or endpoint:

```
1. Mark endpoint/field as DEPRECATED in documentation
2. Return `X-Deprecated: true` header on responses
3. Keep working for minimum 90 days
4. After 90 days: return 410 GONE with message
5. After 180 days: endpoint may be removed entirely
```

### Rule V4: Version Naming
If versioning is ever needed:
- URL-based: `/api/v2/tribes/standings`
- Old endpoint continues to work at `/api/tribes/standings`
- Both versions documented
- v1 gets deprecation notice after v2 is stable

---

## 3. Current Deprecation Registry

| What | Status | Since | Returns |
|------|--------|-------|---------|
| `POST /api/house-points` | DEPRECATED | Stage 12X | HTTP 410 GONE |
| House system (all) | LEGACY | Stage 12 | Works but frozen |
| `awardHousePoints()` function | REMOVED | Stage 12X | Code commented out |

### Nothing Else Is Deprecated
All other endpoints, fields, and contracts documented in B0-S1 through B0-S7 are **ACTIVE AND CANONICAL**.

---

## 4. Contract Stability Guarantees

### What Android v1 Can Rely On

| Guarantee | Duration |
|-----------|----------|
| All ANDROID_V1_USE endpoints will not break | Until Android v2 exists |
| All entity JSON shapes (B0-S3) are stable | Indefinite (additive only) |
| All state machines (B0-S4) are stable | Indefinite (additive states only) |
| All SSE event names (B0-S6) are stable | Indefinite (new events additive) |
| Error codes are stable | Indefinite (new codes additive) |
| Pagination patterns per endpoint are stable | Indefinite |
| Auth mechanism (bearer token) is stable | Indefinite |
| 21 tribes are permanent | Indefinite (no tribe added/removed) |

### What May Change (Non-Breaking)
| Area | Possible Change |
|------|----------------|
| New fields on existing objects | Optional fields added |
| New endpoints | New features |
| New enum values | New contest types, event categories, etc. |
| New SSE event types | New real-time events |
| Performance improvements | Faster responses |
| New admin endpoints | New admin tools |
| Internal processing | Behind-the-scenes optimization |

---

## 5. Error Code Freeze

### Universal Error Codes (Never Change Meaning)
| Code | HTTP | Meaning |
|------|------|---------|
| `VALIDATION_ERROR` | 400 | Bad input |
| `UNAUTHORIZED` | 401 | Missing/invalid token |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource doesn't exist |
| `CONFLICT` | 409 | Duplicate action |
| `GONE` | 410 | Expired or deprecated |
| `CONTENT_REJECTED` | 422 | AI moderation rejected |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

### Feature-Specific Error Codes (Frozen)
| Code | Context |
|------|---------|
| `AGE_REQUIRED` | Onboarding not complete |
| `CHILD_RESTRICTED` | Child cannot perform action |
| `FILE_TOO_LARGE` | Media upload size exceeded |
| `INVALID_MIME_TYPE` | Unsupported file type |
| `DURATION_EXCEEDED` | Video too long |
| `DUPLICATE_CODE` | Contest code already exists |
| `INVALID_TRANSITION` | Invalid state machine transition |
| `SELF_VOTE_BLOCKED` | Cannot vote on own contest entry |
| `VOTE_CAP_REACHED` | Exceeded max votes per contest |
| `ALREADY_ENTERED` | Duplicate contest entry |
| `CONTEST_NOT_ACCEPTING` | Contest not in ENTRY_OPEN state |
| `NO_TRIBE` | User must have tribe to enter contest |
| `CLAIM_COOLDOWN` | Must wait before re-submitting claim |
| `ACTIVE_CLAIM_EXISTS` | Already has a pending claim |
| `MAX_CLOSE_FRIENDS` | Close friends limit reached (500) |
| `MAX_HIGHLIGHTS` | Highlights limit reached |
| `STORY_EXPIRED` | Story has expired |
| `BLOCKED` | Blocked user interaction |
| `BANNED` | Account is banned |
| `SUSPENDED` | Account is suspended |

---

## 6. 21 Tribes — Permanent Freeze

The 21 tribes are **permanent and immutable**. No tribe will be added, removed, or renamed.

| tribeCode | Frozen? |
|-----------|---------|
| SOMNATH | YES |
| JADUNATH | YES |
| PIRU | YES |
| KARAM | YES |
| RANE | YES |
| SALARIA | YES |
| THAPA | YES |
| JOGINDER | YES |
| SHAITAN | YES |
| HAMID | YES |
| TARAPORE | YES |
| EKKA | YES |
| SEKHON | YES |
| HOSHIAR | YES |
| KHETARPAL | YES |
| BANA | YES |
| PARAMESWARAN | YES |
| PANDEY | YES |
| YADAV | YES |
| SANJAY | YES |
| BATRA | YES |

Each tribe's `tribeName`, `heroName`, `quote`, `animalIcon`, `primaryColor`, `secondaryColor` are also frozen.

---

## 7. Rate Limit Freeze

| Scope | Limit | Window |
|-------|-------|--------|
| Global per IP | 500 requests | Per minute |
| Login attempts | 5 failures | Then lockout |
| Resource creation | 10 | Per hour |
| Event creation | 10 | Per hour |
| Story creation | 30 | Per hour |
| Reel creation | 20 | Per hour |
| Resource download | 50 | Per day |
| Vote per contest | `maxVotesPerUser` (default 5) | Per contest lifetime |

All rate limits return **HTTP 429** with `Retry-After` header.

---

## 8. Final Seal Statement

### This document, combined with B0-S1 through B0-S7, constitutes the complete Backend Source of Truth Freeze for Tribe.

### What is frozen:
- Domain vocabulary (B0-S1)
- Endpoint register with labels (B0-S2)
- Response JSON shapes (B0-S3)
- State machines and transitions (B0-S4)
- Role and permission matrix (B0-S5)
- SSE real-time contracts (B0-S6)
- Media upload contracts (B0-S7)
- Legacy boundaries and versioning rules (B0-S8)

### Android v1 is SAFE TO START building on this canonical truth.

### Future changes will be:
- Additive only
- Versioned if breaking
- Documented before implementation
- Backward-compatible by default

---

## PASS Gate Verification

- [x] Houses declared LEGACY — hard boundary documented
- [x] Tribes declared CANONICAL — permanent
- [x] Breaking vs non-breaking change rules documented
- [x] Deprecation protocol documented (90-day + 180-day)
- [x] Version naming convention documented
- [x] All error codes frozen with exact meanings
- [x] 21 tribes permanently frozen
- [x] Rate limits frozen
- [x] Contract stability guarantees documented with duration
- [x] Final seal statement issued
- [x] Android v1 declared safe to start

**B0-S8 STATUS: FROZEN**

---

# STAGE B0 — BACKEND SOURCE OF TRUTH FREEZE: COMPLETE

All 8 sub-stages PASSED:
- B0-S1: Domain Freeze ✅
- B0-S2: Endpoint Freeze ✅
- B0-S3: Response Contract Freeze ✅
- B0-S4: State Machine Freeze ✅
- B0-S5: Permission Freeze ✅
- B0-S6: SSE Contract Freeze ✅
- B0-S7: Media Upload Freeze ✅
- B0-S8: Deprecation & Versioning Seal ✅

**"Backend source of truth abhi ke liye frozen hai. Android v1 safe to start."**
