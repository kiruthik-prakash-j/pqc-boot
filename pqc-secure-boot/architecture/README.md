# Post-Quantum Cryptographic (PQC) Secure Boot Architecture

## Executive Overview

Welcome to the **Post-Quantum Cryptographic Secure Boot Architecture** specification repository, designed and maintained by **Dr. Q-Boot (Cryptographic Architect & Mentor)**.

This architecture establishes an end-to-end, zero-allocation, hardware-anchored secure boot framework for resource-constrained embedded microcontrollers (ARM Cortex-M, RISC-V RV32) and System-on-Chips (SoCs). It transitions classical boot trust chains (RSA / ECDSA) to NIST-standardized Post-Quantum Cryptography algorithms:
- **ML-DSA (Dilithium - NIST FIPS 204)**: Primary stateless lattice-based signature scheme.
- **LMS (Leighton-Micali Signature - RFC 8554 / NIST SP 800-208)**: Secondary stateful hash-based signature scheme.
- **SLH-DSA (SPHINCS+ - NIST FIPS 205)**: Tertiary stateless hash-based signature scheme.

---

## Architectural Directory Structure

```
architecture/
├── README.md                                # Master Architecture Index & Mentor Guide (This File)
└── specs/
    ├── 01_pqc_signature_tradeoff_matrix.md  # PQC Algorithm Evaluation, Performance & Resource Matrix
    ├── 02_secure_boot_threat_model.md       # End-to-End Threat Model, Trust Boundaries & Hypotheses
    ├── 03_root_of_trust_key_storage.md      # OTP eFuse Layout, PKH Verification & Revocation
    ├── 04_signature_verification_pipeline.md# Multi-Stage Bootloader Pipeline & Zero-Heap Execution
    └── 05_key_lifecycle_management.md     # Offline Signing Ceremonies, Provisioning & Anti-Rollback
```

---

## Specification Index

| Document | Title | Core Topics Covered |
| :--- | :--- | :--- |
| [**Spec 01**](./specs/01_pqc_signature_tradeoff_matrix.md) | **PQC Signature Trade-Off Matrix** | Comparative breakdown of LMS, XMSS, ML-DSA-44/65, and SLH-DSA; signature size, public key size, RAM stack footprint, CPU cycles, state risk analysis. |
| [**Spec 02**](./specs/02_secure_boot_threat_model.md) | **Secure Boot Threat Model** | Trust boundaries (0-4), Security Hypotheses (H1-H5), Threat Vectors (tampering, rollback, glitching, Shor/Grover quantum attacks), anti-glitch branch hardening. |
| [**Spec 03**](./specs/03_root_of_trust_key_storage.md) | **Root-of-Trust Key Storage** | OTP/eFuse flash programming model, 256-bit Public Key Hash (PKH) verification, dual-key hierarchy, revocation vector, C HAL header API. |
| [**Spec 04**](./specs/04_signature_verification_pipeline.md) | **Signature Verification Pipeline** | Multi-stage bootloader flow (Stage 0 ROM to Stage 1 SPL), `pqc_boot_header_t` struct, streaming SHA-256/SHAKE256 engine, zero-allocation memory model, failure reset. |
| [**Spec 05**](./specs/05_key_lifecycle_management.md) | **Key Lifecycle & Signing Ceremonies**| TRNG entropy requirements, air-gapped M-of-N offline signing ceremony, factory eFuse provisioning, anti-rollback monotonic counters, emergency PQC response. |

---

## Core Architectural Guarantees

1. **Quantum Resilience**: Resistant to quantum attacks targeting public-key cryptography (Shor's algorithm) and hash collisions (Grover's algorithm).
2. **Zero-Allocation Safety**: Strictly zero dynamic heap allocation (`malloc`/`free` prohibited). Verification operates within static stack frames (~9 KB SRAM max).
3. **Hardware Root of Trust**: Anchored by Mask ROM (Stage 0) and OTP eFuse arrays storing a 256-bit SHA-256 digest of the Primary Root Public Key.
4. **Physical Glitch Resistance**: All critical verification return codes use Hamming-balanced 32-bit constants (`0x5A5A3C3C`) with dual-evaluation execution guards to prevent fault-injection branch skipping.
5. **Anti-Rollback Protection**: Hardware eFuse monotonic bit-counters reject firmware downgrades (`V_header < V_efuse`).
6. **Crypto Agility**: Standardized header algorithm identifiers (`sig_alg_id`) enable seamless switching between ML-DSA, LMS, and SLH-DSA without modifying immutable Stage 0 ROM code.

---

## Key System Parameters Summary

| Metric | System Design Specification |
| :--- | :--- |
| **Primary PQC Algorithm** | ML-DSA-44 (NIST FIPS 204) |
| **Primary Hash Engine** | SHA-256 (Default) / SHAKE256 (High Security) |
| **eFuse Storage Allocation** | 32 Bytes (Root PKH) + 4 Bytes (Revocation) + 4 Bytes (Anti-Rollback) |
| **Header Overhead** | 256-Byte Aligned (4096-Byte total header slot including signature payload) |
| **Stage 0 SRAM Footprint** | ~ 9.0 KB Total Stack Budget |
| **Verification Latency** | ~ 3.5 ms @ 120 MHz (ML-DSA-44) / ~ 10.0 ms @ 120 MHz (LMS) |
| **Glitch Resistance Standard** | Glitch-safe double evaluation macros (`GLITCH_SAFE_VERIFY`) |

---

## Mentor's Note for Implementing Engineers

> *"Building post-quantum security into embedded bootloaders is not merely about swapping cryptographic primitive calls. It requires holistic systems engineering—balancing severe RAM/ROM constraints against physical fault injection vectors, hardware eFuse limitations, and lifecycle operations. Ensure every verification step is verified twice, every memory buffer is zeroized upon exit, and dynamic memory allocation remains strictly out of your boot code."*  
> — **Dr. Q-Boot**
