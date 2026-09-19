#!/usr/bin/env bash
# Shell runner script for PQC Secure Boot E2E Test Suite
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Executing PQC Secure Boot E2E Test Suite..."
python3 "${SCRIPT_DIR}/run_e2e_tests.py" "$@"
