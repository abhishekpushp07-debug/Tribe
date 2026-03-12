"""Category 2: FEED (Posts) — Regression Tests"""
import pytest


class TestFeed:
    def test_home_feed(self, api):
        """Home feed returns posts."""
        r = api.get("/feed")
        assert r.status_code == 200
        d = r.json()
        items = d.get("items") or d.get("data", {}).get("items", [])
        assert isinstance(items, list)
        assert len(items) > 0, "Feed should have posts"

    def test_home_feed_pagination(self, api):
        """Feed supports limit and cursor."""
        r = api.get("/feed?limit=5")
        assert r.status_code == 200
        d = r.json()
        items = d.get("items") or d.get("data", {}).get("items", [])
        assert len(items) <= 5

    def test_public_feed(self, api):
        r = api.get("/feed/public")
        assert r.status_code == 200
        d = r.json()
        items = d.get("items") or d.get("data", {}).get("items", [])
        assert isinstance(items, list)

    def test_following_feed(self, api):
        r = api.get("/feed/following")
        assert r.status_code == 200

    def test_explore_page(self, api):
        r = api.get("/explore")
        assert r.status_code == 200
        d = r.json()
        data = d.get("data") or d
        # explore returns posts, reels, hashtags
        assert "trendingHashtags" in data or "posts" in data or "trendingPosts" in data

    def test_explore_unauthenticated(self, anon):
        r = anon.get("/explore")
        assert r.status_code == 200

    def test_feed_unauthenticated(self, anon):
        """Home feed is accessible without auth (open feed)."""
        r = anon.get("/feed")
        assert r.status_code == 200

    def test_feed_post_structure(self, api):
        """Posts have required fields."""
        r = api.get("/feed")
        d = r.json()
        items = d.get("items") or d.get("data", {}).get("items", [])
        if items:
            post = items[0]
            assert "id" in post
            assert "authorId" in post or "author" in post
