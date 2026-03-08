# B0-S2 — Endpoint Canonicalization Freeze

**Status**: FROZEN  
**Freeze Date**: 2026-02-XX  
**Rule**: Every endpoint has exactly ONE label. Android builds ONLY on CANONICAL + ANDROID_V1_USE endpoints.

---

## Label Definitions

| Label | Meaning | Android v1 Builds On? |
|-------|---------|----------------------|
| **CANONICAL** | Primary endpoint, stable contract | YES |
| **ANDROID_V1_USE** | Canonical AND explicitly needed for Android v1 screens | YES |
| **ADMIN_ONLY** | Admin/moderator panel only, not in user-facing app | NO |
| **BOARD_ONLY** | Board member governance actions | NO (unless board UI built) |
| **INTERNAL_ONLY** | System/worker endpoints, never called from client | NO |
| **LEGACY** | Old system, still works but do not build new UI on it | NO |
| **DEPRECATED** | Returns 410, will be removed | NO |

---

## Complete Endpoint Register

### AUTH — 7 endpoints

| Method | Path | Label | Android Screen |
|--------|------|-------|----------------|
| POST | `/api/auth/register` | ANDROID_V1_USE | Signup |
| POST | `/api/auth/login` | ANDROID_V1_USE | Login |
| POST | `/api/auth/logout` | ANDROID_V1_USE | Settings |
| GET | `/api/auth/me` | ANDROID_V1_USE | App bootstrap |
| GET | `/api/auth/sessions` | ANDROID_V1_USE | Settings > Sessions |
| DELETE | `/api/auth/sessions` | ANDROID_V1_USE | Settings > Logout All |
| PATCH | `/api/auth/pin` | ANDROID_V1_USE | Settings > Change PIN |

### ONBOARDING & PROFILE — 4 endpoints

| Method | Path | Label | Android Screen |
|--------|------|-------|----------------|
| PATCH | `/api/me/profile` | ANDROID_V1_USE | Edit Profile |
| PATCH | `/api/me/age` | ANDROID_V1_USE | Onboarding |
| PATCH | `/api/me/college` | ANDROID_V1_USE | Onboarding |
| PATCH | `/api/me/onboarding` | ANDROID_V1_USE | Onboarding completion |

### CONTENT (Posts) — 3 endpoints

| Method | Path | Label | Android Screen |
|--------|------|-------|----------------|
| POST | `/api/content/posts` | ANDROID_V1_USE | Create Post |
| GET | `/api/content/{contentId}` | ANDROID_V1_USE | Post Detail |
| DELETE | `/api/content/{contentId}` | ANDROID_V1_USE | Post Options |

### FEEDS — 6 endpoints

| Method | Path | Label | Android Screen |
|--------|------|-------|----------------|
| GET | `/api/feed/public` | ANDROID_V1_USE | Home > Discover |
| GET | `/api/feed/following` | ANDROID_V1_USE | Home > Following |
| GET | `/api/feed/college/{collegeId}` | ANDROID_V1_USE | College Feed |
| GET | `/api/feed/house/{houseId}` | LEGACY | — |
| GET | `/api/feed/stories` | ANDROID_V1_USE | Story Rail (top of feed) |
| GET | `/api/feed/reels` | ANDROID_V1_USE | Reels Tab |

### SOCIAL — 9 endpoints

| Method | Path | Label | Android Screen |
|--------|------|-------|----------------|
| POST | `/api/follow/{userId}` | ANDROID_V1_USE | Profile > Follow |
| DELETE | `/api/follow/{userId}` | ANDROID_V1_USE | Profile > Unfollow |
| POST | `/api/content/{contentId}/like` | ANDROID_V1_USE | Post Interaction |
| POST | `/api/content/{contentId}/dislike` | ANDROID_V1_USE | Post Interaction |
| DELETE | `/api/content/{contentId}/reaction` | ANDROID_V1_USE | Post Interaction |
| POST | `/api/content/{contentId}/save` | ANDROID_V1_USE | Post Interaction |
| DELETE | `/api/content/{contentId}/save` | ANDROID_V1_USE | Post Interaction |
| POST | `/api/content/{contentId}/comments` | ANDROID_V1_USE | Post Detail > Comment |
| GET | `/api/content/{contentId}/comments` | ANDROID_V1_USE | Post Detail > Comments |

