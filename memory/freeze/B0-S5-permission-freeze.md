# B0-S5 — Role & Permission Freeze

**Status**: FROZEN  
**Freeze Date**: 2026-02-XX  
**Rule**: Every role has explicit capabilities. Android never shows a CTA the user cannot execute.

---

## 1. Role Hierarchy

```
SUPER_ADMIN (highest)
    │
  ADMIN
    │
  MODERATOR
    │
  USER (default)
    │
  CHILD_USER (USER with ageStatus=CHILD)
    │
  ANONYMOUS (lowest, no token)
```

### Special Context-Dependent Roles
| Role | Context | How Assigned |
|------|---------|-------------|
| **BOARD_MEMBER** | College governance | Elected via `/governance/.../apply` + vote |
| **JUDGE** | Contest scoring | Admin-assigned per contest |
| **CONTEST_ADMIN** | Contest management | Admin role automatically grants this |

---

## 2. Master Permission Matrix

### 2.1 Content Permissions

| Action | ANONYMOUS | CHILD_USER | USER | MODERATOR | ADMIN | SUPER_ADMIN |
|--------|-----------|------------|------|-----------|-------|-------------|
| View public post | YES | YES | YES | YES | YES | YES |
| View college post | YES | YES | YES | YES | YES | YES |
| Create text post | NO | YES | YES | YES | YES | YES |
| Create media post | NO | NO | YES | YES | YES | YES |
| Create reel | NO | NO | YES | YES | YES | YES |
| Create story | NO | NO | YES | YES | YES | YES |
| Upload media | NO | NO | YES | YES | YES | YES |
| Delete own post | NO | YES | YES | YES | YES | YES |
| Delete any post | NO | NO | NO | YES | YES | YES |
| Like/dislike post | NO | YES | YES | YES | YES | YES |
| Comment on post | NO | YES | YES | YES | YES | YES |
| Save/bookmark post | NO | YES | YES | YES | YES | YES |
| Report content | NO | YES | YES | YES | YES | YES |

### 2.2 Social Permissions

| Action | ANONYMOUS | CHILD_USER | USER | MODERATOR | ADMIN |
|--------|-----------|------------|------|-----------|-------|
| View profiles | YES | YES | YES | YES | YES |
| Follow/unfollow | NO | YES | YES | YES | YES |
| Search users | YES | YES | YES | YES | YES |
| Block/unblock | NO | YES | YES | YES | YES |
| Manage close friends | NO | NO | YES | YES | YES |

### 2.3 Story Permissions

| Action | ANONYMOUS | CHILD_USER | USER | MODERATOR | ADMIN |
|--------|-----------|------------|------|-----------|-------|
| View stories (per privacy) | NO | YES | YES | YES | YES |
| Create story | NO | NO | YES | YES | YES |
| React to story | NO | YES | YES | YES | YES |
| Reply to story | NO | YES | YES | YES | YES |
| Respond to sticker | NO | YES | YES | YES | YES |
| View own story viewers | NO | NO | YES | YES | YES |
| Manage highlights | NO | NO | YES | YES | YES |
| Moderate stories | NO | NO | NO | YES | YES |
| View story analytics | NO | NO | NO | YES | YES |
| Trigger story cleanup | NO | NO | NO | NO | YES |

### 2.4 Reel Permissions

| Action | ANONYMOUS | CHILD_USER | USER | MODERATOR | ADMIN |
|--------|-----------|------------|------|-----------|-------|
| View reels feed | YES | YES | YES | YES | YES |
| View reel detail | YES | YES | YES | YES | YES |
| Create reel | NO | NO | YES | YES | YES |
| Edit own reel | NO | NO | YES | YES | YES |
| Delete own reel | NO | NO | YES | YES | YES |
| Like/save reel | NO | YES | YES | YES | YES |
| Comment on reel | NO | YES | YES | YES | YES |
| Report reel | NO | YES | YES | YES | YES |
| View own analytics | NO | NO | YES | YES | YES |
| Moderate any reel | NO | NO | NO | YES | YES |
| View platform analytics | NO | NO | NO | YES | YES |
| Recompute counters | NO | NO | NO | NO | YES |

