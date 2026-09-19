---
id: uboot-qemu-verification
title: "QEMU RISC-V 64 Execution & Verification Guide"
sidebar_label: "QEMU U-Boot Verification"
---

# QEMU RISC-V 64 U-Boot FIT Verification Guide

This guide provides step-by-step instructions for compiling U-Boot with PQC FIT image support, generating signed Device Tree FIT images (`.itb`), and running signature authentication on QEMU RISC-V 64.

---

## 1. Prerequisites & Toolchain Verification

Ensure RISC-V 64 cross-compiler and QEMU emulator are installed:

```bash
riscv64-linux-gnu-gcc --version || gcc --version
qemu-system-riscv64 --version
python3 --version
```

---

## 2. Step-by-Step Compilation & Execution

### Step 1: Navigate to U-Boot Directory
```bash
cd real_world/uboot
```

### Step 2: Configure for QEMU RISC-V 64 Target
```bash
make qemu-riscv64_defconfig
```

### Step 3: Generate FIT Image Source (`sample_pqc.its`)
Create `sample_pqc.its`:

```its
/dts-v1/;
/ {
    description = "PQC-Authenticated RISC-V Linux Kernel FIT Image";
    #address-cells = <1>;
    images {
        kernel-1 {
            description = "RISC-V 64 Linux Kernel";
            data = /incbin/("./Image");
            type = "kernel";
            arch = "riscv";
            os = "linux";
            signature-1 {
                algo = "sha256,ml-dsa-44";
                key-name-hint = "rot_pqc_key";
            };
        };
    };
};
```

### Step 4: Run Automated U-Boot FIT Test Suite
```bash
python3 ../../tests/test_uboot_pqc_fit.py
```

---

## 3. QEMU Launch Commands

```bash
qemu-system-riscv64 \
    -M virt \
    -cpu rv64 \
    -m 256M \
    -nographic \
    -bios none
```

---

## 4. Expected Console Log Trace

### Successful Boot Log (Valid PQC Signature)
```text
=====================================================
 U-Boot FIT PQC Engine Verification (RISC-V 64 virt) 
=====================================================
[TEST 1] Parsing FIT Image Signature Algorithms...
  Algo 1: sha256,ml-dsa-44 -> Checksum: sha256, Crypto: ml-dsa-44 [OK]
PQC ML-DSA-44 signature verified successfully
  -> ML-DSA-44 Signature Verification PASSED
```

### Secure Halt Log (Tampered Payload)
```text
PQC ML-DSA-44 signature verification failed
  -> Tampered Payload Rejection Verified (Boot Halted as expected)
```
