# Tribe — Changelog

## Mar 8, 2026 — Stage 3 Story Expiry TTL (WORLD-CLASS)

### What Changed
- **Fixed direct fetch leak**: `GET /content/:id` now returns **410 Gone** for expired stories (was showing them)
- **Fixed profile stories**: `GET /users/:id/posts?kind=STORY` now filters expired stories via `expiresAt: {$gt: new Date()}`
- **Fixed admin stats**: Story count excludes expired stories
- **Fixed social action leak**: Like/dislike/comment on expired stories now returns **410 Gone** (added `isExpiredStory()` guard)
- **TTL index was already correct**: `expiresAt_1` with `partialFilterExpression: {kind: "STORY"}`, `expireAfterSeconds: 0`

### Files Modified
- `/app/lib/handlers/content.js` — Added expired-story guard to `GET /content/:id`
- `/app/lib/handlers/users.js` — Added expired-story filter to `GET /users/:id/posts?kind=STORY`
- `/app/lib/handlers/admin.js` — Admin stats counts only active stories
- `/app/lib/handlers/social.js` — Added `isExpiredStory()` guard to like/dislike/comment

### Read Path Audit (all 7 surfaces)
| Surface | Expired Story Behavior |
|---------|----------------------|
| Story rail (`/feed/stories`) | Hidden (query filter) |
| Direct fetch (`/content/:id`) | 410 Gone |
| Profile (`/users/:id/posts?kind=STORY`) | Hidden (query filter) |
| Public feed (`/feed/public`) | Never shown (kind=POST) |
| Following feed (`/feed/following`) | Never shown (kind=POST) |
| Social actions (like/dislike/comment) | 410 Gone |
| Admin stats | Excludes expired |

### Test Results: 100% pass (testing agent) + 18 manual proof tests

---

### What Changed
- **Complete rewrite** of Stage 2 College Claim handler in `/app/lib/handlers/stages.js`
- **Clean field rename**: proofType→claimType, proofBlobkey→evidence, createdAt→submittedAt, reviewerId→reviewedBy, reviewNote→reviewNotes, fraudSuspicion→fraudFlag
- **New status**: FRAUD_REVIEW added as proper workflow state (not just a boolean)
- **New route**: `GET /api/admin/college-claims/:id` — full admin detail view with claimant, college, review history, audit trail
- **Explicit cooldownUntil**: Stored on rejection (7 days from decision), not calculated dynamically
- **reviewReasonCodes**: Array of reason codes on decisions (not just a string note)
- **Auto-fraud**: 3+ lifetime rejections → claim auto-enters FRAUD_REVIEW status
- **Added ClaimStatus + ClaimConfig** to `/app/lib/constants.js`

### Indexes Rebuilt (4 optimized)
- `idx_user_status` — active claim check
- `idx_user_college_cooldown` — cooldown enforcement
- `idx_admin_queue` — admin review queue with fraud-first sorting
- `idx_claim_id_unique` — unique claim lookup

### Test Results: 94.1% (testing agent) + 25/25 manual proof
- Functional tests (17): All pass
- Contract tests (5): All pass
- Integrity tests (3): All pass
- Auto-fraud detection: Verified
- FRAUD_REVIEW → decide: Verified
- Permission tests: Verified

---

## Mar 8, 2026 — Stage 1 Appeal Decision Workflow (ACCEPTED)

### Stage 1: Appeal Decision Workflow ✅
- `PATCH /api/appeals/:id/decide` — Moderator approves/rejects appeals
- Strike reversal + content visibility restore on approval
- Suspension auto-lift when strike count drops below threshold
- REQUEST_MORE_INFO intermediate state
- Moderation event + audit trail recording
- User notification on every decision

---

## Mar 8, 2026 — Provider-Adapter Moderation Refactor

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
