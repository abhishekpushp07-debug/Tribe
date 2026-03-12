"""Category 3: REELS — Regression Tests"""
import pytest


class TestReels:
    def test_reels_feed(self, api):
        """Main reel discovery feed."""
        r = api.get("/reels/feed")
        assert r.status_code == 200
        d = r.json()
        items = d.get("items") or d.get("data", {}).get("items", [])
        assert isinstance(items, list)
        assert len(items) > 0, "Reels feed should have reels"

    def test_reels_feed_pagination(self, api):
        r = api.get("/reels/feed?limit=5")
        assert r.status_code == 200
        d = r.json()
        items = d.get("items") or d.get("data", {}).get("items", [])
        assert len(items) <= 5

    def test_reels_following(self, api):
        r = api.get("/reels/following")
        assert r.status_code == 200

    def test_reels_trending(self, api):
        r = api.get("/reels/trending")
        assert r.status_code == 200

    def test_reels_personalized(self, api):
        r = api.get("/reels/personalized")
        assert r.status_code == 200

    def test_reel_detail(self, api, sample_reel_id):
        """Single reel detail."""
        if not sample_reel_id:
            pytest.skip("No reels available")
        r = api.get(f"/reels/{sample_reel_id}")
        assert r.status_code == 200
        d = r.json()
        reel = d.get("data") or d
        assert "id" in reel or "reel" in reel

    def test_reel_not_found(self, api):
        r = api.get("/reels/nonexistent-id")
        assert r.status_code == 404

    def test_reels_feed_unauthenticated(self, anon):
        r = anon.get("/reels/feed")
        assert r.status_code in (401, 403)

    def test_reel_structure(self, api):
        """Reels have required fields."""
        r = api.get("/reels/feed")
        d = r.json()
        items = d.get("items") or d.get("data", {}).get("items", [])
        if items:
            reel = items[0]
            assert "id" in reel
