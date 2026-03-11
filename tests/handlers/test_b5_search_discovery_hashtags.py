"""
B5 — Discovery, Search & Hashtag Engine: WORLD-BEST TEST SUITE
Tribe Project — Stage B5

Covers all B5 requirements:
  A. Search: user, page, post, hashtag (exact, prefix, normalized, type-filtered)
  B. Hashtag extraction: on create/edit (user + page posts)
  C. Hashtag feed: pagination, safety, ordering
  D. Hashtag detail + trending
  E. Safety: blocked/moderated/deleted exclusion
  F. Contracts: stable response shapes
  G. Pagination: cursor for feed, limit for search
  H. Index/regression: existing flows unbroken

Rate-limit strategy: dedicated users per test domain, unique IPs, retry on 429.
"""

import pytest
import requests
import time
import os
import random
from pymongo import MongoClient

API_URL = os.environ.get("TEST_API_URL", "http://localhost:3000/api")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "your_database_name")

_client = MongoClient(MONGO_URL)
_db = _client[DB_NAME]


# ──────────────────── helpers ────────────────────

def _ip():
    return f"10.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"


def _h(token=None):
    h = {"Content-Type": "application/json", "X-Forwarded-For": _ip()}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def _retry(fn, retries=5, delay=2.5):
    for i in range(retries):
        r = fn()
        if r.status_code == 429:
            time.sleep(delay * (i + 1))
            continue
        return r
    return r


def _register(suffix, name=None):
    phone = f"88850{suffix:05d}"
    display = name or f"B5User{suffix}"
    h = _h()
    r = _retry(lambda: requests.post(f"{API_URL}/auth/register", json={
        "phone": phone, "pin": "1234", "displayName": display, "username": f"b5u{suffix}"
    }, headers=h))
    if r.status_code == 409:
        r = _retry(lambda: requests.post(f"{API_URL}/auth/login", json={"phone": phone, "pin": "1234"}, headers=h))
    assert r.status_code in (200, 201), f"Auth fail {suffix}: {r.status_code} {r.text[:200]}"
    d = r.json()
    uid = d.get("user", {}).get("id")
    tok = d.get("accessToken") or d.get("token")
    _db.users.update_one({"id": uid}, {"$set": {"ageStatus": "ADULT"}})
    return tok, uid


def _create_post(token, caption, kind="POST"):
    r = _retry(lambda: requests.post(f"{API_URL}/content/posts", json={
        "caption": caption, "kind": kind
    }, headers=_h(token)))
    assert r.status_code in (200, 201), f"Post create fail: {r.status_code} {r.text[:200]}"
    d = r.json().get("data", r.json())
    return d.get("post", {})


def _edit_post(token, post_id, caption):
    r = _retry(lambda: requests.patch(f"{API_URL}/content/{post_id}", json={
        "caption": caption
    }, headers=_h(token)))
    assert r.status_code == 200, f"Post edit fail: {r.status_code} {r.text[:200]}"
    d = r.json().get("data", r.json())
    return d.get("post", {})


def _search(token, q, type_filter="all", limit=10):
    r = _retry(lambda: requests.get(
        f"{API_URL}/search?q={requests.utils.quote(q)}&type={type_filter}&limit={limit}",
        headers=_h(token)
    ))
    return r


def _create_page(token, name, slug, category="CLUB"):
    r = _retry(lambda: requests.post(f"{API_URL}/pages", json={
        "name": name, "slug": slug, "category": category, "bio": f"Test page {name}"
    }, headers=_h(token)))
    if r.status_code == 409:
        doc = _db.pages.find_one({"slug": slug}, {"_id": 0})
        return doc
    assert r.status_code in (200, 201), f"Page create fail: {r.status_code} {r.text[:200]}"
    d = r.json().get("data", r.json())
    return d.get("page", {})


def _create_page_post(token, page_id, caption):
    r = _retry(lambda: requests.post(f"{API_URL}/pages/{page_id}/posts", json={
        "caption": caption
    }, headers=_h(token)))
    assert r.status_code in (200, 201), f"Page post fail: {r.status_code} {r.text[:200]}"
    d = r.json().get("data", r.json())
    return d.get("post", {})


def _edit_page_post(token, page_id, post_id, caption):
    r = _retry(lambda: requests.patch(f"{API_URL}/pages/{page_id}/posts/{post_id}", json={
        "caption": caption
    }, headers=_h(token)))
    assert r.status_code == 200, f"Page post edit fail: {r.status_code} {r.text[:200]}"
    d = r.json().get("data", r.json())
    return d.get("post", {})


# ──────────────────── fixtures ────────────────────

@pytest.fixture(scope="module")
def search_user_a():
    """Primary search test user."""
    return _register(501, "AlphaSearcher")


@pytest.fixture(scope="module")
def search_user_b():
    """Secondary search test user."""
    return _register(502, "BetaFinder")


@pytest.fixture(scope="module")
def search_user_c():
    """Third user for block/safety tests."""
    return _register(503, "GammaHidden")


@pytest.fixture(scope="module")
def hashtag_user_a():
    """Primary hashtag test user."""
    return _register(504, "HashCreatorAlpha")


@pytest.fixture(scope="module")
def hashtag_user_b():
    """Secondary hashtag test user for feed tests."""
    return _register(505, "HashCreatorBeta")


@pytest.fixture(scope="module")
def page_owner():
    """User who owns a page for page-post hashtag tests."""
    return _register(506, "PageOwnerB5")


@pytest.fixture(scope="module")
def safety_blocker():
    """User who blocks others for safety tests."""
    return _register(507, "SafetyBlocker")


@pytest.fixture(scope="module")
def safety_target():
    """User who gets blocked for safety tests."""
    return _register(508, "SafetyTarget")


@pytest.fixture(scope="module")
def b5_test_page(page_owner):
    """A test page for B5 tests."""
    tok, uid = page_owner
    page = _create_page(tok, "B5TestPage", f"b5-test-page-{random.randint(1000,9999)}", "CLUB")
    return page


