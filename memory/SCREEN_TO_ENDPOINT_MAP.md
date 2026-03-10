# Tribe — Screen-to-Endpoint Map
**Version**: 2.1 (Post B4 + FH1-U)
**Every screen mapped to exact backend endpoints**

---

## 1. Splash / Auth Check
| Action | Endpoint | Response |
|--------|----------|----------|
| Check if logged in | `GET /auth/me` | 200 → logged in, 401 → not |
| **Flow**: On app launch, call `/auth/me`. If 200, go to home. If 401, go to login. |

## 2. Login Screen
| Action | Endpoint | Body | Response |
|--------|----------|------|----------|
| Login | `POST /auth/login` | `{ phone, pin }` | `{ accessToken, refreshToken, user }` |
| **Error**: Wrong pin → 401. Phone not found → 404. |

## 3. Register Screen
| Action | Endpoint | Body | Response |
|--------|----------|------|----------|
| Register | `POST /auth/register` | `{ phone, pin, displayName, username }` | `{ accessToken, refreshToken, user }` |
| **Error**: Phone exists → 409. Username taken → 409. Phone not 10 digits → 400. |

## 4. Onboarding Flow
| Step | Endpoint | Body |
|------|----------|------|
| Check step | Read `user.onboardingStep` | — |
| Set age | `PATCH /me/age` | `{ birthDate: "2000-01-15" }` |
| Set college | `PATCH /me/college` | `{ collegeId: "uuid" }` |
| Find colleges | `GET /colleges/search?q=IIT` | — |
| Complete | `PATCH /me/onboarding` | `{ step: "COMPLETE" }` |

## 5. Edit Profile Screen
| Action | Endpoint | Body |
|--------|----------|------|
| Update name/bio | `PATCH /me/profile` | `{ displayName, bio }` |
| Upload avatar | `POST /media/upload` → then `PATCH /me/profile` | `{ avatarMediaId: "id" }` |
| Change PIN | `PATCH /auth/pin` | `{ currentPin, newPin }` |

## 6. Home Feed Screen
| Action | Endpoint | Notes |
|--------|----------|-------|
| Public feed | `GET /feed/public?cursor=...&limit=20` | Mixed user + page posts |
| Following feed | `GET /feed/following?cursor=...&limit=20` | Includes followed page posts (B3) |
| Story rail | `GET /stories/feed` or `GET /feed/stories` | Story circles at top |
| Like post | `POST /content/:id/like` | Optimistic OK |
| Save post | `POST /content/:id/save` | Optimistic OK |
| **NEW (B4)** Share post | `POST /content/:id/share` | NOT optimistic — wait for 201 |

**Feed items can be**: normal post, page post, repost (B4), edited post (B4)

## 7. Post Detail Screen
| Action | Endpoint | Notes |
|--------|----------|-------|
| Fetch detail | `GET /content/:id` | Returns enriched PostObject |
| Like | `POST /content/:id/like` | Optimistic OK |
| Unlike | `DELETE /content/:id/reaction` | Optimistic OK |
| Save | `POST /content/:id/save` | Optimistic OK |
| **NEW (B4)** Edit | `PATCH /content/:id` body: `{ caption }` | NOT optimistic (moderation) |
| **NEW (B4)** Share | `POST /content/:id/share` | NOT optimistic |
| Delete (own) | `DELETE /content/:id` | Confirm first |
| **Show edit button**: Only if user is author OR page role OWNER/ADMIN/EDITOR |
| **Show "(edited)"**: If `post.editedAt !== null` |
| **Repost detail**: If `post.isRepost === true`, embed original content card |

## 8. Comment Sheet
| Action | Endpoint | Notes |
|--------|----------|-------|
| List comments | `GET /content/:postId/comments?cursor=...` | Cursor-paginated |
| Create comment | `POST /content/:postId/comments` body: `{ text }` | Returns comment |
| **NEW (B4)** Like comment | `POST /content/:postId/comments/:commentId/like` | Optimistic OK |
| **NEW (B4)** Unlike comment | `DELETE /content/:postId/comments/:commentId/like` | Optimistic OK |
| **Each comment shows**: text, author, likeCount, heart icon |

## 9. Create Post Screen
| Action | Endpoint | Notes |
|--------|----------|-------|
| Upload media | `POST /media/upload` (multipart) | Returns { id, url } |
| Create post | `POST /content/posts` body: `{ caption, kind, media, visibility }` | NOT optimistic |
| **Prerequisite**: `user.ageStatus === "ADULT"` |

