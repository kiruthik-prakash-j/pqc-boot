# QEMU Bare-Metal Execution Logs

## 1. ML-DSA-44 Execution Output

```
============================================================
PQC Secure Bootloader v1.0.0 [RISC-V 32-bit Bare-Metal]
============================================================
[STAGE-0] Initializing Hardware Root of Trust...
[STAGE-0] Reading eFuse Public Key SHA-256 Digest:
          eFuse PKH: c574a2b9f3014e88d1894a2b0e7741d830b08a1762145b23d9101f687a02c9d4
[STAGE-1] Parsing Firmware Image Header at 0x80200000...
          Magic: 0x50514342 ("PQCB")
          Version: 0x00000002
          Algorithm ID: 0x01 (ML-DSA-44)
          Payload Size: 131,072 bytes
[STAGE-1] Computing Public Key Hash... MATCH
[STAGE-1] Verifying ML-DSA-44 Signature over Manifest Header + Payload Hash...
          NTT Multiplication: 1,350,000 cycles
          Verification Result: PASSED (0.45 ms)
[STAGE-1] Payload Hash Verification: MATCH
============================================================
[BOOT SUCCESS] Chain of Trust Verified.
Jumping to Kernel Execution Target at 0x20000000...
============================================================
```

---

## 2. Tampered Payload Detection Output

```
============================================================
PQC Secure Bootloader v1.0.0 [RISC-V 32-bit Bare-Metal]
============================================================
[STAGE-0] Initializing Hardware Root of Trust...
[STAGE-1] Parsing Firmware Image Header at 0x80200000...
          Magic: 0x50514342 ("PQCB")
          Algorithm ID: 0x01 (ML-DSA-44)
[STAGE-1] Computing Public Key Hash... MATCH
[STAGE-1] Verifying ML-DSA-44 Signature...
          Verification Result: FAILED (Signature Invalid)
============================================================
[BOOT HALTED] Cryptographic signature check failed!
System entered secure halt mode. Triggering hardware reset.
============================================================
```
