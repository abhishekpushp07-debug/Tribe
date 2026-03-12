# Tribe — Security & Authentication Deep Dive

> Complete security architecture, token management, and threat mitigation.

---

## 1. Token Architecture

### Access + Refresh Token Split
```
Access Token (at_...)
├── Format: UUID v4 with "at_" prefix
├── TTL: 15 minutes
├── Storage: Client memory only (NEVER persist)
├── Used: Every API call via Authorization header
├── On expiry: 401 ACCESS_TOKEN_EXPIRED
└── Recovery: POST /auth/refresh

Refresh Token (rt_...)
├── Format: UUID v4 with "rt_" prefix  
├── TTL: 30 days
├── Storage: EncryptedSharedPreferences (Android) / Keychain (iOS)
├── Used: POST /auth/refresh ONLY
├── Rotation: Each use issues new pair, invalidates old
├── Family: Grouped for reuse detection
└── Reuse: ALL family sessions revoked (REFRESH_TOKEN_REUSED)
```

### Token Rotation Chain
```
Login → at_v0 + rt_v0 (family_A)
         │
         ▼ (rt_v0 used for refresh)
Refresh → at_v1 + rt_v1 (family_A, version 2)
         │      rt_v0 marked as "used"
         │
         ▼ (rt_v1 used for refresh)  
Refresh → at_v2 + rt_v2 (family_A, version 3)
         │      rt_v1 marked as "used"
         │
         ✗ (attacker tries rt_v0 which is marked "used")
         → REFRESH_TOKEN_REUSED
         → ALL sessions in family_A REVOKED
         → User must re-authenticate
```

---

## 2. PIN Security

### Hashing
```
Algorithm: PBKDF2
Iterations: 100,000
Digest: SHA-512
Salt: 64 random bytes (per-user, stored)
Output: 64-byte hash
```

### Brute Force Protection
| Attempt | Action |
|---------|--------|
| 1-5 | Normal (allow login) |
| 6+ | 429 Rate Limited, cooldown 300 seconds |
| Per IP | Max 5 failed per 15 minutes |
| Per phone | Max 10 failed per hour |

---

## 3. Session Management

### Limits
| Config | Value |
|--------|-------|
| Max concurrent sessions | 10 per user |
| Access token TTL | 15 minutes |
| Refresh token TTL | 30 days |
| Session TTL | 30 days |

### Session Eviction
When 11th session is created:
1. Find oldest session (by lastAccessedAt)
2. Revoke it automatically
3. Create new session

### Session Fields Stored
```json
{
  "id": "session-uuid",
  "userId": "user-uuid",
  "token": "at_...",
  "refreshToken": "rt_...",
  "refreshTokenFamily": "family-uuid",
  "refreshTokenVersion": 1,
  "refreshTokenUsed": false,
  "ipAddress": "192.168.1.1",
  "deviceInfo": "Mozilla/5.0...",
  "lastAccessedAt": "2025-01-15T10:00:00Z",
  "expiresAt": "2025-02-14T10:00:00Z",
  "createdAt": "2025-01-15T10:00:00Z"
}
```

---

## 4. PIN Change Security

When user changes PIN:
1. Re-authenticate with current PIN (prevents stolen-token abuse)
2. Hash new PIN with fresh salt
3. **Revoke ALL other sessions** (force logout everywhere)
4. Issue fresh tokens for current session
5. Return new accessToken + refreshToken

---

## 5. Content Moderation Security

### Auto-Moderation
- Text content checked for profanity/hate speech on creation
- Score 0.0-1.0: >0.85 auto-reject, >0.50 hold for review
- Images checked for nudity/violence

### Report-Based Auto-Hold
- 3+ unique reports → content auto-held for review
- 3+ reports on comments → comment hidden
- Deduplicated by userId (can't report same content twice)

---

## 6. Rate Limiting

### Per-Endpoint Limits
| Endpoint Category | Per Minute | Per Hour |
|-------------------|-----------|----------|
| Auth (login/register) | 5 | 30 |
| Content creation | 10 | 60 |
| Likes | 30 | 200 |
| Comments | 15 | 80 |
| Shares | 10 | 50 |
| Search | 30 | 300 |
| Story creation | 30 | 200 |

### Rate Limit Response
```
HTTP 429 Too Many Requests
Retry-After: 30

{
  "error": "Rate limit exceeded. Try again in 30 seconds",
  "code": "RATE_LIMITED"
}
```

---

## 7. Block System Security

When User A blocks User B:
- A cannot see B: profile, posts, comments, stories, reels
- B cannot see A: profile, posts, comments, stories, reels
- Follow relationships removed both directions
- B's comments on A's posts: hidden (not deleted for audit)
- Search: B filtered from A's results and vice versa
- Stories: B cannot view A's stories and vice versa

### Block Check Pattern
```javascript
async function isBlocked(db, userId1, userId2) {
  const block = await db.collection('blocks').findOne({
    $or: [
      { blockerId: userId1, blockedId: userId2 },
      { blockerId: userId2, blockedId: userId1 }
    ]
  })
  return !!block
}
```

---

## 8. Data Privacy

### User Sanitization
Sensitive fields ALWAYS removed before response:
- `_id` (MongoDB internal)
- `pinHash` (hashed PIN)
- `pinSalt` (salt)
- `refreshToken` (in session responses)

### Private Account Rules
- Profile info (name, bio, avatar) still visible
- Post count visible, but posts NOT accessible
- Follow requires approval (follow_request)
- Stories only visible to approved followers

### Account Deactivation
- Sets `isDeactivated: true`
- Revokes ALL sessions
- Profile hidden from search
- Content hidden from feeds
- Can reactivate by logging in

---

## 9. Threat Mitigation Matrix

| Threat | Mitigation |
|--------|------------|
| Token theft | 15-min access token, refresh rotation, family reuse detection |
| Brute force | Rate limiting, exponential backoff, per-IP cooldown |
| Replay attack | Refresh token version tracking, one-time use |
| Session hijack | IP logging, device fingerprinting, manual session revocation |
| Content spam | AI moderation, rate limits, anti-abuse velocity detection |
| Vote manipulation | Same-target burst detection, per-user vote caps |
| Fake accounts | Phone-based registration, age verification |
| Data scraping | Rate limiting on search/feeds, cursor-based pagination |

---

*Security Architecture v3.0.0*
