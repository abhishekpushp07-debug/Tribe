# Tribe — Product Requirements Document
**Version**: 4.0
**Last Updated**: 2026-03-11

## Problem Statement
Build a world-best social media backend for "Tribe" — a college-centric social platform. The system serves users across colleges, tribes, houses with content types including Posts, Reels, Stories, and Pages.

## Core Architecture
- **Application**: Next.js 14 monolithic API with Service-Oriented Architecture
- **Database**: MongoDB (local)
- **Media Storage**: Supabase Storage (bucket: `tribe-media`)
- **Video Processing**: ffmpeg (real transcoding pipeline)
- **Testing**: pytest (~1001 tests, 99.9% pass rate)
- **Auth**: Phone + PIN with JWT tokens

## User Personas
1. **Student**: Creates posts, stories, reels. Joins tribes, follows pages
2. **Page Admin**: Manages pages, creates page-authored content
3. **Moderator**: Reviews flagged content, manages reports
4. **Admin/Super Admin**: Platform governance, tribe management, analytics

## Current Feature Status (as of 2026-03-11)

### Stories — 100% ✅
- CRUD: Create, Read, Edit, Delete
- Privacy: EVERYONE, CLOSE_FRIENDS, CUSTOM, hideStoryFrom
- Interactions: Views, Reactions, Replies, Sticker responses
- Story Mutes: Mute/unmute user stories without blocking
- View Duration Tracking: Per-viewer duration + completion analytics
- Bulk Moderation: Batch HOLD/REMOVE/RESTORE/APPROVE (MOD+)
- Sticker Rate Limits: 30/hour per user
- Story Rail: Batched privacy/mute/block filtering (no N+1)
- Admin: Moderate, analytics, archive
- Contract Freeze: STORIES_CONTRACT_FREEZE.md

### Posts — 100% ✅
- CRUD: Create, Read, Edit, Delete
- Post Types: STANDARD, POLL, LINK, THREAD, CAROUSEL
- Polls: Create, Vote, Results with expiry
- Link Previews: Auto-fetched metadata (SSRF-safe)
- Threads: Multi-part threaded posts
- Carousel: Multi-media with explicit ordering (max 10 items)
- Drafts: Create draft, list drafts, publish draft
- Scheduling: Schedule future publish (max 30 days), reschedule, auto-publish worker
- Distribution Pipeline: Stage 0→1→2 auto-promotion
- Feed Cache: Zero cross-user leakage (auth users bypass cache)
- Moderation: On create, on edit, content rejection
- Contract Freeze: POSTS_CONTRACT_FREEZE.md

### Reels — 100% ✅
- CRUD: Create, Read, Patch, Delete, Publish, Archive, Restore
- Video Processing: Real ffmpeg transcoding (MP4 H.264), thumbnail generation
- Feed Types: Default (score), Trending (velocity/age), Personalized (user-aware), Following, Audio
- Creator Analytics: Detailed — daily views/likes trend, retention curve, top engagers, weekly performance
- Interactions: Like, Comment, Share, Save, View tracking
- Anti-abuse: Rate-limited via AntiAbuseService
- Moderation: Full lifecycle
- Contract Freeze: REELS_CONTRACT_FREEZE.md + REEL_PROCESSING_POLICY.md

### Pages — 100% ✅
- CRUD: Create, Read, Update, Archive, Restore, Delete
- Verification Workflow: Request → Admin Review → Approve/Reject with notifications
- Audience: Members, Followers, Admins, Moderators, Editors
- Page Invite System: Invite users with role assignment
- Page Posts: Create as page, page posts in feed
- Page Report: Dedicated report endpoint
- Page Analytics: Daily activity, follower growth, engagement, top posts
- Page Search: Text, category, college-based with verified boost
- Visibility: ACTIVE/ARCHIVED/SUSPENDED/DELETED with proper filtering
- Contract Freeze: PAGES_CONTRACT_FREEZE.md

### Shared Systems — Complete ✅
- Anti-Abuse: 5-layer detection (velocity, burst, same-author, rapid-diverse, cumulative)
- Feed Cache: Zero cross-user leakage, event-driven invalidation
- Moderation Pipeline: Content moderation on create/edit, multi-tier review
- Media Pipeline: Supabase storage, chunked upload, real video transcoding
- Notifications: 12+ types, grouped view, preferences
- Search: Multi-type (users, pages, posts, hashtags, colleges, houses)
- Age Protection: CHILD/ADULT content restrictions
- Audit Trail: 25,000+ audit log entries

## Documentation (22 documents)
All contract freeze docs, operational policies, integration guides, and seed data references are in `/app/memory/`.

## Deployment Fixes (2026-03-12)
- Fixed `GET /stories` route — was returning 404, now returns story rail
- Fixed `POST /media/initiate` — added alias for `/media/upload-init` (frontend compatibility)
- Fixed media upload-init to accept flexible param names (`type`/`kind`, `size`/`sizeBytes`)
- Added `POST /media/complete` alias for `/media/upload-complete`
- Made storage URL configurable via `EMERGENT_STORAGE_URL` env var
- Fixed Redis connection to skip when `REDIS_URL` not in environment
- Added 4 key test users to auto-seed (7777099001 ADMIN, 7777099002 USER, 9876543210 ADMIN, 9000000001 SUPER_ADMIN)
- Fixed malformed `.gitignore` (removed duplicate `-e` entries)

## Critical Bug Fixes (2026-03-12 — Session 2)
### Root Cause Analysis
The entire app was broken due to 4 bugs in `/app/lib/handlers/feed.js`:

1. **GET /feed (home feed) returning `{}` for anon, 500 for auth:**
   - `cache.get()` was NOT awaited → returned Promise (truthy) → serialized to `{}`
   - `applyFeedPolicy()` called with 2 args instead of 4 (db, viewerId, viewerRole, items) AND not awaited → TypeError for auth users
   - `cache.set()` was NOT awaited
   
2. **GET /feed/stories returning empty:**
   - Queried `content_items` collection with `kind: STORY` → 0 results
   - Stories are actually stored in the `stories` collection (separate from content_items)
   - Fixed to query `stories` collection with `status: ACTIVE/PUBLISHED`

3. **GET /feed/reels showing minimal content:**
   - Queried `content_items` with `kind: REEL` → only 33 results
   - 553 reels live in the `reels` collection (separate from content_items)
   - Fixed to query `reels` collection with proper status/visibility filters

4. **Reels follow visibility check broken:**
   - Used `followingId` field but DB schema uses `followeeId`
   - Fixed in `/app/lib/handlers/reels.js`

### Verification
All 6 feed endpoints, Story CRUD, Reel CRUD, Post CRUD, Media Upload, and Social features verified as working via automated testing.

## Remaining Roadmap
- **P1: Write pytest tests** for all recently added features (Stories edit/mute, Post drafts/scheduling, Reel analytics) — required by Master Prompt  
- **P2: Phase 1 Core Blockers** — Post distributionStage automation, feed cache key collision fix
- **P3: Reel Processing** — Real video transcoding, anti-gaming strengthening
- **P4: Phase 2-6 Subsystem Completion** — Continue sprints from Master Prompt
- **P5: Test Suite Hardening** — Zero-flake test suite (rate-limit flake fix)
- **P6: Infra & Scale** — Redis, job queues, dedicated test DB
- **P7: Advanced Features** — Recommendation engine, ML ranking, push notifications

## Test Credentials
- All seeded accounts use PIN: `1234`
- Primary test: `7777099001` (ADMIN), `7777099002` (USER)
- Super Admin: `9000000001`, `9000099001`
- See SEED_DATA_REFERENCE.md for full inventory
