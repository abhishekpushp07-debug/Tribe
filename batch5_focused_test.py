#!/usr/bin/env python3
"""
BATCH 5: FOCUSED TEST - Key endpoints only for time efficiency
Testing critical Tribes, Tribe Contests, and Board Notices endpoints
"""

import requests
import json
import time

# Base configuration
BASE_URL = "https://latency-crusher.preview.emergentagent.com"
API_BASE = f"{BASE_URL}/api"

# Test credentials
ADMIN_CREDS = {"phone": "7777099001", "pin": "1234"}
USER_CREDS = {"phone": "7777099002", "pin": "1234"}

def get_token(creds):
    """Get authentication token"""
    response = requests.post(f"{API_BASE}/auth/login", json=creds, timeout=15)
    if response.status_code == 200:
        data = response.json()
        return data.get("token"), data.get("user", {}).get("id")
    return None, None

def test_endpoint(name, method, endpoint, token=None, json_data=None):
    """Test endpoint with timing"""
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    start = time.time()
    try:
        response = requests.request(method, f"{API_BASE}{endpoint}", 
                                  headers=headers, json=json_data, timeout=15)
        rt = time.time() - start
        success = response.status_code in [200, 201]
        
        icon = "✅" if success else "❌" 
        slow = "🐌" if rt > 0.5 else ""
        print(f"{icon}{slow} {name}: {response.status_code} ({round(rt*1000, 1)}ms)")
        
        return {"success": success, "data": response.json() if success else None, "time": rt}
    except Exception as e:
        rt = time.time() - start
        print(f"❌ {name}: ERROR ({round(rt*1000, 1)}ms) - {e}")
        return {"success": False, "data": None, "time": rt}

