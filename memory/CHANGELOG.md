# Tribe — Changelog

## Mar 8, 2026 — Stages 1-7 Implementation (PHASE 0-2 of Master Plan)

### PHASE 0: Freeze the Base
- Created `/app/docs/frozen-contracts.md` documenting all frozen routes, collections, indexes, and breaking change rules

### Stage 1: Appeal Decision Workflow ✅
- `PATCH /api/appeals/:id/decide` — Moderator approves/rejects appeals
- Strike reversal + content visibility restore on approval
- Suspension auto-lift when strike count drops below threshold
- Moderation event + audit trail recording

### Stage 2: College Claim Workflow ✅
- `POST /api/colleges/:id/claim` — Submit with proofType
- `GET /api/me/college-claims` — User's claims history
- `GET /api/admin/college-claims?status=PENDING` — Admin review queue
- `PATCH /api/admin/college-claims/:id/decide` — Admin decision
- 7-day reapply cooldown, one active claim per user/college, fraud flag support

### Stage 3: Story Expiry Cleanup ✅
- MongoDB TTL index on `expiresAt` with `partialFilterExpression: { kind: "STORY" }`
- Expired stories auto-deleted by MongoDB, excluded from feed queries

### Stage 4: Distribution Ladder ✅
- 3-tier distribution: Stage 0 (profile/house) → 1 (college) → 2 (public)
- Promotion rules: account age 7d + 0 strikes + 1+ like for 0→1; 24h + 3 likes + 0 reports for 1→2
- Demotion on active reports/strikes
- Admin endpoints: config, evaluate, manual override

### Stage 5: Notes/PYQs Library ✅
- Full CRUD: create, search (multi-filter), detail (with download count), soft delete, report
- 5 kinds: NOTE, PYQ, ASSIGNMENT, SYLLABUS, LAB_FILE
- Taxonomy: college → branch → subject → semester
- AI moderation on title+description
- Auto-hold at 3+ reports

### Stage 6: Events + RSVP ✅
- Event CRUD: create, search (by college, startDate), detail with RSVP counts
- RSVP upsert (GOING/INTERESTED), cancel
- Atomic RSVP count tracking
- AI moderation on event text

### Stage 7: Board Notices + Authenticity Tags ✅
- Board notices: create (board members only) → moderator review → publish
- College notices endpoint (public, published only)
- Authenticity tags: board/moderator can tag RESOURCE/EVENT as VERIFIED/USEFUL/OUTDATED/MISLEADING
- Duplicate tag prevention (update instead)

### New collections created: 6
- `college_claims`, `resources`, `events`, `event_rsvps`, `board_notices`, `authenticity_tags`

### New indexes created: 18+
- All new collections properly indexed for query patterns

### Test Results
- Stage 1 Appeals: 100%
- Stage 2 Claims: 100%
- Stage 4 Distribution: 100%
- Stage 5 Resources: 100%
- Stage 6 Events: 100%
- Stage 7 Notices/Tags: Working with proper access controls

### What changed
- **Replaced** old tightly-coupled moderation module (`/app/lib/moderation.js` → deleted)
- **Implemented** clean Provider-Adapter Pattern in `/app/lib/moderation/` with 10 files
- **Wired** OpenAI Moderations API as primary production provider (`omni-moderation-latest`)
- **Built** keyword fallback provider as automatic backup when OpenAI is unavailable
- **Created** composite provider that chains OpenAI → keyword fallback seamlessly
- **Refactored** content handler and social handler to use `ModerationService.moderateOrThrow()`
- **Added** provider-agnostic audit logs and review queue in MongoDB
- **Made** provider swappable via `MODERATION_PROVIDER` env var — zero handler refactor

### Files created/modified
- `/app/lib/moderation/config.js` — ENV-driven config
- `/app/lib/moderation/rules.js` — Risk score engine with category weights
- `/app/lib/moderation/provider.js` — Factory with singleton pattern
- `/app/lib/moderation/providers/openai.provider.js` — OpenAI Moderations API
- `/app/lib/moderation/providers/fallback-keyword.provider.js` — Keyword safety net
- `/app/lib/moderation/providers/composite.provider.js` — OpenAI + fallback chain
- `/app/lib/moderation/repositories/moderation.repository.js` — Audit + review queue
- `/app/lib/moderation/services/moderation.service.js` — Orchestrator
- `/app/lib/moderation/middleware/moderate-create-content.js` — Handler utility
- `/app/lib/moderation/routes/moderation.routes.js` — API endpoints
- `/app/lib/handlers/content.js` — Refactored to use ModerationService
- `/app/lib/handlers/social.js` — Refactored to use ModerationService
- `/app/app/api/[[...path]]/route.js` — Updated routing + health check

### Files deleted
- `/app/lib/moderation.js` — Old tightly-coupled module
- `/app/lib/moderation/providers/gpt-classify.js` — Replaced by OpenAI provider
- `/app/lib/moderation/types.js` — Removed (using JSDoc instead)
- `/app/lib/moderation/provider-factory.js` — Renamed to provider.js
- `/app/lib/moderation/service.js` — Moved to services/moderation.service.js

### Test results
- Moderation config endpoint: ✅ shows composite with ["openai", "fallback"] chain
- Clean text moderation: ✅ ALLOW with near-zero scores
- Harmful text moderation: ✅ ESCALATE with review ticket creation
- Content creation with moderation: ✅ clean→PUBLIC, harmful→HELD
- Comment moderation: ✅ harmful comments rejected
- Audit logs: ✅ written to moderation_audit_logs collection
- Review queue: ✅ tickets created for ESCALATE actions
- Health check: ✅ shows moderation provider status
