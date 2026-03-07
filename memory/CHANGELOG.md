# Tribe — Changelog

## Mar 7, 2026 — Provider-Adapter Pattern for Moderation (P0)

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
