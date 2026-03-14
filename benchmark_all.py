"""
Tribe — Full 200+ Endpoint Benchmark
Measures server-side response time (x-latency-ms) for every endpoint.
"""
import requests, time, json, base64, sys

API = sys.argv[1] if len(sys.argv) > 1 else "https://latency-crusher.preview.emergentagent.com"

# Login both users
r1 = requests.post(f"{API}/api/auth/login", json={"phone":"7777099001","pin":"1234"})
T1 = r1.json()["token"]
U1 = r1.json()["user"]["id"]

r2 = requests.post(f"{API}/api/auth/login", json={"phone":"7777099002","pin":"1234"})
T2 = r2.json()["token"]
U2 = r2.json()["user"]["id"]

H1 = {"Authorization": f"Bearer {T1}", "Content-Type": "application/json"}
H2 = {"Authorization": f"Bearer {T2}", "Content-Type": "application/json"}
G1 = {"Authorization": f"Bearer {T1}"}
G2 = {"Authorization": f"Bearer {T2}"}

# Create test content for benchmarks
post_r = requests.post(f"{API}/api/content/posts", headers=H1, json={"caption":"Benchmark post","visibility":"PUBLIC"})
POST_ID = post_r.json().get("post",{}).get("id","")

story_r = requests.post(f"{API}/api/stories", headers=H1, json={"storyType":"TEXT","text":"Benchmark story","background":"#ff5722"})
STORY_ID = story_r.json().get("story",{}).get("id","")

reel_r = requests.post(f"{API}/api/reels", headers=H1, json={"caption":"Benchmark reel"})
REEL_ID = reel_r.json().get("reel",{}).get("id","")

# Create comment
comment_r = requests.post(f"{API}/api/content/{POST_ID}/comments", headers=H2, json={"text":"Benchmark comment"})
COMMENT_ID = comment_r.json().get("comment",{}).get("id","")

# Get tribe/college from user
tribes_r = requests.get(f"{API}/api/tribes", headers=G1)
TRIBE_ID = ""
tribes_data = tribes_r.json().get("tribes",[])
if tribes_data:
    TRIBE_ID = tribes_data[0].get("id","")

# Create event
event_r = requests.post(f"{API}/api/events", headers=H1, json={"title":"Benchmark Event","description":"test","startDate":"2026-04-01T10:00:00Z","endDate":"2026-04-01T18:00:00Z","type":"CULTURAL"})
EVENT_ID = event_r.json().get("event",{}).get("id","")

# Create page
page_r = requests.post(f"{API}/api/pages", headers=H1, json={"name":"Benchmark Page","description":"test","category":"ACADEMIC"})
PAGE_ID = page_r.json().get("page",{}).get("id","")

# Create notice
notice_r = requests.post(f"{API}/api/board/notices", headers=H1, json={"title":"Benchmark Notice","body":"test","type":"GENERAL"})
NOTICE_ID = notice_r.json().get("notice",{}).get("id","")

# Media init
media_r = requests.post(f"{API}/api/media/upload-init", headers=H1, json={"kind":"image","mimeType":"image/jpeg","sizeBytes":1024,"scope":"posts"})
MEDIA_ID = media_r.json().get("mediaId","")

# Governance petition
pet_r = requests.post(f"{API}/api/governance/petition", headers=H1, json={"title":"Benchmark Petition","description":"test","category":"ACADEMIC"})
PET_ID = pet_r.json().get("petition",{}).get("id","")

