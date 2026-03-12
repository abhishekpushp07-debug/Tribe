# 19 — Onboarding Flow

**Source**: `/app/lib/handlers/auth.js`, `/app/lib/handlers/onboarding.js`

---

## 1. Overview

Four-step onboarding flow after registration: Age verification → College selection → Consent → Done. Each step gates specific features.

---

## 2. Onboarding Steps

```
REGISTER → AGE → COLLEGE → CONSENT → DONE
```

| Step | Endpoint | What Happens |
|------|----------|-------------|
| Register | `POST /api/auth/register` | Account created, `onboardingStep: AGE` |
| Age | `PATCH /api/me/age` | Sets `birthYear`, `ageStatus` (CHILD/ADULT), moves to COLLEGE |
| College | `PATCH /api/me/college` | Links college, moves to CONSENT |
| Consent | `POST /api/legal/accept` | Accepts legal terms |
| Done | `PATCH /api/me/onboarding` | Sets `onboardingComplete: true`, step: DONE |

---

## 3. Registration

`POST /api/auth/register`

```json
{
  "phone": "9876543210",
  "pin": "1234",
  "displayName": "Priya Sharma"
}
```

**Validation**:
- Phone: exactly 10 digits
- PIN: exactly 4 digits
- displayName: 2–50 characters

**Response**:
```json
{
  "accessToken": "...",
  "refreshToken": "...",
  "expiresIn": 900,
  "token": "...",
  "user": {
    "id": "uuid",
    "phone": "9876543210",
    "displayName": "Priya Sharma",
    "ageStatus": "UNKNOWN",
    "onboardingComplete": false,
    "onboardingStep": "AGE",
    "tribeCode": "SHAURYA",
    "tribeName": "Shaurya"
  }
}
```

**Side effects**:
- Auto-assigned to one of 21 tribes
- Tribe membership recorded
- Session created with access + refresh tokens
- Security audit logged

---

## 4. Age Verification

`PATCH /api/me/age`

```json
{
  "birthYear": 2004
}
```

**Rules**:
- `birthYear` must be between 1940 and current year
- Age < 18 → `ageStatus: CHILD`
- Age >= 18 → `ageStatus: ADULT`
- Cannot change from CHILD to ADULT without admin review

**DPDP Compliance (Children)**:
When ageStatus is CHILD:
- `personalizedFeed: false`
- `targetedAds: false`
- Cannot upload media
- Cannot create Reels or Stories
- Text-only posts allowed

---

## 5. College Selection

`PATCH /api/me/college`

```json
{
  "collegeId": "college-uuid"
}
```

**Flow**:
1. User searches colleges via `GET /api/colleges/search?q=IIT`
2. Selects college from results
3. Links via `PATCH /api/me/college`

Passing `collegeId: null` unlinks the college.

---

## 6. Consent

`POST /api/legal/accept`

```json
{
  "version": "1.0",
  "acceptedTerms": true
}
```

`GET /api/legal/consent` returns current consent status and required version.

---

## 7. Completing Onboarding

`PATCH /api/me/onboarding`

Sets:
```json
{
  "onboardingComplete": true,
  "onboardingStep": "DONE"
}
```

---

## 8. Profile Setup (Optional, Any Time)

`PATCH /api/me/profile`

```json
{
  "displayName": "Priya S.",
  "username": "priya.sharma",
  "bio": "Photography enthusiast",
  "avatarMediaId": "media-uuid"
}
```

**Username rules**:
- 3–30 characters
- Lowercase letters, numbers, dots, underscores only
- Must be unique

---

## 9. Feature Gating by Onboarding State

| Feature | Requires |
|---------|----------|
| Post text | `ageStatus != UNKNOWN` |
| Post media | `ageStatus == ADULT` |
| Create Stories | `ageStatus == ADULT` |
| Create Reels | `ageStatus == ADULT` |
| Create Events | `ageStatus == ADULT` |
| Follow users | Login only |
| View feed | Login only |

---

## 10. Android Implementation

### Onboarding Flow
```kotlin
// Step 1: Register
val auth = api.post("/api/auth/register", registerBody)
saveTokens(auth.accessToken, auth.refreshToken)

// Step 2: Age
api.patch("/api/me/age", mapOf("birthYear" to 2002))

// Step 3: College
val colleges = api.get("/api/colleges/search?q=IIT")
api.patch("/api/me/college", mapOf("collegeId" to selectedCollege.id))

// Step 4: Consent
api.post("/api/legal/accept", mapOf("version" to "1.0", "acceptedTerms" to true))

// Step 5: Complete
api.patch("/api/me/onboarding")
```

### Check Onboarding State
```kotlin
val me = api.get("/api/auth/me")
if (!me.user.onboardingComplete) {
    navigateToOnboarding(me.user.onboardingStep) // AGE, COLLEGE, CONSENT
}
```
