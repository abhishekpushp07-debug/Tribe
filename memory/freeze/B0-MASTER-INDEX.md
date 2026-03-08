# TRIBE Backend Freeze — Stage B0 Master Index

**Status**: ALL 8 SUB-STAGES FROZEN  
**Freeze Date**: 2026-02-XX

---

## Freeze Package Contents

| Document | File | Status | Description |
|----------|------|--------|-------------|
| **B0-S1** | `B0-S1-domain-freeze.md` | FROZEN | 52 domain concepts, hard vocabulary rules |
| **B0-S2** | `B0-S2-endpoint-freeze.md` | FROZEN | ~186 endpoints labeled (CANONICAL / LEGACY / ADMIN / V1_USE) |
| **B0-S3** | `B0-S3-response-contract-freeze.md` | FROZEN | 26 entity JSON shapes, pagination standards, enrichment rules |
| **B0-S4** | `B0-S4-state-machine-freeze.md` | FROZEN | 13 lifecycle state machines with allowed transitions |
| **B0-S5** | `B0-S5-permission-freeze.md` | FROZEN | 12 permission matrices across all feature domains |
| **B0-S6** | `B0-S6-sse-contract-freeze.md` | FROZEN | 4 SSE endpoints, 15 event types, snapshot/delta shapes |
| **B0-S7** | `B0-S7-media-upload-freeze.md` | FROZEN | Upload flow, size limits, processing pipeline, error codes |
| **B0-S8** | `B0-S8-deprecation-versioning-seal.md` | FROZEN | Legacy boundary, versioning rules, error code registry, final seal |

---

## 7 Canonical Documents for Android Agent

As specified in the user's requirements, the freeze package maps to the 7 canonical deliverables:

| # | Canonical Document | Freeze Sub-Stage |
|---|-------------------|-----------------|
| 1 | **Canonical Endpoint Register** | B0-S2 |
| 2 | **Entity Contract Book** | B0-S3 |
| 3 | **State Machine Book** | B0-S4 |
| 4 | **Error Code Book** | B0-S8 (Section 5) |
| 5 | **SSE Contract Book** | B0-S6 |
| 6 | **Permission Matrix** | B0-S5 |
| 7 | **Legacy & Deprecation Note** | B0-S8 (Sections 1-4) |

---

## Quick Reference for Android Agent

### Base URL
```
{BACKEND_URL}/api
```

### Auth Header
```
Authorization: Bearer {token}
Content-Type: application/json
```

### Build ONLY on these labels
- `ANDROID_V1_USE` — primary user-facing endpoints
- `CANONICAL` — stable, safe to build on

### NEVER build on these labels
- `LEGACY` — old system, will be removed
- `DEPRECATED` — returns 410
- `ADMIN_ONLY` — admin panel only
- `INTERNAL_ONLY` — system endpoints

### Key Business Rules (Quick)
1. Tribes are canonical, Houses are legacy
2. 21 tribes are permanent
3. Content distribution: Stage 0 → 1 → 2
4. Stories expire in 24h (410 after)
5. Contests: strict lifecycle with idempotent resolution
6. Salutes are append-only (immutable ledger)
7. Children cannot upload media
8. Blocks are bidirectional
9. Like (social) ≠ Vote (contest) ≠ Score (computed) ≠ Salute (tribe currency)

---

## Seal
**"Backend source of truth abhi ke liye frozen hai. Android v1 safe to start."**
