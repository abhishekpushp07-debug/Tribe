"""
Tribe — Media Infrastructure Tests (Supabase Storage)

Tests the complete media upload pipeline:
- POST /api/media/upload-init (signed URL generation)
- POST /api/media/upload-complete (finalize after direct upload)
- GET /api/media/upload-status/:id (check status)
- POST /api/media/upload (legacy base64, now via Supabase)
- GET /api/media/:id (serve / redirect)

Validation: mime types, file sizes, kind/mime mismatch, auth
"""
import pytest
import requests
import os
import base64

API_URL = os.environ.get('TEST_API_URL', 'http://localhost:3000/api')

# Minimal valid JPEG bytes (1x1 pixel)
TINY_JPEG = bytes([
    0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
    0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43,
    0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08, 0x07, 0x07, 0x07, 0x09,
    0x09, 0x08, 0x0A, 0x0C, 0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12,
    0x13, 0x0F, 0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20,
    0x24, 0x2E, 0x27, 0x20, 0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28, 0x37, 0x29,
    0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27, 0x39, 0x3D, 0x38, 0x32,
    0x3C, 0x2E, 0x33, 0x34, 0x32, 0xFF, 0xC0, 0x00, 0x0B, 0x08, 0x00, 0x01,
    0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0xFF, 0xC4, 0x00, 0x1F, 0x00, 0x00,
    0x01, 0x05, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
    0x09, 0x0A, 0x0B, 0xFF, 0xC4, 0x00, 0xB5, 0x10, 0x00, 0x02, 0x01, 0x03,
    0x03, 0x02, 0x04, 0x03, 0x05, 0x05, 0x04, 0x04, 0x00, 0x00, 0x01, 0x7D,
    0x01, 0x02, 0x03, 0x00, 0x04, 0x11, 0x05, 0x12, 0x21, 0x31, 0x41, 0x06,
    0x13, 0x51, 0x61, 0x07, 0x22, 0x71, 0x14, 0x32, 0x81, 0x91, 0xA1, 0x08,
    0x23, 0x42, 0xB1, 0xC1, 0x15, 0x52, 0xD1, 0xF0, 0x24, 0x33, 0x62, 0x72,
    0x82, 0x09, 0x0A, 0x16, 0x17, 0x18, 0x19, 0x1A, 0x25, 0x26, 0x27, 0x28,
    0x29, 0x2A, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3A, 0x43, 0x44, 0x45,
    0x46, 0x47, 0x48, 0x49, 0x4A, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59,
    0x5A, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6A, 0x73, 0x74, 0x75,
    0x76, 0x77, 0x78, 0x79, 0x7A, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89,
    0x8A, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 0x99, 0x9A, 0xA2, 0xA3,
    0xA4, 0xA5, 0xA6, 0xA7, 0xA8, 0xA9, 0xAA, 0xB2, 0xB3, 0xB4, 0xB5, 0xB6,
    0xB7, 0xB8, 0xB9, 0xBA, 0xC2, 0xC3, 0xC4, 0xC5, 0xC6, 0xC7, 0xC8, 0xC9,
    0xCA, 0xD2, 0xD3, 0xD4, 0xD5, 0xD6, 0xD7, 0xD8, 0xD9, 0xDA, 0xE1, 0xE2,
    0xE3, 0xE4, 0xE5, 0xE6, 0xE7, 0xE8, 0xE9, 0xEA, 0xF1, 0xF2, 0xF3, 0xF4,
    0xF5, 0xF6, 0xF7, 0xF8, 0xF9, 0xFA, 0xFF, 0xDA, 0x00, 0x08, 0x01, 0x01,
    0x00, 0x00, 0x3F, 0x00, 0x7B, 0x94, 0x11, 0x00, 0x00, 0x00, 0x00, 0xFF,
    0xD9
])


def _headers(token=None, ip=None):
    """Build request headers with rate limit bypass."""
    import random
    h = {
        'Content-Type': 'application/json',
        'X-Forwarded-For': ip or f'10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}'
    }
    if token:
        h['Authorization'] = f'Bearer {token}'
    return h


def _post_with_retry(url, json, headers, max_retries=3):
    """POST with 429 retry."""
    import time
    for attempt in range(max_retries):
        resp = requests.post(url, json=json, headers=headers)
        if resp.status_code != 429:
            return resp
        time.sleep(2 * (attempt + 1))
    return resp


def _get_with_retry(url, headers, max_retries=3, **kwargs):
    """GET with 429 retry."""
    import time
    for attempt in range(max_retries):
        resp = requests.get(url, headers=headers, **kwargs)
        if resp.status_code != 429:
            return resp
        time.sleep(2 * (attempt + 1))
    return resp


@pytest.fixture(scope='module')
def media_user(api_url, db):
    """Register/login a dedicated test user for media tests."""
    import random
    phone = f'99999{random.randint(40000,49999)}'
    ip = f'10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}'
    h = _headers(ip=ip)
    resp = requests.post(f'{api_url}/auth/register', json={
        'phone': phone, 'pin': '1234', 'displayName': 'Media Test User',
        'dob': '2000-01-01',
    }, headers=h)
    if resp.status_code not in (200, 201):
        resp = requests.post(f'{api_url}/auth/login', json={
            'phone': phone, 'pin': '1234'
        }, headers=h)
    data = resp.json()
    token = data.get('accessToken') or data.get('token')
    user_id = data.get('user', {}).get('id')
    # Ensure ADULT status for content creation
    db.users.update_one({'id': user_id}, {'$set': {'ageStatus': 'ADULT', 'dob': '2000-01-01'}})
    return {'token': token, 'userId': user_id, 'phone': phone, 'ip': ip}


@pytest.fixture(scope='module')
def media_user_child(api_url, db):
    """A CHILD user for age-restriction tests."""
    import random
    phone = f'99999{random.randint(50000,59999)}'
    ip = f'10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}'
    h = _headers(ip=ip)
    resp = requests.post(f'{api_url}/auth/register', json={
        'phone': phone, 'pin': '1234', 'displayName': 'Child Media User'
    }, headers=h)
    if resp.status_code not in (200, 201):
        resp = requests.post(f'{api_url}/auth/login', json={
            'phone': phone, 'pin': '1234'
        }, headers=h)
    data = resp.json()
    token = data.get('accessToken') or data.get('token')
    user_id = data.get('user', {}).get('id')
    db.users.update_one({'id': user_id}, {'$set': {'ageStatus': 'CHILD'}})
    return {'token': token, 'userId': user_id, 'phone': phone, 'ip': ip}


