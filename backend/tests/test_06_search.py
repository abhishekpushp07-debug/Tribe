"""Category 6: SEARCH — Regression Tests"""
import pytest


class TestSearch:
    def test_unified_search(self, api):
        """Unified search returns totalResults."""
        r = api.get("/search?q=test")
        assert r.status_code == 200
        d = r.json()
        data = d.get("data") or d
        assert "totalResults" in data
        assert "results" in data

    def test_search_type_filter_users(self, api):
        r = api.get("/search?q=test&type=users")
        assert r.status_code == 200
        d = r.json()
        data = d.get("data") or d
        assert data.get("type") == "users"

    def test_search_invalid_type(self, api):
        """Invalid type returns 400."""
        r = api.get("/search?q=test&type=invalid_type")
        assert r.status_code == 400

    def test_search_empty_query(self, api):
        r = api.get("/search?q=")
        assert r.status_code == 400

    def test_autocomplete(self, api):
        r = api.get("/search/autocomplete?q=te")
        assert r.status_code == 200
        d = r.json()
        data = d.get("data") or d
        assert "suggestions" in data

    def test_autocomplete_cached(self, api):
        """Autocomplete should be cached."""
        r1 = api.get("/search/autocomplete?q=te")
        r2 = api.get("/search/autocomplete?q=te")
        assert r1.status_code == 200
        assert r2.status_code == 200
        # Both should return same data
        assert r1.json() == r2.json()

    def test_user_search(self, api):
        r = api.get("/search/users?q=test")
        assert r.status_code == 200

    def test_hashtag_search(self, api):
        """Hashtag search includes reelCount and totalCount."""
        r = api.get("/search/hashtags?q=test")
        assert r.status_code == 200
        d = r.json()
        data = d.get("data") or d
        items = data.get("items") or data.get("hashtags", [])
        if items:
            h = items[0]
            assert "postCount" in h
            assert "reelCount" in h
            assert "totalCount" in h

    def test_content_search(self, api):
        r = api.get("/search/content?q=test")
        assert r.status_code == 200

    def test_recent_searches(self, api):
        r = api.get("/search/recent")
        assert r.status_code == 200

    def test_clear_recent_searches(self, api):
        r = api.delete("/search/recent")
        assert r.status_code == 200
