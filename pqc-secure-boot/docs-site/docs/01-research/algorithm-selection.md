# Algorithm Selection & Trade-Off Matrix for Embedded Bootloaders

## Overview

Selecting a Post-Quantum Cryptography (PQC) signature algorithm for secure boot requires balancing tight embedded constraints:
- **eFuse / OTP storage** for public key hash.
- **Stage-1 SRAM size** for signature buffer and workspace memory.
- **Boot speed budgets** (e.g., automotive deadline `< 50 ms`).
- **Security category** (NIST Category 1 to 5).

---

## Comparative Selection Matrix

| Algorithm | NIST Standard | Public Key Size | Signature Size | Verification Time | Stack RAM Peak | Best Use Case |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **LMS** | RFC 8554 / SP 800-208 | 60 B | 1,180 B | 0.18 ms | 2.4 KB | Stage-0 ROM / Extreme SRAM constraint |
| **ML-DSA-44** | FIPS 204 | 1,312 B | 2,420 B | 0.45 ms | 8.2 KB | Balanced general embedded bootloader |
| **ML-DSA-87** | FIPS 204 | 2,592 B | 4,627 B | 0.92 ms | 14.8 KB | High-security mission-critical targets |
| **SLH-DSA-128f** | FIPS 205 | 32 B | 17,088 B | 12.40 ms | 4.1 KB | Systems with ultra-tiny eFuse key storage |

---

## Trade-off Analysis & Recommendation

1. **For Bare-Metal Microcontrollers (SRAM < 16 KB)**:
   - **Recommended Choice**: **LMS** (or XMSS).
   - **Rationale**: Minimal RAM impact, fast verification, tiny public key digest stored in OTP eFuse.

2. **For High-Performance Bootloaders (Cortex-A / RISC-V 64-bit with SRAM > 64 KB)**:
   - **Recommended Choice**: **ML-DSA-44** or **ML-DSA-65**.
   - **Rationale**: Sub-millisecond verification time using Number Theoretic Transform (NTT), reasonable signature footprint, no state management during signing.

3. **For eFuse-Constrained Hardware**:
   - **Recommended Choice**: **SLH-DSA**.
   - **Rationale**: Public key is only 32 bytes, requiring minimal OTP hardware overhead, though signature bus transfer time must be budgeted.
