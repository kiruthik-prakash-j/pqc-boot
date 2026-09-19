# Specification 04: Zero-Allocation Embedded Signature Verification Pipeline

## 1. Multi-Stage Boot Pipeline Overview

The signature verification pipeline is designed to execute under zero-dynamic-memory (zero-heap) allocation constraints inside Stage 0 Boot ROM and Stage 1 Secondary Program Loader (SPL).

```
+-----------------------------------------------------------------------------------+
| BOOT STAGE 0 (BOOT ROM) VERIFICATION PIPELINE STATE MACHINE                       |
+-----------------------------------------------------------------------------------+
  [ STATE 0: HARDWARE BIST & RESET ]
                 |
                 v
  [ STATE 1: FIRMWARE HEADER INGESTION & BOUNDS CHECKING ]
                 |
                 v
  [ STATE 2: PUBLIC KEY HASH (PKH) eFUSE VERIFICATION ]
                 |
                 v
  [ STATE 3: MONOTONIC ROLLBACK COUNTER CHECK ]
                 |
                 v
  [ STATE 4: STREAMING HASH COMPUTATION OVER FIRMWARE PAYLOAD ]
                 |
                 v
  [ STATE 5: PQC SIGNATURE VERIFICATION (ML-DSA-44 / LMS) ]
                 |
                 v
  [ STATE 6: MONOTONIC COUNTER UPDATE (IF UPGRADING) ]
                 |
                 v
  [ STATE 7: ZEROIZATION & JUMP TO STAGE 1 FIRMWARE ENTRY ]
```

---

## 2. Firmware Image Header Structure Specification

All signed firmware images (Stage 1 and Stage 2 payloads) must begin with a standardized 256-byte aligned binary header (`pqc_boot_header_t`).

```c
/**
 * @file pqc_boot_header.h
 * @brief Post-Quantum Secure Boot Image Header Definition
 */

#ifndef PQC_BOOT_HEADER_H
#define PQC_BOOT_HEADER_H

#include <stdint.h>

#define PQC_BOOT_MAGIC           0x50514342  /* ASCII "PQCB" (Post-Quantum Secure Boot) */
#define PQC_HEADER_VERSION_1     0x00010000  /* Format Version 1.0 */
#define PQC_MAX_PUBKEY_SIZE      1952        /* Max size for ML-DSA-65 */
#define PQC_MAX_SIG_SIZE         3309        /* Max size for ML-DSA-65 */

/* Cryptographic Algorithm Identifiers */
typedef enum {
    PQC_HASH_SHA256   = 0x01,
    PQC_HASH_SHA3_256 = 0x02,
    PQC_HASH_SHAKE256 = 0x03
} pqc_hash_alg_t;

typedef enum {
    PQC_SIG_LMS_SHA256_M32_H10 = 0x01,
    PQC_SIG_XMSS_SHA2_10_256   = 0x02,
    PQC_SIG_ML_DSA_44          = 0x10,
    PQC_SIG_ML_DSA_65          = 0x11,
    PQC_SIG_SLH_DSA_SHA2_128F  = 0x20
} pqc_sig_alg_t;

/**
 * @brief Firmware Image Header Structure (Binary Layout: 256-Byte Aligned)
 */
typedef struct __attribute__((packed)) {
    uint32_t magic;              /* Magic Number: 0x50514342 */
    uint32_t header_version;     /* Header Struct Version */
    uint32_t header_size;        /* Total header size in bytes (e.g., 4096) */
    uint32_t image_size;         /* Firmware payload size in bytes */
    uint32_t load_address;       /* Target RAM execution address */
    uint32_t entry_point;        /* Reset handler execution vector */
    uint32_t security_version;   /* Anti-rollback monotonic counter value */
    uint8_t  hash_alg_id;        /* Hash Algorithm Identifier (pqc_hash_alg_t) */
    uint8_t  sig_alg_id;         /* Signature Algorithm ID (pqc_sig_alg_t) */
    uint8_t  reserved[2];        /* Padding / Alignment */
    uint32_t public_key_len;     /* Length of public key payload */
    uint32_t signature_len;      /* Length of signature payload */
    uint8_t  payload_hash[64];   /* Pre-computed expected digest of payload */
    uint8_t  public_key[PQC_MAX_PUBKEY_SIZE]; /* PQC Public Key bytes */
    uint8_t  signature[PQC_MAX_SIG_SIZE];   /* PQC Signature bytes */
} pqc_boot_header_t;

#endif /* PQC_BOOT_HEADER_H */
```

