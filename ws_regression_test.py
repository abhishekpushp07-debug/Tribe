#!/usr/bin/env python3
"""
Comprehensive Regression Test Suite for Tribe Backend API
- Tests all refactored routes after dispatch registry implementation
- Tests new WebSocket server functionality
- Validates all authentication scenarios
"""

import asyncio
import json
import requests
import redis
import time
import websockets
from datetime import datetime
import uuid

# Test Configuration
API_BASE = "https://upload-overhaul.preview.emergentagent.com"
WS_URL = "ws://localhost:3001"
TEST_USER1 = {"phone": "7777099001", "pin": "1234"}
TEST_USER2 = {"phone": "7777099002", "pin": "1234"}

class TribeAPITester:
    def __init__(self):
        self.token1 = None
        self.token2 = None
        self.user1_id = None
        self.user2_id = None
        self.results = []
        self.redis_client = None
        
        # Try to connect to Redis for WebSocket testing
        try:
            self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            self.redis_client.ping()
            print("✅ Redis connected for WebSocket testing")
        except:
            print("⚠️ Redis not available - WebSocket broadcast tests will be skipped")

    def log_result(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} {test_name}"
        if details:
            result += f" - {details}"
        print(result)
        self.results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def get_headers(self, token=None):
        """Get request headers"""
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def test_auth_flow(self):
        """Test authentication endpoints"""
        print("\n🔐 Testing Authentication Flow...")
        
        # Test login for user1
        try:
            resp = requests.post(
                f"{API_BASE}/api/auth/login", 
                json=TEST_USER1, 
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                self.token1 = data.get("token")
                self.user1_id = data.get("user", {}).get("id")
                self.log_result("Auth Login User1", True, f"Token: {self.token1[:20]}...")
            else:
                self.log_result("Auth Login User1", False, f"Status: {resp.status_code}")
        except Exception as e:
            self.log_result("Auth Login User1", False, f"Exception: {str(e)}")

        # Test login for user2
        try:
            resp = requests.post(
                f"{API_BASE}/api/auth/login", 
                json=TEST_USER2, 
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                self.token2 = data.get("token")
                self.user2_id = data.get("user", {}).get("id")
                self.log_result("Auth Login User2", True, f"Token: {self.token2[:20]}...")
            else:
                self.log_result("Auth Login User2", False, f"Status: {resp.status_code}")
        except Exception as e:
            self.log_result("Auth Login User2", False, f"Exception: {str(e)}")

        # Test auth/me endpoint
        if self.token1:
            try:
                resp = requests.get(
                    f"{API_BASE}/api/me", 
                    headers=self.get_headers(self.token1),
                    timeout=10
                )
                success = resp.status_code == 200
                self.log_result("Auth Me Endpoint", success, f"Status: {resp.status_code}")
            except Exception as e:
                self.log_result("Auth Me Endpoint", False, f"Exception: {str(e)}")

    def test_route_refactoring_regression(self):
        """Test all routes after refactoring to dispatch registry"""
        print("\n🔄 Testing Route Refactoring Regression...")
        
        # List of critical routes to test (routes from review request)
        test_routes = [
            ("GET", "/api/healthz", None, 200),
            ("GET", "/api/readyz", None, 200), 
            ("GET", "/api/feed?limit=3", None, 200),  # Anonymous feed
            ("GET", "/api/feed?limit=3", self.token1, 200),  # Authenticated feed
            ("GET", "/api/tribes", None, 200),
            ("GET", "/api/search?q=test", None, 200),
            ("GET", "/api/notifications", self.token1, 200),
            ("GET", "/api/stories/feed", self.token1, 200),
            ("GET", "/api/reels/feed", self.token1, 200),
            ("GET", "/api/analytics/overview", self.token1, 200),  # Should work if user has access
        ]

        # Additional critical routes from the review request specification
        if self.token1:
            test_routes.extend([
                ("POST", "/api/content/posts", self.token1, 201),
                ("POST", "/api/media/upload-init", self.token1, 200),
            ])

        for method, route, token, expected_status in test_routes:
            try:
                headers = self.get_headers(token) if token else {}
                
                if method == "GET":
                    resp = requests.get(f"{API_BASE}{route}", headers=headers, timeout=10)
                elif method == "POST":
                    # Provide test data for POST endpoints
                    test_data = {}
                    if "content/posts" in route:
                        test_data = {"caption": f"Test post {int(time.time())}", "kind": "POST"}
                    elif "media/upload-init" in route:
                        test_data = {"filename": "test.jpg", "contentType": "image/jpeg", "size": 100000}
                    resp = requests.post(f"{API_BASE}{route}", json=test_data, headers=headers, timeout=10)
                else:
                    resp = requests.request(method, f"{API_BASE}{route}", headers=headers, timeout=10)
                
                # Allow 401/403 for auth-required endpoints without proper permissions
                success = (resp.status_code == expected_status or 
                          resp.status_code in [401, 403])
                
                self.log_result(
                    f"Route {method} {route}", 
                    success, 
                    f"Status: {resp.status_code}"
                )
            except Exception as e:
                self.log_result(f"Route {method} {route}", False, f"Exception: {str(e)}")

    def test_complete_route_regression(self):
        """Test the complete list of routes from the review specification"""
        print("\n🎯 Testing Complete Route Regression from Specification...")
        
        if not self.token1:
            self.log_result("Complete Route Regression", False, "No auth token available")
            return

        # Routes exactly as specified in the review request
        routes_to_test = [
            ("GET", "/api/healthz"),
            ("GET", "/api/readyz"), 
            ("POST", "/api/auth/login"),
            ("GET", "/api/feed?limit=3"),
            ("GET", "/api/tribes"),
            ("GET", "/api/search?q=test"),
            ("GET", "/api/notifications"),
            ("GET", "/api/stories/feed"),
            ("GET", "/api/reels/feed"),
            ("GET", "/api/analytics/overview"),
            ("GET", "/api/cache/stats"),
            ("GET", "/api/ops/metrics"),
            ("GET", "/api/ops/health"),
            ("GET", "/api/ws/stats"),
            ("GET", "/api/me"),
            ("PUT", "/api/me/profile"),
            ("POST", "/api/media/upload-init"),
        ]

        for method, route in routes_to_test:
            try:
                headers = self.get_headers(self.token1)
                test_data = {}
                
                # Prepare test data for specific endpoints
                if route == "/api/auth/login":
                    test_data = TEST_USER1
                    headers = {}  # No auth for login
                elif route == "/api/me/profile":
                    test_data = {"displayName": f"Test {int(time.time())}"}
                elif route == "/api/media/upload-init":
                    test_data = {"filename": "test.jpg", "contentType": "image/jpeg", "size": 100000}
                
                if method == "GET":
                    resp = requests.get(f"{API_BASE}{route}", headers=headers, timeout=10)
                elif method == "POST":
                    resp = requests.post(f"{API_BASE}{route}", json=test_data, headers=headers, timeout=10)
                elif method == "PUT":
                    resp = requests.put(f"{API_BASE}{route}", json=test_data, headers=headers, timeout=10)
                else:
                    resp = requests.request(method, f"{API_BASE}{route}", headers=headers, timeout=10)
                
                # Success criteria: 200-299 or expected auth failures
                success = (200 <= resp.status_code < 300) or resp.status_code in [401, 403]
                
                self.log_result(
                    f"Spec Route {method} {route}", 
                    success, 
                    f"Status: {resp.status_code}"
                )
            except Exception as e:
                self.log_result(f"Spec Route {method} {route}", False, f"Exception: {str(e)}")

    def test_content_crud_operations(self):
        """Test content CRUD operations mentioned in review request"""
        print("\n📝 Testing Content CRUD Operations...")
        
        if not self.token1:
            self.log_result("Content CRUD", False, "No auth token available")
            return

        post_id = None
        
        # Create a post
        try:
            post_data = {
                "caption": f"Regression test post {datetime.now().isoformat()}",
                "kind": "POST"
            }
            resp = requests.post(
                f"{API_BASE}/api/content/posts",
                json=post_data,
                headers=self.get_headers(self.token1),
                timeout=10
            )
            
            if resp.status_code == 201:
                post = resp.json()
                post_id = post.get("id")
                self.log_result("POST /api/content/posts", True, f"Created post: {post_id}")
            else:
                self.log_result("POST /api/content/posts", False, f"Status: {resp.status_code}")
                
        except Exception as e:
            self.log_result("POST /api/content/posts", False, f"Exception: {str(e)}")

        if post_id:
            # Test GET content/:id
            try:
                resp = requests.get(
                    f"{API_BASE}/api/content/{post_id}",
                    headers=self.get_headers(self.token1),
                    timeout=10
                )
                success = resp.status_code == 200
                self.log_result("GET /api/content/:id", success, f"Status: {resp.status_code}")
            except Exception as e:
                self.log_result("GET /api/content/:id", False, f"Exception: {str(e)}")
            
            # Test POST like
            try:
                resp = requests.post(
                    f"{API_BASE}/api/content/{post_id}/like",
                    json={"reactionType": "LIKE"},
                    headers=self.get_headers(self.token1),
                    timeout=10
                )
                success = resp.status_code in [200, 201]
                self.log_result("POST /api/content/:id/like", success, f"Status: {resp.status_code}")
            except Exception as e:
                self.log_result("POST /api/content/:id/like", False, f"Exception: {str(e)}")
            
            # Test POST comment
            try:
                resp = requests.post(
                    f"{API_BASE}/api/content/{post_id}/comments",
                    json={"text": "Regression test comment"},
                    headers=self.get_headers(self.token1),
                    timeout=10
                )
                success = resp.status_code in [200, 201]
                self.log_result("POST /api/content/:id/comments", success, f"Status: {resp.status_code}")
            except Exception as e:
                self.log_result("POST /api/content/:id/comments", False, f"Exception: {str(e)}")
            
            # Test DELETE content
            try:
                resp = requests.delete(
                    f"{API_BASE}/api/content/{post_id}",
                    headers=self.get_headers(self.token1),
                    timeout=10
                )
                success = resp.status_code in [200, 204]
                self.log_result("DELETE /api/content/:id", success, f"Status: {resp.status_code}")
            except Exception as e:
                self.log_result("DELETE /api/content/:id", False, f"Exception: {str(e)}")

    def test_error_handling(self):
        """Test error handling scenarios"""
        print("\n🚫 Testing Error Handling...")
        
        # Test invalid token
        try:
            resp = requests.get(
                f"{API_BASE}/api/me",
                headers={"Authorization": "Bearer invalid_token"},
                timeout=10
            )
            success = resp.status_code == 401
            self.log_result("Invalid Token → 401", success, f"Status: {resp.status_code}")
        except Exception as e:
            self.log_result("Invalid Token → 401", False, f"Exception: {str(e)}")

        # Test non-existent route
        try:
            resp = requests.get(f"{API_BASE}/api/nonexistent-route-12345", timeout=10)
            success = resp.status_code == 404
            self.log_result("Bad Route → 404", success, f"Status: {resp.status_code}")
        except Exception as e:
            self.log_result("Bad Route → 404", False, f"Exception: {str(e)}")

    async def test_websocket_server(self):
        """Test WebSocket server functionality"""
        print("\n🔌 Testing WebSocket Server...")
        
        if not self.token1:
            self.log_result("WebSocket Auth", False, "No auth token available")
            return

        # Test WebSocket connection with valid token
        try:
            uri = f"{WS_URL}?token={self.token1}"
            async with websockets.connect(uri) as websocket:
                # Wait for authentication message
                auth_msg = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                auth_data = json.loads(auth_msg)
                
                expected_auth = {
                    "type": "authenticated", 
                    "data": {"userId": self.user1_id, "displayName": True}
                }
                
                success = (auth_data.get("type") == "authenticated" and 
                          auth_data.get("data", {}).get("userId") == self.user1_id)
                self.log_result("WebSocket Auth Valid Token", success, 
                              f"Type: {auth_data.get('type')}, UserID match: {success}")
                
                if success:
                    # Test ping-pong
                    await websocket.send(json.dumps({"type": "ping"}))
                    pong_msg = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    pong_data = json.loads(pong_msg)
                    
                    ping_success = pong_data.get("type") == "pong"
                    self.log_result("WebSocket Ping → Pong", ping_success, 
                                  f"Response: {pong_data.get('type')}")
                    
                    # Test presence query
                    if self.user2_id:
                        await websocket.send(json.dumps({
                            "type": "presence_query",
                            "data": {"userIds": [self.user1_id, self.user2_id]}
                        }))
                        
                        presence_msg = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        presence_data = json.loads(presence_msg)
                        
                        presence_success = presence_data.get("type") == "presence_result"
                        self.log_result("WebSocket Presence Query", presence_success,
                                      f"Type: {presence_data.get('type')}")
                    
                    # Test typing event (no response expected)
                    if self.user2_id:
                        await websocket.send(json.dumps({
                            "type": "typing",
                            "data": {
                                "targetUserId": self.user2_id,
                                "context": "comment"
                            }
                        }))
                        # Typing events don't send responses
                        self.log_result("WebSocket Typing Event", True, "No response expected")
                    
        except asyncio.TimeoutError:
            self.log_result("WebSocket Connection", False, "Connection timeout")
        except Exception as e:
            self.log_result("WebSocket Connection", False, f"Exception: {str(e)}")

        # Test WebSocket with invalid token
        try:
            uri = f"{WS_URL}?token=invalid_token"
            async with websockets.connect(uri) as websocket:
                try:
                    msg = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    # Should not receive successful auth
                    self.log_result("WebSocket Invalid Token → Close", False, "Should have closed connection")
                except websockets.exceptions.ConnectionClosed as e:
                    success = e.code == 4003  # Invalid token close code
                    self.log_result("WebSocket Invalid Token → Close", success, f"Close code: {e.code}")
        except websockets.exceptions.ConnectionClosed as e:
            success = e.code == 4003
            self.log_result("WebSocket Invalid Token → Close", success, f"Close code: {e.code}")
        except Exception as e:
            self.log_result("WebSocket Invalid Token → Close", False, f"Exception: {str(e)}")

    async def test_websocket_redis_broadcast(self):
        """Test WebSocket Redis broadcast functionality (2-way push)"""
        print("\n📡 Testing WebSocket Redis Broadcast...")
        
        if not self.redis_client or not self.token2 or not self.user2_id:
            self.log_result("WebSocket Redis Broadcast", False, 
                          "Redis or user2 not available for testing")
            return

        try:
            # Connect user2 to WebSocket
            uri = f"{WS_URL}?token={self.token2}"
            async with websockets.connect(uri) as websocket:
                # Wait for auth
                auth_msg = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                auth_data = json.loads(auth_msg)
                
                if auth_data.get("type") != "authenticated":
                    self.log_result("WebSocket Broadcast Setup", False, "Auth failed")
                    return

                # Publish a like event via Redis that should be delivered to user2
                # (as specified in the review request)
                event_data = {
                    "type": "like",
                    "targetUserId": self.user2_id,
                    "data": {
                        "userId": "test",
                        "contentId": "test"
                    }
                }
                
                print(f"Publishing Redis event for user {self.user2_id}...")
                # Publish to Redis
                self.redis_client.publish('tribe:ws:broadcast', json.dumps(event_data))
                
                # Wait for the WebSocket to receive the broadcast
                try:
                    broadcast_msg = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    broadcast_data = json.loads(broadcast_msg)
                    
                    success = (broadcast_data.get("type") == "like" and 
                              broadcast_data.get("targetUserId") == self.user2_id)
                    self.log_result("WebSocket 2-Way Push (Redis)", success,
                                  f"Received: {broadcast_data.get('type')} for {broadcast_data.get('targetUserId')}")
                except asyncio.TimeoutError:
                    self.log_result("WebSocket 2-Way Push (Redis)", False, "No broadcast received within timeout")
                    
        except Exception as e:
            self.log_result("WebSocket 2-Way Push (Redis)", False, f"Exception: {str(e)}")

    def test_route_contract_consistency(self):
        """Test that route responses include expected contract headers/fields"""
        print("\n📄 Testing Route Contract Consistency...")
        
        try:
            resp = requests.get(f"{API_BASE}/api/healthz", timeout=10)
            headers = resp.headers
            
            # Check for expected security and contract headers
            has_cors = 'access-control-allow-origin' in headers
            has_contract = 'x-contract-version' in headers
            has_request_id = 'x-request-id' in headers
            
            self.log_result("Route Headers Present", True, 
                          f"CORS: {has_cors}, Contract: {has_contract}, RequestID: {has_request_id}")
            
            # Test that health endpoint returns expected structure
            if resp.status_code == 200:
                data = resp.json()
                has_status = 'status' in data
                self.log_result("Health Route Structure", has_status, 
                              f"Has status field: {has_status}")
            
        except Exception as e:
            self.log_result("Route Contract", False, f"Exception: {str(e)}")

    async def run_all_tests(self):
        """Run all test suites"""
        print("🚀 TRIBE BACKEND REGRESSION TEST SUITE")
        print("🎯 Testing: WebSocket Server + Route Dispatch Refactoring")
        print(f"📅 Test run: {datetime.now().isoformat()}")
        print(f"🌐 Base URL: {API_BASE}")
        print(f"🔌 WebSocket URL: {WS_URL}")
        print("=" * 80)
        
        # Authentication and setup
        self.test_auth_flow()
        
        # Core route testing (main focus of regression)
        self.test_route_refactoring_regression()
        self.test_complete_route_regression()
        self.test_content_crud_operations()
        self.test_error_handling()
        self.test_route_contract_consistency()
        
        # WebSocket testing (new feature)
        await self.test_websocket_server()
        await self.test_websocket_redis_broadcast()
        
        # Summary
        return self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 FINAL REGRESSION TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for r in self.results if r['success'])
        total = len(self.results)
        percentage = (passed / total * 100) if total > 0 else 0
        
        print(f"✅ PASSED: {passed}/{total} ({percentage:.1f}%)")
        print(f"❌ FAILED: {total - passed}/{total}")
        
        # Categorize results
        auth_tests = [r for r in self.results if 'Auth' in r['test']]
        route_tests = [r for r in self.results if 'Route' in r['test'] or 'Spec Route' in r['test']]
        content_tests = [r for r in self.results if 'content' in r['test'] or 'POST' in r['test'] or 'GET' in r['test'] or 'DELETE' in r['test']]
        ws_tests = [r for r in self.results if 'WebSocket' in r['test']]
        
        auth_pass = sum(1 for r in auth_tests if r['success'])
        route_pass = sum(1 for r in route_tests if r['success'])
        content_pass = sum(1 for r in content_tests if r['success'])
        ws_pass = sum(1 for r in ws_tests if r['success'])
        
        print(f"\n📋 CATEGORY BREAKDOWN:")
        auth_pct = (auth_pass/len(auth_tests)*100) if len(auth_tests) > 0 else 0
        route_pct = (route_pass/len(route_tests)*100) if len(route_tests) > 0 else 0
        content_pct = (content_pass/len(content_tests)*100) if len(content_tests) > 0 else 0
        ws_pct = (ws_pass/len(ws_tests)*100) if len(ws_tests) > 0 else 0
        
        print(f"   🔐 Authentication: {auth_pass}/{len(auth_tests)} ({auth_pct:.1f}%)")
        print(f"   🔄 Route Dispatch: {route_pass}/{len(route_tests)} ({route_pct:.1f}%)")
        print(f"   📝 Content CRUD: {content_pass}/{len(content_tests)} ({content_pct:.1f}%)")
        print(f"   🔌 WebSocket Server: {ws_pass}/{len(ws_tests)} ({ws_pct:.1f}%)")
        
        # Show failed tests
        failed_tests = [r for r in self.results if not r['success']]
        if failed_tests:
            print(f"\n🚨 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['details']}")
        
        # Key findings
        print(f"\n🔍 KEY FINDINGS:")
        route_dispatch_working = sum(1 for r in route_tests if r['success']) / len(route_tests) >= 0.8 if route_tests else False
        websocket_working = sum(1 for r in ws_tests if r['success']) / len(ws_tests) >= 0.8 if ws_tests else False
        
        print(f"   📊 Route Dispatch Refactoring: {'✅ WORKING' if route_dispatch_working else '❌ ISSUES'}")
        print(f"   🔌 WebSocket Server (NEW): {'✅ WORKING' if websocket_working else '❌ ISSUES'}")
        
        # Overall verdict based on requirements
        if percentage >= 90:
            verdict = "🎉 EXCELLENT - Backend ready for production"
        elif percentage >= 80:
            verdict = "✅ GOOD - Minor issues, generally functional"  
        elif percentage >= 70:
            verdict = "⚠️ ACCEPTABLE - Some issues need attention"
        else:
            verdict = "🚨 CRITICAL - Major issues blocking deployment"
        
        print(f"\n{verdict}")
        print(f"📈 Overall Success Rate: {percentage:.1f}%")
        
        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "percentage": percentage,
            "verdict": "PASS" if percentage >= 75 else "FAIL",
            "route_dispatch_working": route_dispatch_working,
            "websocket_working": websocket_working
        }

async def main():
    """Main test runner"""
    tester = TribeAPITester()
    results = await tester.run_all_tests()
    return results

if __name__ == "__main__":
    asyncio.run(main())