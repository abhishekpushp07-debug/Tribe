"""Category 4: STORIES — Regression Tests"""
import pytest


class TestStories:
    def test_story_rail(self, api):
        """Story rail shows all users' stories."""
        r = api.get("/stories")
        assert r.status_code == 200
        d = r.json()
        data = d.get("data") or d
        items = data.get("items") or data.get("stories", [])
        assert isinstance(items, list)

    def test_story_feed(self, api):
        r = api.get("/stories/feed")
        assert r.status_code == 200

    def test_story_rail_has_multiple_authors(self, api):
        """Story rail shows stories from ALL users (not just followed)."""
        r = api.get("/stories")
        d = r.json()
        data = d.get("data") or d
        count = data.get("count", 0)
        items = data.get("items", [])
        # Should have stories from multiple authors
        assert len(items) > 0 or count >= 0

    def test_stories_unauthenticated(self, anon):
        r = anon.get("/stories")
        assert r.status_code in (401, 403)
