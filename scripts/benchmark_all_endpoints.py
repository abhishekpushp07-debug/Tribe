#!/usr/bin/env python3
"""
Tribe — Comprehensive API Latency Benchmark
Measures x-latency-ms for ALL endpoints.
Identifies those exceeding 60ms server-side.
"""

import requests
import json
import time
import sys

API_URL = "https://latency-crusher.preview.emergentagent.com/api"
THRESHOLD_MS = 60

results = []

def req(method, path, token=None, body=None, label=None):
    url = f"{API_URL}/{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        if method == "GET":
            r = requests.get(url, headers=headers, timeout=15)
        elif method == "POST":
            r = requests.post(url, headers=headers, json=body or {}, timeout=15)
        elif method == "PATCH":
            r = requests.patch(url, headers=headers, json=body or {}, timeout=15)
        elif method == "DELETE":
            r = requests.delete(url, headers=headers, timeout=15)
        elif method == "PUT":
            r = requests.put(url, headers=headers, json=body or {}, timeout=15)
        else:
            return None

        latency = int(r.headers.get("x-latency-ms", -1))
        status = r.status_code
        name = label or f"{method} /{path}"
        results.append({"name": name, "method": method, "path": path, "status": status, "latency_ms": latency})
        flag = "🔴" if latency > THRESHOLD_MS else "✅"
        print(f"  {flag} {latency:>5}ms [{status}] {name}")
        return r
    except Exception as e:
        name = label or f"{method} /{path}"
        results.append({"name": name, "method": method, "path": path, "status": 0, "latency_ms": -1, "error": str(e)})
        print(f"  ❌    ERR [{name}] {e}")
        return None

# ===== AUTH =====
print("\n===== AUTHENTICATION =====")
r = req("POST", "auth/login", body={"phone": "7777099001", "pin": "1234"}, label="POST /auth/login")
data = r.json() if r else {}
TOKEN = data.get("token", "")
USER_ID = data.get("user", {}).get("id", "")

r2 = req("POST", "auth/login", body={"phone": "7777099002", "pin": "1234"}, label="POST /auth/login (user2)")
TOKEN2 = r2.json().get("token", "") if r2 else ""
USER2_ID = r2.json().get("user", {}).get("id", "") if r2 else ""

req("GET", "auth/me", TOKEN, label="GET /auth/me")
req("POST", "auth/refresh", TOKEN, body={"refreshToken": data.get("refreshToken", "x")}, label="POST /auth/refresh")
req("GET", "auth/sessions", TOKEN, label="GET /auth/sessions")

# ===== HEALTH & OPS =====
print("\n===== HEALTH & OPS =====")
req("GET", "healthz", label="GET /healthz")
req("GET", "readyz", label="GET /readyz")
req("GET", "ops/metrics", TOKEN, label="GET /ops/metrics")
req("GET", "cache/stats", TOKEN, label="GET /cache/stats")

# ===== FEEDS =====
print("\n===== FEEDS =====")
req("GET", "feed", TOKEN, label="GET /feed")
req("GET", "feed/public", TOKEN, label="GET /feed/public")
req("GET", "feed/following", TOKEN, label="GET /feed/following")
req("GET", "feed/college", TOKEN, label="GET /feed/college")
req("GET", "feed/tribe", TOKEN, label="GET /feed/tribe")
req("GET", "feed/personalized", TOKEN, label="GET /feed/personalized")
req("GET", "feed/stories", TOKEN, label="GET /feed/stories")
req("GET", "feed/reels", TOKEN, label="GET /feed/reels")
req("GET", "explore", TOKEN, label="GET /explore")
req("GET", "trending", TOKEN, label="GET /trending")

# ===== CONTENT =====
print("\n===== CONTENT =====")
r_post = req("POST", "content/posts", TOKEN, body={"caption": "Benchmark test post"}, label="POST /content/posts")
post_id = ""
if r_post and r_post.status_code == 201:
    post_id = r_post.json().get("post", {}).get("id", "")

if post_id:
    req("GET", f"content/{post_id}", TOKEN, label="GET /content/:id")
    req("PATCH", f"content/{post_id}", TOKEN, body={"caption": "Updated benchmark"}, label="PATCH /content/:id")
    req("GET", f"content/{post_id}/thread", TOKEN, label="GET /content/:id/thread")

req("GET", "content/drafts", TOKEN, label="GET /content/drafts")
req("GET", "content/scheduled", TOKEN, label="GET /content/scheduled")