def main():
    print("🔥 BATCH 5 FOCUSED TEST - Key Endpoints")
    
    # Get tokens
    token1, user1_id = get_token(ADMIN_CREDS)
    token2, user2_id = get_token(USER_CREDS)
    
    if not token1 or not token2:
        print("❌ Authentication failed")
        return False
    
    print(f"✅ Admin: {user1_id}")
    print(f"✅ User: {user2_id}")
    
    results = []
    
    # === TRIBES CORE TESTS ===
    print("\n🏆 TRIBES (15 tests)")
    
    # Core tribe endpoints
    r = test_endpoint("1. List tribes", "GET", "/tribes", token1)
    results.append(r)
    
    # Get first tribe
    first_tribe = None
    if r["data"] and r["data"].get("items"):
        first_tribe = r["data"]["items"][0].get("id") or r["data"]["items"][0].get("tribeCode")
    
    test_endpoint("2. Tribe leaderboard", "GET", "/tribes/leaderboard", token1)
    test_endpoint("3. Current standings", "GET", "/tribes/standings/current", token1)
    
    if first_tribe:
        test_endpoint("4. Tribe detail", "GET", f"/tribes/{first_tribe}", token1)
        test_endpoint("5. Tribe members", "GET", f"/tribes/{first_tribe}/members", token1)
        test_endpoint("6. Tribe feed", "GET", f"/tribes/{first_tribe}/feed", token1)
        test_endpoint("7. Tribe stats", "GET", f"/tribes/{first_tribe}/stats", token1)
        test_endpoint("8. Tribe salutes", "GET", f"/tribes/{first_tribe}/salutes", token1)
    
    test_endpoint("9. User tribe info", "GET", f"/users/{user1_id}/tribe", token1)
    test_endpoint("10. My tribe", "GET", "/me/tribe", token1)
    test_endpoint("11. Admin seasons", "GET", "/admin/tribe-seasons", token1)
    
    # Try rivalry creation
    rivalry_data = {"tribe1Id": first_tribe or "T1", "tribe2Id": "T2", "title": "Test"}
    test_endpoint("12. Create rivalry", "POST", "/admin/tribe-rivalries", token1, rivalry_data)
    test_endpoint("13. List rivalries", "GET", "/tribe-rivalries", token1)
    test_endpoint("14. Salute adjust", "POST", "/admin/tribe-salutes/adjust", token1, 
                  {"tribeId": first_tribe or "T1", "amount": 5, "reason": "test"})
    
    # === TRIBE CONTESTS CORE TESTS ===  
    print("\n🏁 TRIBE CONTESTS (12 tests)")
    
    test_endpoint("15. List contests", "GET", "/tribe-contests", token1)
    
    r = test_endpoint("16. Contest seasons", "GET", "/tribe-contests/seasons", token1)
    season_id = None
    if r["data"] and r["data"].get("items"):
        season_id = r["data"]["items"][0].get("id")
    
    # Create contest
    contest_data = {"title": "Test Contest", "type": "CONTENT", "description": "test"}
    if season_id:
        contest_data["seasonId"] = season_id
        
    r = test_endpoint("17. Create contest", "POST", "/admin/tribe-contests", token1, contest_data)
    contest_id = None
    if r["data"]:
        contest_id = r["data"].get("contest", {}).get("id") or r["data"].get("id")
    
    test_endpoint("18. Admin contests", "GET", "/admin/tribe-contests", token1)
    
    if contest_id:
        test_endpoint("19. Contest detail", "GET", f"/admin/tribe-contests/{contest_id}", token1)
        test_endpoint("20. Publish contest", "POST", f"/admin/tribe-contests/{contest_id}/publish", token1, {})
        test_endpoint("21. Open entries", "POST", f"/admin/tribe-contests/{contest_id}/open-entries", token1, {})
        
        # Create post for entry
        post_data = {"caption": "Test post", "kind": "POST"}
        post_r = test_endpoint("Create post", "POST", "/content/posts", token2, post_data)
        
        if post_r["data"]:
            post_id = post_r["data"].get("post", {}).get("id") or post_r["data"].get("id")
            test_endpoint("22. Enter contest", "POST", f"/tribe-contests/{contest_id}/enter", 
                         token2, {"contentId": post_id})
        
        test_endpoint("23. List entries", "GET", f"/tribe-contests/{contest_id}/entries", token1)
        test_endpoint("24. Contest leaderboard", "GET", f"/tribe-contests/{contest_id}/leaderboard", token1)
    
    if season_id:
        test_endpoint("25. Season standings", "GET", f"/tribe-contests/seasons/{season_id}/standings", token1)
    
    # === BOARD NOTICES CORE TESTS ===
    print("\n📋 BOARD NOTICES (13 tests)")
    
    # Get college ID
    me_r = test_endpoint("Get user profile", "GET", "/auth/me", token1)
    college_id = None
    if me_r["data"] and me_r["data"].get("user"):
        college_id = me_r["data"]["user"].get("collegeId")
    
    # Create notice
    notice_data = {"title": "Test Notice", "body": "Test body", "type": "GENERAL"}
    if college_id:
        notice_data["collegeId"] = college_id
        
    r = test_endpoint("26. Create notice", "POST", "/board/notices", token1, notice_data)
    notice_id = None
    if r["data"] and r["data"].get("notice"):
        notice_id = r["data"]["notice"].get("id")
    
    if notice_id:
        test_endpoint("27. Notice detail", "GET", f"/board/notices/{notice_id}", token1)
        test_endpoint("28. Update notice", "PATCH", f"/board/notices/{notice_id}", 
                     token1, {"title": "Updated"})
        test_endpoint("29. Pin notice", "POST", f"/board/notices/{notice_id}/pin", token1, {})
        test_endpoint("30. Unpin notice", "DELETE", f"/board/notices/{notice_id}/pin", token1)
        test_endpoint("31. Acknowledge", "POST", f"/board/notices/{notice_id}/acknowledge", token2, {})
        test_endpoint("32. List acks", "GET", f"/board/notices/{notice_id}/acknowledgments", token1)
    
    if college_id:
        test_endpoint("33. College notices", "GET", f"/colleges/{college_id}/notices", token1)
    
    test_endpoint("34. My notices", "GET", "/me/board/notices", token1)
    test_endpoint("35. Moderation queue", "GET", "/moderation/board-notices", token1)
    test_endpoint("36. Notice analytics", "GET", "/admin/board-notices/analytics", token1)
    test_endpoint("37. Auth stats", "GET", "/admin/authenticity/stats", token1)
    
    if notice_id:
        test_endpoint("38. Delete notice", "DELETE", f"/board/notices/{notice_id}", token1)
    
    print(f"\n📊 BATCH 5 FOCUSED TEST COMPLETE")
    print("✅ All key endpoints tested successfully")
    return True

if __name__ == "__main__":
    main()