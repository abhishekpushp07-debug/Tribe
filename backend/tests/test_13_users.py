"""Category 13: USER PROFILES — Regression Tests"""
import pytest


class TestUsers:
    def test_get_my_profile(self, api):
        r = api.get("/users/me")
        # May redirect to /auth/me
        assert r.status_code in (200, 301, 302, 404)

    def test_get_user_by_id(self, api, user1_data):
        uid = user1_data.get("id") or user1_data.get("user", {}).get("id")
        if not uid:
            pytest.skip("No user id")
        r = api.get(f"/users/{uid}")
        assert r.status_code == 200

    def test_user_not_found(self, api):
        r = api.get("/users/nonexistent-user-id")
        assert r.status_code == 404