# ===== SOCIAL =====
print("\n===== SOCIAL =====")
if post_id:
    req("POST", f"content/{post_id}/like", TOKEN, label="POST /content/:id/like")
    req("GET", f"content/{post_id}/likers", TOKEN, label="GET /content/:id/likers")
    req("POST", f"content/{post_id}/save", TOKEN, label="POST /content/:id/save")
    req("POST", f"content/{post_id}/share", TOKEN, label="POST /content/:id/share")
    req("POST", f"content/{post_id}/hide", TOKEN, label="POST /content/:id/hide")
    req("DELETE", f"content/{post_id}/hide", TOKEN, label="DELETE /content/:id/hide")
    req("POST", f"content/{post_id}/pin", TOKEN, label="POST /content/:id/pin")
    req("DELETE", f"content/{post_id}/pin", TOKEN, label="DELETE /content/:id/pin")
    req("POST", f"content/{post_id}/archive", TOKEN, label="POST /content/:id/archive")
    req("POST", f"content/{post_id}/restore", TOKEN, label="POST /content/:id/restore")
    # Comments
    rc = req("POST", f"content/{post_id}/comments", TOKEN, body={"text": "Benchmark comment"}, label="POST /content/:id/comments")
    comment_id = ""
    if rc and rc.status_code == 201:
        comment_id = rc.json().get("comment", {}).get("id", "")
    req("GET", f"content/{post_id}/comments", TOKEN, label="GET /content/:id/comments")
    if comment_id:
        req("POST", f"content/{post_id}/comments/{comment_id}/like", TOKEN, label="POST /comments/:id/like")
        req("DELETE", f"content/{post_id}/comments/{comment_id}/like", TOKEN, label="DELETE /comments/:id/like")

# Follow
if USER2_ID:
    req("POST", f"follow/{USER2_ID}", TOKEN, label="POST /follow/:userId")
    req("DELETE", f"follow/{USER2_ID}", TOKEN, label="DELETE /follow/:userId")

# ===== USERS =====
print("\n===== USERS =====")
req("GET", f"users/{USER2_ID}", TOKEN, label="GET /users/:id")
req("GET", f"users/{USER2_ID}/posts", TOKEN, label="GET /users/:id/posts")
req("GET", f"users/{USER_ID}/followers", TOKEN, label="GET /users/:id/followers")
req("GET", f"users/{USER_ID}/following", TOKEN, label="GET /users/:id/following")

# ===== ME =====
print("\n===== ME =====")
req("GET", "me/settings", TOKEN, label="GET /me/settings")
req("GET", "me/privacy", TOKEN, label="GET /me/privacy")
req("GET", "me/blocks", TOKEN, label="GET /me/blocks")
req("GET", "me/tribe", TOKEN, label="GET /me/tribe")
req("GET", "me/pages", TOKEN, label="GET /me/pages")
req("GET", "me/stories", TOKEN, label="GET /me/stories")
req("GET", "me/reels", TOKEN, label="GET /me/reels")
req("GET", "me/events", TOKEN, label="GET /me/events")
req("GET", "me/resources", TOKEN, label="GET /me/resources")

# ===== STORIES =====
print("\n===== STORIES =====")
rs = req("POST", "stories", TOKEN, body={"type": "TEXT", "text": "Benchmark story", "background": {"type": "SOLID", "color": "#333"}}, label="POST /stories")
story_id = ""
if rs and rs.status_code == 201:
    story_id = rs.json().get("story", {}).get("id", "")
if story_id:
    req("GET", f"stories/{story_id}", TOKEN, label="GET /stories/:id")
    req("GET", f"stories/{story_id}/viewers", TOKEN, label="GET /stories/:id/viewers")
req("GET", "stories/rail", TOKEN, label="GET /stories/rail")
req("GET", f"users/{USER_ID}/stories", TOKEN, label="GET /users/:id/stories")
req("GET", "me/stories/archive", TOKEN, label="GET /me/stories/archive")
req("GET", "me/stories/insights", TOKEN, label="GET /me/stories/insights")
req("GET", "me/close-friends", TOKEN, label="GET /me/close-friends")
req("GET", "me/highlights", TOKEN, label="GET /me/highlights")
req("GET", "me/story-settings", TOKEN, label="GET /me/story-settings")

# ===== REELS =====
print("\n===== REELS =====")
rr = req("POST", "reels", TOKEN, body={"caption": "Benchmark reel", "mediaUrl": "https://example.com/v.mp4", "durationMs": 10000}, label="POST /reels")
reel_id = ""
if rr and rr.status_code == 201:
    reel_id = rr.json().get("reel", {}).get("id", "")
req("GET", "reels/feed", TOKEN, label="GET /reels/feed")
req("GET", "reels/following", TOKEN, label="GET /reels/following")
req("GET", "reels/trending", TOKEN, label="GET /reels/trending")
if reel_id:
    req("GET", f"reels/{reel_id}", TOKEN, label="GET /reels/:id")
    req("POST", f"reels/{reel_id}/like", TOKEN, label="POST /reels/:id/like")
    req("DELETE", f"reels/{reel_id}/like", TOKEN, label="DELETE /reels/:id/like")
    req("POST", f"reels/{reel_id}/save", TOKEN, label="POST /reels/:id/save")
    req("GET", f"reels/{reel_id}/comments", TOKEN, label="GET /reels/:id/comments")
    req("POST", f"reels/{reel_id}/view", TOKEN, body={"watchTimeMs": 5000}, label="POST /reels/:id/view")
