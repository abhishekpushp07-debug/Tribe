# Tribe — Test Suite (Stage 4A)

## Overview

This is the canonical test system for the Tribe backend. It replaces all ad-hoc root-level test scripts.

### Architecture

```
tests/
  conftest.py          # Shared fixtures (api_url, db, test_user, admin_user, cleanup)
  pytest.ini           # pytest configuration
  helpers/
    js_eval.py         # JS eval bridge (runs Node.js code from pytest)
  unit/                # Pure function tests (no network, no DB)
    test_security.py   # sanitizeTextInput, deepSanitizeStrings, maskPII, getEndpointTier
    test_auth_utils.py # hashPin/verifyPin, generateToken, loginThrottle, sanitizeUser
    test_metrics.py    # recordRequest, recordError, getRouteFamily, percentiles, SLIs
    test_logger.py     # PII redaction, NDJSON format, stderr routing
    test_request_context.py # AsyncLocalStorage: isolation, mutation, nesting
  integration/         # API endpoint tests (requires running server + MongoDB)
    test_auth_flow.py  # register, login, refresh, replay, logout, pin change
    test_sessions.py   # list, revoke-one, revoke-all
    test_observability.py # healthz, readyz, ops/health, ops/metrics, ops/slis
    test_security_guards.py # XSS, payload size, auth boundaries, security headers
    test_correlation.py # requestId header, audit DB proof, error code metrics proof
  smoke/               # End-to-end flow tests (minimal, critical paths)
    test_smoke_auth_ops.py  # register→login→me, admin→ops
    test_smoke_metrics.py   # 404→metrics, rate limit visibility
```

## Running Tests

### All layers
```bash
./scripts/ci-gate.sh
```

### Individual layers
```bash
# Unit tests only
python -m pytest tests/unit -v --tb=short -c tests/pytest.ini

# Integration tests only
python -m pytest tests/integration -v --tb=short -c tests/pytest.ini

# Smoke tests only
python -m pytest tests/smoke -v --tb=short -c tests/pytest.ini

# Specific test file
python -m pytest tests/unit/test_security.py -v --tb=short -c tests/pytest.ini

# Specific test class
python -m pytest tests/unit/test_security.py::TestSanitizeTextInput -v -c tests/pytest.ini
```

## Test Isolation Strategy

- **Phone namespace**: All test users use phone numbers starting with `99999`
- **Session cleanup**: `conftest.py::pytest_sessionfinish` removes ALL test-namespaced data
- **Idempotent**: Tests handle "already exists" gracefully—safe to re-run
- **No production pollution**: Only `99999*` phones are touched

## Unit Test Approach (JS Bridge)

Since the Tribe backend is JavaScript (Next.js), unit tests use a **JS eval bridge**:
- `tests/helpers/js_eval.py` creates temporary `.mjs` files
- Node.js executes them, importing real JS modules
- Results are returned as parsed JSON to pytest
- This gives us pytest-native test collection while testing actual JS functions

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `TEST_API_URL` | `http://localhost:3000/api` | API base URL |
| `TEST_MONGO_URL` | `mongodb://localhost:27017` | MongoDB connection |
| `TEST_DB_NAME` | `your_database_name` | Database name |

## CI Gate

`scripts/ci-gate.sh` runs all three layers in sequence. Exits non-zero if ANY layer fails.

```bash
./scripts/ci-gate.sh           # All layers
./scripts/ci-gate.sh unit      # Just unit
./scripts/ci-gate.sh integration # Just integration
./scripts/ci-gate.sh smoke     # Just smoke
```
