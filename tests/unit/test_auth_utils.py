"""Unit Tests — auth-utils.js pure functions

Tests: hashPin/verifyPin, generateToken format, checkLoginThrottle, parsePagination, sanitizeUser
"""
import pytest
from tests.helpers.js_eval import eval_js, eval_js_raw

pytestmark = pytest.mark.unit

AUTH = 'import { generateSalt, hashPin, verifyPin, generateToken, generateAccessToken, generateRefreshToken, checkLoginThrottle, recordLoginFailure, clearLoginFailures, sanitizeUser } from "./lib/auth-utils.js";'


class TestPinHashing:
    def test_hash_roundtrip(self):
        r = eval_js_raw(f"""
{AUTH}
const salt = generateSalt();
const hash = hashPin('1234', salt);
const valid = verifyPin('1234', salt, hash);
const invalid = verifyPin('5678', salt, hash);
process.stdout.write(JSON.stringify({{ valid, invalid }}));
process.exit(0);
""")
        assert r['valid'] is True
        assert r['invalid'] is False

    def test_different_salts_different_hashes(self):
        r = eval_js_raw(f"""
{AUTH}
const salt1 = generateSalt();
const salt2 = generateSalt();
const hash1 = hashPin('1234', salt1);
const hash2 = hashPin('1234', salt2);
process.stdout.write(JSON.stringify({{ same: hash1 === hash2, len1: hash1.length, len2: hash2.length }}));
process.exit(0);
""")
        assert r['same'] is False
        assert r['len1'] > 32
        assert r['len2'] > 32


class TestTokenGeneration:
    def test_access_token_format(self):
        r = eval_js(AUTH, '({ token: generateAccessToken(), prefix: generateAccessToken().startsWith("at_") })')
        assert r['prefix'] is True
        assert len(r['token']) > 30

    def test_refresh_token_format(self):
        r = eval_js(AUTH, '({ token: generateRefreshToken(), prefix: generateRefreshToken().startsWith("rt_") })')
        assert r['prefix'] is True
        assert len(r['token']) > 50

    def test_tokens_are_unique(self):
        r = eval_js(AUTH, '({ t1: generateAccessToken(), t2: generateAccessToken() })')
        assert r['t1'] != r['t2']


class TestLoginThrottle:
    def test_first_attempt_allowed(self):
        r = eval_js(AUTH, 'checkLoginThrottle("9999999999")')
        assert r['allowed'] is True

    def test_throttle_after_5_failures(self):
        r = eval_js_raw(f"""
{AUTH}
const phone = '8888888888';
for (let i = 0; i < 5; i++) recordLoginFailure(phone);
const result = checkLoginThrottle(phone);
process.stdout.write(JSON.stringify(result));
process.exit(0);
""")
        assert r['allowed'] is False
        assert 'retryAfterSec' in r

    def test_clear_resets_throttle(self):
        r = eval_js_raw(f"""
{AUTH}
const phone = '7777777777';
for (let i = 0; i < 5; i++) recordLoginFailure(phone);
clearLoginFailures(phone);
const result = checkLoginThrottle(phone);
process.stdout.write(JSON.stringify(result));
process.exit(0);
""")
        assert r['allowed'] is True


class TestSanitizeUser:
    def test_strips_id_and_pin(self):
        r = eval_js(AUTH, 'sanitizeUser({ _id: "mongo_id", id: "user-1", pinHash: "abc", pinSalt: "def", displayName: "John" })')
        assert '_id' not in r
        assert 'pinHash' not in r
        assert 'pinSalt' not in r
        assert r['id'] == 'user-1'
        assert r['displayName'] == 'John'

    def test_null_returns_null(self):
        r = eval_js(AUTH, 'sanitizeUser(null)')
        assert r is None
