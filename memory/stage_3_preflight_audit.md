# Stage 3: Observability Baseline + Health Intelligence — Pre-Flight Audit

**Date**: 2026-03-15
**Auditor**: E1 Agent
**Scope**: Full codebase scan of logging, metrics, health, error handling, tracing, and alertability.
**Method**: Line-by-line grep + manual review of all 18 handler files, router, security module, cache, DB, realtime, and auth-utils.

---

## Executive Summary

**Current Score: 14/100 (CRITICAL)**

The codebase has virtually zero production observability infrastructure. Logging is entirely ad-hoc `console.*` calls (9 total across the entire codebase). There is no structured logging, no request logging, no request correlation IDs, no HTTP metrics, no process metrics, no latency tracking, and no alertability signals. The two audit systems (`writeAudit` and `writeSecurityAudit`) write to the same collection with incompatible schemas.

The existing health checks (`/healthz`, `/readyz`) are functional but insufficient. The deep health check (`/ops/health`) requires auth, making it unusable for Kubernetes probes.

**Bottom line**: If this server were deployed to production today, operators would be flying completely blind.

---

## Detailed Scorecard

### 1. Structured Logging — 0/15

| What exists | Score |
|---|---|
| JSON-formatted log output | NONE |
| Consistent log schema (timestamp, level, message, context) | NONE |
| Logger abstraction module | NONE |
| Total `console.*` statements across entire codebase | **9** |

**Evidence (exhaustive list of ALL log statements):**

| File | Line | Statement | Issue |
|---|---|---|---|
| `route.js` | 571 | `console.error('API Error:', error)` | Unstructured. No route/method/userId/requestId context. |
| `security.js` | 208 | `console.error('[SECURITY_AUDIT_WRITE_FAIL]', e.message)` | Ad-hoc prefix. No structured metadata. |
| `realtime.js` | 41 | `console.log('[Realtime] Redis connected...')` | Startup info. No JSON. |
| `realtime.js` | 44 | `console.log('[Realtime] Redis unavailable...')` | Startup info. No JSON. |
| `realtime.js` | 147 | `console.error('[SSE] Stream init error:', err.message)` | Error with no connection context. |
| `stories.js` | 127 | `console.log('[StoryExpiry] Marked ... stories as EXPIRED')` | Operational info. No JSON. |
| `stories.js` | 130 | `console.error('[StoryExpiry] Cleanup error:', err.message)` | Error without stack trace. |
| `auth.js` | 135 | `console.error('Auto tribe assignment failed:', e.message)` | Missing prefix convention. |
| `media.js` | 58 | `console.warn('Object storage upload failed...')` | Degradation warning. No structured context. |

**Verdict**: Every log call is a raw string. No JSON. No schema. No level filtering. Effectively zero observability from logs alone.

---

### 2. Log Levels & Categories — 1/10

| What exists | Score |
|---|---|
| Logger with configurable levels (DEBUG/INFO/WARN/ERROR/FATAL) | NONE |
| Category/namespace system | Ad-hoc `[Prefix]` brackets, inconsistent |
| Log level filtering (e.g., suppress DEBUG in production) | NONE |
| Environment-based log configuration | NONE |

**Notes**: The 9 console statements use a mix of `console.log` (3), `console.error` (5), `console.warn` (1). There is no way to filter, route, or configure these. The ad-hoc `[Prefix]` pattern is used by 5/9 statements but is not standardized.

Score: 1 (for at least using different console methods).

---

### 3. Access/Request Logging — 0/15

| What exists | Score |
|---|---|
| HTTP access log (method, route, status, duration, ip) | NONE |
| Request timing (start → end latency measurement) | NONE |
| Response status code tracking | NONE |
| User agent logging | NONE (only in security audit) |
| Slow request detection | NONE |

**Evidence**: The main router (`route.js`) processes requests through `handleRouteCore` and returns. At NO point does it:
- Record the start time
- Log the method + route combination
- Log the response status code
- Log the execution duration

**Impact**: With 100+ endpoints across 18 handler files, there is zero visibility into which endpoints are being called, how often, or how fast they respond.

---

