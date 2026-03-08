# B0-S1 — Canonical Domain Freeze

**Status**: FROZEN  
**Freeze Date**: 2026-02-XX  
**Rule**: One concept = one name. Zero ambiguity. Zero overloading.

---

## Master Domain Dictionary

Every domain concept used in Tribe, its canonical name, its meaning, and where it lives.

### Core Identity Domains

| # | Canonical Term | Definition | Scope | DB Collection(s) | NEVER Confuse With |
|---|---------------|------------|-------|-------------------|-------------------|
| 1 | **user** | A registered human account on Tribe | Global | `users` | member, account, profile |
| 2 | **session** | An authenticated login session (bearer token) | Auth | `sessions` | token, login |
| 3 | **college** | A verified educational institution | Identity | `colleges` | school, university, campus |
| 4 | **claim** | A user's request to verify their college affiliation | Identity | `college_claims` | verification, request |
| 5 | **tribe** | One of 21 permanent groups named after Param Vir Chakra awardees. **CANONICAL identity group.** | Identity | `tribes`, `user_tribe_memberships` | house, team, clan |
| 6 | **house** | **LEGACY** grouping system (12 houses). Deprecated. Do not build new features on this. | Legacy | `houses`, `house_ledger` | tribe |

### Content Domains

| # | Canonical Term | Definition | Scope | DB Collection(s) | NEVER Confuse With |
|---|---------------|------------|-------|-------------------|-------------------|
| 7 | **post** | A text/image content item (kind=POST) | Content | `content_items` | content, article |
| 8 | **story** | An ephemeral 24-hour content item with stickers | Content | `stories` | snap, status |
| 9 | **reel** | A short-form video content item | Content | `reels` | video, clip |
| 10 | **comment** | A text reply to a post | Social | `comments` | reply (on posts), response |
| 11 | **reel_comment** | A text reply to a reel | Social | `reel_comments` | comment (on posts) |
| 12 | **story_reply** | A DM-style text reply to a story (visible only to story author) | Social | `story_replies` | comment, response |
| 13 | **resource** | An academic document (notes, PYQ, assignment, syllabus, lab file) | Library | `resources` | document, file, material |
| 14 | **event** | A campus event with RSVP | Events | `events` | activity, meetup |
| 15 | **notice** | A board-published campus notice/announcement | Board | `board_notices` | post, announcement |
| 16 | **media** | An uploaded binary asset (image/video) identified by mediaId | Storage | `media_assets` | file, attachment, asset |

### Social Action Domains

| # | Canonical Term | Definition | Scope | DB Collection(s) | NEVER Confuse With |
|---|---------------|------------|-------|-------------------|-------------------|
| 17 | **follow** | A user-to-user subscription relationship | Social | `follows` | subscribe, connect |
| 18 | **like** | A positive reaction to a post (social engagement) | Social | `reactions` (type=LIKE) | vote, upvote, heart |
| 19 | **dislike** | A private negative signal on a post (not visible to author) | Social | `reactions` (type=DISLIKE) | downvote |
| 20 | **save** | A user bookmarking content for later | Social | `saves` | bookmark, favorite |
| 21 | **reaction** | A like or dislike on a post (the parent concept) | Social | `reactions` | emoji reaction (stories) |
| 22 | **story_reaction** | An emoji reaction to a story (separate from post likes) | Social | `story_reactions` | like, reaction |
| 23 | **reel_like** | A like on a reel (separate collection from post likes) | Social | `reel_likes` | like (on posts) |
| 24 | **reel_save** | A save/bookmark on a reel | Social | `reel_saves` | save (on posts) |
| 25 | **block** | A bidirectional user-to-user blocking action | Social | `blocks` | mute, hide |

### Contest Domains (Stage 12X)

| # | Canonical Term | Definition | Scope | NEVER Confuse With |
|---|---------------|------------|-------|--------------------|
| 26 | **season** | A time-bounded competitive period for tribes | Contest | year, term |
| 27 | **contest** | A specific competition within a season | Contest | challenge, tournament |
| 28 | **contest_entry** | A user's submission to a contest | Contest | submission, participation |
| 29 | **vote** | A user's support signal for a contest entry. **CONTEST ACTION ONLY.** | Contest | like, upvote, reaction |
| 30 | **score** | A computed numerical result for a contest entry | Contest | points, rating |
| 31 | **judge_score** | A manual score submitted by an authorized judge | Contest | rating, review |
| 32 | **salute** | The tribe reward currency. **ONLY earned through contests or admin grants.** | Tribe Economy | point, coin, credit |
| 33 | **fund** | A tribe's financial/accounting balance derived from salutes | Tribe Economy | wallet, balance |
| 34 | **standing** | A tribe's rank and accumulated salutes within a season | Tribe Economy | ranking, leaderboard |
| 35 | **contest_result** | The official, immutable outcome of a resolved contest | Contest | winner, resolution |
| 36 | **salute_ledger** | The append-only, immutable record of all salute movements | Tribe Economy | transaction log, history |

### Governance Domains

