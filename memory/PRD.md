# Tribe — Trust-First College Social Platform for India

## Problem Statement
Build a world-class social media backend for Indian college students called **Tribe**. Backend-first approach: production-grade API + database + infra. Native Android client to be developed separately.

## Tech Stack
- **Backend**: Next.js 14 API Routes (modular handler architecture)
- **Database**: MongoDB (33 collections, 130+ indexes, zero COLLSCANs)
- **Cache**: Redis 7.x via ioredis (TTL jitter, stampede protection, event invalidation, auto-failover)
- **Storage**: Object Storage via Emergent Integrations (S3-compatible)
- **AI Moderation**: OpenAI Moderations API (omni-moderation-latest) via Provider-Adapter Pattern
- **Auth**: Phone + 4-digit PIN → Bearer token sessions (PBKDF2 100K, 30-day TTL)

## Architecture
```
Client → K8s Ingress → Next.js API Router → Handlers → MongoDB
                                    ├─→ Redis Cache
                                    ├─→ Object Storage (media)
                                    └─→ ModerationService (Provider-Adapter)
                                          ├─→ OpenAI Moderations API (primary)
                                          └─→ Keyword Fallback (secondary)
```

## 90+ API Endpoints (v3.0.0)
Auth(7) + Onboarding(6) + Content(4) + Feeds(6) + Social(8) + Discovery(6) + Admin(12) + Media(2) + House Points(5) + Governance(8) + Moderation(5) + Ops(4) + Resources(5) + Events(5) + Board Notices(4) + Authenticity(2) + Distribution(3) + College Claims(4) + Appeals(2)

## Stage Completion Status (Mar 8, 2026)

| Stage | Name | Status | Pass Rate |
|-------|------|--------|-----------|
| A | Foundation Bootstrap | ✅ FROZEN | 100% |
| B | Auth + Profile + Age + Consent | ✅ 90% | ✅ |
| C | College Registry + Claims | ✅ DONE | 100% |
| D | Social Core | ✅ FROZEN | 100% |
| E | Stories + Reels + Expiry | ✅ DONE | ✅ |
| F.1 | Moderation Adapter | ✅ DONE | 100% |
| F.2 | Appeals Decision | ✅ DONE | 100% |
| F.3 | Distribution Ladder | ✅ DONE | 100% |
| G.1 | Board Notices | ✅ DONE | ✅ |
| G.2 | Notes/PYQs Library | ✅ DONE | 100% |
| G.3 | Events + RSVP | ✅ DONE | 100% |
| G.4 | Authenticity Tags | ✅ DONE | ✅ |

## 33 MongoDB Collections
users, sessions, audit_logs, content_items, follows, reactions, comments, saves, reports, appeals, moderation_events, moderation_audit_logs, moderation_review_queue, strikes, suspensions, grievance_tickets, colleges, houses, house_ledger, board_seats, board_applications, board_proposals, board_notices, media_assets, consent_notices, consent_acceptances, notifications, feature_flags, college_claims, resources, events, event_rsvps, authenticity_tags

## Remaining Backlog

### P1 — Upcoming
- [ ] OTP Challenge Flow (Stage 8)
- [ ] Post-Publish Signal Processing (Stage 9)
- [ ] Synthetic Content Provenance enforcement

### P2 — Future
- [ ] Video Transcoding Pipeline (Stage 10)
- [ ] Ops/Scale Excellence (Stage 11)
- [ ] Final Launch Gate (Stage 12)
- [ ] Admin Moderation Panel (UI)
- [ ] SSE real-time leaderboard
- [ ] Presigned URL uploads
- [ ] Signed CDN URLs
- [ ] Board seat types (FOUNDING/MEMBER)
- [ ] College aliases + de-dup
- [ ] Request logging middleware

### P3 — Backlog
- [ ] Live rooms, chat (WebSockets)
- [ ] Push notifications
- [ ] User blocking/muting
- [ ] Native Android app shell
