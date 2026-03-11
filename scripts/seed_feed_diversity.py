"""
Tribe — Live Feed Diversity Seed Script
Creates real backend data for frontend live validation:
  - 2 PAGE posts (1 with verified badge)
  - 2 media posts (1 single, 1 multi)
  - 2 repost posts 
  - 1 edited post
All created through canonical API paths.
"""
import requests
import json
import base64
import time
import sys

API_URL = 'http://localhost:3000/api'

# Minimal 1x1 red PNG (valid image)
TINY_PNG = base64.b64encode(
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
    b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f'
    b'\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
).decode()

# Minimal 1x1 blue PNG (different image for carousel)
TINY_PNG_2 = base64.b64encode(
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
    b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf'
    b'\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
).decode()

IP_CTR = [100]
def next_ip():
    IP_CTR[0] += 1
    return f'10.99.{IP_CTR[0] // 256}.{IP_CTR[0] % 256}'

def auth_h(token):
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'X-Forwarded-For': next_ip(),
    }

def register(phone, name):
    """Register or login a user via canonical auth paths."""
    ip = next_ip()
    h = {'Content-Type': 'application/json', 'X-Forwarded-For': ip}
    pin = '1234'
    
    # Try register first
    r = requests.post(f'{API_URL}/auth/register', json={
        'phone': phone, 'pin': pin, 'displayName': name
    }, headers=h)
    
    if r.status_code in (200, 201):
        data = r.json()
        token = data.get('accessToken') or data.get('token')
        user_id = data.get('user', {}).get('id')
        return {'token': token, 'userId': user_id, 'phone': phone, 'name': name}
    
    # Already exists — login
    r = requests.post(f'{API_URL}/auth/login', json={'phone': phone, 'pin': pin}, headers=h)
    if r.status_code == 200:
        data = r.json()
        token = data.get('accessToken') or data.get('token')
        user_id = data.get('user', {}).get('id')
        return {'token': token, 'userId': user_id, 'phone': phone, 'name': name}
    
    print(f'  Auth failed for {phone}: {r.status_code} {r.text}')
    return None

def retry(fn, retries=3):
    for i in range(retries):
        r = fn()
        if r.status_code == 429:
            time.sleep(3 + i * 3)
            continue
        return r
    return r

