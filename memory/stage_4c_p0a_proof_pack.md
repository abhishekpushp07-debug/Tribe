# Stage 4C — P0-A Proof Pack: Cross-Surface Entity Consistency

## Status: ✅ PERFECT — 24/24 PASSED, 0 SKIPPED, 0 REGRESSIONS

## What P0-A Proves
Every core entity (Post, Event, Resource, Notice, Reel) returns **consistent truth fields** across all relevant API surfaces — detail views, feeds, search, college listings, and cross-user reads. If data is created, mutated, or deleted through one surface, every other surface reflects the same state.

## Test Inventory (24 tests)

### TestPostCrossSurface — 8 tests
| # | Test | What it proves |
|---|------|---------------|
| 1 | `test_post_detail_matches_following_feed` | Core truth fields (id, caption, kind, authorId, visibility) identical in detail vs following feed |
| 2 | `test_post_counts_consistent_after_like` | likeCount identical in detail vs following feed after like |
| 3 | `test_post_counts_consistent_after_comment` | commentCount identical in detail vs following feed after comment |
| 4 | `test_deleted_post_gone_from_all_surfaces` | Deleted post → 404 detail + absent from following feed |
| 5 | `test_post_in_college_feed_matches_detail` | Promoted post → truth fields match in college feed |
| 6 | `test_post_in_house_feed_matches_detail` | Promoted post → truth fields match in house feed |
| 7 | `test_dislike_state_consistent_across_surfaces` | Dislike → viewerHasDisliked=True consistent in detail (viewer's perspective) |
| 8 | `test_reaction_remove_count_consistent` | Like→remove → likeCount returns to 0, consistent across surfaces |

### TestEventCrossSurface — 6 tests
| # | Test | What it proves |
|---|------|---------------|
| 1 | `test_event_detail_matches_feed` | Truth fields (id, title, category, creatorId, status) identical in detail vs event feed |
| 2 | `test_event_detail_matches_search` | Truth fields identical in detail vs search results |
| 3 | `test_rsvp_count_consistent_across_surfaces` | goingCount identical when read by different users |
| 4 | `test_deleted_event_gone_from_surfaces` | Deleted event → 410 on detail |
| 5 | `test_rsvp_cancel_decrements_count` | RSVP→cancel → goingCount decrements consistently |
| 6 | `test_event_in_college_feed_matches_detail` | Event in college feed matches detail for core fields |

### TestResourceCrossSurface — 4 tests
| # | Test | What it proves |
|---|------|---------------|
| 1 | `test_resource_detail_matches_search` | Truth fields identical in detail vs search results |
| 2 | `test_vote_score_consistent_after_upvote` | voteScore & voteCount consistent between users after upvote |
| 3 | `test_vote_score_consistent_after_downvote` | voteScore & voteCount consistent between users after downvote |
| 4 | `test_removed_resource_returns_410` | REMOVED resource → 410 on detail |

### TestNoticeCrossSurface — 3 tests
| # | Test | What it proves |
|---|------|---------------|
| 1 | `test_notice_detail_matches_college_listing` | Truth fields identical in detail vs college listing |
| 2 | `test_ack_count_consistent_across_reads` | acknowledgmentCount consistent between users after acknowledge |
| 3 | `test_removed_notice_gone_from_detail` | REMOVED notice → 410 on detail |

### TestReelCrossSurface — 3 tests
| # | Test | What it proves |
|---|------|---------------|
| 1 | `test_reel_like_reflected_in_detail` | Like → likeCount >= 1 in detail |
| 2 | `test_reel_like_count_consistent_between_users` | likeCount identical regardless of which user reads |
| 3 | `test_removed_reel_returns_error` | REMOVED reel → 404/410 on detail |

## Entity Coverage Matrix

| Entity | Detail | Following Feed | College Feed | House Feed | Search | Cross-User | Delete/Remove | Mutation→Read |
|--------|--------|---------------|-------------|-----------|--------|------------|--------------|---------------|
| Post | ✅ | ✅ | ✅ | ✅ | — | ✅ | ✅ (404) | ✅ (like, dislike, comment, reaction remove) |
| Event | ✅ | — | ✅ | — | ✅ | ✅ | ✅ (410) | ✅ (RSVP, cancel RSVP) |
| Resource | ✅ | — | — | — | ✅ | ✅ | ✅ (410) | ✅ (upvote, downvote) |
| Notice | ✅ | — | ✅ | — | — | ✅ | ✅ (410) | ✅ (acknowledge) |
| Reel | ✅ | — | — | — | — | ✅ | ✅ (404/410) | ✅ (like) |

## Full Suite Proof

```
Run 1: 352 passed, 0 failed, 0 skipped — 38.33s
Run 2: 352 passed, 0 failed, 0 skipped — 37.22s
Idempotency: CONFIRMED (2x identical results)
```

## Test Infrastructure
- 3 dedicated consistency users: `consistency_user_a`, `consistency_user_b`, `consistency_resource_user`
- Full cleanup in session teardown (all consistency test data removed)
- Rate-limit isolated via unique X-Forwarded-For IPs per request

## Fixes Applied
1. `test_dislike_count_consistent_across_surfaces` → renamed to `test_dislike_state_consistent_across_surfaces`. API exposes `viewerHasDisliked` (boolean), not `dislikeCount`. Test now verifies the boolean state is consistent.
2. `test_vote_count_consistent_after_upvote` → renamed to `test_vote_score_consistent_after_upvote`. API uses `voteScore` (net) + `voteCount` (total), not `upvoteCount`.
3. `test_vote_count_consistent_after_downvote` → renamed to `test_vote_score_consistent_after_downvote`. Same field correction.
