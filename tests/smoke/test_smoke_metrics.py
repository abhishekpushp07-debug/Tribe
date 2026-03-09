"""Smoke Tests — Metrics Verification

Tests: 404 → error code increment, rate limit status
"""
import pytest
import requests

pytestmark = pytest.mark.smoke


def _h(ip=None):
    from tests.conftest import _next_test_ip, _make_headers
    return _make_headers(ip=ip or _next_test_ip())


def _auth(token, ip=None):
    from tests.conftest import auth_header
    return auth_header(token, ip=ip)


class TestMetricsSmoke:
    def test_404_reflected_in_metrics(self, api_url, admin_user):
        headers = _auth(admin_user['token'])
        m1 = requests.get(f'{api_url}/ops/metrics', headers=headers).json()
        baseline = m1.get('errorCodes', {}).get('NOT_FOUND', 0)
        requests.get(f'{api_url}/smoke-test-404', headers=_h())
        m2 = requests.get(f'{api_url}/ops/metrics', headers=headers).json()
        after = m2.get('errorCodes', {}).get('NOT_FOUND', 0)
        assert after > baseline

    def test_rate_limit_status_visible(self, api_url, admin_user):
        headers = _auth(admin_user['token'])
        metrics = requests.get(f'{api_url}/ops/metrics', headers=headers).json()
        assert 'rateLimiting' in metrics
        assert 'totalHits' in metrics['rateLimiting']