## 10. NEW: Edit Post Screen (B4)
| Action | Endpoint | Notes |
|--------|----------|-------|
| Edit caption | `PATCH /content/:id` body: `{ caption }` | Returns updated PostObject |
| **Who can edit**: Post owner, OR page role OWNER/ADMIN/EDITOR for page posts |
| **What can't be edited**: Media, visibility, author fields |
| **Moderation**: Backend re-checks edited text. Can reject (422) |

## 11. NEW: Share/Repost Flow (B4)
| Action | Endpoint | Notes |
|--------|----------|-------|
| Share/Repost | `POST /content/:id/share` optionally: `{ caption }` | Returns 201 with repost |
| **Duplicate**: Returns 409 — disable share button |
| **Cannot repost repost**: Returns 400 |
| **Cannot repost deleted**: Returns 404 |

## 12. Notifications Screen
| Action | Endpoint | Notes |
|--------|----------|-------|
| List | `GET /notifications?cursor=...` | Returns notification objects |
| Mark read | `PATCH /notifications/read` | — |
| **NEW types (B4)**: `COMMENT_LIKE` → comment sheet, `SHARE` → original post |
| **Deep-link by targetType**: CONTENT→post detail, USER→profile, COMMENT→comment sheet, PAGE→page detail |

## 13. Search Screen
| Action | Endpoint | Notes |
|--------|----------|-------|
| Search users | `GET /search?q=...&type=users` | Returns user snippets |
| Search colleges | `GET /search?q=...&type=colleges` | Returns college snippets |
| Search houses | `GET /search?q=...&type=houses` | Returns house snippets |
| **NEW (B3)** Search pages | `GET /search?q=...&type=pages` | Returns page snippets |
| Page-specific search | `GET /pages?q=...&category=...` | With category filter |
| User suggestions | `GET /suggestions/users` | For recommendation rail |
| **NOT working**: `type=posts` (deferred to B5) |

## 14. Profile Screen
| Action | Endpoint | Notes |
|--------|----------|-------|
| Self profile | `GET /auth/me` | Full profile |
| Other profile | `GET /users/:id` | Other user's profile |
| User posts | `GET /users/:id/posts?cursor=...` | Their posts |
| Followers | `GET /users/:id/followers` | Follower list |
| Following | `GET /users/:id/following` | Following list |
| Saved posts | `GET /users/:id/saved` | Self only |
| Follow | `POST /follow/:userId` | Optimistic OK |
| Unfollow | `DELETE /follow/:userId` | Optimistic OK |

## 15. Stories Rail / Viewer
| Action | Endpoint |
|--------|----------|
| Story rail | `GET /stories/feed` |
| View story | `GET /stories/:id` |
| Create story | `POST /stories` |
| React | `POST /stories/:id/react` |
| Reply | `POST /stories/:id/reply` |
| Delete | `DELETE /stories/:id` |
| Archive | `GET /me/stories/archive` |
| Highlights | `POST /me/highlights`, `GET /users/:id/highlights` |
| Settings | `GET/PATCH /me/story-settings` |
| Close friends | `GET /me/close-friends`, `POST/DELETE /me/close-friends/:userId` |

## 16. Reels Feed / Detail
| Action | Endpoint |
|--------|----------|
| Feed | `GET /reels/feed?cursor=...` |
| Following | `GET /reels/following` |
| Detail | `GET /reels/:id` |
| Like/Unlike | `POST/DELETE /reels/:id/like` |
| Save/Unsave | `POST/DELETE /reels/:id/save` |
| Comment | `POST /reels/:id/comment` |
| Comments list | `GET /reels/:id/comments` |
| Share | `POST /reels/:id/share` |
| Report | `POST /reels/:id/report` |
| Watch | `POST /reels/:id/watch` |
| Analytics | `GET /me/reels/analytics` |
| User's reels | `GET /users/:id/reels` |

## 17. NEW: Page List / Search (B3)
| Action | Endpoint |
|--------|----------|
| Browse pages | `GET /pages?q=...&category=...` |
| My pages | `GET /me/pages` |

