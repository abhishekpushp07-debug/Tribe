# Tribe — Product Requirements Document

## Original Problem Statement
Build the "Tribe" social media backend to world-best standard, targeting quality score >900/1000.
Executed through staged plan: Security → Observability → Testing → Scalability → Production.

## Architecture
- **Framework**: Monolithic Next.js API (backend-only)
- **Database**: MongoDB
- **Cache/Pub-Sub**: Redis (with in-memory fallback)
- **AI**: OpenAI GPT-4o-mini (moderation)
- **Storage**: Emergent Object Storage
- **Context**: AsyncLocalStorage for request lineage
- **Testing**: pytest (canonical runner) with JS bridge for unit tests

## Stage Completion Status

### Stage 2: Security Hardening — PASS (88/100)
- Access/refresh token system with replay detection
- Session management (list, revoke-one, revoke-all)
- Layered rate limiting (7 tiers, Redis-backed with Lua)
- Centralized input sanitization (XSS, payload size)

### Stage 3 + 3B: Observability — PASS (90/100)
- Structured JSON logging (NDJSON, PII redaction, 12+ categories)
- End-to-end request lineage via AsyncLocalStorage
- 3-tier health checks (liveness/readiness/deep)
- Metrics: histogram, percentiles, error codes, SLIs
- Redis resilience: degraded mode + recovery strategy
- Full observability coverage including OPTIONS

### Stage 4A: Test Foundation + CI Gate — GOLD CLOSURE COMPLETE (87/100)
- **139 pytest-collected tests** (78 unit + 57 integration + 4 smoke)
- JS eval bridge for testing actual JS functions from pytest
- Rate limit isolation via X-Forwarded-For unique IPs
- Phone namespace isolation (prefix 99999) + session cleanup
- CI gate script (scripts/ci-gate.sh) — exits non-zero on failure
- 3x idempotent consecutive runs — 0 failures
- 35+ old ad-hoc scripts archived to tests/archive/
- Full documentation (tests/README.md)
- **Gold Closure additions**:
  - Rate-limit STRICT 429 proof (real 429, RATE_LIMITED code)
  - OPTIONS/preflight observability proof (4 tests)
  - Redis degraded-mode direct assertion (4 tests, semi-direct)
  - pytest-cov installed, 96% baseline (no fake threshold)
  - health.js unit tests (4 tests)
  - constants.js unit tests (10 tests)
  - Marker-based selective execution working
  - package.json + Makefile execution hooks

## Upcoming Tasks

### Stage 4B: Product/Handler Test Coverage (P1)
- Posts, feed, social actions, events, resources, notices, reels
- Moderation-linked flows, house/contest domain logic
- Migrate valuable assertions from archived gold_freeze_gate.py

### Stage 5: Scalability Foundation Refactor (P1)
- Service/Repository layer separation
- handler.js → service.js → repository.js pattern

### Future Stages (P2-P3)
- Stage 6: Async Backbone + Job System + CQRS-lite
- Stage 7: Real-Time Reliability Layer (SSE improvements)
- Stage 8: Moderation v2
- Stage 9: Feature Depth (Pages, Push Notifications, DMs)
- Stages 10-12: Production Hardening, Load/Chaos Testing, Final 900+ Gate

## Known Limitations
1. No TTL on audit_logs collection (P2)
2. Legacy audit entries (2124) lack requestId (forward-only migration)
3. Redis recovery not live-tested (code verified, degraded mode proven)
4. In-memory metrics (per-instance, not distributed)
5. 2 console.log in realtime.js (Bootstrap only)
6. Duplicate headers from next.config.js vs security.js
7. Login throttle persists in memory (affects test re-runs with same phone)
8. No separate test DB (tests use namespace isolation)
9. No JS lib coverage measurement (would need Istanbul/c8)
