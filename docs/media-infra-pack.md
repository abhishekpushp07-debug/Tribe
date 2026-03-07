# Tribe — Media Infrastructure Pack

## Architecture

```
Client → POST /api/media/upload (base64 body)
  → Auth check (RBAC: adults only)
  → Size validation (10MB images, 50MB videos)
  → Duration check (30s max for reels)
  → Object Storage upload (Emergent Integrations)
  → Store metadata in media_assets collection
  → Return { id, url, type, size, storageType }

Client → GET /api/media/:id
  → Fetch metadata from media_assets
  → Download from Object Storage
  → Stream binary with correct Content-Type
  → Cache-Control: public, max-age=31536000, immutable
```

## Object Storage Implementation

**Provider**: Emergent Object Storage (S3-compatible)
**Library**: `emergentintegrations` npm package
**File**: `/app/lib/storage.js`

### Upload Flow
1. Client sends base64-encoded data with mimeType
2. Server decodes, generates unique path: `tribe/uploads/{userId}/{timestamp}_{uuid}.{ext}`
3. Uploads to object storage via `emergentintegrations`
4. Stores storage path in `media_assets.storagePath`
5. Sets `storageType: 'OBJECT_STORAGE'`

### Download Flow
1. Client requests `GET /api/media/:id`
2. Server looks up `media_assets` by ID
3. Downloads from object storage using `storagePath`
4. Returns binary with proper MIME type
5. Sets immutable cache headers (1-year max-age)

### Fallback Strategy
- If object storage upload fails → falls back to base64 in MongoDB
- If object storage download fails → checks for base64 fallback data
- Logged as warning, not error

## Media Metadata Schema

```json
{
  "id": "uuid",
  "ownerId": "uuid (user who uploaded)",
  "type": "IMAGE | VIDEO",
  "mimeType": "image/jpeg | video/mp4 | ...",
  "size": "bytes (integer)",
  "width": "pixels | null",
  "height": "pixels | null",
  "duration": "seconds | null (video only)",
  "thumbnailId": "uuid | null (future)",
  "status": "READY | PROCESSING | FAILED",
  "storageType": "OBJECT_STORAGE | BASE64",
  "storagePath": "tribe/uploads/... | null",
  "data": "base64 string | null (only if BASE64 fallback)",
  "isDeleted": "boolean",
  "createdAt": "date"
}
```

## CDN Strategy (Production)

### Current (Preview)
- Direct serve through API route with Cache-Control headers
- Suitable for development and testing

### Production Recommendation
1. **CloudFront/CDN** in front of object storage
2. Signed URLs for private media (DMs, restricted content)
3. Edge caching with 1-year TTL for public media
4. Custom domain: `media.tribe.app`

### Implementation Path
```
Client → CDN (CloudFront)
  ↓ miss
  Object Storage (S3-compatible)
  ↓ hit
  Return cached binary with headers
```

## Thumbnail/Transcoding Plan

### Phase 1 (Current)
- Client uploads pre-processed media
- No server-side transcoding
- Accept: JPEG, PNG, WebP, MP4, MOV

### Phase 2 (Planned)
- **Image**: Generate 3 variants (thumbnail 150px, medium 600px, full)
- **Video**: 
  - Extract first frame as thumbnail
  - Transcode to H.264/AAC MP4 (web-compatible)
  - Generate 720p and 360p variants
- **Queue**: Background job queue for processing
- **Status**: Track in `media_assets.status` (PROCESSING → READY/FAILED)

## Size Limits

| Type | Max Size | Max Duration | Enforced In |
|------|----------|-------------|-------------|
| Image | 10 MB | — | media.handler.js |
| Video | 50 MB | 30 seconds | media.handler.js |

## DPDP Compliance

- **Children (under 18)**: Media upload blocked entirely (403 CHILD_RESTRICTED)
- **All users**: No location metadata stored
- **Deletion**: `isDeleted` soft-delete flag, actual storage cleanup via background job

## Migration Status: Base64 → Object Storage

| Aspect | Status |
|--------|--------|
| New uploads → Object Storage | COMPLETE |
| Serve from Object Storage | COMPLETE |
| Base64 fallback for legacy | COMPLETE |
| Legacy data migration | NOT NEEDED (no production users yet) |
| Object storage health check | COMPLETE (`isStorageAvailable()`) |

## Rollback Plan

If object storage becomes unavailable:
1. `isStorageAvailable()` returns false
2. Uploads automatically fall back to base64-in-MongoDB
3. Existing object storage media returns 503 → client retry
4. Manual: Set `STORAGE_DISABLED=true` env var to force base64 mode
5. No data loss — metadata always in MongoDB regardless of storage type