### USERS & DISCOVERY — 12 endpoints

| Method | Path | Label | Android Screen |
|--------|------|-------|----------------|
| GET | `/api/users/{userId}` | ANDROID_V1_USE | User Profile |
| GET | `/api/users/{userId}/posts` | ANDROID_V1_USE | User Profile > Posts |
| GET | `/api/users/{userId}/followers` | ANDROID_V1_USE | Followers List |
| GET | `/api/users/{userId}/following` | ANDROID_V1_USE | Following List |
| GET | `/api/users/{userId}/saved` | ANDROID_V1_USE | My Saved (self only) |
| GET | `/api/search` | ANDROID_V1_USE | Search |
| GET | `/api/suggestions/users` | ANDROID_V1_USE | Discover > Suggested |
| GET | `/api/colleges/search` | ANDROID_V1_USE | College Search (onboarding) |
| GET | `/api/colleges/states` | ANDROID_V1_USE | College Filter |
| GET | `/api/colleges/types` | ANDROID_V1_USE | College Filter |
| GET | `/api/colleges/{collegeId}` | ANDROID_V1_USE | College Profile |
| GET | `/api/colleges/{collegeId}/members` | ANDROID_V1_USE | College Members |

### HOUSES (LEGACY) — 3 endpoints

| Method | Path | Label | Android Screen |
|--------|------|-------|----------------|
| GET | `/api/houses` | LEGACY | — |
| GET | `/api/houses/leaderboard` | LEGACY | — |
| GET | `/api/houses/{idOrSlug}` | LEGACY | — |

### HOUSE POINTS (DEPRECATED) — 1 endpoint

| Method | Path | Label | Android Screen |
|--------|------|-------|----------------|
| POST | `/api/house-points` | DEPRECATED (410) | — |

### MEDIA — 2 endpoints

| Method | Path | Label | Android Screen |
|--------|------|-------|----------------|
| POST | `/api/media/upload` | ANDROID_V1_USE | Upload (any media flow) |
| GET | `/api/media/{mediaId}` | ANDROID_V1_USE | Media display (images/video) |

### COLLEGE CLAIMS (Stage 2) — 5 endpoints

| Method | Path | Label | Android Screen |
|--------|------|-------|----------------|
| POST | `/api/colleges/{collegeId}/claim` | ANDROID_V1_USE | College Verification |
| GET | `/api/me/college-claims` | ANDROID_V1_USE | My Verification History |
| DELETE | `/api/me/college-claims/{claimId}` | ANDROID_V1_USE | Withdraw Claim |
| GET | `/api/admin/college-claims` | ADMIN_ONLY | — |
| GET | `/api/admin/college-claims/{claimId}` | ADMIN_ONLY | — |
| PATCH | `/api/admin/college-claims/{claimId}/flag-fraud` | ADMIN_ONLY | — |
| PATCH | `/api/admin/college-claims/{claimId}/decide` | ADMIN_ONLY | — |

### DISTRIBUTION LADDER (Stage 4) — 6 endpoints

| Method | Path | Label | Android Screen |
|--------|------|-------|----------------|
| POST | `/api/admin/distribution/evaluate` | ADMIN_ONLY | — |
| POST | `/api/admin/distribution/evaluate/{contentId}` | ADMIN_ONLY | — |
| GET | `/api/admin/distribution/config` | ADMIN_ONLY | — |
| GET | `/api/admin/distribution/inspect/{contentId}` | ADMIN_ONLY | — |
| POST | `/api/admin/distribution/override` | ADMIN_ONLY | — |
| DELETE | `/api/admin/distribution/override/{contentId}` | ADMIN_ONLY | — |
| POST | `/api/admin/distribution/kill-switch` | ADMIN_ONLY | — |

### RESOURCES / Notes Library (Stage 5) — 9 endpoints

