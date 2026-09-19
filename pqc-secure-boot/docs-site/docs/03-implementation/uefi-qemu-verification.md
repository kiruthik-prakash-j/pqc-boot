---
id: uefi-qemu-verification
title: "QEMU ARM Cortex-A57 4-Core SMP Verification Guide"
sidebar_label: "QEMU UEFI Verification"
---

# QEMU ARM Cortex-A57 4-Core SMP UEFI Verification Guide

This guide provides step-by-step instructions for running EDKII / UEFI SecurityPkg PE/COFF image verification on QEMU ARM Cortex-A57 across 4 SMP CPU cores.

---

## 1. Prerequisites & Toolchain Verification

Ensure AArch64 cross-compiler and QEMU emulator are installed:

```bash
aarch64-linux-gnu-gcc --version || gcc --version
qemu-system-aarch64 --version
python3 --version
```

---

## 2. Step-by-Step Compilation & Execution

### Step 1: Navigate to Workspace Root
```bash
cd pqc-secure-boot
```

### Step 2: Execute Automated UEFI SecurityPkg Test Suite
```bash
python3 tests/test_uefi_pqc_securitypkg.py
```

### Step 3: Run QEMU ARM Cortex-A57 4-Core SMP Launcher
```bash
./firmware/platform/arm-cortex-a/run_qemu_cortex_a57_smp.sh
```

---

## 3. Direct QEMU Emulation Command

```bash
qemu-system-aarch64 \
    -M virt \
    -cpu cortex-a57 \
    -smp 4 \
    -m 1024M \
    -nographic \
    -kernel firmware/build/pqc_boot_host
```

---

## 4. Expected Console Log Trace

```text
================================================================================
    POST-QUANTUM SECURE BOOT: EDKII / UEFI ARM CORTEX-A57 4-CORE SMP (QEMU)
================================================================================
Target Processor: ARM Cortex-A57 64-bit (AArch64)
Multiprocessor Topology: 4-Core SMP (-smp 4)
UEFI Secure Boot Database: db (Authenticated RoT Key)
================================================================================
[UEFI-PQC] Initializing 4 ARM Cortex-A57 SMP cores...
[UEFI-PQC] Loading SecurityPkg DxeImageVerificationLib with Pkcs7VerifyPqc...
[UEFI-PQC] Verifying PE/COFF image digest against ML-DSA-44 db RoT key...
[UEFI-PQC] SUCCESS: PE/COFF PQC signature verified across 4 SMP Cores!
[UEFI-PQC] Transferring execution to UEFI OS Bootloader.
```