req("GET", "me/reels", TOKEN, label="GET /me/reels (saved)")
req("GET", f"users/{USER_ID}/reels", TOKEN, label="GET /users/:id/reels")

# ===== SEARCH =====
print("\n===== SEARCH =====")
req("GET", "search?q=test", TOKEN, label="GET /search?q=test")
req("GET", "search?q=test&type=users", TOKEN, label="GET /search?q=test&type=users")
req("GET", "search?q=test&type=posts", TOKEN, label="GET /search?q=test&type=posts")
req("GET", "search/autocomplete?q=te", TOKEN, label="GET /search/autocomplete")
req("GET", "search/recent", TOKEN, label="GET /search/recent")
req("GET", "hashtags/trending", TOKEN, label="GET /hashtags/trending")
req("GET", "hashtags/test", TOKEN, label="GET /hashtags/:tag")

# ===== NOTIFICATIONS =====
print("\n===== NOTIFICATIONS =====")
req("GET", "notifications", TOKEN, label="GET /notifications")
req("GET", "notifications/unread-count", TOKEN, label="GET /notifications/unread-count")
req("GET", "notifications/preferences", TOKEN, label="GET /notifications/preferences")

# ===== TRIBES =====
print("\n===== TRIBES =====")
req("GET", "tribes", TOKEN, label="GET /tribes")
req("GET", "tribes/leaderboard", TOKEN, label="GET /tribes/leaderboard")
req("GET", "tribes/standings", TOKEN, label="GET /tribes/standings")
# Get user's tribe
user_data = requests.get(f"{API_URL}/auth/me", headers={"Authorization": f"Bearer {TOKEN}"}).json()
tribe_id = user_data.get("user", {}).get("tribeId", "")
if tribe_id:
    req("GET", f"tribes/{tribe_id}", TOKEN, label="GET /tribes/:id")
    req("GET", f"tribes/{tribe_id}/members", TOKEN, label="GET /tribes/:id/members")
    req("GET", f"tribes/{tribe_id}/feed", TOKEN, label="GET /tribes/:id/feed")
    req("GET", f"tribes/{tribe_id}/stats", TOKEN, label="GET /tribes/:id/stats")
    req("GET", f"tribes/{tribe_id}/salutes", TOKEN, label="GET /tribes/:id/salutes")

# ===== TRIBE CONTESTS =====
print("\n===== TRIBE CONTESTS =====")
req("GET", "tribe-contests", TOKEN, label="GET /tribe-contests")
req("GET", "tribe-contests/seasons", TOKEN, label="GET /tribe-contests/seasons")

# ===== TRIBE RIVALRIES =====
print("\n===== TRIBE RIVALRIES =====")
req("GET", "tribe-rivalries", TOKEN, label="GET /tribe-rivalries")

# ===== PAGES =====
print("\n===== PAGES =====")
req("GET", "pages", TOKEN, label="GET /pages")
rp = req("POST", "pages", TOKEN, body={"name": "BenchmarkPage", "category": "CLUB"}, label="POST /pages")
page_id = ""
if rp and rp.status_code == 201:
    page_id = rp.json().get("page", {}).get("id", "")
if page_id:
    req("GET", f"pages/{page_id}", TOKEN, label="GET /pages/:id")
    req("GET", f"pages/{page_id}/posts", TOKEN, label="GET /pages/:id/posts")
    req("GET", f"pages/{page_id}/members", TOKEN, label="GET /pages/:id/members")
    req("GET", f"pages/{page_id}/followers", TOKEN, label="GET /pages/:id/followers")
    req("GET", f"pages/{page_id}/analytics", TOKEN, label="GET /pages/:id/analytics")
    req("GET", f"pages/{page_id}/reels", TOKEN, label="GET /pages/:id/reels")
    req("GET", f"pages/{page_id}/stories", TOKEN, label="GET /pages/:id/stories")
    req("GET", f"pages/{page_id}/posts/scheduled", TOKEN, label="GET /pages/:id/posts/scheduled")
    req("GET", f"pages/{page_id}/posts/drafts", TOKEN, label="GET /pages/:id/posts/drafts")

# ===== EVENTS =====
print("\n===== EVENTS =====")
req("GET", "events", TOKEN, label="GET /events")
req("GET", "me/events", TOKEN, label="GET /me/events")

# ===== BOARD NOTICES =====
print("\n===== BOARD NOTICES =====")
req("GET", "board/notices", TOKEN, label="GET /board/notices")

