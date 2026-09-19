# Specification 02: End-to-End PQC Secure Boot Threat Model & Security Hypotheses

## 1. System Overview & Architectural Scope

The Post-Quantum Cryptographic (PQC) Secure Boot architecture establishes a hardware-anchored chain of trust for embedded SoCs, microcontrollers, and IoT systems. The target execution flow consists of three sequential boot stages:
- **Stage 0 (Boot ROM)**: Mask ROM code burned during chip fabrication. Executes directly from silicon ROM and establishes the Root of Trust for Verification (RoTV).
- **Stage 1 (Secondary Program Loader / SPL)**: First-stage bootloader residing in non-volatile flash memory, executed in internal SRAM after Stage 0 verification.
- **Stage 2 (Application Firmware / OS Kernel)**: Main application payload or Rich OS kernel residing in external/internal flash, verified and executed by Stage 1.

```
+-----------------------------------------------------------------------------------+
|                            HARDWARE ROOT OF TRUST (RoT)                           |
|  +--------------------------------+   +---------------------------------------+  |
|  | Mask ROM (Stage 0 Code)        |   | OTP / eFuse (PKH Digest & Anti-Roll)  |  |
|  +--------------------------------+   +---------------------------------------+  |
+-----------------------------------------|-----------------------------------------+
                                          | Verify Stage 1 Header & Signature
                                          v
+-----------------------------------------------------------------------------------+
| STAGE 1 BOOTLOADER (SPL)                | Trusted Execution Environment (SRAM)    |
+-----------------------------------------|-----------------------------------------+
                                          | Verify Stage 2 Header & Signature
                                          v
+-----------------------------------------------------------------------------------+
| STAGE 2 APPLICATION FIRMWARE / KERNEL   | Main System Flash Memory                |
+-----------------------------------------------------------------------------------+
```

---

## 2. Security Hypotheses & System Assumptions

The security of the PQC Secure Boot pipeline relies on the following fundamental security hypotheses:

1. **H1 — Immutable Mask ROM Hypothesis**: Stage 0 code residing in hardware Mask ROM cannot be altered, patched, or bypassed by software or post-fabrication physical manipulation.
2. **H2 — eFuse Write-Once Integrity Hypothesis**: The One-Time Programmable (OTP) eFuse array, once programmed and locked via hardware lock-bits (`PKH_LOCKED`), cannot be rewritten, reset, or cleared back to unprogrammed states.
3. **H3 — Offline Signing Authority Isolation Hypothesis**: Private keys used for signing Stage 1 and Stage 2 firmware are generated, stored, and managed strictly inside Hardware Security Modules (HSMs) isolated from production networks, internet access, and build infrastructure.
4. **H4 — Hardware Hash Engine Timing Immunity Hypothesis**: Cryptographic hash accelerators (SHA-256 / SHA-3 / SHAKE256) operate in constant time with respect to input message data, preventing timing side-channel leakage.
5. **H5 — Non-Volatile Anti-Rollback Counter Hypothesis**: The hardware eFuse monotonic counter increments sequentially and cannot be decremented under any operational or environmental condition.

---

## 3. Trust Boundaries

The system is compartmentalized into five explicit Trust Boundaries:

```
[ External World / Untrusted ]
     |
     | Boundary 4: External Interfaces (UART, SPI, USB, CAN, OTA)
     v
[ Boundary 3: Flash Storage / Application Payload ]
     |
     | Boundary 2: Stage 1 / Stage 2 Headers & Signatures in Flash
     v
[ Boundary 1: Internal SRAM & SoC Internal Bus Architecture ]
     |
     | Boundary 0: Silicon Die / Immutable ROM & eFuse (HARDWARE RoT)
```

- **Boundary 0 (Silicon Core / Hardware RoT)**: *Highest Trust*. Includes Mask ROM, eFuse array, and on-chip crypto engine. Hardware-enforced read/write protection.
- **Boundary 1 (Stage 0 SRAM Execution Realm)**: *High Trust*. Internal SRAM during Stage 0 verification. Isolated from external memory buses.
- **Boundary 2 (Non-Volatile Flash Partitioning)**: *Medium Trust*. Contains Stage 1 SPL, Stage 2 Firmware, and image headers. Subject to flash tampering, corruption, or replacement via hardware probes.
- **Boundary 3 (Runtime System Execution Environment)**: *Variable Trust*. Operating environment once Stage 2 application takes control.
- **Boundary 4 (External Peripheral Interfaces)**: *Untrusted*. UART debugging ports, JTAG/SWD interfaces, SPI flash lines, USB, CAN bus, and wireless Over-The-Air (OTA) update channels.

---

## 4. Threat Vectors & Vulnerability Analysis Matrix

The threat model evaluates four primary categories of adversaries: Remote Network Attackers, Local Physical Attackers, Hardware Glitching Attackers, and Post-Quantum Cryptanalytic Attackers.