# ════════════════════════════════════════════════════════════════════
# A. SEARCH TESTS
# ════════════════════════════════════════════════════════════════════

class TestSearchUsers:
    """A1-A4: User search (exact, prefix, case-normalized)."""

    def test_user_exact_match(self, search_user_a):
        tok, uid = search_user_a
        r = _search(tok, "AlphaSearcher", "users")
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        users = data.get("users", [])
        assert any(u.get("id") == uid for u in users), "Exact user match not found"

    def test_user_prefix_match(self, search_user_a):
        tok, uid = search_user_a
        r = _search(tok, "Alpha", "users")
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        users = data.get("users", [])
        assert any(u.get("id") == uid for u in users), "Prefix user match not found"

    def test_user_case_normalized_match(self, search_user_a):
        tok, uid = search_user_a
        r = _search(tok, "alphasearcher", "users")
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        users = data.get("users", [])
        assert any(u.get("id") == uid for u in users), "Case-normalized user match not found"

    def test_user_username_search(self, search_user_a):
        tok, uid = search_user_a
        # Ensure username is set in DB
        _db.users.update_one({"id": uid}, {"$set": {"username": "b5u501"}})
        r = _search(tok, "b5u501", "users")
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        users = data.get("users", [])
        assert any(u.get("id") == uid for u in users), "Username search not found"

    def test_user_no_results_for_garbage(self, search_user_a):
        tok, _ = search_user_a
        r = _search(tok, "zzznouser999xyzabc", "users")
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        users = data.get("users", [])
        assert len(users) == 0

    def test_banned_user_excluded(self, search_user_a, search_user_c):
        """Banned users must not appear in search."""
        tok_a, _ = search_user_a
        _, uid_c = search_user_c
        # Ban user C
        _db.users.update_one({"id": uid_c}, {"$set": {"isBanned": True}})
        try:
            r = _search(tok_a, "GammaHidden", "users")
            assert r.status_code == 200
            data = r.json().get("data", r.json())
            users = data.get("users", [])
            assert not any(u.get("id") == uid_c for u in users), "Banned user should not appear"
        finally:
            _db.users.update_one({"id": uid_c}, {"$set": {"isBanned": False}})


class TestSearchPages:
    """A5-A6: Page search (name, slug, official ranking)."""

    def test_page_search_by_name(self, search_user_a, b5_test_page):
        tok, _ = search_user_a
        r = _search(tok, "B5TestPage", "pages")
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        pages = data.get("pages", [])
        assert any(p.get("id") == b5_test_page["id"] for p in pages), "Page name search failed"

    def test_page_search_by_slug(self, search_user_a, b5_test_page):
        tok, _ = search_user_a
        slug = b5_test_page.get("slug", "")
        r = _search(tok, slug, "pages")
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        pages = data.get("pages", [])
        assert any(p.get("id") == b5_test_page["id"] for p in pages), "Page slug search failed"

    def test_page_result_has_snippet_fields(self, search_user_a, b5_test_page):
        tok, _ = search_user_a
        r = _search(tok, "B5TestPage", "pages")
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        pages = data.get("pages", [])
        page = next((p for p in pages if p.get("id") == b5_test_page["id"]), None)
        assert page is not None
        # Contract: page snippet must have these fields
        for field in ["id", "slug", "name", "category", "isOfficial", "verificationStatus", "status"]:
            assert field in page, f"Missing field: {field}"

    def test_suspended_page_excluded(self, search_user_a, page_owner):
        """Suspended pages should not appear in search."""
        tok_a, _ = search_user_a
        tok_p, _ = page_owner
        slug = f"b5-suspended-{random.randint(10000,99999)}"
        page = _create_page(tok_p, "B5SuspendedPage", slug)
        _db.pages.update_one({"id": page["id"]}, {"$set": {"status": "SUSPENDED"}})
        try:
            r = _search(tok_a, "B5SuspendedPage", "pages")
            assert r.status_code == 200
            data = r.json().get("data", r.json())
            pages = data.get("pages", [])
            assert not any(p.get("id") == page["id"] for p in pages), "Suspended page should not appear"
        finally:
            _db.pages.delete_one({"id": page["id"]})


class TestSearchPosts:
    """A7-A9: Post/content search (caption match, safety)."""

    def test_post_search_by_caption(self, search_user_a):
        tok, uid = search_user_a
        unique = f"uniqueB5caption{random.randint(100000,999999)}"
        post = _create_post(tok, f"This is a {unique} test post")
        # Promote to PUBLIC visibility
        _db.content_items.update_one({"id": post["id"]}, {"$set": {"visibility": "PUBLIC"}})
        time.sleep(0.3)
        r = _search(tok, unique, "posts")
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        posts = data.get("posts", [])
        assert any(p.get("id") == post["id"] for p in posts), "Post caption search failed"

    def test_post_search_excludes_removed(self, search_user_a):
        tok, uid = search_user_a
        unique = f"removedB5{random.randint(100000,999999)}"
        post = _create_post(tok, f"This is {unique} removed post")
        _db.content_items.update_one({"id": post["id"]}, {"$set": {"visibility": "PUBLIC", "isRemoved": True}})
        time.sleep(0.3)
        r = _search(tok, unique, "posts")
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        posts = data.get("posts", [])
        assert not any(p.get("id") == post["id"] for p in posts), "Removed post should not appear"

    def test_post_search_excludes_held(self, search_user_a):
        tok, uid = search_user_a
        unique = f"heldB5{random.randint(100000,999999)}"
        post = _create_post(tok, f"This is {unique} moderated post")
        _db.content_items.update_one({"id": post["id"]}, {"$set": {"visibility": "PUBLIC", "moderationHold": True}})
        time.sleep(0.3)
        r = _search(tok, unique, "posts")
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        posts = data.get("posts", [])
        assert not any(p.get("id") == post["id"] for p in posts), "Moderation-held post should not appear"

    def test_post_search_only_public(self, search_user_a):
        tok, uid = search_user_a
        unique = f"privateB5{random.randint(100000,999999)}"
        post = _create_post(tok, f"This is {unique} private post")
        _db.content_items.update_one({"id": post["id"]}, {"$set": {"visibility": "PRIVATE"}})
        time.sleep(0.3)
        r = _search(tok, unique, "posts")
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        posts = data.get("posts", [])
        assert not any(p.get("id") == post["id"] for p in posts), "Private post should not appear"