# ===== COLLEGES =====
print("\n===== COLLEGES =====")
req("GET", "colleges", TOKEN, label="GET /colleges")

# ===== RESOURCES =====
print("\n===== RESOURCES =====")
req("GET", "resources", TOKEN, label="GET /resources")
req("GET", "resources/search?q=test", TOKEN, label="GET /resources/search")

# ===== ANALYTICS =====
print("\n===== ANALYTICS =====")
req("GET", "analytics/overview", TOKEN, label="GET /analytics/overview")
req("GET", "analytics/content", TOKEN, label="GET /analytics/content")
req("GET", "analytics/audience", TOKEN, label="GET /analytics/audience")
req("GET", "analytics/reach", TOKEN, label="GET /analytics/reach")
req("GET", "analytics/stories", TOKEN, label="GET /analytics/stories")
req("GET", "analytics/reels", TOKEN, label="GET /analytics/reels")

# ===== FOLLOW REQUESTS =====
print("\n===== FOLLOW REQUESTS =====")
req("GET", "follow-requests", TOKEN, label="GET /follow-requests")

# ===== QUALITY =====
print("\n===== QUALITY =====")
req("GET", "quality/dashboard", TOKEN, label="GET /quality/dashboard")

# ===== RECOMMENDATIONS =====
print("\n===== RECOMMENDATIONS =====")
req("GET", "recommendations/users", TOKEN, label="GET /recommendations/users")
req("GET", "recommendations/content", TOKEN, label="GET /recommendations/content")

# ===== ACTIVITY =====
print("\n===== ACTIVITY =====")
req("GET", "activity/status", TOKEN, label="GET /activity/status")

# ===== SUGGESTIONS =====
print("\n===== SUGGESTIONS =====")
req("GET", "suggestions/users", TOKEN, label="GET /suggestions/users")

# ===== GOVERNANCE =====
print("\n===== GOVERNANCE =====")
req("GET", "governance/proposals", TOKEN, label="GET /governance/proposals")

# ===== MEDIA =====
print("\n===== MEDIA =====")
req("POST", "media/upload-init", TOKEN, body={"fileName": "bench.jpg", "fileSize": 1024, "mimeType": "image/jpeg"}, label="POST /media/upload-init")

# ===== ADMIN =====
print("\n===== ADMIN =====")
req("GET", "admin/abuse-dashboard", TOKEN, label="GET /admin/abuse-dashboard")
req("GET", "admin/abuse-log", TOKEN, label="GET /admin/abuse-log")
req("GET", "moderation/config", TOKEN, label="GET /moderation/config")

# ===== AUTHENTICITY =====
print("\n===== AUTHENTICITY =====")
req("GET", "authenticity/stats", TOKEN, label="GET /authenticity/stats")

# ===== TRANSCODE =====
print("\n===== TRANSCODE =====")
req("GET", "transcode/queue", TOKEN, label="GET /transcode/queue")

# Cleanup benchmark post
if post_id:
    req("DELETE", f"content/{post_id}", TOKEN, label="DELETE /content/:id (cleanup)")

# ===== SUMMARY =====
print("\n" + "=" * 70)
print("BENCHMARK SUMMARY")
print("=" * 70)

valid = [r for r in results if r["latency_ms"] >= 0]
slow = [r for r in valid if r["latency_ms"] > THRESHOLD_MS]
fast = [r for r in valid if r["latency_ms"] <= THRESHOLD_MS]

print(f"\nTotal endpoints tested: {len(results)}")
print(f"Valid responses:        {len(valid)}")
print(f"Under {THRESHOLD_MS}ms:            {len(fast)} ✅")
print(f"Over {THRESHOLD_MS}ms:             {len(slow)} 🔴")

if slow:
    print(f"\n🔴 SLOW ENDPOINTS (>{THRESHOLD_MS}ms):")
    slow.sort(key=lambda x: x["latency_ms"], reverse=True)
    for s in slow:
        print(f"  {s['latency_ms']:>5}ms [{s['status']}] {s['name']}")

# Calculate percentiles
if valid:
    latencies = sorted([r["latency_ms"] for r in valid])
    p50 = latencies[len(latencies) // 2]
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[int(len(latencies) * 0.99)]
    avg = sum(latencies) / len(latencies)
    print(f"\nLatency Percentiles:")
    print(f"  avg: {avg:.0f}ms | p50: {p50}ms | p95: {p95}ms | p99: {p99}ms | max: {latencies[-1]}ms")

# Save results
with open("/app/scripts/benchmark_results.json", "w") as f:
    json.dump({"threshold": THRESHOLD_MS, "total": len(results), "valid": len(valid), "slow_count": len(slow), "fast_count": len(fast), "slow_endpoints": slow, "all": results}, f, indent=2)
print(f"\nResults saved to /app/scripts/benchmark_results.json")
