"""Integration Tests — Session Management

Tests: list sessions, revoke one, revoke all
"""
import pytest
import requests

pytestmark = pytest.mark.integration


def _h(ip=None):
    from tests.conftest import _next_test_ip, _make_headers
    return _make_headers(ip=ip or _next_test_ip())


def _auth(token, ip=None):
    from tests.conftest import auth_header
    return auth_header(token, ip=ip)


def _login(api_url, phone, pin='1234', name='Session Test'):
    from tests.conftest import _next_test_ip
    ip = _next_test_ip()
    requests.post(f'{api_url}/auth/register', json={'phone': phone, 'pin': pin, 'displayName': name}, headers=_h(ip))
    resp = requests.post(f'{api_url}/auth/login', json={'phone': phone, 'pin': pin}, headers=_h(ip))
    data = resp.json()
    return data.get('accessToken') or data.get('token'), ip


class TestSessionList:
    def test_list_sessions(self, api_url):
        phone = '9999960001'
        token, ip = _login(api_url, phone)
        resp = requests.get(f'{api_url}/auth/sessions', headers=_auth(token, ip))
        assert resp.status_code == 200
        data = resp.json()
        assert 'sessions' in data
        assert isinstance(data['sessions'], list)
        assert len(data['sessions']) >= 1
        current = [s for s in data['sessions'] if s.get('isCurrent')]
        assert len(current) == 1

    def test_sessions_dont_expose_tokens(self, api_url):
        phone = '9999960002'
        token, ip = _login(api_url, phone)
        resp = requests.get(f'{api_url}/auth/sessions', headers=_auth(token, ip))
        data = resp.json()
        for s in data['sessions']:
            assert 'token' not in s
            assert 'refreshToken' not in s
            assert 'accessToken' not in s


class TestRevokeSession:
    def test_revoke_other_session(self, api_url):
        phone = '9999960003'
        token1, ip = _login(api_url, phone)
        # Login again from same IP to create 2nd session
        resp2 = requests.post(f'{api_url}/auth/login', json={'phone': phone, 'pin': '1234'}, headers=_h(ip))
        token2 = resp2.json().get('accessToken') or resp2.json().get('token')
        # List sessions from token2
        sessions = requests.get(f'{api_url}/auth/sessions', headers=_auth(token2, ip)).json()['sessions']
        other = [s for s in sessions if not s.get('isCurrent')]
        if not other:
            pytest.skip('Only one session visible')
        resp = requests.delete(f'{api_url}/auth/sessions/{other[0]["id"]}', headers=_auth(token2, ip))
        assert resp.status_code == 200

    def test_revoke_all_sessions(self, api_url):
        phone = '9999960004'
        token, ip = _login(api_url, phone)
        _login(api_url, phone)  # 2nd session
        resp = requests.delete(f'{api_url}/auth/sessions', headers=_auth(token, ip))
        assert resp.status_code == 200
        data = resp.json()
        assert 'revokedCount' in data
        resp2 = requests.get(f'{api_url}/auth/me', headers=_auth(token, ip))
        assert resp2.status_code == 401
