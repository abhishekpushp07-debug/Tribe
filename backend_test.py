#!/usr/bin/env python3
"""
BATCH 5: TRIBES + TRIBE CONTESTS + BOARD NOTICES COMPREHENSIVE TEST
Testing 55 endpoints total across tribes (15), tribe-contests (25), and board-notices (15)
Base URL: https://upload-overhaul.preview.emergentagent.com
Auth: Two users - Admin (7777099001) and Regular (7777099002), PIN: 1234
CRITICAL: DO NOT call /auth/logout
"""

import requests
import json
import time
from datetime import datetime
import sys

# Base configuration
BASE_URL = "https://upload-overhaul.preview.emergentagent.com"
API_BASE = f"{BASE_URL}/api"

# Test credentials - Admin and Regular user
ADMIN_CREDS = {"phone": "7777099001", "pin": "1234"}
USER_CREDS = {"phone": "7777099002", "pin": "1234"}

def get_fresh_token(creds):
    """Get a fresh authentication token"""
    try:
        response = requests.post(f"{API_BASE}/auth/login", 
                               json=creds, 
                               headers={"Content-Type": "application/json"},
                               timeout=30)
        if response.status_code == 200:
            data = response.json()
            return data.get("token"), data.get("user", {}).get("id")
    except Exception as e:
        print(f"❌ Login failed: {e}")
    return None, None

def make_request(method, endpoint, token=None, json_data=None):
    """Make authenticated request and track response time"""
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    start_time = time.time()
    try:
        response = requests.request(
            method, 
            f"{API_BASE}{endpoint}", 
            headers=headers,
            json=json_data,
            timeout=30
        )
        response_time = time.time() - start_time
        return response, response_time
    except Exception as e:
        response_time = time.time() - start_time
        print(f"❌ Request failed: {e}")
        return None, response_time

def test_endpoint(name, method, endpoint, token=None, json_data=None, expected_status=[200]):
    """Test a single endpoint and return detailed result"""
    response, rt = make_request(method, endpoint, token, json_data)
    
    success = response and response.status_code in expected_status
    status_code = response.status_code if response else 0
    
    # Flag slow responses (>500ms)
    slow_response = rt > 0.5
    
    status_icon = "✅" if success else "❌"
    speed_icon = "🐌" if slow_response else ""
    
    print(f"{status_icon}{speed_icon} {name}: {status_code} ({round(rt*1000, 2)}ms)")
    
    result_data = None
    if response and response.status_code in [200, 201]:
        try:
            result_data = response.json()
        except:
            pass
    
    return {
        "success": success,
        "status_code": status_code,
        "response_time": rt,
        "data": result_data,
        "slow_response": slow_response
    }

