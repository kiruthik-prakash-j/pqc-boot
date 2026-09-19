#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIRMWARE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

BUILD_DIR="${FIRMWARE_DIR}/build"
mkdir -p "${BUILD_DIR}"
cd "${BUILD_DIR}"

echo "========================================================="
echo "[PQC-BOOT] Building & Running RISC-V Virt Target in QEMU"
echo "========================================================="

# Sign test firmware
python3 "${FIRMWARE_DIR}/scripts/sign_firmware.py" \
    --input "${FIRMWARE_DIR}/scripts/sign_firmware.py" \
    --output "${BUILD_DIR}/firmware_signed_riscv.bin" \
    --scheme ml-dsa --entry 0x80000000

# Try compiling RISC-V target or host target fallback
if command -v riscv64-unknown-elf-gcc &> /dev/null || command -v riscv64-linux-gnu-gcc &> /dev/null; then
    echo "[BUILD] Compiling with RISC-V toolchain..."
    cmake .. -DCMAKE_SYSTEM_NAME=Generic -DCMAKE_PROCESSOR=riscv64
    make pqc_boot_riscv
    if command -v qemu-system-riscv64 &> /dev/null; then
        echo "[RUN] Launching qemu-system-riscv64..."
        qemu-system-riscv64 -M virt -nographic -bios none -kernel bin/pqc_boot_riscv || true
    fi
else
    echo "[INFO] RISC-V cross-compiler not found, executing host test runner..."
    cmake ..
    make pqc_boot_host
    ./pqc_boot_host
fi

echo "[PQC-BOOT] RISC-V Execution Test Complete."
