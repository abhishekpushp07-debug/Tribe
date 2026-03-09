"""Smoke Tests — Auth + Ops Full Flow

Tests: register → login → authenticated endpoint, admin → ops endpoints
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


class TestAuthSmoke:
    def test_register_login_me_flow(self, api_url):
        from tests.conftest import _next_test_ip
        phone = '9999990001'
        ip = _next_test_ip()
        requests.post(f'{api_url}/auth/register', json={
            'phone': phone, 'pin': '1234', 'displayName': 'Smoke Auth'
        }, headers=_h(ip))
        login = requests.post(f'{api_url}/auth/login', json={
            'phone': phone, 'pin': '1234'
        }, headers=_h(ip))
        assert login.status_code == 200
        token = login.json().get('accessToken') or login.json().get('token')
        assert token is not None
        me = requests.get(f'{api_url}/auth/me', headers=_auth(token, ip))
        assert me.status_code == 200


class TestOpsSmoke:
    def test_admin_ops_full_flow(self, api_url, admin_user):
        headers = _auth(admin_user['token'])
        health = requests.get(f'{api_url}/ops/health', headers=headers)
        assert health.status_code == 200
        assert 'checks' in health.json()
        metrics = requests.get(f'{api_url}/ops/metrics', headers=headers)
        assert metrics.status_code == 200
        assert 'http' in metrics.json()
        slis = requests.get(f'{api_url}/ops/slis', headers=headers)
        assert slis.status_code == 200
        assert 'errorRate' in slis.json()
