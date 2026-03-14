#!/bin/bash
# Tribe — Full Authenticated Endpoint Benchmark
# Uses curl for accurate x-latency-ms measurement

API="https://latency-crusher.preview.emergentagent.com/api"
THRESHOLD=60
SLOW=()
TOTAL=0
PASS=0
FAIL=0

# Warm the server
curl -s -o /dev/null "$API/healthz"
sleep 1

# Login
TOKEN=$(curl -s -X POST "$API/auth/login" -H "Content-Type: application/json" -d '{"phone":"7777099001","pin":"1234"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
TOKEN2=$(curl -s -X POST "$API/auth/login" -H "Content-Type: application/json" -d '{"phone":"7777099002","pin":"1234"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
USER_ID=$(curl -s "$API/auth/me" -H "Authorization: Bearer $TOKEN" | python3 -c "import sys,json; print(json.load(sys.stdin)['user']['id'])")
USER2_ID=$(curl -s "$API/auth/me" -H "Authorization: Bearer $TOKEN2" | python3 -c "import sys,json; print(json.load(sys.stdin)['user']['id'])")
TRIBE_ID=$(curl -s "$API/auth/me" -H "Authorization: Bearer $TOKEN" | python3 -c "import sys,json; print(json.load(sys.stdin)['user'].get('tribeId',''))")

echo "User1: $USER_ID / User2: $USER2_ID / Tribe: $TRIBE_ID"

bench() {
    local method="$1" path="$2" label="$3" body="$4"
    TOTAL=$((TOTAL+1))
    
    local hdrs="-H 'Authorization: Bearer $TOKEN' -H 'Content-Type: application/json'"
    local cmd="curl -s -D- -o /tmp/bench_body.txt"
    
    if [ "$method" = "GET" ]; then
        resp=$(curl -s -D- -o /tmp/bench_body.txt "$API/$path" -H "Authorization: Bearer $TOKEN" 2>/dev/null)
    elif [ "$method" = "POST" ]; then
        resp=$(curl -s -D- -o /tmp/bench_body.txt -X POST "$API/$path" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "${body:-{}}" 2>/dev/null)
    elif [ "$method" = "PATCH" ]; then
        resp=$(curl -s -D- -o /tmp/bench_body.txt -X PATCH "$API/$path" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "${body:-{}}" 2>/dev/null)
    elif [ "$method" = "DELETE" ]; then
        resp=$(curl -s -D- -o /tmp/bench_body.txt -X DELETE "$API/$path" -H "Authorization: Bearer $TOKEN" 2>/dev/null)
    elif [ "$method" = "PUT" ]; then
        resp=$(curl -s -D- -o /tmp/bench_body.txt -X PUT "$API/$path" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "${body:-{}}" 2>/dev/null)
    fi
    
    local latency=$(echo "$resp" | grep -i "x-latency-ms" | head -1 | tr -d '\r' | awk -F': ' '{print $2}')
    local status=$(echo "$resp" | head -1 | awk '{print $2}')
    
    if [ -z "$latency" ]; then latency="-1"; fi
    
    if [ "$latency" -gt "$THRESHOLD" ] 2>/dev/null; then
        echo "  🔴 ${latency}ms [$status] $label"
        SLOW+=("${latency}ms [$status] $label")
        FAIL=$((FAIL+1))
    else
        echo "  ✅ ${latency}ms [$status] $label"
        PASS=$((PASS+1))
    fi
}

# Helper to get IDs from responses
get_id() {
    python3 -c "import sys,json; print(json.load(sys.stdin).get('$1',{}).get('id',''))" < /tmp/bench_body.txt 2>/dev/null
}

echo ""
echo "===== AUTH (5) ====="
bench POST "auth/login" "POST /auth/login" '{"phone":"7777099001","pin":"1234"}'
bench GET "auth/me" "GET /auth/me"
bench GET "auth/sessions" "GET /auth/sessions"
bench POST "auth/refresh" "POST /auth/refresh" "{\"refreshToken\":\"dummy\"}"
bench GET "auth/login-activity" "GET /auth/login-activity"

echo ""
echo "===== HEALTH & OPS (4) ====="
bench GET "healthz" "GET /healthz"
bench GET "readyz" "GET /readyz"
bench GET "ops/metrics" "GET /ops/metrics"
bench GET "cache/stats" "GET /cache/stats"

echo ""
echo "===== FEEDS (10) ====="
bench GET "feed" "GET /feed"
bench GET "feed" "GET /feed (cached)"
bench GET "feed/public" "GET /feed/public"
bench GET "feed/following" "GET /feed/following"
bench GET "feed/college" "GET /feed/college"
bench GET "feed/tribe" "GET /feed/tribe"
bench GET "feed/personalized" "GET /feed/personalized"
bench GET "feed/stories" "GET /feed/stories"
bench GET "feed/reels" "GET /feed/reels"
bench GET "explore" "GET /explore"

echo ""
echo "===== CONTENT CRUD (8) ====="
bench POST "content/posts" "POST /content/posts (create)" '{"caption":"Bench post"}'
POST_ID=$(get_id post)
bench GET "content/$POST_ID" "GET /content/:id"
bench PATCH "content/$POST_ID" "PATCH /content/:id" '{"caption":"Updated bench"}'
bench GET "content/$POST_ID/thread" "GET /content/:id/thread"
bench GET "content/drafts" "GET /content/drafts"
bench GET "content/scheduled" "GET /content/scheduled"
bench POST "content/posts" "POST /content/posts (poll)" '{"caption":"Poll post","poll":{"options":["A","B"],"expiresIn":24}}'
POLL_ID=$(get_id post)
bench POST "content/$POLL_ID/vote" "POST /content/:id/vote" '{"optionId":"opt_0"}'

echo ""
echo "===== SOCIAL (16) ====="
bench POST "content/$POST_ID/like" "POST /content/:id/like" '{"type":"LIKE"}'
bench GET "content/$POST_ID/likers" "GET /content/:id/likers"
bench POST "content/$POST_ID/dislike" "POST /content/:id/dislike" '{"type":"DISLIKE"}'
bench DELETE "content/$POST_ID/like" "DELETE /content/:id/like"
bench POST "content/$POST_ID/save" "POST /content/:id/save"
bench DELETE "content/$POST_ID/save" "DELETE /content/:id/save"
bench POST "content/$POST_ID/share" "POST /content/:id/share"
bench POST "content/$POST_ID/hide" "POST /content/:id/hide"
bench DELETE "content/$POST_ID/hide" "DELETE /content/:id/hide"
bench POST "content/$POST_ID/pin" "POST /content/:id/pin"
bench DELETE "content/$POST_ID/pin" "DELETE /content/:id/pin"
bench POST "content/$POST_ID/archive" "POST /content/:id/archive"
bench POST "content/$POST_ID/restore" "POST /content/:id/restore"
bench POST "content/$POST_ID/report" "POST /content/:id/report" '{"reason":"spam","category":"SPAM"}'

# Comments
bench POST "content/$POST_ID/comments" "POST /content/:id/comments" '{"text":"Bench comment"}'
CMT_ID=$(get_id comment)
bench GET "content/$POST_ID/comments" "GET /content/:id/comments"

echo ""
echo "===== FOLLOW (4) ====="
bench POST "follow/$USER2_ID" "POST /follow/:userId"
bench DELETE "follow/$USER2_ID" "DELETE /follow/:userId"
bench GET "follow-requests" "GET /follow-requests"
bench POST "follow-requests/accept-all" "POST /follow-requests/accept-all"

echo ""
echo "===== USERS (8) ====="
bench GET "users/$USER2_ID" "GET /users/:id"
bench GET "users/$USER_ID/posts" "GET /users/:id/posts"
bench GET "users/$USER_ID/followers" "GET /users/:id/followers"
bench GET "users/$USER_ID/following" "GET /users/:id/following"
bench GET "users/$USER_ID/stories" "GET /users/:id/stories"
bench GET "users/$USER_ID/reels" "GET /users/:id/reels"
bench GET "users/$USER_ID/highlights" "GET /users/:id/highlights"
bench GET "users/$USER_ID/tribe" "GET /users/:id/tribe"

echo ""
echo "===== ME (18) ====="
bench GET "me/settings" "GET /me/settings"
bench GET "me/privacy" "GET /me/privacy"
bench GET "me/blocks" "GET /me/blocks"
bench GET "me/tribe" "GET /me/tribe"
bench GET "me/pages" "GET /me/pages"
bench GET "me/stories" "GET /me/stories"
bench GET "me/stories/archive" "GET /me/stories/archive"
bench GET "me/stories/insights" "GET /me/stories/insights"
bench GET "me/reels" "GET /me/reels"
bench GET "me/events" "GET /me/events"
bench GET "me/resources" "GET /me/resources"
bench GET "me/close-friends" "GET /me/close-friends"
bench GET "me/highlights" "GET /me/highlights"
bench GET "me/story-settings" "GET /me/story-settings"
bench GET "me/story-mutes" "GET /me/story-mutes"
bench GET "me/board" "GET /me/board"
bench GET "me/college-claims" "GET /me/college-claims"
bench PATCH "me/settings" "PATCH /me/settings" '{"bio":"Bench test"}'

echo ""
echo "===== STORIES (12) ====="
bench POST "stories" "POST /stories (text)" '{"type":"TEXT","text":"Bench story","background":{"type":"SOLID","color":"#333"}}'
STORY_ID=$(get_id story)
if [ -n "$STORY_ID" ]; then
    bench GET "stories/$STORY_ID" "GET /stories/:id"
    bench GET "stories/$STORY_ID/viewers" "GET /stories/:id/viewers"
    bench POST "stories/$STORY_ID/react" "POST /stories/:id/react" '{"emoji":"❤️"}'
    bench POST "stories/$STORY_ID/view" "POST /stories/:id/view"
fi
bench GET "stories/rail" "GET /stories/rail"
bench GET "stories/events/stream?token=$TOKEN" "GET /stories/events/stream" &
STREAM_PID=$!
sleep 0.3
kill $STREAM_PID 2>/dev/null
wait $STREAM_PID 2>/dev/null

echo ""
echo "===== REELS (16) ====="
bench POST "reels" "POST /reels" '{"caption":"Bench reel","mediaUrl":"https://example.com/v.mp4","durationMs":10000}'
REEL_ID=$(get_id reel)
bench GET "reels/feed" "GET /reels/feed"
bench GET "reels/following" "GET /reels/following"
bench GET "reels/trending" "GET /reels/trending"
if [ -n "$REEL_ID" ]; then
    bench GET "reels/$REEL_ID" "GET /reels/:id"
    bench POST "reels/$REEL_ID/like" "POST /reels/:id/like"
    bench DELETE "reels/$REEL_ID/like" "DELETE /reels/:id/like"
    bench POST "reels/$REEL_ID/save" "POST /reels/:id/save"
    bench DELETE "reels/$REEL_ID/save" "DELETE /reels/:id/save"
    bench GET "reels/$REEL_ID/comments" "GET /reels/:id/comments"
    bench POST "reels/$REEL_ID/comments" "POST /reels/:id/comments" '{"text":"Reel comment"}'
    bench POST "reels/$REEL_ID/view" "POST /reels/:id/view" '{"watchTimeMs":5000}'
    bench POST "reels/$REEL_ID/share" "POST /reels/:id/share"
    bench GET "reels/$REEL_ID/analytics" "GET /reels/:id/analytics"
fi

echo ""
echo "===== SEARCH (8) ====="
bench GET "search?q=test" "GET /search?q=test"
bench GET "search?q=test&type=users" "GET /search?type=users"
bench GET "search?q=test&type=posts" "GET /search?type=posts"
bench GET "search?q=test&type=reels" "GET /search?type=reels"
bench GET "search/autocomplete?q=te" "GET /search/autocomplete"
bench GET "search/recent" "GET /search/recent"
bench GET "hashtags/trending" "GET /hashtags/trending"
bench GET "hashtags/test" "GET /hashtags/:tag"

echo ""
echo "===== NOTIFICATIONS (4) ====="
bench GET "notifications" "GET /notifications"
bench GET "notifications/unread-count" "GET /notifications/unread-count"
bench GET "notifications/preferences" "GET /notifications/preferences"
bench POST "notifications/test-push" "POST /notifications/test-push"

echo ""
echo "===== TRIBES (12) ====="
bench GET "tribes" "GET /tribes"
bench GET "tribes/leaderboard" "GET /tribes/leaderboard"
bench GET "tribes/leaderboard?period=7d" "GET /tribes/leaderboard?period=7d"
bench GET "tribes/standings" "GET /tribes/standings"
if [ -n "$TRIBE_ID" ]; then
    bench GET "tribes/$TRIBE_ID" "GET /tribes/:id"
    bench GET "tribes/$TRIBE_ID/members" "GET /tribes/:id/members"
    bench GET "tribes/$TRIBE_ID/feed" "GET /tribes/:id/feed"
    bench GET "tribes/$TRIBE_ID/stats" "GET /tribes/:id/stats"
    bench GET "tribes/$TRIBE_ID/salutes" "GET /tribes/:id/salutes"
    bench POST "tribes/$TRIBE_ID/cheer" "POST /tribes/:id/cheer"
fi

echo ""
echo "===== TRIBE CONTESTS (4) ====="
bench GET "tribe-contests" "GET /tribe-contests"
bench GET "tribe-contests/seasons" "GET /tribe-contests/seasons"

echo ""
echo "===== TRIBE RIVALRIES (2) ====="
bench GET "tribe-rivalries" "GET /tribe-rivalries"

echo ""
echo "===== PAGES (16) ====="
bench GET "pages" "GET /pages"
bench POST "pages" "POST /pages" '{"name":"BenchPage2","category":"CLUB"}'
PAGE_ID=$(get_id page)
if [ -n "$PAGE_ID" ]; then
    bench GET "pages/$PAGE_ID" "GET /pages/:id"
    bench PATCH "pages/$PAGE_ID" "PATCH /pages/:id" '{"bio":"Updated"}'
    bench GET "pages/$PAGE_ID/posts" "GET /pages/:id/posts"
    bench GET "pages/$PAGE_ID/members" "GET /pages/:id/members"
    bench GET "pages/$PAGE_ID/followers" "GET /pages/:id/followers"
    bench GET "pages/$PAGE_ID/analytics" "GET /pages/:id/analytics"
    bench GET "pages/$PAGE_ID/reels" "GET /pages/:id/reels"
    bench GET "pages/$PAGE_ID/stories" "GET /pages/:id/stories"
    bench GET "pages/$PAGE_ID/posts/scheduled" "GET /pages/:id/posts/scheduled"
    bench GET "pages/$PAGE_ID/posts/drafts" "GET /pages/:id/posts/drafts"
    bench POST "pages/$PAGE_ID/posts" "POST /pages/:id/posts" '{"caption":"Page bench post"}'
    PPOST_ID=$(get_id post)
    bench POST "pages/$PAGE_ID/reels" "POST /pages/:id/reels" '{"caption":"Page reel","mediaUrl":"https://example.com/v.mp4"}'
    bench POST "pages/$PAGE_ID/stories" "POST /pages/:id/stories" '{"type":"TEXT","text":"Page story","background":{"type":"SOLID","color":"#000"}}'
fi

echo ""
echo "===== EVENTS (4) ====="
bench POST "events" "POST /events" '{"title":"Bench event","description":"Test","startDate":"2026-04-01T10:00:00Z","endDate":"2026-04-01T12:00:00Z"}'
EVENT_ID=$(get_id event)
bench GET "events" "GET /events"
bench GET "me/events" "GET /me/events"

echo ""
echo "===== BOARD NOTICES (2) ====="
bench GET "board/notices" "GET /board/notices"

echo ""
echo "===== COLLEGES (2) ====="
bench GET "colleges" "GET /colleges"
bench GET "houses" "GET /houses"

echo ""
echo "===== RESOURCES (3) ====="
bench GET "resources" "GET /resources"
bench GET "resources/search?q=test" "GET /resources/search"

echo ""
echo "===== ANALYTICS (6) ====="
bench GET "analytics/overview" "GET /analytics/overview"
bench GET "analytics/content" "GET /analytics/content"
bench GET "analytics/audience" "GET /analytics/audience"
bench GET "analytics/reach" "GET /analytics/reach"
bench GET "analytics/stories" "GET /analytics/stories"
bench GET "analytics/reels" "GET /analytics/reels"

echo ""
echo "===== QUALITY & RECO (4) ====="
bench GET "quality/dashboard" "GET /quality/dashboard"
bench GET "recommendations/users" "GET /recommendations/users"
bench GET "recommendations/content" "GET /recommendations/content"
bench GET "suggestions/users" "GET /suggestions/users"

echo ""
echo "===== ACTIVITY (2) ====="
bench GET "activity/status" "GET /activity/status"
bench POST "activity/heartbeat" "POST /activity/heartbeat"

echo ""
echo "===== GOVERNANCE (2) ====="
bench GET "governance/proposals" "GET /governance/proposals"

echo ""
echo "===== MEDIA (2) ====="
bench POST "media/upload-init" "POST /media/upload-init" '{"fileName":"b.jpg","fileSize":1024,"mimeType":"image/jpeg"}'

echo ""
echo "===== ADMIN (8) ====="
bench GET "admin/abuse-dashboard" "GET /admin/abuse-dashboard"
bench GET "admin/abuse-log" "GET /admin/abuse-log"
bench GET "moderation/config" "GET /moderation/config"
bench GET "moderation/check" "GET /moderation/check"
bench GET "transcode/queue" "GET /transcode/queue"
bench GET "authenticity/stats" "GET /authenticity/stats"
bench GET "admin/stories" "GET /admin/stories"
bench GET "admin/reels" "GET /admin/reels"

# Cleanup
if [ -n "$POST_ID" ]; then
    bench DELETE "content/$POST_ID" "DELETE /content/:id (cleanup)"
fi

echo ""
echo "================================================================"
echo "BENCHMARK COMPLETE"
echo "================================================================"
echo "Total: $TOTAL | Under ${THRESHOLD}ms: $PASS ✅ | Over ${THRESHOLD}ms: $FAIL 🔴"
echo ""
if [ ${#SLOW[@]} -gt 0 ]; then
    echo "🔴 SLOW ENDPOINTS:"
    for s in "${SLOW[@]}"; do
        echo "  $s"
    done
else
    echo "🎉 ALL ENDPOINTS UNDER ${THRESHOLD}ms!"
fi