| Threat ID | Threat Vector | Target Boundary | Attack Mechanism | Impact | Architectural Mitigation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TV-01** | Firmware Tampering / Code Injection | Boundary 2, 3 | Malicious modification of firmware binary in SPI flash. | Execution of unauthorized code, privilege escalation, persistent rootkit. | PQC digital signature (ML-DSA / LMS) verification over full image digest before branching. |
| **TV-02** | Rollback / Downgrade Attack | Boundary 2 | Re-flashing older, legitimately signed firmware containing known security flaws. | Re-introduction of patched vulnerabilities. | Monotonic anti-rollback counter verified against hardware eFuse counter bits (`efuse_version >= header_version`). |
| **TV-03** | Branch Skipping via Voltage Glitching | Boundary 0, 1 | Injecting voltage spikes on $V_{DD}$ rail during `if (verify_signature() == SUCCESS)` branch evaluation. | Bypassing cryptographic signature verification entirely. | Fault-tolerant branch logic, double-evaluation, glitch-hardened boolean returns, random execution delay jitter. |
| **TV-04** | eFuse Read Glitching | Boundary 0 | Fault injection during OTP read to force read value to all `0x00` or `0xFF`. | Spoofing blank eFuse state or bypassing PKH match check. | Dual-read eFuse verification, non-zero hash checksum validation, redundant eFuse bit inversion checks. |
| **TV-05** | Quantum Cryptanalysis (Shor's Algo) | Boundary 0 - 3 | Quantum computer running Shor's algorithm against classical public keys (RSA/ECC). | Derivation of private signing key from public key; arbitrary signature forgery. | Deprecation of RSA/ECDSA; migration to NIST-standardized PQC signatures (ML-DSA-44 / LMS). |
| **TV-06** | Quantum Collision Search (Grover's Algo) | Boundary 0 - 3 | Quantum quadratic speedup ($O(\sqrt{N})$) against pre-image / collision resistance of hashes. | Finding hash collisions for signed firmware payloads. | Use of 256-bit+ quantum-secure hash functions (SHA-256 yields 128-bit quantum security; SHAKE256 / SHA3-384 yields 192-bit+ quantum security). |
| **TV-07** | JTAG / SWD Memory Probe | Boundary 1, 4 | Attaching hardware debugger during Stage 0/1 boot to read SRAM or alter instruction pointer. | Dumping secret keys, altering register contents during signature check. | Hardware JTAG lock-bits (`JTAG_DISABLE`) blown in eFuse during manufacturing provisioning. |
| **TV-08** | Header Spoofing / Malformed Structure | Boundary 2 | Injecting integer overflows or out-of-bound offsets into boot image header fields. | Buffer overflow, stack smash, or pointer hijacking during header parsing. | Zero-allocation strict header bounds parser with explicit length validation prior to memory copy. |

---

## 5. Architectural Countermeasures & Mitigation Protocols

### 5.1 Fault-Tolerant Glitch-Resistant Branching Strategy
To prevent single instruction skips via voltage/clock glitching from bypassing signature verification, the bootloader must avoid simple boolean returns (`true`/`false` or `0`/`1`).

```c
/* Glitch-Hardened Verification Return Identifiers */
typedef enum {
    PQC_BOOT_SUCCESS = 0x5A5A3C3C, /* Balanced Hamming weight 32-bit constant */
    PQC_BOOT_FAILURE = 0xA5A5C3C3  /* Bitwise inverse of SUCCESS */
} pqc_boot_status_t;

/* Double-Check Verification Macro */
#define GLITCH_SAFE_VERIFY(expr) do { \
    pqc_boot_status_t res1 = (expr); \
    pqc_boot_status_t res2 = (expr); \
    if ((res1 != PQC_BOOT_SUCCESS) || (res2 != PQC_BOOT_SUCCESS)) { \
        pqc_boot_secure_reset(); \
    } \
} while(0)
```

### 5.2 Quantum Grover Protection for Hashing Engine
Grover's search algorithm reduces the effective collision search complexity of an $n$-bit hash function to $2^{n/3}$ (for multi-target collisions) and preimage complexity to $2^{n/2}$.
- **SHA-256**: Provides 128 bits of quantum preimage security. Suitable for standard Level 1 / Category 1 security.
- **SHAKE256 / SHA3-384**: Configured with 256-bit or 384-bit output digests, providing 192 to 256 bits of quantum preimage and collision security, completely mitigating Grover attacks.

### 5.3 Anti-Rollback Monotonic eFuse Counter Protocol
Each signed firmware header carries a 32-bit monotonic `security_version` field.
1. Stage 0 ROM reads `efuse_security_version` (number of blown bits in monotonic eFuse bank).
2. If `header.security_version < efuse_security_version`, verification fails immediately with `PQC_BOOT_FAILURE`.
3. If `header.security_version > efuse_security_version`, Stage 0 verifies the signature first. Upon successful verification, Stage 0 blows the additional eFuse bits to equal `header.security_version` before jumping to the new firmware image.

### 5.4 Zeroization & Failure Reset Policy
If any threat vector triggers a validation error (header checksum mismatch, PKH mismatch, signature verification failure, rollback attempt):
1. **Immediate Zeroization**: The bootloader overwrites internal SRAM stack/buffers with `0x00` and `0xFF` using `explicit_bzero()` or hardware crypto wipe commands.
2. **Peripheral Isolation**: Disables JTAG/SWD, resets DMA controllers, and revokes external bus access.
3. **Hardware Reset / Lockout**: Issues a forced system reset via Watchdog Timer (WDT) trigger or `NVIC_SystemReset()`, incrementing an error counter in persistent tamper RAM to implement exponential boot delay throttling.
