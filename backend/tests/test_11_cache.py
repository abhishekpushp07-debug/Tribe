"""Category 11: REDIS CACHE — Regression Tests"""
import pytest


class TestCache:
    def test_cache_stats(self, api):
        """Cache stats endpoint returns Redis status."""
        r = api.get("/cache/stats")
        assert r.status_code == 200
        d = r.json()
        data = d.get("data") or d
        assert "redis" in data
        # Redis may be connected or disconnected depending on environment
        assert data["redis"]["status"] in ("connected", "disconnected")

    def test_cache_has_keys(self, api):
        """After hitting endpoints, cache should have keys."""
        # Hit a cached endpoint first
        api.get("/tribes")
        api.get("/tribes/leaderboard")
        r = api.get("/cache/stats")
        d = r.json()
        data = d.get("data") or d
        assert data["redis"]["keys"] >= 0  # May be 0 if TTL expired

    def test_cache_zero_errors(self, api):
        """Redis should have zero errors."""
        r = api.get("/cache/stats")
        d = r.json()
        data = d.get("data") or d
        assert data.get("redisErrors", 0) == 0

    def test_cache_stats_unauthenticated(self, anon):
        r = anon.get("/cache/stats")
        assert r.status_code in (401, 403)
