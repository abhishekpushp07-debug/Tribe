"""Category 1: AUTH & ONBOARDING — Regression Tests"""
import pytest


class TestAuth:
    def test_login_success(self, api):
        """Login with valid credentials returns token."""
        assert api.token is not None
        assert len(api.token) > 10

    def test_login_wrong_pin(self, anon):
        r = anon.post("/auth/login", json={"phone": "7777099001", "pin": "9999"})
        assert r.status_code in (401, 403)

    def test_login_missing_fields(self, anon):
        r = anon.post("/auth/login", json={})
        assert r.status_code in (400, 401, 422)

    def test_auth_me(self, api):
        r = api.get("/auth/me")
        assert r.status_code == 200
        d = r.json()
        profile = d.get("data") or d
        assert "id" in profile or "user" in profile

    def test_auth_me_unauthenticated(self, anon):
        r = anon.get("/auth/me")
        assert r.status_code in (401, 403)

    def test_healthz(self, anon):
        r = anon.get("/healthz")
        assert r.status_code == 200
        d = r.json()
        assert d["status"] == "ok"