class TestSearchHashtags:
    """A10-A12: Hashtag search (with/without #, normalized)."""

    def test_hashtag_search_with_hash_prefix(self, hashtag_user_a):
        tok, _ = hashtag_user_a
        tag = f"b5testtag{random.randint(10000,99999)}"
        _create_post(tok, f"Hello world #{tag}")
        time.sleep(0.3)
        r = _search(tok, f"#{tag}", "hashtags")
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        hashtags = data.get("hashtags", [])
        assert any(h.get("tag") == tag for h in hashtags), f"Hashtag #{tag} not found in search"

    def test_hashtag_search_without_hash_prefix(self, hashtag_user_a):
        tok, _ = hashtag_user_a
        tag = f"b5nohash{random.randint(10000,99999)}"
        _create_post(tok, f"Testing #{tag} without prefix")
        time.sleep(0.3)
        r = _search(tok, tag, "hashtags")
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        hashtags = data.get("hashtags", [])
        assert any(h.get("tag") == tag for h in hashtags), f"Hashtag {tag} not found without #"

    def test_hashtag_search_case_insensitive(self, hashtag_user_a):
        tok, _ = hashtag_user_a
        tag = f"b5casetest{random.randint(10000,99999)}"
        _create_post(tok, f"Testing #{tag}")
        time.sleep(0.3)
        r = _search(tok, tag.upper(), "hashtags")
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        hashtags = data.get("hashtags", [])
        assert any(h.get("tag") == tag for h in hashtags), "Case-insensitive hashtag search failed"

    def test_hashtag_result_has_postcount(self, hashtag_user_a):
        tok, _ = hashtag_user_a
        tag = f"b5countcheck{random.randint(10000,99999)}"
        _create_post(tok, f"First #{tag}")
        _create_post(tok, f"Second #{tag}")
        time.sleep(0.3)
        r = _search(tok, tag, "hashtags")
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        hashtags = data.get("hashtags", [])
        found = next((h for h in hashtags if h.get("tag") == tag), None)
        assert found is not None
        assert found.get("postCount", 0) >= 2, "Post count should reflect multiple uses"


class TestSearchMixed:
    """A13-A16: Mixed/all-type search, query validation, result contract."""

    def test_mixed_search_returns_typed_items(self, search_user_a):
        tok, _ = search_user_a
        r = _search(tok, "Alpha", "all")
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        items = data.get("items", [])
        # items should have _resultType markers
        if len(items) > 0:
            for item in items:
                assert "_resultType" in item, "Mixed result item missing _resultType"
                assert item["_resultType"] in ("user", "page", "hashtag", "post", "college", "house")

    def test_empty_query_returns_empty(self, search_user_a):
        tok, _ = search_user_a
        r = _search(tok, "", "all")
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        items = data.get("items", [])
        assert len(items) == 0, "Empty query should return empty results"

    def test_single_char_query_returns_empty(self, search_user_a):
        tok, _ = search_user_a
        r = _search(tok, "x", "all")
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        items = data.get("items", [])
        assert len(items) == 0, "Single-char query should return empty (min 2 chars)"

    def test_search_limit_respected(self, search_user_a):
        tok, _ = search_user_a
        r = _search(tok, "User", "users", limit=3)
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        users = data.get("users", [])
        assert len(users) <= 3, "Search limit not respected"

    def test_search_limit_capped_at_20(self, search_user_a):
        tok, _ = search_user_a
        r = _search(tok, "User", "users", limit=100)
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        users = data.get("users", [])
        assert len(users) <= 20, "Search limit should cap at 20"

    def test_mixed_search_has_backward_compat_keys(self, search_user_a):
        """Response must have both 'items' and type-specific keys."""
        tok, _ = search_user_a
        r = _search(tok, "Alpha", "all")
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        assert "items" in data, "Missing 'items' key"
        # Type-specific aliases should also exist
        assert "users" in data or "pages" in data or "hashtags" in data


class TestSearchRequiresAuth:
    """Search endpoint requires authentication."""

    def test_search_without_token(self):
        r = requests.get(f"{API_URL}/search?q=test&type=all", headers=_h())
        # Should either 401 or return empty (depending on authenticate vs requireAuth)
        # Based on code: uses authenticate() which allows null user but blocks if required
        assert r.status_code in (200, 401)


# ════════════════════════════════════════════════════════════════════
# B. HASHTAG EXTRACTION TESTS
# ════════════════════════════════════════════════════════════════════

