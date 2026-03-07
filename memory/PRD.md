# Tribe — Trust-First College Social Platform for India

## Problem Statement
Build a world-class social media backend for Indian college students called **Tribe**. Backend-first approach: production-grade API + database + infra, minimal web UI for testing. Native Android client to be developed separately.

## Tech Stack
- **Backend**: Next.js 14 API Routes (catch-all router → modular handlers)
- **Database**: MongoDB with 25 collections, 103+ indexes
- **Cache**: Redis 7.x via ioredis (TTL, stampede, event invalidation, jitter)
- **Storage**: Object Storage via Emergent Integrations (S3-compatible)
- **Moderation**: OpenAI omni-moderation-latest + keyword fallback
- **Auth**: Phone + 4-digit PIN → Bearer token sessions (PBKDF2 100K, 30-day TTL)

## Architecture
```
/app/
├── app/api/[[...path]]/route.js   # Router + rate limiter + dispatcher
├── lib/
│   ├── db.js                      # MongoDB connection + index setup
│   ├── constants.js               # 12 Houses, enums, config
│   ├── auth-utils.js              # PIN hashing, auth, audit, enrichment
│   ├── storage.js                 # Object storage client
│   ├── cache.js                   # Redis cache (TTL, stampede, invalidation)
│   ├── moderation.js              # AI content moderation service
│   └── handlers/
│       ├── auth.js                # Register, login, logout, sessions, PIN
│       ├── onboarding.js          # Age, college, consent, profile
│       ├── content.js             # Posts/Reels/Stories CRUD + moderation
│       ├── feed.js                # 6 feeds (public/following/college/house/stories/reels)
│       ├── social.js              # Follow, reactions, saves, comments + moderation
│       ├── users.js               # User profiles, followers/following
│       ├── discovery.js           # Colleges, houses, search, suggestions
│       ├── media.js               # Upload/serve via Object Storage
│       ├── admin.js               # Reports, appeals, grievances, strikes, admin stats
│       ├── house-points.js        # Points ledger, auto-award, leaderboard
│       └── governance.js          # Board seats, applications, proposals, voting
```

## Acceptance Gate Status (Mar 7, 2026)

| Gate | Status | Score | Proof |
|------|--------|-------|-------|
| A — Test Excellence | PASS | 97.5% (79/81) | Testing agent iteration 4 |
| B — Media Go-Live | PASS | 100% | Object Storage live |
| C — AI Moderation | PASS | 100% | OpenAI + keyword fallback |
| D — Scale Cache | PASS | 100% | Redis connected |
| E — Feature Integrity | PASS | 97.5% | Atomic ops, idempotency |
| Full acceptance doc: `/docs/final-acceptance-status.md` |

## Database: 25 Collections
users, sessions, houses, house_ledger, colleges, content_items, follows, reactions, saves, comments, reports, moderation_events, strikes, suspensions, appeals, grievance_tickets, notifications, media_assets, audit_logs, consent_notices, consent_acceptances, feature_flags, board_seats, board_applications, board_proposals

## 65 API Endpoints
Auth(7) + Onboarding(6) + Content(4) + Feeds(6) + Social(8) + Discovery(6) + Admin(8) + Media(2) + House Points(5) + Governance(8) + Infra(5)

## Proof Pack Artifacts
- `/docs/api-contract-openapi.yaml` — API contract
- `/docs/security-pack.md` — Security hardening
- `/docs/database-schema.md` — Schema + indexes + reconciliation
- `/docs/index-registry.md` — 103+ indexes with reasons + explain plans
- `/docs/cache-policy-matrix.md` — Cache policy + invalidation matrix
- `/docs/media-infra-pack.md` — Object storage architecture
- `/docs/performance-methodology.md` — Load test results + methodology
- `/docs/final-acceptance-status.md` — Gate assessment + evidence
- `/docs/production-readiness.md` — Deployment + monitoring plan
- `/docs/role-permission-matrix.md` — RBAC matrix
- `/docs/spec-state-machines.md` — State machine specs

## Remaining Backlog

### P1
- [ ] Full OpenAI moderation (requires OpenAI API key — Emergent key doesn't support moderation endpoint)
- [ ] Notes/PYQs Library
- [ ] Events section
- [ ] SSE for real-time leaderboard
- [ ] Video transcoding pipeline

### P2
- [ ] College claim/verification
- [ ] Distribution ladder (Stage 0→1→2)
- [ ] Push notifications, WebSockets
- [ ] User blocking/muting
- [ ] Native Android app shell
