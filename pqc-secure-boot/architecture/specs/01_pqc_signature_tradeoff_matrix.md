# Specification 01: Post-Quantum Signature Scheme Trade-Off Matrix & Analysis

## 1. Executive Summary & Design Rationale

Embedded secure bootloaders operate in severely constrained hardware environments characterized by limited Read-Only Memory (ROM), tightly coupled Static RAM (SRAM), fixed OTP/eFuse storage capacity, and strict boot latency budgets (typically < 100 ms). Transitioning secure boot architectures from classical public-key cryptography (RSA-2048/3072, ECDSA P-256/Ed25519) to Post-Quantum Cryptography (PQC) introduces significant resource trade-offs.

This specification provides a rigorous comparative evaluation of the leading PQC digital signature standards approved by NIST:
1. **Stateful Hash-Based Signatures**: Leighton-Micali Signature (LMS - RFC 8554 / NIST SP 800-208) and eXtended Merkle Signature Scheme (XMSS - RFC 8391 / NIST SP 800-208).
2. **Lattice-Based Signatures**: Module-Lattice-Based Digital Signature Algorithm (ML-DSA / Dilithium - NIST FIPS 204).
3. **Stateless Hash-Based Signatures**: Stateless Hash-Based Digital Signature Algorithm (SLH-DSA / SPHINCS+ - NIST FIPS 205).

The design rationale for embedded secure boot favors algorithms with minimal public key footprints (to fit into silicon eFuses), rapid verification speed, modest SRAM usage for signature context state, and small signature headers to minimize flash storage overhead.

---

## 2. PQC Signature Algorithm Trade-Off Matrix

The matrix below compares key cryptographic and performance metrics relevant to Cortex-M4 / RISC-V RV32IM class embedded bootloaders.

| Metric / Parameter | LMS (RFC 8554 / SP 800-208) | XMSS (RFC 8391 / SP 800-208) | ML-DSA-44 (FIPS 204 / Dilithium2) | ML-DSA-65 (FIPS 204 / Dilithium3) | SLH-DSA-SHA2-128f (FIPS 205) | SLH-DSA-SHAKE-128s (FIPS 205) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **NIST Security Category** | Level 1 - 5 (Param dependent) | Level 1 - 5 (Param dependent) | Category 2 (128-bit quantum) | Category 3 (192-bit quantum) | Category 1 (128-bit quantum) | Category 1 (128-bit quantum) |
| **Underlying Hard Problem** | Preimage / Collision resistance of Hash (SHA-256 / SHAKE256) | Preimage / Collision resistance of Hash (SHA-256 / SHAKE256) | Module Learning With Errors (M-LWE) & Module Short Integer Solution (M-SIS) | Module Learning With Errors (M-LWE) & Module Short Integer Solution (M-SIS) | Preimage / Second-Preimage resistance of Hash (SHA-256 / SHAKE256) | Preimage / Second-Preimage resistance of Hash (SHA-256 / SHAKE256) |
| **Public Key Size** | **56 bytes** (LMS_SHA256_M32_H10) | **64 bytes** (XMSS_SHA2_10_256) | **1,312 bytes** | **1,952 bytes** | **32 bytes** | **32 bytes** |
| **Signature Size** | **2,480 bytes** | **2,500 bytes** | **2,420 bytes** | **3,309 bytes** | **17,088 bytes** | **7,856 bytes** |
| **Private Key Size** | 48 - 64 bytes (Seed + State Index) | 64 - 132 bytes (Seed + Index) | 2,560 bytes | 4,032 bytes | 64 bytes | 64 bytes |
| **State Management Risk** | **CRITICAL (Stateful)** | **CRITICAL (Stateful)** | **Stateless (Zero Risk)** | **Stateless (Zero Risk)** | **Stateless (Zero Risk)** | **Stateless (Zero Risk)** |
| **Verification Speed (Cortex-M4)** | **~ 1.2M - 2.5M cycles** (~ 10-20 ms @ 120MHz) | **~ 1.5M - 3.0M cycles** (~ 12-25 ms @ 120MHz) | **~ 350K - 600K cycles** (~ 3-5 ms @ 120MHz) | **~ 550K - 900K cycles** (~ 5-8 ms @ 120MHz) | **~ 15M - 35M cycles** (~ 125-290 ms @ 120MHz) | **~ 45M - 90M cycles** (~ 375-750 ms @ 120MHz) |
| **Verification RAM Footprint** | **~ 1.2 KB** (Stack buffer for hash chains) | **~ 1.5 KB** (Stack buffer for Merkle tree) | **~ 8.5 KB** (Polynomial stack allocations) | **~ 12.8 KB** (Polynomial stack allocations) | **~ 2.5 KB** (FORS / Hypertree stack context) | **~ 2.2 KB** (FORS / Hypertree stack context) |
| **Key Generation Overhead** | Extremely High (Tree precomputation) | Extremely High (Tree precomputation) | Very Low (< 1 ms) | Very Low (< 1 ms) | Low (< 5 ms) | Low (< 5 ms) |
| **Signing Overhead** | Fast (State increment + WOTS+) | Fast (State increment + WOTS+) | Fast (~ 2M-5M cycles, probabilistic rejection) | Fast (~ 3M-8M cycles) | Slow (~ 50M-200M cycles) | Extremely Slow (~ 200M-800M cycles) |
| **Suitability for Bootloader RoT** | **EXCELLENT** (Small PK, fast verify, ideal for static firmware signing) | **EXCELLENT** (Small PK, fast verify, ideal for static firmware signing) | **VERY GOOD** (Ultra-fast verify, stateless, slightly larger PK) | **GOOD** (High security, moderate PK size) | **POOR** (Signature size & verification cycles exceed boot limits) | **POOR** (Extreme latency unacceptable for cold boot) |