---

## 3. Streaming Hash Engine Interface (SHA-256 / SHAKE256)

To support verifying large firmware payloads (e.g., 2 MB to 16 MB) within limited Stage 0 internal SRAM (e.g., 16 KB SRAM), the hash engine MUST operate in a **chunked streaming mode**. The binary payload is read block-by-block from flash memory into a small stack buffer (e.g., 512 bytes) without loading the full image into RAM at once.

```c
typedef struct {
    uint8_t  state_buffer[256]; /* Hardware/Software SHA context state */
    uint64_t bytes_processed;   /* Total bytes hashed */
    uint8_t  alg_id;            /* PQC_HASH_SHA256 or PQC_HASH_SHAKE256 */
} pqc_hash_ctx_t;

/* Streaming Cryptographic Hash API */
void pqc_hash_init(pqc_hash_ctx_t *ctx, uint8_t alg_id);
void pqc_hash_update(pqc_hash_ctx_t *ctx, const uint8_t *data, size_t len);
void pqc_hash_final(pqc_hash_ctx_t *ctx, uint8_t *digest_out);
```

---

## 4. Step-by-Step Pipeline State Machine Implementation

The complete verification sequence is governed by a strict state machine:

```c
pqc_boot_status_t pqc_verify_pipeline(const pqc_boot_header_t *hdr, uint32_t flash_payload_addr) {
    pqc_boot_status_t status = PQC_BOOT_FAILURE;
    uint8_t efuse_pkh[32];
    uint8_t computed_pkh[32];
    uint8_t computed_payload_hash[64];
    uint32_t efuse_sec_ver = 0;
    pqc_hash_ctx_t hash_ctx;
    
    /* STATE 1: Header Ingestion & Bounds Check */
    if (hdr->magic != PQC_BOOT_MAGIC || hdr->image_size == 0 || hdr->image_size > MAX_FLASH_IMAGE_SIZE) {
        return PQC_BOOT_FAILURE;
    }

    /* STATE 2: eFuse Public Key Hash (PKH) Verification */
    rot_efuse_read_pkh(efuse_pkh);
    pqc_hash_init(&hash_ctx, PQC_HASH_SHA256);
    pqc_hash_update(&hash_ctx, hdr->public_key, hdr->public_key_len);
    pqc_hash_final(&hash_ctx, computed_pkh);
    
    if (const_time_memcmp(efuse_pkh, computed_pkh, 32) != 0) {
        return PQC_BOOT_FAILURE; /* Public key mismatch */
    }

    /* STATE 3: Monotonic Rollback Counter Check */
    rot_efuse_read_security_version(&efuse_sec_ver);
    if (hdr->security_version < efuse_sec_ver) {
        return PQC_BOOT_FAILURE; /* Downgrade attempt detected */
    }

    /* STATE 4: Streaming Binary Payload Hash Computation */
    pqc_hash_init(&hash_ctx, hdr->hash_alg_id);
    uint32_t bytes_remaining = hdr->image_size;
    uint32_t current_addr = flash_payload_addr;
    uint8_t  chunk_buf[512];

    while (bytes_remaining > 0) {
        uint32_t chunk_size = (bytes_remaining > sizeof(chunk_buf)) ? sizeof(chunk_buf) : bytes_remaining;
        flash_read_bytes(current_addr, chunk_buf, chunk_size);
        pqc_hash_update(&hash_ctx, chunk_buf, chunk_size);
        current_addr += chunk_size;
        bytes_remaining -= chunk_size;
    }
    pqc_hash_final(&hash_ctx, computed_payload_hash);

    /* Verify payload digest matches header assertion */
    if (const_time_memcmp(computed_payload_hash, hdr->payload_hash, 32) != 0) {
        return PQC_BOOT_FAILURE;
    }

    /* STATE 5: PQC Signature Verification */
    if (hdr->sig_alg_id == PQC_SIG_ML_DSA_44) {
        status = mldsa44_verify(hdr->public_key, hdr->public_key_len,
                                computed_payload_hash, 32,
                                hdr->signature, hdr->signature_len);
    } else if (hdr->sig_alg_id == PQC_SIG_LMS_SHA256_M32_H10) {
        status = lms_verify(hdr->public_key, hdr->public_key_len,
                            computed_payload_hash, 32,
                            hdr->signature, hdr->signature_len);
    } else {
        return PQC_BOOT_FAILURE; /* Unsupported algorithm */
    }

    if (status != PQC_BOOT_SUCCESS) {
        return PQC_BOOT_FAILURE;
    }

    /* STATE 6: Monotonic Anti-Rollback Counter Update */
    if (hdr->security_version > efuse_sec_ver) {
        rot_efuse_update_security_version(hdr->security_version);
    }

    /* STATE 7: Secure Memory Zeroization before transfer */
    explicit_bzero(chunk_buf, sizeof(chunk_buf));
    explicit_bzero(&hash_ctx, sizeof(hash_ctx));

    return PQC_BOOT_SUCCESS;
}
```

