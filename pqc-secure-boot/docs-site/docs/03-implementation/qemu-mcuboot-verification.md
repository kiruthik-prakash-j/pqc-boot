---
id: qemu-mcuboot-verification
title: QEMU ARM Cortex-M4 Execution & Verification Guide
sidebar_label: QEMU MCUboot Verification
---

# QEMU ARM Cortex-M4 MCUboot Verification Guide

This guide provides step-by-step instructions for compiling MCUboot for **ARM Cortex-M4** (`mps2-an386`), generating PQC signed firmware images using `imgtool`, and running signature authentication tests on QEMU.

---

## 1. Prerequisites & Toolchain Verification

Ensure cross-compilation and emulation tools are available:

```bash
# Verify C compiler and QEMU ARM emulator
arm-none-eabi-gcc --version || gcc --version
qemu-system-arm --version || echo "Host simulation fallback enabled"
python3 --version
```

---

## 2. Step-by-Step Compilation & QEMU Execution

### Step 1: Navigate to Workspace Root
```bash
cd pqc-secure-boot
```

### Step 2: Build MCUboot C Verification Engine & Host Target
```bash
cmake -B firmware/build -S firmware
cmake --build firmware/build
```

### Step 3: Generate PQC Keypair & Sign Sample MCUboot Firmware
Using `scripts/imgtool`:

```bash
cd real_world/mcuboot

# 1. Generate PQC Keypair (ML-DSA-44)
python3 scripts/imgtool/main.py keygen -k keys/ml_dsa_key.json -t ml-dsa-44

# 2. Format & Sign Firmware Payload with PQC TLV (Type 0x80)
python3 scripts/imgtool/main.py sign \
    -k keys/ml_dsa_key.json \
    --header-size 0x200 \
    --align 4 \
    --version 1.0.0+0 \
    --pad-header \
    ../../firmware/build/pqc_boot_host signed_firmware_m4.bin
```

---

## 3. QEMU Launch Commands

### Option A: Direct QEMU Emulation Launch (`mps2-an386` Cortex-M4)
```bash
qemu-system-arm \
    -machine mps2-an386 \
    -cpu cortex-m4 \
    -nographic \
    -kernel firmware/build/pqc_boot_host
```

### Option B: Automated Execution Script
```bash
firmware/platform/arm-cortex-m/run_qemu_cortex_m4.sh
```

---

## 4. Expected Console Log Outputs

### Successful Boot Trace (Valid Signature)
```text
[PQC-BOOT] Initializing Root of Trust...
[PQC-BOOT] Target Platform: ARM MPS2 FPGA (Cortex-M4 / mps2-an386)
[PQC-BOOT] Scheme: ML-DSA-44 (NIST FIPS 204)
[PQC-BOOT] Running PQC Signature Verification engine...
[PQC-BOOT] ML-DSA Signature Verification PASSED
[PQC-BOOT] Booting payload...

========================================
[PAYLOAD] Bare-metal payload executed successfully!
[PAYLOAD] PQC Secure Boot sequence complete.
========================================
```

### Secure Halt Output (Tampered Binary Payload)
If a single byte of the payload or signature is corrupted:
```text
[PQC-BOOT] Initializing Root of Trust...
[PQC-BOOT] Running PQC Signature Verification engine...
[PQC-BOOT] ERROR: Signature Verification FAILED!
[PQC-BOOT] FATAL: Bootloader failed!
```

---

## 5. Automated E2E Test Suite Run

To run all 15 test cases (covering ML-DSA, SPHINCS+, and LMS signature verification, static memory analysis, and boundary rejections):

```bash
python3 tests/run_e2e_tests.py
```
*Result*: `ALL E2E TEST HARNESSES VERIFIED SUCCESSFULLY [SUCCESS]` (15 / 15 Passed).
