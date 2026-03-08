# B0-S7 — Media & Upload Contract Freeze

**Status**: FROZEN  
**Freeze Date**: 2026-02-XX  
**Rule**: Every media upload behavior, size limit, processing state, and error code is locked.

---

## 1. Upload Endpoint

### `POST /api/media/upload`

**Auth**: Required. Children (ageStatus=CHILD) are blocked (403).

#### Request Body
```json
{
  "data": "base64_encoded_binary_data",
  "mimeType": "image/jpeg | image/png | image/webp | image/gif | video/mp4 | video/quicktime",
  "type": "IMAGE | VIDEO",
  "width": 1080,
  "height": 1920,
  "duration": 15
}
```

#### Response (201)
```json
{
  "id": "uuid",
  "url": "https://storage.example.com/path/to/file",
  "type": "IMAGE | VIDEO",
  "size": 245000,
  "mimeType": "image/jpeg",
  "storageType": "OBJECT_STORAGE | BASE64",
  "ownerId": "uuid",
  "createdAt": "ISO date"
}
```

### Key: `id` (mediaId)
This `id` is the canonical reference used everywhere:
- `user.avatarMediaId`
- `content_items.mediaIds[]`
- `stories.mediaIds[]`
- `reels.mediaId`
- `resources.fileAssetId`

---

## 2. Media Retrieval

### `GET /api/media/{mediaId}`

**Auth**: None (public, immutable)

#### Response
- Binary data with correct `Content-Type` header
- `Cache-Control: public, max-age=31536000, immutable` (1 year cache)
- Returns the raw image/video bytes

#### Error
- 404 if mediaId not found

---

## 3. Size & Type Limits

| Constraint | Value | Error Code |
|-----------|-------|-----------|
| Image max size | 5 MB | `FILE_TOO_LARGE` |
| Video max size | 30 MB | `FILE_TOO_LARGE` |
| Video max duration | 30 seconds | `DURATION_EXCEEDED` |
| Allowed image types | `image/jpeg`, `image/png`, `image/webp`, `image/gif` | `INVALID_MIME_TYPE` |
| Allowed video types | `video/mp4`, `video/quicktime` | `INVALID_MIME_TYPE` |
| Child upload | Blocked | `AGE_RESTRICTED` (403) |

---

## 4. Storage Strategy

### Primary: Emergent Object Storage
- Binary uploaded to S3-compatible object storage
- Returns permanent URL
- `storageType: "OBJECT_STORAGE"`

### Fallback: Base64 Storage
- If object storage unavailable, stores base64 in MongoDB
- Served via `/api/media/{id}` which decodes and returns binary
- `storageType: "BASE64"`

### Android Behavior
- Always use the `url` from upload response
- OR construct: `{BASE_URL}/api/media/{mediaId}`
- Both work — the URL from response is preferred

---

## 5. Media in Context

### Posts (content_items)
- `mediaIds: ["uuid1", "uuid2"]` — array of media asset IDs
- `media: [{ id, url, type, width, height }]` — enriched in responses
- Multiple images per post allowed

### Stories
- `mediaIds: ["uuid"]` — usually single media
- `type: "IMAGE" | "VIDEO" | "TEXT"` — TEXT stories have no media
- VIDEO stories: max 30 seconds
- IMAGE stories: any size within 5MB limit

### Reels
- `mediaId: "uuid"` — single video asset (required)
- Always VIDEO type
- Processing pipeline runs after upload (see Section 6)
- `thumbnailUrl` generated during processing (or null if not processed)

### Resources
- `fileAssetId: "uuid | null"` — optional, for attached documents
- May reference PDF/doc files (no strict video/image constraint here)

### User Avatar
- `avatarMediaId: "uuid | null"` on user object
- Should be an IMAGE type

---

## 6. Reel Processing Pipeline

When a reel is created with `isDraft: false`, or when a draft is published:

