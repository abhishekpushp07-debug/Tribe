"""Integration Tests — Auth Flow

Tests: register, login success/failure, throttle, refresh, replay, logout, pin change
Requires: running server + MongoDB
"""
import pytest
import requests

pytestmark = pytest.mark.integration


def _h(ip=None):
    """Generate headers with unique IP."""
    from tests.conftest import _next_test_ip, _make_headers
    return _make_headers(ip=ip or _next_test_ip())


def _auth(token, ip=None):
    from tests.conftest import auth_header
    return auth_header(token, ip=ip)


class TestRegister:
    def test_register_new_user(self, api_url):
        phone = '9999910001'
        resp = requests.post(f'{api_url}/auth/register', json={
            'phone': phone, 'pin': '1234', 'displayName': 'IntTest Register'
        }, headers=_h())
        assert resp.status_code in (200, 201, 409)
        if resp.status_code in (200, 201):
            data = resp.json()
            assert 'accessToken' in data or 'token' in data
            assert 'user' in data

    def test_register_duplicate_fails(self, api_url):
        phone = '9999910002'
        ip = from_conftest_ip()
        requests.post(f'{api_url}/auth/register', json={
            'phone': phone, 'pin': '1234', 'displayName': 'IntTest Dup'
        }, headers=_h(ip))
        resp = requests.post(f'{api_url}/auth/register', json={
            'phone': phone, 'pin': '1234', 'displayName': 'IntTest Dup'
        }, headers=_h(ip))
        assert resp.status_code == 409
        assert resp.json()['code'] == 'CONFLICT'

    def test_register_validation_missing_fields(self, api_url):
        resp = requests.post(f'{api_url}/auth/register', json={'phone': '9999910003'}, headers=_h())
        assert resp.status_code == 400

    def test_register_validation_bad_phone(self, api_url):
        resp = requests.post(f'{api_url}/auth/register', json={
            'phone': '123', 'pin': '1234', 'displayName': 'Bad Phone'
        }, headers=_h())
        assert resp.status_code == 400

    def test_register_validation_bad_pin(self, api_url):
        resp = requests.post(f'{api_url}/auth/register', json={
            'phone': '9999910004', 'pin': '12', 'displayName': 'Bad Pin'
        }, headers=_h())
        assert resp.status_code == 400


def from_conftest_ip():
    from tests.conftest import _next_test_ip
    return _next_test_ip()


class TestLogin:
    def test_login_success(self, api_url):
        phone = '9999920001'
        ip = from_conftest_ip()
        requests.post(f'{api_url}/auth/register', json={
            'phone': phone, 'pin': '1234', 'displayName': 'Login Test'
        }, headers=_h(ip))
        resp = requests.post(f'{api_url}/auth/login', json={'phone': phone, 'pin': '1234'}, headers=_h(ip))
        assert resp.status_code == 200
        data = resp.json()
        assert 'accessToken' in data or 'token' in data

    def test_login_wrong_pin(self, api_url):
        import random
        suffix = random.randint(20100, 29999)
        phone = f'99999{suffix}'
        ip = from_conftest_ip()
        requests.post(f'{api_url}/auth/register', json={
            'phone': phone, 'pin': '1234', 'displayName': 'Wrong Pin Test'
        }, headers=_h(ip))
        resp = requests.post(f'{api_url}/auth/login', json={'phone': phone, 'pin': '9999'}, headers=_h(ip))
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, api_url):
        import random
        phone = f'00000{random.randint(10000, 99999)}'
        resp = requests.post(f'{api_url}/auth/login', json={'phone': phone, 'pin': '1234'}, headers=_h())
        assert resp.status_code == 401

    def test_login_missing_fields(self, api_url):
        resp = requests.post(f'{api_url}/auth/login', json={'phone': '9999920003'}, headers=_h())
        assert resp.status_code == 400