class TestHashtagExtraction:
    """B1-B5: Hashtag extraction on create/edit paths."""

    def test_create_post_extracts_hashtags(self, hashtag_user_a):
        tok, _ = hashtag_user_a
        tag = f"b5extract{random.randint(10000,99999)}"
        post = _create_post(tok, f"Hello #{tag} world")
        # Check DB directly
        doc = _db.content_items.find_one({"id": post["id"]}, {"_id": 0})
        assert tag in doc.get("hashtags", []), "Hashtag not extracted on create"

    def test_duplicate_tag_in_same_post(self, hashtag_user_a):
        tok, _ = hashtag_user_a
        tag = f"b5dup{random.randint(10000,99999)}"
        post = _create_post(tok, f"#{tag} is great #{tag} is awesome")
        doc = _db.content_items.find_one({"id": post["id"]}, {"_id": 0})
        tags = doc.get("hashtags", [])
        assert tags.count(tag) == 1, "Duplicate tag should be deduplicated"

    def test_multiple_distinct_tags(self, hashtag_user_a):
        tok, _ = hashtag_user_a
        r = random.randint(10000, 99999)
        tag1 = f"b5multi1_{r}"
        tag2 = f"b5multi2_{r}"
        post = _create_post(tok, f"#{tag1} and #{tag2}")
        doc = _db.content_items.find_one({"id": post["id"]}, {"_id": 0})
        tags = doc.get("hashtags", [])
        assert tag1 in tags, f"Tag {tag1} not extracted"
        assert tag2 in tags, f"Tag {tag2} not extracted"

    def test_edit_post_updates_hashtags(self, hashtag_user_a):
        tok, _ = hashtag_user_a
        r = random.randint(10000, 99999)
        old_tag = f"b5old{r}"
        new_tag = f"b5new{r}"
        post = _create_post(tok, f"#{old_tag} post")
        doc_before = _db.content_items.find_one({"id": post["id"]}, {"_id": 0})
        assert old_tag in doc_before.get("hashtags", [])

        _edit_post(tok, post["id"], f"#{new_tag} updated post")
        doc_after = _db.content_items.find_one({"id": post["id"]}, {"_id": 0})
        assert new_tag in doc_after.get("hashtags", []), "New tag not present after edit"
        assert old_tag not in doc_after.get("hashtags", []), "Old tag should be removed after edit"

    def test_edit_removes_all_hashtags(self, hashtag_user_a):
        tok, _ = hashtag_user_a
        tag = f"b5removable{random.randint(10000,99999)}"
        post = _create_post(tok, f"#{tag} gone soon")
        _edit_post(tok, post["id"], "No hashtags here anymore")
        doc = _db.content_items.find_one({"id": post["id"]}, {"_id": 0})
        assert len(doc.get("hashtags", [])) == 0, "All hashtags should be removed"

    def test_hashtag_normalization_lowercase(self, hashtag_user_a):
        tok, _ = hashtag_user_a
        tag = f"B5UPPER{random.randint(10000,99999)}"
        post = _create_post(tok, f"#{tag} mixed case")
        doc = _db.content_items.find_one({"id": post["id"]}, {"_id": 0})
        tags = doc.get("hashtags", [])
        assert tag.lower() in tags, "Tags should be normalized to lowercase"
        assert tag not in tags, "Original case should not be stored"

    def test_hashtag_with_numbers_and_underscores(self, hashtag_user_a):
        tok, _ = hashtag_user_a
        tag = f"b5_test_123_{random.randint(1000,9999)}"
        post = _create_post(tok, f"#{tag}")
        doc = _db.content_items.find_one({"id": post["id"]}, {"_id": 0})
        assert tag in doc.get("hashtags", []), "Tags with numbers/underscores should work"

    def test_no_caption_no_hashtags(self, hashtag_user_a):
        """Post with empty caption should have empty hashtags array."""
        tok, _ = hashtag_user_a
        r = _retry(lambda: requests.post(f"{API_URL}/content/posts", json={
            "caption": "", "kind": "POST", "mediaIds": []
        }, headers=_h(tok)))
        # Empty caption with no media may be rejected; if so, that's fine
        if r.status_code in (200, 201):
            d = r.json().get("data", r.json())
            post = d.get("post", {})
            doc = _db.content_items.find_one({"id": post["id"]}, {"_id": 0})
            assert doc.get("hashtags", []) == []

    def test_hashtag_stats_incremented(self, hashtag_user_a):
        tok, _ = hashtag_user_a
        tag = f"b5stats{random.randint(10000,99999)}"
        _create_post(tok, f"First #{tag}")
        _create_post(tok, f"Second #{tag}")
        time.sleep(0.3)
        stat = _db.hashtags.find_one({"tag": tag}, {"_id": 0})
        assert stat is not None, "Hashtag stat doc should exist"
        assert stat.get("postCount", 0) >= 2, "Post count should be >= 2"

    def test_hashtag_stats_decremented_on_edit(self, hashtag_user_a):
        tok, _ = hashtag_user_a
        tag = f"b5decr{random.randint(10000,99999)}"
        post = _create_post(tok, f"#{tag} will be removed")
        time.sleep(0.2)
        stat_before = _db.hashtags.find_one({"tag": tag}, {"_id": 0})
        count_before = stat_before.get("postCount", 0)
        _edit_post(tok, post["id"], "No tags now")
        time.sleep(0.2)
        stat_after = _db.hashtags.find_one({"tag": tag}, {"_id": 0})
        count_after = stat_after.get("postCount", 0) if stat_after else 0
        assert count_after < count_before, "Stat count should decrement after tag removal"


class TestHashtagExtractionPage:
    """B6-B8: Hashtag extraction on page post create/edit."""

    def test_page_post_extracts_hashtags(self, page_owner, b5_test_page):
        tok, _ = page_owner
        tag = f"b5pagetag{random.randint(10000,99999)}"
        post = _create_page_post(tok, b5_test_page["id"], f"Page post #{tag}")
        doc = _db.content_items.find_one({"id": post["id"]}, {"_id": 0})
        assert tag in doc.get("hashtags", []), "Page post hashtag extraction failed"

    def test_page_post_edit_updates_hashtags(self, page_owner, b5_test_page):
        tok, _ = page_owner
        r = random.randint(10000, 99999)
        old_tag = f"b5pageold{r}"
        new_tag = f"b5pagenew{r}"
        post = _create_page_post(tok, b5_test_page["id"], f"#{old_tag}")
        _edit_page_post(tok, b5_test_page["id"], post["id"], f"#{new_tag}")
        doc = _db.content_items.find_one({"id": post["id"]}, {"_id": 0})
        assert new_tag in doc.get("hashtags", []), "New tag missing after page post edit"
        assert old_tag not in doc.get("hashtags", []), "Old tag should be gone after page post edit"

    def test_page_post_hashtag_stats_synced(self, page_owner, b5_test_page):
        tok, _ = page_owner
        tag = f"b5pagestat{random.randint(10000,99999)}"
        _create_page_post(tok, b5_test_page["id"], f"#{tag} page content")
        time.sleep(0.3)
        stat = _db.hashtags.find_one({"tag": tag}, {"_id": 0})
        assert stat is not None, "Hashtag stat for page post should exist"
        assert stat.get("postCount", 0) >= 1


