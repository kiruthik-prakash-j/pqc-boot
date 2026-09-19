# Specification 03: Root-of-Trust (RoT) Public Key Storage, PKH Verification & Revocation

## 1. Root-of-Trust (RoT) Architecture & Hardware Assumptions

The Root of Trust (RoT) forms the foundational anchor of system security. It consists of hardware elements whose integrity and authenticity are implicitly trusted and cannot be modified after factory manufacturing:
1. **Root of Trust for Verification (RoTV)**: Executable code embedded immutably inside hardware Mask ROM (Stage 0).
2. **Root of Trust for Storage (RoTS)**: A physical One-Time Programmable (OTP) eFuse array integrated directly into the SoC die.

```
+-----------------------------------------------------------------------------------+
| SoC SILICON DIE / OTP eFUSE ARRAY MAP (512 Bytes / 4096 Bits)                     |
+-----------------------------------------------------------------------------------+
| Offset      | Field Name                   | Size     | Lock Bit                  |
+-------------+------------------------------+----------+---------------------------+
| 0x000 - 0x01F| Primary Root PKH (SHA-256)   | 32 Bytes | eFuse Bit 0 (ROTV_LOCK_0) |
| 0x020 - 0x03F| Secondary Root PKH (SHA-256) | 32 Bytes | eFuse Bit 1 (ROTV_LOCK_1) |
| 0x040 - 0x043| Key Revocation Vector        | 4 Bytes  | eFuse Bit 2 (REV_LOCK)    |
| 0x044 - 0x047| Anti-Rollback Counter Bank   | 4 Bytes  | eFuse Bit 3 (CNT_LOCK)    |
| 0x048 - 0x04B| Hardware Security Flags      | 4 Bytes  | eFuse Bit 4 (SEC_LOCK)    |
| 0x04C - 0x1FF| Reserved / Custom OEM OTP    | 436 Bytes| OEM Lock Bits             |
+-----------------------------------------------------------------------------------+
```

---

## 2. OTP / eFuse Flash Memory Programming Model

### 2.1 Physical eFuse Characteristics
- **Bit-Burning Mechanics**: eFuses start in an unprogrammed logic `0` state. Programming involves applying a controlled high-voltage pulse ($V_{PP} \approx 1.8\text{V} - 2.5\text{V}$) to vaporize polysilicon links, permanently shifting the state to logic `1`.
- **Irreversibility**: Burning an eFuse bit is physically irreversible.
- **Hardware Lock Bits**: Once the Root Public Key Hash (PKH) is written to the eFuse bank during factory provisioning, a dedicated lock bit (`ROTV_LOCK`) is burned. Once set, the hardware eFuse controller blocks any further programming voltage pulses ($V_{PP}$) to the PKH registers.

### 2.2 Security Flag Mapping (Offset `0x048`)
- Bit 0: `JTAG_DISABLE` — Permanently disables hardware debugging interfaces (SWD/JTAG).
- Bit 1: `SECURE_BOOT_EN` — Forces the CPU to execute Stage 0 ROM on power-on reset.
- Bit 2: `PKH_LOCKED` — Prevents further modification of the Root PKH slots.
- Bit 3: `FAIL_HALT_EN` — Controls reset vs hard halt behavior on verification failure.

---

## 3. Public Key Hash (PKH) Verification Scheme

### 3.1 Motivation for Hash-Based Public Key Anchoring
PQC public keys, particularly lattice-based signatures like ML-DSA-44 (**1,312 bytes**) and ML-DSA-65 (**1,952 bytes**), are too large to fit into hardware eFuse arrays (which typically offer 32 to 128 bytes of secure storage).

To solve this, the architecture stores a **256-bit (32-byte) SHA-256 Public Key Hash (PKH)** in eFuse. The full PQC public key is embedded inside the firmware binary header.

$$\text{PKH}_{\text{eFuse}} = \text{SHA-256}(\text{Public Key}_{\text{Header}})$$

```
                                +-----------------------------------+
                                | Firmware Header (in External Flash)|
                                | +-------------------------------+ |
                                | | PQC Public Key (1,312 Bytes)  | |
                                | +-------------------------------+ |
                                +-----------------|-----------------+
                                                  |
                                                  v
                                      [ Hardware SHA-256 Engine ]
                                                  |
                                                  v  Computed PKH (32 Bytes)
                                      +-----------+-----------+
                                      |                       |
                                      v                       v
+-----------------------+     +---------------+       +---------------+
| eFuse Array (On-Chip) |---->| PKH Read Reg  |  ===  | Computed PKH  |
| Primary PKH (32 Bytes)|     +---------------+       +---------------+
+-----------------------+             |                       |
                                      +-----------+-----------+
                                                  |
                                                  v
                                      Constant-Time Comparison
                                                  |
                                  +---------------+---------------+
                                  |                               |
                              [ Match ]                       [ Mismatch ]
                                  |                               |
                                  v                               v
                       Proceed to PQC Signature             Abort Boot &
                             Verification                    Secure Reset
```

