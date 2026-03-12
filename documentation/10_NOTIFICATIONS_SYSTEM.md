# 10 — Notifications System

## Overview

The notifications system delivers **16 notification types** with push device token management, user preferences, grouped views, and blocked-actor filtering. It supports the full notification lifecycle: creation, delivery, read tracking, grouping, and cleanup.

**Source**: `lib/handlers/notifications.js` (358 lines) + `lib/services/notification-service.js` (233 lines)

---

## Notification Types

| Type | Trigger | Example Message |
|------|---------|------------------|
| `FOLLOW` | User follows you | "Alex started following you" |
| `LIKE` | Content liked | "Alex liked your post" |
| `COMMENT` | New comment | "Alex commented on your post" |
| `COMMENT_LIKE` | Comment liked | "Alex liked your comment" |
| `SHARE` | Content shared/reposted | "Alex shared your post" |
| `REEL_LIKE` | Reel liked | "Alex liked your reel" |
| `REEL_COMMENT` | Reel commented | "Alex commented on your reel" |
| `REEL_SHARE` | Reel shared | "Alex shared your reel" |
| `STORY_REACTION` | Story reacted to | "Alex reacted to your story" |
| `STORY_REPLY` | Story replied to | "Alex replied to your story" |
| `EVENT_REMINDER` | Event starting soon | "Music Fest starts in 1 hour" |
| `PAGE_INVITE` | Added to a page | "You've been added to Photo Club" |
| `PAGE_VERIFICATION_RESULT` | Verification decided | "Your page has been verified!" |
| `CONTEST_ENTRY` | Contest entry update | "Your entry was accepted" |
| `BOARD_APPLICATION` | Board seat decision | "Your board application was approved" |
| `SYSTEM` | System announcement | "New feature available" |

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/notifications` | Required | List notifications |
| `PATCH` | `/api/notifications/read` | Required | Mark specific or all as read |
| `POST` | `/api/notifications/read-all` | Required | Mark all as read |
| `GET` | `/api/notifications/unread-count` | Required | Lightweight unread count |
| `DELETE` | `/api/notifications/clear` | Required | Delete all notifications |
| `POST` | `/api/notifications/register-device` | Required | Register push token |
| `DELETE` | `/api/notifications/unregister-device` | Required | Deactivate push token |
| `GET` | `/api/notifications/preferences` | Required | Get notification preferences |
| `PATCH` | `/api/notifications/preferences` | Required | Update preferences |

---

## Notification Data Model

```javascript
{
  id: UUID,
  userId: String,          // Recipient
  type: String,            // One of 16 types above
  actorId: String,         // User who triggered the notification
  targetType: String,      // 'CONTENT' | 'REEL' | 'STORY' | 'USER' | 'PAGE'
  targetId: String,        // ID of the target entity
  message: String,         // Human-readable message
  read: Boolean,           // Read status
  dedupKey: String,        // Deduplication key (internal)
  createdAt: Date
}
```

---

## List Notifications

`GET /api/notifications?cursor=&limit=20&grouped=true`

**Features**:
1. **Cursor pagination**: Uses `createdAt` for chronological traversal
2. **Block filtering**: Notifications from blocked users are silently removed
3. **Actor enrichment**: Each notification includes the actor's profile (or null if deleted)
4. **Target existence check**: A `targetExists` boolean signals if the referenced content still exists (for UI degradation)
5. **Grouped view**: When `grouped=true`, similar notifications are merged (e.g., "Alex and 3 others liked your post")

**Response**:
```json
{
  "items": [
    {
      "id": "notif-uuid",
      "type": "LIKE",
      "actor": { "id": "...", "displayName": "Alex" },
      "targetType": "CONTENT",
      "targetId": "post-uuid",
      "targetExists": true,
      "message": "Alex liked your post",
      "read": false,
      "createdAt": "2026-03-15T..."
    }
  ],
  "unreadCount": 5,
  "pagination": {
    "nextCursor": "2026-03-14T...",
    "hasMore": true
  }
}
```

---

## Mark Read

`PATCH /api/notifications/read`

```json
// Mark specific notifications
{ "ids": ["notif-1", "notif-2"] }

