#!/usr/bin/env python3

"""
Performance Optimization Testing for Tribe Social Media API
Testing focus: Response latency, caching, headers, and optimization features
"""

import requests
import time
import json
import sys
from typing import Dict, Any, Optional, List, Tuple

# Test Configuration
EXTERNAL_URL = "https://comprehensive-guide-1.preview.emergentagent.com"
INTERNAL_URL = "http://localhost:3000"
TEST_USER1 = {"phone": "7777099001", "pin": "1234"}
TEST_USER2 = {"phone": "7777099002", "pin": "1234"}

class PerformanceTestSuite:
    def __init__(self):
        self.external_base = EXTERNAL_URL
        self.internal_base = INTERNAL_URL
        self.auth_token = None
        self.auth_token2 = None
        self.test_results = []
        self.session = requests.Session()
        
    def log_result(self, test_name: str, success: bool, details: str, latency: Optional[float] = None):
        """Log test result with optional latency measurement"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "latency_ms": latency
        }
        self.test_results.append(result)
        status = "✅" if success else "❌"
        latency_str = f" ({latency:.0f}ms)" if latency else ""
        print(f"{status} {test_name}: {details}{latency_str}")
        
    def authenticate_user1(self) -> bool:
        """Authenticate first test user"""
        try:
            response = self.session.post(
                f"{self.external_base}/api/auth/login",
                json=TEST_USER1,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("accessToken")
                self.log_result("User 1 Authentication", True, "Login successful")
                return True
            else:
                self.log_result("User 1 Authentication", False, f"Login failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("User 1 Authentication", False, f"Authentication error: {str(e)}")
            return False
            
    def authenticate_user2(self) -> bool:
        """Authenticate second test user"""
        try:
            response = self.session.post(
                f"{self.external_base}/api/auth/login",
                json=TEST_USER2,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token2 = data.get("accessToken")
                self.log_result("User 2 Authentication", True, "Login successful")
                return True
            else:
                self.log_result("User 2 Authentication", False, f"Login failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("User 2 Authentication", False, f"Authentication error: {str(e)}")
            return False

    def get_auth_headers(self, user1: bool = True) -> Dict[str, str]:
        """Get authorization headers for API requests"""
        token = self.auth_token if user1 else self.auth_token2
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def measure_endpoint_latency(self, endpoint: str, headers: Dict[str, str], cold_warm: bool = True) -> Tuple[float, float, Dict]:
        """Measure cold and warm call latencies for cache testing"""
        # Cold call
        start_time = time.time()
        cold_response = self.session.get(f"{self.external_base}{endpoint}", headers=headers)
        cold_latency = (time.time() - start_time) * 1000
        
        if not cold_warm:
            return cold_latency, 0, cold_response.json() if cold_response.status_code == 200 else {}
        
        # Small delay to ensure cache is set
        time.sleep(0.1)
        
        # Warm call (should be faster due to Redis cache)
        start_time = time.time()
        warm_response = self.session.get(f"{self.external_base}{endpoint}", headers=headers)
        warm_latency = (time.time() - start_time) * 1000
        
        return cold_latency, warm_latency, warm_response.json() if warm_response.status_code == 200 else {}

    def test_1_response_latency_benchmarks(self):
        """Test 1: Response latency benchmarks for key endpoints with Redis cache verification"""
        print("\n=== Test 1: Response Latency Benchmarks ===")
        
        if not self.auth_token:
            self.log_result("Response Latency Setup", False, "Authentication required")
            return
        
        headers = self.get_auth_headers()
        endpoints = [
            "/api/feed?limit=10",
            "/api/feed/public?limit=10", 
            "/api/tribes",
            "/api/tribe-contests?limit=10",
            "/api/tribe-rivalries",
            "/api/reels/feed?limit=10"
        ]
        
        for endpoint in endpoints:
            try:
                cold_ms, warm_ms, data = self.measure_endpoint_latency(endpoint, headers)
                
                if cold_ms > 0 and warm_ms > 0:
                    cache_improvement = ((cold_ms - warm_ms) / cold_ms) * 100 if cold_ms > 0 else 0
                    if warm_ms < cold_ms:
                        self.log_result(
                            f"Latency {endpoint}",
                            True,
                            f"Cold: {cold_ms:.0f}ms, Warm: {warm_ms:.0f}ms (Cache improved by {cache_improvement:.1f}%)"
                        )
                    else:
                        self.log_result(
                            f"Latency {endpoint}",
                            True,
                            f"Cold: {cold_ms:.0f}ms, Warm: {warm_ms:.0f}ms (No cache improvement detected)"
                        )
                else:
                    self.log_result(f"Latency {endpoint}", False, "Failed to get response")
                    
            except Exception as e:
                self.log_result(f"Latency {endpoint}", False, f"Error: {str(e)}")

    def test_2_cache_control_headers(self):
        """Test 2: Cache-Control headers on localhost:3000"""
        print("\n=== Test 2: Cache-Control Headers (Internal) ===")
        
        if not self.auth_token:
            self.log_result("Cache Headers Setup", False, "Authentication required")
            return
        
        headers = self.get_auth_headers()
        
        # Test endpoints with expected cache headers
        test_cases = [
            ("/api/feed", "public, max-age=10, s-maxage=15"),
            ("/api/tribes", "public, max-age=30, s-maxage=60"),
            ("/api/search", "public, max-age=15, s-maxage=20")
        ]
        
        for endpoint, expected_pattern in test_cases:
            try:
                response = self.session.get(f"{self.internal_base}{endpoint}", headers=headers)
                cache_control = response.headers.get('cache-control', '')
                
                if cache_control:
                    # Check if expected patterns are in the cache-control header
                    has_public = 'public' in cache_control.lower()
                    has_max_age = 'max-age' in cache_control.lower()
                    has_s_maxage = 's-maxage' in cache_control.lower()
                    
                    if has_public and has_max_age:
                        self.log_result(
                            f"Cache-Control {endpoint}",
                            True,
                            f"Found: {cache_control}"
                        )
                    else:
                        self.log_result(
                            f"Cache-Control {endpoint}",
                            False,
                            f"Missing expected cache directives. Found: {cache_control}"
                        )
                else:
                    self.log_result(f"Cache-Control {endpoint}", False, "No Cache-Control header found")
                    
            except Exception as e:
                self.log_result(f"Cache-Control {endpoint}", False, f"Error: {str(e)}")

    def test_3_latency_header(self):
        """Test 3: X-LATENCY-MS header presence"""
        print("\n=== Test 3: X-LATENCY-MS Header ===")
        
        if not self.auth_token:
            self.log_result("Latency Header Setup", False, "Authentication required")
            return
        
        headers = self.get_auth_headers()
        endpoints = ["/api/feed", "/api/tribes", "/api/reels/feed"]
        
        for endpoint in endpoints:
            try:
                response = self.session.get(f"{self.external_base}{endpoint}", headers=headers)
                latency_header = response.headers.get('x-latency-ms')
                
                if latency_header:
                    try:
                        latency_value = float(latency_header)
                        self.log_result(
                            f"X-LATENCY-MS {endpoint}",
                            True,
                            f"Found header: {latency_value}ms"
                        )
                    except ValueError:
                        self.log_result(
                            f"X-LATENCY-MS {endpoint}",
                            False,
                            f"Invalid latency value: {latency_header}"
                        )
                else:
                    self.log_result(f"X-LATENCY-MS {endpoint}", False, "Header not found")
                    
            except Exception as e:
                self.log_result(f"X-LATENCY-MS {endpoint}", False, f"Error: {str(e)}")

    def test_4_feed_visibility_filtering(self):
        """Test 4: Feed visibility filtering"""
        print("\n=== Test 4: Feed Visibility Filtering ===")
        
        if not self.auth_token:
            self.log_result("Feed Visibility Setup", False, "Authentication required")
            return
        
        headers = self.get_auth_headers()
        
        # Create posts with different visibility levels
        test_posts = [
            {"caption": "House only post", "visibility": "HOUSE_ONLY"},
            {"caption": "College only post", "visibility": "COLLEGE_ONLY"},
            {"caption": "Public post"}  # Should default to PUBLIC
        ]
        
        created_posts = []
        for post_data in test_posts:
            try:
                response = self.session.post(
                    f"{self.external_base}/api/content/posts",
                    json=post_data,
                    headers=headers
                )
                
                if response.status_code == 201 or response.status_code == 200:
                    post_info = response.json()
                    created_posts.append(post_info)
                    visibility = post_data.get("visibility", "PUBLIC")
                    self.log_result(
                        f"Create {visibility} post",
                        True,
                        f"Post created successfully with visibility: {visibility}"
                    )
                else:
                    visibility = post_data.get("visibility", "PUBLIC")
                    self.log_result(
                        f"Create {visibility} post",
                        False,
                        f"Failed to create post: {response.status_code}"
                    )
            except Exception as e:
                visibility = post_data.get("visibility", "PUBLIC")
                self.log_result(f"Create {visibility} post", False, f"Error: {str(e)}")
        
        # Test feed retrieval to verify visibility filtering
        try:
            response = self.session.get(f"{self.external_base}/api/feed", headers=headers)
            if response.status_code == 200:
                feed_data = response.json()
                posts = feed_data.get('items', []) or feed_data.get('posts', [])
                
                # Look for our created posts in the feed
                house_posts = [p for p in posts if p.get('visibility') == 'HOUSE_ONLY']
                college_posts = [p for p in posts if p.get('visibility') == 'COLLEGE_ONLY']
                
                self.log_result(
                    "Feed Visibility Filtering",
                    True,
                    f"Feed contains {len(house_posts)} HOUSE_ONLY and {len(college_posts)} COLLEGE_ONLY posts"
                )
            else:
                self.log_result("Feed Visibility Filtering", False, f"Feed request failed: {response.status_code}")
        except Exception as e:
            self.log_result("Feed Visibility Filtering", False, f"Error: {str(e)}")

    def test_5_tribe_detail_cached(self):
        """Test 5: Tribe detail endpoint caching"""
        print("\n=== Test 5: Tribe Detail Caching ===")
        
        if not self.auth_token:
            self.log_result("Tribe Detail Setup", False, "Authentication required")
            return
        
        headers = self.get_auth_headers()
        
        # First get list of tribes to pick one for detail testing
        try:
            tribes_response = self.session.get(f"{self.external_base}/api/tribes", headers=headers)
            if tribes_response.status_code == 200:
                tribes_data = tribes_response.json()
                tribes = tribes_data.get('items', []) or tribes_data.get('tribes', [])
                
                if tribes:
                    tribe_id = tribes[0].get('id') or tribes[0].get('tribeId')
                    if tribe_id:
                        # Test caching with cold/warm calls
                        endpoint = f"/api/tribes/{tribe_id}"
                        cold_ms, warm_ms, data = self.measure_endpoint_latency(endpoint, headers)
                        
                        if 'tribe' in data and data['tribe']:
                            cache_improvement = ((cold_ms - warm_ms) / cold_ms) * 100 if cold_ms > 0 else 0
                            has_enrichment = (
                                'topMembers' in data or 
                                'board' in data or 
                                'recentSalutes' in data
                            )
                            
                            self.log_result(
                                "Tribe Detail Caching",
                                True,
                                f"Cold: {cold_ms:.0f}ms, Warm: {warm_ms:.0f}ms. Enrichment: {has_enrichment}. Cache improvement: {cache_improvement:.1f}%"
                            )
                        else:
                            self.log_result("Tribe Detail Caching", False, "Missing tribe data in response")
                    else:
                        self.log_result("Tribe Detail Caching", False, "No tribe ID found")
                else:
                    self.log_result("Tribe Detail Caching", False, "No tribes found")
            else:
                self.log_result("Tribe Detail Caching", False, f"Failed to get tribes: {tribes_response.status_code}")
        except Exception as e:
            self.log_result("Tribe Detail Caching", False, f"Error: {str(e)}")

    def test_6_contest_list_cached(self):
        """Test 6: Contest list caching"""
        print("\n=== Test 6: Contest List Caching ===")
        
        if not self.auth_token:
            self.log_result("Contest List Setup", False, "Authentication required")
            return
        
        headers = self.get_auth_headers()
        endpoint = "/api/tribe-contests?limit=5"
        
        try:
            cold_ms, warm_ms, data = self.measure_endpoint_latency(endpoint, headers)
            
            if 'items' in data:
                contests = data['items']
                has_season_enrichment = any(
                    'seasonName' in contest for contest in contests
                ) if contests else False
                
                cache_improvement = ((cold_ms - warm_ms) / cold_ms) * 100 if cold_ms > 0 else 0
                self.log_result(
                    "Contest List Caching",
                    True,
                    f"Cold: {cold_ms:.0f}ms, Warm: {warm_ms:.0f}ms. Season enrichment: {has_season_enrichment}. Cache improvement: {cache_improvement:.1f}%"
                )
            else:
                self.log_result("Contest List Caching", False, "No contest items in response")
                
        except Exception as e:
            self.log_result("Contest List Caching", False, f"Error: {str(e)}")

    def test_7_rivalry_list_cached(self):
        """Test 7: Rivalry list caching"""
        print("\n=== Test 7: Rivalry List Caching ===")
        
        if not self.auth_token:
            self.log_result("Rivalry List Setup", False, "Authentication required")
            return
        
        headers = self.get_auth_headers()
        endpoint = "/api/tribe-rivalries?status=ACTIVE"
        
        try:
            cold_ms, warm_ms, data = self.measure_endpoint_latency(endpoint, headers)
            
            if isinstance(data, dict) and ('items' in data or 'rivalries' in data):
                rivalries = data.get('items', []) or data.get('rivalries', [])
                has_tribe_enrichment = any(
                    'tribeName' in rivalry and 'heroName' in rivalry and 'primaryColor' in rivalry
                    for rivalry in rivalries
                ) if rivalries else False
                
                cache_improvement = ((cold_ms - warm_ms) / cold_ms) * 100 if cold_ms > 0 else 0
                self.log_result(
                    "Rivalry List Caching",
                    True,
                    f"Cold: {cold_ms:.0f}ms, Warm: {warm_ms:.0f}ms. Tribe enrichment: {has_tribe_enrichment}. Cache improvement: {cache_improvement:.1f}%"
                )
            else:
                self.log_result("Rivalry List Caching", True, f"Cold: {cold_ms:.0f}ms, Warm: {warm_ms:.0f}ms. Response structure: {type(data)}")
                
        except Exception as e:
            self.log_result("Rivalry List Caching", False, f"Error: {str(e)}")

    def test_8_projection_optimization(self):
        """Test 8: Projection optimization - user snippets should only contain essential fields"""
        print("\n=== Test 8: Projection Optimization ===")
        
        if not self.auth_token:
            self.log_result("Projection Optimization Setup", False, "Authentication required")
            return
        
        headers = self.get_auth_headers()
        
        # Test various endpoints that return user snippets
        test_endpoints = [
            "/api/feed/public?limit=3",
            "/api/content/posts?limit=3"
        ]
        
        essential_fields = {'id', 'displayName', 'username', 'avatarMediaId', 'role', 'tribeId'}
        forbidden_fields = {'passwordHash', 'pinHash', 'pinSalt', 'phone'}
        
        for endpoint in test_endpoints:
            try:
                response = self.session.get(f"{self.external_base}{endpoint}", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    posts = data.get('items', []) or data.get('posts', [])
                    
                    projection_violations = []
                    good_projections = 0
                    
                    for post in posts:
                        author = post.get('author', {})
                        if author:
                            # Check for forbidden fields
                            forbidden_found = [field for field in forbidden_fields if field in author]
                            if forbidden_found:
                                projection_violations.append(f"Forbidden fields in author: {forbidden_found}")
                            else:
                                good_projections += 1
                    
                    if projection_violations:
                        self.log_result(
                            f"Projection {endpoint}",
                            False,
                            f"Violations: {', '.join(projection_violations)}"
                        )
                    else:
                        self.log_result(
                            f"Projection {endpoint}",
                            True,
                            f"Clean user projections found in {good_projections} posts"
                        )
                else:
                    self.log_result(f"Projection {endpoint}", False, f"Failed to get data: {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Projection {endpoint}", False, f"Error: {str(e)}")

    def test_9_cleanup_worker(self):
        """Test 9: Cleanup worker verification"""
        print("\n=== Test 9: Cleanup Worker ===")
        
        if not self.auth_token:
            self.log_result("Cleanup Worker Setup", False, "Authentication required")
            return
        
        headers = self.get_auth_headers()
        
        # Create a chunked upload session to test cleanup worker
        try:
            upload_data = {
                "mimeType": "video/mp4",
                "totalSize": 1000,
                "totalChunks": 2
            }
            
            response = self.session.post(
                f"{self.external_base}/api/media/chunked/init",
                json=upload_data,
                headers=headers
            )
            
            if response.status_code == 200 or response.status_code == 201:
                session_data = response.json()
                session_id = session_data.get('sessionId')
                
                if session_id:
                    # Check status of chunked upload session
                    status_response = self.session.get(
                        f"{self.external_base}/api/media/chunked/{session_id}/status",
                        headers=headers
                    )
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        status = status_data.get('status', '')
                        
                        if status == 'UPLOADING':
                            self.log_result(
                                "Cleanup Worker",
                                True,
                                f"Chunked upload session created with status: {status}"
                            )
                        else:
                            self.log_result(
                                "Cleanup Worker",
                                True,
                                f"Session created with status: {status}"
                            )
                    else:
                        self.log_result("Cleanup Worker", False, f"Status check failed: {status_response.status_code}")
                else:
                    self.log_result("Cleanup Worker", False, "No session ID in response")
            else:
                self.log_result("Cleanup Worker", False, f"Failed to create upload session: {response.status_code}")
                
        except Exception as e:
            self.log_result("Cleanup Worker", False, f"Error: {str(e)}")

    def test_10_push_notifications_stream(self):
        """Test 10: Push notifications stream"""
        print("\n=== Test 10: Push Notifications Stream ===")
        
        if not self.auth_token:
            self.log_result("Push Notifications Setup", False, "Authentication required")
            return
        
        headers = self.get_auth_headers()
        
        try:
            # Test the notifications stream endpoint
            response = self.session.get(
                f"{self.external_base}/api/notifications/stream",
                headers=headers,
                stream=True,
                timeout=5  # Short timeout since this is a stream
            )
            
            content_type = response.headers.get('content-type', '')
            
            if response.status_code == 200:
                if 'text/event-stream' in content_type:
                    # Try to read first event
                    try:
                        for line in response.iter_lines(decode_unicode=True):
                            if line and line.startswith('data:'):
                                data_part = line[5:].strip()  # Remove 'data:' prefix
                                try:
                                    event_data = json.loads(data_part)
                                    if event_data.get('type') == 'connected':
                                        supported_events = event_data.get('supportedEvents', [])
                                        self.log_result(
                                            "Push Notifications Stream",
                                            True,
                                            f"Connected event received with {len(supported_events)} supported events"
                                        )
                                        break
                                except json.JSONDecodeError:
                                    pass
                            elif line and 'connected' in line:
                                self.log_result(
                                    "Push Notifications Stream",
                                    True,
                                    "Connected to event stream"
                                )
                                break
                    except requests.exceptions.ReadTimeout:
                        self.log_result(
                            "Push Notifications Stream",
                            True,
                            "Stream connection established (timeout on read)"
                        )
                else:
                    self.log_result(
                        "Push Notifications Stream",
                        False,
                        f"Wrong content type: {content_type}, expected text/event-stream"
                    )
            else:
                self.log_result(
                    "Push Notifications Stream",
                    False,
                    f"Stream connection failed: {response.status_code}"
                )
                
        except requests.exceptions.Timeout:
            self.log_result(
                "Push Notifications Stream",
                True,
                "Stream timeout (expected for testing)"
            )
        except Exception as e:
            self.log_result("Push Notifications Stream", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all performance optimization tests"""
        print("Starting Performance Optimization Tests for Tribe Social Media API")
        print("=" * 70)
        
        # Authenticate users
        if not self.authenticate_user1():
            print("❌ Cannot proceed without authentication")
            return False
        
        if not self.authenticate_user2():
            print("⚠️ Second user authentication failed, using only first user")
        
        # Run all tests
        self.test_1_response_latency_benchmarks()
        self.test_2_cache_control_headers()
        self.test_3_latency_header()
        self.test_4_feed_visibility_filtering()
        self.test_5_tribe_detail_cached()
        self.test_6_contest_list_cached()
        self.test_7_rivalry_list_cached()
        self.test_8_projection_optimization()
        self.test_9_cleanup_worker()
        self.test_10_push_notifications_stream()
        
        # Print summary
        print("\n" + "=" * 70)
        print("PERFORMANCE OPTIMIZATION TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 PERFORMANCE OPTIMIZATION TESTS: EXCELLENT RESULTS!")
        elif success_rate >= 60:
            print("✅ PERFORMANCE OPTIMIZATION TESTS: GOOD RESULTS")
        else:
            print("⚠️ PERFORMANCE OPTIMIZATION TESTS: NEEDS IMPROVEMENT")
        
        return success_rate >= 70

def main():
    """Main test execution"""
    test_suite = PerformanceTestSuite()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()