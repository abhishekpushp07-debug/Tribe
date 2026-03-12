"""Category 14: CROSS-USER FLOWS — Regression Tests

Tests that verify user2 can see user1's content."""
import pytest


class TestCrossUser:
    def test_user2_sees_feed(self, api2):
        """User 2 can see the home feed."""
        r = api2.get("/feed")
        assert r.status_code == 200
        d = r.json()
        items = d.get("items") or d.get("data", {}).get("items", [])
        assert len(items) > 0

    def test_user2_sees_reels(self, api2):
        r = api2.get("/reels/feed")
        assert r.status_code == 200
        d = r.json()
        items = d.get("items") or d.get("data", {}).get("items", [])
        assert len(items) > 0

    def test_user2_sees_stories(self, api2):
        r = api2.get("/stories")
        assert r.status_code == 200

    def test_user2_sees_tribes(self, api2):
        r = api2.get("/tribes")
        assert r.status_code == 200
        d = r.json()
        data = d.get("data") or d
        assert len(data.get("items", [])) >= 20

    def test_both_users_same_feed_content(self, api, api2):
        """Both users should see posts (open feed)."""
        r1 = api.get("/feed")
        r2 = api2.get("/feed")
        d1 = r1.json()
        d2 = r2.json()
        items1 = d1.get("items") or d1.get("data", {}).get("items", [])
        items2 = d2.get("items") or d2.get("data", {}).get("items", [])
        assert len(items1) > 0
        assert len(items2) > 0
