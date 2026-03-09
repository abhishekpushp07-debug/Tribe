# Tribe — Product Requirements Document

## Problem Statement
World-class social media backend for Indian college students, named **Tribe**. Features 21 tribes (Param Vir Chakra awardees), college verification, content distribution ladder, stories, reels, events, board notices, governance, and a full contest engine.

## Architecture
- **Backend**: Monolithic Next.js API (all routes under `/api/*`)
- **Database**: MongoDB (60+ collections, 200+ indexes)
- **Cache/PubSub**: Redis (with in-memory fallback)
- **Real-time**: Server-Sent Events (SSE) via Redis Pub/Sub
- **Content Moderation**: OpenAI GPT-4o-mini
- **Storage**: Emergent Object Storage (with base64 fallback)

## Completed Stages

| Stage | Name | Status | Date |
|-------|------|--------|------|
| 0 | Auth & Core | DONE | — |
| 1 | Appeal Decision | DONE | — |
| 2 | College Claims | DONE | — |
| 4 | Distribution Ladder | DONE (2 test failures) | — |
| 5 | Notes/PYQs Library | DONE (needs formal proof pack) | — |
| 6 | Events + RSVP | DONE | — |
| 7 | Board Notices + Authenticity | DONE | — |
| 9 | Stories (full) | DONE | — |
| 10 | Reels (full) | DONE | — |
| 12 | Tribe System | DONE | — |
| 12X | Tribe Contest Engine | GOLD FROZEN (69/69 tests) | — |
| 12X-RT | Real-Time SSE Layer | GOLD FROZEN | — |
| B0 | Backend Source of Truth Freeze | COMPLETE (8/8 sub-stages) | 2026-02 |
| B0-E | Backend Freeze Code Enforcement | COMPLETE (85/85 tests) | 2026-03 |

## Stage B0-E — Code-Level Freeze Enforcement (COMPLETED)

Three layers of enforcement:
1. **Freeze Registry** (`/app/lib/freeze-registry.js`) — Every endpoint mapped to freeze label
2. **Freeze Headers Middleware** — Every response gets:
   - `X-Contract-Version: v1` (always)
   - `X-Freeze-Status: canonical | android_v1_use | legacy | deprecated | admin_only | board_only | internal_only`
   - `X-Deprecated: true` + `X-Deprecation-Notice` (on legacy/deprecated)
3. **Contract Test Suite** (`/app/tests/contract-freeze-test.sh`) — 85 tests across 12 gates
   - Freeze headers, auth shapes, feed shapes, tribe shapes, error shapes, permissions, legacy boundary, content/social, search, contests, notifications, governance

Bug fixed during enforcement: `/admin/stats` was accessible to regular users (no auth check) — now requires ADMIN role.

Documents at: `/app/memory/freeze/`

## Pending Issues (P2)
1. Stage 4: 2 automated test failures (Distribution Ladder)
2. Stage 5: Needs formal deep proof pack for acceptance

## Upcoming Tasks
1. P0: Stage 11 — Scale / Reliability / Disaster Excellence
2. P1: Stage 12Y — Tribe Contest Product Surfaces (frontend)
3. P2: Fix Stage 4 test failures
4. P2: Stage 5 formal acceptance

## Key Documents
- `/app/memory/freeze/B0-MASTER-INDEX.md` — Master freeze index
- `/app/memory/android_agent_handoff.md` — Complete API reference for Android
- `/app/memory/freeze/B0-S1-domain-freeze.md` through `B0-S8-*` — Full freeze package