---

## 5. Zero-Allocation Memory Model & Stack Budget

To ensure safety in embedded environments without dynamic memory allocators (`malloc`/`free` are strictly prohibited):
1. **Static Pipeline Context**: All execution variables, polynomial arrays, and hash contexts are allocated on the C execution stack or in a statically declared `.bss` verification buffer block.
2. **Stack Allocation Budget**:
   - `pqc_boot_header_t` pointer: 4 bytes (header read directly from memory-mapped flash or single static buffer).
   - SHA Context (`pqc_hash_ctx_t`): ~ 280 bytes.
   - Streaming Chunk Buffer: 512 bytes.
   - PQC Verification Workspace (ML-DSA-44 NTT & polynomial vectors): **8,192 bytes** static stack frame.
   - **Total Stack Memory Required**: **~ 9.0 KB SRAM**.

```
+-----------------------------------------------------------------------------------+
| STACK FRAME LAYOUT FOR PQC VERIFICATION PIPELINE (TOTAL: 9,192 BYTES)             |
+-----------------------------------------------------------------------------------+
| 0x20002400 | ML-DSA-44 Polynomial Vectors & NTT Workspace (8,192 Bytes)           |
| 0x20000400 | Flash Reading Chunk Buffer (512 Bytes)                             |
| 0x20000200 | Hash Context & State Machinery (280 Bytes)                         |
| 0x20000100 | Temporary Hash Outputs & Variables (208 Bytes)                      |
+-----------------------------------------------------------------------------------+
```

---

## 6. Failure & Exception Handling (Secure Lockout Policy)

If any verification step fails (State 1 through State 5):
1. **Zeroization**: Execute immediate hardware/software memory wipe over SRAM:
   ```c
   void pqc_boot_secure_cleanup(void) {
       volatile uint8_t *sram_ptr = (volatile uint8_t *)SRAM_BASE;
       for (size_t i = 0; i < SRAM_SIZE_BYTES; i++) {
           sram_ptr[i] = 0x00;
       }
   }
   ```
2. **Peripheral Lockout**: Disable SWD/JTAG debug access registers and bus matrix DMA channels.
3. **Execution Termination**: Trigger a system hard reset or enter an infinite loop with Watchdog Timer (WDT) forced reset:
   ```c
   void pqc_boot_secure_reset(void) {
       pqc_boot_secure_cleanup();
       NVIC_SystemReset(); /* ARM Cortex System Reset */
       while(1) { __asm__ volatile("wfi"); }
   }
   ```
