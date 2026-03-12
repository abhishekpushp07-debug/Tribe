"""Category 10: SOCIAL INTERACTIONS — Regression Tests"""
import pytest


class TestSocial:
    def test_like_post(self, api, sample_post_id):
        """Like a post."""
        if not sample_post_id:
            pytest.skip("No posts available")
        r = api.post(f"/content/{sample_post_id}/like")
        assert r.status_code in (200, 201, 409)  # 409 if already liked

    def test_unlike_post(self, api, sample_post_id):
        """Unlike a post."""
        if not sample_post_id:
            pytest.skip("No posts available")
        r = api.delete(f"/content/{sample_post_id}/like")
        assert r.status_code in (200, 404)  # 404 if not liked

    def test_comment_on_post(self, api, sample_post_id):
        if not sample_post_id:
            pytest.skip("No posts available")
        r = api.post(f"/content/{sample_post_id}/comments", json={"text": "pytest regression test comment"})
        assert r.status_code in (200, 201)

    def test_save_post(self, api, sample_post_id):
        if not sample_post_id:
            pytest.skip("No posts available")
        r = api.post(f"/content/{sample_post_id}/save")
        assert r.status_code in (200, 201, 409)

    def test_unsave_post(self, api, sample_post_id):
        if not sample_post_id:
            pytest.skip("No posts available")
        r = api.delete(f"/content/{sample_post_id}/save")
        assert r.status_code in (200, 404)

    def test_like_nonexistent(self, api):
        r = api.post("/content/nonexistent-post/like")
        assert r.status_code in (404, 400)