@pytest.fixture(scope='module')
def media_user_b(api_url, db):
    """A second dedicated media test user for later test classes."""
    import random
    phone = f'99999{random.randint(70000,79999)}'
    ip = f'10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}'
    h = _headers(ip=ip)
    resp = requests.post(f'{api_url}/auth/register', json={
        'phone': phone, 'pin': '1234', 'displayName': 'Media Test User B',
        'dob': '2000-01-01',
    }, headers=h)
    if resp.status_code not in (200, 201):
        resp = requests.post(f'{api_url}/auth/login', json={
            'phone': phone, 'pin': '1234'
        }, headers=h)
    data = resp.json()
    token = data.get('accessToken') or data.get('token')
    user_id = data.get('user', {}).get('id')
    # Ensure ADULT status for content creation
    db.users.update_one({'id': user_id}, {'$set': {'ageStatus': 'ADULT', 'dob': '2000-01-01'}})
    return {'token': token, 'userId': user_id, 'phone': phone, 'ip': ip}


# ============================================================
# UPLOAD-INIT TESTS
# ============================================================

class TestUploadInit:
    """Tests for POST /api/media/upload-init"""

    def test_init_image_jpeg(self, api_url, media_user):
        """Should return signed URL for JPEG image upload."""
        resp = requests.post(f'{api_url}/media/upload-init', json={
            'kind': 'image', 'mimeType': 'image/jpeg', 'sizeBytes': 500000, 'scope': 'posts'
        }, headers=_headers(media_user['token'], media_user['ip']))
        assert resp.status_code == 201
        data = resp.json()
        assert 'mediaId' in data
        assert 'uploadUrl' in data
        assert 'publicUrl' in data
        assert 'token' in data
        assert data['expiresIn'] == 7200
        assert 'supabase.co' in data['uploadUrl']
        assert 'posts/' in data['path']

    def test_init_image_png(self, api_url, media_user):
        """Should return signed URL for PNG image upload."""
        resp = requests.post(f'{api_url}/media/upload-init', json={
            'kind': 'image', 'mimeType': 'image/png', 'sizeBytes': 200000, 'scope': 'stories'
        }, headers=_headers(media_user['token'], media_user['ip']))
        assert resp.status_code == 201
        data = resp.json()
        assert 'stories/' in data['path']
        assert data['path'].endswith('.png')

    def test_init_image_webp(self, api_url, media_user):
        """Should return signed URL for WebP image upload."""
        resp = requests.post(f'{api_url}/media/upload-init', json={
            'kind': 'image', 'mimeType': 'image/webp', 'sizeBytes': 100000, 'scope': 'thumbnails'
        }, headers=_headers(media_user['token'], media_user['ip']))
        assert resp.status_code == 201
        data = resp.json()
        assert 'thumbnails/' in data['path']

    def test_init_video_mp4(self, api_url, media_user):
        """Should return signed URL for MP4 video upload."""
        resp = requests.post(f'{api_url}/media/upload-init', json={
            'kind': 'video', 'mimeType': 'video/mp4', 'sizeBytes': 10000000, 'scope': 'reels'
        }, headers=_headers(media_user['token'], media_user['ip']))
        assert resp.status_code == 201
        data = resp.json()
        assert 'reels/' in data['path']
        assert data['path'].endswith('.mp4')

    def test_init_video_quicktime(self, api_url, media_user):
        """Should return signed URL for QuickTime video upload."""
        resp = requests.post(f'{api_url}/media/upload-init', json={
            'kind': 'video', 'mimeType': 'video/quicktime', 'sizeBytes': 5000000, 'scope': 'reels'
        }, headers=_headers(media_user['token'], media_user['ip']))
        assert resp.status_code == 201
        data = resp.json()
        assert data['path'].endswith('.mov')

    def test_init_default_scope(self, api_url, media_user):
        """Should default to 'posts' scope when not provided."""
        resp = requests.post(f'{api_url}/media/upload-init', json={
            'kind': 'image', 'mimeType': 'image/jpeg', 'sizeBytes': 1000
        }, headers=_headers(media_user['token'], media_user['ip']))
        assert resp.status_code == 201
        assert 'posts/' in resp.json()['path']

    def test_init_invalid_scope_defaults_to_posts(self, api_url, media_user):
        """Should default to posts for invalid scope."""
        resp = requests.post(f'{api_url}/media/upload-init', json={
            'kind': 'image', 'mimeType': 'image/jpeg', 'sizeBytes': 1000, 'scope': 'invalid'
        }, headers=_headers(media_user['token'], media_user['ip']))
        assert resp.status_code == 201
        assert 'posts/' in resp.json()['path']

    # ---- Validation errors ----

    def test_init_invalid_mime_type(self, api_url, media_user):
        """Should reject unsupported MIME types."""
        resp = requests.post(f'{api_url}/media/upload-init', json={
            'kind': 'image', 'mimeType': 'application/pdf', 'sizeBytes': 1000
        }, headers=_headers(media_user['token'], media_user['ip']))
        assert resp.status_code == 400
        assert 'mimeType' in resp.json()['error'].lower() or 'allowed' in resp.json()['error'].lower()

    def test_init_kind_mime_mismatch_image(self, api_url, media_user):
        """Should reject when kind=image but mime is video."""
        resp = requests.post(f'{api_url}/media/upload-init', json={
            'kind': 'image', 'mimeType': 'video/mp4', 'sizeBytes': 1000
        }, headers=_headers(media_user['token'], media_user['ip']))
        assert resp.status_code == 400
        assert 'image' in resp.json()['error'].lower()

    def test_init_kind_mime_mismatch_video(self, api_url, media_user):
        """Should reject when kind=video but mime is image."""
        resp = requests.post(f'{api_url}/media/upload-init', json={
            'kind': 'video', 'mimeType': 'image/jpeg', 'sizeBytes': 1000
        }, headers=_headers(media_user['token'], media_user['ip']))
        assert resp.status_code == 400
        assert 'video' in resp.json()['error'].lower()

    def test_init_invalid_kind(self, api_url, media_user):
        """Should reject invalid kind values."""
        resp = requests.post(f'{api_url}/media/upload-init', json={
            'kind': 'audio', 'mimeType': 'image/jpeg', 'sizeBytes': 1000
        }, headers=_headers(media_user['token'], media_user['ip']))
        assert resp.status_code == 400

    def test_init_missing_required_fields(self, api_url, media_user):
        """Should reject when required fields are missing."""
        resp = requests.post(f'{api_url}/media/upload-init', json={
            'kind': 'image'
        }, headers=_headers(media_user['token'], media_user['ip']))
        assert resp.status_code == 400

    def test_init_file_too_large(self, api_url, media_user):
        """Should reject files exceeding 200MB."""
        resp = requests.post(f'{api_url}/media/upload-init', json={
            'kind': 'video', 'mimeType': 'video/mp4', 'sizeBytes': 210_000_000
        }, headers=_headers(media_user['token'], media_user['ip']))
        assert resp.status_code == 413
        assert resp.json()['code'] == 'PAYLOAD_TOO_LARGE'

    def test_init_zero_size(self, api_url, media_user):
        """Should reject zero-byte files."""
        resp = requests.post(f'{api_url}/media/upload-init', json={
            'kind': 'image', 'mimeType': 'image/jpeg', 'sizeBytes': 0
        }, headers=_headers(media_user['token'], media_user['ip']))
        assert resp.status_code in (400, 413)

    def test_init_requires_auth(self, api_url):
        """Should require authentication."""
        resp = requests.post(f'{api_url}/media/upload-init', json={
            'kind': 'image', 'mimeType': 'image/jpeg', 'sizeBytes': 1000
        }, headers=_headers())
        assert resp.status_code == 401

    def test_init_child_restricted(self, api_url, media_user_child):
        """Should block CHILD users from uploading."""
        resp = requests.post(f'{api_url}/media/upload-init', json={
            'kind': 'image', 'mimeType': 'image/jpeg', 'sizeBytes': 1000
        }, headers=_headers(media_user_child['token'], media_user_child['ip']))
        assert resp.status_code == 403


