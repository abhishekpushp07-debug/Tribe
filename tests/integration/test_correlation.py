"""Integration Tests — Request Correlation & Audit Trail

Tests: x-request-id roundtrip, audit DB entries with requestId, error code metrics proof
"""
import pytest
import requests
import time

pytestmark = pytest.mark.integration


def _h(ip=None):
    from tests.conftest import _next_test_ip, _make_headers
    return _make_headers(ip=ip or _next_test_ip())


def _auth(token, ip=None):
    from tests.conftest import auth_header
    return auth_header(token, ip=ip)


class TestRequestIdHeader:
    def test_request_id_on_success(self, api_url):
        resp = requests.get(f'{api_url}/healthz', headers=_h())
        rid = resp.headers.get('x-request-id')
        assert rid is not None
        assert len(rid) == 36

    def test_request_id_on_error(self, api_url):
        resp = requests.get(f'{api_url}/nonexistent-route-correlation-test', headers=_h())
        assert resp.status_code == 404
        rid = resp.headers.get('x-request-id')
        assert rid is not None
        assert len(rid) == 36

    def test_request_id_unique_per_request(self, api_url):
        ip = None  # healthz doesn't need unique IP (not rate-limited per se)
        r1 = requests.get(f'{api_url}/healthz', headers=_h())
        r2 = requests.get(f'{api_url}/healthz', headers=_h())
        assert r1.headers['x-request-id'] != r2.headers['x-request-id']


class TestAuditCorrelation:
    def test_login_creates_audit_with_request_id(self, api_url, db):
        phone = '9999980001'
        ip = None
        from tests.conftest import _next_test_ip
        ip = _next_test_ip()
        requests.post(f'{api_url}/auth/register', json={
            'phone': phone, 'pin': '1234', 'displayName': 'Correlation Test'
        }, headers=_h(ip))
        resp = requests.post(f'{api_url}/auth/login', json={'phone': phone, 'pin': '1234'}, headers=_h(ip))
        assert resp.status_code == 200
        request_id = resp.headers.get('x-request-id')
        assert request_id is not None
        time.sleep(0.5)
        audit = db.audit_logs.find_one({'requestId': request_id})
        assert audit is not None, f'No audit entry found for requestId={request_id}'
        assert audit['requestId'] == request_id
        assert audit.get('ip') is not None
        assert audit.get('route') is not None

    def test_new_audit_entries_have_category(self, db):
        recent = list(db.audit_logs.find(
            {'requestId': {'$ne': None}},
            {'_id': 0, 'category': 1, 'requestId': 1}
        ).sort('createdAt', -1).limit(5))
        assert len(recent) > 0
        for entry in recent:
            assert entry.get('category') is not None

    def test_audit_has_severity(self, db):
        recent = list(db.audit_logs.find(
            {'requestId': {'$ne': None}},
            {'_id': 0, 'severity': 1, 'requestId': 1}
        ).sort('createdAt', -1).limit(5))
        for entry in recent:
            assert entry.get('severity') in ('INFO', 'WARN', 'CRITICAL')


class TestErrorCodeMetrics:
    def test_404_increments_not_found(self, api_url, admin_user):
        m1 = requests.get(f'{api_url}/ops/metrics', headers=_auth(admin_user['token'])).json()
        baseline = m1.get('errorCodes', {}).get('NOT_FOUND', 0)
        requests.get(f'{api_url}/error-code-test-404-route', headers=_h())
        m2 = requests.get(f'{api_url}/ops/metrics', headers=_auth(admin_user['token'])).json()
        after = m2.get('errorCodes', {}).get('NOT_FOUND', 0)
        assert after > baseline

    def test_401_increments_unauthorized(self, api_url, admin_user):
        m1 = requests.get(f'{api_url}/ops/metrics', headers=_auth(admin_user['token'])).json()
        baseline = m1.get('errorCodes', {}).get('UNAUTHORIZED', 0)
        requests.get(f'{api_url}/ops/health', headers=_h())
        m2 = requests.get(f'{api_url}/ops/metrics', headers=_auth(admin_user['token'])).json()
        after = m2.get('errorCodes', {}).get('UNAUTHORIZED', 0)
        assert after > baseline

    def test_403_increments_forbidden(self, api_url, admin_user, test_user):
        m1 = requests.get(f'{api_url}/ops/metrics', headers=_auth(admin_user['token'])).json()
        baseline = m1.get('errorCodes', {}).get('FORBIDDEN', 0)
        requests.get(f'{api_url}/ops/health', headers=_auth(test_user['token']))
        m2 = requests.get(f'{api_url}/ops/metrics', headers=_auth(admin_user['token'])).json()
        after = m2.get('errorCodes', {}).get('FORBIDDEN', 0)
        assert after > baseline