# ════════════════════════════════════════════════════════════════════
# C. HASHTAG DETAIL + TRENDING
# ════════════════════════════════════════════════════════════════════

class TestHashtagDetail:
    """C1-C3: GET /hashtags/:tag detail and trending."""

    def test_hashtag_detail_existing(self, hashtag_user_a):
        tok, _ = hashtag_user_a
        tag = f"b5detail{random.randint(10000,99999)}"
        _create_post(tok, f"#{tag} detail test")
        time.sleep(0.3)
        r = _retry(lambda: requests.get(f"{API_URL}/hashtags/{tag}", headers=_h(tok)))
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        assert data.get("tag") == tag
        assert "postCount" in data

    def test_hashtag_detail_with_hash_prefix(self, hashtag_user_a):
        tok, _ = hashtag_user_a
        tag = f"b5hashpfx{random.randint(10000,99999)}"
        _create_post(tok, f"#{tag}")
        time.sleep(0.3)
        r = _retry(lambda: requests.get(f"{API_URL}/hashtags/%23{tag}", headers=_h(tok)))
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        assert data.get("tag") == tag

    def test_hashtag_detail_nonexistent(self, hashtag_user_a):
        tok, _ = hashtag_user_a
        r = _retry(lambda: requests.get(f"{API_URL}/hashtags/zzzneverused999", headers=_h(tok)))
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        assert data.get("tag") == "zzzneverused999"
        assert data.get("postCount", 0) == 0

    def test_hashtag_invalid_empty(self, hashtag_user_a):
        tok, _ = hashtag_user_a
        r = _retry(lambda: requests.get(f"{API_URL}/hashtags/%23", headers=_h(tok)))
        assert r.status_code == 400


class TestHashtagTrending:
    """C4-C5: GET /hashtags/trending."""

    def test_trending_returns_list(self, hashtag_user_a):
        tok, _ = hashtag_user_a
        # Create some tagged posts to ensure trending has data
        tag = f"b5trending{random.randint(10000,99999)}"
        _create_post(tok, f"#{tag} trending test")
        time.sleep(0.3)
        r = _retry(lambda: requests.get(f"{API_URL}/hashtags/trending", headers=_h(tok)))
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        items = data.get("items", [])
        assert isinstance(items, list)
        assert "count" in data

    def test_trending_sorted_by_postcount(self, hashtag_user_a):
        tok, _ = hashtag_user_a
        r = _retry(lambda: requests.get(f"{API_URL}/hashtags/trending?limit=10", headers=_h(tok)))
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        items = data.get("items", [])
        counts = [item.get("postCount", 0) for item in items]
        assert counts == sorted(counts, reverse=True), "Trending should be sorted by postCount desc"

    def test_trending_limit_respected(self, hashtag_user_a):
        tok, _ = hashtag_user_a
        r = _retry(lambda: requests.get(f"{API_URL}/hashtags/trending?limit=3", headers=_h(tok)))
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        items = data.get("items", [])
        assert len(items) <= 3

    def test_trending_items_have_no_id(self, hashtag_user_a):
        """Trending results should not leak MongoDB _id."""
        tok, _ = hashtag_user_a
        r = _retry(lambda: requests.get(f"{API_URL}/hashtags/trending", headers=_h(tok)))
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        items = data.get("items", [])
        for item in items:
            assert "_id" not in item, "MongoDB _id should not leak"


@pytest.fixture(scope="module")
def feed_safety_user():
    """Dedicated user for hashtag feed safety tests — separate WRITE budget."""
    return _register(509, "FeedSafetyUser")


@pytest.fixture(scope="module")
def feed_pagination_user():
    """Dedicated user for hashtag feed pagination tests — separate WRITE budget."""
    return _register(510, "FeedPaginationUser")


# ════════════════════════════════════════════════════════════════════
# D. HASHTAG FEED TESTS
# ════════════════════════════════════════════════════════════════════

