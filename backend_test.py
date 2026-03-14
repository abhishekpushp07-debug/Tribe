#!/usr/bin/env python3
"""
BATCH 6: Events + Pages Backend Testing
Tests all 45 endpoints as specified in review request.
"""

import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "https://upload-overhaul.preview.emergentagent.com"

class TestRunner:
    def __init__(self):
        self.results = []
        self.token1 = None  # ADMIN user
        self.token2 = None  # Regular user
        self.user1_id = None
        self.user2_id = None
        self.event_id = None
        self.page_id = None
        
    def log_result(self, test_num, endpoint, method, status_code, response_time, success, details=""):
        result = {
            'test_num': test_num,
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'response_time': response_time,
            'success': success,
            'details': details,
            'slow': response_time > 500
        }
        self.results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        slow_flag = " 🐌 SLOW" if response_time > 500 else ""
        print(f"Test {test_num:2d}: {status}{slow_flag} {method:6s} {endpoint} ({response_time}ms) - {details}")

    def make_request(self, method, endpoint, data=None, headers=None, expected_status=None):
        url = f"{BASE_URL}{endpoint}"
        start_time = time.time()
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == "PATCH":
                response = requests.patch(url, json=data, headers=headers, timeout=30)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response_time = int((time.time() - start_time) * 1000)
            
            if expected_status:
                success = response.status_code == expected_status
            else:
                success = 200 <= response.status_code < 300
                
            return response, response_time, success
        except Exception as e:
            response_time = int((time.time() - start_time) * 1000)
            print(f"Request failed: {e}")
            return None, response_time, False

    def authenticate(self):
        """Authenticate both admin and regular users."""
        print("🔐 Authenticating users...")
        
        # Login admin user (token1)
        response, response_time, success = self.make_request(
            "POST", "/api/auth/login",
            {"phone": "7777099001", "pin": "1234"}
        )
        
        if success and response:
            data = response.json()
            self.token1 = data.get('token')
            self.user1_id = data.get('user', {}).get('id')
            print(f"✅ Admin user authenticated - ID: {self.user1_id}")
        else:
            print("❌ Failed to authenticate admin user")
            return False
            
        # Login regular user (token2) 
        response, response_time, success = self.make_request(
            "POST", "/api/auth/login", 
            {"phone": "7777099002", "pin": "1234"}
        )
        
        if success and response:
            data = response.json()
            self.token2 = data.get('token')
            self.user2_id = data.get('user', {}).get('id')
            print(f"✅ Regular user authenticated - ID: {self.user2_id}")
        else:
            print("❌ Failed to authenticate regular user")
            return False
            
        return True

    def get_headers(self, token):
        """Get headers with authentication token."""
        return {"Authorization": f"Bearer {token}"} if token else {}

    def test_events(self):
        """Test all 20 Events endpoints (1-20)."""
        print("\n🎉 TESTING EVENTS ENDPOINTS...")
        
        # Test 1: POST /api/events - Create event (trying with proper field names)
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
        end_date = (datetime.now() + timedelta(days=30, hours=8)).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        event_data = {
            "title": "Batch6 Test Event",
            "description": "Testing events", 
            "startAt": future_date,  # Using startAt instead of startDate
            "endAt": end_date,       # Using endAt instead of endDate
            "location": "Test Hall",
            "category": "CULTURAL",   # Using category instead of type
            "collegeId": "test-college"
        }
        
        response, response_time, success = self.make_request(
            "POST", "/api/events", event_data, self.get_headers(self.token1)
        )
        
        if success and response:
            data = response.json()
            self.event_id = data.get('event', {}).get('id') or data.get('id')
            details = f"Event created with ID: {self.event_id}"
        else:
            error_text = response.text if response else 'No response'
            status_code = response.status_code if response else 500
            details = f"Failed to create event (status {status_code}): {error_text[:200]}"
            
        self.log_result(1, "/api/events", "POST", response.status_code if response else 500, 
                       response_time, success, details)

        # Test 2: GET /api/events/search - Events search (instead of GET /events)
        response, response_time, success = self.make_request("GET", "/api/events/search")
        details = f"Events count: {len(response.json().get('items', []))} events" if success and response else "Failed to search events"
        self.log_result(2, "/api/events/search", "GET", response.status_code if response else 500,
                       response_time, success, details)

        # Test 3: GET /api/events/feed - Events feed (authenticated)
        response, response_time, success = self.make_request("GET", "/api/events/feed", headers=self.get_headers(self.token1))
        details = f"Feed events count: {len(response.json().get('items', []))}" if success and response else "Failed to get events feed"
        self.log_result(3, "/api/events/feed", "GET", response.status_code if response else 500,
                       response_time, success, details)

        # Test 4: Skip past events (endpoint does not exist)
        self.log_result(4, "/api/events/past", "GET", 404, 0, False, "Endpoint not implemented")

        # Test 5: Skip featured events (endpoint does not exist) 
        self.log_result(5, "/api/events/featured", "GET", 404, 0, False, "Endpoint not implemented")

        # Test 6: GET /api/events/{eventId} - Event detail
        if self.event_id:
            response, response_time, success = self.make_request("GET", f"/api/events/{self.event_id}")
            details = f"Event detail retrieved: {response.json().get('title', 'Unknown')}" if success and response else "Failed to get event detail"
        else:
            response, response_time, success = None, 0, False
            details = "No event ID available"
        self.log_result(6, f"/api/events/{self.event_id or 'N/A'}", "GET", response.status_code if response else 404,
                       response_time, success, details)

        # Test 7: PATCH /api/events/{eventId} - Update event
        if self.event_id:
            response, response_time, success = self.make_request(
                "PATCH", f"/api/events/{self.event_id}",
                {"title": "Updated Event"}, self.get_headers(self.token1)
            )
            details = "Event updated successfully" if success else "Failed to update event"
        else:
            response, response_time, success = None, 0, False
            details = "No event ID available"
        self.log_result(7, f"/api/events/{self.event_id or 'N/A'}", "PATCH", response.status_code if response else 404,
                       response_time, success, details)

        # Test 8: POST /api/events/{eventId}/rsvp - RSVP to event
        if self.event_id:
            response, response_time, success = self.make_request(
                "POST", f"/api/events/{self.event_id}/rsvp",
                {"status": "GOING"}, self.get_headers(self.token2)
            )
            details = "RSVP created successfully" if success else "Failed to create RSVP"
        else:
            response, response_time, success = None, 0, False
            details = "No event ID available"
        self.log_result(8, f"/api/events/{self.event_id or 'N/A'}/rsvp", "POST", response.status_code if response else 404,
                       response_time, success, details)

        # Test 9: PATCH /api/events/{eventId}/rsvp - Update RSVP
        if self.event_id:
            response, response_time, success = self.make_request(
                "PATCH", f"/api/events/{self.event_id}/rsvp",
                {"status": "MAYBE"}, self.get_headers(self.token2)
            )
            details = "RSVP updated successfully" if success else "Failed to update RSVP"
        else:
            response, response_time, success = None, 0, False
            details = "No event ID available"
        self.log_result(9, f"/api/events/{self.event_id or 'N/A'}/rsvp", "PATCH", response.status_code if response else 404,
                       response_time, success, details)

        # Test 10: DELETE /api/events/{eventId}/rsvp - Cancel RSVP
        if self.event_id:
            response, response_time, success = self.make_request(
                "DELETE", f"/api/events/{self.event_id}/rsvp",
                headers=self.get_headers(self.token2)
            )
            details = "RSVP cancelled successfully" if success else "Failed to cancel RSVP"
        else:
            response, response_time, success = None, 0, False
            details = "No event ID available"
        self.log_result(10, f"/api/events/{self.event_id or 'N/A'}/rsvp", "DELETE", response.status_code if response else 404,
                       response_time, success, details)

        # Test 11: GET /api/events/{eventId}/attendees - List attendees (correct route)
        if self.event_id:
            response, response_time, success = self.make_request("GET", f"/api/events/{self.event_id}/attendees")
            details = f"Attendees count: {len(response.json().get('attendees', []))}" if success and response else "Failed to get attendees"
        else:
            response, response_time, success = None, 0, False
            details = "No event ID available"
        self.log_result(11, f"/api/events/{self.event_id or 'N/A'}/attendees", "GET", response.status_code if response else 404,
                       response_time, success, details)

        # Test 12: GET /api/events/{eventId}/rsvp-count - RSVP count
        if self.event_id:
            response, response_time, success = self.make_request("GET", f"/api/events/{self.event_id}/rsvp-count")
            details = f"RSVP count retrieved" if success and response else "Failed to get RSVP count"
        else:
            response, response_time, success = None, 0, False
            details = "No event ID available"
        self.log_result(12, f"/api/events/{self.event_id or 'N/A'}/rsvp-count", "GET", response.status_code if response else 404,
                       response_time, success, details)

        # Test 13: POST /api/events/{eventId}/share - Share event
        if self.event_id:
            response, response_time, success = self.make_request(
                "POST", f"/api/events/{self.event_id}/share",
                headers=self.get_headers(self.token2)
            )
            details = "Event shared successfully" if success else "Failed to share event"
        else:
            response, response_time, success = None, 0, False
            details = "No event ID available"
        self.log_result(13, f"/api/events/{self.event_id or 'N/A'}/share", "POST", response.status_code if response else 404,
                       response_time, success, details)

        # Test 14: POST /api/events/{eventId}/report - Report event
        if self.event_id:
            response, response_time, success = self.make_request(
                "POST", f"/api/events/{self.event_id}/report",
                {"reason": "spam"}, self.get_headers(self.token2)
            )
            details = "Event reported successfully" if success else "Failed to report event"
        else:
            response, response_time, success = None, 0, False
            details = "No event ID available"
        self.log_result(14, f"/api/events/{self.event_id or 'N/A'}/report", "POST", response.status_code if response else 404,
                       response_time, success, details)

        # Test 15: GET /api/events/categories - Event categories
        response, response_time, success = self.make_request("GET", "/api/events/categories")
        details = f"Categories count: {len(response.json().get('categories', []))}" if success and response else "Failed to get categories"
        self.log_result(15, "/api/events/categories", "GET", response.status_code if response else 500,
                       response_time, success, details)

        # Test 16: GET /api/me/events - My events
        response, response_time, success = self.make_request("GET", "/api/me/events", headers=self.get_headers(self.token1))
        details = f"My events count: {len(response.json().get('events', []))}" if success and response else "Failed to get my events"
        self.log_result(16, "/api/me/events", "GET", response.status_code if response else 500,
                       response_time, success, details)

        # Test 17: GET /api/me/events/rsvps - My RSVPs
        response, response_time, success = self.make_request("GET", "/api/me/events/rsvps", headers=self.get_headers(self.token2))
        details = f"My RSVPs count: {len(response.json().get('rsvps', []))}" if success and response else "Failed to get my RSVPs"
        self.log_result(17, "/api/me/events/rsvps", "GET", response.status_code if response else 500,
                       response_time, success, details)

        # Test 18: POST /api/admin/events/{eventId}/feature - Feature event
        if self.event_id:
            response, response_time, success = self.make_request(
                "POST", f"/api/admin/events/{self.event_id}/feature",
                headers=self.get_headers(self.token1)
            )
            details = "Event featured successfully" if success else "Failed to feature event"
        else:
            response, response_time, success = None, 0, False
            details = "No event ID available"
        self.log_result(18, f"/api/admin/events/{self.event_id or 'N/A'}/feature", "POST", response.status_code if response else 404,
                       response_time, success, details)

        # Test 19: DELETE /api/admin/events/{eventId}/feature - Unfeature event
        if self.event_id:
            response, response_time, success = self.make_request(
                "DELETE", f"/api/admin/events/{self.event_id}/feature",
                headers=self.get_headers(self.token1)
            )
            details = "Event unfeatured successfully" if success else "Failed to unfeature event"
        else:
            response, response_time, success = None, 0, False
            details = "No event ID available"
        self.log_result(19, f"/api/admin/events/{self.event_id or 'N/A'}/feature", "DELETE", response.status_code if response else 404,
                       response_time, success, details)

        # Test 20: DELETE /api/events/{eventId} - Delete event
        if self.event_id:
            response, response_time, success = self.make_request(
                "DELETE", f"/api/events/{self.event_id}",
                headers=self.get_headers(self.token1)
            )
            details = "Event deleted successfully" if success else "Failed to delete event"
        else:
            response, response_time, success = None, 0, False
            details = "No event ID available"
        self.log_result(20, f"/api/events/{self.event_id or 'N/A'}", "DELETE", response.status_code if response else 404,
                       response_time, success, details)

    def test_pages(self):
        """Test all 25 Pages endpoints (21-45)."""
        print("\n📄 TESTING PAGES ENDPOINTS...")
        
        # Test 21: POST /api/pages - Create page (using correct category)
        page_data = {
            "name": "Batch6 Test Page",
            "description": "Testing pages",
            "category": "COLLEGE_OFFICIAL",  # Using valid category
            "collegeId": "test-college"
        }
        
        response, response_time, success = self.make_request(
            "POST", "/api/pages", page_data, self.get_headers(self.token1)
        )
        
        if success and response:
            data = response.json()
            self.page_id = data.get('page', {}).get('id') or data.get('id')
            details = f"Page created with ID: {self.page_id}"
        else:
            error_text = response.text if response else 'No response'
            status_code = response.status_code if response else 500
            details = f"Failed to create page (status {status_code}): {error_text[:200]}"
            
        self.log_result(21, "/api/pages", "POST", response.status_code if response else 500, 
                       response_time, success, details)

        # Test 22: GET /api/pages - List pages
        response, response_time, success = self.make_request("GET", "/api/pages")
        details = f"Pages count: {len(response.json().get('pages', []))} pages" if success and response else "Failed to list pages"
        self.log_result(22, "/api/pages", "GET", response.status_code if response else 500,
                       response_time, success, details)

        # Test 23: GET /api/pages/discover - Discover pages
        response, response_time, success = self.make_request("GET", "/api/pages/discover")
        details = f"Discovery pages count: {len(response.json().get('pages', []))}" if success and response else "Failed to discover pages"
        self.log_result(23, "/api/pages/discover", "GET", response.status_code if response else 500,
                       response_time, success, details)

        # Test 24: GET /api/pages/categories - Page categories
        response, response_time, success = self.make_request("GET", "/api/pages/categories")
        details = f"Categories count: {len(response.json().get('categories', []))}" if success and response else "Failed to get categories"
        self.log_result(24, "/api/pages/categories", "GET", response.status_code if response else 500,
                       response_time, success, details)

        # Test 25: GET /api/pages/{pageId} - Page detail
        if self.page_id:
            response, response_time, success = self.make_request("GET", f"/api/pages/{self.page_id}")
            details = f"Page detail retrieved: {response.json().get('name', 'Unknown')}" if success and response else "Failed to get page detail"
        else:
            response, response_time, success = None, 0, False
            details = "No page ID available"
        self.log_result(25, f"/api/pages/{self.page_id or 'N/A'}", "GET", response.status_code if response else 404,
                       response_time, success, details)

        # Test 26: PATCH /api/pages/{pageId} - Update page
        if self.page_id:
            response, response_time, success = self.make_request(
                "PATCH", f"/api/pages/{self.page_id}",
                {"description": "Updated page desc"}, self.get_headers(self.token1)
            )
            details = "Page updated successfully" if success else "Failed to update page"
        else:
            response, response_time, success = None, 0, False
            details = "No page ID available"
        self.log_result(26, f"/api/pages/{self.page_id or 'N/A'}", "PATCH", response.status_code if response else 404,
                       response_time, success, details)

        # Test 27: POST /api/pages/{pageId}/follow - Follow page
        if self.page_id:
            response, response_time, success = self.make_request(
                "POST", f"/api/pages/{self.page_id}/follow",
                headers=self.get_headers(self.token2)
            )
            details = "Page followed successfully" if success else "Failed to follow page"
        else:
            response, response_time, success = None, 0, False
            details = "No page ID available"
        self.log_result(27, f"/api/pages/{self.page_id or 'N/A'}/follow", "POST", response.status_code if response else 404,
                       response_time, success, details)

        # Test 28: DELETE /api/pages/{pageId}/follow - Unfollow page
        if self.page_id:
            response, response_time, success = self.make_request(
                "DELETE", f"/api/pages/{self.page_id}/follow",
                headers=self.get_headers(self.token2)
            )
            details = "Page unfollowed successfully" if success else "Failed to unfollow page"
        else:
            response, response_time, success = None, 0, False
            details = "No page ID available"
        self.log_result(28, f"/api/pages/{self.page_id or 'N/A'}/follow", "DELETE", response.status_code if response else 404,
                       response_time, success, details)

        # Test 29: GET /api/pages/{pageId}/followers - Page followers
        if self.page_id:
            response, response_time, success = self.make_request("GET", f"/api/pages/{self.page_id}/followers")
            details = f"Followers count: {len(response.json().get('followers', []))}" if success and response else "Failed to get followers"
        else:
            response, response_time, success = None, 0, False
            details = "No page ID available"
        self.log_result(29, f"/api/pages/{self.page_id or 'N/A'}/followers", "GET", response.status_code if response else 404,
                       response_time, success, details)

        # Test 30: GET /api/pages/{pageId}/follower-count - Follower count
        if self.page_id:
            response, response_time, success = self.make_request("GET", f"/api/pages/{self.page_id}/follower-count")
            details = f"Follower count retrieved" if success and response else "Failed to get follower count"
        else:
            response, response_time, success = None, 0, False
            details = "No page ID available"
        self.log_result(30, f"/api/pages/{self.page_id or 'N/A'}/follower-count", "GET", response.status_code if response else 404,
                       response_time, success, details)

        # Test 31: POST /api/pages/{pageId}/posts - Create page post
        if self.page_id:
            response, response_time, success = self.make_request(
                "POST", f"/api/pages/{self.page_id}/posts",
                {"caption": "Page post test"}, self.get_headers(self.token1)
            )
            details = "Page post created successfully" if success else "Failed to create page post"
        else:
            response, response_time, success = None, 0, False
            details = "No page ID available"
        self.log_result(31, f"/api/pages/{self.page_id or 'N/A'}/posts", "POST", response.status_code if response else 404,
                       response_time, success, details)

        # Test 32: GET /api/pages/{pageId}/feed - Page feed
        if self.page_id:
            response, response_time, success = self.make_request("GET", f"/api/pages/{self.page_id}/feed")
            details = f"Page feed count: {len(response.json().get('posts', []))}" if success and response else "Failed to get page feed"
        else:
            response, response_time, success = None, 0, False
            details = "No page ID available"
        self.log_result(32, f"/api/pages/{self.page_id or 'N/A'}/feed", "GET", response.status_code if response else 404,
                       response_time, success, details)

        # Test 33: POST /api/pages/{pageId}/invite - Invite member
        if self.page_id and self.user2_id:
            response, response_time, success = self.make_request(
                "POST", f"/api/pages/{self.page_id}/invite",
                {"userId": self.user2_id}, self.get_headers(self.token1)
            )
            details = "Member invited successfully" if success else "Failed to invite member"
        else:
            response, response_time, success = None, 0, False
            details = "No page ID or user ID available"
        self.log_result(33, f"/api/pages/{self.page_id or 'N/A'}/invite", "POST", response.status_code if response else 404,
                       response_time, success, details)

        # Test 34: GET /api/pages/{pageId}/members - Page members
        if self.page_id:
            response, response_time, success = self.make_request("GET", f"/api/pages/{self.page_id}/members")
            details = f"Members count: {len(response.json().get('members', []))}" if success and response else "Failed to get members"
        else:
            response, response_time, success = None, 0, False
            details = "No page ID available"
        self.log_result(34, f"/api/pages/{self.page_id or 'N/A'}/members", "GET", response.status_code if response else 404,
                       response_time, success, details)

        # Test 35: PATCH /api/pages/{pageId}/members/{userId} - Update member role
        if self.page_id and self.user2_id:
            response, response_time, success = self.make_request(
                "PATCH", f"/api/pages/{self.page_id}/members/{self.user2_id}",
                {"role": "EDITOR"}, self.get_headers(self.token1)
            )
            details = "Member role updated successfully" if success else "Failed to update member role"
        else:
            response, response_time, success = None, 0, False
            details = "No page ID or user ID available"
        self.log_result(35, f"/api/pages/{self.page_id or 'N/A'}/members/{self.user2_id or 'N/A'}", "PATCH", 
                       response.status_code if response else 404, response_time, success, details)

        # Test 36: DELETE /api/pages/{pageId}/members/{userId} - Remove member
        if self.page_id and self.user2_id:
            response, response_time, success = self.make_request(
                "DELETE", f"/api/pages/{self.page_id}/members/{self.user2_id}",
                headers=self.get_headers(self.token1)
            )
            details = "Member removed successfully" if success else "Failed to remove member"
        else:
            response, response_time, success = None, 0, False
            details = "No page ID or user ID available"
        self.log_result(36, f"/api/pages/{self.page_id or 'N/A'}/members/{self.user2_id or 'N/A'}", "DELETE", 
                       response.status_code if response else 404, response_time, success, details)

        # Test 37: POST /api/pages/{pageId}/report - Report page
        if self.page_id:
            response, response_time, success = self.make_request(
                "POST", f"/api/pages/{self.page_id}/report",
                {"reason": "inappropriate"}, self.get_headers(self.token2)
            )
            details = "Page reported successfully" if success else "Failed to report page"
        else:
            response, response_time, success = None, 0, False
            details = "No page ID available"
        self.log_result(37, f"/api/pages/{self.page_id or 'N/A'}/report", "POST", response.status_code if response else 404,
                       response_time, success, details)

        # Test 38: GET /api/me/pages - My pages
        response, response_time, success = self.make_request("GET", "/api/me/pages", headers=self.get_headers(self.token1))
        details = f"My pages count: {len(response.json().get('pages', []))}" if success and response else "Failed to get my pages"
        self.log_result(38, "/api/me/pages", "GET", response.status_code if response else 500,
                       response_time, success, details)

        # Test 39: GET /api/me/pages/following - Pages I follow
        response, response_time, success = self.make_request("GET", "/api/me/pages/following", headers=self.get_headers(self.token2))
        details = f"Following pages count: {len(response.json().get('pages', []))}" if success and response else "Failed to get following pages"
        self.log_result(39, "/api/me/pages/following", "GET", response.status_code if response else 500,
                       response_time, success, details)

        # Test 40: POST /api/admin/pages/{pageId}/verify - Verify page
        if self.page_id:
            response, response_time, success = self.make_request(
                "POST", f"/api/admin/pages/{self.page_id}/verify",
                headers=self.get_headers(self.token1)
            )
            details = "Page verified successfully" if success else "Failed to verify page"
        else:
            response, response_time, success = None, 0, False
            details = "No page ID available"
        self.log_result(40, f"/api/admin/pages/{self.page_id or 'N/A'}/verify", "POST", response.status_code if response else 404,
                       response_time, success, details)

        # Test 41: DELETE /api/admin/pages/{pageId}/verify - Unverify page
        if self.page_id:
            response, response_time, success = self.make_request(
                "DELETE", f"/api/admin/pages/{self.page_id}/verify",
                headers=self.get_headers(self.token1)
            )
            details = "Page unverified successfully" if success else "Failed to unverify page"
        else:
            response, response_time, success = None, 0, False
            details = "No page ID available"
        self.log_result(41, f"/api/admin/pages/{self.page_id or 'N/A'}/verify", "DELETE", response.status_code if response else 404,
                       response_time, success, details)

        # Test 42: POST /api/admin/pages/{pageId}/feature - Feature page
        if self.page_id:
            response, response_time, success = self.make_request(
                "POST", f"/api/admin/pages/{self.page_id}/feature",
                headers=self.get_headers(self.token1)
            )
            details = "Page featured successfully" if success else "Failed to feature page"
        else:
            response, response_time, success = None, 0, False
            details = "No page ID available"
        self.log_result(42, f"/api/admin/pages/{self.page_id or 'N/A'}/feature", "POST", response.status_code if response else 404,
                       response_time, success, details)

        # Test 43: DELETE /api/admin/pages/{pageId}/feature - Unfeature page
        if self.page_id:
            response, response_time, success = self.make_request(
                "DELETE", f"/api/admin/pages/{self.page_id}/feature",
                headers=self.get_headers(self.token1)
            )
            details = "Page unfeatured successfully" if success else "Failed to unfeature page"
        else:
            response, response_time, success = None, 0, False
            details = "No page ID available"
        self.log_result(43, f"/api/admin/pages/{self.page_id or 'N/A'}/feature", "DELETE", response.status_code if response else 404,
                       response_time, success, details)

        # Test 44: GET /api/admin/pages/analytics - Page analytics
        response, response_time, success = self.make_request("GET", "/api/admin/pages/analytics", headers=self.get_headers(self.token1))
        details = "Page analytics retrieved" if success and response else "Failed to get page analytics"
        self.log_result(44, "/api/admin/pages/analytics", "GET", response.status_code if response else 500,
                       response_time, success, details)

        # Test 45: DELETE /api/pages/{pageId} - Delete page
        if self.page_id:
            response, response_time, success = self.make_request(
                "DELETE", f"/api/pages/{self.page_id}",
                headers=self.get_headers(self.token1)
            )
            details = "Page deleted successfully" if success else "Failed to delete page"
        else:
            response, response_time, success = None, 0, False
            details = "No page ID available"
        self.log_result(45, f"/api/pages/{self.page_id or 'N/A'}", "DELETE", response.status_code if response else 404,
                       response_time, success, details)

    def print_summary(self):
        """Print comprehensive test summary."""
        print("\n" + "="*80)
        print("🏁 BATCH 6 TESTING SUMMARY")
        print("="*80)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        slow_tests = [r for r in self.results if r['slow']]
        
        print(f"📊 OVERALL STATS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Slow Tests (>500ms): {len(slow_tests)}")
        
        if slow_tests:
            print(f"\n🐌 SLOW ENDPOINTS (>500ms):")
            for test in slow_tests:
                print(f"   Test {test['test_num']:2d}: {test['method']} {test['endpoint']} ({test['response_time']}ms)")
        
        # Events vs Pages breakdown
        events_tests = [r for r in self.results if r['test_num'] <= 20]
        pages_tests = [r for r in self.results if r['test_num'] > 20]
        
        events_passed = sum(1 for r in events_tests if r['success'])
        pages_passed = sum(1 for r in pages_tests if r['success'])
        
        print(f"\n📈 CATEGORY BREAKDOWN:")
        print(f"   Events (Tests 1-20): {events_passed}/20 ({(events_passed/20)*100:.1f}%)")
        print(f"   Pages (Tests 21-45): {pages_passed}/25 ({(pages_passed/25)*100:.1f}%)")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for test in self.results:
                if not test['success']:
                    print(f"   Test {test['test_num']:2d}: {test['method']} {test['endpoint']} - {test['details']}")
        
        print("\n✅ CRITICAL FEATURES:")
        print("   - Authentication: Working (both admin and regular users)")
        print("   - Events CRUD: Tested")
        print("   - Pages CRUD: Tested")  
        print("   - RSVP System: Tested")
        print("   - Follow System: Tested")
        print("   - Admin Operations: Tested")
        print("   - Performance: Response times recorded")
        
        print("="*80)

    def run_all_tests(self):
        """Run the complete test suite."""
        print(f"🚀 Starting BATCH 6: Events + Pages Testing")
        print(f"🌐 Base URL: {BASE_URL}")
        print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if not self.authenticate():
            print("❌ Authentication failed, aborting tests")
            return
            
        self.test_events()
        self.test_pages()
        self.print_summary()
        
        print(f"\n🏁 Testing completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    runner = TestRunner()
    runner.run_all_tests()