### 4. Error Visibility — 2/10

| What exists | Score |
|---|---|
| Global error catch with logging | YES — but unstructured (route.js:566-573) |
| Error context (route, method, userId) | NONE |
| Stack trace preservation | Partial — `error` object logged but format uncontrolled |
| Empty catch blocks (swallowed errors) | **7 identified** — zero visibility |
| Error categorization (client vs infra vs bug) | NONE |

**Empty catch blocks (error swallowing):**

| File | Line | Context |
|---|---|---|
| `admin.js` | 438 | `catch {}` — unknown operation |
| `auth.js` | 230 | `catch {}` — refresh token cleanup |
| `auth.js` | 489 | `catch {}` — session operation |
| `reels.js` | 221 | `catch {}` — reel creation sub-operation |
| `reels.js` | 620 | `catch {}` — reel interaction |
| `reels.js` | 930 | `catch {}` — reel operation |
| `stages.js` | 2356 | `catch {}` — resource operation |

**Verdict**: Errors from these 7 locations are completely invisible. If any of these fail in production, there will be zero indication in any log.

---

### 5. Health Checks — 6/15

| Endpoint | What it checks | K8s Compatible | Score |
|---|---|---|---|
| `GET /healthz` | Returns `{ok: true}` — pure liveness | YES (public) | 2/2 |
| `GET /readyz` | MongoDB ping | YES (public) | 2/3 |
| `GET /ops/health` | MongoDB + Redis + Moderation + Storage | NO (requires ADMIN auth) | 2/5 |
| Startup probe | NONE | — | 0/2 |
| Custom check registration | NONE | — | 0/3 |

**Issues**:
- `/readyz` only checks MongoDB. Doesn't check Redis or storage.
- `/ops/health` is an excellent deep check BUT requires authentication, so k8s liveness/readiness probes can't call it.
- No startup probe (important for slow-starting apps with 200+ index creation).
- No degraded-but-running distinction (e.g., Redis down but app can still serve using fallback).
- Health check doesn't verify audit_logs writability.
- No health check expiry/staleness detection.

---

### 6. Metrics Collection — 3/15

| Metric Category | What exists | Score |
|---|---|---|
| Business metrics (user counts, post counts) | YES — `/ops/metrics` | 2/3 |
| Cache metrics (hit rate, redis status) | YES — `/ops/metrics` + `/cache/stats` | 1/2 |
| HTTP metrics (request count, latency, status codes) | NONE | 0/4 |
| Process metrics (memory, CPU, uptime, event loop lag) | NONE | 0/3 |
| Rate limit metrics (hits, blocks, top offenders) | NONE | 0/2 |
| Prometheus/OpenMetrics format | NONE | 0/1 |

**What `/ops/metrics` currently returns:**
```json
{
  "users": <count>,
  "posts": <count>,
  "activeSessions": <count>,
  "openReports": <count>,
  "openGrievances": <count>,
  "cache": { "hitRate": "...", "redisStatus": "..." },
  "timestamp": "..."
}
```

This is a business dashboard snapshot, NOT observability metrics. It tells you nothing about:
- Request throughput (RPS)
- Error rate (% of 5xx responses)
- Latency distribution (p50, p95, p99)
- Memory pressure or GC activity
- Rate limit effectiveness

---

### 7. Request Correlation — 0/10

| What exists | Score |
|---|---|
| Request ID generation (UUID per request) | NONE |
| Request ID in response headers (x-request-id) | NONE |
| Request ID propagated to audit logs | NONE |
| Request ID propagated to error logs | NONE |
| Correlation across services | N/A (monolith, but still useful) |

**Impact**: When a user reports "my request failed," there is NO way to find that specific request in any log. The only option is to search by approximate timestamp and hope.

---

### 8. Alertability & SLIs — 0/5

| What exists | Score |
|---|---|
| Error rate tracking | NONE |
| Latency percentile tracking (p50/p95/p99) | NONE |
| SLO definitions | NONE |
| Anomaly detection / threshold alerts | NONE |
| Rate limit violation tracking | NONE |

**Verdict**: Zero alertability infrastructure. No way to detect degradation programmatically.

