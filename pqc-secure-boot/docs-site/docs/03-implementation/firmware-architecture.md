# Secure Bootloader Firmware Architecture

## Overview

The PQC Secure Bootloader architecture implements a strict Chain of Trust (CoT) starting from an immutable Hardware Root of Trust (RoT) down to the operating system payload.

---

## Bootloader Execution Stages

```
+------------------------------------+
| Stage-0: Boot ROM                  |
| - Immutable mask ROM               |
| - eFuse Public Key Hash (PKH)      |
| - PQC Verification Engine          |
+------------------------------------+
                   |
     Authenticates & Loads
                   v
+------------------------------------+
| Stage-1: Secondary Bootloader (SRAM)|
| - Peripheral Initialization         |
| - Security Policy Enforcement      |
| - Zero-Malloc Buffer Pipeline      |
+------------------------------------+
                   |
     Authenticates & Executes
                   v
+------------------------------------+
| Stage-2: Kernel Payload (DRAM)     |
| - Linux / Zephyr OS execution      |
+------------------------------------+
```

---

## Manifest Format & Header Structure

Firmware binaries are packaged with a 512-byte signed header manifest:

```c
typedef struct __attribute__((packed)) {
    uint32_t magic;           // 0x50514342 ("PQCB")
    uint32_t header_version;  // Version counter (anti-rollback)
    uint32_t image_size;      // Payload length in bytes
    uint32_t load_address;    // SRAM/DRAM execution target address (e.g., 0x20000000)
    uint32_t entry_point;     // Jump entry point address
    uint32_t algo_id;         // PQC Algorithm ID (0x01: ML-DSA-44, 0x02: ML-DSA-87, 0x03: LMS, 0x04: SLH-DSA)
    uint8_t  payload_hash[32];// SHA-256 digest of payload binary
    uint8_t  reserved[64];    // Future extensions
    uint16_t pk_size;         // Public key size in bytes
    uint16_t sig_size;        // Signature size in bytes
    uint8_t  public_key[2592];// Public key buffer
    uint8_t  signature[17088];// Signature buffer
} pqc_boot_manifest_t;
```

---

## Verification Control Flow

1. **Hardware eFuse Check**: Compute `SHA-256(manifest.public_key)` and assert equality with `OTP_EFUSE_PK_HASH`.
2. **Header Validation**: Check `magic == 0x50514342` and verify anti-rollback counter.
3. **PQC Signature Verification**: Execute chosen PQC verification algorithm over `manifest.header` and `manifest.payload_hash`.
4. **Payload Digest Verification**: Compute SHA-256 over target payload memory range and compare against `manifest.payload_hash`.
5. **Execution Handover**: Flush instruction cache and jump to `entry_point`.
