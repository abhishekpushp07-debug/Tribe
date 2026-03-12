# Tribe — Product Requirements Document
**Version**: 5.0
**Last Updated**: 2026-03-12

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

## Current Feature Status (as of 2026-03-12)

### Critical Bugs Fixed (Session 2)
- GET /feed returned {} (anon) or 500 (auth) — cache.get not awaited + wrong applyFeedPolicy args
- GET /feed/stories returned empty — queried wrong collection
- GET /feed/reels showed minimal content — queried wrong collection  
- Reels follow check used wrong field name (followingId → followeeId)

### 50 New Social Media Features Added (Session 2)

#### Profile & Settings (12 endpoints)
1. GET /me — own profile with stats
2. GET /me/stats — dashboard (posts, reels, stories, followers, following, likes, saves)
3. GET /me/settings — all settings (privacy, notifications, profile, interests)
4. PATCH /me/settings — bulk update settings
5. GET /me/privacy — privacy settings
6. PATCH /me/privacy — toggle private/public, tagging, mentions, online status
7. GET /me/activity — 7-day activity summary
8. POST /me/interests — set interests
9. GET /me/interests — get interests
10. GET /me/login-activity — recent sessions
11. GET /me/bookmarks — all saved content
12. POST /me/deactivate — deactivate account

#### Content Interactions (9 endpoints)
13. POST /content/:id/report — report content
14. POST /content/:id/archive — archive post
15. POST /content/:id/unarchive — restore archived post
16. POST /content/:id/pin — pin to profile
17. DELETE /content/:id/pin — unpin
18. POST /content/:id/hide — hide from feed
19. GET /content/:id/likers — who liked
20. GET /content/:id/shares — who shared/reposted

#### Comment Operations (5 endpoints)
21. POST /content/:id/comments/:cid/reply — threaded replies
22. PATCH /content/:id/comments/:cid — edit comment
23. POST /content/:id/comments/:cid/pin — pin comment (author only)
24. POST /content/:id/comments/:cid/report — report comment
25. DELETE /content/:id/comments/:cid — delete comment

#### Stories (3 endpoints)
26. POST /stories/:id/view — mark as viewed + increment count
27. GET /me/stories/insights — story analytics
28. POST /stories/:id/share — share story as post

#### Reels (4 endpoints)
29. GET /reels/:id/likers — who liked reel
30. GET /me/reels/saved — saved reels list
31. POST /reels/:id/duet — create duet
32. GET /reels/sounds/popular — popular sounds

#### Tribes (8 endpoints)
33. POST /tribes/:id/join — join tribe
34. POST /tribes/:id/leave — leave tribe
35. GET /tribes/:id/feed — tribe content feed
36. GET /tribes/:id/events — tribe events
37. GET /tribes/:id/stats — tribe statistics
38. POST /tribes/:id/cheer — daily cheer (rate-limited)
39. GET /users/:id/mutual-followers — mutual followers

#### Feed & Discovery (7 endpoints)
40. GET /explore — trending posts + reels + hashtags
41. GET /explore/creators — popular creators with follow status
42. GET /explore/reels — trending reels
43. GET /feed/mixed — interleaved posts + reels
44. GET /feed/personalized — interest-based ranking
45. GET /trending/topics — trending hashtags with scores

#### Notifications (2 endpoints)
46. POST /notifications/read-all — mark all read
47. DELETE /notifications/clear — clear all

### Pre-existing Features (from prior sessions)
- Stories: Full CRUD, privacy, reactions, replies, stickers, highlights, close friends, mutes, view duration, bulk moderation
- Posts: CRUD, polls, link previews, threads, carousel, drafts, scheduling
- Reels: CRUD, feed, publish, archive, restore, pin, like/save, comments, report, hide, share, audio, remixes, series, analytics
- Social: Follow/unfollow, like/dislike, comment/reply, save/unsave, share/repost
- Pages: Full CRUD, members, verification, analytics
- Events: Full CRUD, RSVP, attendees, reminders
- Tribes: Leaderboard, standings, distribution, seasons, contests
- Notifications: List, read, unread count, device registration, preferences
- Discovery: Search, hashtags, suggestions, colleges

## Remaining Roadmap
- **P1: Write pytest tests** for all recently added features — required by Master Prompt  
- **P2: Phase 1 Core Blockers** — Post distributionStage automation, feed cache key collision fix
- **P3: Reel Processing** — Real video transcoding, anti-gaming strengthening
- **P4: Phase 2-6 Subsystem Completion** — Continue sprints from Master Prompt
- **P5: Test Suite Hardening** — Zero-flake test suite (rate-limit flake fix)
- **P6: Infra & Scale** — Redis, job queues, dedicated test DB
- **P7: Advanced Features** — Recommendation engine, ML ranking, push notifications

## Test Credentials
- Admin: `7777099001` / PIN: `1234`
- User: `7777099002` / PIN: `1234`
- See SEED_DATA_REFERENCE.md for full inventory
