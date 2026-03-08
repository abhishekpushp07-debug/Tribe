# Tribe — Trust-First Social Platform for Indian College Students

## Vision
World-class social media backend for Indian college students, built stage-by-stage with proof-based acceptance.

## Core Architecture
- **Backend**: Monolithic Next.js API
- **Database**: MongoDB (35+ collections, 100+ indexes)
- **Cache**: Redis (with in-memory fallback)
- **Real-time**: SSE via Redis Pub/Sub + EventEmitter fallback
- **Moderation**: OpenAI GPT-4o-mini
- **Storage**: Emergent Object Storage

## Stage Status

| Stage | Feature | Status | Test Results |
|-------|---------|--------|-------------|
| 1 | Appeal Decision Workflow | PASSED | — |
| 2 | College Claim Workflow | PASSED | — |
| 3 | Story Expiry Cleanup | PASSED | — |
| 4 | Distribution Ladder | PASSED (2 old test failures) | — |
| 5 | Notes/PYQs Library | **PASSED** | — |
| 9 | World's Best Stories | **PASSED** | Proof pack delivered |
| 10 | World's Best Reels | **PASSED** | 53/53 manual + 46/46 auto + 39/39 IXSCAN |
| **6** | **World's Best Events + RSVP** | **PROOF PACK DELIVERED** | **43/43 auto (Stage 6+7) + 32/32 IXSCAN** |
| **7** | **World's Best Board Notices + Authenticity** | **PROOF PACK DELIVERED** | **43/43 auto (Stage 6+7) + 32/32 IXSCAN** |
| 8 | OTP Challenge Flow | REMOVED (user request) | — |
| 11 | Scale/Reliability Excellence | UPCOMING | — |
| 12 | Final Launch Readiness Gate | UPCOMING | — |

## Stage 6: Events + RSVP — Summary
- **22 endpoints**, 4 collections (events, event_rsvps, event_reports, event_reminders)
- **16 indexes**, all IXSCAN, zero COLLSCAN
- Features: full lifecycle (create/edit/publish/cancel/archive), 7 categories, capacity+waitlist, RSVP with auto-promote, block integration, reports+auto-hold@3, reminders, admin moderation, counter integrity
- Full proof: `/app/memory/stage_6_7_deep_proof_pack.md`

## Stage 7: Board Notices + Authenticity — Summary
- **17 endpoints**, 4 collections (board_notices, board_seats, authenticity_tags, notice_acknowledgments)
- **16 indexes**, all IXSCAN, zero COLLSCAN
- Features: notice lifecycle (create→review→publish→pin→archive), 6 categories, 4 priority levels, max 3 pins, acknowledgments (read receipts), authenticity tag system (VERIFIED/USEFUL/OUTDATED/MISLEADING), moderation workflow, admin analytics
- Full proof: `/app/memory/stage_6_7_deep_proof_pack.md`

## Key Files
- `/app/lib/handlers/events.js` — Stage 6 handler
- `/app/lib/handlers/board-notices.js` — Stage 7 handler
- `/app/lib/handlers/reels.js` — Stage 10 handler
- `/app/lib/handlers/stories.js` — Stage 9 handler
- `/app/lib/db.js` — All indexes (38 reels + 16 events + 16 notices = 70 new)
- `/app/app/api/[[...path]]/route.js` — Route dispatcher

## Proof Packs
- `/app/memory/stage_10_deep_proof_pack.md` — Reels
- `/app/memory/stage_6_7_deep_proof_pack.md` — Events + Notices

## Next Tasks
1. User verdict on Stage 6 + 7
2. Stage 11: Scale / Reliability / Disaster Excellence
3. Stage 12: Final Launch Readiness Gate