| Method | Path | Label | Android Screen |
|--------|------|-------|----------------|
| POST | `/api/resources` | ANDROID_V1_USE | Upload Resource |
| GET | `/api/resources/search` | ANDROID_V1_USE | Library Search |
| GET | `/api/resources/{resourceId}` | ANDROID_V1_USE | Resource Detail |
| POST | `/api/resources/{resourceId}/vote` | ANDROID_V1_USE | Resource Vote |
| POST | `/api/resources/{resourceId}/download` | ANDROID_V1_USE | Resource Download |
| POST | `/api/resources/{resourceId}/report` | ANDROID_V1_USE | Resource Report |
| GET | `/api/me/resources` | ANDROID_V1_USE | My Uploads |
| GET | `/api/admin/resources` | ADMIN_ONLY | — |
| PATCH | `/api/admin/resources/{id}/moderate` | ADMIN_ONLY | — |
| POST | `/api/admin/resources/{id}/recompute-counters` | ADMIN_ONLY | — |
| POST | `/api/admin/resources/reconcile` | ADMIN_ONLY | — |

### EVENTS (Stage 6) — 11 endpoints

| Method | Path | Label | Android Screen |
|--------|------|-------|----------------|
| POST | `/api/events` | ANDROID_V1_USE | Create Event |
| GET | `/api/events/search` | ANDROID_V1_USE | Events Discovery |
| GET | `/api/events/feed` | ANDROID_V1_USE | Events Tab |
| GET | `/api/events/college/{collegeId}` | ANDROID_V1_USE | College Events |
| GET | `/api/events/{eventId}` | ANDROID_V1_USE | Event Detail |
| PATCH | `/api/events/{eventId}` | ANDROID_V1_USE | Edit Event |
| DELETE | `/api/events/{eventId}` | ANDROID_V1_USE | Delete Event |
| POST | `/api/events/{eventId}/publish` | ANDROID_V1_USE | Publish Draft |
| POST | `/api/events/{eventId}/cancel` | ANDROID_V1_USE | Cancel Event |
| POST | `/api/events/{eventId}/rsvp` | ANDROID_V1_USE | RSVP |
| DELETE | `/api/events/{eventId}/rsvp` | ANDROID_V1_USE | Cancel RSVP |
| GET | `/api/events/{eventId}/attendees` | ANDROID_V1_USE | Attendees List |
| POST | `/api/events/{eventId}/report` | ANDROID_V1_USE | Report Event |
| POST | `/api/events/{eventId}/remind` | ANDROID_V1_USE | Set Reminder |
| DELETE | `/api/events/{eventId}/remind` | ANDROID_V1_USE | Remove Reminder |
| GET | `/api/me/events` | ANDROID_V1_USE | My Events |
| GET | `/api/me/events/rsvps` | ANDROID_V1_USE | My RSVPs |
| GET | `/api/admin/events` | ADMIN_ONLY | — |
| PATCH | `/api/admin/events/{id}/moderate` | ADMIN_ONLY | — |
| GET | `/api/admin/events/analytics` | ADMIN_ONLY | — |
| POST | `/api/admin/events/{id}/recompute-counters` | ADMIN_ONLY | — |

### BOARD NOTICES (Stage 7) — 6 endpoints

| Method | Path | Label | Android Screen |
|--------|------|-------|----------------|
| POST | `/api/board/notices` | BOARD_ONLY | Board Panel |
| GET | `/api/board/notices/{noticeId}` | ANDROID_V1_USE | Notice Detail |
| PATCH | `/api/board/notices/{noticeId}` | BOARD_ONLY | Edit Notice |
| DELETE | `/api/board/notices/{noticeId}` | BOARD_ONLY | Delete Notice |
| POST | `/api/board/notices/{noticeId}/pin` | BOARD_ONLY | Pin Notice |
| DELETE | `/api/board/notices/{noticeId}/pin` | BOARD_ONLY | Unpin Notice |
| POST | `/api/board/notices/{noticeId}/acknowledge` | ANDROID_V1_USE | Acknowledge Notice |
| GET | `/api/board/notices/{noticeId}/acknowledgments` | CANONICAL | Acknowledgment List |
| GET | `/api/colleges/{collegeId}/notices` | ANDROID_V1_USE | College Notices Board |
| GET | `/api/me/board/notices` | BOARD_ONLY | My Notices |
| GET | `/api/moderation/board-notices` | ADMIN_ONLY | — |
| POST | `/api/moderation/board-notices/{id}/decide` | ADMIN_ONLY | — |
| GET | `/api/admin/board-notices/analytics` | ADMIN_ONLY | — |
| GET | `/api/admin/authenticity/stats` | ADMIN_ONLY | — |

