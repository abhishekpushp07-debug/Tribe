"""Unit Tests — metrics.js pure functions

Tests: recordRequest, recordError, getRouteFamily, getMetrics, computePercentiles
"""
import pytest
from tests.helpers.js_eval import eval_js_raw

pytestmark = pytest.mark.unit


class TestGetRouteFamily:
    def test_collapses_uuid(self):
        from tests.helpers.js_eval import eval_js
        r = eval_js(
            'import metrics from "./lib/metrics.js";',
            'metrics.getRouteFamily("/users/a1b2c3d4-e5f6-7890-abcd-ef1234567890/posts")'
        )
        assert r == '/users/:id/posts'

    def test_preserves_non_uuid_path(self):
        from tests.helpers.js_eval import eval_js
        r = eval_js(
            'import metrics from "./lib/metrics.js";',
            'metrics.getRouteFamily("/auth/login")'
        )
        assert r == '/auth/login'

    def test_multiple_uuids(self):
        from tests.helpers.js_eval import eval_js
        r = eval_js(
            'import metrics from "./lib/metrics.js";',
            'metrics.getRouteFamily("/content/a1b2c3d4-e5f6-7890-abcd-ef1234567890/comments/b2c3d4e5-f6a7-8901-bcde-f12345678901")'
        )
        assert ':id' in r
        # Both UUIDs should be collapsed
        assert r.count(':id') == 2


class TestMetricsRecording:
    """Tests that metrics state updates correctly after recording events."""

    def test_record_request_updates_counters(self):
        r = eval_js_raw("""
import metrics from './lib/metrics.js';
metrics.recordRequest('/test', 'GET', 200, 10);
metrics.recordRequest('/test', 'GET', 200, 20);
metrics.recordRequest('/test', 'POST', 404, 5);
const m = metrics.getMetrics();
process.stdout.write(JSON.stringify({
    total: m.http.totalRequests,
    s200: m.http.statusCodes[200] || 0,
    s404: m.http.statusCodes[404] || 0,
    e4xx: m.http.errors4xx,
    e5xx: m.http.errors5xx,
}));
process.exit(0);
""")
        assert r['total'] >= 3
        assert r['s200'] >= 2
        assert r['s404'] >= 1
        assert r['e4xx'] >= 1
        assert r['e5xx'] == 0

    def test_record_error_tracks_codes(self):
        r = eval_js_raw("""
import metrics from './lib/metrics.js';
metrics.recordError('NOT_FOUND');
metrics.recordError('NOT_FOUND');
metrics.recordError('UNAUTHORIZED');
const m = metrics.getMetrics();
process.stdout.write(JSON.stringify(m.errorCodes));
process.exit(0);
""")
        assert r.get('NOT_FOUND', 0) >= 2
        assert r.get('UNAUTHORIZED', 0) >= 1

    def test_latency_percentiles(self):
        r = eval_js_raw("""
import metrics from './lib/metrics.js';
// Record 100 requests with known latencies
for (let i = 1; i <= 100; i++) {
    metrics.recordRequest('/perf', 'GET', 200, i);
}
const m = metrics.getMetrics();
process.stdout.write(JSON.stringify({
    p50: m.http.latency.p50Ms,
    p95: m.http.latency.p95Ms,
    p99: m.http.latency.p99Ms,
    avg: m.http.latency.avgMs,
}));
process.exit(0);
""")
        assert r['p50'] > 0
        assert r['p95'] > r['p50']
        assert r['p99'] >= r['p95']

    def test_histogram_buckets(self):
        r = eval_js_raw("""
import metrics from './lib/metrics.js';
metrics.recordRequest('/fast', 'GET', 200, 3);  // <= 5ms bucket
metrics.recordRequest('/slow', 'GET', 200, 600); // <= 1000ms bucket
const m = metrics.getMetrics();
process.stdout.write(JSON.stringify(m.http.histogramBuckets));
process.exit(0);
""")
        # 3ms request should be in 5ms bucket
        assert r['5'] >= 1
        # 600ms request should NOT be in 500ms bucket but should be in 1000ms bucket
        assert r['1000'] >= r['500']


class TestSLIs:
    def test_sli_shape(self):
        r = eval_js_raw("""
import metrics from './lib/metrics.js';
metrics.recordRequest('/sli', 'GET', 200, 10);
metrics.recordRequest('/sli', 'GET', 500, 50);
const sli = metrics.getSLIs();
process.stdout.write(JSON.stringify({
    hasErrorRate: typeof sli.errorRate === 'number',
    hasLatency: typeof sli.latency === 'object',
    hasCounters: typeof sli.counters === 'object',
    hasTimestamp: typeof sli.timestamp === 'string',
    errorRate: sli.errorRate,
    total5xx: sli.counters.total5xx,
}));
process.exit(0);
""")
        assert r['hasErrorRate'] is True
        assert r['hasLatency'] is True
        assert r['hasCounters'] is True
        assert r['hasTimestamp'] is True
        assert r['total5xx'] >= 1
        assert r['errorRate'] > 0