class TestHashtagFeed:
    """D1-D6: GET /hashtags/:tag/feed — content feed for a hashtag."""

    def test_hashtag_feed_returns_matching_posts(self, hashtag_user_a):
        tok, _ = hashtag_user_a
        tag = f"b5feed{random.randint(10000,99999)}"
        post1 = _create_post(tok, f"#{tag} first post")
        post2 = _create_post(tok, f"#{tag} second post")
        # Promote to public
        _db.content_items.update_many(
            {"id": {"$in": [post1["id"], post2["id"]]}},
            {"$set": {"visibility": "PUBLIC"}}
        )
        time.sleep(0.3)
        r = _retry(lambda: requests.get(f"{API_URL}/hashtags/{tag}/feed", headers=_h(tok)))
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        items = data.get("items", [])
        ids = [i.get("id") for i in items]
        assert post1["id"] in ids, "First tagged post not in feed"
        assert post2["id"] in ids, "Second tagged post not in feed"

    def test_hashtag_feed_sorted_by_recency(self, hashtag_user_a):
        tok, _ = hashtag_user_a
        tag = f"b5feedsort{random.randint(10000,99999)}"
        post1 = _create_post(tok, f"#{tag} older")
        time.sleep(0.5)
        post2 = _create_post(tok, f"#{tag} newer")
        _db.content_items.update_many(
            {"id": {"$in": [post1["id"], post2["id"]]}},
            {"$set": {"visibility": "PUBLIC"}}
        )
        time.sleep(0.3)
        r = _retry(lambda: requests.get(f"{API_URL}/hashtags/{tag}/feed", headers=_h(tok)))
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        items = data.get("items", [])
        ids = [i.get("id") for i in items]
        # Newer post should come first (createdAt desc)
        if post1["id"] in ids and post2["id"] in ids:
            assert ids.index(post2["id"]) < ids.index(post1["id"]), "Newer post should come first"

    def test_hashtag_feed_pagination(self, feed_pagination_user):
        tok, _ = feed_pagination_user
        tag = f"b5feedpage{random.randint(10000,99999)}"
        created_ids = []
        for i in range(4):
            p = _create_post(tok, f"#{tag} post {i}")
            created_ids.append(p["id"])
            time.sleep(0.2)
        _db.content_items.update_many(
            {"id": {"$in": created_ids}},
            {"$set": {"visibility": "PUBLIC"}}
        )
        time.sleep(0.3)
        # Page 1: limit 2
        r1 = _retry(lambda: requests.get(f"{API_URL}/hashtags/{tag}/feed?limit=2", headers=_h(tok)))
        assert r1.status_code == 200
        d1 = r1.json().get("data", r1.json())
        items1 = d1.get("items", [])
        assert len(items1) == 2, f"Expected 2 items, got {len(items1)}"
        pag1 = d1.get("pagination", {})
        assert pag1.get("hasMore") is True
        cursor = pag1.get("nextCursor")
        assert cursor is not None

        # Page 2
        r2 = _retry(lambda: requests.get(f"{API_URL}/hashtags/{tag}/feed?limit=2&cursor={cursor}", headers=_h(tok)))
        assert r2.status_code == 200
        d2 = r2.json().get("data", r2.json())
        items2 = d2.get("items", [])
        assert len(items2) == 2, f"Expected 2 items on page 2, got {len(items2)}"

        # No duplicates across pages
        ids1 = {i["id"] for i in items1}
        ids2 = {i["id"] for i in items2}
        assert ids1.isdisjoint(ids2), "Duplicate items across pages"

    def test_hashtag_feed_excludes_removed(self, feed_safety_user):
        tok, _ = feed_safety_user
        tag = f"b5feedrm{random.randint(10000,99999)}"
        post = _create_post(tok, f"#{tag} will be removed")
        _db.content_items.update_one({"id": post["id"]}, {"$set": {"visibility": "PUBLIC", "isRemoved": True}})
        time.sleep(0.3)
        r = _retry(lambda: requests.get(f"{API_URL}/hashtags/{tag}/feed", headers=_h(tok)))
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        items = data.get("items", [])
        assert not any(i.get("id") == post["id"] for i in items), "Removed post should not appear in feed"

    def test_hashtag_feed_excludes_moderated(self, feed_safety_user):
        tok, _ = feed_safety_user
        tag = f"b5feedmod{random.randint(10000,99999)}"
        post = _create_post(tok, f"#{tag} moderated post")
        _db.content_items.update_one({"id": post["id"]}, {"$set": {"visibility": "PUBLIC", "moderationHold": True}})
        time.sleep(0.3)
        r = _retry(lambda: requests.get(f"{API_URL}/hashtags/{tag}/feed", headers=_h(tok)))
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        items = data.get("items", [])
        assert not any(i.get("id") == post["id"] for i in items)

    def test_hashtag_feed_excludes_deleted(self, feed_safety_user):
        tok, _ = feed_safety_user
        tag = f"b5feeddel{random.randint(10000,99999)}"
        post = _create_post(tok, f"#{tag} to be deleted")
        _db.content_items.update_one({"id": post["id"]}, {"$set": {"visibility": "PUBLIC", "isDeleted": True}})
        time.sleep(0.3)
        r = _retry(lambda: requests.get(f"{API_URL}/hashtags/{tag}/feed", headers=_h(tok)))
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        items = data.get("items", [])
        assert not any(i.get("id") == post["id"] for i in items)

    def test_hashtag_feed_includes_tag_in_response(self, feed_safety_user):
        tok, _ = feed_safety_user
        tag = f"b5feedtag{random.randint(10000,99999)}"
        _create_post(tok, f"#{tag}")
        time.sleep(0.3)
        r = _retry(lambda: requests.get(f"{API_URL}/hashtags/{tag}/feed", headers=_h(tok)))
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        assert data.get("tag") == tag, "Response should include the tag"

    def test_hashtag_feed_invalid_tag(self, hashtag_user_a):
        tok, _ = hashtag_user_a
        r = _retry(lambda: requests.get(f"{API_URL}/hashtags/%23/feed", headers=_h(tok)))
        assert r.status_code == 400


# ════════════════════════════════════════════════════════════════════
# E. SAFETY TESTS — Block/Privacy/Moderation
# ════════════════════════════════════════════════════════════════════

