"""
JS Eval Bridge — Runs JavaScript ES module code from pytest.

Since the Tribe backend is Node.js/Next.js, pure function unit tests
must execute actual JS code. This bridge creates temp .mjs files,
runs them with Node.js, and returns parsed JSON results.

Usage:
    from tests.helpers.js_eval import eval_js
    result = eval_js('import { fn } from "./lib/mod.js"; fn("input")')
"""
import subprocess
import json
import os
import tempfile

APP_ROOT = '/app'

def eval_js(import_stmt, expression, timeout=8):
    """Run a JS expression with imports and return the result as Python object.
    
    Args:
        import_stmt: ES module import statement(s)
        expression: JS expression that evaluates to a JSON-serializable value
        timeout: Max seconds to wait
    
    Returns:
        Parsed JSON result from the JS expression
    """
    code = f"""
{import_stmt}
const __result__ = {expression};
process.stdout.write(JSON.stringify(__result__));
process.exit(0);
"""
    fd, path = tempfile.mkstemp(suffix='.mjs', dir=APP_ROOT)
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(code)
        result = subprocess.run(
            ['node', path],
            capture_output=True, text=True, cwd=APP_ROOT,
            timeout=timeout
        )
        if result.returncode != 0:
            stderr = result.stderr.split('\n')
            # Filter out module type warnings
            errors = [l for l in stderr if l and 'MODULE_TYPELESS' not in l and 'trace-warnings' not in l]
            if errors:
                raise RuntimeError(f"JS error: {''.join(errors)}")
        if not result.stdout.strip():
            raise RuntimeError(f"JS returned empty output. stderr: {result.stderr[:300]}")
        return json.loads(result.stdout)
    finally:
        os.unlink(path)


def eval_js_raw(code, timeout=8):
    """Run arbitrary JS code. Code must write JSON to stdout and call process.exit(0)."""
    fd, path = tempfile.mkstemp(suffix='.mjs', dir=APP_ROOT)
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(code)
        result = subprocess.run(
            ['node', path],
            capture_output=True, text=True, cwd=APP_ROOT,
            timeout=timeout
        )
        if result.returncode != 0:
            stderr = [l for l in result.stderr.split('\n') if l and 'MODULE_TYPELESS' not in l]
            if stderr:
                raise RuntimeError(f"JS error: {''.join(stderr)}")
        return json.loads(result.stdout) if result.stdout.strip() else None
    finally:
        os.unlink(path)
