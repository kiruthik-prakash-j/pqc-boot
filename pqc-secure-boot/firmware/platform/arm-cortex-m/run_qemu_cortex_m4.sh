#!/bin/bash
# Script to run MCUboot / PQC Firmware on ARM Cortex-M4 QEMU (mps2-an386)
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIRMWARE_BIN="${1:-${SCRIPT_DIR}/../../build/pqc_boot_host}"

echo "[QEMU ARM Cortex-M4] Launching QEMU mps2-an386 emulator..."
if command -v qemu-system-arm >/dev/null 2>&1; then
    qemu-system-arm -machine mps2-an386 -cpu cortex-m4 -nographic -kernel "$FIRMWARE_BIN"
else
    echo "[QEMU ARM Cortex-M4] Host test execution (qemu-system-arm simulated mode):"
    "$FIRMWARE_BIN" --verify
fi
