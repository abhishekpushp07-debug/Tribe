# Tribe — Tribes & Contests System Complete Reference

> 21 Param Vir Chakra tribes with engagement scoring, seasons, and full contest lifecycle.
> 1,235 + 1,500+ lines of handler code.

---

## 1. The 21 Tribes

Each tribe honors a Param Vir Chakra recipient (India's highest wartime military decoration).

| # | Code | Hero | Animal | Color |
|---|------|------|--------|-------|
| 1 | SOMNATH | Maj Somnath Sharma | lion | #B71C1C |
| 2 | JADUNATH | Naik Jadunath Singh | tiger | #E65100 |
| 3 | PIRU | CHM Piru Singh | panther | #4A148C |
| 4 | KARAM | L/Naik Karam Singh | wolf | #1B5E20 |
| 5 | RANE | 2nd Lt Rama Raghoba Rane | rhino | #37474F |
| 6 | SALARIA | Capt Gurbachan Singh Salaria | falcon | #0D47A1 |
| 7 | THAPA | Maj Dhan Singh Thapa | snow_leopard | #006064 |
| 8 | JOGINDER | Sub Joginder Singh | bear | #5D4037 |
| 9 | SHAITAN | Maj Shaitan Singh | eagle | #263238 |
| 10 | HAMID | CQMH Abdul Hamid | cobra | #1A237E |
| 11 | TARAPORE | Lt Col AB Tarapore | bull | #880E4F |
| 12 | EKKA | L/Naik Albert Ekka | jaguar | #2E7D32 |
| 13 | SEKHON | Fg Off NJ Singh Sekhon | hawk | #1565C0 |
| 14 | HOSHIAR | Maj Hoshiar Singh | bison | #6D4C41 |
| 15 | KHETARPAL | 2nd Lt Arun Khetarpal | stallion | #3E2723 |
| 16 | BANA | Naib Sub Bana Singh | mountain_wolf | #004D40 |
| 17 | PARAMESWARAN | Maj R Parameswaran | black_panther | #311B92 |
| 18 | PANDEY | Lt Manoj Kumar Pandey | leopard | #C62828 |
| 19 | YADAV | Grenadier YS Yadav | iron_tiger | #AD1457 |
| 20 | SANJAY | Rfn Sanjay Kumar | honey_badger | #2C3E50 |
| 21 | BATRA | Capt Vikram Batra | phoenix_wolf | #D32F2F |

---

## 2. Tribe Assignment

### Algorithm (Deterministic)
```javascript
function assignTribe(userId) {
  const hash = SHA256(userId)
  const index = parseInt(hash.slice(0, 8), 16) % 21
  return TRIBES[index]
}
```

- **Deterministic**: Same userId always → same tribe
- **Permanent**: Cannot be changed by user
- **Even distribution**: SHA-256 mod 21 gives near-uniform distribution
- **Admin override**: POST /admin/tribes/reassign can override

---

## 3. Engagement Scoring (v3)

### Points Table
| Action | Points |
|--------|--------|
| Upload (post/reel/story) | 100 |
| Like received | 10 |
| Comment received | 20 |
| Share received | 50 |
| Story reaction received | 15 |
| Story reply received | 25 |

### Viral Bonuses
| Threshold | Bonus | Label |
|-----------|-------|-------|
| 1,000 likes on reel | +1,000 | viral |
| 5,000 likes on reel | +3,000 | super_viral |
| 10,000 likes on reel | +5,000 | mega_viral |

*Cumulative: 12K likes = 1000 + 3000 + 5000 = 9000 bonus*

### Anti-Cheat Upload Caps
| Period | Max Uploads Per User |
|--------|---------------------|
| 7 days | 350 |
| 30 days | 1,500 |
| 90 days | 4,500 |
| All time | 50,000 |

---

## 4. Contest Lifecycle

### State Machine
```
DRAFT ──publish──> PUBLISHED ──open──> ENTRY_OPEN
                       │                   │
                       └── cancel          └── cancel
                                               │
ENTRY_CLOSED <──close── ENTRY_OPEN             │
     │                                         │
     └── evaluate ──> EVALUATING ── cancel ────>│
                          │                     │
                          └── lock ──> LOCKED   │
                                         │      │
                                   resolve│     │
                                         ▼      ▼
                                      RESOLVED  CANCELLED
```

### Contest Entry Flow
```
1. User checks GET /tribe-contests (finds open contest)
2. User submits POST /tribe-contests/:id/enter
   - Must have tribe membership
   - Per-tribe entry caps enforced
   - Content duplication check
3. Other users vote: POST /tribe-contests/:id/vote
   - Can't vote for own entry
   - One vote per user per entry
4. Judges score: POST /admin/tribe-contests/:id/judge-score
5. Admin resolves: POST /admin/tribe-contests/:id/resolve
   - Computes final scores
   - Awards salute points to winning tribes
```

### Scoring Formula
```
finalScore = (judgeScore × judgeWeight) + (publicVoteNormalized × voteWeight)

Default: judgeWeight=0.7, voteWeight=0.3
```

---

## 5. Live SSE Feeds

### Contest Live Scoreboard
```
GET /api/tribe-contests/:id/live

Events:
  - entry_submitted: { entryId, tribeId, userId }
  - vote_cast: { entryId, voteCount }
  - score_update: { entryId, score }
  - rank_change: { entryId, oldRank, newRank }
  - contest_state_change: { contestId, newStatus }
```

### Season Live Standings
```
GET /api/tribe-contests/seasons/:id/live-standings
```

---

## 6. Seasons

### Season Lifecycle
```
POST /admin/tribe-seasons → Create season
GET /tribe-contests/seasons → List all seasons
GET /tribe-contests/seasons/:id/standings → Season standings
```

---

## 7. Salute System

### Immutable Ledger
All salute point changes are recorded as immutable ledger entries:

```json
{
  "tribeId": "...",
  "amount": 1000,
  "reason": "CONTEST_WIN",
  "description": "1st place in Photography Contest",
  "contestId": "...",
  "seasonId": "...",
  "awardedBy": "admin-uuid"
}
```

### Salute Reasons
```
CONTEST_WIN, CONTEST_RUNNER_UP, CONTENT_BONUS,
ADMIN_AWARD, ADMIN_DEDUCT, REVERSAL,
MIGRATION_CARRYOVER, WEEKLY_BONUS
```

---

*Tribes & Contests v3.0.0 — 21 tribes, full contest lifecycle*
