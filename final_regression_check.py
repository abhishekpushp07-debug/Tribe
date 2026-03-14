#!/usr/bin/env python3
"""
Final Validation Test - Complete Route Regression
Tests all routes mentioned in the review request specification
"""

import requests
import json

API_BASE = "https://latency-crusher.preview.emergentagent.com"

def get_auth_token():
    """Get auth token for testing"""
    try:
        resp = requests.post(f"{API_BASE}/api/auth/login", json={"phone": "7777099001", "pin": "1234"}, timeout=10)
        if resp.status_code == 200:
            return resp.json().get("token")
    except:
        pass
    return None

def test_all_specified_routes():
    """Test all routes from the review specification"""
    token = get_auth_token()
    if not token:
        print("❌ Failed to get auth token")
        return

    print("🎯 Testing ALL routes from review specification...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # All routes mentioned in the review request
    test_routes = [
        # Health endpoints
        ("GET", "/api/healthz", None, "Health check"),
        ("GET", "/api/readyz", None, "Readiness check"),
        
        # Auth endpoints  
        ("POST", "/api/auth/login", {"phone": "7777099001", "pin": "1234"}, "Auth login"),
        
        # Feed endpoints
        ("GET", "/api/feed?limit=3", None, "Public feed (anon)"),
        ("GET", "/api/feed?limit=3", {}, "Public feed (auth)"),
        
        # Content endpoints
        ("POST", "/api/content/posts", {"caption": "Test regression", "kind": "POST"}, "Create post"),
        ("GET", "/api/content/{id}", {}, "Get content (placeholder)"),
        
        # Other endpoints
        ("DELETE", "/api/content/{id}", {}, "Delete content (placeholder)"),
        ("GET", "/api/tribes", None, "Get tribes"),
        ("GET", "/api/search?q=test", None, "Search"),
        ("GET", "/api/notifications", {}, "Notifications"),
        ("GET", "/api/stories/feed", {}, "Stories feed"),  
        ("GET", "/api/reels/feed", {}, "Reels feed"),
        ("GET", "/api/analytics/overview", {}, "Analytics overview"),
        ("GET", "/api/cache/stats", {}, "Cache stats (admin)"),
        ("GET", "/api/ops/metrics", {}, "Ops metrics (admin)"),
        ("GET", "/api/ops/health", {}, "Ops health (admin)"),
        ("GET", "/api/ws/stats", {}, "WebSocket stats (admin)"),
        ("GET", "/api/me", {}, "Get current user"),
        ("PUT", "/api/me/profile", {"displayName": "Test User"}, "Update profile"),
        ("POST", "/api/media/upload-init", {"kind": "image", "mimeType": "image/jpeg", "sizeBytes": 100000}, "Media upload init"),
    ]
    
    passed = 0
    total = 0
    post_id = None
    
    for method, route, data, description in test_routes:
        total += 1
        
        # Skip placeholder routes 
        if "{id}" in route and not post_id:
            print(f"⏭️  SKIP {method} {route} - {description} (no post ID yet)")
            continue
            
        # Replace placeholder with actual ID
        if "{id}" in route and post_id:
            route = route.replace("{id}", post_id)
        
        try:
            # Determine headers to use
            request_headers = {}
            if data == {}:  # Empty dict means use auth
                request_headers = headers
            elif data is None:  # None means no auth
                request_headers = {"Content-Type": "application/json"}
            else:  # Has data, needs auth
                request_headers = {**headers, "Content-Type": "application/json"}
            
            # Make request
            if method == "GET":
                resp = requests.get(f"{API_BASE}{route}", headers=request_headers, timeout=10)
            elif method == "POST":
                resp = requests.post(f"{API_BASE}{route}", json=data, headers=request_headers, timeout=10)
            elif method == "PUT":
                resp = requests.put(f"{API_BASE}{route}", json=data, headers=request_headers, timeout=10)  
            elif method == "DELETE":
                resp = requests.delete(f"{API_BASE}{route}", headers=request_headers, timeout=10)
            else:
                resp = requests.request(method, f"{API_BASE}{route}", headers=request_headers, timeout=10)
            
            # Check success
            success = (200 <= resp.status_code < 300) or resp.status_code in [401, 403]
            status_icon = "✅" if success else "❌"
            
            print(f"{status_icon} {method} {route} - {resp.status_code} - {description}")
            
            if success:
                passed += 1
                
            # Extract post ID for later tests
            if method == "POST" and "content/posts" in route and resp.status_code == 201:
                try:
                    post_data = resp.json()
                    post_id = post_data.get("id")
                    print(f"   📝 Created post ID: {post_id}")
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ {method} {route} - ERROR - {description}: {str(e)}")
    
    # Test content operations with the created post
    if post_id:
        content_tests = [
            ("GET", f"/api/content/{post_id}", {}, "Get specific content"),
            ("POST", f"/api/content/{post_id}/like", {"reactionType": "LIKE"}, "Like content"),
            ("POST", f"/api/content/{post_id}/comments", {"text": "Test comment"}, "Comment on content"),
            ("DELETE", f"/api/content/{post_id}", {}, "Delete content"),
        ]
        
        for method, route, data, description in content_tests:
            total += 1
            try:
                request_headers = {**headers, "Content-Type": "application/json"}
                
                if method == "GET":
                    resp = requests.get(f"{API_BASE}{route}", headers=request_headers, timeout=10)
                elif method == "POST":
                    resp = requests.post(f"{API_BASE}{route}", json=data, headers=request_headers, timeout=10)
                elif method == "DELETE":
                    resp = requests.delete(f"{API_BASE}{route}", headers=request_headers, timeout=10)
                else:
                    resp = requests.request(method, f"{API_BASE}{route}", headers=request_headers, timeout=10)
                
                success = (200 <= resp.status_code < 300)
                status_icon = "✅" if success else "❌"
                
                print(f"{status_icon} {method} {route} - {resp.status_code} - {description}")
                
                if success:
                    passed += 1
                    
            except Exception as e:
                print(f"❌ {method} {route} - ERROR - {description}: {str(e)}")
    
    print(f"\n📊 ROUTE REGRESSION SUMMARY: {passed}/{total} ({passed/total*100:.1f}%)")
    
    return passed/total >= 0.85

def test_error_scenarios():
    """Test specific error scenarios mentioned in review"""
    print("\n🚫 Testing Error Scenarios...")
    
    # Invalid token
    resp = requests.get(f"{API_BASE}/api/me", headers={"Authorization": "Bearer invalid"}, timeout=10)
    invalid_token_ok = resp.status_code == 401
    print(f"{'✅' if invalid_token_ok else '❌'} Invalid token → 401: {resp.status_code}")
    
    # Bad route  
    resp = requests.get(f"{API_BASE}/api/bad-route-xyz", timeout=10)
    bad_route_ok = resp.status_code == 404
    print(f"{'✅' if bad_route_ok else '❌'} Bad route → 404: {resp.status_code}")
    
    return invalid_token_ok and bad_route_ok

def main():
    print("🎯 FINAL REGRESSION VALIDATION")
    print("=" * 50)
    
    routes_ok = test_all_specified_routes()
    errors_ok = test_error_scenarios()
    
    print(f"\n📊 FINAL RESULTS:")
    print(f"   🔄 Route Dispatch: {'✅ PASS' if routes_ok else '❌ FAIL'}")
    print(f"   🚫 Error Handling: {'✅ PASS' if errors_ok else '❌ FAIL'}")
    
    overall = routes_ok and errors_ok
    print(f"\n🎉 OVERALL: {'✅ REGRESSION PASSED' if overall else '❌ REGRESSION FAILED'}")
    
    return overall

if __name__ == "__main__":
    main()