#!/bin/bash
# ==============================================================================
# TRIBE CI Gate v1 — Stage 4A
#
# Runs all test layers in order: unit → integration → smoke
# Exits non-zero on ANY failure in ANY layer.
#
# Usage:
#   ./scripts/ci-gate.sh              # Run all layers
#   ./scripts/ci-gate.sh unit          # Run only unit tests
#   ./scripts/ci-gate.sh integration   # Run only integration tests
#   ./scripts/ci-gate.sh smoke         # Run only smoke tests
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"
TEST_DIR="$APP_DIR/tests"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

TOTAL_PASS=0
TOTAL_FAIL=0
LAYER=$1

echo "=============================================================="
echo "  TRIBE CI GATE v1 — Stage 4A"
echo "=============================================================="
echo ""

run_layer() {
    local layer=$1
    local dir=$2
    echo -e "${YELLOW}[▶] Running $layer tests...${NC}"
    
    if cd "$APP_DIR" && python -m pytest "$dir" -v --tb=short -c "$TEST_DIR/pytest.ini" 2>&1; then
        echo -e "${GREEN}[✓] $layer tests PASSED${NC}"
        TOTAL_PASS=$((TOTAL_PASS + 1))
    else
        echo -e "${RED}[✗] $layer tests FAILED${NC}"
        TOTAL_FAIL=$((TOTAL_FAIL + 1))
    fi
    echo ""
}

# Run requested layer(s)
if [ -z "$LAYER" ] || [ "$LAYER" = "unit" ]; then
    run_layer "UNIT" "tests/unit"
fi

if [ -z "$LAYER" ] || [ "$LAYER" = "integration" ]; then
    run_layer "INTEGRATION" "tests/integration"
fi

if [ -z "$LAYER" ] || [ "$LAYER" = "smoke" ]; then
    run_layer "SMOKE" "tests/smoke"
fi

# Summary
echo "=============================================================="
echo "  CI GATE SUMMARY"
echo "=============================================================="
echo -e "  Layers passed: ${GREEN}$TOTAL_PASS${NC}"
echo -e "  Layers failed: ${RED}$TOTAL_FAIL${NC}"
echo ""

if [ $TOTAL_FAIL -gt 0 ]; then
    echo -e "${RED}  ✗ CI GATE FAILED — $TOTAL_FAIL layer(s) have failures${NC}"
    exit 1
else
    echo -e "${GREEN}  ✓ CI GATE PASSED — all layers green${NC}"
    exit 0
fi
