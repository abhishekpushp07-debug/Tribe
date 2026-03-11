# Tribe — Product Requirements Document

## Overview
World-class social media backend for the "Tribe" platform. Features tribes, content feeds, stories, reels, contests, leaderboards, and a full media pipeline.

## Backend URL
`https://tribal-architecture.preview.emergentagent.com`

## Core Architecture
- **Application**: Next.js monolithic API with service-oriented architecture
- **Database**: MongoDB
- **Media Storage**: Supabase Storage
- **Testing**: pytest (1,000+ tests)

## Service Layer Architecture (COMPLETED ✅)
Business logic extracted from monolithic handlers into dedicated service files:

### Service Files (1,620 lines total)
- `/app/lib/services/scoring.js` (266 lines) — Leaderboard: tiered viral bonuses (1K/5K/10K), 10-min cache, anti-cheat caps. **WIRED into tribes.js**
- `/app/lib/services/feed-ranking.js` (111 lines) — Algorithmic ranking: recency decay (6h half-life), engagement velocity, affinity boost, diversity penalty. **WIRED into feed.js** (public, following, college, tribe feeds)
- `/app/lib/services/story-service.js` (471 lines) — Story rail construction, sticker validation, privacy checks, expiry worker. **WIRED into stories.js**
- `/app/lib/services/reel-service.js` (236 lines) — Reel scoring, feed construction, viewer personalization. **IMPORTED by reels.js**
- `/app/lib/services/contest-service.js` (222 lines) — Contest scoring, lifecycle, season standings. **IMPORTED by tribe-contests.js**

### Handler Reduction
| Handler | Before | After | Saved |
|---------|--------|-------|-------|
| stories.js | 2,158 | 1,648 | -510 |
| tribes.js | 1,206 | 1,003 | -203 |
| tribe-contests.js | 1,600 | 1,538 | -62 |
| **Total** | **7,005** | **6,294** | **-711** |

### Test Results
- 15/16 tests passed (93.8% pass rate)
- All P0 (service wiring), P1 (story service), P2 (reel service), P3 (contest service) passing

## Next Priority
- **P1: B7 — Test Hardening + Gold Freeze** — Zero-flake suite
- **P1: Further service extraction** — Shared block/privacy utilities
- **P2: B8 — Infra, Observability, Scale Path** — Redis queues, separate test DB
- **P3: Audit Log TTL** — TTL policy on audit_logs

## Key Files
- `/app/lib/services/scoring.js` — Scoring service: leaderboard computation, tiered viral bonuses, caching
- `/app/lib/services/feed-ranking.js` — Feed ranking: algorithmic ranking with recency + engagement + affinity
- `/app/lib/services/story-service.js` — Story service: rail, stickers, privacy, expiry
- `/app/lib/services/reel-service.js` — Reel service: scoring, feed, personalization
- `/app/lib/services/contest-service.js` — Contest service: scoring, lifecycle, seasons
- `/app/lib/handlers/tribes.js` — Tribe handler (1003 lines, leaderboard delegated to scoring.js)
- `/app/lib/handlers/feed.js` — Feed handler (386 lines, ranking delegated to feed-ranking.js)
- `/app/lib/handlers/stories.js` — Stories handler (1648 lines, rail/stickers delegated to story-service.js)
- `/app/lib/handlers/reels.js` — Reels handler (1716 lines, imports from reel-service.js)
- `/app/lib/handlers/tribe-contests.js` — Contest handler (1538 lines, imports from contest-service.js)
- `/app/lib/supabase-storage.js` — Supabase Storage client
- `/app/lib/handlers/media.js` — Media upload/serve/delete handler
- `/app/tests/handlers/test_media_supabase.py` — 54 media pipeline tests
- `/app/tests/handlers/test_media_lifecycle.py` — 21 lifecycle tests

## Completed Stages
- B0: API Contract & Manifest
- B1: Canonical Identity & Media
- B2: Visibility & Feed Safety
- B3: Pages System (107 tests)
- B4: Core Social Gaps (72 tests)
- B5: Discovery & Hashtag Engine (77 tests)
- B5.1: Search Quality Upgrade (27 tests)
- B6: Notifications 2.0 (78 tests)
- Media Infra: Supabase Storage (54 tests)
- Media Lifecycle: Hardening (21 tests)
- Tribe/House Cutover: Legacy migration
- Tribe Leaderboard v1 & v2 (31 tests)
- Judge Hardening: 50-param audit
- Stage 9: World's Best Stories
- Stage 10: World's Best Reels
- **Service Layer Refactor: 5 services, 1620 lines extracted, 15/16 tests pass**

## 3rd Party Integrations
- **Supabase Storage**: Media storage and serving
- **ffmpeg**: Video thumbnailing

## Authentication
- Login: `POST /api/auth/login` with `{"phone":"<phone>","pin":"<pin>"}`
- Test users: `9999960001`, `9999960002`, `9000099001` (PIN: `1234`)
