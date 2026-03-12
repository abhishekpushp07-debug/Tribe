"""Category 8: TRANSCODE (Video) — Regression Tests"""
import pytest


class TestTranscode:
    def test_queue(self, api):
        """Transcode queue returns jobs and total."""
        r = api.get("/transcode/queue")
        assert r.status_code == 200
        d = r.json()
        data = d.get("data") or d
        assert "jobs" in data
        assert "total" in data or "stats" in data

    def test_queue_filter_completed(self, api):
        r = api.get("/transcode/queue?status=COMPLETED")
        assert r.status_code == 200

    def test_queue_filter_invalid(self, api):
        """Invalid status filter still returns (ignores bad filter)."""
        r = api.get("/transcode/queue?status=INVALID")
        assert r.status_code == 200

    def test_cancel_nonexistent(self, api):
        r = api.post("/transcode/nonexistent-job/cancel")
        assert r.status_code == 404

    def test_retry_nonexistent(self, api):
        r = api.post("/transcode/nonexistent-job/retry")
        assert r.status_code == 404

    def test_queue_unauthenticated(self, anon):
        r = anon.get("/transcode/queue")
        assert r.status_code in (401, 403)
