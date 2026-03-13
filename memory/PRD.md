# Tribe — Product Requirements Document

## Product Vision
Build the world's best social media application for Indian college students.

## Tech Stack
- **Frontend**: Next.js (React)
- **Backend**: Next.js API Routes (monolithic)
- **Database**: MongoDB (95 collections)
- **Caching**: Redis (ioredis)
- **Media Storage**: Supabase Storage
- **Video Processing**: ffmpeg (HLS transcoding)
- **Testing**: pytest (121 tests, 100% pass rate)

## Architecture
- Central router: `/app/app/api/[[...path]]/route.js`
- Handlers: `/app/lib/handlers/` (22 handler files)
- Services: `/app/lib/services/` (6 service files)
- Cache layer: `/app/lib/cache.js`
- Feed ranking: `/app/lib/services/feed-ranking.js`
- Real-time: `/app/lib/realtime.js` (SSE via Redis Pub/Sub)
- Constants: `/app/lib/constants.js`

## Core Features (All Implemented — 435+ Endpoints)
1. Auth, Sessions, Token Rotation (access + refresh split)
2. Onboarding (age, college, profile, interests)
3. User profiles, settings, privacy, deactivation
4. Content (posts, polls, threads, carousels, drafts, scheduling)
5. Feeds (home, public, following, college, tribe, mixed, personalized)
6. Smart Feed Algorithm (multi-signal ranking)
7. Social interactions (like/dislike, save, share, hide, pin, archive)
8. Comments (threaded, likes, pin, edit, report)
9. Stories (24h expiry, 10 sticker types, reactions, highlights, close friends, SSE)
10. Reels (feeds, interactions, watch metrics, creator tools, series, duets, remixes)
11. Pages (CRUD, RBAC roles, follow, publishing, analytics, verification)
12. Events (CRUD, RSVP, reminders, moderation)
13. Tribes (21-tribe system, contests, seasons, salutes, governance)
14. Tribe Contests (full lifecycle, judging, voting, SSE live feeds)
15. Search (unified full-text, autocomplete, recent searches)
16. Hashtags (trending, feeds, stats)
17. Notifications (16 types, preferences, device push tokens)
18. Follow Requests (private accounts)
19. Analytics (overview, content, audience, reach, stories, reels)
20. Media upload (signed URLs, Supabase, HLS transcoding)
21. Board Notices, Authenticity Tags
22. College Claims & Discovery
23. Governance (board elections, proposals, voting)
24. Resources (study materials, voting, download tracking)
25. Content Distribution (3-stage pipeline)
26. Reports, Moderation & Appeals (auto + manual)
27. Content Quality Scoring (5-signal, 4-tier)
28. Content Recommendations
29. User Activity Status
30. Smart Suggestions
31. Blocks & Mutes
32. Anti-Abuse System
33. Redis Caching Layer (stampede protection, event-driven invalidation)
34. Admin & Ops (stats, abuse dashboard, health checks)

## Documentation Suite (DELIVERED)
| Document | Lines | Purpose |
|----------|-------|---------|
| `/app/API_DOCS.md` | 4,438 | Complete API reference (464 endpoints, 41 sections) |
| `/app/DATA_MODELS.md` | 1,082 | All 95 MongoDB collections with schemas & indexes |
| `/app/ANDROID_GUIDE.md` | 905 | Android/mobile integration guide (15 screens, auth/media/SSE flows) |
| `/app/CONSTANTS_REFERENCE.md` | 754 | All enums, error codes, config values, 21 tribes |
| `/app/FEATURE_SPECS.md` | 625 | Business logic, state machines, algorithms |
| **TOTAL** | **7,804** | **Complete frontend/Android handoff documentation** |

## Test Accounts
- Phone: `7777099001` / PIN: `1234`
- Phone: `7777099002` / PIN: `1234`

## What's Completed
- All 435+ backend API endpoints implemented and tested
- Redis caching layer integrated
- Smart Feed Algorithm with multi-signal ranking
- Complete pytest regression suite (121 tests, 100% pass rate)
- **World-class documentation suite (7,804 lines across 5 documents)**
- **Bug Fix (Feb 2026)**: Backend now honors `visibility` field from frontend for posts, reels, and story-to-post sharing. Added `HOUSE_ONLY`, `COLLEGE_ONLY`, `FOLLOWERS` to allowed visibility values. Fixed draft publish to restore intended visibility.

## Backlog
- Frontend UI development
- WebSocket real-time push notifications (P2)
- route.js refactoring (P3)
- A/B testing framework (P3)
- CDN integration for media delivery (P4)