## 18. NEW: Page Detail (B3)
| Action | Endpoint | Notes |
|--------|----------|-------|
| Detail | `GET /pages/:idOrSlug` | Returns PageProfile with viewerRole |
| Posts | `GET /pages/:id/posts?cursor=...` | Page's posts |
| Follow | `POST /pages/:id/follow` | Optimistic OK |
| Unfollow | `DELETE /pages/:id/follow` | Optimistic OK |
| Analytics | `GET /pages/:id/analytics` | OWNER/ADMIN only |
| **Use `viewerRole`** to show/hide admin buttons |

## 19. NEW: Page Create / Edit (B3)
| Action | Endpoint | Body |
|--------|----------|------|
| Create | `POST /pages` | `{ name, slug, category, bio?, avatarMediaId? }` |
| Update | `PATCH /pages/:id` | `{ name?, bio?, avatarMediaId? }` |
| Archive | `POST /pages/:id/archive` | — |
| Restore | `POST /pages/:id/restore` | — |

## 20. NEW: Page Member Management (B3)
| Action | Endpoint | Body | Who Can |
|--------|----------|------|---------|
| List members | `GET /pages/:id/members` | — | Any member |
| Add member | `POST /pages/:id/members` | `{ userId, role }` | OWNER/ADMIN |
| Change role | `PATCH /pages/:id/members/:userId` | `{ role }` | OWNER/ADMIN |
| Remove member | `DELETE /pages/:id/members/:userId` | — | OWNER/ADMIN |
| Transfer ownership | `POST /pages/:id/transfer-ownership` | `{ userId }` | OWNER only |

## 21. NEW: Page Posts Flow (B3)
| Action | Endpoint | Who Can |
|--------|----------|---------|
| List page posts | `GET /pages/:id/posts` | Anyone |
| Publish as page | `POST /pages/:id/posts` body: `{ caption }` | OWNER/ADMIN/EDITOR |
| Edit page post | `PATCH /pages/:id/posts/:postId` body: `{ caption }` | OWNER/ADMIN/EDITOR |
| Delete page post | `DELETE /pages/:id/posts/:postId` | OWNER/ADMIN/EDITOR |
| **Also editable via**: `PATCH /content/:postId` (checks page role) |

## 22. Tribe Detail / Standings
| Action | Endpoint |
|--------|----------|
| List tribes | `GET /tribes` |
| Detail | `GET /tribes/:id` |
| Standings | `GET /tribes/standings/current` |
| Members | `GET /tribes/:id/members` |
| My tribe | `GET /me/tribe` |

## 23. Contest List / Detail / Leaderboard
| Action | Endpoint |
|--------|----------|
| List | `GET /tribe-contests` |
| Detail | `GET /tribe-contests/:id` |
| Enter | `POST /tribe-contests/:id/enter` |
| Leaderboard | `GET /tribe-contests/:id/leaderboard` |
| Vote | `POST /tribe-contests/:id/vote` |
| Seasons | `GET /tribe-contests/seasons` |

## 24. Events
| Action | Endpoint |
|--------|----------|
| Feed | `GET /events/feed` |
| Detail | `GET /events/:id` |
| Create | `POST /events` |
| RSVP | `POST /events/:id/rsvp` |
| Cancel RSVP | `DELETE /events/:id/rsvp` |
| My events | `GET /me/events` |
| My RSVPs | `GET /me/events/rsvps` |

## 25. Block Management
| Action | Endpoint |
|--------|----------|
| Block | `POST /me/blocks/:userId` |
| Unblock | `DELETE /me/blocks/:userId` |
| Blocked list | `GET /me/blocks` |

## 26. Board Notices
| Action | Endpoint |
|--------|----------|
| Create | `POST /board/notices` |
| Detail | `GET /board/notices/:id` |
| College notices | `GET /colleges/:id/notices` |
| My notices | `GET /me/board/notices` |
| Acknowledge | `POST /board/notices/:id/acknowledge` |

## 27. Resources
| Action | Endpoint |
|--------|----------|
| Create | `POST /resources` |
| Search | `GET /resources/search?q=...` |
| Detail | `GET /resources/:id` |
| Vote | `POST /resources/:id/vote` |
| My resources | `GET /me/resources` |

## 28. Governance
| Action | Endpoint |
|--------|----------|
| College board | `GET /governance/college/:id/board` |
| Apply for board | `POST /governance/college/:id/apply` |
| Create proposal | `POST /governance/college/:id/proposals` |
| Vote on proposal | `POST /governance/proposals/:id/vote` |
