"""Unit Tests — request-context.js

Tests: AsyncLocalStorage context propagation, getRequestContext safety
"""
import pytest
from tests.helpers.js_eval import eval_js_raw

pytestmark = pytest.mark.unit


class TestRequestContext:
    def test_returns_empty_object_outside_store(self):
        r = eval_js_raw("""
import { getRequestContext } from './lib/request-context.js';
const ctx = getRequestContext();
process.stdout.write(JSON.stringify({
    isEmpty: Object.keys(ctx).length === 0,
    isObject: typeof ctx === 'object',
}));
process.exit(0);
""")
        assert r['isEmpty'] is True
        assert r['isObject'] is True

    def test_returns_store_inside_run(self):
        r = eval_js_raw("""
import { requestContext, getRequestContext } from './lib/request-context.js';
const store = { requestId: 'test-123', ip: '1.2.3.4', method: 'GET', route: '/test' };
let result;
requestContext.run(store, () => {
    result = getRequestContext();
});
process.stdout.write(JSON.stringify(result));
process.exit(0);
""")
        assert r['requestId'] == 'test-123'
        assert r['ip'] == '1.2.3.4'
        assert r['method'] == 'GET'
        assert r['route'] == '/test'

    def test_context_not_leaked_after_run(self):
        r = eval_js_raw("""
import { requestContext, getRequestContext } from './lib/request-context.js';
const store = { requestId: 'leak-test' };
requestContext.run(store, () => {});
const after = getRequestContext();
process.stdout.write(JSON.stringify({
    isEmpty: Object.keys(after).length === 0,
}));
process.exit(0);
""")
        assert r['isEmpty'] is True

    def test_nested_runs_isolate(self):
        r = eval_js_raw("""
import { requestContext, getRequestContext } from './lib/request-context.js';
let outer, inner, afterInner;
requestContext.run({ requestId: 'outer' }, () => {
    outer = getRequestContext().requestId;
    requestContext.run({ requestId: 'inner' }, () => {
        inner = getRequestContext().requestId;
    });
    afterInner = getRequestContext().requestId;
});
process.stdout.write(JSON.stringify({ outer, inner, afterInner }));
process.exit(0);
""")
        assert r['outer'] == 'outer'
        assert r['inner'] == 'inner'
        assert r['afterInner'] == 'outer'

    def test_mutable_store_in_run(self):
        """Verify userId can be updated mid-request (as route.js does)."""
        r = eval_js_raw("""
import { requestContext, getRequestContext } from './lib/request-context.js';
let beforeAuth, afterAuth;
requestContext.run({ requestId: 'mut-test', userId: null }, () => {
    beforeAuth = getRequestContext().userId;
    const ctx = requestContext.getStore();
    ctx.userId = 'user-abc';
    afterAuth = getRequestContext().userId;
});
process.stdout.write(JSON.stringify({ beforeAuth, afterAuth }));
process.exit(0);
""")
        assert r['beforeAuth'] is None
        assert r['afterAuth'] == 'user-abc'
