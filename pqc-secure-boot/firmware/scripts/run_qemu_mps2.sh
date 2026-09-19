#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIRMWARE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

BUILD_DIR="${FIRMWARE_DIR}/build"
mkdir -p "${BUILD_DIR}"
cd "${BUILD_DIR}"

echo "========================================================="
echo "[PQC-BOOT] Building & Running MPS2-AN385 Target in QEMU"
echo "========================================================="

# Sign test firmware
python3 "${FIRMWARE_DIR}/scripts/sign_firmware.py" \
    --input "${FIRMWARE_DIR}/scripts/sign_firmware.py" \
    --output "${BUILD_DIR}/firmware_signed_mps2.bin" \
    --scheme sphincs+ --entry 0x00000000

# Try compiling ARM Cortex-M target or host fallback
if command -v arm-none-eabi-gcc &> /dev/null; then
    echo "[BUILD] Compiling with ARM toolchain..."
    cmake .. -DCMAKE_SYSTEM_NAME=Generic -DCMAKE_PROCESSOR=arm
    make pqc_boot_mps2
    if command -v qemu-system-arm &> /dev/null; then
        echo "[RUN] Launching qemu-system-arm -M mps2-an385..."
        qemu-system-arm -M mps2-an385 -nographic -kernel bin/pqc_boot_mps2 || true
    fi
else
    echo "[INFO] ARM cross-compiler not found, executing host test runner..."
    cmake ..
    make pqc_boot_host
    ./pqc_boot_host
fi

echo "[PQC-BOOT] MPS2 Execution Test Complete."