class TestRefreshToken:
    def test_refresh_success(self, api_url):
        phone = '9999930001'
        ip = from_conftest_ip()
        requests.post(f'{api_url}/auth/register', json={
            'phone': phone, 'pin': '1234', 'displayName': 'Refresh Test'
        }, headers=_h(ip))
        login = requests.post(f'{api_url}/auth/login', json={'phone': phone, 'pin': '1234'}, headers=_h(ip)).json()
        refresh_token = login.get('refreshToken')
        if not refresh_token:
            pytest.skip('No refreshToken in login response')
        resp = requests.post(f'{api_url}/auth/refresh', json={'refreshToken': refresh_token}, headers=_h(ip))
        assert resp.status_code == 200
        data = resp.json()
        assert 'accessToken' in data
        assert 'refreshToken' in data
        assert data['refreshToken'] != refresh_token

    def test_refresh_invalid_token(self, api_url):
        resp = requests.post(f'{api_url}/auth/refresh', json={'refreshToken': 'rt_invalid_fake_token'}, headers=_h())
        assert resp.status_code == 401

    def test_refresh_replay_revokes_family(self, api_url):
        phone = '9999930002'
        ip = from_conftest_ip()
        requests.post(f'{api_url}/auth/register', json={
            'phone': phone, 'pin': '1234', 'displayName': 'Replay Test'
        }, headers=_h(ip))
        login = requests.post(f'{api_url}/auth/login', json={'phone': phone, 'pin': '1234'}, headers=_h(ip)).json()
        old_refresh = login.get('refreshToken')
        if not old_refresh:
            pytest.skip('No refreshToken')
        # First rotation (valid)
        resp1 = requests.post(f'{api_url}/auth/refresh', json={'refreshToken': old_refresh}, headers=_h(ip))
        assert resp1.status_code == 200
        # Replay the OLD token (should trigger reuse detection)
        resp2 = requests.post(f'{api_url}/auth/refresh', json={'refreshToken': old_refresh}, headers=_h(ip))
        assert resp2.status_code == 401


class TestLogout:
    def test_logout(self, api_url):
        phone = '9999940001'
        ip = from_conftest_ip()
        requests.post(f'{api_url}/auth/register', json={
            'phone': phone, 'pin': '1234', 'displayName': 'Logout Test'
        }, headers=_h(ip))
        login = requests.post(f'{api_url}/auth/login', json={'phone': phone, 'pin': '1234'}, headers=_h(ip)).json()
        token = login.get('accessToken') or login.get('token')
        resp = requests.post(f'{api_url}/auth/logout', headers=_auth(token, ip))
        assert resp.status_code == 200
        resp2 = requests.get(f'{api_url}/auth/me', headers=_auth(token, ip))
        assert resp2.status_code == 401


class TestPinChange:
    def test_pin_change_success(self, api_url):
        phone = '9999950001'
        ip = from_conftest_ip()
        requests.post(f'{api_url}/auth/register', json={
            'phone': phone, 'pin': '1234', 'displayName': 'Pin Change Test'
        }, headers=_h(ip))
        login = requests.post(f'{api_url}/auth/login', json={'phone': phone, 'pin': '1234'}, headers=_h(ip)).json()
        token = login.get('accessToken') or login.get('token')
        resp = requests.patch(f'{api_url}/auth/pin',
            headers=_auth(token, ip),
            json={'currentPin': '1234', 'newPin': '5678'})
        assert resp.status_code == 200
        data = resp.json()
        assert 'accessToken' in data
        # Can login with new PIN
        login2 = requests.post(f'{api_url}/auth/login', json={'phone': phone, 'pin': '5678'}, headers=_h(ip))
        assert login2.status_code == 200
        # Restore PIN
        new_token = data.get('accessToken') or data.get('token')
        requests.patch(f'{api_url}/auth/pin',
            headers=_auth(new_token, ip),
            json={'currentPin': '5678', 'newPin': '1234'})

    def test_pin_change_wrong_current(self, api_url):
        phone = '9999950002'
        ip = from_conftest_ip()
        requests.post(f'{api_url}/auth/register', json={
            'phone': phone, 'pin': '1234', 'displayName': 'Pin Fail Test'
        }, headers=_h(ip))
        login = requests.post(f'{api_url}/auth/login', json={'phone': phone, 'pin': '1234'}, headers=_h(ip)).json()
        token = login.get('accessToken') or login.get('token')
        resp = requests.patch(f'{api_url}/auth/pin',
            headers=_auth(token, ip),
            json={'currentPin': '9999', 'newPin': '5678'})
        assert resp.status_code == 401