# ============================================================
# FULL UPLOAD FLOW (init → direct upload → complete)
# ============================================================

class TestFullUploadFlow:
    """Tests the complete 3-step upload process."""

    def test_full_image_upload(self, api_url, media_user):
        """Full flow: init → upload to Supabase → complete."""
        # Step 1: Init
        resp = requests.post(f'{api_url}/media/upload-init', json={
            'kind': 'image', 'mimeType': 'image/jpeg', 'sizeBytes': len(TINY_JPEG), 'scope': 'posts'
        }, headers=_headers(media_user['token'], media_user['ip']))
        assert resp.status_code == 201
        init_data = resp.json()
        media_id = init_data['mediaId']

        # Step 2: Upload directly to Supabase
        upload_resp = requests.put(
            init_data['uploadUrl'],
            data=TINY_JPEG,
            headers={'Content-Type': 'image/jpeg'}
        )
        assert upload_resp.status_code == 200

        # Step 3: Complete
        resp = requests.post(f'{api_url}/media/upload-complete', json={
            'mediaId': media_id, 'width': 1, 'height': 1
        }, headers=_headers(media_user['token'], media_user['ip']))
        assert resp.status_code == 200
        data = resp.json()
        assert data['status'] == 'READY'
        assert data['storageType'] == 'SUPABASE'
        assert 'supabase.co' in data['publicUrl']

        # Step 4: Verify public URL works
        pub_resp = requests.get(data['publicUrl'])
        assert pub_resp.status_code == 200
        assert len(pub_resp.content) == len(TINY_JPEG)

    def test_full_video_upload(self, api_url, media_user):
        """Full flow for video: init → upload → complete with duration."""
        # Create a tiny "video" file (just bytes, Supabase doesn't validate content)
        fake_video = b'\x00' * 1024

        resp = requests.post(f'{api_url}/media/upload-init', json={
            'kind': 'video', 'mimeType': 'video/mp4', 'sizeBytes': len(fake_video), 'scope': 'reels'
        }, headers=_headers(media_user['token'], media_user['ip']))
        assert resp.status_code == 201
        init_data = resp.json()
        media_id = init_data['mediaId']

        # Upload
        upload_resp = requests.put(
            init_data['uploadUrl'],
            data=fake_video,
            headers={'Content-Type': 'video/mp4'}
        )
        assert upload_resp.status_code == 200

        # Complete with duration
        resp = requests.post(f'{api_url}/media/upload-complete', json={
            'mediaId': media_id, 'width': 1080, 'height': 1920, 'duration': 15.5
        }, headers=_headers(media_user['token'], media_user['ip']))
        assert resp.status_code == 200
        data = resp.json()
        assert data['status'] == 'READY'
        assert data['kind'] == 'VIDEO'

    def test_complete_idempotent(self, api_url, media_user):
        """Calling upload-complete twice should be idempotent."""
        # Init + Upload
        resp = requests.post(f'{api_url}/media/upload-init', json={
            'kind': 'image', 'mimeType': 'image/jpeg', 'sizeBytes': len(TINY_JPEG), 'scope': 'posts'
        }, headers=_headers(media_user['token'], media_user['ip']))
        init_data = resp.json()
        media_id = init_data['mediaId']

        requests.put(init_data['uploadUrl'], data=TINY_JPEG,
                     headers={'Content-Type': 'image/jpeg'})

        # Complete first time
        resp1 = requests.post(f'{api_url}/media/upload-complete', json={
            'mediaId': media_id
        }, headers=_headers(media_user['token'], media_user['ip']))
        assert resp1.status_code == 200

        # Complete second time (idempotent)
        resp2 = requests.post(f'{api_url}/media/upload-complete', json={
            'mediaId': media_id
        }, headers=_headers(media_user['token'], media_user['ip']))
        assert resp2.status_code == 200
        assert resp2.json()['status'] == 'READY'


# ============================================================
# UPLOAD-COMPLETE VALIDATION
# ============================================================

class TestUploadComplete:
    """Tests for POST /api/media/upload-complete."""

    def test_complete_missing_media_id(self, api_url, media_user):
        """Should reject when mediaId is missing."""
        resp = requests.post(f'{api_url}/media/upload-complete', json={},
                             headers=_headers(media_user['token'], media_user['ip']))
        assert resp.status_code == 400

    def test_complete_nonexistent_media(self, api_url, media_user):
        """Should return 404 for nonexistent mediaId."""
        resp = requests.post(f'{api_url}/media/upload-complete', json={
            'mediaId': 'nonexistent-uuid'
        }, headers=_headers(media_user['token'], media_user['ip']))
        assert resp.status_code == 404

    def test_complete_requires_auth(self, api_url):
        """Should require authentication."""
        resp = requests.post(f'{api_url}/media/upload-complete', json={
            'mediaId': 'some-id'
        }, headers=_headers())
        assert resp.status_code == 401

    def test_complete_wrong_user(self, api_url, media_user):
        """Should not allow completing another user's upload."""
        # Create upload as media_user
        resp = requests.post(f'{api_url}/media/upload-init', json={
            'kind': 'image', 'mimeType': 'image/jpeg', 'sizeBytes': 100, 'scope': 'posts'
        }, headers=_headers(media_user['token'], media_user['ip']))
        media_id = resp.json()['mediaId']

        # Try to complete as different user
        import random
        phone2 = f'99999{random.randint(60000,69999)}'
        ip2 = f'10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}'
        resp2 = requests.post(f'{api_url}/auth/register', json={
            'phone': phone2, 'pin': '1234', 'displayName': 'Other Media User'
        }, headers=_headers(ip=ip2))
        if resp2.status_code not in (200, 201):
            resp2 = requests.post(f'{api_url}/auth/login', json={
                'phone': phone2, 'pin': '1234'
            }, headers=_headers(ip=ip2))
        token2 = resp2.json().get('accessToken') or resp2.json().get('token')

        resp3 = requests.post(f'{api_url}/media/upload-complete', json={
            'mediaId': media_id
        }, headers=_headers(token2, ip2))
        assert resp3.status_code == 404  # Not found for this user


