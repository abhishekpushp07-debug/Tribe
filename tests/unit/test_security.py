"""
Unit Tests — security.js pure functions

Tests: sanitizeTextInput, deepSanitizeStrings, maskPII, extractIP, getEndpointTier, checkPayloadSize
Method: JS eval bridge (runs actual JS code via Node.js subprocess)
"""
import pytest
from tests.helpers.js_eval import eval_js

SEC = 'import { sanitizeTextInput, deepSanitizeStrings, maskPII, extractIP, getEndpointTier, checkPayloadSize } from "./lib/security.js";'

pytestmark = pytest.mark.unit


# ========== sanitizeTextInput ==========

class TestSanitizeTextInput:
    def test_strips_script_tags(self):
        r = eval_js(SEC, 'sanitizeTextInput("<script>alert(1)</script>hello")')
        assert r == 'hello'

    def test_strips_style_tags(self):
        r = eval_js(SEC, 'sanitizeTextInput("<style>body{display:none}</style>visible")')
        assert r == 'visible'

    def test_strips_html_tags(self):
        r = eval_js(SEC, 'sanitizeTextInput("<b>bold</b> <i>italic</i> plain")')
        assert r == 'bold italic plain'

    def test_strips_event_handlers(self):
        r = eval_js(SEC, 'sanitizeTextInput("hi onload=alert(1) there")')
        assert 'onload' not in r
        assert 'alert' not in r

    def test_strips_javascript_protocol(self):
        r = eval_js(SEC, 'sanitizeTextInput("click javascript:alert(1) here")')
        assert 'javascript' not in r.lower()

    def test_strips_control_chars(self):
        r = eval_js(SEC, r'sanitizeTextInput("hello\x00\x01\x02world")')
        assert r == 'helloworld'

    def test_preserves_clean_text(self):
        r = eval_js(SEC, 'sanitizeTextInput("Hello World! 123 @#$")')
        assert r == 'Hello World! 123 @#$'

    def test_trims_whitespace(self):
        r = eval_js(SEC, 'sanitizeTextInput("  hello  ")')
        assert r == 'hello'

    def test_non_string_passthrough(self):
        r = eval_js(SEC, 'sanitizeTextInput(42)')
        assert r == 42

    def test_empty_string(self):
        r = eval_js(SEC, 'sanitizeTextInput("")')
        assert r == ''

    def test_nested_script_tags(self):
        r = eval_js(SEC, 'sanitizeTextInput("<script><script>alert(1)</script></script>safe")')
        assert 'script' not in r.lower()
        assert 'safe' in r


# ========== deepSanitizeStrings ==========

class TestDeepSanitizeStrings:
    def test_sanitizes_nested_object(self):
        r = eval_js(SEC, 'deepSanitizeStrings({ name: "<script>x</script>clean", bio: "<b>bold</b>" })')
        assert r['name'] == 'clean'
        assert r['bio'] == 'bold'

    def test_sanitizes_array(self):
        r = eval_js(SEC, 'deepSanitizeStrings(["<script>x</script>a", "b", "<i>c</i>"])')
        assert r == ['a', 'b', 'c']

    def test_deep_nesting(self):
        r = eval_js(SEC, 'deepSanitizeStrings({ a: { b: { c: "<script>x</script>deep" } } })')
        assert r['a']['b']['c'] == 'deep'

    def test_preserves_non_strings(self):
        r = eval_js(SEC, 'deepSanitizeStrings({ num: 42, bool: true, nil: null })')
        assert r == {'num': 42, 'bool': True, 'nil': None}


# ========== maskPII ==========

class TestMaskPII:
    def test_masks_phone(self):
        r = eval_js(SEC, 'maskPII({ phone: "9876543210" })')
        assert r['phone'] == '****3210'

    def test_masks_token(self):
        r = eval_js(SEC, 'maskPII({ token: "secret123abc" })')
        assert r['token'] == '***REDACTED***'

    def test_masks_access_token(self):
        r = eval_js(SEC, 'maskPII({ accessToken: "at_abc123" })')
        assert r['accessToken'] == '***REDACTED***'

    def test_masks_refresh_token(self):
        r = eval_js(SEC, 'maskPII({ refreshToken: "rt_xyz" })')
        assert r['refreshToken'] == '***REDACTED***'

    def test_masks_pin(self):
        r = eval_js(SEC, 'maskPII({ pin: "1234" })')
        assert r['pin'] == '****'

    def test_masks_pin_hash(self):
        r = eval_js(SEC, 'maskPII({ pinHash: "abc123hex" })')
        assert r['pinHash'] == '***REDACTED***'

    def test_preserves_safe_fields(self):
        r = eval_js(SEC, 'maskPII({ name: "John", role: "USER" })')
        assert r == {'name': 'John', 'role': 'USER'}

    def test_handles_null(self):
        r = eval_js(SEC, 'maskPII(null)')
        assert r is None


# ========== getEndpointTier ==========

class TestGetEndpointTier:
    def test_auth_login_is_auth_tier(self):
        r = eval_js(SEC, 'getEndpointTier("/auth/login", "POST").name')
        assert r == 'AUTH'

    def test_auth_register_is_auth_tier(self):
        r = eval_js(SEC, 'getEndpointTier("/auth/register", "POST").name')
        assert r == 'AUTH'

    def test_auth_refresh_is_auth_tier(self):
        r = eval_js(SEC, 'getEndpointTier("/auth/refresh", "POST").name')
        assert r == 'AUTH'

    def test_auth_pin_is_sensitive(self):
        r = eval_js(SEC, 'getEndpointTier("/auth/pin", "PATCH").name')
        assert r == 'SENSITIVE'

    def test_admin_is_admin_tier(self):
        r = eval_js(SEC, 'getEndpointTier("/admin/stats", "GET").name')
        assert r == 'ADMIN'

    def test_ops_is_admin_tier(self):
        r = eval_js(SEC, 'getEndpointTier("/ops/metrics", "GET").name')
        assert r == 'ADMIN'

    def test_content_post_is_write(self):
        r = eval_js(SEC, 'getEndpointTier("/content/new", "POST").name')
        assert r == 'WRITE'

    def test_content_like_is_social(self):
        r = eval_js(SEC, 'getEndpointTier("/content/123/like", "POST").name')
        assert r == 'SOCIAL'

    def test_follow_is_social(self):
        r = eval_js(SEC, 'getEndpointTier("/follow/someone", "POST").name')
        assert r == 'SOCIAL'

    def test_get_feed_is_read(self):
        r = eval_js(SEC, 'getEndpointTier("/feed", "GET").name')
        assert r == 'READ'

    def test_session_delete_all_is_sensitive(self):
        r = eval_js(SEC, 'getEndpointTier("/auth/sessions", "DELETE").name')
        assert r == 'SENSITIVE'

    def test_session_delete_one_is_sensitive(self):
        r = eval_js(SEC, 'getEndpointTier("/auth/sessions/abc-123", "DELETE").name')
        assert r == 'SENSITIVE'
