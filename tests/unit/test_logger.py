"""Unit Tests — logger.js pure functions

Tests: redactPII, level filtering, output format
"""
import pytest
from tests.helpers.js_eval import eval_js_raw

pytestmark = pytest.mark.unit


class TestRedactPII:
    def test_redacts_token(self):
        r = eval_js_raw("""
import { logger } from './lib/logger.js';
// Access redactPII indirectly by capturing logger output
// Actually, redactPII is not exported. We test it through the logger.
// Let's test by checking what the logger does with sensitive fields.

// Capture stdout
let captured = '';
const origWrite = process.stdout.write;
process.stdout.write = (chunk) => { captured += chunk; return true; };

logger.info('TEST', 'test_event', { token: 'secret123', name: 'John' });

process.stdout.write = origWrite;
const parsed = JSON.parse(captured);
process.stdout.write(JSON.stringify({
    token: parsed.token,
    name: parsed.name,
}));
process.exit(0);
""")
        assert r['token'] == '***REDACTED***'
        assert r['name'] == 'John'

    def test_redacts_password(self):
        r = eval_js_raw("""
import { logger } from './lib/logger.js';
let captured = '';
const origWrite = process.stdout.write;
process.stdout.write = (chunk) => { captured += chunk; return true; };
logger.info('TEST', 'test', { password: 'secret', authorization: 'Bearer xyz' });
process.stdout.write = origWrite;
const parsed = JSON.parse(captured);
process.stdout.write(JSON.stringify({
    password: parsed.password,
    authorization: parsed.authorization,
}));
process.exit(0);
""")
        assert r['password'] == '***REDACTED***'
        assert r['authorization'] == '***REDACTED***'

    def test_redacts_pin_variants(self):
        r = eval_js_raw("""
import { logger } from './lib/logger.js';
let captured = '';
const origWrite = process.stdout.write;
process.stdout.write = (chunk) => { captured += chunk; return true; };
logger.info('TEST', 'test', { pin: '1234', currentPin: '5678', newPin: '9012', pinHash: 'abc', pinSalt: 'def' });
process.stdout.write = origWrite;
const parsed = JSON.parse(captured);
process.stdout.write(JSON.stringify(parsed));
process.exit(0);
""")
        assert r['pin'] == '***REDACTED***'
        assert r['currentPin'] == '***REDACTED***'
        assert r['newPin'] == '***REDACTED***'
        assert r['pinHash'] == '***REDACTED***'
        assert r['pinSalt'] == '***REDACTED***'

    def test_handles_nested_pii(self):
        r = eval_js_raw("""
import { logger } from './lib/logger.js';
let captured = '';
const origWrite = process.stdout.write;
process.stdout.write = (chunk) => { captured += chunk; return true; };
logger.info('TEST', 'test', { user: { token: 'secret', name: 'John' } });
process.stdout.write = origWrite;
const parsed = JSON.parse(captured);
process.stdout.write(JSON.stringify({ nested_token: parsed.user.token, nested_name: parsed.user.name }));
process.exit(0);
""")
        assert r['nested_token'] == '***REDACTED***'
        assert r['nested_name'] == 'John'


class TestLoggerOutput:
    def test_ndjson_format(self):
        r = eval_js_raw("""
import { logger } from './lib/logger.js';
let captured = '';
const origWrite = process.stdout.write;
process.stdout.write = (chunk) => { captured += chunk; return true; };
logger.info('HTTP', 'test_message', { requestId: '123' });
process.stdout.write = origWrite;
const parsed = JSON.parse(captured);
process.stdout.write(JSON.stringify({
    hasTimestamp: typeof parsed.timestamp === 'string',
    hasLevel: parsed.level === 'INFO',
    hasCategory: parsed.category === 'HTTP',
    hasMsg: parsed.msg === 'test_message',
    hasRequestId: parsed.requestId === '123',
}));
process.exit(0);
""")
        assert r['hasTimestamp'] is True
        assert r['hasLevel'] is True
        assert r['hasCategory'] is True
        assert r['hasMsg'] is True
        assert r['hasRequestId'] is True

    def test_error_goes_to_stderr(self):
        r = eval_js_raw("""
import { logger } from './lib/logger.js';
let stdoutCap = '';
let stderrCap = '';
const origOut = process.stdout.write;
const origErr = process.stderr.write;
process.stdout.write = (chunk) => { stdoutCap += chunk; return true; };
process.stderr.write = (chunk) => { stderrCap += chunk; return true; };
logger.info('TEST', 'info_msg');
logger.error('TEST', 'error_msg');
process.stdout.write = origOut;
process.stderr.write = origErr;
process.stdout.write(JSON.stringify({
    infoInStdout: stdoutCap.includes('info_msg'),
    errorInStderr: stderrCap.includes('error_msg'),
}));
process.exit(0);
""")
        assert r['infoInStdout'] is True
        assert r['errorInStderr'] is True