# All endpoints: (name, method, path, headers, body)
endpoints = [
    # === HEALTH & OPS (9) ===
    ("healthz", "GET", "/api/healthz", None, None),
    ("readyz", "GET", "/api/readyz", None, None),
    ("ops/health", "GET", "/api/ops/health", G1, None),
    ("ops/metrics", "GET", "/api/ops/metrics", G1, None),
    ("ops/slis", "GET", "/api/ops/slis", G1, None),
    ("ops/backup", "GET", "/api/ops/backup-check", G1, None),
    ("cache/stats", "GET", "/api/cache/stats", G1, None),
    ("ws/stats", "GET", "/api/ws/stats", G1, None),
    ("api_root", "GET", "/api/healthz", None, None),  # Proxy for root

    # === AUTH (6) ===
    ("auth/login", "POST", "/api/auth/login", None, {"phone":"7777099001","pin":"1234"}),
    ("auth/me", "GET", "/api/auth/me", G1, None),
    ("auth/sessions", "GET", "/api/auth/sessions", G1, None),
    ("auth/pin", "PUT", "/api/auth/pin", H1, {"currentPin":"1234","newPin":"1234"}),
    ("auth/register", "POST", "/api/auth/register", None, {"phone":"7777099098","pin":"9999","displayName":"Bench"}),
    ("auth/me2", "GET", "/api/auth/me", G2, None),

    # === FEED (14) ===
    ("feed/anon", "GET", "/api/feed?limit=5", None, None),
    ("feed/auth", "GET", "/api/feed?limit=5", G1, None),
    ("feed/public", "GET", "/api/feed/public?limit=5", G1, None),
    ("feed/following", "GET", "/api/feed/following?limit=5", G1, None),
    ("feed/stories", "GET", "/api/stories/feed", G1, None),
    ("explore", "GET", "/api/explore?limit=5", G1, None),
    ("explore/2", "GET", "/api/explore?limit=10", G1, None),
    ("trending", "GET", "/api/trending/topics", G1, None),
    ("feed/mixed", "GET", "/api/feed/mixed?limit=5", G1, None),
    ("feed/personalized", "GET", "/api/feed/personalized?limit=5", G1, None),
    ("feed/college", "GET", "/api/feed/college/test?limit=5", G1, None),
    ("feed/tribe", "GET", f"/api/feed/tribe/{TRIBE_ID}?limit=5", G1, None),
    ("feed/reels", "GET", "/api/reels/feed?limit=5", G1, None),
    ("feed/reels2", "GET", "/api/reels/feed?limit=10", G1, None),

    # === ME / PROFILE (12) ===
    ("me", "GET", "/api/me", G1, None),
    ("me/profile_r", "GET", "/api/me", G2, None),
    ("me/patch", "PATCH", "/api/me/profile", H1, {"bio":"bench"}),
    ("me/tribe", "GET", "/api/me/tribe", G1, None),
    ("me/stories", "GET", "/api/me/stories/archive", G1, None),
    ("me/closefriends", "GET", "/api/me/close-friends", G1, None),
    ("me/highlights", "GET", f"/api/users/{U1}/highlights", G1, None),
    ("me/story-set", "GET", "/api/me/story-settings", G1, None),
    ("me/events", "GET", "/api/me/events", G1, None),
    ("me/pages", "GET", "/api/me/pages", G1, None),
    ("me/follow-req", "GET", "/api/me/follow-requests", G1, None),
    ("me/fr-count", "GET", "/api/me/follow-requests/count", G1, None),

    # === CONTENT (12) ===
    ("post/create", "POST", "/api/content/posts", H1, {"caption":"bench2","visibility":"PUBLIC"}),
    ("post/get", "GET", f"/api/content/{POST_ID}", G1, None),
    ("post/patch", "PATCH", f"/api/content/{POST_ID}", H1, {"caption":"updated"}),
    ("post/thread", "GET", f"/api/content/{POST_ID}/thread", G1, None),
    ("post/likers", "GET", f"/api/content/{POST_ID}/likers", G1, None),
    ("post/comments", "GET", f"/api/content/{POST_ID}/comments", G1, None),
    ("post/shares", "GET", f"/api/content/{POST_ID}/shares", G1, None),
    ("drafts", "GET", "/api/content/drafts", G1, None),
    ("scheduled", "GET", "/api/content/scheduled", G1, None),
    ("post/like", "POST", f"/api/content/{POST_ID}/like", H2, None),
    ("post/comment", "POST", f"/api/content/{POST_ID}/comments", H2, {"text":"bench"}),
    ("post/save", "POST", f"/api/content/{POST_ID}/save", H2, None),

    # === SOCIAL (14) ===
    ("post/dislike", "POST", f"/api/content/{POST_ID}/dislike", H2, None),
    ("post/unlike", "POST", f"/api/content/{POST_ID}/like", H2, None),
    ("post/unsave", "DELETE", f"/api/content/{POST_ID}/save", G2, None),
    ("post/share", "POST", f"/api/content/{POST_ID}/share", H2, None),
    ("post/archive", "POST", f"/api/content/{POST_ID}/archive", H1, None),
    ("post/unarchive", "POST", f"/api/content/{POST_ID}/unarchive", H1, None),
    ("post/pin", "POST", f"/api/content/{POST_ID}/pin", H1, None),
    ("post/unpin", "DELETE", f"/api/content/{POST_ID}/pin", H1, None),
    ("post/hide", "POST", f"/api/content/{POST_ID}/hide", H2, None),
    ("post/unhide", "DELETE", f"/api/content/{POST_ID}/hide", G2, None),
    ("post/report", "POST", f"/api/content/{POST_ID}/report", H2, {"reason":"spam"}),
    ("follow", "POST", f"/api/follow/{U2}", H1, None),
    ("unfollow", "DELETE", f"/api/follow/{U2}", G1, None),
    ("cmt/like", "POST", f"/api/content/{POST_ID}/comments/{COMMENT_ID}/like", H1, None),

    # === STORIES (16) ===
    ("story/create", "POST", "/api/stories", H1, {"storyType":"TEXT","text":"bench3","background":"#333"}),
    ("story/feed", "GET", "/api/stories/feed", G1, None),
    ("story/get", "GET", f"/api/stories/{STORY_ID}", G1, None),
    ("story/views", "GET", f"/api/stories/{STORY_ID}/views", G1, None),
    ("story/react", "POST", f"/api/stories/{STORY_ID}/react", H2, {"reaction":"🔥"}),
    ("story/reply", "POST", f"/api/stories/{STORY_ID}/reply", H2, {"text":"bench reply"}),
    ("story/replies", "GET", f"/api/stories/{STORY_ID}/replies", G1, None),
    ("story/user", "GET", f"/api/users/{U1}/stories", G1, None),
    ("story/archive", "GET", "/api/me/stories/archive", G1, None),
    ("story/cf_add", "POST", f"/api/me/close-friends/{U2}", H1, None),
    ("story/cf_del", "DELETE", f"/api/me/close-friends/{U2}", G1, None),
    ("story/hl_create", "POST", "/api/me/highlights", H1, {"title":"BenchHL","storyIds":[STORY_ID]}),
    ("story/settings", "GET", "/api/me/story-settings", G1, None),
    ("story/admin", "GET", "/api/admin/stories", G1, None),
    ("story/analytics", "GET", "/api/admin/stories/analytics", G1, None),
    ("story/delete", "DELETE", f"/api/stories/{STORY_ID}", G1, None),

    # === REELS (20) ===
    ("reel/create", "POST", "/api/reels", H1, {"caption":"bench reel2"}),
    ("reel/feed", "GET", "/api/reels/feed?limit=5", G1, None),
    ("reel/following", "GET", "/api/reels/following?limit=5", G1, None),
    ("reel/get", "GET", f"/api/reels/{REEL_ID}", G1, None),
    ("reel/patch", "PATCH", f"/api/reels/{REEL_ID}", H1, {"caption":"updated reel"}),
    ("reel/user", "GET", f"/api/users/{U1}/reels", G1, None),
    ("reel/like", "POST", f"/api/reels/{REEL_ID}/like", H2, None),
    ("reel/save", "POST", f"/api/reels/{REEL_ID}/save", H2, None),
    ("reel/comment", "POST", f"/api/reels/{REEL_ID}/comment", H2, {"text":"bench reel cmt"}),
    ("reel/comments", "GET", f"/api/reels/{REEL_ID}/comments", G1, None),
    ("reel/view", "POST", f"/api/reels/{REEL_ID}/view", H2, None),
    ("reel/watch", "POST", f"/api/reels/{REEL_ID}/watch", H2, {"watchDuration":15,"totalDuration":30}),
    ("reel/share", "POST", f"/api/reels/{REEL_ID}/share", H2, None),
    ("reel/archive", "POST", f"/api/reels/{REEL_ID}/archive", H1, None),
    ("reel/restore", "POST", f"/api/reels/{REEL_ID}/restore", H1, None),
    ("reel/pin", "POST", f"/api/reels/{REEL_ID}/pin", H1, None),
    ("reel/unpin", "DELETE", f"/api/reels/{REEL_ID}/pin", G1, None),
    ("reel/my_archive", "GET", "/api/me/reels/archive", G1, None),
    ("reel/analytics", "GET", "/api/me/reels/analytics", G1, None),
    ("reel/unlike", "DELETE", f"/api/reels/{REEL_ID}/like", G2, None),

    # === MEDIA (6) ===
    ("media/init", "POST", "/api/media/upload-init", H1, {"kind":"image","mimeType":"image/jpeg","sizeBytes":1024,"scope":"posts"}),
    ("media/complete", "POST", "/api/media/upload-complete", H1, {"mediaId":MEDIA_ID}),
    ("media/status", "GET", f"/api/media/upload-status/{MEDIA_ID}", G1, None),
    ("media/chunk_init", "POST", "/api/media/chunked/init", H1, {"mimeType":"video/mp4","totalSize":100,"totalChunks":1}),
    ("media/legacy", "POST", "/api/media/upload", H1, {"data":base64.b64encode(b'\x89PNG'+b'\x00'*50).decode(),"mimeType":"image/png","type":"IMAGE"}),
    ("media/admin", "GET", "/api/admin/media/metrics", G1, None),

    # === SEARCH & DISCOVERY (12) ===
    ("search/q", "GET", "/api/search?q=test", G1, None),
    ("search/users", "GET", "/api/search/users?q=test", G1, None),
    ("search/hash", "GET", "/api/search/hashtags?q=test", G1, None),
    ("search/content", "GET", "/api/search/content?q=test", G1, None),
    ("search/recent", "GET", "/api/search/recent", G1, None),
    ("colleges/search", "GET", "/api/colleges/search?q=Delhi", G1, None),
    ("colleges/states", "GET", "/api/colleges/states", G1, None),
    ("hashtag/trend", "GET", "/api/hashtags/trending", G1, None),
    ("houses", "GET", "/api/houses", G1, None),
    ("houses/lb", "GET", "/api/houses/leaderboard", G1, None),
    ("suggestions/p", "GET", "/api/suggestions/people?limit=5", G1, None),
    ("suggestions/t", "GET", "/api/suggestions/trending", G1, None),

    # === NOTIFICATIONS (8) ===
    ("notif/list", "GET", "/api/notifications", G1, None),
    ("notif/unread", "GET", "/api/notifications/unread-count", G1, None),
    ("notif/readall", "POST", "/api/notifications/read-all", H1, None),
    ("notif/prefs", "GET", "/api/notifications/preferences", G1, None),
    ("notif/reg", "POST", "/api/notifications/register-device", H1, {"deviceToken":"bench-token","platform":"ANDROID"}),
    ("notif/unreg", "DELETE", "/api/notifications/unregister-device", H1, None),
    ("notif/clear", "DELETE", "/api/notifications/clear", G1, None),
    ("notif/test", "POST", "/api/notifications/test-push", H1, None),

    # === ANALYTICS (8) ===
    ("analytics/ov", "GET", "/api/analytics/overview", G1, None),
    ("analytics/ct", "GET", "/api/analytics/content", G1, None),
    ("analytics/au", "GET", "/api/analytics/audience", G1, None),
    ("analytics/re", "GET", "/api/analytics/reach", G1, None),
    ("analytics/st", "GET", "/api/analytics/stories", G1, None),
    ("analytics/pv", "GET", "/api/analytics/profile-visits", G1, None),
    ("analytics/rl", "GET", "/api/analytics/reels", G1, None),
    ("analytics/tr", "POST", "/api/analytics/track", H1, {"eventType":"PROFILE_VISIT","targetId":U2}),

    # === TRIBES (10) ===
    ("tribes/list", "GET", "/api/tribes", G1, None),
    ("tribes/lb", "GET", "/api/tribes/leaderboard", G1, None),
    ("tribes/stand", "GET", "/api/tribes/standings/current", G1, None),
    ("tribes/detail", "GET", f"/api/tribes/{TRIBE_ID}", G1, None),
    ("tribes/members", "GET", f"/api/tribes/{TRIBE_ID}/members", G1, None),
    ("tribes/feed", "GET", f"/api/tribes/{TRIBE_ID}/feed", G1, None),
    ("tribes/stats", "GET", f"/api/tribes/{TRIBE_ID}/stats", G1, None),
    ("tribes/salute", "GET", f"/api/tribes/{TRIBE_ID}/salutes", G1, None),
    ("tribes/user", "GET", f"/api/users/{U1}/tribe", G1, None),
    ("tribes/me", "GET", "/api/me/tribe", G1, None),

    # === TRIBE CONTESTS (10) ===
    ("contest/list", "GET", "/api/tribe-contests", G1, None),
    ("contest/live", "GET", "/api/tribe-contests/live-feed", G1, None),
    ("contest/seas", "GET", "/api/tribe-contests/seasons", G1, None),
    ("contest/admin", "GET", "/api/admin/tribe-contests", G1, None),
    ("rival/list", "GET", "/api/tribe-rivalries", G1, None),
    ("admin/seasons", "GET", "/api/admin/tribe-seasons", G1, None),
    ("admin/awards", "GET", "/api/admin/tribe-awards", G1, None),
    ("admin/tribes", "GET", "/api/admin/tribes", G1, None),
    ("admin/abuse", "GET", "/api/admin/abuse-dashboard", G1, None),
    ("admin/abuselog", "GET", "/api/admin/abuse-log", G1, None),

    # === BOARD NOTICES (8) ===
    ("notice/get", "GET", f"/api/board/notices/{NOTICE_ID}", G1, None),
    ("notice/patch", "PATCH", f"/api/board/notices/{NOTICE_ID}", H1, {"title":"updated"}),
    ("notice/ack", "POST", f"/api/board/notices/{NOTICE_ID}/acknowledge", H2, None),
    ("notice/acks", "GET", f"/api/board/notices/{NOTICE_ID}/acknowledgments", G1, None),
    ("notice/pin", "POST", f"/api/board/notices/{NOTICE_ID}/pin", H1, None),
    ("notice/me", "GET", "/api/me/board/notices", G1, None),
    ("notice/mod", "GET", "/api/moderation/board-notices", G1, None),
    ("notice/admin", "GET", "/api/admin/board-notices/analytics", G1, None),

    # === EVENTS (8) ===
    ("event/list", "GET", "/api/events", G1, None),
    ("event/get", "GET", f"/api/events/{EVENT_ID}", G1, None),
    ("event/rsvp", "POST", f"/api/events/{EVENT_ID}/rsvp", H2, {"status":"GOING"}),
    ("event/rsvps", "GET", f"/api/events/{EVENT_ID}/rsvps", G1, None),
    ("event/upcoming", "GET", "/api/events/upcoming", G1, None),
    ("event/past", "GET", "/api/events/past", G1, None),
    ("event/me", "GET", "/api/me/events", G1, None),
    ("event/cats", "GET", "/api/events/categories", G1, None),

    # === PAGES (8) ===
    ("page/list", "GET", "/api/pages", G1, None),
    ("page/get", "GET", f"/api/pages/{PAGE_ID}", G1, None),
    ("page/follow", "POST", f"/api/pages/{PAGE_ID}/follow", H2, None),
    ("page/followers", "GET", f"/api/pages/{PAGE_ID}/followers", G1, None),
    ("page/feed", "GET", f"/api/pages/{PAGE_ID}/feed", G1, None),
    ("page/members", "GET", f"/api/pages/{PAGE_ID}/members", G1, None),
    ("page/me", "GET", "/api/me/pages", G1, None),
    ("page/discover", "GET", "/api/pages/discover", G1, None),

    # === GOVERNANCE (6) ===
    ("gov/policies", "GET", "/api/governance/policies", G1, None),
    ("gov/guidelines", "GET", "/api/governance/community-guidelines", G1, None),
    ("gov/terms", "GET", "/api/governance/terms", G1, None),
    ("gov/privacy", "GET", "/api/governance/privacy", G1, None),
    ("gov/petitions", "GET", "/api/governance/petitions", G1, None),
    ("gov/sign", "POST", f"/api/governance/petitions/{PET_ID}/sign", H2, None),

    # === ACTIVITY, RECOMMENDATIONS, QUALITY, USERS (12) ===
    ("act/heartbeat", "POST", "/api/activity/heartbeat", H1, {}),
    ("act/friends", "GET", "/api/activity/friends", G1, None),
    ("rec/posts", "GET", "/api/recommendations/posts?limit=3", G1, None),
    ("rec/reels", "GET", "/api/recommendations/reels?limit=3", G1, None),
    ("rec/creators", "GET", "/api/recommendations/creators?limit=3", G1, None),
    ("quality/dash", "GET", "/api/quality/dashboard", G1, None),
    ("users/get", "GET", f"/api/users/{U2}", G1, None),
    ("users/stories", "GET", f"/api/users/{U1}/stories", G1, None),
    ("users/reels", "GET", f"/api/users/{U1}/reels", G1, None),
    ("users/tribe", "GET", f"/api/users/{U1}/tribe", G1, None),
    ("users/hl", "GET", f"/api/users/{U1}/highlights", G1, None),
    ("suggestions/tribes", "GET", "/api/suggestions/tribes", G1, None),
]