### 3.2 Verification Sequence in Stage 0 Boot ROM
1. **Ingest Public Key**: Read the 1,312-byte ML-DSA public key from the firmware image header in flash.
2. **Compute Digest**: Execute SHA-256 over the public key bytes to produce a 32-byte candidate hash: $\text{PKH}_{\text{cand}} = \text{SHA-256}(\text{PK}_{\text{Header}})$.
3. **Read eFuse**: Read the 32-byte reference hash $\text{PKH}_{\text{eFuse}}$ from eFuse address offset `0x000`.
4. **Constant-Time Verification**: Perform a bitwise constant-time memcmp. If $\text{PKH}_{\text{cand}} \neq \text{PKH}_{\text{eFuse}}$, abort execution and trigger a secure hardware reset.

---

## 4. Dual-Key & Multi-Key Revocation Hierarchy

To protect against key compromise without bricking deployed devices in the field, the architecture implements a two-tier key delegation and revocation hierarchy.

```
                    +-----------------------------------+
                    |  PRIMARY ROOT OF TRUST (RoT KEY)  |
                    |   (Offline Cold Storage / HSM)    |
                    +-----------------|-----------------+
                                      |
                   Signs Key Delegation Manifest
                                      |
                                      v
                    +-----------------------------------+
                    | SECONDARY OEM FIRMWARE SIGNING KEY|
                    |    (Online Signing Server HSM)    |
                    +-----------------|-----------------+
                                      |
                     Signs Firmware Binary Payload
                                      |
                                      v
                    +-----------------------------------+
                    |  TARGET EMBEDDED DEVICE FIRMWARE  |
                    +-----------------------------------+
```

### 4.1 Key Manifest Header Structure
When a dual-key hierarchy is used, the firmware image contains a **Key Manifest** preceding the firmware header:

```c
typedef struct __attribute__((packed)) {
    uint32_t manifest_magic;       /* 0x4D4E4653 ("MNFS") */
    uint32_t key_index;            /* 0 = Primary RoT, 1 = Secondary Key 1, etc. */
    uint8_t  root_pubkey[1312];    /* ML-DSA-44 Root Public Key */
    uint8_t  oem_pubkey[1312];     /* ML-DSA-44 Secondary OEM Public Key */
    uint32_t delegation_sig_len;   /* Length of delegation signature */
    uint8_t  delegation_sig[2420]; /* Root Key Signature over OEM Public Key */
} pqc_key_manifest_t;
```

### 4.2 eFuse Bit-Vector Revocation Mask
The eFuse array contains a 32-bit field at offset `0x040` acting as a bit-vector revocation mask for secondary keys.

- `0x00000000`: All secondary keys valid.
- `0x00000001`: Key Slot 0 Revoked (eFuse bit 0 burned).
- `0x00000003`: Key Slots 0 and 1 Revoked (eFuse bits 0 and 1 burned).

If an online OEM signing key is compromised:
1. OEM issues a new firmware package signed by **Secondary Key 2** with a **Revocation Certificate** signed by the **Primary Root Key**.
2. Stage 0 ROM verifies the Revocation Certificate using the Primary Root Key (whose hash matches eFuse).
3. Upon verification, Stage 0 ROM burns bit `0` of the eFuse Revocation Vector.
4. Any future bootloader attempts using Key Slot 0 will be rejected by Stage 0 ROM.

---

## 5. Hardware Abstraction Layer (HAL) C API Specifications

Below are the normative C HAL interface definitions required for RoT storage and key verification.

```c
/**
 * @file rot_storage.h
 * @brief Hardware Abstraction Layer for Root-of-Trust eFuse & PKH Verification
 */

#ifndef ROT_STORAGE_H
#define ROT_STORAGE_H

#include <stdint.h>
#include <stddef.h>

#define PQC_PKH_SIZE_BYTES       32   /* SHA-256 PKH digest length */
#define PQC_MLDSA44_PK_SIZE    1312   /* ML-DSA-44 Public Key size */
#define PQC_HAL_SUCCESS  0x5A5A3C3C
#define PQC_HAL_ERROR    0xA5A5C3C3

/**
 * @brief Read the Primary Root Public Key Hash from OTP eFuse.
 * @param[out] pkh_buffer Pointer to 32-byte output buffer.
 * @return PQC_HAL_SUCCESS on successful read, PQC_HAL_ERROR on hardware error.
 */
uint32_t rot_efuse_read_pkh(uint8_t pkh_buffer[PQC_PKH_SIZE_BYTES]);

/**
 * @brief Read the 32-bit Key Revocation Vector from OTP eFuse.
 * @param[out] revocation_mask Pointer to 32-bit bit-vector mask.
 * @return PQC_HAL_SUCCESS on successful read.
 */
uint32_t rot_efuse_read_revocation_mask(uint32_t *revocation_mask);

/**
 * @brief Permanently burn a revocation bit for a compromised key index.
 * @param[in] key_index Key slot index (0 to 31) to revoke.
 * @return PQC_HAL_SUCCESS on successful write/lock.
 */
uint32_t rot_efuse_revoke_key_index(uint32_t key_index);

/**
 * @brief Verifies that a provided public key matches the eFuse PKH in constant time.
 * @param[in] pubkey Pointer to PQC Public Key bytes.
 * @param[in] pubkey_len Size of public key in bytes.
 * @return PQC_HAL_SUCCESS if SHA256(pubkey) matches eFuse PKH, PQC_HAL_ERROR otherwise.
 */
uint32_t rot_verify_public_key_hash(const uint8_t *pubkey, size_t pubkey_len);

#endif /* ROT_STORAGE_H */
```