# ============================================================
# UPLOAD-STATUS TESTS
# ============================================================

class TestUploadStatus:
    """Tests for GET /api/media/upload-status/:id."""

    def test_status_pending(self, api_url, media_user):
        """Should show PENDING_UPLOAD for unfinished upload."""
        resp = requests.post(f'{api_url}/media/upload-init', json={
            'kind': 'image', 'mimeType': 'image/jpeg', 'sizeBytes': 1000, 'scope': 'posts'
        }, headers=_headers(media_user['token'], media_user['ip']))
        media_id = resp.json()['mediaId']

        status_resp = requests.get(f'{api_url}/media/upload-status/{media_id}',
                                   headers=_headers(media_user['token'], media_user['ip']))
        assert status_resp.status_code == 200
        data = status_resp.json()
        assert data['status'] == 'PENDING_UPLOAD'
        assert data['storageType'] == 'SUPABASE'

    def test_status_ready(self, api_url, media_user):
        """Should show READY after completion."""
        # Full flow
        resp = requests.post(f'{api_url}/media/upload-init', json={
            'kind': 'image', 'mimeType': 'image/jpeg', 'sizeBytes': len(TINY_JPEG), 'scope': 'posts'
        }, headers=_headers(media_user['token'], media_user['ip']))
        init_data = resp.json()
        requests.put(init_data['uploadUrl'], data=TINY_JPEG,
                     headers={'Content-Type': 'image/jpeg'})
        requests.post(f'{api_url}/media/upload-complete', json={
            'mediaId': init_data['mediaId']
        }, headers=_headers(media_user['token'], media_user['ip']))

        status_resp = requests.get(f'{api_url}/media/upload-status/{init_data["mediaId"]}',
                                   headers=_headers(media_user['token'], media_user['ip']))
        assert status_resp.status_code == 200
        assert status_resp.json()['status'] == 'READY'

    def test_status_not_found(self, api_url, media_user):
        """Should 404 for nonexistent ID."""
        resp = requests.get(f'{api_url}/media/upload-status/nonexistent-id',
                            headers=_headers(media_user['token'], media_user['ip']))
        assert resp.status_code == 404

    def test_status_requires_auth(self, api_url):
        """Should require authentication."""
        resp = requests.get(f'{api_url}/media/upload-status/some-id',
                            headers=_headers())
        assert resp.status_code == 401


# ============================================================
# LEGACY BASE64 UPLOAD (backward compatibility)
# ============================================================

class TestLegacyBase64Upload:
    """Tests for POST /api/media/upload (legacy base64)."""

    def test_legacy_upload_stores_in_supabase(self, api_url, media_user, db):
        """Legacy base64 upload should now go to Supabase."""
        b64 = base64.b64encode(TINY_JPEG).decode()
        resp = requests.post(f'{api_url}/media/upload', json={
            'data': b64, 'mimeType': 'image/jpeg', 'type': 'IMAGE'
        }, headers=_headers(media_user['token'], media_user['ip']))
        assert resp.status_code == 201
        data = resp.json()
        assert data['storageType'] == 'SUPABASE'
        assert 'supabase.co' in (data.get('publicUrl') or data.get('url', ''))

    def test_legacy_upload_requires_auth(self, api_url):
        """Should require authentication."""
        resp = requests.post(f'{api_url}/media/upload', json={
            'data': 'dGVzdA==', 'mimeType': 'image/jpeg'
        }, headers=_headers())
        assert resp.status_code == 401

    def test_legacy_upload_child_restricted(self, api_url, media_user_child):
        """Should block CHILD users."""
        resp = requests.post(f'{api_url}/media/upload', json={
            'data': 'dGVzdA==', 'mimeType': 'image/jpeg'
        }, headers=_headers(media_user_child['token'], media_user_child['ip']))
        assert resp.status_code == 403


# ============================================================
# MEDIA SERVE (GET /api/media/:id)
# ============================================================