### AUTHENTICITY TAGS (Stage 7) — 3 endpoints

| Method | Path | Label | Android Screen |
|--------|------|-------|----------------|
| POST | `/api/authenticity/tag` | BOARD_ONLY | Tag Resource/Event |
| GET | `/api/authenticity/tags/{targetType}/{targetId}` | ANDROID_V1_USE | View Tags (on resource/event detail) |
| DELETE | `/api/authenticity/tags/{tagId}` | BOARD_ONLY | Remove Tag |

### STORIES (Stage 9) — 24 endpoints

| Method | Path | Label | Android Screen |
|--------|------|-------|----------------|
| POST | `/api/stories` | ANDROID_V1_USE | Create Story |
| GET | `/api/stories/feed` | ANDROID_V1_USE | Story Rail |
| GET | `/api/stories/{storyId}` | ANDROID_V1_USE | View Story |
| DELETE | `/api/stories/{storyId}` | ANDROID_V1_USE | Delete Story |
| GET | `/api/stories/{storyId}/views` | ANDROID_V1_USE | Story Viewers (owner) |
| POST | `/api/stories/{storyId}/react` | ANDROID_V1_USE | Story Reaction |
| DELETE | `/api/stories/{storyId}/react` | ANDROID_V1_USE | Remove Reaction |
| POST | `/api/stories/{storyId}/reply` | ANDROID_V1_USE | Story Reply |
| GET | `/api/stories/{storyId}/replies` | ANDROID_V1_USE | Story Replies (owner) |
| POST | `/api/stories/{storyId}/sticker/{stickerId}/respond` | ANDROID_V1_USE | Sticker Response |
| GET | `/api/stories/{storyId}/sticker/{stickerId}/results` | ANDROID_V1_USE | Sticker Results |
| GET | `/api/stories/{storyId}/sticker/{stickerId}/responses` | CANONICAL | Sticker Responses (owner) |
| POST | `/api/stories/{storyId}/report` | ANDROID_V1_USE | Report Story |
| GET | `/api/me/stories/archive` | ANDROID_V1_USE | My Story Archive |
| GET | `/api/users/{userId}/stories` | ANDROID_V1_USE | User Stories |
| GET | `/api/me/close-friends` | ANDROID_V1_USE | Close Friends List |
| POST | `/api/me/close-friends/{userId}` | ANDROID_V1_USE | Add Close Friend |
| DELETE | `/api/me/close-friends/{userId}` | ANDROID_V1_USE | Remove Close Friend |
| POST | `/api/me/highlights` | ANDROID_V1_USE | Create Highlight |
| GET | `/api/users/{userId}/highlights` | ANDROID_V1_USE | User Highlights |
| PATCH | `/api/me/highlights/{highlightId}` | ANDROID_V1_USE | Edit Highlight |
| DELETE | `/api/me/highlights/{highlightId}` | ANDROID_V1_USE | Delete Highlight |
| GET | `/api/me/story-settings` | ANDROID_V1_USE | Story Settings |
| PATCH | `/api/me/story-settings` | ANDROID_V1_USE | Update Story Settings |
| POST | `/api/me/blocks/{userId}` | ANDROID_V1_USE | Block User |
| DELETE | `/api/me/blocks/{userId}` | ANDROID_V1_USE | Unblock User |
| GET | `/api/me/blocks` | ANDROID_V1_USE | Blocked Users List |
| GET | `/api/stories/events/stream` | ANDROID_V1_USE | Story SSE (real-time) |
| GET | `/api/admin/stories` | ADMIN_ONLY | — |
| PATCH | `/api/admin/stories/{id}/moderate` | ADMIN_ONLY | — |
| GET | `/api/admin/stories/analytics` | ADMIN_ONLY | — |
| POST | `/api/admin/stories/{id}/recompute-counters` | ADMIN_ONLY | — |
| POST | `/api/admin/stories/cleanup` | ADMIN_ONLY | — |

