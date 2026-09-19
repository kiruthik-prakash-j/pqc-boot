# U-Boot FIT Image Post-Quantum Cryptography (PQC) Integration

This directory contains the **U-Boot** bootloader repository extended with Flattened Image Tree (FIT) Device Tree Blob (`.itb`) PQC signature verification.

---

## Technical Specifications

- **Target Architecture**: RISC-V 64-bit (`qemu-system-riscv64 -M virt -cpu rv64`).
- **Defconfig**: `configs/qemu-riscv64_defconfig`.
- **FIT Device Tree Node**:
  ```its
  signature-1 {
      algo = "sha256,ml-dsa-44";
      key-name-hint = "rot_pqc_key";
  };
  ```
- **Cryptographic Registration**:
  - `include/u-boot/pqc_fit.h` and `lib/pqc/pqc_fit_verify.c`.
  - Registered in `boot/image-sig.c` via `U_BOOT_CRYPTO_ALGO(ml_dsa_44)`, `U_BOOT_CRYPTO_ALGO(sphincs_plus)`, and `U_BOOT_CRYPTO_ALGO(lms)`.

---

## Verification Test

```bash
# Execute U-Boot FIT PQC Unit Test Harness
python3 ../../tests/test_uboot_pqc_fit.py
```