### 2.5 Event Permissions

| Action | ANONYMOUS | CHILD_USER | USER | MODERATOR | ADMIN |
|--------|-----------|------------|------|-----------|-------|
| View events | YES | YES | YES | YES | YES |
| Create event | NO | NO | YES | YES | YES |
| RSVP to event | NO | YES | YES | YES | YES |
| Edit own event | NO | NO | YES | YES | YES |
| Delete own event | NO | NO | YES | YES | YES |
| Cancel own event | NO | NO | YES | YES | YES |
| Report event | NO | YES | YES | YES | YES |
| Moderate any event | NO | NO | NO | YES | YES |

### 2.6 Resource (Notes/PYQ) Permissions

| Action | ANONYMOUS | CHILD_USER | USER | MODERATOR | ADMIN |
|--------|-----------|------------|------|-----------|-------|
| Search resources | YES | YES | YES | YES | YES |
| View resource | YES | YES | YES | YES | YES |
| Create resource | NO | NO | YES (ADULT) | YES | YES |
| Vote on resource | NO | YES | YES | YES | YES |
| Download resource | NO | YES | YES | YES | YES |
| Report resource | NO | YES | YES | YES | YES |
| Moderate resource | NO | NO | NO | YES | YES |
| Recompute counters | NO | NO | NO | NO | YES |

### 2.7 Board Notice Permissions

| Action | ANONYMOUS | USER | BOARD_MEMBER | MODERATOR | ADMIN |
|--------|-----------|------|-------------|-----------|-------|
| View published notices | YES | YES | YES | YES | YES |
| Acknowledge notice | NO | YES | YES | YES | YES |
| Create notice | NO | NO | YES | NO | YES |
| Edit own notice | NO | NO | YES | NO | YES |
| Pin/unpin notice | NO | NO | YES | NO | YES |
| Review pending notices | NO | NO | NO | YES | YES |
| Approve/reject notices | NO | NO | NO | YES | YES |

### 2.8 Authenticity Tag Permissions

| Action | ANONYMOUS | USER | BOARD_MEMBER | MODERATOR | ADMIN |
|--------|-----------|------|-------------|-----------|-------|
| View tags | YES | YES | YES | YES | YES |
| Add tag | NO | NO | YES | YES | YES |
| Remove own tag | NO | NO | YES | YES | YES |
| Remove any tag | NO | NO | NO | NO | YES |

### 2.9 Tribe Permissions

| Action | ANONYMOUS | USER | MODERATOR | ADMIN |
|--------|-----------|------|-----------|-------|
| View tribes | YES | YES | YES | YES |
| View tribe detail | YES | YES | YES | YES |
| View standings | YES | YES | YES | YES |
| View my tribe | NO | YES | YES | YES |
| Reassign user tribe | NO | NO | NO | YES |
| Manage seasons | NO | NO | NO | YES |
| Adjust salutes | NO | NO | NO | YES |
| Migrate house→tribe | NO | NO | NO | YES |
| Manage tribe boards | NO | NO | NO | YES |

### 2.10 Contest Permissions

| Action | ANONYMOUS | USER | JUDGE | ADMIN |
|--------|-----------|------|-------|-------|
| View contest list | YES | YES | YES | YES |
| View contest detail | YES | YES | YES | YES |
| View leaderboard | YES | YES | YES | YES |
| View results | YES | YES | YES | YES |
| Submit entry | NO | YES (must have tribe) | YES | YES |
| Vote on entry | NO | YES | YES | YES |
| Withdraw own entry | NO | YES | YES | YES |
| Connect to live SSE | YES | YES | YES | YES |
| Create contest | NO | NO | NO | YES |
| Publish/transition contest | NO | NO | NO | YES |
| Submit judge score | NO | NO | YES | YES |
| Compute scores | NO | NO | NO | YES |
| Resolve contest | NO | NO | NO | YES |
| Disqualify entry | NO | NO | NO | YES |
| Cancel contest | NO | NO | NO | YES |
| Add contest rules | NO | NO | NO | YES |
| View admin dashboard | NO | NO | NO | YES |