---

### 9. Audit Log Hygiene — 2/5

| What exists | Score |
|---|---|
| Unified audit schema | NO — two incompatible systems |
| PII masking on all audit writes | NO — only `writeSecurityAudit` masks |
| Audit log TTL/rotation | NONE |
| Audit log queryability (indexed fields) | YES — 3 indexes exist |

**The Two Systems:**

| System | Location | Schema | PII Masking | Severity | IP/UA | Call Sites |
|---|---|---|---|---|---|---|
| `writeAudit` | `auth-utils.js:310` | `{id, eventType, actorId, targetType, targetId, metadata, createdAt}` | NONE | NONE | NONE | ~50+ |
| `writeSecurityAudit` | `security.js:190` | `{id, category, eventType, actorId, targetType, targetId, ip, userAgent, metadata, severity, createdAt}` | YES | YES | YES | ~15 |

Both write to `audit_logs` collection. Schema mismatch means querying by `severity` or `category` will miss 75% of entries.

---

## Summary Heat Map

| Parameter | Current Score | Target (Stage 3) | Gap |
|---|---|---|---|
| 1. Structured Logging | 0/15 | 13+ | BUILD FROM SCRATCH |
| 2. Log Levels & Categories | 1/10 | 8+ | BUILD FROM SCRATCH |
| 3. Access/Request Logging | 0/15 | 13+ | BUILD FROM SCRATCH |
| 4. Error Visibility | 2/10 | 8+ | MAJOR WORK |
| 5. Health Checks | 6/15 | 12+ | UPGRADE EXISTING |
| 6. Metrics Collection | 3/15 | 12+ | MAJOR WORK |
| 7. Request Correlation | 0/10 | 8+ | BUILD FROM SCRATCH |
| 8. Alertability & SLIs | 0/5 | 3+ | BUILD FROM SCRATCH |
| 9. Audit Log Hygiene | 2/5 | 4+ | MERGE + HARDEN |
| **TOTAL** | **14/100** | **81+** | **67 points to gain** |

---

## Stage 3 Implementation Priorities (Recommended Order)

### Phase 1: Foundation (Highest ROI)
1. **Create structured logger module** (`/lib/logger.js`) — JSON output, levels, categories, request context injection.
2. **Add request ID generation** in router — UUID per request, propagate everywhere, return in response header.
3. **Add access logging** in router — method, route, status, duration, requestId, userId, IP.

### Phase 2: Health Intelligence
4. **Upgrade health checks** — Make `/readyz` check Redis+Storage. Add unauthenticated `/ops/health/live` for k8s probes. Add startup probe.
5. **Add process metrics** to `/ops/metrics` — memory, uptime, event loop lag.
6. **Add HTTP metrics** — In-memory counters for request count, status code distribution, latency histogram (p50/p95/p99).

### Phase 3: Error & Audit Hardening
7. **Fix empty catch blocks** — Replace all 7 with logger.error calls.
8. **Unify audit systems** — Migrate `writeAudit` to use the richer `writeSecurityAudit` schema (add category, severity, PII masking to all audit writes).
9. **Add rate limit metrics** — Track blocked requests, top limited IPs/users.

### Phase 4: Alertability
10. **Add SLI tracking** — Error rate, latency percentiles, computed from in-memory counters.
11. **Expose Prometheus-compatible metrics** endpoint (optional, high value for production).

---

## Exception Register (Known Limitations to Accept for Stage 3)

| # | Item | Rationale |
|---|---|---|
| 1 | No distributed tracing (OpenTelemetry) | Overkill for monolith. Request IDs sufficient. |
| 2 | No external log aggregation (ELK/Datadog) | Infrastructure concern, not app code. Structured JSON is the prerequisite. |
| 3 | Metrics are in-memory only | Same limitation as rate limiting. Redis-backed metrics are Stage 10. |
| 4 | No alerting rules / PagerDuty integration | Infrastructure concern. Stage 3 provides the signals; Stage 10 wires the alerts. |

---

**Audit Status: COMPLETE**
**Recommendation: Proceed to Stage 3 Implementation per the priority order above.**
