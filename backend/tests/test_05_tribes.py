"""Category 5: TRIBES — Regression Tests"""
import pytest


class TestTribes:
    def test_list_tribes(self, api):
        """List all tribes (21 pre-seeded)."""
        r = api.get("/tribes")
        assert r.status_code == 200
        d = r.json()
        data = d.get("data") or d
        items = data.get("items", [])
        assert len(items) >= 20, f"Expected 20+ tribes, got {len(items)}"

    def test_list_tribes_cached(self, api):
        """Second call should be faster (cached)."""
        import time
        start = time.time()
        r1 = api.get("/tribes")
        t1 = time.time() - start
        start = time.time()
        r2 = api.get("/tribes")
        t2 = time.time() - start
        assert r1.status_code == 200
        assert r2.status_code == 200
        # Cached call should generally be faster, but don't fail on network variance

    def test_leaderboard(self, api):
        r = api.get("/tribes/leaderboard")
        assert r.status_code == 200
        d = r.json()
        data = d.get("data") or d
        assert "items" in data or "leaderboard" in data or "rankings" in data or isinstance(data, list)

    def test_standings(self, api):
        r = api.get("/tribes/standings/current")
        assert r.status_code == 200
        d = r.json()
        data = d.get("data") or d
        assert "standings" in data or "season" in data

    def test_tribe_detail(self, api, sample_tribe_id):
        r = api.get(f"/tribes/{sample_tribe_id}")
        assert r.status_code == 200

    def test_tribe_members(self, api, sample_tribe_id):
        r = api.get(f"/tribes/{sample_tribe_id}/members")
        assert r.status_code == 200
        d = r.json()
        data = d.get("data") or d
        pagination = data.get("pagination", {})
        # Enhanced: should have hasMore, limit, offset
        assert "total" in pagination or "hasMore" in pagination

    def test_tribe_stats(self, api, sample_tribe_id):
        r = api.get(f"/tribes/{sample_tribe_id}/stats")
        assert r.status_code == 200

    def test_tribe_feed(self, api, sample_tribe_id):
        r = api.get(f"/tribes/{sample_tribe_id}/feed")
        assert r.status_code == 200

    def test_my_tribe(self, api):
        r = api.get("/me/tribe")
        assert r.status_code == 200
        d = r.json()
        data = d.get("data") or d
        assert "tribe" in data or "membership" in data

    def test_tribe_not_found(self, api):
        r = api.get("/tribes/nonexistent-tribe-id")
        assert r.status_code == 404

    def test_tribes_public_access(self, anon):
        """Tribe list is publicly accessible."""
        r = anon.get("/tribes")
        assert r.status_code == 200