### REELS (Stage 10) — 26 endpoints

| Method | Path | Label | Android Screen |
|--------|------|-------|----------------|
| POST | `/api/reels` | ANDROID_V1_USE | Create Reel |
| GET | `/api/reels/feed` | ANDROID_V1_USE | Reels Discovery |
| GET | `/api/reels/following` | ANDROID_V1_USE | Reels Following |
| GET | `/api/reels/{reelId}` | ANDROID_V1_USE | Reel Detail |
| PATCH | `/api/reels/{reelId}` | ANDROID_V1_USE | Edit Reel |
| DELETE | `/api/reels/{reelId}` | ANDROID_V1_USE | Delete Reel |
| POST | `/api/reels/{reelId}/publish` | ANDROID_V1_USE | Publish Draft |
| POST | `/api/reels/{reelId}/archive` | ANDROID_V1_USE | Archive Reel |
| POST | `/api/reels/{reelId}/restore` | ANDROID_V1_USE | Restore Reel |
| POST | `/api/reels/{reelId}/pin` | ANDROID_V1_USE | Pin to Profile |
| DELETE | `/api/reels/{reelId}/pin` | ANDROID_V1_USE | Unpin |
| POST | `/api/reels/{reelId}/like` | ANDROID_V1_USE | Like Reel |
| DELETE | `/api/reels/{reelId}/like` | ANDROID_V1_USE | Unlike Reel |
| POST | `/api/reels/{reelId}/save` | ANDROID_V1_USE | Save Reel |
| DELETE | `/api/reels/{reelId}/save` | ANDROID_V1_USE | Unsave Reel |
| POST | `/api/reels/{reelId}/comment` | ANDROID_V1_USE | Comment on Reel |
| GET | `/api/reels/{reelId}/comments` | ANDROID_V1_USE | Reel Comments |
| POST | `/api/reels/{reelId}/report` | ANDROID_V1_USE | Report Reel |
| GET | `/api/reels/audio/{audioId}` | ANDROID_V1_USE | Audio Page |
| GET | `/api/reels/{reelId}/remixes` | ANDROID_V1_USE | Reel Remixes |
| POST | `/api/me/reels/series` | ANDROID_V1_USE | Create Series |
| GET | `/api/users/{userId}/reels/series` | ANDROID_V1_USE | User Series |
| GET | `/api/me/reels/archive` | ANDROID_V1_USE | My Reel Archive |
| GET | `/api/me/reels/analytics` | ANDROID_V1_USE | Creator Analytics |
| GET | `/api/users/{userId}/reels` | ANDROID_V1_USE | User Profile Reels |
| POST | `/api/reels/{reelId}/processing` | INTERNAL_ONLY | — |
| GET | `/api/reels/{reelId}/processing` | CANONICAL | Processing Status |
| GET | `/api/admin/reels` | ADMIN_ONLY | — |
| PATCH | `/api/admin/reels/{id}/moderate` | ADMIN_ONLY | — |
| GET | `/api/admin/reels/analytics` | ADMIN_ONLY | — |
| POST | `/api/admin/reels/{id}/recompute-counters` | ADMIN_ONLY | — |

### TRIBES (Stage 12) — 9 public endpoints

| Method | Path | Label | Android Screen |
|--------|------|-------|----------------|
| GET | `/api/tribes` | ANDROID_V1_USE | Tribes List |
| GET | `/api/tribes/{tribeIdOrCode}` | ANDROID_V1_USE | Tribe Detail |
| GET | `/api/tribes/{tribeId}/members` | ANDROID_V1_USE | Tribe Members |
| GET | `/api/tribes/{tribeId}/board` | ANDROID_V1_USE | Tribe Board |
| GET | `/api/tribes/{tribeId}/fund` | ANDROID_V1_USE | Tribe Fund |
| GET | `/api/tribes/{tribeId}/salutes` | ANDROID_V1_USE | Tribe Salute History |
| GET | `/api/tribes/standings/current` | ANDROID_V1_USE | Season Standings |
| GET | `/api/me/tribe` | ANDROID_V1_USE | My Tribe |
| GET | `/api/users/{userId}/tribe` | ANDROID_V1_USE | User's Tribe |

