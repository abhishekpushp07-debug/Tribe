"""Integration Tests — Security Guards

Tests: XSS sanitization, oversized payload, missing auth, admin-only denial
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


class TestXSSSanitization:
    def test_xss_in_display_name_stripped(self, api_url):
        phone = '9999970001'
        resp = requests.post(f'{api_url}/auth/register', json={
            'phone': phone, 'pin': '1234',
            'displayName': '<script>alert(1)</script>SafeName'
        }, headers=_h())
        if resp.status_code in (200, 201):
            user = resp.json()['user']
            assert '<script>' not in user['displayName']
            assert 'SafeName' in user['displayName']


class TestPayloadSize:
    def test_oversized_payload_rejected(self, api_url):
        huge_body = {'data': 'x' * (1024 * 1024 + 100)}
        resp = requests.post(f'{api_url}/auth/register', json=huge_body,
            headers=_h())
        assert resp.status_code in (400, 413)


class TestAuthBoundaries:
    def test_protected_endpoint_without_auth(self, api_url):
        resp = requests.get(f'{api_url}/auth/me', headers=_h())
        assert resp.status_code == 401
        assert resp.json()['code'] == 'UNAUTHORIZED'

    def test_admin_endpoint_with_regular_user(self, api_url, test_user):
        resp = requests.get(f'{api_url}/ops/metrics', headers=_auth(test_user['token']))
        assert resp.status_code == 403
        assert resp.json()['code'] == 'FORBIDDEN'

    def test_admin_endpoint_with_admin(self, api_url, admin_user):
        resp = requests.get(f'{api_url}/ops/metrics', headers=_auth(admin_user['token']))
        assert resp.status_code == 200


class TestSecurityHeaders:
    def test_security_headers_present(self, api_url):
        resp = requests.get(f'{api_url}/healthz', headers=_h())
        headers = resp.headers
        assert 'x-content-type-options' in headers
        assert 'x-xss-protection' in headers
        assert 'referrer-policy' in headers
        assert 'strict-transport-security' in headers
        assert 'permissions-policy' in headers
        assert 'x-request-id' in headers

    def test_contract_version_header(self, api_url):
        resp = requests.get(f'{api_url}/healthz', headers=_h())
        assert resp.headers.get('x-contract-version') == 'v2'