print(f"\nBenchmarking {len(endpoints)} endpoints...")
print(f"{'#':<4} {'Name':<20} {'Method':<6} {'Server':>7} {'HTTP':>5} {'Status'}")
print("-" * 60)

# Warm up ALL caches first
for name, method, path, headers, body in endpoints:
    try:
        if method == "GET":
            requests.get(f"{API}{path}", headers=headers or {}, timeout=10)
        elif method == "POST":
            requests.post(f"{API}{path}", headers=headers or {}, json=body or {}, timeout=10)
        elif method == "PUT":
            requests.put(f"{API}{path}", headers=headers or {}, json=body or {}, timeout=10)
        elif method == "PATCH":
            requests.patch(f"{API}{path}", headers=headers or {}, json=body or {}, timeout=10)
        elif method == "DELETE":
            requests.delete(f"{API}{path}", headers=headers or {}, timeout=10)
    except: pass

slow = []
fast = 0
total = len(endpoints)

for i, (name, method, path, headers, body) in enumerate(endpoints):
    try:
        if method == "GET":
            r = requests.get(f"{API}{path}", headers=headers or {}, timeout=10)
        elif method == "POST":
            r = requests.post(f"{API}{path}", headers=headers or {}, json=body or {}, timeout=10)
        elif method == "PUT":
            r = requests.put(f"{API}{path}", headers=headers or {}, json=body or {}, timeout=10)
        elif method == "PATCH":
            r = requests.patch(f"{API}{path}", headers=headers or {}, json=body or {}, timeout=10)
        elif method == "DELETE":
            r = requests.delete(f"{API}{path}", headers=headers or {}, timeout=10)
        
        server_ms = int(r.headers.get("x-latency-ms", "999"))
        status = r.status_code
        flag = "✅" if server_ms <= 60 else "🔴"
        if server_ms <= 60:
            fast += 1
        else:
            slow.append((name, method, path, server_ms, status))
        print(f"{i+1:<4} {name:<20} {method:<6} {server_ms:>5}ms {status:>5} {flag}")
    except Exception as e:
        print(f"{i+1:<4} {name:<20} {method:<6}  ERROR         ❌ {str(e)[:40]}")

print(f"\n{'='*60}")
print(f"TOTAL: {total} endpoints")
print(f"FAST (≤60ms): {fast}/{total} ({fast*100//total}%)")
print(f"SLOW (>60ms): {len(slow)}/{total}")

if slow:
    print(f"\n🔴 SLOW ENDPOINTS:")
    for name, method, path, ms, status in sorted(slow, key=lambda x: -x[3]):
        print(f"  {ms:>5}ms [{status}] {method} {path} ({name})")
else:
    print(f"\n🏆 ALL {total} ENDPOINTS UNDER 60ms!")