---

## 3. Deep-Dive Comparative Dimension Analysis

### 3.1 Signature Size & Flash/ROM Overhead
- **Stateful Hash-Based (LMS / XMSS)**: Signature sizes range between 2.4 KB and 2.8 KB for $H=10$ or $H=15$ tree heights with Winternitz parameter $w=4$. This fits easily within standard firmware image headers (typically 4 KB header slot).
- **Lattice-Based (ML-DSA-44 / Dilithium2)**: Generates signatures of 2,420 bytes, virtually identical to LMS in size. Flash overhead is minimal (~ 2.4 KB header addition).
- **Stateless Hash-Based (SLH-DSA / SPHINCS+)**: Signature size is the primary bottleneck. The fastest variant (`128f`) produces signatures of **17,088 bytes**, requiring more than 16 KB of header space per signed partition. Even the small variant (`128s`) requires **7,856 bytes**, which severely bloats storage-constrained boot ROMs and flash flash sectors (e.g., 4 KB physical flash erase blocks).

### 3.2 Public Key Size & OTP/eFuse Provisioning
- **OTP / eFuse Constraints**: On-chip eFuse arrays on microcontrollers (e.g., STM32, ESP32, NXP LPC, RISC-V SoC) typically dedicate **256 bits (32 bytes)** to **512 bits (64 bytes)** for Root-of-Trust public key storage.
- **LMS / XMSS**: LMS public keys are **56 bytes** (4-byte type, 4-byte $I$, 16-byte $T[1]$, 32-byte hash seed/root). XMSS public keys are **64 bytes**. Either can be directly stored in an eFuse array or hashed down to a 256-bit SHA-256 digest (**32 bytes**) stored in eFuse.
- **ML-DSA-44**: Public key size is **1,312 bytes** (encoded polynomial vector $\mathbf{t}_1$ and seed $\rho$). It is impossible to program a 1.3 KB public key directly into hardware eFuses. Thus, secure boot architectures **must** store a 256-bit or 384-bit **Public Key Hash (PKH)** in eFuse, and embed the full ML-DSA public key inside the firmware header.
- **SLH-DSA**: Public keys are **32 bytes** (16-byte PK.seed + 16-byte PK.root), allowing direct 1:1 programming into eFuse without requiring a separate hash layer.

