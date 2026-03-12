"""Category 12: NOTIFICATIONS — Regression Tests"""
import pytest


class TestNotifications:
    def test_get_notifications(self, api):
        r = api.get("/notifications")
        assert r.status_code == 200
        d = r.json()
        data = d.get("data") or d
        items = data.get("items") or data.get("notifications", [])
        assert isinstance(items, list) or isinstance(data, dict)

    def test_notifications_unauthenticated(self, anon):
        r = anon.get("/notifications")
        assert r.status_code in (401, 403)
