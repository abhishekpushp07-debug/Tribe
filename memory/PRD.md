# Tribe — Trust-First College Social Platform for India

## Problem Statement
Build a world-class social media backend for Indian college students called **Tribe**. Backend-first approach: production-grade API + database + infra. Native Android client to be developed separately.

## Tech Stack
- **Backend**: Next.js 14 API Routes (modular handler architecture)
- **Database**: MongoDB (25+ collections, 103+ indexes, zero COLLSCANs)
- **Cache**: Redis 7.x via ioredis (TTL jitter, stampede protection, event invalidation, auto-failover)
- **Storage**: Object Storage via Emergent Integrations (S3-compatible, live upload/download/serve)
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

## Moderation Provider-Adapter Architecture (Implemented Mar 7, 2026)
```
/app/lib/moderation/
  config.js                          - ENV-driven config (MODERATION_PROVIDER)
  rules.js                           - Provider-agnostic decision engine
  provider.js                        - Factory (singleton, env-driven selection)
  providers/
    fallback-keyword.provider.js     - Keyword backup provider
    openai.provider.js               - OpenAI Moderations API (production primary)
    composite.provider.js            - OpenAI primary + fallback secondary chain
  repositories/
    moderation.repository.js         - MongoDB audit log + review queue
  services/
    moderation.service.js            - Orchestrator (moderateOrThrow)
  middleware/
    moderate-create-content.js       - Reusable moderation function for handlers
  routes/
    moderation.routes.js             - Moderation API endpoints
```

### Non-Negotiables:
- Handlers/routes NEVER call OpenAI directly → only ModerationService
- Provider chosen via env: `fallback | openai | composite`
- `composite = OpenAI primary + keyword fallback secondary`
- Audit logs and review queue are provider-agnostic
- Adding/changing provider requires ZERO handler refactor

## Acceptance Gate Status (Mar 7, 2026)

| Gate | Status | Evidence |
|------|--------|----------|
| A — Test Excellence | PASS | 84%+ pass rate, all core APIs working |
| B — Media Go-Live | PASS | Object Storage live, upload/download verified |
| C — AI Moderation | **PASS (Upgraded)** | Provider-Adapter Pattern, OpenAI primary, keyword fallback, audit trail |
| D — Scale Cache | PASS | Redis connected, failover tested, auto-reconnect |
| E — Feature Integrity | PASS | Atomic votes, idempotency keys, race protection |
| F — Ops Excellence | PASS | Deep health, metrics, backup drill, runbook |

## 65+ API Endpoints
Auth(7) + Onboarding(6) + Content(4) + Feeds(6) + Social(8) + Discovery(6) + Admin(8) + Media(2) + House Points(5) + Governance(8) + Moderation(3) + Ops(4) + Infra(3)

## Remaining Backlog

### P1
- [ ] Notes/PYQs Library
- [ ] Events section
- [ ] SSE for real-time leaderboard
- [ ] Video transcoding pipeline

### P2
- [ ] Admin Moderation Panel (UI for review queue)
- [ ] College claim/verification
- [ ] Distribution ladder
- [ ] Push notifications, WebSockets
- [ ] User blocking/muting
- [ ] Native Android app shell
