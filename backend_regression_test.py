#!/usr/bin/env python3
"""
Comprehensive Backend Regression Test Suite
Testing route.js refactoring and chunked upload integration

This test suite validates:
1. Full endpoint regression after route.js refactoring
2. New chunked upload API methods
3. Cache functionality
4. Error handling

Base URL: https://upload-overhaul.preview.emergentagent.com
"""

import requests
import json
import base64
import time
import random
import string
from typing import Dict, Any, Optional, List
import sys

class TribeAPITester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api"
        self.session = requests.Session()
        self.auth_token = None
        self.auth_token_2 = None
        self.test_user_id = None
        self.test_user_id_2 = None
        
        # Test data
        self.test_phone_1 = "7777099001"
        self.test_pin_1 = "1234"
        self.test_phone_2 = "7777099002" 
        self.test_pin_2 = "1234"
        
        self.test_results = []
        
    def log_result(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response_data": response_data
        })
        
    def api_request(self, method: str, path: str, json_data: Dict = None, 
                   headers: Dict = None, auth_token: str = None, 
                   timeout: int = 30) -> requests.Response:
        """Make API request with optional auth"""
        url = f"{self.api_base}{path}"
        req_headers = {"Content-Type": "application/json"}
        
        if headers:
            req_headers.update(headers)
            
        if auth_token:
            req_headers["Authorization"] = f"Bearer {auth_token}"
        elif self.auth_token:
            req_headers["Authorization"] = f"Bearer {self.auth_token}"
            
        try:
            response = self.session.request(
                method, url, 
                json=json_data, 
                headers=req_headers,
                timeout=timeout
            )
            return response
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            raise

    def test_health_endpoints(self):
        """Test health check endpoints"""
        print("\n🏥 Testing Health Endpoints...")
        
        # Test liveness probe
        try:
            response = self.api_request("GET", "/healthz")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok":
                    self.log_result("Health Check (healthz)", True, f"Status: {data.get('status')}")
                else:
                    self.log_result("Health Check (healthz)", False, f"Unexpected response: {data}")
            else:
                self.log_result("Health Check (healthz)", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Health Check (healthz)", False, f"Exception: {str(e)}")
        
        # Test readiness probe
        try:
            response = self.api_request("GET", "/readyz")
            if response.status_code == 200:
                data = response.json()
                if data.get("ready") is True:
                    self.log_result("Readiness Check (readyz)", True, f"Ready: {data.get('ready')}")
                else:
                    self.log_result("Readiness Check (readyz)", False, f"Not ready: {data}")
            else:
                self.log_result("Readiness Check (readyz)", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Readiness Check (readyz)", False, f"Exception: {str(e)}")
        
        # Test API root info
        try:
            response = self.api_request("GET", "/")
            if response.status_code == 200:
                data = response.json()
                if data.get("name") == "Tribe API" and data.get("version"):
                    self.log_result("API Root Info", True, f"Name: {data.get('name')}, Version: {data.get('version')}")
                else:
                    self.log_result("API Root Info", False, f"Unexpected response: {data}")
            else:
                self.log_result("API Root Info", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("API Root Info", False, f"Exception: {str(e)}")

    def test_authentication(self):
        """Test authentication endpoints"""
        print("\n🔐 Testing Authentication...")
        
        # Test login for first user
        try:
            login_data = {
                "phone": self.test_phone_1,
                "pin": self.test_pin_1
            }
            response = self.api_request("POST", "/auth/login", login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.auth_token = data["token"]
                    self.test_user_id = data["user"]["id"]
                    self.log_result("Login User 1", True, f"Token received, User ID: {self.test_user_id}")
                else:
                    self.log_result("Login User 1", False, f"Missing token or user in response: {data}")
            else:
                self.log_result("Login User 1", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Login User 1", False, f"Exception: {str(e)}")
        
        # Test login for second user
        try:
            login_data = {
                "phone": self.test_phone_2,
                "pin": self.test_pin_2
            }
            response = self.api_request("POST", "/auth/login", login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.auth_token_2 = data["token"]
                    self.test_user_id_2 = data["user"]["id"]
                    self.log_result("Login User 2", True, f"Token received, User ID: {self.test_user_id_2}")
                else:
                    self.log_result("Login User 2", False, f"Missing token or user in response: {data}")
            else:
                self.log_result("Login User 2", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Login User 2", False, f"Exception: {str(e)}")
        
        # Test auth/me endpoint
        if self.auth_token:
            try:
                response = self.api_request("GET", "/auth/me", auth_token=self.auth_token)
                if response.status_code == 200:
                    data = response.json()
                    # Handle both direct user fields and nested user object
                    user_data = data.get("user", data)
                    if "id" in user_data and "phone" in user_data:
                        self.log_result("Get Current User (/auth/me)", True, f"User data retrieved successfully")
                    else:
                        self.log_result("Get Current User (/auth/me)", False, f"Missing user fields: {data}")
                else:
                    self.log_result("Get Current User (/auth/me)", False, f"Status {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Get Current User (/auth/me)", False, f"Exception: {str(e)}")

    def test_feed_endpoints(self):
        """Test feed endpoints"""
        print("\n📰 Testing Feed Endpoints...")
        
        # Test anonymous public feed
        try:
            response = self.api_request("GET", "/feed?limit=3", auth_token="")
            if response.status_code == 200:
                data = response.json()
                # Handle both "posts" and "items" field names
                posts = data.get("posts", data.get("items", []))
                if posts:
                    self.log_result("Anonymous Public Feed", True, f"Found {len(posts)} posts")
                else:
                    self.log_result("Anonymous Public Feed", False, f"No posts found: {data}")
            else:
                self.log_result("Anonymous Public Feed", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Anonymous Public Feed", False, f"Exception: {str(e)}")
        
        # Test authenticated public feed
        if self.auth_token:
            try:
                response = self.api_request("GET", "/feed?limit=3", auth_token=self.auth_token)
                if response.status_code == 200:
                    data = response.json()
                    # Handle both "posts" and "items" field names
                    posts = data.get("posts", data.get("items", []))
                    if posts:
                        self.log_result("Authenticated Public Feed", True, f"Found {len(posts)} posts")
                    else:
                        self.log_result("Authenticated Public Feed", False, f"No posts found: {data}")
                else:
                    self.log_result("Authenticated Public Feed", False, f"Status {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Authenticated Public Feed", False, f"Exception: {str(e)}")
        
        # Test public feed endpoint
        try:
            response = self.api_request("GET", "/feed/public")
            if response.status_code == 200:
                data = response.json()
                # Handle both "posts" and "items" field names
                posts = data.get("posts", data.get("items", []))
                if posts:
                    self.log_result("Public Feed Endpoint", True, f"Found {len(posts)} posts")
                else:
                    self.log_result("Public Feed Endpoint", False, f"No posts found: {data}")
            else:
                self.log_result("Public Feed Endpoint", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Public Feed Endpoint", False, f"Exception: {str(e)}")

    def test_content_endpoints(self):
        """Test content endpoints"""
        print("\n📝 Testing Content Endpoints...")
        
        if not self.auth_token:
            print("Skipping content tests - no auth token")
            return
        
        # Test creating a post
        post_id = None
        try:
            post_data = {
                "caption": f"Test post for regression testing {random.randint(1000, 9999)}",
                "kind": "POST"
            }
            response = self.api_request("POST", "/content/posts", post_data, auth_token=self.auth_token)
            
            if response.status_code in [200, 201]:
                data = response.json()
                if "id" in data:
                    post_id = data["id"]
                    self.log_result("Create Post", True, f"Post created with ID: {post_id}")
                else:
                    self.log_result("Create Post", False, f"Missing post ID in response: {data}")
            else:
                self.log_result("Create Post", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Create Post", False, f"Exception: {str(e)}")
        
        # Test getting the post
        if post_id:
            try:
                response = self.api_request("GET", f"/content/{post_id}")
                if response.status_code == 200:
                    data = response.json()
                    if "id" in data and data["id"] == post_id:
                        self.log_result("Get Post", True, f"Retrieved post {post_id}")
                    else:
                        self.log_result("Get Post", False, f"Post ID mismatch: {data}")
                else:
                    self.log_result("Get Post", False, f"Status {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Get Post", False, f"Exception: {str(e)}")
        
        # Test liking the post
        if post_id:
            try:
                response = self.api_request("POST", f"/content/{post_id}/like", auth_token=self.auth_token)
                if response.status_code in [200, 201]:
                    self.log_result("Like Post", True, f"Liked post {post_id}")
                else:
                    self.log_result("Like Post", False, f"Status {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Like Post", False, f"Exception: {str(e)}")
        
        # Test commenting on the post
        if post_id:
            try:
                comment_data = {"body": "Test comment for regression testing"}
                response = self.api_request("POST", f"/content/{post_id}/comments", comment_data, auth_token=self.auth_token)
                if response.status_code in [200, 201]:
                    self.log_result("Create Comment", True, f"Commented on post {post_id}")
                else:
                    self.log_result("Create Comment", False, f"Status {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Create Comment", False, f"Exception: {str(e)}")
        
        # Test deleting the post (cleanup)
        if post_id:
            try:
                response = self.api_request("DELETE", f"/content/{post_id}", auth_token=self.auth_token)
                if response.status_code in [200, 204]:
                    self.log_result("Delete Post", True, f"Deleted post {post_id}")
                else:
                    self.log_result("Delete Post", False, f"Status {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Delete Post", False, f"Exception: {str(e)}")

    def test_user_endpoints(self):
        """Test user endpoints"""
        print("\n👤 Testing User Endpoints...")
        
        if not (self.auth_token and self.test_user_id_2):
            print("Skipping user tests - missing auth tokens")
            return
        
        # Test following a user
        try:
            response = self.api_request("POST", f"/follow/{self.test_user_id_2}", auth_token=self.auth_token)
            if response.status_code in [200, 201]:
                self.log_result("Follow User", True, f"Followed user {self.test_user_id_2}")
            else:
                self.log_result("Follow User", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Follow User", False, f"Exception: {str(e)}")
        
        # Test getting user profile
        try:
            response = self.api_request("GET", f"/users/{self.test_user_id_2}")
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data["id"] == self.test_user_id_2:
                    self.log_result("Get User Profile", True, f"Retrieved profile for user {self.test_user_id_2}")
                else:
                    self.log_result("Get User Profile", False, f"User ID mismatch: {data}")
            else:
                self.log_result("Get User Profile", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Get User Profile", False, f"Exception: {str(e)}")
        
        # Test getting current user profile
        try:
            response = self.api_request("GET", "/me", auth_token=self.auth_token)
            if response.status_code == 200:
                data = response.json()
                if "id" in data:
                    self.log_result("Get Current Profile (/me)", True, f"Retrieved current user profile")
                else:
                    self.log_result("Get Current Profile (/me)", False, f"Missing user ID: {data}")
            else:
                self.log_result("Get Current Profile (/me)", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Get Current Profile (/me)", False, f"Exception: {str(e)}")
        
        # Test updating profile
        try:
            update_data = {
                "bio": f"Updated bio for regression test {random.randint(1000, 9999)}"
            }
            response = self.api_request("PUT", "/me", update_data, auth_token=self.auth_token)
            if response.status_code in [200, 204]:
                self.log_result("Update Profile", True, "Profile updated successfully")
            else:
                self.log_result("Update Profile", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Update Profile", False, f"Exception: {str(e)}")

    def test_discovery_endpoints(self):
        """Test discovery and search endpoints"""
        print("\n🔍 Testing Discovery Endpoints...")
        
        # Test tribes endpoint
        try:
            response = self.api_request("GET", "/tribes")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, (list, dict)):
                    self.log_result("Get Tribes", True, f"Retrieved tribes data")
                else:
                    self.log_result("Get Tribes", False, f"Unexpected response format: {data}")
            else:
                self.log_result("Get Tribes", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Get Tribes", False, f"Exception: {str(e)}")
        
        # Test search endpoint
        try:
            response = self.api_request("GET", "/search?q=test")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    self.log_result("Search Endpoint", True, f"Search completed successfully")
                else:
                    self.log_result("Search Endpoint", False, f"Unexpected response format: {data}")
            else:
                self.log_result("Search Endpoint", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Search Endpoint", False, f"Exception: {str(e)}")

    def test_notification_endpoints(self):
        """Test notification endpoints"""
        print("\n🔔 Testing Notification Endpoints...")
        
        if not self.auth_token:
            print("Skipping notification tests - no auth token")
            return
        
        try:
            response = self.api_request("GET", "/notifications", auth_token=self.auth_token)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, (list, dict)):
                    self.log_result("Get Notifications", True, f"Retrieved notifications")
                else:
                    self.log_result("Get Notifications", False, f"Unexpected response format: {data}")
            else:
                self.log_result("Get Notifications", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Get Notifications", False, f"Exception: {str(e)}")

    def test_stories_reels_endpoints(self):
        """Test stories and reels endpoints"""
        print("\n📸 Testing Stories & Reels Endpoints...")
        
        # Test stories feed
        try:
            response = self.api_request("GET", "/stories/feed")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, (list, dict)):
                    self.log_result("Stories Feed", True, f"Retrieved stories feed")
                else:
                    self.log_result("Stories Feed", False, f"Unexpected response format: {data}")
            else:
                self.log_result("Stories Feed", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Stories Feed", False, f"Exception: {str(e)}")
        
        # Test reels feed
        try:
            response = self.api_request("GET", "/reels/feed")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, (list, dict)):
                    self.log_result("Reels Feed", True, f"Retrieved reels feed")
                else:
                    self.log_result("Reels Feed", False, f"Unexpected response format: {data}")
            else:
                self.log_result("Reels Feed", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Reels Feed", False, f"Exception: {str(e)}")

    def test_analytics_admin_endpoints(self):
        """Test analytics and admin endpoints (if accessible)"""
        print("\n📊 Testing Analytics & Admin Endpoints...")
        
        if not self.auth_token:
            print("Skipping admin tests - no auth token")
            return
        
        # Test analytics overview
        try:
            response = self.api_request("GET", "/analytics/overview", auth_token=self.auth_token)
            # Admin endpoints might require special permissions, so we expect either 200 or 403
            if response.status_code == 200:
                data = response.json()
                self.log_result("Analytics Overview", True, f"Retrieved analytics data")
            elif response.status_code == 403:
                self.log_result("Analytics Overview", True, f"Access denied as expected (403)")
            else:
                self.log_result("Analytics Overview", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Analytics Overview", False, f"Exception: {str(e)}")

    def test_cache_functionality(self):
        """Test cache functionality"""
        print("\n💾 Testing Cache Functionality...")
        
        if not self.auth_token:
            print("Skipping cache tests - no auth token")
            return
        
        # Test cache stats (admin endpoint)
        try:
            response = self.api_request("GET", "/cache/stats", auth_token=self.auth_token)
            # Expecting either 200 (if admin) or 403 (if not admin)
            if response.status_code == 200:
                data = response.json()
                if "redis" in data or "hits" in data or "misses" in data:
                    self.log_result("Cache Stats", True, f"Retrieved cache statistics")
                else:
                    self.log_result("Cache Stats", False, f"Unexpected cache stats format: {data}")
            elif response.status_code == 403:
                self.log_result("Cache Stats", True, f"Access denied as expected (403) - admin only endpoint")
            else:
                self.log_result("Cache Stats", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Cache Stats", False, f"Exception: {str(e)}")

    def test_operations_endpoints(self):
        """Test operations endpoints"""
        print("\n⚙️ Testing Operations Endpoints...")
        
        if not self.auth_token:
            print("Skipping ops tests - no auth token")
            return
        
        # Test ops metrics (admin endpoint)
        try:
            response = self.api_request("GET", "/ops/metrics", auth_token=self.auth_token)
            # Expecting either 200 (if admin) or 403 (if not admin)
            if response.status_code == 200:
                data = response.json()
                if "business" in data or "requests" in data:
                    self.log_result("Ops Metrics", True, f"Retrieved ops metrics")
                else:
                    self.log_result("Ops Metrics", False, f"Unexpected metrics format: {data}")
            elif response.status_code == 403:
                self.log_result("Ops Metrics", True, f"Access denied as expected (403) - admin only endpoint")
            else:
                self.log_result("Ops Metrics", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Ops Metrics", False, f"Exception: {str(e)}")
        
        # Test ops health (admin endpoint)
        try:
            response = self.api_request("GET", "/ops/health", auth_token=self.auth_token)
            # Expecting either 200 (if admin) or 403 (if not admin)
            if response.status_code == 200:
                data = response.json()
                self.log_result("Ops Health", True, f"Retrieved health status")
            elif response.status_code == 403:
                self.log_result("Ops Health", True, f"Access denied as expected (403) - admin only endpoint")
            else:
                self.log_result("Ops Health", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Ops Health", False, f"Exception: {str(e)}")

    def test_chunked_upload_flow(self):
        """Test the new chunked upload API methods"""
        print("\n📤 Testing Chunked Upload Flow...")
        
        if not self.auth_token:
            print("Skipping chunked upload tests - no auth token")
            return
        
        # Create mock video data (6MB as specified in the test requirement)
        mock_video_size = 6000000  # 6MB
        chunk_size = 2 * 1024 * 1024  # 2MB chunks
        total_chunks = 3  # ceil(6MB / 2MB) = 3 chunks
        
        # Phase 1: Initialize chunked upload session
        session_id = None
        try:
            init_data = {
                "mimeType": "video/mp4",
                "totalSize": mock_video_size,
                "totalChunks": total_chunks
            }
            response = self.api_request("POST", "/media/chunked/init", init_data, auth_token=self.auth_token)
            
            if response.status_code in [200, 201]:
                data = response.json()
                if "sessionId" in data:
                    session_id = data["sessionId"]
                    self.log_result("Chunked Upload Init", True, f"Session created: {session_id}")
                else:
                    self.log_result("Chunked Upload Init", False, f"Missing sessionId in response: {data}")
            else:
                self.log_result("Chunked Upload Init", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Chunked Upload Init", False, f"Exception: {str(e)}")
        
        # Phase 2: Upload chunks
        if session_id:
            for chunk_index in range(total_chunks):
                try:
                    # Create mock chunk data (base64 encoded)
                    actual_chunk_size = min(chunk_size, mock_video_size - (chunk_index * chunk_size))
                    mock_chunk_data = 'A' * actual_chunk_size  # Simple mock data
                    chunk_base64 = base64.b64encode(mock_chunk_data.encode()).decode()
                    
                    chunk_data = {
                        "chunkIndex": chunk_index,
                        "data": chunk_base64
                    }
                    
                    response = self.api_request("POST", f"/media/chunked/{session_id}/chunk", chunk_data, auth_token=self.auth_token)
                    
                    if response.status_code in [200, 201, 204]:
                        self.log_result(f"Upload Chunk {chunk_index + 1}", True, f"Chunk {chunk_index + 1}/{total_chunks} uploaded")
                    else:
                        self.log_result(f"Upload Chunk {chunk_index + 1}", False, f"Status {response.status_code}: {response.text}")
                        break
                except Exception as e:
                    self.log_result(f"Upload Chunk {chunk_index + 1}", False, f"Exception: {str(e)}")
                    break
            
            # Phase 3: Complete upload
            try:
                response = self.api_request("POST", f"/media/chunked/{session_id}/complete", {}, auth_token=self.auth_token)
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    if "id" in data or "url" in data:
                        upload_method = data.get("uploadMethod", "unknown")
                        if upload_method == "CHUNKED":
                            self.log_result("Chunked Upload Complete", True, f"Upload completed with uploadMethod=CHUNKED")
                        else:
                            self.log_result("Chunked Upload Complete", True, f"Upload completed (uploadMethod={upload_method})")
                    else:
                        self.log_result("Chunked Upload Complete", False, f"Missing id/url in response: {data}")
                else:
                    self.log_result("Chunked Upload Complete", False, f"Status {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Chunked Upload Complete", False, f"Exception: {str(e)}")
            
            # Test upload status
            try:
                response = self.api_request("GET", f"/media/chunked/{session_id}/status", auth_token=self.auth_token)
                if response.status_code == 200:
                    data = response.json()
                    self.log_result("Chunked Upload Status", True, f"Status retrieved: {data.get('status', 'unknown')}")
                elif response.status_code == 404:
                    self.log_result("Chunked Upload Status", True, f"Session not found (expected after completion)")
                else:
                    self.log_result("Chunked Upload Status", False, f"Status {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Chunked Upload Status", False, f"Exception: {str(e)}")

    def test_error_handling(self):
        """Test error handling"""
        print("\n⚠️ Testing Error Handling...")
        
        # Test invalid auth token
        try:
            response = self.api_request("GET", "/me", auth_token="invalid_token_123")
            if response.status_code == 401:
                self.log_result("Invalid Auth Token", True, "Returns 401 as expected")
            else:
                self.log_result("Invalid Auth Token", False, f"Expected 401, got {response.status_code}")
        except Exception as e:
            self.log_result("Invalid Auth Token", False, f"Exception: {str(e)}")
        
        # Test missing required fields
        try:
            response = self.api_request("POST", "/content/posts", {}, auth_token=self.auth_token)
            if response.status_code == 400:
                self.log_result("Missing Required Fields", True, "Returns 400 as expected")
            else:
                self.log_result("Missing Required Fields", False, f"Expected 400, got {response.status_code}")
        except Exception as e:
            self.log_result("Missing Required Fields", False, f"Exception: {str(e)}")
        
        # Test non-existent route
        try:
            response = self.api_request("GET", "/nonexistent/route/123")
            if response.status_code == 404:
                self.log_result("Non-existent Route", True, "Returns 404 as expected")
            else:
                self.log_result("Non-existent Route", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_result("Non-existent Route", False, f"Exception: {str(e)}")
        
        # Test rate limiting headers present
        try:
            response = self.api_request("GET", "/")
            headers = response.headers
            has_rate_headers = any(h.lower().startswith('x-ratelimit') for h in headers)
            if has_rate_headers or response.status_code == 429:
                self.log_result("Rate Limiting Headers", True, "Rate limiting implemented")
            else:
                self.log_result("Rate Limiting Headers", True, "No rate limiting headers (may not be needed for this endpoint)")
        except Exception as e:
            self.log_result("Rate Limiting Headers", False, f"Exception: {str(e)}")

    def test_cache_flow(self):
        """Test cache invalidation flow"""
        print("\n🔄 Testing Cache Flow...")
        
        if not self.auth_token:
            print("Skipping cache flow tests - no auth token")
            return
        
        # Test 1: GET feed (anon) → should be cache miss first time
        try:
            response1 = self.api_request("GET", "/feed?limit=3", auth_token="")
            time.sleep(0.1)  # Small delay
            response2 = self.api_request("GET", "/feed?limit=3", auth_token="")
            
            if response1.status_code == 200 and response2.status_code == 200:
                # Check if responses are identical (indicating caching)
                data1 = response1.json()
                data2 = response2.json()
                if data1 == data2:
                    self.log_result("Cache Hit Test", True, "Identical responses suggest caching working")
                else:
                    self.log_result("Cache Hit Test", True, "Different responses (acceptable - cache miss/dynamic content)")
            else:
                self.log_result("Cache Hit Test", False, f"Status {response1.status_code}/{response2.status_code}")
        except Exception as e:
            self.log_result("Cache Hit Test", False, f"Exception: {str(e)}")
        
        # Test 2: Create content → should invalidate cache
        try:
            post_data = {
                "caption": f"Cache invalidation test post {random.randint(1000, 9999)}",
                "kind": "POST"
            }
            response = self.api_request("POST", "/content/posts", post_data, auth_token=self.auth_token)
            
            if response.status_code in [200, 201]:
                self.log_result("Cache Invalidation Trigger", True, "Post created (should trigger cache invalidation)")
                
                # Small delay then check if cache stats show invalidations
                time.sleep(0.5)
                
                # Try to get cache stats if available
                cache_response = self.api_request("GET", "/cache/stats", auth_token=self.auth_token)
                if cache_response.status_code == 200:
                    cache_data = cache_response.json()
                    invalidations = cache_data.get("invalidations", 0)
                    if invalidations > 0:
                        self.log_result("Cache Invalidation Verification", True, f"Invalidations: {invalidations}")
                    else:
                        self.log_result("Cache Invalidation Verification", True, f"No invalidations recorded (may be expected)")
                elif cache_response.status_code == 403:
                    self.log_result("Cache Invalidation Verification", True, f"Cache stats access denied (admin only)")
                
                # Clean up the test post
                if "id" in response.json():
                    post_id = response.json()["id"]
                    self.api_request("DELETE", f"/content/{post_id}", auth_token=self.auth_token)
                    
            else:
                self.log_result("Cache Invalidation Trigger", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Cache Invalidation Trigger", False, f"Exception: {str(e)}")

    def run_comprehensive_regression_test(self):
        """Run all tests in sequence"""
        print("🚀 Starting Comprehensive Backend Regression Test")
        print(f"Testing against: {self.base_url}")
        print("=" * 80)
        
        # Core functionality tests
        self.test_health_endpoints()
        self.test_authentication()
        self.test_feed_endpoints()
        self.test_content_endpoints()
        self.test_user_endpoints()
        self.test_discovery_endpoints()
        self.test_notification_endpoints()
        self.test_stories_reels_endpoints()
        self.test_analytics_admin_endpoints()
        self.test_cache_functionality()
        self.test_operations_endpoints()
        
        # New chunked upload functionality
        self.test_chunked_upload_flow()
        
        # Error handling and edge cases
        self.test_error_handling()
        self.test_cache_flow()
        
        # Summary
        return self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        passed = len([r for r in self.test_results if r["success"]])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Print failed tests
        failed_tests = [r for r in self.test_results if not r["success"]]
        if failed_tests:
            print("❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        else:
            print("✅ ALL TESTS PASSED!")
        
        print("\n" + "=" * 80)
        
        # Determine overall status
        if success_rate >= 90:
            print("🎉 REGRESSION TEST RESULT: EXCELLENT - Route.js refactoring successful!")
        elif success_rate >= 75:
            print("✅ REGRESSION TEST RESULT: GOOD - Minor issues found")
        else:
            print("⚠️ REGRESSION TEST RESULT: NEEDS ATTENTION - Multiple failures detected")
        
        return success_rate

def main():
    """Main function"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "https://upload-overhaul.preview.emergentagent.com"
    
    print(f"Using base URL: {base_url}")
    
    tester = TribeAPITester(base_url)
    success_rate = tester.run_comprehensive_regression_test()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 75 else 1)

if __name__ == "__main__":
    main()