#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# GitHub Codespaces Automatic Setup Script for PQC Secure Boot
set -e

echo "================================================================================"
echo "    INITIALIZING PQC SECURE BOOT ENVIRONMENT (GITHUB CODESPACES)"
echo "================================================================================"

# 1. Update and install required QEMU emulators, cross-compilers, and dependencies
echo "[1/4] Installing QEMU system emulators and cross-compilers..."
sudo apt-get update -y
sudo apt-get install -y --no-install-recommends \
    qemu-system-arm \
    qemu-system-misc \
    qemu-system-x86 \
    gcc-arm-none-eabi \
    libnewlib-arm-none-eabi \
    gcc-aarch64-linux-gnu \
    cmake \
    build-essential \
    libssl-dev \
    libfdt-dev \
    device-tree-compiler \
    python3-pip \
    python3-pytest \
    python3-tabulate \
    curl \
    git

# Attempt RISC-V cross-compiler installation (either elf or linux-gnu)
sudo apt-get install -y --no-install-recommends gcc-riscv64-unknown-elf || \
sudo apt-get install -y --no-install-recommends gcc-riscv64-linux-gnu || true

# 2. Synchronize Git Submodules (MCUboot, U-Boot, EDK2)
echo "[2/4] Initializing Git submodules (shallow clone for efficiency)..."
git submodule update --init --recursive --depth 1 || echo "[WARN] Git submodule update had warnings, continuing..."

# 3. Build native C Reference PQC Firmware Engine
echo "[3/4] Building C reference PQC firmware engine..."
mkdir -p pqc-secure-boot/firmware/build
cmake -B pqc-secure-boot/firmware/build -S pqc-secure-boot/firmware
make -C pqc-secure-boot/firmware/build pqc_boot_host

# 4. Set execution permissions for QEMU launchers and profiling tools
echo "[4/4] Setting execution permissions for QEMU launchers and profiling tools..."
chmod +x pqc-secure-boot/firmware/scripts/*.sh 2>/dev/null || true
chmod +x pqc-secure-boot/firmware/platform/*/*.sh 2>/dev/null || true
chmod +x pqc-secure-boot/tests/*.sh 2>/dev/null || true
chmod +x pqc-secure-boot/scripts/*.sh 2>/dev/null || true
chmod +x pqc-secure-boot/scripts/*.py 2>/dev/null || true

echo "================================================================================"
echo "    PQC SECURE BOOT ENVIRONMENT SETUP COMPLETE!"
echo ""
echo "    Commands to get started:"
echo "    1. Run All Tests:      python3 pqc-secure-boot/tests/run_e2e_tests.py"
echo "    2. Run Profiler:       python3 pqc-secure-boot/scripts/profile_targets.py --target all"
echo "    3. Run QEMU M4:        bash pqc-secure-boot/firmware/platform/arm-cortex-m/run_qemu_cortex_m4.sh"
echo "    4. Run QEMU RISC-V:    bash pqc-secure-boot/firmware/scripts/run_qemu_riscv.sh"
echo "    5. Run QEMU A57 SMP:   bash pqc-secure-boot/firmware/platform/arm-cortex-a/run_qemu_cortex_a57_smp.sh"
echo "================================================================================"
