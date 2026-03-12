# Tribe — Product Requirements Document

## Product Vision
Build the world's best social media application for Indian college students.

## Tech Stack
- **Frontend**: Next.js (React)
- **Backend**: Next.js API Routes (monolithic)
- **Database**: MongoDB
- **Caching**: Redis (ioredis)
- **Media Storage**: Supabase Storage
- **Video Processing**: ffmpeg
- **Testing**: pytest (121 tests, 100% pass rate)

## Architecture
- Central router: `/app/app/api/[[...path]]/route.js`
- Handlers: `/app/lib/handlers/` (modular, service-oriented)
- Services: `/app/lib/services/`
- Cache layer: `/app/lib/cache.js` + `/app/lib/cache-utils.js`
- Feed ranking: `/app/lib/services/feed-ranking.js`

## Core Features (All Implemented)
1. Auth (register, login, refresh tokens, sessions, PIN change)
2. Onboarding (age, college, profile, consent)
3. User profiles, settings, privacy, interests, deactivation
4. Content system (posts, polls, threads, carousels, drafts, scheduling)
5. Feed system (home, public, following, college, tribe, mixed, personalized)
6. Smart Feed Algorithm (multi-signal ranking)
7. Social interactions (like/dislike, save, share/repost, hide, pin, archive)
8. Full comments system (threaded, likes, pin, edit, report)
9. Stories (24h expiry, stickers, reactions, replies, highlights, close friends, SSE)
10. Reels (create, feeds, interactions, watch metrics, creator tools, series, duets)
11. Pages (CRUD, roles, follow, publishing, analytics, verification)
12. Events (CRUD, RSVP, waitlist, reminders, moderation)
13. Tribes (21-tribe system, governance, contests, salutes, seasons)
14. Tribe Contests (full lifecycle, judging, voting, SSE live feeds)
15. Search (unified full-text, autocomplete, recent searches)
16. Hashtags (trending, feeds, stats)
17. Notifications (grouped, preferences, device push tokens)
18. Follow Requests (private accounts)
19. Analytics (overview, content, audience, reach, stories, reels)
20. Media upload (signed URLs, Supabase, HLS transcoding)
21. Board Notices (CRUD, moderation, acknowledgments)
22. Authenticity Tags
23. College Claims & Discovery
24. Governance (board elections, proposals, voting)
25. Resources (study materials, voting, download tracking)
26. Content Distribution (admin pipeline)
27. Reports, Moderation & Appeals
28. Content Quality Scoring
29. Content Recommendations
30. User Activity Status (heartbeat, friends activity)
31. Smart Suggestions (people, trending, tribes)
32. Blocks & Mutes
33. Admin & Ops (stats, abuse dashboard, health checks)
34. Redis Caching Layer

## Test Accounts
- Phone: `7777099001` / PIN: `1234`
- Phone: `7777099002` / PIN: `1234`

## Documents
- `/app/API_DOCS.md` — Complete API documentation (4,438 lines, 464 endpoints, 41 sections)
- `/app/memory/CHANGELOG.md` — Development history
- `/app/backend/tests/` — pytest regression suite (19 files, 121 tests)

## What's Completed
- All 435+ backend API endpoints implemented and tested
- Redis caching layer integrated
- Smart Feed Algorithm with multi-signal ranking
- Complete pytest regression suite (100% pass rate)
- **Exhaustive API documentation delivered (v3.0.0)**

## Backlog
- Frontend UI development
- WebSocket real-time push notifications (P2)
- route.js refactoring (monolithic if/else → route map) (P3)
- A/B testing framework for algorithm tuning (P3)
- CDN integration for media delivery (P4)