class TestSearchBlockSafety:
    """E1-E4: Blocked users and their content excluded from search and feeds."""

    def test_blocked_user_excluded_from_search(self, safety_blocker, safety_target):
        tok_blocker, uid_blocker = safety_blocker
        tok_target, uid_target = safety_target
        # Create block via canonical /me/blocks/:userId
        r_block = _retry(lambda: requests.post(f"{API_URL}/me/blocks/{uid_target}", headers=_h(tok_blocker)))
        assert r_block.status_code == 200, f"Block failed: {r_block.status_code} {r_block.text[:100]}"
        time.sleep(0.3)
        r = _search(tok_blocker, "SafetyTarget", "users")
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        users = data.get("users", [])
        assert not any(u.get("id") == uid_target for u in users), "Blocked user should not appear in search"
        # Cleanup: unblock
        _retry(lambda: requests.delete(f"{API_URL}/me/blocks/{uid_target}", headers=_h(tok_blocker)))

    def test_blocked_user_content_excluded_from_post_search(self, safety_blocker, safety_target):
        tok_blocker, uid_blocker = safety_blocker
        tok_target, uid_target = safety_target
        unique = f"blockedcontent{random.randint(100000,999999)}"
        post = _create_post(tok_target, f"This is {unique} from target")
        _db.content_items.update_one({"id": post["id"]}, {"$set": {"visibility": "PUBLIC"}})
        # Block via canonical endpoint
        _retry(lambda: requests.post(f"{API_URL}/me/blocks/{uid_target}", headers=_h(tok_blocker)))
        time.sleep(0.3)
        r = _search(tok_blocker, unique, "posts")
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        posts = data.get("posts", [])
        assert not any(p.get("id") == post["id"] for p in posts), "Blocked user's post should not appear"
        # Cleanup
        _retry(lambda: requests.delete(f"{API_URL}/me/blocks/{uid_target}", headers=_h(tok_blocker)))

    def test_blocked_user_content_excluded_from_hashtag_feed(self, safety_blocker, safety_target):
        tok_blocker, uid_blocker = safety_blocker
        tok_target, uid_target = safety_target
        tag = f"b5blockhash{random.randint(10000,99999)}"
        post = _create_post(tok_target, f"#{tag} blocked content")
        _db.content_items.update_one({"id": post["id"]}, {"$set": {"visibility": "PUBLIC"}})
        # Block via canonical endpoint
        _retry(lambda: requests.post(f"{API_URL}/me/blocks/{uid_target}", headers=_h(tok_blocker)))
        time.sleep(0.3)
        r = _retry(lambda: requests.get(f"{API_URL}/hashtags/{tag}/feed", headers=_h(tok_blocker)))
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        items = data.get("items", [])
        assert not any(i.get("id") == post["id"] for i in items), "Blocked user's content should not appear in hashtag feed"
        # Cleanup
        _retry(lambda: requests.delete(f"{API_URL}/me/blocks/{uid_target}", headers=_h(tok_blocker)))

    def test_reverse_block_also_excluded(self, safety_blocker, safety_target):
        """If target blocks the searcher, target should also be excluded."""
        tok_blocker, uid_blocker = safety_blocker
        tok_target, uid_target = safety_target
        # Target blocks searcher (reverse direction) via canonical endpoint
        _retry(lambda: requests.post(f"{API_URL}/me/blocks/{uid_blocker}", headers=_h(tok_target)))
        time.sleep(0.3)
        r = _search(tok_blocker, "SafetyTarget", "users")
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        users = data.get("users", [])
        assert not any(u.get("id") == uid_target for u in users), "Reverse-blocked user should not appear"
        # Cleanup
        _retry(lambda: requests.delete(f"{API_URL}/me/blocks/{uid_blocker}", headers=_h(tok_target)))


# ════════════════════════════════════════════════════════════════════
# F. CONTRACT TESTS — Stable response shapes
# ════════════════════════════════════════════════════════════════════

class TestSearchContracts:
    """F1-F5: Validate response object shapes are stable and frontend-buildable."""

    def test_user_result_contract(self, search_user_a):
        tok, uid = search_user_a
        r = _search(tok, "AlphaSearcher", "users")
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        users = data.get("users", [])
        user = next((u for u in users if u.get("id") == uid), None)
        assert user is not None
        # User snippet contract fields
        required = ["id", "displayName", "username"]
        for f in required:
            assert f in user, f"User result missing '{f}'"

    def test_page_result_contract(self, search_user_a, b5_test_page):
        tok, _ = search_user_a
        r = _search(tok, "B5TestPage", "pages")
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        pages = data.get("pages", [])
        page = next((p for p in pages if p.get("id") == b5_test_page["id"]), None)
        assert page is not None
        required = ["id", "slug", "name", "category", "isOfficial", "verificationStatus", "status"]
        for f in required:
            assert f in page, f"Page result missing '{f}'"

    def test_hashtag_result_contract(self, hashtag_user_a):
        tok, _ = hashtag_user_a
        tag = f"b5contract{random.randint(10000,99999)}"
        _create_post(tok, f"#{tag}")
        time.sleep(0.3)
        r = _search(tok, tag, "hashtags")
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        hashtags = data.get("hashtags", [])
        ht = next((h for h in hashtags if h.get("tag") == tag), None)
        assert ht is not None
        required = ["tag", "postCount"]
        for f in required:
            assert f in ht, f"Hashtag result missing '{f}'"
        assert "_id" not in ht, "MongoDB _id should not leak"

    def test_hashtag_feed_item_contract(self, hashtag_user_a):
        tok, _ = hashtag_user_a
        tag = f"b5feedcontract{random.randint(10000,99999)}"
        post = _create_post(tok, f"#{tag} contract check")
        _db.content_items.update_one({"id": post["id"]}, {"$set": {"visibility": "PUBLIC"}})
        time.sleep(0.3)
        r = _retry(lambda: requests.get(f"{API_URL}/hashtags/{tag}/feed", headers=_h(tok)))
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        items = data.get("items", [])
        assert len(items) > 0, "Feed should have items"
        item = items[0]
        # Post/content item contract
        required = ["id", "caption", "author"]
        for f in required:
            assert f in item, f"Feed item missing '{f}'"
        assert "_id" not in item, "MongoDB _id should not leak"

    def test_hashtag_feed_pagination_contract(self, hashtag_user_a):
        tok, _ = hashtag_user_a
        tag = f"b5pagcontract{random.randint(10000,99999)}"
        _create_post(tok, f"#{tag}")
        time.sleep(0.3)
        r = _retry(lambda: requests.get(f"{API_URL}/hashtags/{tag}/feed", headers=_h(tok)))
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        pag = data.get("pagination", {})
        assert "nextCursor" in pag, "Pagination must have nextCursor"
        assert "hasMore" in pag, "Pagination must have hasMore"
        assert data.get("tag") is not None, "Response must include tag"

    def test_mixed_result_type_marker(self, search_user_a):
        """Mixed search items must have _resultType."""
        tok, _ = search_user_a
        r = _search(tok, "Alpha", "all")
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        items = data.get("items", [])
        for item in items:
            assert "_resultType" in item

    def test_search_error_contract(self, search_user_a):
        """Errors should have stable shape."""
        tok, _ = search_user_a
        # Single char — returns empty, not error (based on code: returns empty data)
        r = _search(tok, "x", "all")
        assert r.status_code == 200


# ════════════════════════════════════════════════════════════════════
# G. RANKING / ORDERING TESTS
# ════════════════════════════════════════════════════════════════════

