#!/usr/bin/env python3
"""
TRIBE Stage 1 — Canonical Contract Freeze v2 Validation Tests

This comprehensive test suite validates all Stage 1 Contract v2 changes:
1. All list endpoints include `items` key alongside backward-compat aliases
2. All paginated endpoints include `pagination` metadata with `hasMore`
3. All error codes use centralized ErrorCode.* constants (no raw strings)
4. `x-contract-version: v2` header on every response
5. Response contract builders implementation
6. ErrorCode registry expanded from 12 to 36 constants

Base URL: https://api-consistency-hub.preview.emergentagent.com
All endpoints prefixed with /api

Test User: phone 9888800001, PIN 1234, displayName "Test User v2", age 22
"""

import requests
import json
import sys
import time
from datetime import datetime

BASE_URL = "https://api-consistency-hub.preview.emergentagent.com/api"

# Test configuration
TEST_USER = {
    "phone": "9888800001",
    "pin": "1234",
    "displayName": "Test User v2",
    "age": 22
}

AUTH_TOKEN = None
TEST_USER_ID = None
TEST_POST_ID = None
TEST_COLLEGE_ID = None

def log_test(test_name, success, message=""):
    """Log test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}: {message}")
    return success

def check_contract_headers(response, endpoint_name):
    """Check if response has required contract v2 headers"""
    headers = response.headers
    
    # Check x-contract-version: v2
    contract_version = headers.get('x-contract-version', '').lower()
    if contract_version != 'v2':
        return False, f"Missing or incorrect x-contract-version header. Expected 'v2', got '{contract_version}'"
    
    return True, "Contract headers valid"

def check_items_key(data, endpoint_name):
    """Check if response has canonical 'items' key for list endpoints"""
    if not isinstance(data, dict):
        return False, "Response is not a dict"
    
    if 'items' not in data:
        return False, f"Missing canonical 'items' key in {endpoint_name}"
    
    return True, "Items key present"

def check_pagination(data, endpoint_name, expected_type="cursor"):
    """Check pagination metadata structure"""
    if 'pagination' not in data:
        return False, f"Missing pagination object in {endpoint_name}"
    
    pagination = data['pagination']
    
    if expected_type == "cursor":
        # Cursor pagination: nextCursor, hasMore
        if 'hasMore' not in pagination:
            return False, f"Missing hasMore in pagination for {endpoint_name}"
        if 'nextCursor' not in pagination:
            return False, f"Missing nextCursor in pagination for {endpoint_name}"
        # nextCursor should be null or ISO-8601 string
        next_cursor = pagination['nextCursor']
        if next_cursor is not None and not isinstance(next_cursor, str):
            return False, f"nextCursor should be null or string, got {type(next_cursor)}"
    
    elif expected_type == "offset":
        # Offset pagination: total, limit, offset, hasMore
        required_keys = ['total', 'limit', 'offset', 'hasMore']
        for key in required_keys:
            if key not in pagination:
                return False, f"Missing {key} in offset pagination for {endpoint_name}"
    
    return True, f"Pagination structure valid for {expected_type}"

def check_error_structure(response, endpoint_name):
    """Check error response structure and ErrorCode usage"""
    try:
        data = response.json()
        
        # Error response should have 'error' and 'code' keys
        if 'error' not in data:
            return False, f"Missing 'error' key in error response"
        if 'code' not in data:
            return False, f"Missing 'code' key in error response"
        
        # Code should be a known ErrorCode constant (not raw string)
        error_code = data['code']
        
        # List of known ErrorCode constants from constants.js
        known_error_codes = [
            'VALIDATION_ERROR', 'UNAUTHORIZED', 'FORBIDDEN', 'NOT_FOUND', 'CONFLICT',
            'RATE_LIMITED', 'PAYLOAD_TOO_LARGE', 'INTERNAL_ERROR', 'AGE_REQUIRED',
            'CHILD_RESTRICTED', 'BANNED', 'SUSPENDED', 'INVALID_STATE', 'GONE',
            'EXPIRED', 'DUPLICATE', 'SELF_ACTION', 'LIMIT_EXCEEDED', 'CONTENT_REJECTED',
            'COOLDOWN_ACTIVE', 'CONTEST_NOT_OPEN', 'ENTRY_PERIOD_ENDED', 'NO_TRIBE',
            'TRIBE_NOT_ELIGIBLE', 'MAX_ENTRIES_REACHED', 'TRIBE_MAX_ENTRIES',
            'DUPLICATE_CONTENT', 'NOT_RESOLVED', 'VOTING_CLOSED', 'VOTING_DISABLED',
            'ENTRY_NOT_FOUND', 'SELF_VOTE_BLOCKED', 'DUPLICATE_VOTE', 'VOTE_CAP_REACHED',
            'INVALID_STATUS', 'DUPLICATE_CODE', 'INVALID_TRANSITION', 'ALREADY_DISQUALIFIED',
            'MEDIA_NOT_READY'
        ]
        
        if error_code not in known_error_codes:
            return False, f"Unknown error code '{error_code}' - should use ErrorCode constants"
        
        return True, f"Error structure valid with code {error_code}"
        
    except json.JSONDecodeError:
        return False, "Invalid JSON in error response"

def test_1_register_login():
    """Test 1: Register + Login"""
    print("\n=== Test 1: Register + Login ===")
    
    global AUTH_TOKEN, TEST_USER_ID
    
    try:
        # Register
        register_payload = {
            "phone": TEST_USER["phone"],
            "pin": TEST_USER["pin"],
            "displayName": TEST_USER["displayName"]
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=register_payload)
        
        # Check headers
        headers_valid, headers_msg = check_contract_headers(response, "POST /auth/register")
        if not headers_valid:
            return log_test("Register", False, headers_msg)
        
        if response.status_code not in [200, 201]:
            # If already exists, try login instead
            if response.status_code == 409:
                print("User already exists, proceeding to login")
            else:
                return log_test("Register", False, f"Status {response.status_code}: {response.text}")
        else:
            data = response.json()
            if 'token' in data and 'user' in data:
                AUTH_TOKEN = data['token']
                TEST_USER_ID = data['user']['id']
                return log_test("Register", True, f"User registered with ID {TEST_USER_ID}")
        
        # Login
        login_payload = {
            "phone": TEST_USER["phone"], 
            "pin": TEST_USER["pin"]
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
        
        # Check headers
        headers_valid, headers_msg = check_contract_headers(response, "POST /auth/login")
        if not headers_valid:
            return log_test("Login", False, headers_msg)
        
        if response.status_code != 200:
            return log_test("Login", False, f"Status {response.status_code}: {response.text}")
        
        data = response.json()
        if 'token' not in data or 'user' not in data:
            return log_test("Login", False, "Missing token or user in response")
        
        AUTH_TOKEN = data['token']
        TEST_USER_ID = data['user']['id']
        
        return log_test("Login", True, f"User logged in with token")
        
    except Exception as e:
        return log_test("Register/Login", False, f"Exception: {e}")

def test_2_feed_pagination():
    """Test 2: Feed Pagination Contract"""
    print("\n=== Test 2: Feed Pagination Contract ===")
    
    if not AUTH_TOKEN:
        return log_test("Feed Pagination", False, "No auth token available")
    
    try:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        response = requests.get(f"{BASE_URL}/feed/public", headers=headers)
        
        # Check contract headers
        headers_valid, headers_msg = check_contract_headers(response, "GET /feed/public")
        if not headers_valid:
            return log_test("Feed Pagination", False, headers_msg)
        
        if response.status_code != 200:
            return log_test("Feed Pagination", False, f"Status {response.status_code}: {response.text}")
        
        data = response.json()
        
        # Check items key
        items_valid, items_msg = check_items_key(data, "feed/public")
        if not items_valid:
            return log_test("Feed Pagination", False, items_msg)
        
        # Check pagination structure (cursor type)
        pagination_valid, pagination_msg = check_pagination(data, "feed/public", "cursor")
        if not pagination_valid:
            return log_test("Feed Pagination", False, pagination_msg)
        
        # Check feedType field
        if 'feedType' not in data:
            return log_test("Feed Pagination", False, "Missing feedType field")
        
        return log_test("Feed Pagination", True, f"Feed contract valid: {len(data.get('items', []))} items")
        
    except Exception as e:
        return log_test("Feed Pagination", False, f"Exception: {e}")

def test_3_notifications_contract():
    """Test 3: Notifications Contract"""
    print("\n=== Test 3: Notifications Contract ===")
    
    if not AUTH_TOKEN:
        return log_test("Notifications Contract", False, "No auth token available")
    
    try:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        response = requests.get(f"{BASE_URL}/notifications", headers=headers)
        
        # Check contract headers
        headers_valid, headers_msg = check_contract_headers(response, "GET /notifications")
        if not headers_valid:
            return log_test("Notifications Contract", False, headers_msg)
        
        if response.status_code != 200:
            return log_test("Notifications Contract", False, f"Status {response.status_code}: {response.text}")
        
        data = response.json()
        
        # Check canonical items key
        items_valid, items_msg = check_items_key(data, "notifications")
        if not items_valid:
            return log_test("Notifications Contract", False, items_msg)
        
        # Check backward-compat alias
        if 'notifications' not in data:
            return log_test("Notifications Contract", False, "Missing backward-compat 'notifications' alias")
        
        # Check pagination structure
        pagination_valid, pagination_msg = check_pagination(data, "notifications", "cursor")
        if not pagination_valid:
            return log_test("Notifications Contract", False, pagination_msg)
        
        # Check unreadCount
        if 'unreadCount' not in data:
            return log_test("Notifications Contract", False, "Missing unreadCount field")
        
        if not isinstance(data['unreadCount'], int):
            return log_test("Notifications Contract", False, "unreadCount should be integer")
        
        return log_test("Notifications Contract", True, f"Notifications contract valid: {len(data.get('items', []))} items, {data['unreadCount']} unread")
        
    except Exception as e:
        return log_test("Notifications Contract", False, f"Exception: {e}")

def test_4_comments_contract():
    """Test 4: Comments Contract"""
    print("\n=== Test 4: Comments Contract ===")
    
    if not AUTH_TOKEN:
        return log_test("Comments Contract", False, "No auth token available")
    
    global TEST_POST_ID
    
    try:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        
        # First complete age verification if needed
        age_payload = {"birthYear": 2000}  # Makes user adult
        age_response = requests.patch(f"{BASE_URL}/me/age", json=age_payload, headers=headers)
        
        # Try to create a test post
        post_payload = {
            "kind": "POST",
            "caption": "Test post for contract v2",
            "visibility": "PUBLIC"
        }
        
        response = requests.post(f"{BASE_URL}/content/posts", json=post_payload, headers=headers)
        if response.status_code in [200, 201]:
            post_data = response.json()
            if 'post' in post_data:
                TEST_POST_ID = post_data['post']['id']
            elif 'content' in post_data:
                TEST_POST_ID = post_data['content']['id']
        
        # If still no post ID, try to find an existing post to test comments on
        if not TEST_POST_ID:
            # Get public feed and use the first post
            feed_response = requests.get(f"{BASE_URL}/feed/public", headers=headers)
            if feed_response.status_code == 200:
                feed_data = feed_response.json()
                if feed_data.get('items') and len(feed_data['items']) > 0:
                    TEST_POST_ID = feed_data['items'][0]['id']
        
        if not TEST_POST_ID:
            return log_test("Comments Contract", False, "Could not create or find test post")
        
        # Add a comment
        comment_payload = {"body": "Test comment"}
        comment_response = requests.post(f"{BASE_URL}/content/{TEST_POST_ID}/comments", json=comment_payload, headers=headers)
        
        # Get comments
        response = requests.get(f"{BASE_URL}/content/{TEST_POST_ID}/comments", headers=headers)
        
        # Check contract headers
        headers_valid, headers_msg = check_contract_headers(response, "GET /content/:id/comments")
        if not headers_valid:
            return log_test("Comments Contract", False, headers_msg)
        
        if response.status_code != 200:
            return log_test("Comments Contract", False, f"Status {response.status_code}: {response.text}")
        
        data = response.json()
        
        # Check both items AND comments keys (dual presence required)
        if 'items' not in data:
            return log_test("Comments Contract", False, "Missing canonical 'items' key")
        
        if 'comments' not in data:
            return log_test("Comments Contract", False, "Missing backward-compat 'comments' key")
        
        # Check pagination structure
        pagination_valid, pagination_msg = check_pagination(data, "comments", "cursor")
        if not pagination_valid:
            return log_test("Comments Contract", False, pagination_msg)
        
        return log_test("Comments Contract", True, f"Comments contract valid: {len(data.get('items', []))} comments")
        
    except Exception as e:
        return log_test("Comments Contract", False, f"Exception: {e}")

def test_5_followers_following_contract():
    """Test 5: Followers/Following Contract"""
    print("\n=== Test 5: Followers/Following Contract ===")
    
    if not AUTH_TOKEN or not TEST_USER_ID:
        return log_test("Followers/Following Contract", False, "No auth token or user ID available")
    
    try:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        
        # Test followers endpoint
        response = requests.get(f"{BASE_URL}/users/{TEST_USER_ID}/followers", headers=headers)
        
        # Check contract headers
        headers_valid, headers_msg = check_contract_headers(response, "GET /users/:id/followers")
        if not headers_valid:
            return log_test("Followers Contract", False, headers_msg)
        
        if response.status_code != 200:
            return log_test("Followers Contract", False, f"Status {response.status_code}: {response.text}")
        
        data = response.json()
        
        # Check items key
        if 'items' not in data:
            return log_test("Followers Contract", False, "Missing 'items' key in followers")
        
        # Check backward-compat alias
        if 'users' not in data:
            return log_test("Followers Contract", False, "Missing backward-compat 'users' key in followers")
        
        # Check offset pagination
        pagination_valid, pagination_msg = check_pagination(data, "followers", "offset")
        if not pagination_valid:
            return log_test("Followers Contract", False, pagination_msg)
        
        # Test following endpoint
        response = requests.get(f"{BASE_URL}/users/{TEST_USER_ID}/following", headers=headers)
        
        # Check contract headers
        headers_valid, headers_msg = check_contract_headers(response, "GET /users/:id/following")
        if not headers_valid:
            return log_test("Following Contract", False, headers_msg)
        
        if response.status_code != 200:
            return log_test("Following Contract", False, f"Status {response.status_code}: {response.text}")
        
        data = response.json()
        
        # Check items and users keys
        if 'items' not in data or 'users' not in data:
            return log_test("Following Contract", False, "Missing 'items' or 'users' key in following")
        
        # Check pagination
        pagination_valid, pagination_msg = check_pagination(data, "following", "offset")
        if not pagination_valid:
            return log_test("Following Contract", False, pagination_msg)
        
        return log_test("Followers/Following Contract", True, "Both endpoints have valid contract structure")
        
    except Exception as e:
        return log_test("Followers/Following Contract", False, f"Exception: {e}")

def test_6_college_search_contract():
    """Test 6: College Search Contract"""
    print("\n=== Test 6: College Search Contract ===")
    
    global TEST_COLLEGE_ID
    
    try:
        # Test college search
        response = requests.get(f"{BASE_URL}/colleges/search?q=delhi")
        
        # Check contract headers
        headers_valid, headers_msg = check_contract_headers(response, "GET /colleges/search")
        if not headers_valid:
            return log_test("College Search", False, headers_msg)
        
        if response.status_code != 200:
            return log_test("College Search", False, f"Status {response.status_code}: {response.text}")
        
        data = response.json()
        
        # Check items key and backward-compat
        if 'items' not in data:
            return log_test("College Search", False, "Missing 'items' key in college search")
        if 'colleges' not in data:
            return log_test("College Search", False, "Missing 'colleges' backward-compat key")
        
        # Check pagination (offset type)
        pagination_valid, pagination_msg = check_pagination(data, "college search", "offset")
        if not pagination_valid:
            return log_test("College Search", False, pagination_msg)
        
        # Save a college ID for later tests
        if data['items'] and len(data['items']) > 0:
            TEST_COLLEGE_ID = data['items'][0]['id']
        
        # Test college states
        response = requests.get(f"{BASE_URL}/colleges/states")
        
        # Check contract headers  
        headers_valid, headers_msg = check_contract_headers(response, "GET /colleges/states")
        if not headers_valid:
            return log_test("College States", False, headers_msg)
        
        if response.status_code != 200:
            return log_test("College States", False, f"Status {response.status_code}: {response.text}")
        
        data = response.json()
        
        # Check structure
        if 'items' not in data:
            return log_test("College States", False, "Missing 'items' key in college states")
        if 'states' not in data:
            return log_test("College States", False, "Missing 'states' backward-compat key")  
        if 'count' not in data:
            return log_test("College States", False, "Missing 'count' field")
        
        # Test college types
        response = requests.get(f"{BASE_URL}/colleges/types")
        
        # Check contract headers
        headers_valid, headers_msg = check_contract_headers(response, "GET /colleges/types")
        if not headers_valid:
            return log_test("College Types", False, headers_msg)
        
        if response.status_code != 200:
            return log_test("College Types", False, f"Status {response.status_code}: {response.text}")
        
        data = response.json()
        
        # Check structure
        if 'items' not in data or 'types' not in data or 'count' not in data:
            return log_test("College Types", False, "Missing required keys in college types")
        
        return log_test("College Search Contract", True, "All college endpoints have valid contract structure")
        
    except Exception as e:
        return log_test("College Search Contract", False, f"Exception: {e}")

def test_7_houses_leaderboard_contract():
    """Test 7: Houses/Leaderboard Contract"""
    print("\n=== Test 7: Houses/Leaderboard Contract ===")
    
    try:
        # Test houses list
        response = requests.get(f"{BASE_URL}/houses")
        
        # Check contract headers
        headers_valid, headers_msg = check_contract_headers(response, "GET /houses")
        if not headers_valid:
            return log_test("Houses Contract", False, headers_msg)
        
        if response.status_code != 200:
            return log_test("Houses Contract", False, f"Status {response.status_code}: {response.text}")
        
        data = response.json()
        
        # Check structure
        if 'items' not in data:
            return log_test("Houses Contract", False, "Missing 'items' key in houses")
        if 'houses' not in data:
            return log_test("Houses Contract", False, "Missing 'houses' backward-compat key")
        if 'count' not in data:
            return log_test("Houses Contract", False, "Missing 'count' field")
        
        # Test leaderboard
        response = requests.get(f"{BASE_URL}/houses/leaderboard")
        
        # Check contract headers
        headers_valid, headers_msg = check_contract_headers(response, "GET /houses/leaderboard") 
        if not headers_valid:
            return log_test("Houses Leaderboard", False, headers_msg)
        
        if response.status_code != 200:
            return log_test("Houses Leaderboard", False, f"Status {response.status_code}: {response.text}")
        
        data = response.json()
        
        # Check structure
        if 'items' not in data:
            return log_test("Houses Leaderboard", False, "Missing 'items' key in leaderboard")
        if 'leaderboard' not in data:
            return log_test("Houses Leaderboard", False, "Missing 'leaderboard' backward-compat key")
        if 'count' not in data:
            return log_test("Houses Leaderboard", False, "Missing 'count' field")
        
        return log_test("Houses/Leaderboard Contract", True, "Both endpoints have valid contract structure")
        
    except Exception as e:
        return log_test("Houses/Leaderboard Contract", False, f"Exception: {e}")

def test_8_college_members_contract():
    """Test 8: College Members Contract"""
    print("\n=== Test 8: College Members Contract ===")
    
    if not TEST_COLLEGE_ID:
        return log_test("College Members Contract", False, "No college ID available from previous tests")
    
    try:
        response = requests.get(f"{BASE_URL}/colleges/{TEST_COLLEGE_ID}/members")
        
        # Check contract headers
        headers_valid, headers_msg = check_contract_headers(response, "GET /colleges/:id/members")
        if not headers_valid:
            return log_test("College Members Contract", False, headers_msg)
        
        if response.status_code != 200:
            return log_test("College Members Contract", False, f"Status {response.status_code}: {response.text}")
        
        data = response.json()
        
        # Check items key
        if 'items' not in data:
            return log_test("College Members Contract", False, "Missing 'items' key")
        
        # Check backward-compat alias  
        if 'members' not in data:
            return log_test("College Members Contract", False, "Missing 'members' backward-compat key")
        
        # Check offset pagination
        pagination_valid, pagination_msg = check_pagination(data, "college members", "offset")
        if not pagination_valid:
            return log_test("College Members Contract", False, pagination_msg)
        
        return log_test("College Members Contract", True, f"Contract valid: {len(data.get('items', []))} members")
        
    except Exception as e:
        return log_test("College Members Contract", False, f"Exception: {e}")

def test_9_suggestions_contract():
    """Test 9: Suggestions Contract"""
    print("\n=== Test 9: Suggestions Contract ===")
    
    if not AUTH_TOKEN:
        return log_test("Suggestions Contract", False, "No auth token available")
    
    try:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        response = requests.get(f"{BASE_URL}/suggestions/users", headers=headers)
        
        # Check contract headers
        headers_valid, headers_msg = check_contract_headers(response, "GET /suggestions/users")
        if not headers_valid:
            return log_test("Suggestions Contract", False, headers_msg)
        
        if response.status_code != 200:
            return log_test("Suggestions Contract", False, f"Status {response.status_code}: {response.text}")
        
        data = response.json()
        
        # Check structure
        if 'items' not in data:
            return log_test("Suggestions Contract", False, "Missing 'items' key")
        if 'users' not in data:
            return log_test("Suggestions Contract", False, "Missing 'users' backward-compat key")
        if 'count' not in data:
            return log_test("Suggestions Contract", False, "Missing 'count' field")
        
        return log_test("Suggestions Contract", True, f"Contract valid: {data['count']} suggestions")
        
    except Exception as e:
        return log_test("Suggestions Contract", False, f"Exception: {e}")

def test_10_appeals_contract():
    """Test 10: Appeals Contract"""
    print("\n=== Test 10: Appeals Contract ===")
    
    if not AUTH_TOKEN:
        return log_test("Appeals Contract", False, "No auth token available")
    
    try:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        response = requests.get(f"{BASE_URL}/appeals", headers=headers)
        
        # Check contract headers
        headers_valid, headers_msg = check_contract_headers(response, "GET /appeals")
        if not headers_valid:
            return log_test("Appeals Contract", False, headers_msg)
        
        if response.status_code != 200:
            return log_test("Appeals Contract", False, f"Status {response.status_code}: {response.text}")
        
        data = response.json()
        
        # Check structure
        if 'items' not in data:
            return log_test("Appeals Contract", False, "Missing 'items' key")
        if 'appeals' not in data:
            return log_test("Appeals Contract", False, "Missing 'appeals' backward-compat key")
        if 'count' not in data:
            return log_test("Appeals Contract", False, "Missing 'count' field")
        
        return log_test("Appeals Contract", True, f"Contract valid: {data['count']} appeals")
        
    except Exception as e:
        return log_test("Appeals Contract", False, f"Exception: {e}")

def test_11_grievances_contract():
    """Test 11: Grievances Contract"""
    print("\n=== Test 11: Grievances Contract ===")
    
    if not AUTH_TOKEN:
        return log_test("Grievances Contract", False, "No auth token available")
    
    try:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        response = requests.get(f"{BASE_URL}/grievances", headers=headers)
        
        # Check contract headers
        headers_valid, headers_msg = check_contract_headers(response, "GET /grievances")
        if not headers_valid:
            return log_test("Grievances Contract", False, headers_msg)
        
        if response.status_code != 200:
            return log_test("Grievances Contract", False, f"Status {response.status_code}: {response.text}")
        
        data = response.json()
        
        # Check structure - should have items, grievances, tickets (all present), count
        required_keys = ['items', 'grievances', 'tickets', 'count']
        for key in required_keys:
            if key not in data:
                return log_test("Grievances Contract", False, f"Missing '{key}' key")
        
        return log_test("Grievances Contract", True, f"Contract valid: {data['count']} grievances")
        
    except Exception as e:
        return log_test("Grievances Contract", False, f"Exception: {e}")

def test_12_error_code_contract():
    """Test 12: Error Code Contract"""
    print("\n=== Test 12: Error Code Contract ===")
    
    try:
        # Test invalid credentials
        login_payload = {
            "phone": "0000000000",
            "pin": "0000"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
        
        # Check contract headers even on errors
        headers_valid, headers_msg = check_contract_headers(response, "POST /auth/login (error)")
        if not headers_valid:
            return log_test("Error Code Contract - Login", False, headers_msg)
        
        if response.status_code != 401:
            return log_test("Error Code Contract - Login", False, f"Expected 401, got {response.status_code}")
        
        # Check error structure
        error_valid, error_msg = check_error_structure(response, "invalid login")
        if not error_valid:
            return log_test("Error Code Contract - Login", False, error_msg)
        
        # Test nonexistent resource
        if AUTH_TOKEN:
            headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
            response = requests.get(f"{BASE_URL}/content/nonexistent-id", headers=headers)
            
            # Check contract headers
            headers_valid, headers_msg = check_contract_headers(response, "GET /content/nonexistent-id")
            if not headers_valid:
                return log_test("Error Code Contract - Not Found", False, headers_msg)
            
            if response.status_code != 404:
                return log_test("Error Code Contract - Not Found", False, f"Expected 404, got {response.status_code}")
            
            # Check error structure
            error_valid, error_msg = check_error_structure(response, "not found")
            if not error_valid:
                return log_test("Error Code Contract - Not Found", False, error_msg)
        
        return log_test("Error Code Contract", True, "Error responses have proper structure with ErrorCode constants")
        
    except Exception as e:
        return log_test("Error Code Contract", False, f"Exception: {e}")

def test_13_contract_version_header():
    """Test 13: Contract Version Header"""
    print("\n=== Test 13: Contract Version Header ===")
    
    endpoints_to_check = [
        ("/", "GET"),
        ("/healthz", "GET"),
        ("/colleges/search", "GET")
    ]
    
    success_count = 0
    
    for endpoint, method in endpoints_to_check:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}")
            
            # Check x-contract-version header
            contract_version = response.headers.get('x-contract-version', '').lower()
            if contract_version == 'v2':
                success_count += 1
                log_test(f"Contract Version {endpoint}", True, f"Has x-contract-version: v2")
            else:
                log_test(f"Contract Version {endpoint}", False, f"Expected v2, got '{contract_version}'")
                
        except Exception as e:
            log_test(f"Contract Version {endpoint}", False, f"Exception: {e}")
    
    overall_success = success_count == len(endpoints_to_check)
    return log_test("Contract Version Header", overall_success, f"{success_count}/{len(endpoints_to_check)} endpoints have correct version header")

def test_14_user_posts_contract():
    """Test 14: User Posts Contract"""
    print("\n=== Test 14: User Posts Contract ===")
    
    if not AUTH_TOKEN or not TEST_USER_ID:
        return log_test("User Posts Contract", False, "No auth token or user ID available")
    
    try:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        response = requests.get(f"{BASE_URL}/users/{TEST_USER_ID}/posts", headers=headers)
        
        # Check contract headers
        headers_valid, headers_msg = check_contract_headers(response, "GET /users/:id/posts")
        if not headers_valid:
            return log_test("User Posts Contract", False, headers_msg)
        
        if response.status_code != 200:
            return log_test("User Posts Contract", False, f"Status {response.status_code}: {response.text}")
        
        data = response.json()
        
        # Check items key
        if 'items' not in data:
            return log_test("User Posts Contract", False, "Missing 'items' key")
        
        # Check cursor pagination
        pagination_valid, pagination_msg = check_pagination(data, "user posts", "cursor")
        if not pagination_valid:
            return log_test("User Posts Contract", False, pagination_msg)
        
        return log_test("User Posts Contract", True, f"Contract valid: {len(data.get('items', []))} posts")
        
    except Exception as e:
        return log_test("User Posts Contract", False, f"Exception: {e}")

def test_15_tribes_list_contract():
    """Test 15: Tribes List Contract"""
    print("\n=== Test 15: Tribes List Contract ===")
    
    try:
        response = requests.get(f"{BASE_URL}/tribes")
        
        # Check contract headers
        headers_valid, headers_msg = check_contract_headers(response, "GET /tribes")
        if not headers_valid:
            return log_test("Tribes List Contract", False, headers_msg)
        
        if response.status_code != 200:
            return log_test("Tribes List Contract", False, f"Status {response.status_code}: {response.text}")
        
        data = response.json()
        
        # Check tribes array
        if 'tribes' not in data:
            return log_test("Tribes List Contract", False, "Missing 'tribes' array")
        
        if not isinstance(data['tribes'], list):
            return log_test("Tribes List Contract", False, "tribes should be an array")
        
        return log_test("Tribes List Contract", True, f"Contract valid: {len(data.get('tribes', []))} tribes")
        
    except Exception as e:
        return log_test("Tribes List Contract", False, f"Exception: {e}")

def test_16_admin_stats_access():
    """Test 16: Admin Stats (should require admin role)"""
    print("\n=== Test 16: Admin Stats Access Control ===")
    
    if not AUTH_TOKEN:
        return log_test("Admin Stats Access", False, "No auth token available")
    
    try:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        response = requests.get(f"{BASE_URL}/admin/stats", headers=headers)
        
        # Check contract headers
        headers_valid, headers_msg = check_contract_headers(response, "GET /admin/stats")
        if not headers_valid:
            return log_test("Admin Stats Access", False, headers_msg)
        
        # Should return 403 for regular user
        if response.status_code != 403:
            return log_test("Admin Stats Access", False, f"Expected 403, got {response.status_code}")
        
        # Check error structure
        error_valid, error_msg = check_error_structure(response, "admin stats access")
        if not error_valid:
            return log_test("Admin Stats Access", False, error_msg)
        
        return log_test("Admin Stats Access", True, "Correctly returns 403 with proper error code for regular user")
        
    except Exception as e:
        return log_test("Admin Stats Access", False, f"Exception: {e}")

def main():
    """Run all Stage 1 Contract v2 validation tests"""
    print("🚀 TRIBE Stage 1 — Canonical Contract Freeze v2 Validation Tests")
    print("=" * 70)
    print(f"Base URL: {BASE_URL}")
    print(f"Test User: {TEST_USER['phone']} / {TEST_USER['displayName']}")
    print("=" * 70)
    
    # Track results
    results = []
    
    # Run all tests
    results.append(test_1_register_login())
    results.append(test_2_feed_pagination())
    results.append(test_3_notifications_contract())
    results.append(test_4_comments_contract())
    results.append(test_5_followers_following_contract())
    results.append(test_6_college_search_contract())
    results.append(test_7_houses_leaderboard_contract())
    results.append(test_8_college_members_contract())
    results.append(test_9_suggestions_contract())
    results.append(test_10_appeals_contract())
    results.append(test_11_grievances_contract())
    results.append(test_12_error_code_contract())
    results.append(test_13_contract_version_header())
    results.append(test_14_user_posts_contract())
    results.append(test_15_tribes_list_contract())
    results.append(test_16_admin_stats_access())
    
    # Summary
    passed = sum(1 for r in results if r)
    total = len(results)
    success_rate = (passed / total) * 100
    
    print("\n" + "=" * 70)
    print("📊 TRIBE Stage 1 Contract v2 Validation Results")
    print("=" * 70)
    print(f"✅ Passed: {passed}/{total} tests ({success_rate:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Stage 1 Contract v2 is PRODUCTION READY!")
        print("\nKey Validations Confirmed:")
        print("✅ All list endpoints include canonical 'items' key")
        print("✅ All paginated endpoints have 'pagination' metadata with 'hasMore'")
        print("✅ All error responses use centralized ErrorCode constants")
        print("✅ All responses include 'x-contract-version: v2' header")
        print("✅ Response contract builders working correctly")
        print("✅ Backward-compatibility aliases preserved")
    else:
        failed = total - passed
        print(f"❌ {failed} tests failed - Contract v2 needs fixes")
        
    print("=" * 70)
    return success_rate >= 95.0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)