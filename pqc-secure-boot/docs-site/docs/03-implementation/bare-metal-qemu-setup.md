# Bare-Metal QEMU Setup & Execution Guide

## Overview

To evaluate PQC secure bootloaders without requiring physical silicon, we target bare-metal virtual platforms in QEMU:
- **RISC-V 32/64-bit**: `qemu-system-riscv32` / `qemu-system-riscv64` (virt machine).
- **ARM Cortex-M3 / Cortex-A**: `qemu-system-arm` (lm3s6965evb / virt machine).

---

## 1. Prerequisites & Toolchain

Required toolchains and tools:
```bash
# RISC-V GNU Toolchain
gcc-riscv64-unknown-elf

# ARM GNU Toolchain
gcc-arm-none-eabi

# QEMU System Emulators
qemu-system-riscv32 qemu-system-arm
```

---

## 2. Launching Bootloader in QEMU RISC-V Virt

```bash
qemu-system-riscv32 \
  -machine virt \
  -cpu rv32 \
  -m 64M \
  -nographic \
  -bios none \
  -kernel build/pqc_bootloader.bin \
  -device loader,file=build/signed_kernel.img,addr=0x80200000
```

---

## 3. Emulated Memory Layout

| Memory Region | Address Range | Description |
| :--- | :--- | :--- |
| **Boot ROM (eFuse)** | `0x00001000 - 0x00010000` | Stage-0 Execution & OTP eFuse PK Hash |
| **SRAM Execution** | `0x80000000 - 0x80040000` | Stage-1 Bootloader (256 KB SRAM) |
| **DRAM Execution** | `0x80200000 - 0x84000000` | Target Kernel Payload Memory |

---

## 4. Expected Console Verification Output

```
[PQC-BOOT] Stage-0 Hardware Initialization Complete.
[PQC-BOOT] Reading OTP eFuse Public Key Hash... [OK]
[PQC-BOOT] Manifest Magic: 0x50514342 ("PQCB")
[PQC-BOOT] Selected Algorithm: ML-DSA-44 (NIST FIPS 204)
[PQC-BOOT] Verifying PQC Signature... [SUCCESS] (0.45 ms / 1,350,000 cycles)
[PQC-BOOT] Payload SHA-256 Digest Match: 100%
[PQC-BOOT] Chain of Trust Verified. Jumping to 0x80200000...
```