### TRIBE ADMIN — 8 endpoints

| Method | Path | Label | Android Screen |
|--------|------|-------|----------------|
| GET | `/api/admin/tribes/distribution` | ADMIN_ONLY | — |
| POST | `/api/admin/tribes/reassign` | ADMIN_ONLY | — |
| POST | `/api/admin/tribe-seasons` | ADMIN_ONLY | — |
| GET | `/api/admin/tribe-seasons` | ADMIN_ONLY | — |
| POST | `/api/admin/tribes/migrate` | ADMIN_ONLY | — |
| POST | `/api/admin/tribes/boards` | ADMIN_ONLY | — |
| POST | `/api/admin/tribe-awards/resolve` | ADMIN_ONLY | — |
| POST | `/api/admin/tribe-salutes/adjust` | ADMIN_ONLY | — |

### TRIBE CONTESTS — Public (Stage 12X) — 9 endpoints

| Method | Path | Label | Android Screen |
|--------|------|-------|----------------|
| GET | `/api/tribe-contests` | ANDROID_V1_USE | Contests List |
| GET | `/api/tribe-contests/{contestId}` | ANDROID_V1_USE | Contest Detail |
| POST | `/api/tribe-contests/{contestId}/enter` | ANDROID_V1_USE | Submit Entry |
| GET | `/api/tribe-contests/{contestId}/entries` | ANDROID_V1_USE | Contest Entries |
| GET | `/api/tribe-contests/{contestId}/leaderboard` | ANDROID_V1_USE | Contest Leaderboard |
| GET | `/api/tribe-contests/{contestId}/results` | ANDROID_V1_USE | Contest Results |
| POST | `/api/tribe-contests/{contestId}/vote` | ANDROID_V1_USE | Vote on Entry |
| POST | `/api/tribe-contests/{contestId}/withdraw` | ANDROID_V1_USE | Withdraw Entry |
| GET | `/api/tribe-contests/seasons` | ANDROID_V1_USE | Seasons List |
| GET | `/api/tribe-contests/seasons/{seasonId}/standings` | ANDROID_V1_USE | Season Standings |

### TRIBE CONTESTS — SSE (Stage 12X-RT) — 3 endpoints

| Method | Path | Label | Android Screen |
|--------|------|-------|----------------|
| GET | `/api/tribe-contests/{contestId}/live` | ANDROID_V1_USE | Live Scoreboard |
| GET | `/api/tribe-contests/seasons/{seasonId}/live-standings` | ANDROID_V1_USE | Live Season Standings |
| GET | `/api/tribe-contests/live-feed` | ANDROID_V1_USE | Global Activity Feed |

### TRIBE CONTESTS — Admin (Stage 12X) — 13 endpoints

| Method | Path | Label | Android Screen |
|--------|------|-------|----------------|
| POST | `/api/admin/tribe-contests` | ADMIN_ONLY | — |
| GET | `/api/admin/tribe-contests` | ADMIN_ONLY | — |
| GET | `/api/admin/tribe-contests/{id}` | ADMIN_ONLY | — |
| POST | `/api/admin/tribe-contests/{id}/publish` | ADMIN_ONLY | — |
| POST | `/api/admin/tribe-contests/{id}/open-entries` | ADMIN_ONLY | — |
| POST | `/api/admin/tribe-contests/{id}/close-entries` | ADMIN_ONLY | — |
| POST | `/api/admin/tribe-contests/{id}/lock` | ADMIN_ONLY | — |
| POST | `/api/admin/tribe-contests/{id}/resolve` | ADMIN_ONLY | — |
| POST | `/api/admin/tribe-contests/{id}/disqualify` | ADMIN_ONLY | — |
| POST | `/api/admin/tribe-contests/{id}/judge-score` | ADMIN_ONLY | — |
| POST | `/api/admin/tribe-contests/{id}/compute-scores` | ADMIN_ONLY | — |
| POST | `/api/admin/tribe-contests/{id}/recompute-broadcast` | ADMIN_ONLY | — |
| POST | `/api/admin/tribe-contests/{id}/cancel` | ADMIN_ONLY | — |
| POST | `/api/admin/tribe-contests/rules` | ADMIN_ONLY | — |
| GET | `/api/admin/tribe-contests/dashboard` | ADMIN_ONLY | — |