| # | Canonical Term | Definition | Scope | DB Collection(s) | NEVER Confuse With |
|---|---------------|------------|-------|-------------------|-------------------|
| 37 | **board_seat** | A governance position in a college board | Governance | `board_seats` | role, position |
| 38 | **board_application** | A user's candidacy for a board seat | Governance | `board_applications` | application, request |
| 39 | **proposal** | A governance proposal for community decision-making | Governance | `board_proposals` | suggestion, vote |
| 40 | **proposal_vote** | A user's vote on a governance proposal | Governance | `proposal_votes` | vote (contest) |

### Moderation & Trust Domains

| # | Canonical Term | Definition | Scope | DB Collection(s) | NEVER Confuse With |
|---|---------------|------------|-------|-------------------|-------------------|
| 41 | **report** | A user's report of objectionable content | Moderation | `reports` | complaint, flag |
| 42 | **moderation_action** | An admin/moderator action on reported content | Moderation | `moderation_events` | decision, review |
| 43 | **strike** | A penalty mark on a user's account | Moderation | `strikes` | warning, flag |
| 44 | **suspension** | A time-limited account restriction | Moderation | `suspensions` | ban, timeout |
| 45 | **appeal** | A user's request to reverse a moderation action | Moderation | `appeals` | complaint, grievance |
| 46 | **grievance** | A general user complaint (not content-specific) | Support | `grievance_tickets` | report, appeal |
| 47 | **authenticity_tag** | A board/moderator verification tag on resources/events | Trust | `authenticity_tags` | badge, verification |

### System Domains

| # | Canonical Term | Definition | Scope | DB Collection(s) | NEVER Confuse With |
|---|---------------|------------|-------|-------------------|-------------------|
| 48 | **notification** | A system-generated notification to a user | System | `notifications` | message, alert |
| 49 | **audit_log** | An immutable record of system actions | System | `audit_logs` | log, history |
| 50 | **consent** | A user's acceptance of legal terms | Legal | `consent_notices`, `consent_acceptances` | agreement, terms |
| 51 | **feature_flag** | A runtime toggle for features | System | `feature_flags` | config, setting |
| 52 | **distribution_stage** | A content item's visibility tier (0, 1, 2) | Distribution | field on `content_items` | level, rank |

---

## Hard Vocabulary Freeze Rules

### Rule V1: Action Disambiguation
| Action Word | Meaning | Context | NEVER Use For |
|------------|---------|---------|---------------|
| `like` | Social positive engagement | Posts | Contest voting |
| `vote` | Contest support signal | Contests | Social engagement |
| `score` | Computed contest metric | Contests | Social engagement count |
| `salute` | Tribe reward currency | Tribe Economy | Like count, points |
| `fund` | Tribe financial balance | Tribe Economy | Wallet, score |
| `reaction` | Like/dislike on post | Posts | Story emoji reaction |
| `story_reaction` | Emoji on story | Stories | Post like/dislike |
| `reel_like` | Like on reel | Reels | Post like |

### Rule V2: Entity Disambiguation
| Term | Canonical Meaning | NEVER Means |
|------|------------------|-------------|
| `tribe` | 21 Param Vir Chakra groups | House (legacy) |
| `house` | 12 legacy groups (DEPRECATED) | Tribe |
| `standing` | Tribe rank in season | User rank |
| `entry` | Contest submission | Post/content |
| `result` | Contest outcome document | API response |
| `member` | User in context of tribe/college | Generic user |
| `board` | College governance body | Leaderboard |
| `leaderboard` | Contest ranking display | Board (governance) |

### Rule V3: Count Field Disambiguation
| Field | Meaning | Lives On |
|-------|---------|----------|
| `likeCount` | Total likes on a post | `content_items` |
| `dislikeCount` | Total dislikes on a post | `content_items` |
| `commentCount` | Total comments on a post | `content_items` |
| `viewCount` | Total views on a post | `content_items` |
| `followersCount` | Total followers of user | `users` |
| `followingCount` | Total following of user | `users` |
| `postsCount` | Total posts by user | `users` |
| `rsvpCount.going` | Total GOING RSVPs | `events` |
| `rsvpCount.interested` | Total INTERESTED RSVPs | `events` |
| `voteScore` | Net vote score on resource | `resources` |
| `voteCount` | Total votes on resource | `resources` |
| `downloadCount` | Total downloads of resource | `resources` |
| `totalSalutes` | Accumulated salutes for tribe | `tribe_standings`, `tribes` |
| `contestsWon` | Contests won by tribe in season | `tribe_standings` |
| `contestsParticipated` | Contests tribe participated in | `tribe_standings` |

---

## PASS Gate Verification

- [x] Every concept has exactly one canonical name
- [x] No overloaded or ambiguous terms
- [x] `like` vs `vote` vs `score` vs `salute` vs `fund` — all distinct
- [x] `house` (legacy) vs `tribe` (canonical) — hard boundary
- [x] `reaction` (post) vs `story_reaction` vs `reel_like` — all separate
- [x] Android agent will have zero concept-level confusion
- [x] Count fields unambiguous per entity

**B0-S1 STATUS: FROZEN**
