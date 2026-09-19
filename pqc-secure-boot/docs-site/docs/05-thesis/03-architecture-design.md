# Chapter 3: Secure Bootloader Architecture and Hardware Root-of-Trust

## 3.1 Overview

Secure bootloader architectures establish a continuous Chain of Trust (CoT) that anchors system execution in an immutable Hardware Root of Trust (RoT). This chapter presents the complete architectural specification, state machine transitions, eFuse memory layouts, and cryptographic verification pipelines designed for post-quantum secure bootloaders.

---

## 3.2 Hardware Root of Trust and Public Key Hashing (PKH)

### 3.2.1 The OTP eFuse Storage Bottleneck

In classical secure boot architectures, public keys are stored directly in One-Time Programmable (OTP) eFuse arrays or mapped to dedicated hardware registers:
- RSA-2048 Public Key: 256 bytes (2,048 fuses).
- ECDSA P-256 Public Key: 64 bytes (512 fuses).

For post-quantum lattice-based signature algorithms like ML-DSA-65, the public key size expands to **1,952 bytes** (15,616 fuses). Silicon footprint constraints prohibit allocating thousands of eFuses exclusively for public key storage.

### 3.2.2 Public Key Hashing (PKH) Mechanics

To bypass the physical eFuse limitation, the PQC Secure Boot architecture implements **Public Key Hashing (PKH)**:

1. **Provisioning Time**: During factory manufacturing, the OEM hashes the vendor's PQC Public Key `PK_Vendor` using a collision-resistant cryptographic hash function (SHA-256 or SHA-512):
   `PKH_eFuse = SHA256(PK_Vendor)`
   The resulting 32-byte digest is blown into the device's OTP eFuse bank.
2. **Boot Verification Time**:
   - The Stage-1 binary manifest delivered in Flash contains the full 1,952-byte `PK_Manifest`.
   - Stage-0 ROM reads `PK_Manifest` from external Flash and computes `PKH_Calc = SHA256(PK_Manifest)`.
   - Stage-0 ROM compares `PKH_Calc` byte-for-byte against `PKH_eFuse` stored in OTP memory.
   - Signature verification proceeds **only if** `PKH_Calc == PKH_eFuse`.

```
[ Flash Manifest: PK_Manifest (1952 Bytes) ]
                     |
                SHA-256 Engine
                     |
                     v
           [ PKH_Calc (32 Bytes) ]
                     |
                     +---- ( Equal? ) ----> [ OTP eFuse: PKH_eFuse (32 Bytes) ]
                     |
            +--------+--------+
            |                 |
         [ YES ]           [ NO ]
            |                 |
            v                 v
   Proceed to PQC      BOOT HALTED
  Signature Check      (Security Reset)
```

---

## 3.3 Multi-Stage Chain of Trust (CoT) Pipeline

### 3.3.1 Execution Stages

The boot sequence progresses through three isolated security stages:

1. **Stage-0 (Boot ROM)**:
   - Resides in immutable silicon mask ROM.
   - Executes immediately upon CPU reset.
   - Initialises minimal hardware peripherals (clocks, SRAM controller).
   - Contains immutable LMS/ML-DSA verification primitives.
   - Reads 32-byte `PKH_eFuse` from OTP eFuse memory.
   - Verifies and loads Stage-1 Bootloader into Static RAM (SRAM).

2. **Stage-1 (Secondary Bootloader - SRAM)**:
   - Resides in external Flash, loaded into internal SRAM.
   - Executes basic board initialization (DRAM controller, power management IC).
   - Enforces anti-rollback security version counters.
   - Verifies and loads Stage-2 Kernel into system DRAM.

3. **Stage-2 (Operating System Kernel - DRAM)**:
   - Resides in main system DRAM.
   - Executes rich OS (Linux, Zephyr RTOS, FreeRTOS).

---

## 3.4 Verification State Machine

The verification engine transitions through seven deterministic states:

```
[ STATE_RESET ]
       |
       v
[ STATE_READ_EFUSE ] ----( eFuse Read Error )----> [ STATE_BOOT_HALTED ]
       |
       v
[ STATE_PARSE_MANIFEST ] --( Magic Mismatch )----> [ STATE_BOOT_HALTED ]
       |
       v
[ STATE_VERIFY_PKH ] ----( PKH Mismatch )--------> [ STATE_BOOT_HALTED ]
       |
       v
[ STATE_ANTI_ROLLBACK ] --( Version Downgrade )--> [ STATE_BOOT_HALTED ]
       |
       v
[ STATE_VERIFY_SIG ] ----( PQC Sig Failure )-----> [ STATE_BOOT_HALTED ]
       |
       v
[ STATE_EXECUTE ]
```

---

## 3.5 Anti-Rollback & Key Revocation Architecture

### 3.5.1 Anti-Rollback Counter Burning Mechanism

To prevent adversaries from downgrading device firmware to an older, vulnerable version that possesses a valid signature, the hardware platform incorporates an eFuse Monotonic Counter array.

- **Version Enforcement**: The bootloader enforces `Version_Manifest >= Version_Hardware`.
- **Counter Burning**: During a validated firmware update, Stage-0/Stage-1 code burns additional bits in the eFuse array to increment `Version_Hardware` to match `Version_Manifest`. Because eFuses cannot be unburned, downgrade attacks are physically blocked.

### 3.5.2 Key Revocation Architecture

- **Multiple PKH eFuse Slots**: The eFuse array provides primary and secondary PKH storage slots (e.g., Slot 0, Slot 1, Slot 2).
- **Revocation Bitmap**: A 4-bit eFuse revocation field tracks revoked key slots:
  - Bit 0: Slot 0 Status (0 = Valid, 1 = Revoked).
  - Bit 1: Slot 1 Status (0 = Valid, 1 = Revoked).
- **Verification Rule**: The manifest header specifies the Key Slot ID used. The bootloader rejects any image attempting to verify against a slot marked as revoked in eFuse.
