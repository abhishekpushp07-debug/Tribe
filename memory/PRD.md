# Tribe — Trust-First College Social Platform for India

## Problem Statement
Build a world-class social media app for Indian college students called **Tribe**. Instagram-like UX with trust, safety, and governance at its core. Backend-first approach: build production-grade API + database first, minimal web UI for testing.

## Core Differentiators
- **Official College Graph**: 1366+ colleges seeded from AISHE/UGC data
- **12-House System**: Deterministic SHA256 assignment at signup, permanent, cross-college
- **Community Governance**: 11-member boards per college with proposal-based powers
- **Safety & Compliance**: DPDP-aware, IT Rules compliant, age-gating, SLA-driven grievances

## Tech Stack
- **Frontend**: Next.js 14 + shadcn/ui + Tailwind (mobile-first web, demo only)
- **Backend**: Next.js API Routes (catch-all router → modular handlers)
- **Database**: MongoDB with 22 collections (3 deferred to P1: board_*)
- **Auth**: Phone + 4-digit PIN → Bearer token sessions (30-day TTL)
- **Storage**: Object Storage via Emergent Integrations (replaced base64-in-MongoDB)
- **Target**: Backend API designed for native Android app integration

## Architecture
```
/app/
├── app/api/[[...path]]/route.js   # Router + dispatcher
├── lib/
│   ├── db.js                      # MongoDB connection + indexes
│   ├── constants.js               # 12 Houses, enums, config
│   ├── auth-utils.js              # PIN hashing, auth, audit, enrichment
│   ├── storage.js                 # Object storage client
│   ├── api.js                     # Frontend API client
│   └── handlers/
│       ├── auth.js                # Register, login, logout, me, PIN change, sessions
│       ├── onboarding.js          # Age, college, consent, profile
│       ├── content.js             # Posts/Reels/Stories CRUD
│       ├── feed.js                # 4 feeds + stories rail + reels
│       ├── social.js              # Follow, reactions, saves, comments
│       ├── users.js               # User profiles, followers/following
│       ├── discovery.js           # Colleges, houses, search, suggestions
│       ├── media.js               # Upload + serve (Object Storage)
│       └── admin.js               # Moderation, reports, appeals, grievances, legal
```

## What's Implemented — Mar 7, 2026

### Phase 1: Foundation
- [x] MongoDB with 22 collections, 50+ indexes
- [x] Phone + PIN auth (PBKDF2 100K iterations, timing-safe compare)
- [x] JWT-style Bearer token sessions with 30-day TTL
- [x] RBAC roles: USER, MODERATOR, ADMIN, SUPER_ADMIN
- [x] Rate limiting (120 req/min per IP)
- [x] Audit logging on all mutations
- [x] Health endpoints: /healthz, /readyz
- [x] Brute-force protection (lockout after 5 failed attempts)
- [x] Session management (list, revoke)

### Phase 2: Onboarding + Houses
- [x] Age capture → ADULT/CHILD classification
- [x] DPDP child protections (no media, no personalization, no targeted ads)
- [x] College selection from 1366+ real institutions
- [x] DPDP consent flow with version tracking
- [x] 12 House System — deterministic SHA256(userId) mod 12
- [x] Profile management (displayName, username, bio)

### Phase 3: Social Core
- [x] Content creation: POST, REEL, STORY kinds
- [x] Stories with 24h TTL auto-expiry
- [x] 4 Feed Types: Public, Following, College, House
- [x] Story rail + Reels feed
- [x] Cursor-based pagination on all feeds
- [x] Follow/unfollow with counter management
- [x] Like + internal-only dislike
- [x] Save/unsave bookmarks
- [x] Comments with threaded replies
- [x] Notifications (actor-enriched)
- [x] Content reporting with auto-hold on 3+ reports
- [x] Moderation queue, strike system, appeals
- [x] Grievance tickets with SLA timers (3h legal, 72h general)
- [x] Object Storage media pipeline
- [x] Global search, user suggestions
- [x] House leaderboard, admin stats

## Acceptance Gate Status (Mar 7, 2026)

| Gate | Status | Proof |
|------|--------|-------|
| G1 — API Contract | PASS | `/docs/openapi.yaml` |
| G2 — Security Hardening | PASS | `/docs/security-pack.md` |
| G3 — Database & Indexing | PASS | `/docs/database-schema.md` (incl. reconciliation) |
| G4 — Testing | PASS | 4 contract bugs fixed, re-tested |
| G5 — Performance | PASS | `/docs/performance-methodology.md` + `/docs/load-test-results.json` |
| G6 — Media Pipeline | PASS | Object Storage via Emergent Integrations |

## Database Collections (22)
users, sessions, houses, house_ledger, colleges, content_items, follows, reactions, saves, comments, reports, moderation_events, strikes, suspensions, appeals, grievance_tickets, notifications, media_assets, audit_logs, consent_notices, consent_acceptances, feature_flags

## Backlog

### P0 — Next
- [ ] House Points ledger + earning mechanics
- [ ] Board Governance system (board_seats, board_applications, board_proposals)

### P1
- [ ] OpenAI content moderation integration
- [ ] Notes/PYQs Library
- [ ] Events section
- [ ] Video processing pipeline improvements

### P2
- [ ] College claim/verification workflow
- [ ] Distribution ladder (Stage 0→1→2)
- [ ] Push notifications, WebSocket feeds
- [ ] User blocking/muting
- [ ] Native Android app shell
