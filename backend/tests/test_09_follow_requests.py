"""Category 9: FOLLOW REQUESTS — Regression Tests"""
import pytest


class TestFollowRequests:
    def test_pending_requests(self, api):
        r = api.get("/me/follow-requests")
        assert r.status_code == 200

    def test_sent_requests(self, api):
        r = api.get("/me/follow-requests/sent")
        assert r.status_code == 200

    def test_pending_count(self, api):
        r = api.get("/me/follow-requests/count")
        assert r.status_code == 200
        d = r.json()
        data = d.get("data") or d
        assert "count" in data

    def test_follow_requests_unauthenticated(self, anon):
        r = anon.get("/me/follow-requests")
        assert r.status_code in (401, 403)
