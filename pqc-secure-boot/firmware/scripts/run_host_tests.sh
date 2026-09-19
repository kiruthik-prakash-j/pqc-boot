#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIRMWARE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

BUILD_DIR="${FIRMWARE_DIR}/build"
mkdir -p "${BUILD_DIR}"
cd "${BUILD_DIR}"

echo "========================================================="
echo "[PQC-BOOT] Host Native Execution & Verification Test Suite"
echo "========================================================="

cmake ..
make pqc_boot_host

echo ""
echo "[RUN] Executing pqc_boot_host binary..."
./pqc_boot_host

echo ""
echo "[CHECK] Verifying Zero Dynamic Memory Allocation..."
if nm pqc_boot_host | grep -iE "(malloc|free|realloc|calloc)"; then
    echo "ERROR: Dynamic memory symbols detected!"
    exit 1
else
    echo "SUCCESS: Zero dynamic memory allocation verified! No heap allocation symbols present."
fi

echo "========================================================="
echo "[PQC-BOOT] All Host Tests Passed Successfully."
echo "========================================================="
