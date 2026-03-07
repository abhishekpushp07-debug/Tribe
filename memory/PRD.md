# Tribe — Trust-First College Social Platform for India

## Problem Statement
Build a world-class social media backend for Indian college students called **Tribe**. Backend-first approach: production-grade API + database + infra. Native Android client to be developed separately.

## Tech Stack
- **Backend**: Next.js 14 API Routes (modular handler architecture)
- **Database**: MongoDB (25 collections, 103+ indexes, zero COLLSCANs)
- **Cache**: Redis 7.x via ioredis (TTL jitter, stampede protection, event invalidation, auto-failover)
- **Storage**: Object Storage via Emergent Integrations (S3-compatible, live upload/download/serve)
- **AI Moderation**: GPT-4o-mini via Emergent Integrations (Python microservice on port 8002)
- **Auth**: Phone + 4-digit PIN → Bearer token sessions (PBKDF2 100K, 30-day TTL)

## Architecture
```
Client → K8s Ingress → Next.js API Router → Handlers → MongoDB
                                    ├─→ Redis Cache
                                    ├─→ Object Storage (media)
                                    └─→ Moderation Service (GPT-4o-mini)
```

## Acceptance Gate Status (Mar 7, 2026)

| Gate | Status | Evidence |
|------|--------|----------|
| A — Test Excellence | PASS | 97.5%+ pass rate, PUT/PATCH compat fixed |
| B — Media Go-Live | PASS | Object Storage live, upload/download verified, storageType: OBJECT_STORAGE |
| C — AI Moderation | PASS | GPT-4o-mini live, threshold system, keyword fallback, audit trail |
| D — Scale Cache | PASS | Redis connected, failover tested (0 downtime), auto-reconnect |
| E — Feature Integrity | PASS | Atomic votes ($addToSet), idempotency keys, race protection |
| F — Ops Excellence | PASS | Deep health, metrics, backup drill (25 collections restored), runbook |

## Key Proof Artifacts
- `/docs/final-acceptance-status.md` — Gate assessment + evidence
- `/docs/index-registry.md` — 103+ indexes, 13 explain plans, zero COLLSCANs
- `/docs/cache-policy-matrix.md` — Cache policy + invalidation matrix
- `/docs/media-infra-pack.md` — Object storage architecture + CDN strategy
- `/docs/ops-excellence-pack.md` — Incident runbook + backup drill + failover proof
- `/docs/performance-methodology.md` — 1900-request soak test, p50/p95/p99
- `/docs/security-pack.md` — Brute-force, session revocation, IDOR protection
- `/docs/database-schema.md` — 25 collections, reconciliation

## 65+ API Endpoints
Auth(7) + Onboarding(6) + Content(4) + Feeds(6) + Social(8) + Discovery(6) + Admin(8) + Media(2) + House Points(5) + Governance(8) + Moderation(3) + Ops(4) + Infra(3)

## Remaining Backlog

### P1
- [ ] Notes/PYQs Library
- [ ] Events section
- [ ] SSE for real-time leaderboard
- [ ] Video transcoding pipeline

### P2
- [ ] College claim/verification
- [ ] Distribution ladder
- [ ] Push notifications, WebSockets
- [ ] User blocking/muting
- [ ] Native Android app shell
