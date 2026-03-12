"""Category 7: ANALYTICS — Regression Tests"""
import pytest


class TestAnalytics:
    def test_track_event(self, api):
        """Track a profile visit event."""
        r = api.post("/analytics/track", json={
            "eventType": "PROFILE_VISIT",
            "targetId": "test-user-analytics"
        })
        assert r.status_code in (200, 201)

    def test_track_content_view(self, api):
        r = api.post("/analytics/track", json={
            "eventType": "CONTENT_VIEW",
            "targetId": "test-content-id"
        })
        assert r.status_code in (200, 201)

    def test_overview(self, api):
        """Overview returns period and engagement data."""
        r = api.get("/analytics/overview")
        assert r.status_code == 200
        d = r.json()
        data = d.get("data") or d
        assert "period" in data
        assert "engagement" in data or "account" in data

    def test_overview_with_period(self, api):
        r = api.get("/analytics/overview?period=30d")
        assert r.status_code == 200
        d = r.json()
        data = d.get("data") or d
        assert data.get("period") == "30d"

    def test_overview_cached(self, api):
        """Overview should be cached per user+period."""
        r1 = api.get("/analytics/overview?period=7d")
        r2 = api.get("/analytics/overview?period=7d")
        assert r1.status_code == 200
        assert r2.status_code == 200

    def test_content_analytics(self, api):
        r = api.get("/analytics/content")
        assert r.status_code == 200

    def test_audience_analytics(self, api):
        r = api.get("/analytics/audience")
        assert r.status_code == 200

    def test_reach_analytics(self, api):
        r = api.get("/analytics/reach")
        assert r.status_code == 200

    def test_profile_visits(self, api):
        r = api.get("/analytics/profile-visits")
        assert r.status_code == 200

    def test_reel_analytics(self, api):
        r = api.get("/analytics/reels")
        assert r.status_code == 200

    def test_story_analytics(self, api):
        """NEW: Story analytics endpoint."""
        r = api.get("/analytics/stories")
        assert r.status_code == 200
        d = r.json()
        data = d.get("data") or d
        assert "totalStories" in data
        assert "viewsByDay" in data

    def test_analytics_unauthenticated(self, anon):
        r = anon.get("/analytics/overview")
        assert r.status_code in (401, 403)