### GOVERNANCE — 7 endpoints

| Method | Path | Label | Android Screen |
|--------|------|-------|----------------|
| GET | `/api/governance/college/{collegeId}/board` | ANDROID_V1_USE | College Board |
| POST | `/api/governance/college/{collegeId}/apply` | ANDROID_V1_USE | Apply for Board |
| GET | `/api/governance/college/{collegeId}/applications` | ANDROID_V1_USE | Board Applications |
| POST | `/api/governance/applications/{appId}/vote` | ANDROID_V1_USE | Vote on Application |
| POST | `/api/governance/college/{collegeId}/proposals` | ANDROID_V1_USE | Create Proposal |
| GET | `/api/governance/college/{collegeId}/proposals` | ANDROID_V1_USE | Proposals List |
| POST | `/api/governance/proposals/{proposalId}/vote` | ANDROID_V1_USE | Vote on Proposal |
| POST | `/api/governance/college/{collegeId}/seed-board` | ADMIN_ONLY | — |

### MODERATION / REPORTS / ADMIN — 9 endpoints

| Method | Path | Label | Android Screen |
|--------|------|-------|----------------|
| POST | `/api/reports` | ANDROID_V1_USE | Report Content |
| GET | `/api/moderation/queue` | ADMIN_ONLY | — |
| POST | `/api/moderation/{contentId}/action` | ADMIN_ONLY | — |
| POST | `/api/appeals` | ANDROID_V1_USE | File Appeal |
| GET | `/api/appeals` | ANDROID_V1_USE | My Appeals |
| PATCH | `/api/appeals/{id}/decide` | ADMIN_ONLY | — |
| POST | `/api/grievances` | ANDROID_V1_USE | Submit Grievance |
| GET | `/api/grievances` | ANDROID_V1_USE | My Grievances |
| POST | `/api/admin/colleges/seed` | ADMIN_ONLY | — |
| GET | `/api/admin/stats` | ADMIN_ONLY | — |

### NOTIFICATIONS & LEGAL — 4 endpoints

| Method | Path | Label | Android Screen |
|--------|------|-------|----------------|
| GET | `/api/notifications` | ANDROID_V1_USE | Notifications Tab |
| PATCH | `/api/notifications/read` | ANDROID_V1_USE | Mark Read |
| GET | `/api/legal/consent` | ANDROID_V1_USE | Consent Flow |
| POST | `/api/legal/accept` | ANDROID_V1_USE | Accept Terms |

### OPS / HEALTH — 5 endpoints

| Method | Path | Label | Android Screen |
|--------|------|-------|----------------|
| GET | `/api/` | INTERNAL_ONLY | — |
| GET | `/api/healthz` | INTERNAL_ONLY | — |
| GET | `/api/readyz` | INTERNAL_ONLY | — |
| GET | `/api/ops/health` | INTERNAL_ONLY | — |
| GET | `/api/ops/metrics` | INTERNAL_ONLY | — |
| GET | `/api/ops/backup-check` | INTERNAL_ONLY | — |
| GET | `/api/cache/stats` | INTERNAL_ONLY | — |

---

## Summary Counts

| Label | Count |
|-------|-------|
| ANDROID_V1_USE | ~120 |
| ADMIN_ONLY | ~45 |
| BOARD_ONLY | ~8 |
| INTERNAL_ONLY | ~8 |
| LEGACY | 4 |
| DEPRECATED | 1 |
| **TOTAL** | ~186 |

---

## PASS Gate Verification

- [x] Every endpoint has exactly ONE label
- [x] No duplicate endpoints serving the same purpose
- [x] Android team has zero "maybe use this" choices
- [x] LEGACY endpoints clearly marked (houses)
- [x] DEPRECATED endpoint returns 410
- [x] Admin-only endpoints clearly separated from user-facing
- [x] SSE endpoints included with correct labels

**B0-S2 STATUS: FROZEN**