class TestMediaServe:
    """Tests for GET /api/media/:id."""

    def _fresh_ip(self):
        import random
        return f'10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}'

    def test_serve_supabase_redirects(self, api_url, media_user_b):
        """Should 302 redirect to Supabase CDN for Supabase-stored media."""
        ip = self._fresh_ip()
        resp = _post_with_retry(f'{api_url}/media/upload-init', json={
            'kind': 'image', 'mimeType': 'image/jpeg', 'sizeBytes': len(TINY_JPEG), 'scope': 'posts'
        }, headers=_headers(media_user_b['token'], ip))
        assert resp.status_code == 201, f"Init failed: {resp.text}"
        init_data = resp.json()
        requests.put(init_data['uploadUrl'], data=TINY_JPEG,
                     headers={'Content-Type': 'image/jpeg'})
        _post_with_retry(f'{api_url}/media/upload-complete', json={
            'mediaId': init_data['mediaId']
        }, headers=_headers(media_user_b['token'], ip))

        serve_resp = _get_with_retry(f'{api_url}/media/{init_data["mediaId"]}',
                                     allow_redirects=False,
                                     headers=_headers(media_user_b['token'], ip))
        assert serve_resp.status_code == 302
        assert 'supabase.co' in serve_resp.headers['Location']

    def test_serve_supabase_follows_redirect(self, api_url, media_user_b):
        """Following the redirect should serve the file."""
        ip = self._fresh_ip()
        resp = _post_with_retry(f'{api_url}/media/upload-init', json={
            'kind': 'image', 'mimeType': 'image/jpeg', 'sizeBytes': len(TINY_JPEG), 'scope': 'posts'
        }, headers=_headers(media_user_b['token'], ip))
        assert resp.status_code == 201, f"Init failed: {resp.text}"
        init_data = resp.json()
        requests.put(init_data['uploadUrl'], data=TINY_JPEG,
                     headers={'Content-Type': 'image/jpeg'})
        _post_with_retry(f'{api_url}/media/upload-complete', json={
            'mediaId': init_data['mediaId']
        }, headers=_headers(media_user_b['token'], ip))

        serve_resp = _get_with_retry(f'{api_url}/media/{init_data["mediaId"]}',
                                     headers=_headers(media_user_b['token'], ip))
        assert serve_resp.status_code == 200
        assert len(serve_resp.content) == len(TINY_JPEG)

    def test_serve_nonexistent(self, api_url, media_user_b):
        """Should 404 for nonexistent media."""
        ip = self._fresh_ip()
        resp = _get_with_retry(f'{api_url}/media/nonexistent-id',
                               headers=_headers(media_user_b['token'], ip))
        assert resp.status_code == 404

    def test_serve_public_url_accessible(self, api_url, media_user_b):
        """Public URL from Supabase should be directly accessible without auth."""
        ip = self._fresh_ip()
        resp = _post_with_retry(f'{api_url}/media/upload-init', json={
            'kind': 'image', 'mimeType': 'image/jpeg', 'sizeBytes': len(TINY_JPEG), 'scope': 'posts'
        }, headers=_headers(media_user_b['token'], ip))
        assert resp.status_code == 201, f"Init failed: {resp.text}"
        init_data = resp.json()
        requests.put(init_data['uploadUrl'], data=TINY_JPEG,
                     headers={'Content-Type': 'image/jpeg'})
        complete_resp = _post_with_retry(f'{api_url}/media/upload-complete', json={
            'mediaId': init_data['mediaId']
        }, headers=_headers(media_user_b['token'], ip))
        public_url = complete_resp.json()['publicUrl']

        pub_resp = requests.get(public_url)
        assert pub_resp.status_code == 200


# ============================================================
# DB RECORD VERIFICATION
# ============================================================

class TestDBRecords:
    """Verify media_assets collection records."""

    def _fresh_ip(self):
        import random
        return f'10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}'

    def test_init_creates_pending_record(self, api_url, media_user_b, db):
        """upload-init should create a PENDING_UPLOAD record in DB."""
        ip = self._fresh_ip()
        resp = _post_with_retry(f'{api_url}/media/upload-init', json={
            'kind': 'image', 'mimeType': 'image/jpeg', 'sizeBytes': 12345, 'scope': 'stories'
        }, headers=_headers(media_user_b['token'], ip))
        assert resp.status_code == 201, f"Init failed: {resp.text}"
        media_id = resp.json()['mediaId']

        record = db.media_assets.find_one({'id': media_id}, {'_id': 0})
        assert record is not None
        assert record['status'] == 'PENDING_UPLOAD'
        assert record['storageType'] == 'SUPABASE'
        assert record['ownerId'] == media_user_b['userId']
        assert record['mimeType'] == 'image/jpeg'
        assert record['sizeBytes'] == 12345
        assert record['scope'] == 'stories'
        assert 'stories/' in record['storagePath']

    def test_complete_updates_record_to_ready(self, api_url, media_user_b, db):
        """upload-complete should update status to READY with dimensions."""
        ip = self._fresh_ip()
        resp = _post_with_retry(f'{api_url}/media/upload-init', json={
            'kind': 'image', 'mimeType': 'image/jpeg', 'sizeBytes': len(TINY_JPEG), 'scope': 'posts'
        }, headers=_headers(media_user_b['token'], ip))
        assert resp.status_code == 201, f"Init failed: {resp.text}"
        init_data = resp.json()
        requests.put(init_data['uploadUrl'], data=TINY_JPEG,
                     headers={'Content-Type': 'image/jpeg'})
        _post_with_retry(f'{api_url}/media/upload-complete', json={
            'mediaId': init_data['mediaId'], 'width': 800, 'height': 600
        }, headers=_headers(media_user_b['token'], ip))

        record = db.media_assets.find_one({'id': init_data['mediaId']}, {'_id': 0})
        assert record['status'] == 'READY'
        assert record['width'] == 800
        assert record['height'] == 600
        assert record['completedAt'] is not None


# ============================================================
# P1 — CONTENT INTEGRATION TESTS (Reels, Stories, Posts with mediaId)
# ============================================================

