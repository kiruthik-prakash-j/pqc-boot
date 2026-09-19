# EDKII / UEFI SecurityPkg Post-Quantum Cryptography (PQC) Integration

This directory contains the **EDKII (tianocore/edk2)** repository extended with PE/COFF image verification using PKCS#7 OID extensions for Post-Quantum Cryptography.

---

## Technical Specifications

- **Target Architecture**: ARM Cortex-A57 64-bit 4-Core SMP (`qemu-system-aarch64 -M virt -cpu cortex-a57 -smp 4`).
- **UEFI Package**: `SecurityPkg` / `BaseCryptLib` / `DxeImageVerificationLib`.
- **PQC Object Identifiers (OIDs)** (`SecurityPkg/Include/Library/PqcVerify.h`):
  - `OID_ML_DSA_44` = `"2.16.840.1.101.3.4.3.17"` (NIST FIPS 204)
  - `OID_SPHINCS_PLUS` = `"2.16.840.1.101.3.4.3.20"` (NIST FIPS 205)
  - `OID_LMS_HASH` = `"1.2.840.113549.1.9.16.3.17"` (RFC 8708 / RFC 8554)
- **C Engine**: `SecurityPkg/Library/DxeImageVerificationLib/Pkcs7VerifyPqc.c`.

---

## Verification Test

```bash
# Execute UEFI SecurityPkg Unit Test Harness
python3 ../../tests/test_uefi_pqc_securitypkg.py

# Launch QEMU ARM Cortex-A57 4-Core SMP Simulation
../../firmware/platform/arm-cortex-a/run_qemu_cortex_a57_smp.sh
```