// Mark all as read
{}
```

Returns updated `unreadCount`.

---

## Push Device Tokens

### Register Device

`POST /api/notifications/register-device`

```json
{
  "token": "firebase-token-string",
  "platform": "ANDROID",     // IOS | ANDROID | WEB
  "deviceId": "device-uuid",
  "appVersion": "2.1.0"
}
```

**Behavior**:
- Upserts by `userId + token` (same user re-registering = update)
- Deactivates the same token registered to OTHER users (device ownership transfer)
- Returns 201 for new registration, 200 for update

### Unregister Device

`DELETE /api/notifications/unregister-device`

```json
{ "token": "firebase-token-string" }
```

Soft-deactivates the token (`isActive: false`).

---

## Notification Preferences

### Get Preferences

`GET /api/notifications/preferences`

Returns the user's preferences merged with defaults. Default preferences are defined in `notification-service.js`.

### Update Preferences

`PATCH /api/notifications/preferences`

```json
{
  "preferences": {
    "likes": false,
    "comments": true,
    "follows": true,
    "reelInteractions": false
  }
}
```

- Only known preference keys are accepted (validated against `DEFAULT_PREFERENCES`)
- All values must be boolean
- Unknown keys return 400 error

---

## Notification Grouping

When `grouped=true`, the `groupNotifications()` function from `notification-service.js` merges notifications by:
- Same `type` + same `targetId` within a time window
- Groups show the most recent actor and a count: "Alex and 3 others liked your post"

---

## Target Existence Check

The `batchCheckTargets()` function performs bulk existence checks:

```javascript
const TARGET_COLLECTIONS = {
  CONTENT: 'content_items',
  REEL: 'reels',
  STORY: 'stories',
  USER: 'users',
  PAGE: 'pages'
}
```

This allows clients to show "This content is no longer available" instead of broken links.

---

## Notification Creation (Internal)

Notifications are created via `createNotification()` from `auth-utils.js`:

```javascript
await createNotification(
  db,
  recipientId,         // Who gets the notification
  NotificationType.LIKE,
  actorId,             // Who triggered it
  'CONTENT',           // Target type
  contentId,           // Target ID
  'Alex liked your post'
)
```

This is called from social handlers, reel handlers, story handlers, page handlers, and event handlers.

---

## Supporting Collections

| Collection | Purpose |
|------------|--------|
| `notifications` | All notification records |
| `device_tokens` | Push device registration |
| `notification_preferences` | Per-user preference overrides |

---

## Observability

All notification operations are logged via the structured logger:

```javascript
logger.debug('NOTIFICATION', 'list', { userId, count, grouped, unreadCount })
logger.info('NOTIFICATION', 'mark_read', { userId, mode, modifiedCount, unreadCount })
logger.info('NOTIFICATION', 'device_registered', { userId, platform, isNew })
logger.info('NOTIFICATION', 'preferences_updated', { userId, changed: ['likes', 'follows'] })
```

---

## Android Integration

### Register FCM Token

```kotlin
// In Application.onCreate or after login
FirebaseMessaging.getInstance().token.addOnSuccessListener { token ->
    api.post("/api/notifications/register-device", DeviceRegistration(
        token = token,
        platform = "ANDROID",
        deviceId = Settings.Secure.getString(contentResolver, Settings.Secure.ANDROID_ID),
        appVersion = BuildConfig.VERSION_NAME
    ))
}
```

### Poll Unread Count

```kotlin
// Lightweight endpoint for badge count
val count = api.get("/api/notifications/unread-count").unreadCount
badgeView.text = if (count > 99) "99+" else count.toString()
```
