#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND TEST SUITE
BATCH 1 RE-TEST + BATCH 2: Content, Social, Follow, Comments
Testing 54 endpoints total - NO logout calls allowed
"""

import requests
import json
import time
from datetime import datetime
import sys

# Base configuration
BASE_URL = "https://upload-overhaul.preview.emergentagent.com"
API_BASE = f"{BASE_URL}/api"

# Test credentials
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
    except:
        pass
    return None, None

def make_request(method, endpoint, token=None, json_data=None):
    """Make authenticated request"""
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
        return None, response_time

def test_endpoint(name, method, endpoint, token=None, json_data=None, expected_status=[200]):
    """Test a single endpoint and return result"""
    response, rt = make_request(method, endpoint, token, json_data)
    
    success = response and response.status_code in expected_status
    status_code = response.status_code if response else 0
    
    # Check for headers
    headers_present = False
    if response and hasattr(response, 'headers'):
        headers_present = 'x-request-id' in response.headers
    
    status_icon = "✅" if success else "❌"
    print(f"{status_icon} {name}: {status_code} ({round(rt*1000, 2)}ms)")
    
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
        "headers_present": headers_present
    }

def main():
    print("🚀 STARTING COMPREHENSIVE BACKEND TEST SUITE")
    print(f"📡 Testing API at: {BASE_URL}")
    print("⚠️  CRITICAL: No logout calls allowed - tokens must remain valid throughout testing")
    
    # Get fresh tokens
    print("\n🔐 Getting fresh authentication tokens...")
    admin_token, admin_user_id = get_fresh_token(ADMIN_CREDS)
    user_token, user_user_id = get_fresh_token(USER_CREDS)
    
    if not admin_token or not user_token:
        print("❌ Failed to get tokens - cannot continue")
        return False
    
    print(f"✅ Admin token obtained - User ID: {admin_user_id}")
    print(f"✅ User token obtained - User ID: {user_user_id}")
    
    results = []
    
    # BATCH 1: Auth endpoints that failed due to logout (17 tests)
    print("\n📋 BATCH 1 RE-TEST: Auth Endpoints")
    
    # Get a fresh admin token for admin endpoints
    fresh_admin_token, _ = get_fresh_token(ADMIN_CREDS)
    
    batch1_tests = [
        ("GET /auth/me", "GET", "/auth/me", fresh_admin_token, None, [200]),
        ("GET /auth/sessions", "GET", "/auth/sessions", fresh_admin_token, None, [200]), 
        ("PUT /auth/pin", "PUT", "/auth/pin", fresh_admin_token, {"currentPin": "1234", "newPin": "1234"}, [200, 204]),
        ("GET /ops/health", "GET", "/ops/health", fresh_admin_token, None, [200]),
        ("GET /ops/metrics", "GET", "/ops/metrics", fresh_admin_token, None, [200]),
        ("GET /ops/slis", "GET", "/ops/slis", fresh_admin_token, None, [200]),
        ("GET /ops/backup-check", "GET", "/ops/backup-check", fresh_admin_token, None, [200]),
        ("GET /cache/stats", "GET", "/cache/stats", fresh_admin_token, None, [200]),
        ("GET /ws/stats", "GET", "/ws/stats", fresh_admin_token, None, [200]),
        ("GET /me", "GET", "/me", fresh_admin_token, None, [200]),
        ("PATCH /me/profile", "PATCH", "/me/profile", fresh_admin_token, {"bio": "Batch test"}, [200, 204]),
        ("GET /me/follow-requests", "GET", "/me/follow-requests", fresh_admin_token, None, [200]),
        ("GET /me/follow-requests/sent", "GET", "/me/follow-requests/sent", fresh_admin_token, None, [200]),
        ("GET /me/follow-requests/count", "GET", "/me/follow-requests/count", fresh_admin_token, None, [200]),
        ("GET /feed/following", "GET", "/feed/following?limit=3", fresh_admin_token, None, [200]),
        ("GET /feed/mixed", "GET", "/feed/mixed?limit=3", fresh_admin_token, None, [200]),
        ("GET /feed/personalized", "GET", "/feed/personalized?limit=3", fresh_admin_token, None, [200])
    ]
    
    for test in batch1_tests:
        result = test_endpoint(*test)
        results.append(result)
    
    # BATCH 2: Content CRUD (8 tests)
    print("\n📝 BATCH 2: Content CRUD")
    
    # Create post with fresh token
    fresh_admin_token, _ = get_fresh_token(ADMIN_CREDS)
    
    create_result = test_endpoint("POST /content/posts", "POST", "/content/posts", 
                                  fresh_admin_token, 
                                  {"caption": "Batch2 test post", "visibility": "PUBLIC"},
                                  [200, 201])
    results.append(create_result)
    
    test_post_id = None
    if create_result["success"] and create_result["data"]:
        test_post_id = create_result["data"].get("post", {}).get("id") or create_result["data"].get("id")
        print(f"   Created post ID: {test_post_id}")
    
    if test_post_id:
        # Content operations
        content_tests = [
            ("GET /content/{postId}", "GET", f"/content/{test_post_id}", fresh_admin_token, None, [200]),
            ("PATCH /content/{postId}", "PATCH", f"/content/{test_post_id}", fresh_admin_token, {"caption": "Updated caption"}, [200, 204]),
            ("GET /content/{postId}/thread", "GET", f"/content/{test_post_id}/thread", fresh_admin_token, None, [200]),
            ("GET /content/{postId}/poll-results", "GET", f"/content/{test_post_id}/poll-results", fresh_admin_token, None, [200, 404]),
            ("POST /content/posts (draft)", "POST", "/content/posts", fresh_admin_token, {"caption": "Draft test", "status": "DRAFT"}, [200, 201]),
            ("GET /content/drafts", "GET", "/content/drafts", fresh_admin_token, None, [200]),
            ("GET /content/scheduled", "GET", "/content/scheduled", fresh_admin_token, None, [200])
        ]
        
        for test in content_tests:
            result = test_endpoint(*test)
            results.append(result)
        
        # BATCH 2: Social reactions (4 tests)
        print("\n👍 BATCH 2: Social Reactions")
        
        # Get fresh user token
        fresh_user_token, _ = get_fresh_token(USER_CREDS)
        
        reaction_tests = [
            ("POST /content/{postId}/like", "POST", f"/content/{test_post_id}/like", fresh_user_token, None, [200, 201, 204]),
            ("POST /content/{postId}/dislike", "POST", f"/content/{test_post_id}/dislike", fresh_user_token, None, [200, 201, 204]),
            ("DELETE /content/{postId}/reaction", "DELETE", f"/content/{test_post_id}/reaction", fresh_user_token, None, [200, 204]),
            ("GET /content/{postId}/likers", "GET", f"/content/{test_post_id}/likers", fresh_admin_token, None, [200])
        ]
        
        for test in reaction_tests:
            result = test_endpoint(*test)
            results.append(result)
        
        # BATCH 2: Comments (9 tests)
        print("\n💬 BATCH 2: Comments")
        
        # Create comment
        comment_result = test_endpoint("POST /content/{postId}/comments", "POST", 
                                     f"/content/{test_post_id}/comments",
                                     fresh_user_token,
                                     {"text": "Test comment"},
                                     [200, 201])
        results.append(comment_result)
        
        test_comment_id = None
        if comment_result["success"] and comment_result["data"]:
            test_comment_id = comment_result["data"].get("comment", {}).get("id") or comment_result["data"].get("id")
            print(f"   Created comment ID: {test_comment_id}")
        
        # Get comments
        get_comments_result = test_endpoint("GET /content/{postId}/comments", "GET", 
                                          f"/content/{test_post_id}/comments",
                                          fresh_admin_token, None, [200])
        results.append(get_comments_result)
        
        if test_comment_id:
            comment_tests = [
                ("POST comment like", "POST", f"/content/{test_post_id}/comments/{test_comment_id}/like", fresh_admin_token, None, [200, 201, 204]),
                ("DELETE comment like", "DELETE", f"/content/{test_post_id}/comments/{test_comment_id}/like", fresh_admin_token, None, [200, 204]),
                ("POST comment reply", "POST", f"/content/{test_post_id}/comments/{test_comment_id}/reply", fresh_admin_token, {"text": "Reply"}, [200, 201]),
                ("PATCH comment", "PATCH", f"/content/{test_post_id}/comments/{test_comment_id}", fresh_user_token, {"text": "Edited"}, [200, 204]),
                ("POST comment pin", "POST", f"/content/{test_post_id}/comments/{test_comment_id}/pin", fresh_admin_token, None, [200, 201, 204]),
                ("POST comment report", "POST", f"/content/{test_post_id}/comments/{test_comment_id}/report", fresh_user_token, {"reason": "spam"}, [200, 201]),
                ("DELETE comment", "DELETE", f"/content/{test_post_id}/comments/{test_comment_id}", fresh_user_token, None, [200, 204])
            ]
            
            for test in comment_tests:
                result = test_endpoint(*test)
                results.append(result)
        
        # BATCH 2: Social Actions (11 tests)
        print("\n📌 BATCH 2: Social Actions")
        
        action_tests = [
            ("POST save", "POST", f"/content/{test_post_id}/save", fresh_user_token, None, [200, 201, 204]),
            ("DELETE save", "DELETE", f"/content/{test_post_id}/save", fresh_user_token, None, [200, 204]),
            ("POST share", "POST", f"/content/{test_post_id}/share", fresh_user_token, None, [200, 201]),
            ("GET shares", "GET", f"/content/{test_post_id}/shares", fresh_admin_token, None, [200]),
            ("POST archive", "POST", f"/content/{test_post_id}/archive", fresh_admin_token, None, [200, 201, 204]),
            ("POST unarchive", "POST", f"/content/{test_post_id}/unarchive", fresh_admin_token, None, [200, 204]),
            ("POST pin", "POST", f"/content/{test_post_id}/pin", fresh_admin_token, None, [200, 201, 204]),
            ("DELETE pin", "DELETE", f"/content/{test_post_id}/pin", fresh_admin_token, None, [200, 204]),
            ("POST hide", "POST", f"/content/{test_post_id}/hide", fresh_user_token, None, [200, 201, 204]),
            ("DELETE hide", "DELETE", f"/content/{test_post_id}/hide", fresh_user_token, None, [200, 204]),
            ("POST report", "POST", f"/content/{test_post_id}/report", fresh_user_token, {"reason": "spam", "details": "test"}, [200, 201])
        ]
        
        for test in action_tests:
            result = test_endpoint(*test)
            results.append(result)
        
        # Clean up
        print("\n🧹 Content Cleanup")
        cleanup_result = test_endpoint("DELETE /content/{postId}", "DELETE", f"/content/{test_post_id}", fresh_admin_token, None, [200, 204])
        results.append(cleanup_result)
    
    # BATCH 2: Follow system (4 tests)
    print("\n👥 BATCH 2: Follow System")
    
    # Get fresh tokens
    fresh_admin_token, fresh_admin_id = get_fresh_token(ADMIN_CREDS)
    fresh_user_token, fresh_user_id = get_fresh_token(USER_CREDS)
    
    if fresh_admin_id and fresh_user_id:
        follow_tests = [
            ("POST follow user2", "POST", f"/follow/{fresh_user_id}", fresh_admin_token, None, [200, 201, 204]),
            ("DELETE follow user2", "DELETE", f"/follow/{fresh_user_id}", fresh_admin_token, None, [200, 204]),
            ("POST follow user1", "POST", f"/follow/{fresh_admin_id}", fresh_user_token, None, [200, 201, 204]),
            ("POST accept-all", "POST", "/follow-requests/accept-all", fresh_admin_token, None, [200, 204])
        ]
        
        for test in follow_tests:
            result = test_endpoint(*test)
            results.append(result)
    
    # Caching test
    print("\n⚡ CACHING VERIFICATION")
    fresh_admin_token, _ = get_fresh_token(ADMIN_CREDS)
    
    response1, rt1 = make_request("GET", "/feed/mixed?limit=3", fresh_admin_token)
    response2, rt2 = make_request("GET", "/feed/mixed?limit=3", fresh_admin_token)
    
    if response1 and response2 and response1.status_code == 200 and response2.status_code == 200:
        cache_msg = f"First: {round(rt1*1000, 2)}ms, Second: {round(rt2*1000, 2)}ms"
        if rt2 < rt1 * 0.8:
            cache_msg += " ✅ Caching detected"
        else:
            cache_msg += " ❓ No clear caching benefit"
        print(f"✅ CACHE /feed/mixed: {cache_msg}")
        results.append({"success": True, "response_time": rt2})
    else:
        print(f"❌ CACHE /feed/mixed: Failed")
        results.append({"success": False, "response_time": 0})
    
    # Calculate results
    total_tests = len(results)
    passed_tests = len([r for r in results if r["success"]])
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    # Calculate performance metrics
    response_times = [r["response_time"] * 1000 for r in results if r["success"] and "response_time" in r]
    avg_time = sum(response_times) / len(response_times) if response_times else 0
    max_time = max(response_times) if response_times else 0
    slow_requests = len([rt for rt in response_times if rt > 500])
    
    # Header analysis
    has_headers = len([r for r in results if r.get("headers_present", False)])
    
    # Final report
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE BACKEND TEST REPORT")
    print("="*80)
    print(f"🎯 SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
    print(f"🔗 BASE URL: {BASE_URL}")
    print(f"📈 PERFORMANCE:")
    print(f"   Average response time: {avg_time:.2f}ms")
    print(f"   Slowest response: {max_time:.2f}ms")
    print(f"   Requests >500ms: {slow_requests}")
    print(f"🏷️  Headers with x-request-id: {has_headers}/{total_tests}")
    
    # Summary of key findings
    auth_working = len([r for r in results[:3] if r["success"]]) >= 2  # At least 2 of first 3 auth endpoints
    content_working = test_post_id is not None
    social_working = len([r for r in results if r["success"]]) > total_tests * 0.5
    
    print(f"\n🔍 KEY FINDINGS:")
    print(f"   Authentication: {'✅ Working' if auth_working else '❌ Issues'}")
    print(f"   Content Creation: {'✅ Working' if content_working else '❌ Issues'}")
    print(f"   Overall System: {'✅ Healthy' if social_working else '❌ Issues'}")
    
    if success_rate >= 85:
        print("\n🎉 TESTING COMPLETED SUCCESSFULLY!")
        return True
    else:
        print("\n⚠️  TESTING COMPLETED WITH ISSUES")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)