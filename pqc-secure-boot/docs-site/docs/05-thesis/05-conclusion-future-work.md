# Chapter 5: Conclusion and Future Work

## 5.1 Synthesis of Findings

This thesis has investigated the operational, cryptographic, and architectural implications of integrating Post-Quantum Cryptography (PQC) into resource-constrained secure boot environments. As cryptographically relevant quantum computers (CRQCs) threaten classical asymmetric algorithms (RSA, ECDSA, Ed25519), embedded devices with multi-decade operational lifespans require an immediate transition to quantum-resistant verification pipelines.

Our quantitative evaluation across ARM Cortex-M3, RISC-V (RV32IMAC / RV64GC), and ARM Cortex-A architectures yields four central findings:

1. **Stateful Hash Signatures (LMS/XMSS) Provide Superior Stage-0 ROM Performance**: LMS (SHA256_M32_H10) achieves the lowest verification latency (16.8 ms @ 25 MHz), smallest binary footprint (4.1 KB Flash), and minimal stack consumption (512 bytes). Because Stage-0 ROM operates strictly as a read-only verifier, statefulness risks are entirely confined to the OEM build infrastructure, making LMS the most efficient choice for immutable boot ROMs.
2. **Lattice-Based Signatures (ML-DSA-65) Deliver Optimal Application Agility**: For Stage-1 and Stage-2 bootloaders executing on application processors, ML-DSA-65 provides sub-millisecond verification (0.18 ms on Cortex-A53) and stateless signing operations, balancing signature size (3.3 KB) with reasonable SRAM requirements (12.24 KB).
3. **Public Key Hashing (PKH) Resolves eFuse Silicon Bottlenecks**: Compressing 1.9 KB to 2.5 KB post-quantum public keys into 32-byte SHA-256 digests in eFuse memory reduces hardware silicon overhead by up to 98.4% while maintaining full cryptographic trust.
4. **Zero-Malloc Determinism is Achievable**: By eliminating dynamic memory allocation and statically allocating verification context buffers, PQC verification engines eliminate heap fragmentation, non-deterministic execution times, and dynamic memory corruption attack vectors.

---

## 5.2 Stratified Deployment Recommendations

Based on empirical benchmarks and hardware memory profiles, we establish a stratified deployment framework for post-quantum secure boot implementation:

```
+-----------------------------------------------------------------------------------+
|                        STRATIFIED PQC DEPLOYMENT FRAMEWORK                        |
+------------------------------------+----------------------------------------------+
| Platform Class                     | Recommended PQC Primitive & Standard         |
+------------------------------------+----------------------------------------------+
| Ultra-Constrained Microcontrollers | Primary: LMS (SHA256_M32_H10) / NIST SP 800-208|
| (ARM Cortex-M0+/M3, RV32I)        | Secondary: XMSS (SHA2_10_256)                |
| SRAM < 32 KB, Flash < 256 KB       | Anchor: 32-Byte PKH Digest in OTP eFuse      |
+------------------------------------+----------------------------------------------+
| Application & Domain Processors    | Primary: ML-DSA-65 (FIPS 204)                |
| (ARM Cortex-A53/A72, RV64GC)       | Secondary: ML-DSA-87 (NIST Level 5)          |
| SRAM > 128 KB, High Frequency      | Anchor: 32-Byte PKH Digest in OTP eFuse      |
+------------------------------------+----------------------------------------------+
| Long-Lifecycle Mission-Critical    | Hybrid Scheme:                               |
| (Aerospace, Defense, Automotive)   | Dual Signature: RSA-3072 + ML-DSA-65         |
| High Assurance & Migration Window  | Fallback: LMS (SHA256_M32_H10)               |
+------------------------------------+----------------------------------------------+
```

---

## 5.3 Future Research Directions

### 5.3.1 Hybrid Classical + PQC Bootloaders

During the multi-year transition period mandated by standards bodies (e.g., NSA CNSA 2.0 timeline extending to 2033), embedded systems will deploy **hybrid dual-signature manifests**:

```
+-------------------------------------------------------------------------+
|                         HYBRID MANIFEST HEADER                          |
+-------------------+--------------------+--------------------------------+
| Manifest Metadata | Classical Sig      | Post-Quantum Sig               |
| (Version, Digest) | (RSA-3072 / ECDSA) | (ML-DSA-65 / LMS)              |
+-------------------+--------------------+--------------------------------+
```

Future research must investigate:
- **AND-Verification vs. OR-Verification Policies**: Evaluating security and performance trade-offs between requiring both signatures to pass versus allowing key fallback during algorithm deprecation.
- **Combined Manifest Parsers**: Designing space-efficient unified verification pipelines that re-use SHA-256 hash engines across both classical and post-quantum verification paths.

### 5.3.2 Hardware Accelerator Integration

While software implementations achieve acceptable speeds on high-frequency application cores, resource-constrained microcontrollers benefit dramatically from dedicated hardware acceleration:

1. **Hardware NTT Co-Processors**: Implementing dedicated vector multiplication units for polynomial arithmetic over `R_q = Z_q[X]/(X^n + 1)` to accelerate ML-DSA verification by 10x to 50x.
2. **Keccak / SHA-3 Hardware Engines**: Offloading SHAKE-128 / SHAKE-256 state evaluations in SLH-DSA and ML-DSA to dedicated crypto-accel IPs.
3. **PQC Root-of-Trust IP Cores**: Designing standalone post-quantum security enclaves (e.g., RISC-V OpenTitan extension) with integrated eFuse controllers and PQC signature verification hardware.

### 5.3.3 Side-Channel and Fault Injection Countermeasures

As post-quantum algorithms transition into production silicon, physical implementation attacks become the primary threat vector:

- **Fault Injection (FI) on Rejection Sampling**: In ML-DSA, disrupting the norm check (`||z||_inf < gamma1 - beta`) via precise voltage or laser glitches can force the verifier to accept invalid signatures.
- **Differential Power Analysis (DPA) on Hash Trees**: Extracting secret seeds in stateful hash signers during WOTS+ key generation.
- **Countermeasure Development**: Researching low-overhead algorithmic countermeasures, such as instruction duplication, constant-time NTT butterfly networks, and dual-rail logic trees for bootloader codebases.

### 5.3.4 Formal Verification of Zero-Malloc Bootloader Code Paths

To ensure absolute immunity from memory corruption and state machine bypass vulnerabilities:
- Applying formal methods (e.g., Frama-C, CBMC bounded model checking, or SeL4-style interactive theorem proving) to verify that Stage-0 ROM PQC verification code paths exhibit zero out-of-bounds array indexing, complete stack frame containment, and deterministic state transitions.

---

## 5.4 Thesis Conclusion

The transition to post-quantum cryptography in secure boot is not merely a theoretical exercise, but an urgent engineering imperative for modern embedded hardware. This thesis demonstrates that through Public Key Hashing, zero-malloc static memory architectures, and platform-tailored algorithm selection (LMS for Stage-0 ROM, ML-DSA-65 for Stage-1/Stage-2 bootloaders), post-quantum secure boot can be implemented efficiently without sacrificing hardware performance or system security.
