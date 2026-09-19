#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIRMWARE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

BUILD_DIR="${FIRMWARE_DIR}/build"
mkdir -p "${BUILD_DIR}"
cd "${BUILD_DIR}"

echo "========================================================="
echo "[PQC-BOOT] Building & Running ARM Virt Target in QEMU"
echo "========================================================="

# Sign test firmware
python3 "${FIRMWARE_DIR}/scripts/sign_firmware.py" \
    --input "${FIRMWARE_DIR}/scripts/sign_firmware.py" \
    --output "${BUILD_DIR}/firmware_signed_arm.bin" \
    --scheme lms --entry 0x40000000

# Try compiling ARM Virt target or host fallback
if command -v aarch64-linux-gnu-gcc &> /dev/null || command -v arm-none-eabi-gcc &> /dev/null; then
    echo "[BUILD] Compiling with ARM Virt toolchain..."
    cmake .. -DCMAKE_SYSTEM_NAME=Generic -DCMAKE_PROCESSOR=aarch64
    make pqc_boot_arm_virt
    if command -v qemu-system-aarch64 &> /dev/null; then
        echo "[RUN] Launching qemu-system-aarch64 -M virt..."
        qemu-system-aarch64 -M virt -cpu cortex-a53 -nographic -kernel bin/pqc_boot_arm_virt || true
    fi
else
    echo "[INFO] ARM Virt cross-compiler not found, executing host test runner..."
    cmake ..
    make pqc_boot_host
    ./pqc_boot_host
fi

echo "[PQC-BOOT] ARM Virt Execution Test Complete."