class TestReelMediaId:
    """P1: Reel creation with canonical mediaId pipeline."""

    @pytest.fixture(autouse=True, scope='class')
    def reel_user(self, api_url, db, request):
        """Dedicated user for reel tests to avoid rate limits."""
        import random
        phone = f'88888{random.randint(10000,19999)}'
        ip = f'10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}'
        resp = requests.post(f'{api_url}/auth/register', json={
            'phone': phone, 'pin': '1234', 'displayName': 'Reel Tester',
            'dob': '2000-01-01',
        }, headers=_headers(ip=ip))
        if resp.status_code not in (200, 201):
            resp = requests.post(f'{api_url}/auth/login', json={
                'phone': phone, 'pin': '1234'
            }, headers=_headers(ip=ip))
        data = resp.json()
        token = data.get('accessToken') or data.get('token')
        user_id = data.get('user', {}).get('id')
        db.users.update_one({'id': user_id}, {'$set': {'ageStatus': 'ADULT', 'dob': '2000-01-01'}})
        request.cls._reel_token = token
        request.cls._reel_user_id = user_id

    def _fresh_ip(self):
        import random
        return f'10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}'

    def _upload_video(self, api_url):
        """Upload a video and return mediaId."""
        ip = self._fresh_ip()
        fake_video = b'\x00' * 1024
        resp = _post_with_retry(f'{api_url}/media/upload-init', json={
            'kind': 'video', 'mimeType': 'video/mp4', 'sizeBytes': len(fake_video), 'scope': 'reels'
        }, headers=_headers(self._reel_token, ip))
        assert resp.status_code == 201, f"Init failed: {resp.text}"
        init_data = resp.json()
        requests.put(init_data['uploadUrl'], data=fake_video,
                     headers={'Content-Type': 'video/mp4'})
        _post_with_retry(f'{api_url}/media/upload-complete', json={
            'mediaId': init_data['mediaId'], 'duration': 15
        }, headers=_headers(self._reel_token, self._fresh_ip()))
        return init_data['mediaId']

    def _upload_image(self, api_url):
        """Upload an image and return mediaId."""
        ip = self._fresh_ip()
        resp = _post_with_retry(f'{api_url}/media/upload-init', json={
            'kind': 'image', 'mimeType': 'image/jpeg', 'sizeBytes': len(TINY_JPEG), 'scope': 'posts'
        }, headers=_headers(self._reel_token, ip))
        assert resp.status_code == 201, f"Init failed: {resp.text}"
        init_data = resp.json()
        requests.put(init_data['uploadUrl'], data=TINY_JPEG,
                     headers={'Content-Type': 'image/jpeg'})
        _post_with_retry(f'{api_url}/media/upload-complete', json={
            'mediaId': init_data['mediaId']
        }, headers=_headers(self._reel_token, self._fresh_ip()))
        return init_data['mediaId']

    def test_reel_with_valid_video_media_id(self, api_url):
        """Reel creation with uploaded video mediaId should succeed."""
        video_id = self._upload_video(api_url)
        ip = self._fresh_ip()
        resp = _post_with_retry(f'{api_url}/reels', json={
            'mediaId': video_id, 'caption': 'Reel with real video'
        }, headers=_headers(self._reel_token, ip))
        assert resp.status_code in (200, 201), f"Reel create failed: {resp.text}"
        reel = resp.json().get('reel', {})
        assert reel.get('mediaId') == video_id
        assert reel.get('mediaStatus') == 'READY'
        assert reel.get('playbackUrl') is not None
        assert 'supabase.co' in reel.get('playbackUrl', '')

    def test_reel_reject_image_media_id(self, api_url):
        """Reel creation with image mediaId should be rejected."""
        image_id = self._upload_image(api_url)
        ip = self._fresh_ip()
        resp = _post_with_retry(f'{api_url}/reels', json={
            'mediaId': image_id, 'caption': 'Should fail'
        }, headers=_headers(self._reel_token, ip))
        assert resp.status_code == 400
        assert 'video' in resp.json().get('error', '').lower()

    def test_reel_reject_pending_media(self, api_url):
        """Reel creation with PENDING_UPLOAD media should be rejected."""
        ip = self._fresh_ip()
        resp = _post_with_retry(f'{api_url}/media/upload-init', json={
            'kind': 'video', 'mimeType': 'video/mp4', 'sizeBytes': 1024, 'scope': 'reels'
        }, headers=_headers(self._reel_token, ip))
        assert resp.status_code == 201, f"Init failed: {resp.text}"
        pending_id = resp.json()['mediaId']

        resp2 = _post_with_retry(f'{api_url}/reels', json={
            'mediaId': pending_id, 'caption': 'Should fail'
        }, headers=_headers(self._reel_token, self._fresh_ip()))
        assert resp2.status_code == 400

    def test_reel_reject_nonexistent_media(self, api_url):
        """Reel creation with nonexistent mediaId should be rejected."""
        ip = self._fresh_ip()
        resp = _post_with_retry(f'{api_url}/reels', json={
            'mediaId': 'nonexistent-uuid', 'caption': 'Should fail'
        }, headers=_headers(self._reel_token, ip))
        assert resp.status_code == 404

    def test_reel_reject_wrong_owner_media(self, api_url, media_user_b):
        """Reel creation with another user's media should be rejected."""
        # Upload as user B
        ip = self._fresh_ip()
        fake_video = b'\x00' * 512
        resp = _post_with_retry(f'{api_url}/media/upload-init', json={
            'kind': 'video', 'mimeType': 'video/mp4', 'sizeBytes': len(fake_video), 'scope': 'reels'
        }, headers=_headers(media_user_b['token'], ip))
        init_data = resp.json()
        requests.put(init_data['uploadUrl'], data=fake_video,
                     headers={'Content-Type': 'video/mp4'})
        _post_with_retry(f'{api_url}/media/upload-complete', json={
            'mediaId': init_data['mediaId']
        }, headers=_headers(media_user_b['token'], self._fresh_ip()))
        video_id = init_data['mediaId']

        # Try to create reel as reel_user (different user)
        resp2 = _post_with_retry(f'{api_url}/reels', json={
            'mediaId': video_id, 'caption': 'Should fail'
        }, headers=_headers(self._reel_token, self._fresh_ip()))
        assert resp2.status_code == 404

    def test_unique_media_ids_for_multiple_reels(self, api_url):
        """Each reel should have its own unique mediaId."""
        video1 = self._upload_video(api_url)
        video2 = self._upload_video(api_url)
        assert video1 != video2

        resp1 = _post_with_retry(f'{api_url}/reels', json={
            'mediaId': video1, 'caption': 'Reel 1'
        }, headers=_headers(self._reel_token, self._fresh_ip()))
        resp2 = _post_with_retry(f'{api_url}/reels', json={
            'mediaId': video2, 'caption': 'Reel 2'
        }, headers=_headers(self._reel_token, self._fresh_ip()))

        reel1 = resp1.json().get('reel', {})
        reel2 = resp2.json().get('reel', {})
        assert reel1.get('mediaId') != reel2.get('mediaId')
        assert reel1.get('playbackUrl') != reel2.get('playbackUrl')

    def test_reel_legacy_media_url_still_works(self, api_url):
        """Legacy mediaUrl field should still create a reel."""
        ip = self._fresh_ip()
        resp = _post_with_retry(f'{api_url}/reels', json={
            'mediaUrl': 'https://example.com/test-video.mp4',
            'caption': 'Legacy reel'
        }, headers=_headers(self._reel_token, ip))
        assert resp.status_code in (200, 201)
        reel = resp.json().get('reel', {})
        assert reel.get('playbackUrl') == 'https://example.com/test-video.mp4'