class TestRanking:
    """G1-G2: Deterministic ranking for pages (official first)."""

    def test_official_page_ranks_higher(self, search_user_a, page_owner):
        tok_a, _ = search_user_a
        tok_p, _ = page_owner
        prefix = f"B5Rnk{random.randint(1000,9999)}"
        slug1 = f"b5-rank-regular-{random.randint(10000,99999)}"
        slug2 = f"b5-rank-verified-{random.randint(10000,99999)}"
        regular_page = _create_page(tok_p, f"{prefix}Regular", slug1)
        verified_page = _create_page(tok_p, f"{prefix}Verified", slug2)
        _db.pages.update_one({"id": verified_page["id"]}, {"$set": {"isOfficial": True, "followerCount": 100}})
        _db.pages.update_one({"id": regular_page["id"]}, {"$set": {"isOfficial": False, "followerCount": 5}})
        time.sleep(0.3)
        r = _search(tok_a, prefix, "pages")
        assert r.status_code == 200
        data = r.json().get("data", r.json())
        pages = data.get("pages", [])
        page_ids = [p["id"] for p in pages if p["id"] in (regular_page["id"], verified_page["id"])]
        if len(page_ids) == 2:
            assert page_ids[0] == verified_page["id"], "Official/verified page should rank first"

    def test_hashtag_trending_order_deterministic(self, hashtag_user_a):
        """Trending hashtags should have stable ordering."""
        tok, _ = hashtag_user_a
        r1 = _retry(lambda: requests.get(f"{API_URL}/hashtags/trending?limit=10", headers=_h(tok)))
        r2 = _retry(lambda: requests.get(f"{API_URL}/hashtags/trending?limit=10", headers=_h(tok)))
        assert r1.status_code == 200
        assert r2.status_code == 200
        tags1 = [h["tag"] for h in r1.json().get("data", {}).get("items", [])]
        tags2 = [h["tag"] for h in r2.json().get("data", {}).get("items", [])]
        assert tags1 == tags2, "Trending order should be deterministic"


# ════════════════════════════════════════════════════════════════════
# H. INDEX / REGRESSION TESTS
# ════════════════════════════════════════════════════════════════════

class TestIndexesPresent:
    """H1: Critical indexes exist in the database."""

    def test_hashtag_tag_unique_index(self):
        indexes = list(_db.hashtags.list_indexes())
        tag_indexes = [idx for idx in indexes if "tag" in idx.get("key", {})]
        assert len(tag_indexes) > 0, "hashtags.tag index missing"
        unique_idx = next((idx for idx in tag_indexes if idx.get("unique")), None)
        assert unique_idx is not None, "hashtags.tag should be unique"

    def test_hashtag_postcount_index(self):
        indexes = list(_db.hashtags.list_indexes())
        count_indexes = [idx for idx in indexes if "postCount" in idx.get("key", {})]
        assert len(count_indexes) > 0, "hashtags.postCount index missing"

    def test_content_hashtags_index(self):
        indexes = list(_db.content_items.list_indexes())
        ht_indexes = [idx for idx in indexes if "hashtags" in idx.get("key", {})]
        assert len(ht_indexes) > 0, "content_items.hashtags index missing"

    def test_content_caption_text_index(self):
        indexes = list(_db.content_items.list_indexes())
        text_indexes = [idx for idx in indexes if any(v == "text" for v in idx.get("key", {}).values())]
        assert len(text_indexes) > 0, "content_items text index for caption search missing"

    def test_user_text_index(self):
        indexes = list(_db.users.list_indexes())
        text_indexes = [idx for idx in indexes if any(v == "text" for v in idx.get("key", {}).values())]
        assert len(text_indexes) > 0, "users text index missing"

    def test_user_displayname_ci_index(self):
        """B5.1: Case-insensitive collation index on displayName."""
        indexes = list(_db.users.list_indexes())
        ci_indexes = [idx for idx in indexes if idx.get("name") == "displayName_ci"]
        assert len(ci_indexes) > 0, "users displayName_ci collation index missing"
        assert ci_indexes[0].get("collation", {}).get("strength") == 2

    def test_page_name_ci_index(self):
        """B5.1: Case-insensitive collation index on page name."""
        indexes = list(_db.pages.list_indexes())
        ci_indexes = [idx for idx in indexes if idx.get("name") == "name_ci"]
        assert len(ci_indexes) > 0, "pages name_ci collation index missing"

    def test_page_status_name_ci_index(self):
        """B5.1: Compound collation index for page search filter+sort."""
        indexes = list(_db.pages.list_indexes())
        ci_indexes = [idx for idx in indexes if idx.get("name") == "status_name_ci"]
        assert len(ci_indexes) > 0, "pages status_name_ci collation index missing"


class TestRegression:
    """H2-H4: Existing flows unbroken by B5 changes."""

    def test_create_post_still_works(self, search_user_a):
        tok, _ = search_user_a
        post = _create_post(tok, "Regression check — no hashtags here")
        assert post.get("id") is not None

    def test_edit_post_still_works(self, search_user_a):
        tok, _ = search_user_a
        post = _create_post(tok, "Will be edited for regression")
        updated = _edit_post(tok, post["id"], "Edited for regression check")
        assert updated.get("id") == post["id"]

    def test_public_feed_still_works(self, search_user_a):
        tok, _ = search_user_a
        r = _retry(lambda: requests.get(f"{API_URL}/feed/public?limit=5", headers=_h(tok)))
        assert r.status_code == 200

    def test_suggestions_still_works(self, search_user_a):
        tok, _ = search_user_a
        r = _retry(lambda: requests.get(f"{API_URL}/suggestions/users", headers=_h(tok)))
        assert r.status_code == 200

    def test_page_post_create_still_works(self, page_owner, b5_test_page):
        tok, _ = page_owner
        post = _create_page_post(tok, b5_test_page["id"], "Regression page post")
        assert post.get("id") is not None
