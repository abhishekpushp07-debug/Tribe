"""Integration Tests — Observability Endpoints

Tests: /healthz, /readyz, /ops/health, /ops/metrics, /ops/slis
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


class TestLiveness:
    def test_healthz_returns_ok(self, api_url):
        resp = requests.get(f'{api_url}/healthz', headers=_h())
        assert resp.status_code == 200
        data = resp.json()
        assert data['status'] == 'ok'
        assert 'uptime' in data
        assert 'timestamp' in data

    def test_healthz_has_request_id(self, api_url):
        resp = requests.get(f'{api_url}/healthz', headers=_h())
        assert 'x-request-id' in resp.headers
        rid = resp.headers['x-request-id']
        assert len(rid) == 36
        assert rid.count('-') == 4


class TestReadiness:
    def test_readyz_returns_status(self, api_url):
        resp = requests.get(f'{api_url}/readyz', headers=_h())
        assert resp.status_code == 200
        data = resp.json()
        assert 'ready' in data
        assert data['ready'] is True
        assert 'status' in data
        assert 'checks' in data
        assert 'mongo' in data['checks']

    def test_readyz_mongo_healthy(self, api_url):
        resp = requests.get(f'{api_url}/readyz', headers=_h())
        data = resp.json()
        assert data['checks']['mongo']['status'] in ('ok', 'slow')


class TestDeepHealth:
    def test_ops_health_requires_auth(self, api_url):
        resp = requests.get(f'{api_url}/ops/health', headers=_h())
        assert resp.status_code == 401

    def test_ops_health_requires_admin(self, api_url, test_user):
        resp = requests.get(f'{api_url}/ops/health', headers=_auth(test_user['token']))
        assert resp.status_code == 403

    def test_ops_health_admin_success(self, api_url, admin_user):
        resp = requests.get(f'{api_url}/ops/health', headers=_auth(admin_user['token']))
        assert resp.status_code == 200
        data = resp.json()
        assert 'status' in data
        assert 'checks' in data
        assert 'mongodb' in data['checks']
        assert 'redis' in data['checks']
        assert 'rateLimiter' in data['checks']
        assert 'moderation' in data['checks']
        assert 'objectStorage' in data['checks']
        assert 'auditSystem' in data['checks']
        assert 'slis' in data


class TestMetrics:
    def test_ops_metrics_requires_auth(self, api_url):
        resp = requests.get(f'{api_url}/ops/metrics', headers=_h())
        assert resp.status_code == 401

    def test_ops_metrics_admin_success(self, api_url, admin_user):
        resp = requests.get(f'{api_url}/ops/metrics', headers=_auth(admin_user['token']))
        assert resp.status_code == 200
        data = resp.json()
        assert 'http' in data
        assert 'totalRequests' in data['http']
        assert 'latency' in data['http']
        assert 'statusCodes' in data['http']
        assert 'errorCodes' in data
        assert 'rateLimiting' in data
        assert 'dependencies' in data
        assert 'topRoutes' in data
        assert 'business' in data

    def test_ops_metrics_has_percentiles(self, api_url, admin_user):
        resp = requests.get(f'{api_url}/ops/metrics', headers=_auth(admin_user['token']))
        latency = resp.json()['http']['latency']
        assert 'p50Ms' in latency
        assert 'p95Ms' in latency
        assert 'p99Ms' in latency


class TestSLIs:
    def test_ops_slis_requires_auth(self, api_url):
        resp = requests.get(f'{api_url}/ops/slis', headers=_h())
        assert resp.status_code == 401

    def test_ops_slis_admin_success(self, api_url, admin_user):
        resp = requests.get(f'{api_url}/ops/slis', headers=_auth(admin_user['token']))
        assert resp.status_code == 200
        data = resp.json()
        assert 'errorRate' in data
        assert 'latency' in data
        assert 'counters' in data
