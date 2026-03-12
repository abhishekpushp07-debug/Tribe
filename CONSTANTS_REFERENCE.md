# Tribe — Constants, Enums & Configuration Reference

> Every enum, error code, config value, and constant used across the Tribe backend.
> Use this as the definitive source of truth for building type-safe Android/iOS models.

---

## Table of Contents
1. [User Enums](#1-user-enums)
2. [Content Enums](#2-content-enums)
3. [Story Enums & Config](#3-story-enums--config)
4. [Reel Enums & Config](#4-reel-enums--config)
5. [Page Enums](#5-page-enums)
6. [Event Enums](#6-event-enums)
7. [Tribe System](#7-tribe-system)
8. [Contest Enums](#8-contest-enums)
9. [Moderation Enums](#9-moderation-enums)
10. [Resource Enums](#10-resource-enums)
11. [Error Codes (Complete)](#11-error-codes-complete)
12. [Notification Types](#12-notification-types)
13. [SSE Event Types](#13-sse-event-types)
14. [Anti-Abuse Thresholds](#14-anti-abuse-thresholds)
15. [Config Limits](#15-config-limits)
16. [Scoring Rules](#16-scoring-rules)
17. [Cache TTLs](#17-cache-ttls)
18. [The 21 Tribes](#18-the-21-tribes)

---

## 1. User Enums

### AgeStatus
```
UNKNOWN    — Not yet verified
ADULT      — 18+ (full access)
CHILD      — Under 18 (restricted content creation)
```

### Role
```
USER         — Standard user
MODERATOR    — Can moderate content
ADMIN        — Full admin access
SUPER_ADMIN  — Superuser
```

### OnboardingStep
```
AGE      — Need to set birth year
COLLEGE  — Need to select college
PROFILE  — Need to set username/bio
DONE     — Onboarding complete
```

### Privacy Settings
```
allowTagging:  EVERYONE | FOLLOWERS | NONE
allowMentions: EVERYONE | FOLLOWERS | NONE
```

---

## 2. Content Enums

### ContentKind
```
POST    — Standard post
REEL    — Short video
STORY   — 24h ephemeral content
```

### Visibility
```
PUBLIC          — Visible to all
LIMITED         — Limited distribution (strike/warning)
SHADOW_LIMITED  — Author thinks it's public, but hidden from feeds
HELD_FOR_REVIEW — Pending moderation
REMOVED         — Soft deleted / moderated
```

### PostSubType
```
STANDARD    — Regular post (text + optional media)
POLL        — Poll post with voting options
THREAD_HEAD — First post in a thread
THREAD_PART — Subsequent thread part
LINK        — Link preview post
CAROUSEL    — Multi-image carousel
```

### Post Status
```
PUBLISHED   — Live and visible
DRAFT       — Saved as draft
SCHEDULED   — Future publish date set
ARCHIVED    — Archived by author
```

---

## 3. Story Enums & Config

### StoryType
```
IMAGE   — Photo story
VIDEO   — Video story
TEXT    — Text-only story (colored background)
```

### StoryStatus
```
ACTIVE   — Live (within 24h TTL)
EXPIRED  — Past 24h (auto-archived)
REMOVED  — Moderated/deleted
HELD     — Held for moderation review
```

### StoryPrivacy
```
EVERYONE      — All users
FOLLOWERS     — Followers only
CLOSE_FRIENDS — Close friends list only
```

### StoryReplyPrivacy
```
EVERYONE      — All can reply
FOLLOWERS     — Followers only
CLOSE_FRIENDS — Close friends only
OFF           — Replies disabled
```

### Sticker Types
```
POLL          — Binary/multi-option poll
QUESTION      — Open-ended question box
QUIZ          — Quiz with correct answer
EMOJI_SLIDER  — Emoji-based slider (0.0 to 1.0)
MENTION       — @mention sticker
LOCATION      — Location tag
HASHTAG       — #hashtag sticker
LINK          — URL link sticker
COUNTDOWN     — Countdown timer
MUSIC         — Music track sticker
```

### Valid Reactions (6 emojis)
```
❤️  🔥  😂  😮  😢  👏
```

### Story Config Limits
| Config | Value |
|--------|-------|
| TTL | 24 hours |
| Max stickers per story | 5 |
| Max caption length | 2200 chars |
| Max poll options | 4 |
| Min poll options | 2 |
| Max quiz options | 4 |
| Max question length | 500 chars |
| Max option length | 100 chars |
| Max reply length | 1000 chars |
| Max close friends | 500 |
| Max highlights per user | 50 |
| Max stories per highlight | 100 |
| Max highlight name length | 50 chars |
| Hourly creation limit | 30 |
| Background types | SOLID, GRADIENT, IMAGE |

---

## 4. Reel Enums & Config

### ReelStatus
```
DRAFT      — Not yet published
PUBLISHED  — Live
ARCHIVED   — Hidden from public
REMOVED    — Moderated/deleted
HELD       — Held for review
```

### ReelVisibility
```
PUBLIC     — Everyone can see
FOLLOWERS  — Followers only
PRIVATE    — Only creator
```

### MediaStatus
```
UPLOADING   — File being uploaded
PROCESSING  — Transcoding/processing
READY       — Ready to play
FAILED      — Processing failed
```

### Reel Limits
| Config | Value |
|--------|-------|
| Max duration | 90 seconds (90000ms) |
| Max caption | 2200 chars |
| Max hashtags | 30 |
| Max mentions | 20 |
| Max video size | 30 MB |

---

## 5. Page Enums

### PageCategory
```
COLLEGE_OFFICIAL  — Official college page
DEPARTMENT        — Department page
CLUB              — Student club
TRIBE_OFFICIAL    — Official tribe page
FEST              — Festival/event page
MEME              — Meme page
STUDY_GROUP       — Study group
HOSTEL            — Hostel page
STUDENT_COUNCIL   — Student council
ALUMNI_CELL       — Alumni network
PLACEMENT_CELL    — Placement cell
OTHER             — Uncategorized
```

### PageStatus
```
DRAFT      — Not yet published
ACTIVE     — Live
ARCHIVED   — Archived
SUSPENDED  — Suspended by admin
```

### PageRole (hierarchy)
```
OWNER (4)      — Full control, transfer ownership
ADMIN (3)      — Manage identity, members, content
EDITOR (2)     — Create/edit/delete content
MODERATOR (1)  — Moderate comments/reports
```

### VerificationStatus
```
NONE      — Not requested
PENDING   — Under review
VERIFIED  — Verified (blue checkmark)
REJECTED  — Request denied
```

### LinkedEntityType
```
COLLEGE | TRIBE | DEPARTMENT | CLUB | FEST | HOSTEL | STUDY_GROUP | HOUSE | OTHER
```

---

## 6. Event Enums

### EventCategory
```
ACADEMIC   — Academic event
CULTURAL   — Cultural event
SPORTS     — Sports event
SOCIAL     — Social gathering
WORKSHOP   — Workshop/seminar
PLACEMENT  — Placement related
OTHER      — Other
```

### EventVisibility
```
PUBLIC   — Open to all
COLLEGE  — College members only
PRIVATE  — Invite only
```

### EventStatus
```
DRAFT      — Not published
PUBLISHED  — Live
CANCELLED  — Cancelled
ARCHIVED   — Past event
HELD       — Held for moderation
REMOVED    — Removed
```

### RSVPStatus
```
GOING       — Attending
INTERESTED  — Might attend
```

---

## 7. Tribe System

### Tribe Assignment
- Deterministic: `SHA-256(userId) mod 21`
- Permanent — cannot be changed by user
- Same userId always maps to same tribe

### 21 Tribes (Param Vir Chakra Heroes)
| # | Code | Hero | Animal | Primary Color |
|---|------|------|--------|---------------|
| 1 | SOMNATH | Major Somnath Sharma | lion | #B71C1C |
| 2 | JADUNATH | Naik Jadunath Singh | tiger | #E65100 |
| 3 | PIRU | CHM Piru Singh | panther | #4A148C |
| 4 | KARAM | Lance Naik Karam Singh | wolf | #1B5E20 |
| 5 | RANE | 2nd Lt Rama Raghoba Rane | rhino | #37474F |
| 6 | SALARIA | Capt Gurbachan Singh Salaria | falcon | #0D47A1 |
| 7 | THAPA | Major Dhan Singh Thapa | snow_leopard | #006064 |
| 8 | JOGINDER | Subedar Joginder Singh | bear | #5D4037 |
| 9 | SHAITAN | Major Shaitan Singh | eagle | #263238 |
| 10 | HAMID | CQMH Abdul Hamid | cobra | #1A237E |
| 11 | TARAPORE | Lt Col AB Tarapore | bull | #880E4F |
| 12 | EKKA | Lance Naik Albert Ekka | jaguar | #2E7D32 |
| 13 | SEKHON | Fg Off NJ Singh Sekhon | hawk | #1565C0 |
| 14 | HOSHIAR | Major Hoshiar Singh | bison | #6D4C41 |
| 15 | KHETARPAL | 2nd Lt Arun Khetarpal | stallion | #3E2723 |
| 16 | BANA | Naib Subedar Bana Singh | mountain_wolf | #004D40 |
| 17 | PARAMESWARAN | Major R Parameswaran | black_panther | #311B92 |
| 18 | PANDEY | Lt Manoj Kumar Pandey | leopard | #C62828 |
| 19 | YADAV | Grenadier YS Yadav | iron_tiger | #AD1457 |
| 20 | SANJAY | Rfn Sanjay Kumar | honey_badger | #2C3E50 |
| 21 | BATRA | Capt Vikram Batra | phoenix_wolf | #D32F2F |

---

## 8. Contest Enums

### ContestStatus (State Machine)
```
DRAFT → PUBLISHED → ENTRY_OPEN → ENTRY_CLOSED → EVALUATING → LOCKED → RESOLVED
                                                                    ↘ CANCELLED
```

### Valid Transitions
| From | To |
|------|----|
| DRAFT | PUBLISHED |
| PUBLISHED | ENTRY_OPEN, CANCELLED |
| ENTRY_OPEN | ENTRY_CLOSED, CANCELLED |
| ENTRY_CLOSED | EVALUATING, CANCELLED |
| EVALUATING | LOCKED, CANCELLED |
| LOCKED | RESOLVED, CANCELLED |

---

## 9. Moderation Enums

### ReportReason
```
SPAM           — Spam content
HARASSMENT     — Harassment/bullying
INAPPROPRIATE  — Inappropriate content
HATE_SPEECH    — Hate speech
VIOLENCE       — Violence/threats
MISINFORMATION — Misinformation
OTHER          — Other reason
```

### ReportStatus
```
OPEN       — New report
REVIEWING  — Under review
RESOLVED   — Action taken
DISMISSED  — No action needed
```

### ModerationAction
```
APPROVE       — Content approved
HOLD          — Hold for review
REMOVE        — Remove content
SHADOW_LIMIT  — Shadow limit (user unaware)
STRIKE        — Issue a strike
SUSPEND       — Suspend user
BAN           — Ban user permanently
```

### AppealStatus
```
PENDING    — Waiting for review
REVIEWING  — Under review
APPROVED   — Appeal approved (content restored)
DENIED     — Appeal denied
```

### CollegeClaimStatus
```
PENDING       — Awaiting verification
APPROVED      — Verified
REJECTED      — Rejected
WITHDRAWN     — User withdrew
FRAUD_REVIEW  — Flagged for fraud
```

### ClaimType
```
STUDENT_ID          — Student ID card
EMAIL               — College email verification
DOCUMENT            — Supporting document
ENROLLMENT_NUMBER   — Enrollment number
```

---

## 10. Resource Enums

### ResourceKind
```
NOTE        — Class notes
PYQ         — Previous year questions
ASSIGNMENT  — Assignment
SYLLABUS    — Course syllabus
LAB_FILE    — Lab file/manual
```

### ResourceStatus
```
PUBLIC       — Visible to all
HELD         — Held for moderation
UNDER_REVIEW — Under review
REMOVED      — Removed
```

### VoteDirection
```
UP    — Upvote (helpful)
DOWN  — Downvote (not helpful)
```

### SortOptions
```
recent           — Newest first
popular          — Most upvoted
most_downloaded  — Most downloaded
```

---

## 11. Error Codes (Complete)

### Core HTTP Errors
| Code | HTTP Status | Meaning |
|------|------------|---------|
| `VALIDATION_ERROR` | 400 | Invalid request data |
| `UNAUTHORIZED` | 401 | Not authenticated |
| `FORBIDDEN` | 403 | Not authorized |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource already exists |
| `RATE_LIMITED` | 429 | Too many requests |
| `PAYLOAD_TOO_LARGE` | 413 | Request body too large |
| `INTERNAL_ERROR` | 500 | Server error |

### Auth-Specific Errors
| Code | HTTP Status | Meaning |
|------|------------|---------|
| `AGE_REQUIRED` | 403 | Must set age first |
| `CHILD_RESTRICTED` | 403 | Under-18 restriction |
| `BANNED` | 403 | Account permanently banned |
| `SUSPENDED` | 403 | Account temporarily suspended |
| `ACCESS_TOKEN_EXPIRED` | 401 | Use refresh token to get new access token |
| `REFRESH_TOKEN_INVALID` | 401 | Refresh token expired/invalid |
| `REFRESH_TOKEN_REUSED` | 401 | Replay attack — force logout all sessions |
| `SESSION_LIMIT_EXCEEDED` | 403 | Too many active sessions |
| `SESSION_NOT_FOUND` | 404 | Session ID not found |
| `RE_AUTH_REQUIRED` | 401 | PIN re-verification needed |

### Domain-Specific Errors
| Code | HTTP Status | Meaning |
|------|------------|---------|
| `INVALID_STATE` | 400 | State machine violation |
| `GONE` | 410 | Resource permanently removed |
| `EXPIRED` | 410 | Temporal resource expired (stories) |
| `DUPLICATE` | 409 | Idempotent action already done |
| `SELF_ACTION` | 400 | Can't perform action on own resource |
| `LIMIT_EXCEEDED` | 400 | Domain limit reached |
| `CONTENT_REJECTED` | 422 | Moderation rejection |
| `COOLDOWN_ACTIVE` | 429 | Action in cooldown period |
| `MEDIA_NOT_READY` | 400 | Media still processing |

### Contest-Specific Errors
| Code | Meaning |
|------|---------|
| `CONTEST_NOT_OPEN` | Contest not accepting actions |
| `ENTRY_PERIOD_ENDED` | Entry period closed |
| `NO_TRIBE` | User not in a tribe |
| `TRIBE_NOT_ELIGIBLE` | Tribe not eligible for this contest |
| `MAX_ENTRIES_REACHED` | Total entry cap hit |
| `TRIBE_MAX_ENTRIES` | Per-tribe entry cap hit |
| `DUPLICATE_CONTENT` | Same content already entered |
| `NOT_RESOLVED` | Contest not yet resolved |
| `VOTING_CLOSED` | Voting period closed |
| `VOTING_DISABLED` | Voting not enabled |
| `ENTRY_NOT_FOUND` | Entry ID not found |
| `SELF_VOTE_BLOCKED` | Can't vote for own entry |
| `DUPLICATE_VOTE` | Already voted for this entry |
| `VOTE_CAP_REACHED` | Max votes per user reached |
| `INVALID_STATUS` | Invalid contest status |
| `INVALID_TRANSITION` | Invalid state transition |
| `ALREADY_DISQUALIFIED` | Entry already disqualified |
| `DUPLICATE_CODE` | Contest code already exists |

---

## 12. Notification Types

| Type | Actor | Target | User Message |
|------|-------|--------|-------------|
| `FOLLOW` | Follower | User | "started following you" |
| `LIKE` | Liker | Content | "liked your post" |
| `COMMENT` | Commenter | Content | "commented on your post" |
| `COMMENT_LIKE` | Liker | Comment | "liked your comment" |
| `SHARE` | Sharer | Content | "shared your post" |
| `MENTION` | Mentioner | Content | "mentioned you in a post" |
| `REPORT_RESOLVED` | System | Report | "Your report has been reviewed" |
| `STRIKE_ISSUED` | System | User | "You received a community strike" |
| `APPEAL_DECIDED` | System | Appeal | "Your appeal has been decided" |
| `HOUSE_POINTS` | System | Tribe | "Your tribe earned points!" |
| `REEL_LIKE` | Liker | Reel | "liked your reel" |
| `REEL_COMMENT` | Commenter | Reel | "commented on your reel" |
| `REEL_SHARE` | Sharer | Reel | "shared your reel" |
| `STORY_REACTION` | Reactor | Story | "reacted to your story" |
| `STORY_REPLY` | Replier | Story | "replied to your story" |
| `STORY_REMOVED` | System | Story | "Your story was removed" |

---

## 13. SSE Event Types

### Story Events (via /api/stories/events/stream)
| Event | Payload | Description |
|-------|---------|-------------|
| `connected` | `{ userId, connectedAt, mode }` | Initial connection |
| `story.viewed` | `{ storyId, viewerId, viewedAt }` | Someone viewed your story |
| `story.reacted` | `{ storyId, userId, emoji }` | Emoji reaction |
| `story.replied` | `{ storyId, userId, text }` | Text reply |
| `story.sticker_responded` | `{ storyId, stickerId, userId }` | Sticker response |
| `story.expired` | `{ storyId }` | Story expired (24h) |

### Contest Live Events
| Event | Description |
|-------|-------------|
| `entry_submitted` | New contest entry |
| `vote_cast` | Vote recorded |
| `score_update` | Score changed |
| `rank_change` | Ranking position changed |
| `contest_state_change` | Contest status transition |

---

## 14. Anti-Abuse Thresholds

| Action | Per Minute | Per Hour |
|--------|-----------|----------|
| Likes | 30 | 200 |
| Comments | 15 | 80 |
| Shares | 10 | 50 |
| Saves | 15 | 100 |
| Views | 60 | — |
| Story Reactions | 20 | — |

### Suspicious Behavior
- 5+ likes on same content in 5 seconds → flagged
- 3+ actions/second sustained for 10s → flagged
- Rapid likes on same author's content in 60s → flagged

---

## 15. Config Limits

### Content Limits
| Config | Value |
|--------|-------|
| Max caption length | 2200 chars |
| Max comment length | 1000 chars |
| Max bio length | 150 chars |
| Max display name | 50 chars |
| Min display name | 2 chars |
| Max username | 30 chars |
| Min username | 3 chars |
| Username regex | `[a-z0-9._]` |
| Max interests | 20 |
| Max close friends | 500 |
| Max highlights per user | 50 |
| Max stories per highlight | 100 |

### Media Limits
| Config | Value |
|--------|-------|
| Max image size | 5 MB |
| Max video size | 30 MB |
| Max reel duration | 90 seconds |
| Story TTL | 24 hours |

### Session & Auth
| Config | Value |
|--------|-------|
| Access token TTL | 15 minutes |
| Refresh token TTL | 30 days |
| Max concurrent sessions | 10 |
| PIN length | 4 digits |
| Phone length | 10 digits |
| PIN hashing | PBKDF2 (100K iterations, SHA-512) |

### Pagination
| Config | Value |
|--------|-------|
| Default page limit | 20 |
| Max page limit | 50 |

### Resources
| Config | Value |
|--------|-------|
| Max title length | 200 chars |
| Min title length | 3 chars |
| Max description | 2000 chars |
| Auto-hold report threshold | 3 reports |
| Daily download rate limit | 50 |
| Hourly upload rate limit | 10 |

---

## 16. Scoring Rules

### Tribe Engagement Scoring (v3)
| Action | Points |
|--------|--------|
| Upload (post/reel/story) | 100 |
| Like received | 10 |
| Comment received | 20 |
| Share received | 50 |
| Story reaction received | 15 |
| Story reply received | 25 |

### Viral Bonuses (per reel)
| Threshold | Bonus Points | Label |
|-----------|-------------|-------|
| 1,000 likes | +1,000 | viral |
| 5,000 likes | +3,000 | super_viral |
| 10,000 likes | +5,000 | mega_viral |

*Bonuses are cumulative: a reel with 12K likes earns 1000+3000+5000 = 9000 bonus*

### Anti-Cheat Upload Caps
| Period | Max Uploads Per User |
|--------|---------------------|
| 7 days | 350 |
| 30 days | 1,500 |
| 90 days | 4,500 |
| All time | 50,000 |

### Smart Feed Scoring Weights
| Signal | Weight |
|--------|--------|
| Like | ×1 |
| Comment | ×3 |
| Save | ×5 |
| Share | ×2 |
| View (reels) | ×0.1 |

### Feed Algorithm Boosts
| Signal | Boost |
|--------|-------|
| Following the author | +0.5 affinity |
| Same tribe | +0.3 affinity |
| Media present | ×1.15 quality |
| Carousel (multi-image) | ×1.05 quality |
| Good caption (50-500 chars) | ×1.05 quality |
| Unseen from followed | ×1.30 quality |
| Viral (2× avg velocity) | ×1.20 boost |
| Same author penalty (2nd post) | ×0.70 |
| Same author penalty (3rd+) | ×0.40 |
| Content type repetition (3+) | ×0.85 |
| Muted author | ×0.01 |
| Hidden post | ×0.00 |

### Half-Lives
| Content Type | Half-Life |
|-------------|-----------|
| Posts | 6 hours |
| Reels | 12 hours |

---

## 17. Cache TTLs (Server-Side)

| Cache | TTL | Notes |
|-------|-----|-------|
| Public feed | 15s | Frequently updated |
| College feed | 30s | Per-college |
| Tribe feed | 30s | Per-tribe |
| Reels feed | 15-30s | Discovery/trending |
| Stories feed | 10s | Short for freshness |
| Story detail | 15s | Per-story |
| Tribe leaderboard | 60s | Expensive query |
| Tribe list | 2 min | Rarely changes |
| Search results | 20s | Per-query |
| Autocomplete | 15s | Per-query |
| Analytics | 60-120s | Per-user |
| Explore page | 30s | Global |
| User profile | 60s | Per-user |
| Notifications | 10s | Short for real-time |

---

## 18. The 21 Tribes (Full Reference)

Each tribe includes:
```json
{
  "tribeCode": "BATRA",
  "tribeName": "Batra Tribe",
  "heroName": "Captain Vikram Batra",
  "paramVirChakraName": "Captain Vikram Batra",
  "animalIcon": "phoenix_wolf",
  "primaryColor": "#D32F2F",
  "secondaryColor": "#FFCDD2",
  "quote": "Victory belongs to the fearless.",
  "sortOrder": 21
}
```

### Tribe Quotes (for UI display)
| Tribe | Quote |
|-------|-------|
| Somnath | "Stand first. Stand firm. Stand for all." |
| Jadunath | "Courage does not wait for numbers." |
| Piru | "Advance through fear. Never around it." |
| Karam | "Duty is the calm inside chaos." |
| Rane | "Break the obstacle. Build the path." |
| Salaria | "Strike with speed. Rise with honour." |
| Thapa | "Hold the heights. Hold the line." |
| Joginder | "Strength means staying when others fall." |
| Shaitan | "Sacrifice turns duty into legend." |
| Hamid | "Precision defeats power." |
| Tarapore | "Lead from the front. Always." |
| Ekka | "Silent grit. Relentless spirit." |
| Sekhon | "Own the sky. Fear nothing." |
| Hoshiar | "True force protects before it conquers." |
| Khetarpal | "Charge beyond doubt." |
| Bana | "Impossible is a peak to be climbed." |
| Parameswaran | "Resolve is the sharpest weapon." |
| Pandey | "If the mission is worthy, give all." |
| Yadav | "Endurance is courage over time." |
| Sanjay | "Keep going. Then go further." |
| Batra | "Victory belongs to the fearless." |

---

*Tribe Constants Reference v3.0.0 — 21 tribes, 95 collections, 60+ error codes, 16 notification types*