### Processing States (on reel)
| Field | State | Meaning |
|-------|-------|---------|
| `mediaStatus` | `PENDING` | Upload received, not processed |
| `mediaStatus` | `PROCESSING` | Transcoding in progress |
| `mediaStatus` | `READY` | Media ready for playback |
| `mediaStatus` | `FAILED` | Processing failed |

### Processing Endpoint
```
POST /api/reels/{reelId}/processing   (INTERNAL_ONLY)
```
Body: `{ mediaStatus: "READY | FAILED", thumbnailUrl: "url | null", processingDetails: {...} }`

### Status Check Endpoint
```
GET /api/reels/{reelId}/processing   (CANONICAL)
```
Response:
```json
{
  "reelId": "uuid",
  "mediaStatus": "PROCESSING | READY | FAILED",
  "thumbnailUrl": "string | null",
  "processingDetails": {},
  "updatedAt": "ISO date"
}
```

### Android Behavior
1. Upload media via `/api/media/upload`
2. Create reel via `POST /api/reels` with `mediaId`
3. If reel status is `PROCESSING`:
   - Show "Processing..." spinner
   - Poll `GET /api/reels/{id}/processing` every 3-5 seconds
   - When `mediaStatus: "READY"` → show reel
   - When `mediaStatus: "FAILED"` → show retry option
4. If reel comes back as `PUBLISHED` immediately → it was instant

---

## 7. Upload Flow for Android

### Image Post
```
1. User selects image(s)
2. For each image: POST /api/media/upload → get mediaId
3. POST /api/content/posts { mediaIds: [id1, id2], caption: "..." }
4. Done — post is immediately visible
```

### Story
```
1. User captures/selects media
2. POST /api/media/upload → get mediaId
3. POST /api/stories { type: "IMAGE|VIDEO", mediaIds: [id], stickers: [...], ... }
4. Done — story is live for 24h
```

### Reel
```
1. User records video (max 30s)
2. POST /api/media/upload → get mediaId
3. POST /api/reels { mediaId: id, caption: "...", isDraft: false }
4. Reel enters PROCESSING state
5. Poll GET /api/reels/{id}/processing until READY
6. Reel appears in feed
```

### Avatar
```
1. User selects photo
2. POST /api/media/upload → get mediaId
3. PATCH /api/me/profile { avatarMediaId: mediaId }
4. Done — avatar updated
```

### Resource Attachment
```
1. User selects file
2. POST /api/media/upload → get mediaId (fileAssetId)
3. POST /api/resources { ..., fileAssetId: mediaId }
4. Done
```

---

## 8. Error Codes (Media-Specific)

| HTTP Status | Error Code | Meaning |
|------------|-----------|---------|
| 400 | `VALIDATION_ERROR` | Missing data, mimeType, or type field |
| 400 | `INVALID_MIME_TYPE` | Unsupported file type |
| 403 | `AGE_RESTRICTED` | Child user attempting upload |
| 413 | `FILE_TOO_LARGE` | Exceeds size limit |
| 422 | `DURATION_EXCEEDED` | Video exceeds 30 seconds |
| 500 | `UPLOAD_FAILED` | Storage failure |

---

## 9. Thumbnail & Display Rules

| Content Type | Thumbnail | Display |
|-------------|----------|---------|
| Image post | Use original URL | Full image |
| Story image | Use original URL | Full-screen overlay |
| Story video | Use original URL | Full-screen video player |
| Reel | `thumbnailUrl` from processing, fallback to first frame | Vertical video player |
| Avatar | Use `GET /api/media/{avatarMediaId}` | Circle crop |

---

## PASS Gate Verification

- [x] Upload endpoint fully specified (request, response, errors)
- [x] Retrieval endpoint fully specified (headers, caching)
- [x] Size limits per type documented
- [x] MIME type whitelist documented
- [x] Storage strategy (primary + fallback) documented
- [x] mediaId usage across all entities documented
- [x] Reel processing pipeline and states documented
- [x] Complete upload flow per content type documented for Android
- [x] Error codes specific to media documented
- [x] Child restriction on upload documented
- [x] Thumbnail rules documented

**B0-S7 STATUS: FROZEN**
