# STAGE 4A — PROOF PACK

**Date**: 2026-03-09
**Scope**: Test Foundation + Infra/Security/Observability Gate

---

## RESULTS SUMMARY

| Metric | Value |
|---|---|
| **pytest --collect-only** | **115 tests collected** |
| **Full suite pass rate** | **115/115 (100%)** |
| **Unit tests** | **64 passed** in 2.12s |
| **Integration tests** | **47 passed** in 5.40s |
| **Smoke tests** | **4 passed** in 0.69s |
| **CI gate exit code** | **0 (PASS)** |
| **Idempotency** | **5 consecutive runs, 0 failures** |
| **DB isolation** | **0 test users remaining after cleanup** |
| **Root dir cleanup** | **0 ad-hoc scripts remaining** (39 archived) |

---

## DIRECTORY STRUCTURE

```
tests/
  pytest.ini          # Config with archive exclusion
  conftest.py         # Fixtures: api_url, db, test_user, admin_user, cleanup, IP isolation
  README.md           # Full documentation
  helpers/
    js_eval.py        # JS eval bridge (Node.js subprocess for unit testing JS functions)
  unit/               # 64 tests
    test_security.py      # sanitizeTextInput(11), deepSanitize(4), maskPII(8), getEndpointTier(12)
    test_auth_utils.py    # hashPin(2), tokens(3), throttle(3), sanitizeUser(2)
    test_metrics.py       # recordRequest(1), recordError(1), percentiles(1), histogram(1), SLIs(1), getRouteFamily(3)
    test_logger.py        # redactPII(4), output format(2)
    test_request_context.py # outside store(1), inside run(1), no leak(1), nested(1), mutable(1)
  integration/        # 47 tests
    test_auth_flow.py     # register(5), login(4), refresh(3), logout(1), pin change(2)
    test_sessions.py      # list(2), revoke one(1), revoke all(1)
    test_observability.py # healthz(2), readyz(2), ops/health(3), ops/metrics(3), ops/slis(2)
    test_security_guards.py # XSS(1), payload(1), auth boundaries(3), headers(2)
    test_correlation.py   # requestId header(3), audit DB(3), error code metrics(3)
  smoke/              # 4 tests
    test_smoke_auth_ops.py  # register->login->me(1), admin->ops(1)
    test_smoke_metrics.py   # 404->metrics(1), rate limit visibility(1)
  archive/            # 39 old ad-hoc scripts (retired)
```

---

## KEY FEATURES

### JS Eval Bridge (Unit Testing JS from pytest)
- Creates temporary `.mjs` files, runs via Node.js subprocess
- Returns parsed JSON to pytest assertions
- Tests ACTUAL JS functions, not HTTP wrappers
- 64 unit tests execute in ~2 seconds

### Rate Limit Isolation (X-Forwarded-For)
- Each test/fixture gets a unique random IP (`10.x.y.z`)
- Prevents rate limit collisions across tests and re-runs
- Uses `_next_test_ip()` with 16M IP space

### Phone Namespace Isolation
- All test phones use prefix `99999` (never collides with real data)
- Cleanup removes all test-namespaced data after session
- Intentional-failure tests use random suffixes to avoid login throttle accumulation

### CI Gate Script
- `scripts/ci-gate.sh` runs unit→integration→smoke in sequence
- Exits non-zero on ANY layer failure
- Supports per-layer execution: `./scripts/ci-gate.sh unit`

---

## CRITICAL PROOFS

### Proof 1: requestId→audit correlation (DB roundtrip)
```
test_login_creates_audit_with_request_id:
  1. POST /auth/login → gets x-request-id from response header
  2. db.audit_logs.find_one({requestId: header_value}) → found
  3. Asserts: audit.requestId == header, audit.ip != null, audit.route != null
  RESULT: PASS
```

### Proof 2: Error code metrics increment
```
test_404_increments_not_found:
  1. GET /ops/metrics → baseline NOT_FOUND count
  2. GET /nonexistent-route → 404
  3. GET /ops/metrics → NOT_FOUND count > baseline
  RESULT: PASS (verified for 404, 401, 403)
```

### Proof 3: DB isolation & cleanup
```
After full suite: db.users.countDocuments({phone: /^99999/}) → 0
All test sessions, audit entries, notifications removed.
```

### Proof 4: Idempotency
```
Run 1: 115 passed in 8.46s
Run 2: 115 passed in 8.46s
Run 3: 115 passed in 8.21s
Run 4: 115 passed in 8.22s
Run 5: 115 passed in 8.35s
```