class TestStoryMediaId:
    """P1: Story creation with canonical mediaId pipeline."""

    def _fresh_ip(self):
        import random
        return f'10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}'

    def test_story_with_image_media_id(self, api_url, media_user_b):
        """Story creation with uploaded image mediaId."""
        ip = self._fresh_ip()
        resp = _post_with_retry(f'{api_url}/media/upload-init', json={
            'kind': 'image', 'mimeType': 'image/jpeg', 'sizeBytes': len(TINY_JPEG), 'scope': 'stories'
        }, headers=_headers(media_user_b['token'], ip))
        init_data = resp.json()
        requests.put(init_data['uploadUrl'], data=TINY_JPEG,
                     headers={'Content-Type': 'image/jpeg'})
        _post_with_retry(f'{api_url}/media/upload-complete', json={
            'mediaId': init_data['mediaId']
        }, headers=_headers(media_user_b['token'], self._fresh_ip()))

        # Create story
        resp2 = _post_with_retry(f'{api_url}/stories', json={
            'type': 'IMAGE', 'mediaIds': [init_data['mediaId']], 'caption': 'Story test'
        }, headers=_headers(media_user_b['token'], self._fresh_ip()))
        assert resp2.status_code in (200, 201)
        story = resp2.json().get('story', {})
        media = story.get('media', [])
        assert len(media) >= 1
        assert 'supabase.co' in media[0].get('url', '')

    def test_story_with_video_media_id(self, api_url, media_user_b):
        """Story creation with uploaded video mediaId."""
        ip = self._fresh_ip()
        fake_video = b'\x00' * 512
        resp = _post_with_retry(f'{api_url}/media/upload-init', json={
            'kind': 'video', 'mimeType': 'video/mp4', 'sizeBytes': len(fake_video), 'scope': 'stories'
        }, headers=_headers(media_user_b['token'], ip))
        init_data = resp.json()
        requests.put(init_data['uploadUrl'], data=fake_video,
                     headers={'Content-Type': 'video/mp4'})
        _post_with_retry(f'{api_url}/media/upload-complete', json={
            'mediaId': init_data['mediaId'], 'duration': 10
        }, headers=_headers(media_user_b['token'], self._fresh_ip()))

        resp2 = _post_with_retry(f'{api_url}/stories', json={
            'type': 'VIDEO', 'mediaIds': [init_data['mediaId']], 'caption': 'Video story'
        }, headers=_headers(media_user_b['token'], self._fresh_ip()))
        assert resp2.status_code in (200, 201)


class TestPostMediaId:
    """P1: Post creation with canonical mediaId pipeline."""

    def _fresh_ip(self):
        import random
        return f'10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}'

    def test_post_with_image_and_caption(self, api_url, media_user_b):
        """Post with image mediaId and caption + hashtags."""
        ip = self._fresh_ip()
        resp = _post_with_retry(f'{api_url}/media/upload-init', json={
            'kind': 'image', 'mimeType': 'image/jpeg', 'sizeBytes': len(TINY_JPEG), 'scope': 'posts'
        }, headers=_headers(media_user_b['token'], ip))
        init_data = resp.json()
        requests.put(init_data['uploadUrl'], data=TINY_JPEG,
                     headers={'Content-Type': 'image/jpeg'})
        _post_with_retry(f'{api_url}/media/upload-complete', json={
            'mediaId': init_data['mediaId']
        }, headers=_headers(media_user_b['token'], self._fresh_ip()))

        resp2 = _post_with_retry(f'{api_url}/content/posts', json={
            'caption': 'Post with media #test #supabase',
            'mediaIds': [init_data['mediaId']]
        }, headers=_headers(media_user_b['token'], self._fresh_ip()))
        assert resp2.status_code in (200, 201)
        post = resp2.json().get('post', {})
        media = post.get('media', [])
        assert len(media) >= 1
        assert 'supabase.co' in media[0].get('url', '')
        assert media[0].get('storageType') == 'SUPABASE'

    def test_text_only_post_unaffected(self, api_url, media_user_b):
        """Text-only posts should still work without media."""
        ip = self._fresh_ip()
        resp = _post_with_retry(f'{api_url}/content/posts', json={
            'caption': 'Just text, no media #textonly'
        }, headers=_headers(media_user_b['token'], ip))
        assert resp.status_code in (200, 201)


# ============================================================
# P2 — CLEANUP TESTS
# ============================================================

class TestOrphanCleanup:
    """P2: Stale PENDING_UPLOAD cleanup."""

    def _fresh_ip(self):
        import random
        return f'10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}'

    def test_admin_cleanup_dry_run(self, api_url, db):
        """Admin cleanup dry-run should report stale uploads."""
        import random
        # Create admin user
        phone = f'99999{random.randint(80000,89999)}'
        ip = self._fresh_ip()
        resp = requests.post(f'{api_url}/auth/register', json={
            'phone': phone, 'pin': '1234', 'displayName': 'Admin Cleanup'
        }, headers=_headers(ip=ip))
        if resp.status_code not in (200, 201):
            resp = requests.post(f'{api_url}/auth/login', json={
                'phone': phone, 'pin': '1234'
            }, headers=_headers(ip=ip))
        data = resp.json()
        token = data.get('accessToken') or data.get('token')
        user_id = data.get('user', {}).get('id')
        db.users.update_one({'id': user_id}, {'$set': {'role': 'ADMIN'}})

        # Insert a synthetic stale PENDING_UPLOAD (25 hours old)
        from datetime import datetime, timedelta
        stale_id = f'stale-test-{random.randint(10000,99999)}'
        db.media_assets.insert_one({
            'id': stale_id,
            'ownerId': user_id,
            'status': 'PENDING_UPLOAD',
            'storageType': 'SUPABASE',
            'storagePath': f'posts/{user_id}/{stale_id}.jpg',
            'mimeType': 'image/jpeg',
            'sizeBytes': 1000,
            'isDeleted': False,
            'createdAt': datetime.utcnow() - timedelta(hours=25),
        })

        # Dry run
        resp2 = _post_with_retry(f'{api_url}/admin/media/cleanup', json={
            'dryRun': True
        }, headers=_headers(token, self._fresh_ip()))
        assert resp2.status_code == 200
        result = resp2.json()
        assert result.get('mode') == 'DRY_RUN'
        assert result.get('staleCount', 0) >= 1

    def test_admin_cleanup_execute(self, api_url, db):
        """Admin cleanup execute should clean stale uploads."""
        import random
        phone = f'99999{random.randint(90000,99999)}'
        ip = self._fresh_ip()
        resp = requests.post(f'{api_url}/auth/register', json={
            'phone': phone, 'pin': '1234', 'displayName': 'Admin Cleanup2'
        }, headers=_headers(ip=ip))
        if resp.status_code not in (200, 201):
            resp = requests.post(f'{api_url}/auth/login', json={
                'phone': phone, 'pin': '1234'
            }, headers=_headers(ip=ip))
        data = resp.json()
        token = data.get('accessToken') or data.get('token')
        user_id = data.get('user', {}).get('id')
        db.users.update_one({'id': user_id}, {'$set': {'role': 'ADMIN'}})

        # Insert stale upload
        from datetime import datetime, timedelta
        stale_id = f'stale-exec-{random.randint(10000,99999)}'
        db.media_assets.insert_one({
            'id': stale_id,
            'ownerId': user_id,
            'status': 'PENDING_UPLOAD',
            'storageType': 'SUPABASE',
            'storagePath': f'posts/{user_id}/{stale_id}.jpg',
            'mimeType': 'image/jpeg',
            'sizeBytes': 1000,
            'isDeleted': False,
            'createdAt': datetime.utcnow() - timedelta(hours=25),
        })

        # Execute cleanup
        resp2 = _post_with_retry(f'{api_url}/admin/media/cleanup', json={
            'dryRun': False
        }, headers=_headers(token, self._fresh_ip()))
        assert resp2.status_code == 200
        result = resp2.json()
        assert result.get('mode') == 'EXECUTE'
        assert result.get('cleaned', 0) >= 1

        # Verify record is marked as cleaned
        record = db.media_assets.find_one({'id': stale_id})
        assert record['status'] == 'ORPHAN_CLEANED'
        assert record['isDeleted'] is True

    def test_cleanup_does_not_touch_ready_media(self, api_url, db):
        """Cleanup must never delete READY media."""
        import random
        from datetime import datetime, timedelta

        # Insert a READY media record that's "old"
        ready_id = f'ready-safe-{random.randint(10000,99999)}'
        db.media_assets.insert_one({
            'id': ready_id,
            'ownerId': 'test',
            'status': 'READY',
            'storageType': 'SUPABASE',
            'storagePath': f'posts/test/{ready_id}.jpg',
            'mimeType': 'image/jpeg',
            'sizeBytes': 1000,
            'isDeleted': False,
            'createdAt': datetime.utcnow() - timedelta(hours=48),
        })

        # Insert admin
        phone = f'88888{random.randint(10000,19999)}'
        ip = f'10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}'
        resp = requests.post(f'{api_url}/auth/register', json={
            'phone': phone, 'pin': '1234', 'displayName': 'Admin Safe'
        }, headers=_headers(ip=ip))
        if resp.status_code not in (200, 201):
            resp = requests.post(f'{api_url}/auth/login', json={
                'phone': phone, 'pin': '1234'
            }, headers=_headers(ip=ip))
        token = resp.json().get('accessToken') or resp.json().get('token')
        uid = resp.json().get('user', {}).get('id')
        db.users.update_one({'id': uid}, {'$set': {'role': 'ADMIN'}})

        # Execute cleanup
        _post_with_retry(f'{api_url}/admin/media/cleanup', json={
            'dryRun': False
        }, headers=_headers(token, ip))

        # READY record must be untouched
        record = db.media_assets.find_one({'id': ready_id})
        assert record['status'] == 'READY'
        assert record.get('isDeleted') is not True

        # Cleanup test data
        db.media_assets.delete_one({'id': ready_id})