### 2.11 Governance Permissions

| Action | ANONYMOUS | USER | BOARD_MEMBER | ADMIN |
|--------|-----------|------|-------------|-------|
| View college board | YES | YES | YES | YES |
| Apply for board seat | NO | YES | YES | YES |
| View applications | NO | YES | YES | YES |
| Vote on application | NO | YES | YES | YES |
| Create proposal | NO | NO | YES | YES |
| View proposals | NO | YES | YES | YES |
| Vote on proposal | NO | YES | YES | YES |
| Seed initial board | NO | NO | NO | YES |

### 2.12 Moderation & Admin Permissions

| Action | USER | MODERATOR | ADMIN | SUPER_ADMIN |
|--------|------|-----------|-------|-------------|
| File report | YES | YES | YES | YES |
| File appeal | YES | YES | YES | YES |
| File grievance | YES | YES | YES | YES |
| View moderation queue | NO | YES | YES | YES |
| Take moderation action | NO | YES | YES | YES |
| Decide on appeal | NO | YES | YES | YES |
| Decide on college claim | NO | YES | YES | YES |
| View admin stats | NO | NO | YES | YES |
| Seed colleges | NO | NO | YES | YES |
| Override distribution | NO | YES | YES | YES |
| Kill-switch distribution | NO | NO | YES | YES |
| Remove distribution override | NO | NO | YES | YES |

---

## 3. Child User Restrictions (ageStatus = CHILD)

Children (`birthYear` indicates under 18) have these automatic restrictions:

| Restriction | Effect |
|------------|--------|
| Cannot upload media | 403 on media upload |
| Cannot create reels | 403 on reel create |
| Cannot create stories | 403 on story create |
| Cannot create media posts | Only text-only posts allowed |
| `personalizedFeed = false` | No personalized algorithm |
| `targetedAds = false` | No targeted advertising |

---

## 4. Block Interaction Rules

When User A blocks User B:

| Interaction | Effect |
|------------|--------|
| B sees A's posts | NO (filtered from all feeds) |
| A sees B's posts | NO (filtered from all feeds) |
| B sees A's stories | NO |
| B can follow A | NO (auto-unfollowed) |
| B can RSVP to A's events | NO |
| B sees A's reels | NO (filtered from feeds) |
| B can comment on A's content | NO |
| A sees B in search | NO |

---

## 5. Android CTA Rules

Based on the permission matrix, here's what Android should show:

### For ANONYMOUS users
- Show: Login/Register CTA on all interactive elements
- Hide: All creation buttons, interaction buttons

### For CHILD_USER
- Show: Text post creation, like, comment, follow, RSVP
- Hide: Media upload, reel create, story create, resource create
- Disable: Any media-related creation flow

### For USER
- Show: Full creation suite, all interactions
- Hide: Admin/moderation panels
- Conditional: Board actions only if user is board member

### For MODERATOR
- Show: Everything USER sees + moderation queue link
- Hide: Admin-only actions (kill-switch, counter recompute, etc.)

### For ADMIN
- Show: Everything + admin panel
- Show: Contest management, season management, tribe management

---

## PASS Gate Verification

- [x] Every role has explicit capabilities across all feature domains
- [x] Child restrictions are comprehensive and documented
- [x] Block bidirectionality documented
- [x] Board member special permissions documented
- [x] Judge special permissions documented
- [x] Contest entry requires tribe membership — documented
- [x] Android CTA rules provided per role
- [x] No unauthorized CTA will be shown to wrong role

**B0-S5 STATUS: FROZEN**
