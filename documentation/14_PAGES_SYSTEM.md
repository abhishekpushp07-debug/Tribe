# 14 — Pages System

**Source**: `/app/lib/handlers/pages.js`, `/app/lib/page-permissions.js`, `/app/lib/page-slugs.js`, `/app/lib/entity-snippets.js`

---

## 1. Overview

Pages are organization/brand profiles that can publish content independently. They support RBAC roles, follow mechanics, verification, and analytics — similar to Facebook Pages or Instagram Professional Accounts.

---

## 2. Page Schema (Collection: `pages`)

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Page ID |
| `slug` | string | URL-friendly unique slug |
| `name` | string | Display name |
| `description` | string | Page bio |
| `category` | enum | `COLLEGE_CLUB`, `SPORTS_TEAM`, `MEDIA`, `BUSINESS`, `COMMUNITY`, `STUDENT_ORG`, `ACADEMIC`, `OTHER` |
| `status` | enum | `DRAFT`, `ACTIVE`, `ARCHIVED`, `REMOVED` |
| `createdByUserId` | string | Creator's user ID |
| `collegeId` | string? | Linked college |
| `tribeId` | string? | Linked tribe |
| `avatarMediaId` | string? | Page avatar |
| `coverMediaId` | string? | Cover image |
| `followerCount` | number | Total followers |
| `postCount` | number | Published posts |
| `isOfficial` | boolean | Official verification |
| `isVerified` | boolean | Verified status |
| `verificationStatus` | enum | `NONE`, `PENDING`, `APPROVED`, `REJECTED` |
| `linkedEntityType` | enum? | `COLLEGE`, `TRIBE`, `HOUSE` |
| `linkedEntityId` | string? | Entity ID |
| `contactEmail` | string? | Contact email |
| `contactPhone` | string? | Contact phone |
| `website` | string? | Website URL |

---

## 3. RBAC Roles

Defined in `/app/lib/page-permissions.js`:

| Role | Create Post | Edit Page | Manage Members | Transfer Owner | Delete Page |
|------|------------|-----------|----------------|----------------|-------------|
| `OWNER` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `ADMIN` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `EDITOR` | ✅ | ❌ | ❌ | ❌ | ❌ |
| `MODERATOR` | ❌ | ❌ | ❌ | ❌ | ❌ |

### Page Members (Collection: `page_members`)

| Field | Type | Description |
|-------|------|-------------|
| `pageId` | string | Page ID |
| `userId` | string | Member user ID |
| `role` | enum | `OWNER`, `ADMIN`, `EDITOR`, `MODERATOR` |
| `status` | enum | `ACTIVE`, `REMOVED`, `INVITED` |
| `invitedBy` | string? | Who invited |

---

## 4. API Endpoints

### CRUD
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/pages` | Create page |
| `GET` | `/api/pages` | List/search pages |
| `GET` | `/api/pages/:idOrSlug` | Page detail |
| `PATCH` | `/api/pages/:id` | Update page |
| `DELETE` | `/api/pages/:id` | Delete page |
| `POST` | `/api/pages/:id/archive` | Archive page |
| `POST` | `/api/pages/:id/restore` | Restore archived |

### Members
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/pages/:id/members` | List members |
| `POST` | `/api/pages/:id/members` | Add member |
| `PATCH` | `/api/pages/:id/members/:userId` | Change role |
| `DELETE` | `/api/pages/:id/members/:userId` | Remove member |
| `POST` | `/api/pages/:id/transfer-ownership` | Transfer ownership |
| `POST` | `/api/pages/:id/invite` | Invite user |

### Follow
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/pages/:id/follow` | Follow page |
| `DELETE` | `/api/pages/:id/follow` | Unfollow page |
| `GET` | `/api/pages/:id/followers` | Follower list |

### Content
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/pages/:id/posts` | Page posts |
| `POST` | `/api/pages/:id/posts` | Create post as page |
| `PATCH` | `/api/pages/:id/posts/:postId` | Edit page post |
| `DELETE` | `/api/pages/:id/posts/:postId` | Delete page post |

### Verification
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/pages/:id/request-verification` | Request verification |
| `GET` | `/api/admin/pages/verification-requests` | Admin: queue |
| `POST` | `/api/admin/pages/verification-decide` | Admin: approve/reject |

### Other
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/pages/:id/report` | Report page |
| `GET` | `/api/pages/:id/analytics` | Analytics dashboard |
| `GET` | `/api/me/pages` | My managed pages |

---

## 5. Creating a Page

```json
POST /api/pages
{
  "name": "Photography Club IIT Delhi",
  "slug": "photo-club-iitd",
  "category": "COLLEGE_CLUB",
  "description": "Official photography club",
  "collegeId": "college-uuid",
  "linkedEntityType": "COLLEGE",
  "linkedEntityId": "college-uuid"
}
```

**Slug rules** (`/app/lib/page-slugs.js`):
- 3–60 characters
- Lowercase alphanumeric + hyphens
- No consecutive hyphens
- Cannot start/end with hyphen
- Anti-spoof check against official names

---

## 6. Publishing as Page

When creating content via `POST /api/pages/:id/posts`, the content item is stored with:
```json
{
  "authorType": "PAGE",
  "pageId": "page-uuid",
  "createdAs": "PAGE"
}
```

This means the post appears in feeds as authored by the page, not the individual user.

### Feed Integration
- Page posts appear in `/api/feed/following` for page followers
- Social interactions (likes, comments, shares) notify page OWNER + ADMIN members

---

## 7. Page Analytics

`GET /api/pages/:id/analytics` returns:
```json
{
  "page": { ... },
  "followers": { "total": 1200, "gained7d": 45, "lost7d": 3 },
  "posts": { "total": 89, "published7d": 5 },
  "engagement": { "likes7d": 340, "comments7d": 78, "shares7d": 12 },
  "topPosts": [ ... ]
}
```

---

## 8. Verification Flow

1. Page owner calls `POST /api/pages/:id/request-verification`
2. Admin reviews at `GET /api/admin/pages/verification-requests`
3. Admin decides via `POST /api/admin/pages/verification-decide`
4. Status updates: `NONE` → `PENDING` → `APPROVED`/`REJECTED`

**Official pages** (college/tribe linked) get special treatment:
- Unique constraint: one official page per entity
- `isOfficial: true` flag

---

## 9. Android Integration

### Page Profile Screen
```kotlin
val page = api.get("/api/pages/$slugOrId")
// Display: name, description, category, followerCount, isVerified, isOfficial
```

### Follow/Unfollow
```kotlin
api.post("/api/pages/$id/follow")
api.delete("/api/pages/$id/follow")
```

### Create Post as Page
```kotlin
api.post("/api/pages/$id/posts", postBody)
// postBody: { caption, mediaIds, kind }
```