# ============================================================
# P3 — MEDIA SERVING TRUTH TESTS
# ============================================================

class TestMediaServingTruth:
    """P3: Media serving returns real content, not stubs."""

    def _fresh_ip(self):
        import random
        return f'10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}'

    def test_supabase_media_serves_real_content(self, api_url, media_user_b):
        """Supabase-stored media should serve real bytes, not stubs."""
        ip = self._fresh_ip()
        resp = _post_with_retry(f'{api_url}/media/upload-init', json={
            'kind': 'image', 'mimeType': 'image/jpeg', 'sizeBytes': len(TINY_JPEG), 'scope': 'posts'
        }, headers=_headers(media_user_b['token'], ip))
        init_data = resp.json()
        requests.put(init_data['uploadUrl'], data=TINY_JPEG,
                     headers={'Content-Type': 'image/jpeg'})
        _post_with_retry(f'{api_url}/media/upload-complete', json={
            'mediaId': init_data['mediaId']
        }, headers=_headers(media_user_b['token'], self._fresh_ip()))

        # Fetch via /api/media/:id (follows redirect)
        serve_resp = _get_with_retry(f'{api_url}/media/{init_data["mediaId"]}',
                                     headers=_headers(media_user_b['token'], self._fresh_ip()))
        assert serve_resp.status_code == 200
        assert len(serve_resp.content) == len(TINY_JPEG)
        # Must NOT be a tiny stub
        assert len(serve_resp.content) > 10

    def test_media_redirect_has_correct_headers(self, api_url, media_user_b):
        """302 redirect should have correct Location and Cache-Control headers."""
        ip = self._fresh_ip()
        resp = _post_with_retry(f'{api_url}/media/upload-init', json={
            'kind': 'image', 'mimeType': 'image/jpeg', 'sizeBytes': len(TINY_JPEG), 'scope': 'posts'
        }, headers=_headers(media_user_b['token'], ip))
        init_data = resp.json()
        requests.put(init_data['uploadUrl'], data=TINY_JPEG,
                     headers={'Content-Type': 'image/jpeg'})
        _post_with_retry(f'{api_url}/media/upload-complete', json={
            'mediaId': init_data['mediaId']
        }, headers=_headers(media_user_b['token'], self._fresh_ip()))

        serve_resp = _get_with_retry(f'{api_url}/media/{init_data["mediaId"]}',
                                     allow_redirects=False,
                                     headers=_headers(media_user_b['token'], self._fresh_ip()))
        assert serve_resp.status_code == 302
        location = serve_resp.headers.get('Location', '')
        assert 'supabase.co' in location
        assert 'tribe-media' in location

    def test_missing_media_returns_404(self, api_url, media_user_b):
        """Nonexistent media ID should return 404."""
        ip = self._fresh_ip()
        resp = _get_with_retry(f'{api_url}/media/does-not-exist-uuid',
                               headers=_headers(media_user_b['token'], ip))
        assert resp.status_code == 404

    def test_video_upload_public_url_accessible(self, api_url, media_user_b):
        """Uploaded video public URL should be directly accessible."""
        ip = self._fresh_ip()
        fake_video = b'\x00\x00\x00\x20ftypmp42' + b'\x00' * 500
        resp = _post_with_retry(f'{api_url}/media/upload-init', json={
            'kind': 'video', 'mimeType': 'video/mp4', 'sizeBytes': len(fake_video), 'scope': 'reels'
        }, headers=_headers(media_user_b['token'], ip))
        init_data = resp.json()
        requests.put(init_data['uploadUrl'], data=fake_video,
                     headers={'Content-Type': 'video/mp4'})
        complete_resp = _post_with_retry(f'{api_url}/media/upload-complete', json={
            'mediaId': init_data['mediaId'], 'duration': 30
        }, headers=_headers(media_user_b['token'], self._fresh_ip()))
        pub_url = complete_resp.json().get('publicUrl', '')

        # Direct access without auth
        pub_resp = requests.get(pub_url)
        assert pub_resp.status_code == 200
        assert len(pub_resp.content) == len(fake_video)