### 3.3 Private Key State Management Risks
- **Stateful Vulnerability (LMS / XMSS)**: LMS and XMSS rely on Winternitz One-Time Signatures (WOTS+). Each leaf in the Merkle tree **must never be used to sign more than one message**. If a private key state index is duplicated or rolled back (e.g., virtual machine snapshot restore, power loss during state update, HSM counter glitch), an attacker can combine signatures to synthesize forgeable private keys.
  - *Mitigation in Secure Boot*: For bootloader signing servers, state management MUST be enforced via hardware security modules (HSMs) with non-volatile monotonic counters. On the verification side (embedded target bootloader), statefulness poses zero risk because the bootloader *only verifies* signatures and never signs messages.
- **Stateless Immunity (ML-DSA / SLH-DSA)**: ML-DSA and SLH-DSA are purely stateless. Signing the same message twice or reusing seeds does not compromise key integrity.

### 3.4 Verification Execution Time (CPU Cycles)
- **ML-DSA (Dilithium)**: Offers the fastest verification performance among all PQC standards. Verification consists of computing the Number Theoretic Transform (NTT), matrix-vector multiplication $\mathbf{A}\mathbf{z} - c\mathbf{t}_1 \cdot 2^d$, inverse NTT, and coefficient norm check. On ARM Cortex-M4 @ 120 MHz, ML-DSA-44 verifies in **~350,000 cycles (~ 3 ms)**.
- **LMS / XMSS**: Verification requires executing $2^w$ hash evaluations per WOTS+ chain plus $H$ Merkle tree node hashes ($H \approx 10$ to $20$). On Cortex-M4, LMS verification completes in **~ 1.2M cycles (~ 10 ms)**.
- **SLH-DSA**: Verification requires evaluating thousands of hash chains across the FORS (Forest-of-Random-Subtrees) structure and multi-layer hypertree. Verification takes **15M - 45M cycles (125 ms - 375 ms)**, which severely degrades cold-boot startup times.

### 3.5 SRAM Footprint in Embedded Stage 0/1 Bootloaders
- **LMS / XMSS**: Requires only **~1.2 KB of SRAM** for hash state contexts and leaf computation buffers. Perfect for tight Stage 0 ROM environments with < 16 KB total SRAM.
- **ML-DSA-44**: Requires storing intermediate polynomial vectors ($\mathbf{z} \in \mathbb{Z}_q^4$, $\mathbf{h} \in \mathbb{Z}_q^4$, matrix $\mathbf{A} \in \mathbb{Z}_q^{4 \times 4}$). Standard unoptimized implementations require **8.5 KB - 12.8 KB of SRAM**. Streaming or in-place NTT execution can reduce this to **~ 4.5 KB SRAM**, but requires careful stack layout.
- **SLH-DSA**: Requires **~2.2 KB - 2.5 KB SRAM** for tree hash traversal buffers.

---

## 4. Architectural Recommendation & Crypto-Agility Strategy

### Primary Architecture Recommendation
1. **Root-of-Trust (RoT) Key Storage**: Program a 256-bit SHA-256 **Public Key Hash (PKH)** into OTP eFuse memory.
2. **Primary Algorithm for Production Firmware**: **ML-DSA-44 (FIPS 204)**.
   - *Rationale*: Delivers stateless security (eliminating signing state corruption risks), exceptionally fast verification (< 5 ms boot latency impact), and modest signature header size (2.4 KB).
3. **Secondary / Factory Provisioning Alternative**: **LMS (RFC 8554 / SP 800-208)** (Parameter `LMS_SHA256_M32_H10`, `LMOTS_SHA256_N32_W4`).
   - *Rationale*: Allows direct fallback if SRAM constraints prohibit the 8.5 KB stack requirement of ML-DSA-44 during ultra-constrained Stage 0 execution.

### Crypto-Agile Header Identifier Strategy
The bootloader image header includes an 8-bit `sig_alg_id` field to support seamless hybrid or agile algorithm switching without altering ROM code:
- `0x01`: LMS (RFC 8554, LMOTS_SHA256_N32_W4)
- `0x02`: XMSS (RFC 8391, XMSS_SHA2_10_256)
- `0x10`: ML-DSA-44 (FIPS 204)
- `0x11`: ML-DSA-65 (FIPS 204)
- `0x20`: SLH-DSA-SHA2-128f (FIPS 205)