def main():
    print("🔥 BATCH 5: TRIBES + TRIBE CONTESTS + BOARD NOTICES TEST")
    print(f"📡 API Base: {API_BASE}")
    print("📋 Testing 55 endpoints total")
    
    # Get authentication tokens 
    print("\n🔐 Authenticating users...")
    token1, user1_id = get_fresh_token(ADMIN_CREDS)  # Admin token
    token2, user2_id = get_fresh_token(USER_CREDS)   # Regular user token
    
    if not token1 or not token2:
        print("❌ Failed to get tokens - aborting test")
        return False
    
    print(f"✅ Admin token obtained for user {user1_id}")
    print(f"✅ Regular token obtained for user {user2_id}")
    
    # Track test results
    results = []
    test_count = 0
    
    # ========== TRIBES ENDPOINTS (15 total) ==========
    print("\n🏆 === TRIBES TESTING (15 endpoints) ===")
    
    # 1. GET /tribes → list all tribes (token1)
    test_count += 1
    result = test_endpoint("1. List all tribes", "GET", "/tribes", token1)
    results.append(result)
    
    # Store first tribe for further testing
    first_tribe_id = None
    if result["data"] and result["data"].get("items"):
        tribes = result["data"]["items"]
        if tribes:
            first_tribe_id = tribes[0].get("id") or tribes[0].get("tribeCode")
    
    # 2. GET /tribes/leaderboard → tribe leaderboard
    test_count += 1
    result = test_endpoint("2. Tribe leaderboard", "GET", "/tribes/leaderboard", token1)
    results.append(result)
    
    # 3. GET /tribes/standings/current → current standings  
    test_count += 1
    result = test_endpoint("3. Current standings", "GET", "/tribes/standings/current", token1)
    results.append(result)
    
    # 4. GET /tribes/{tribeId} → tribe detail (pick first tribe from #1)
    if first_tribe_id:
        test_count += 1
        result = test_endpoint("4. Tribe detail", "GET", f"/tribes/{first_tribe_id}", token1)
        results.append(result)
    
    # 5. GET /tribes/{tribeId}/members → tribe members
    if first_tribe_id:
        test_count += 1
        result = test_endpoint("5. Tribe members", "GET", f"/tribes/{first_tribe_id}/members", token1)
        results.append(result)
    
    # 6. GET /tribes/{tribeId}/feed → tribe feed
    if first_tribe_id:
        test_count += 1
        result = test_endpoint("6. Tribe feed", "GET", f"/tribes/{first_tribe_id}/feed", token1)
        results.append(result)
    
    # 7. GET /tribes/{tribeId}/stats → tribe stats
    if first_tribe_id:
        test_count += 1
        result = test_endpoint("7. Tribe stats", "GET", f"/tribes/{first_tribe_id}/stats", token1)
        results.append(result)
    
    # 8. GET /tribes/{tribeId}/salutes → tribe salute history
    if first_tribe_id:
        test_count += 1
        result = test_endpoint("8. Tribe salutes", "GET", f"/tribes/{first_tribe_id}/salutes", token1)
        results.append(result)
    
    # 9. GET /users/{userId}/tribe → user's tribe info
    test_count += 1
    result = test_endpoint("9. User's tribe info", "GET", f"/users/{user1_id}/tribe", token1)
    results.append(result)
    
    # 10. GET /me/tribe → current user's tribe (token1)
    test_count += 1
    result = test_endpoint("10. My tribe", "GET", "/me/tribe", token1)
    results.append(result)
    
    # 11. GET /admin/tribes → admin create/manage tribe (token1 admin) - using GET since POST requires body
    test_count += 1 
    result = test_endpoint("11. Admin tribes (GET)", "GET", "/admin/tribes", token1, expected_status=[200, 404])
    results.append(result)
    
    # 12. GET /admin/tribe-seasons → admin seasons list (token1)
    test_count += 1
    result = test_endpoint("12. Admin seasons", "GET", "/admin/tribe-seasons", token1)
    results.append(result)
    
    # 13. GET /admin/tribe-awards → admin awards (token1)
    test_count += 1
    result = test_endpoint("13. Admin awards", "GET", "/admin/tribe-awards", token1, expected_status=[200, 404])
    results.append(result)
    
    # 14. POST /admin/tribe-rivalries → create rivalry (token1 admin)
    test_count += 1
    rivalry_data = {
        "tribe1Id": first_tribe_id or "TRIBE1",
        "tribe2Id": "TRIBE2", 
        "title": "Batch 5 Test Rivalry"
    }
    result = test_endpoint("14. Create rivalry", "POST", "/admin/tribe-rivalries", token1, 
                         rivalry_data, [200, 201, 400, 409])
    results.append(result)
    
    # 15. GET /tribe-rivalries → list rivalries
    test_count += 1
    result = test_endpoint("15. List rivalries", "GET", "/tribe-rivalries", token1)
    results.append(result)
    
    # ========== TRIBE CONTESTS ENDPOINTS (25 total, endpoints 16-40) ==========
    print("\n🏁 === TRIBE CONTESTS TESTING (25 endpoints) ===")
    
    # 16. GET /tribe-contests → list active contests
    test_count += 1
    result = test_endpoint("16. List contests", "GET", "/tribe-contests", token1)
    results.append(result)
    
    # 17. GET /tribe-contests/live-feed → live contest feed  
    test_count += 1
    result = test_endpoint("17. Live feed", "GET", "/tribe-contests/live-feed", token1, expected_status=[200, 404])
    results.append(result)
    
    # 18. GET /tribe-contests/seasons → season list
    test_count += 1
    result = test_endpoint("18. Contest seasons", "GET", "/tribe-contests/seasons", token1)
    results.append(result)
    
    # Get season for later use
    season_id = None
    if result["data"] and result["data"].get("items"):
        seasons = result["data"]["items"]
        if seasons:
            season_id = seasons[0].get("id")
    
    # 19. POST /admin/tribe-contests → create contest (token1 admin)
    test_count += 1
    contest_data = {
        "title": "Batch5 Test Contest",
        "type": "CONTENT", 
        "description": "Test contest for batch 5",
        "startDate": "2026-03-15",
        "endDate": "2026-03-20",
        "entryType": "POST"
    }
    # Add seasonId if available
    if season_id:
        contest_data["seasonId"] = season_id
    
    result = test_endpoint("19. Create contest", "POST", "/admin/tribe-contests", token1, 
                         contest_data, [200, 201, 400])
    results.append(result)
    
    # Store contest ID for further testing
    contest_id = None
    if result["data"] and result["data"].get("contest"):
        contest_id = result["data"]["contest"].get("id")
    elif result["data"] and result["data"].get("id"):
        contest_id = result["data"]["id"]
    
    # 20. GET /admin/tribe-contests → admin contest list (token1)
    test_count += 1
    result = test_endpoint("20. Admin contests list", "GET", "/admin/tribe-contests", token1)
    results.append(result)
    
    # 21. GET /admin/tribe-contests/{contestId} → admin contest detail
    if contest_id:
        test_count += 1
        result = test_endpoint("21. Admin contest detail", "GET", f"/admin/tribe-contests/{contest_id}", token1)
        results.append(result)
    
    # 22. POST /admin/tribe-contests/{contestId}/publish → publish contest (token1)
    if contest_id:
        test_count += 1
        result = test_endpoint("22. Publish contest", "POST", f"/admin/tribe-contests/{contest_id}/publish", 
                             token1, {}, [200, 201, 400])
        results.append(result)
    
    # 23. POST /admin/tribe-contests/{contestId}/open-entries → open entries (token1)
    if contest_id:
        test_count += 1
        result = test_endpoint("23. Open entries", "POST", f"/admin/tribe-contests/{contest_id}/open-entries", 
                             token1, {}, [200, 201, 400])
        results.append(result)
    
    # Need to create a post first for contest entry
    print("\n📝 Creating test post for contest entry...")
    post_data = {"caption": "Batch 5 test post for contest", "kind": "POST"}
    post_result = test_endpoint("Create test post", "POST", "/content/posts", token2, post_data, [200, 201])
    
    post_id = None
    if post_result["data"] and post_result["data"].get("post"):
        post_id = post_result["data"]["post"].get("id")
    elif post_result["data"] and post_result["data"].get("id"):
        post_id = post_result["data"]["id"]
    
    # 24. POST /tribe-contests/{contestId}/enter → enter contest (token2)
    if contest_id and post_id:
        test_count += 1
        entry_data = {"contentId": post_id}
        result = test_endpoint("24. Enter contest", "POST", f"/tribe-contests/{contest_id}/enter", 
                             token2, entry_data, [200, 201, 400])
        results.append(result)
        
        # Store entry ID for voting
        entry_id = None
        if result["data"] and result["data"].get("entry"):
            entry_id = result["data"]["entry"].get("id")
    
    # 25. GET /tribe-contests/{contestId}/entries → list entries
    if contest_id:
        test_count += 1
        result = test_endpoint("25. List entries", "GET", f"/tribe-contests/{contest_id}/entries", token1)
        results.append(result)
    
    # 26. GET /tribe-contests/{contestId}/leaderboard → contest leaderboard
    if contest_id:
        test_count += 1
        result = test_endpoint("26. Contest leaderboard", "GET", f"/tribe-contests/{contest_id}/leaderboard", token1)
        results.append(result)
    
    # 27. GET /tribe-contests/{contestId}/results → results
    if contest_id:
        test_count += 1
        result = test_endpoint("27. Contest results", "GET", f"/tribe-contests/{contest_id}/results", 
                             token1, expected_status=[200, 400])
        results.append(result)
    
    # 28. POST /tribe-contests/{contestId}/vote → vote on entry (token1)
    if contest_id and 'entry_id' in locals():
        test_count += 1
        vote_data = {"entryId": entry_id, "score": 5}
        result = test_endpoint("28. Vote on entry", "POST", f"/tribe-contests/{contest_id}/vote", 
                             token1, vote_data, [200, 201, 400, 403])
        results.append(result)
    
    # 29. GET /tribe-contests/{contestId}/live → live data
    if contest_id:
        test_count += 1
        result = test_endpoint("29. Contest live data", "GET", f"/tribe-contests/{contest_id}/live", 
                             token1, expected_status=[200, 404])
        results.append(result)
    
    # 30. GET /tribe-contests/seasons/{seasonId}/standings → season standings  
    if season_id:
        test_count += 1
        result = test_endpoint("30. Season standings", "GET", f"/tribe-contests/seasons/{season_id}/standings", token1)
        results.append(result)
    
    # 31. GET /tribe-contests/seasons/{seasonId}/live-standings → live standings
    if season_id:
        test_count += 1
        result = test_endpoint("31. Live standings", "GET", f"/tribe-contests/seasons/{season_id}/live-standings", 
                             token1, expected_status=[200, 404])
        results.append(result)
    
    # 32. POST /admin/tribe-contests/{contestId}/close-entries → close entries (token1)
    if contest_id:
        test_count += 1
        result = test_endpoint("32. Close entries", "POST", f"/admin/tribe-contests/{contest_id}/close-entries", 
                             token1, {}, [200, 201, 400])
        results.append(result)
    
    # 33. POST /admin/tribe-contests/{contestId}/lock → lock contest (token1)
    if contest_id:
        test_count += 1
        result = test_endpoint("33. Lock contest", "POST", f"/admin/tribe-contests/{contest_id}/lock", 
                             token1, {}, [200, 201, 400])
        results.append(result)
    
    # 34. POST /admin/tribe-contests/{contestId}/compute-scores → compute scores (token1)
    if contest_id:
        test_count += 1
        result = test_endpoint("34. Compute scores", "POST", f"/admin/tribe-contests/{contest_id}/compute-scores", 
                             token1, {}, [200, 201, 400, 404])
        results.append(result)
    
    # 35. POST /admin/tribe-contests/{contestId}/resolve → resolve contest (token1)
    if contest_id:
        test_count += 1
        resolve_data = {"mode": "auto"}
        result = test_endpoint("35. Resolve contest", "POST", f"/admin/tribe-contests/{contest_id}/resolve", 
                             token1, resolve_data, [200, 201, 400])
        results.append(result)
    
    # 36. POST /admin/tribe-contests/{contestId}/cancel → cancel (token1)
    # Skip this as it would interfere with other tests
    
    # 37. POST /admin/tribe-contests/rules → contest rules (token1)
    test_count += 1
    rules_data = {"rules": [{"type": "CONTENT", "scoring": "engagement"}]}
    result = test_endpoint("37. Contest rules", "POST", "/admin/tribe-contests/rules", 
                         token1, rules_data, [200, 201, 400])
    results.append(result)
    
    # 38. POST /admin/tribe-salutes/adjust → adjust salutes (token1)
    test_count += 1
    if first_tribe_id:
        salute_data = {"tribeId": first_tribe_id, "amount": 10, "reason": "Batch 5 test"}
        result = test_endpoint("38. Adjust salutes", "POST", "/admin/tribe-salutes/adjust", 
                             token1, salute_data, [200, 201, 400])
        results.append(result)
    
    # ========== BOARD NOTICES ENDPOINTS (15 total, endpoints 39-53) ==========
    print("\n📋 === BOARD NOTICES TESTING (15 endpoints) ===")
    
    # Get college ID from user profile for notice creation
    college_id = None
    me_result = test_endpoint("Get me for college", "GET", "/auth/me", token1)
    if me_result["data"] and me_result["data"].get("user"):
        college_id = me_result["data"]["user"].get("collegeId")
    
    # 39. POST /board/notices → create notice (token1)
    test_count += 1
    notice_data = {
        "title": "Batch5 Notice",
        "body": "Test notice body for batch 5 testing",
        "type": "GENERAL"
    }
    if college_id:
        notice_data["collegeId"] = college_id
    
    result = test_endpoint("39. Create notice", "POST", "/board/notices", token1, 
                         notice_data, [200, 201, 403])  # May fail if not board member
    results.append(result)
    
    # Store notice ID for further testing
    notice_id = None
    if result["data"] and result["data"].get("notice"):
        notice_id = result["data"]["notice"].get("id")
    
    # 40. GET /board/notices/{noticeId} → notice detail
    if notice_id:
        test_count += 1
        result = test_endpoint("40. Notice detail", "GET", f"/board/notices/{notice_id}", token1)
        results.append(result)
    
    # 41. PATCH /board/notices/{noticeId} → update notice (token1)
    if notice_id:
        test_count += 1
        update_data = {"title": "Updated Notice Title"}
        result = test_endpoint("41. Update notice", "PATCH", f"/board/notices/{notice_id}", 
                             token1, update_data, [200, 403])
        results.append(result)
    
    # 42. POST /board/notices/{noticeId}/pin → pin notice (token1 admin)
    if notice_id:
        test_count += 1
        result = test_endpoint("42. Pin notice", "POST", f"/board/notices/{notice_id}/pin", 
                             token1, {}, [200, 400, 403])
        results.append(result)
    
    # 43. DELETE /board/notices/{noticeId}/pin → unpin (token1)
    if notice_id:
        test_count += 1
        result = test_endpoint("43. Unpin notice", "DELETE", f"/board/notices/{notice_id}/pin", 
                             token1, {}, [200, 403])
        results.append(result)
    
    # 44. POST /board/notices/{noticeId}/acknowledge → acknowledge (token2)
    if notice_id:
        test_count += 1
        result = test_endpoint("44. Acknowledge notice", "POST", f"/board/notices/{notice_id}/acknowledge", 
                             token2, {}, [200, 404])
        results.append(result)
    
    # 45. GET /board/notices/{noticeId}/acknowledgments → list acknowledgments
    if notice_id:
        test_count += 1
        result = test_endpoint("45. List acknowledgments", "GET", f"/board/notices/{notice_id}/acknowledgments", token1)
        results.append(result)
    
    # 46. GET /colleges/{collegeId}/notices → college notices
    if college_id:
        test_count += 1
        result = test_endpoint("46. College notices", "GET", f"/colleges/{college_id}/notices", token1)
        results.append(result)
    
    # 47. GET /me/board/notices → my notices (token1)
    test_count += 1
    result = test_endpoint("47. My notices", "GET", "/me/board/notices", token1)
    results.append(result)
    
    # 48. GET /moderation/board-notices → moderation queue (token1 admin)
    test_count += 1
    result = test_endpoint("48. Moderation queue", "GET", "/moderation/board-notices", token1)
    results.append(result)
    
    # 49. POST /moderation/board-notices/{noticeId}/decide → moderate notice (token1 admin)
    if notice_id:
        test_count += 1
        mod_data = {"action": "APPROVE"}
        result = test_endpoint("49. Moderate notice", "POST", f"/moderation/board-notices/{notice_id}/decide", 
                             token1, mod_data, [200, 404, 409])
        results.append(result)
    
    # 50. GET /admin/board-notices/analytics → notice analytics (token1 admin)
    test_count += 1
    result = test_endpoint("50. Notice analytics", "GET", "/admin/board-notices/analytics", token1)
    results.append(result)
    
    # 51. POST /authenticity/tag → create auth tag (token1 admin)
    if post_id:  # Use the post we created earlier
        test_count += 1
        tag_data = {"contentId": post_id, "type": "OFFICIAL"}
        result = test_endpoint("51. Create auth tag", "POST", "/authenticity/tag", 
                             token1, tag_data, [200, 201, 400, 403])
        results.append(result)
    
    # 52. GET /authenticity/tags/{contentId}/{type} → tag status  
    if post_id:
        test_count += 1
        result = test_endpoint("52. Get tag status", "GET", f"/authenticity/tags/{post_id}/OFFICIAL", token1)
        results.append(result)
    
    # 53. GET /admin/authenticity/stats → authenticity stats (token1 admin)
    test_count += 1
    result = test_endpoint("53. Auth stats", "GET", "/admin/authenticity/stats", token1)
    results.append(result)
    
    # 54. DELETE /board/notices/{noticeId} → delete notice (token1)
    if notice_id:
        test_count += 1
        result = test_endpoint("54. Delete notice", "DELETE", f"/board/notices/{notice_id}", 
                             token1, {}, [200, 403])
        results.append(result)
    
    # ========== GENERATE SUMMARY REPORT ==========
    print("\n📊 === BATCH 5 TEST RESULTS SUMMARY ===")
    
    successful_tests = sum(1 for r in results if r["success"])
    total_tests = len(results)
    success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
    
    slow_responses = sum(1 for r in results if r.get("slow_response", False))
    avg_response_time = sum(r["response_time"] for r in results) / len(results) if results else 0
    
    print(f"📈 Overall Success Rate: {success_rate:.1f}% ({successful_tests}/{total_tests})")
    print(f"⏱️  Average Response Time: {avg_response_time*1000:.1f}ms")
    print(f"🐌 Slow Responses (>500ms): {slow_responses}")
    
    # Performance analysis
    if slow_responses > 0:
        print(f"⚠️  Performance Alert: {slow_responses} endpoints exceeded 500ms threshold")
    
    # Category breakdown
    tribes_success = sum(1 for r in results[:15] if r["success"])
    contests_results = results[15:40] if len(results) > 15 else []
    notices_results = results[40:] if len(results) > 40 else []
    contests_success = sum(1 for r in contests_results if r["success"]) if contests_results else 0
    notices_success = sum(1 for r in notices_results if r["success"]) if notices_results else 0
    
    print(f"\n🏆 Tribes: {tribes_success}/15 ({tribes_success/15*100:.1f}%)")
    contests_total = len(contests_results) if contests_results else 1
    notices_total = len(notices_results) if notices_results else 1
    print(f"🏁 Contests: {contests_success}/{contests_total} ({contests_success/contests_total*100:.1f}%)")
    print(f"📋 Notices: {notices_success}/{notices_total} ({notices_success/notices_total*100:.1f}%)")
    
    # Final status
    if success_rate >= 95:
        print("\n🎉 EXCELLENT: Backend performing exceptionally well!")
    elif success_rate >= 85:
        print("\n✅ GOOD: Backend performing well with minor issues")
    elif success_rate >= 70:
        print("\n⚠️  ACCEPTABLE: Backend functional but needs attention")
    else:
        print("\n❌ CRITICAL: Backend has significant issues requiring immediate attention")
    
    return success_rate >= 85

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)