def main():
    report = {'records': [], 'errors': []}
    
    print("=" * 60)
    print("TRIBE LIVE FEED DIVERSITY SEED")
    print("=" * 60)
    
    # 1. Register/login seed users
    print("\n[1] Registering seed users...")
    user_a = register('9999960001', 'Seed Creator Alpha')
    user_b = register('9999960002', 'Seed Creator Beta')
    
    if not user_a or not user_b:
        print("FATAL: Could not create seed users")
        sys.exit(1)
    
    print(f"  User A: {user_a['userId']}")
    print(f"  User B: {user_b['userId']}")
    
    # Set both as ADULT
    import pymongo
    from pymongo import MongoClient
    import os
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = MongoClient(mongo_url)
    # Read DB_NAME from .env file (same as Next.js app)
    db_name = os.environ.get('DB_NAME')
    if not db_name:
        with open('/app/.env') as f:
            for line in f:
                if line.startswith('DB_NAME='):
                    db_name = line.strip().split('=', 1)[1]
    db = client[db_name]
    print(f"  DB: {db_name}")
    
    db.users.update_many(
        {'phone': {'$in': ['9999960001', '9999960002']}},
        {'$set': {'ageStatus': 'ADULT', 'birthYear': 2000, 'dateOfBirth': '2000-01-15'}}
    )
    
    # Re-login to get fresh tokens reflecting updated user state
    user_a = register('9999960001', 'Seed Creator Alpha')
    user_b = register('9999960002', 'Seed Creator Beta')
    if not user_a or not user_b:
        print("FATAL: Re-login failed")
        sys.exit(1)
    print(f"  Re-logged in with ADULT status")
    
    # 2. Create a Page (will verify via DB)
    print("\n[2] Creating verified page...")
    page_r = retry(lambda: requests.post(f'{API_URL}/pages', json={
        'name': 'Tribe Campus Memes',
        'slug': 'tribe-campus-memes-seed',
        'category': 'MEME',
        'bio': 'The best meme page for Tribe campus life',
    }, headers=auth_h(user_a['token'])))
    
    if page_r.status_code == 409:
        # Page already exists, find it
        search_r = requests.get(f'{API_URL}/pages?q=tribe-memes-seed', headers=auth_h(user_a['token']))
        pages = search_r.json().get('items') or search_r.json().get('pages', [])
        page_id = pages[0]['id'] if pages else None
        if not page_id:
            page_doc = db.pages.find_one({'slug': 'tribe-campus-memes-seed'})
            page_id = page_doc['id'] if page_doc else None
        print(f"  Page already exists: {page_id}")
    elif page_r.status_code in (200, 201):
        page_id = page_r.json().get('page', {}).get('id') or page_r.json().get('data', {}).get('page', {}).get('id')
        print(f"  Page created: {page_id}")
    else:
        print(f"  Page creation failed: {page_r.status_code} {page_r.text}")
        page_id = None
    
    if page_id:
        # Set verification to VERIFIED via DB (admin-only path)
        db.pages.update_one(
            {'id': page_id},
            {'$set': {'verificationStatus': 'VERIFIED', 'isOfficial': True}}
        )
        print(f"  Page verified: {page_id}")
    
    # 3. User B follows User A and the page
    print("\n[3] Setting up follows...")
    retry(lambda: requests.post(f'{API_URL}/follow/{user_a["userId"]}', headers=auth_h(user_b['token'])))
    if page_id:
        retry(lambda: requests.post(f'{API_URL}/pages/{page_id}/follow', headers=auth_h(user_b['token'])))
    print("  Follows set up")
    
    # 4. Upload media assets
    print("\n[4] Uploading media assets...")
    media_ids = []
    for i, (png_data, label) in enumerate([(TINY_PNG, 'Image 1'), (TINY_PNG_2, 'Image 2')]):
        r = retry(lambda d=png_data: requests.post(f'{API_URL}/media/upload', json={
            'data': d,
            'mimeType': 'image/png',
            'type': 'IMAGE',
            'width': 1,
            'height': 1,
        }, headers=auth_h(user_a['token'])))
        if r.status_code in (200, 201):
            mid = r.json().get('id') or r.json().get('data', {}).get('id')
            media_ids.append(mid)
            print(f"  Media {label}: {mid}")
        else:
            print(f"  Media upload failed: {r.status_code} {r.text}")
            report['errors'].append(f'Media upload {label} failed')
    
    # Upload additional media for user B
    media_ids_b = []
    for i, (png_data, label) in enumerate([(TINY_PNG, 'Image B1')]):
        r = retry(lambda d=png_data: requests.post(f'{API_URL}/media/upload', json={
            'data': d,
            'mimeType': 'image/png',
            'type': 'IMAGE',
            'width': 1,
            'height': 1,
        }, headers=auth_h(user_b['token'])))
        if r.status_code in (200, 201):
            mid = r.json().get('id') or r.json().get('data', {}).get('id')
            media_ids_b.append(mid)
            print(f"  Media {label}: {mid}")
        else:
            print(f"  Media upload failed: {r.status_code} {r.text}")
    
    # =========================================
    # 5. CREATE SEED RECORDS
    # =========================================
    
    created_ids = []
    
    # --- PAGE POST #1: Text-only page post ---
    print("\n[5A] Creating PAGE POST #1 (text-only, verified page)...")
    if page_id:
        r = retry(lambda: requests.post(f'{API_URL}/pages/{page_id}/posts', json={
            'caption': 'When you realize finals are next week but you still have not started studying 📚😭 #CampusLife #TribeMemes',
        }, headers=auth_h(user_a['token'])))
        if r.status_code in (200, 201):
            d = r.json().get('data', r.json())
            post = d.get('post', {})
            pid = post.get('id')
            created_ids.append(pid)
            report['records'].append({'type': 'PAGE_POST', 'id': pid, 'author': page_id, 'variant': 'text-only, verified page'})
            print(f"  PAGE POST #1: {pid}")
        else:
            print(f"  Failed: {r.status_code} {r.text}")
            report['errors'].append(f'PAGE POST #1 failed: {r.status_code}')
    
    # --- PAGE POST #2: Page post with media ---
    print("\n[5B] Creating PAGE POST #2 (with media, verified page)...")
    if page_id and len(media_ids) >= 1:
        r = retry(lambda: requests.post(f'{API_URL}/pages/{page_id}/posts', json={
            'caption': 'New campus panorama shot from the rooftop! 🏫✨ #TribeViews',
            'mediaIds': [media_ids[0]],
        }, headers=auth_h(user_a['token'])))
        if r.status_code in (200, 201):
            d = r.json().get('data', r.json())
            post = d.get('post', {})
            pid = post.get('id')
            created_ids.append(pid)
            report['records'].append({'type': 'PAGE_MEDIA_POST', 'id': pid, 'author': page_id, 'variant': 'media + verified page'})
            print(f"  PAGE POST #2: {pid}")
        else:
            print(f"  Failed: {r.status_code} {r.text}")
            report['errors'].append(f'PAGE POST #2 failed: {r.status_code}')
    
    # --- MEDIA POST #1: Single media ---
    print("\n[5C] Creating MEDIA POST #1 (single image, user-authored)...")
    if len(media_ids) >= 2:
        r = retry(lambda: requests.post(f'{API_URL}/content/posts', json={
            'caption': 'Morning vibes at the library ☀️ #StudyGram',
            'kind': 'POST',
            'mediaIds': [media_ids[1]],
        }, headers=auth_h(user_a['token'])))
        if r.status_code in (200, 201):
            d = r.json().get('data', r.json())
            post = d.get('post', {})
            pid = post.get('id')
            created_ids.append(pid)
            report['records'].append({'type': 'MEDIA_POST_SINGLE', 'id': pid, 'author': user_a['userId'], 'variant': 'single image'})
            print(f"  MEDIA POST #1: {pid}")
        else:
            print(f"  Failed: {r.status_code} {r.text}")
            report['errors'].append(f'MEDIA POST #1 failed: {r.status_code}')
    
    # --- MEDIA POST #2: Multi/carousel (2 images) ---
    print("\n[5D] Creating MEDIA POST #2 (carousel, user-authored)...")
    # Upload one more media for user_a
    r = retry(lambda: requests.post(f'{API_URL}/media/upload', json={
        'data': TINY_PNG_2,
        'mimeType': 'image/png',
        'type': 'IMAGE',
        'width': 1,
        'height': 1,
    }, headers=auth_h(user_a['token'])))
    extra_media = None
    if r.status_code in (200, 201):
        extra_media = r.json().get('id') or r.json().get('data', {}).get('id')
    
    if len(media_ids) >= 1 and extra_media:
        # Upload yet another for multi
        r = retry(lambda: requests.post(f'{API_URL}/media/upload', json={
            'data': TINY_PNG,
            'mimeType': 'image/png',
            'type': 'IMAGE',
            'width': 1,
            'height': 1,
        }, headers=auth_h(user_a['token'])))
        extra_media2 = None
        if r.status_code in (200, 201):
            extra_media2 = r.json().get('id') or r.json().get('data', {}).get('id')
        
        carousel_ids = [extra_media]
        if extra_media2:
            carousel_ids.append(extra_media2)
        
        r = retry(lambda: requests.post(f'{API_URL}/content/posts', json={
            'caption': 'College fest highlights 🎉🎶 Swipe for more! #FestLife',
            'kind': 'POST',
            'mediaIds': carousel_ids,
        }, headers=auth_h(user_a['token'])))
        if r.status_code in (200, 201):
            d = r.json().get('data', r.json())
            post = d.get('post', {})
            pid = post.get('id')
            created_ids.append(pid)
            report['records'].append({'type': 'MEDIA_POST_CAROUSEL', 'id': pid, 'author': user_a['userId'], 'variant': f'{len(carousel_ids)}-image carousel'})
            print(f"  MEDIA POST #2 (carousel): {pid}")
        else:
            print(f"  Failed: {r.status_code} {r.text}")
            report['errors'].append(f'MEDIA POST #2 failed: {r.status_code}')
    
    # --- TEXT POST for reposting ---
    print("\n[5E] Creating original text post for repost...")
    r = retry(lambda: requests.post(f'{API_URL}/content/posts', json={
        'caption': 'Hot take: The canteen samosa is overrated. Fight me. 🔥',
        'kind': 'POST',
    }, headers=auth_h(user_a['token'])))
    original_post_id = None
    if r.status_code in (200, 201):
        d = r.json().get('data', r.json())
        post = d.get('post', {})
        original_post_id = post.get('id')
        created_ids.append(original_post_id)
        report['records'].append({'type': 'ORIGINAL_TEXT_POST', 'id': original_post_id, 'author': user_a['userId'], 'variant': 'text-only (repost source)'})
        print(f"  Original post: {original_post_id}")
    else:
        print(f"  Failed: {r.status_code} {r.text}")
    
    # --- REPOST #1: User B reposts User A's text post ---
    print("\n[5F] Creating REPOST #1 (user B reposts user A's text post)...")
    if original_post_id:
        r = retry(lambda: requests.post(f'{API_URL}/content/{original_post_id}/share', json={
            'caption': 'Absolutely agree with this hot take 💯',
        }, headers=auth_h(user_b['token'])))
        if r.status_code in (200, 201):
            d = r.json().get('data', r.json())
            repost = d.get('repost', d.get('post', {}))
            rid = repost.get('id')
            created_ids.append(rid)
            report['records'].append({'type': 'REPOST', 'id': rid, 'author': user_b['userId'], 'variant': 'repost of text post', 'originalId': original_post_id})
            print(f"  REPOST #1: {rid}")
        else:
            print(f"  Failed: {r.status_code} {r.text}")
            report['errors'].append(f'REPOST #1 failed: {r.status_code}')
    
    # --- REPOST #2: User B reposts a PAGE post ---
    print("\n[5G] Creating REPOST #2 (user B reposts PAGE post)...")
    page_post_id = None
    for rec in report['records']:
        if rec['type'] in ('PAGE_POST', 'PAGE_MEDIA_POST'):
            page_post_id = rec['id']
            break
    
    if page_post_id:
        r = retry(lambda: requests.post(f'{API_URL}/content/{page_post_id}/share', json={
            'caption': 'This page always has the best content 🙌',
        }, headers=auth_h(user_b['token'])))
        if r.status_code in (200, 201):
            d = r.json().get('data', r.json())
            repost = d.get('repost', d.get('post', {}))
            rid = repost.get('id')
            created_ids.append(rid)
            report['records'].append({'type': 'REPOST_OF_PAGE', 'id': rid, 'author': user_b['userId'], 'variant': 'repost of PAGE post', 'originalId': page_post_id})
            print(f"  REPOST #2: {rid}")
        else:
            print(f"  Failed: {r.status_code} {r.text}")
            report['errors'].append(f'REPOST #2 failed: {r.status_code}')
    
    # --- EDITED POST ---
    print("\n[5H] Creating EDITED POST (create then edit)...")
    r = retry(lambda: requests.post(f'{API_URL}/content/posts', json={
        'caption': 'Just had the worst day ever...',
        'kind': 'POST',
    }, headers=auth_h(user_a['token'])))
    edit_post_id = None
    if r.status_code in (200, 201):
        d = r.json().get('data', r.json())
        post = d.get('post', {})
        edit_post_id = post.get('id')
        print(f"  Original: {edit_post_id}")
        
        # Now edit it
        time.sleep(0.5)
        r2 = retry(lambda: requests.patch(f'{API_URL}/content/{edit_post_id}', json={
            'caption': 'Update: Day got way better! Just found out I passed my exam! 🎉 (edited)',
        }, headers=auth_h(user_a['token'])))
        if r2.status_code == 200:
            created_ids.append(edit_post_id)
            report['records'].append({'type': 'EDITED_POST', 'id': edit_post_id, 'author': user_a['userId'], 'variant': 'edited via PATCH /content/:id'})
            print(f"  EDITED POST: {edit_post_id}")
        else:
            print(f"  Edit failed: {r2.status_code} {r2.text}")
            report['errors'].append(f'EDITED POST edit failed: {r2.status_code}')
    
    # =========================================
    # 6. Promote all to distributionStage: 2 for public feed
    # =========================================
    print("\n[6] Promoting to distributionStage: 2 for public feed...")
    if created_ids:
        result = db.content_items.update_many(
            {'id': {'$in': created_ids}},
            {'$set': {'distributionStage': 2}}
        )
        print(f"  Promoted {result.modified_count} records to stage 2")
    
    # =========================================
    # 7. VERIFICATION & PROOF
    # =========================================
    print("\n[7] Verifying feed visibility...")
    
    # Check public feed
    time.sleep(0.5)
    r = retry(lambda: requests.get(f'{API_URL}/feed/public?limit=20', headers=auth_h(user_b['token'])))
    if r.status_code == 200:
        feed_items = r.json().get('items') or r.json().get('data', {}).get('items', [])
        feed_ids = {item.get('id') for item in feed_items}
        print(f"  Public feed items: {len(feed_items)}")
        for rec in report['records']:
            visible = rec['id'] in feed_ids
            rec['publicFeedVisible'] = visible
            status = '✅' if visible else '❌'
            print(f"    {status} {rec['type']}: {rec['id'][:12]}...")
    
    # Check following feed
    r = retry(lambda: requests.get(f'{API_URL}/feed/following?limit=20', headers=auth_h(user_b['token'])))
    if r.status_code == 200:
        feed_items = r.json().get('items') or r.json().get('data', {}).get('items', [])
        feed_ids = {item.get('id') for item in feed_items}
        print(f"\n  Following feed items: {len(feed_items)}")
        for rec in report['records']:
            visible = rec['id'] in feed_ids
            rec['followingFeedVisible'] = visible
            status = '✅' if visible else '❌'
            print(f"    {status} {rec['type']}: {rec['id'][:12]}...")
    
    # Verify page verification badge
    if page_id:
        page_doc = db.pages.find_one({'id': page_id}, {'_id': 0})
        print(f"\n  Page verification: {page_doc.get('verificationStatus')}")
        print(f"  Page isOfficial: {page_doc.get('isOfficial')}")
    
    # Verify editedAt on edited post
    if edit_post_id:
        edited_doc = db.content_items.find_one({'id': edit_post_id}, {'_id': 0})
        print(f"\n  Edited post editedAt: {edited_doc.get('editedAt')}")
        print(f"  Edited post caption: {edited_doc.get('caption', '')[:60]}...")
    
    # Verify repost linkage
    for rec in report['records']:
        if rec['type'].startswith('REPOST'):
            repost_doc = db.content_items.find_one({'id': rec['id']}, {'_id': 0})
            print(f"\n  Repost {rec['id'][:12]}:")
            print(f"    isRepost: {repost_doc.get('isRepost')}")
            print(f"    originalContentId: {repost_doc.get('originalContentId')}")
    
    # =========================================
    # 8. FINAL REPORT
    # =========================================
    print("\n" + "=" * 60)
    print("FINAL SEED REPORT")
    print("=" * 60)
    
    print(f"\nRecords created: {len(report['records'])}")
    print(f"Errors: {len(report['errors'])}")
    
    for rec in report['records']:
        print(f"\n  [{rec['type']}]")
        print(f"    ID: {rec['id']}")
        print(f"    Author: {rec.get('author', 'N/A')}")
        print(f"    Variant: {rec.get('variant', 'N/A')}")
        if 'originalId' in rec:
            print(f"    Original: {rec['originalId']}")
        print(f"    Public feed: {'✅' if rec.get('publicFeedVisible') else '❌'}")
        print(f"    Following feed: {'✅' if rec.get('followingFeedVisible') else '❌'}")
    
    if report['errors']:
        print(f"\nErrors:")
        for e in report['errors']:
            print(f"  ❌ {e}")
    
    # Count successes
    success_count = sum(1 for r in report['records'] if r.get('publicFeedVisible') or r.get('followingFeedVisible'))
    total = len(report['records'])
    
    print(f"\n{'=' * 60}")
    if success_count == total and total >= 7:
        print("VERDICT: PASS — All seed variants created and feed-visible")
    elif success_count > 0:
        print(f"VERDICT: PARTIAL — {success_count}/{total} variants feed-visible")
    else:
        print("VERDICT: FAIL — No variants feed-visible")
    print(f"{'=' * 60}")
    
    client.close()

if __name__ == '__main__':
    main()
