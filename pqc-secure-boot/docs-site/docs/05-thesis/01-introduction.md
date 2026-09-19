# Chapter 1: Introduction and Problem Statement

## 1.1 Executive Summary and Thesis Scope

Secure boot represents the foundational bedrock of modern embedded system security. By enforcing a cryptographic Chain of Trust (CoT) starting from an immutable Hardware Root of Trust (RoT), secure boot ensures that an embedded device executes only authenticated, untampered firmware images during system initialization. For decades, this trust architecture has relied upon classical public-key cryptography—specifically RSA (RSA-2048, RSA-3072) and Elliptic Curve Cryptography (ECDSA P-256, Ed25519)—to verify digital signatures on bootloader and kernel binaries prior to execution.

However, the advent of quantum computing poses an existential threat to classical asymmetric cryptographic primitives. Shor's algorithm, executing on a cryptographically relevant quantum computer (CRQC), solves both the Integer Factorization Problem (IFP) and the Elliptic Curve Discrete Logarithm Problem (ECDLP) in polynomial time. Consequently, adversary access to a CRQC will enable arbitrary signature forgery, completely compromising the secure boot pipeline and allowing unauthorized firmware flashing, persistent rootkits, and total hardware subversion.

This thesis investigates the design, implementation, performance, and architectural trade-offs of transitioning secure bootloaders to Post-Quantum Cryptography (PQC). We evaluate stateful hash-based signatures (LMS/XMSS), lattice-based signatures (ML-DSA / CRYSTALS-Dilithium), and stateless hash-based signatures (SLH-DSA / SPHINCS+) within bare-metal, resource-constrained boot environments across RISC-V and ARM architectures.

---

## 1.2 Fundamentals of Secure Boot and the Chain of Trust

### 1.2.1 The Chain of Trust (CoT) Architecture

Secure boot establishes security through an unbroken chain of cryptographic verifications executed sequentially during system power-on. Each stage in the boot sequence measures (hashes) and authenticates (verifies the digital signature of) the subsequent stage before transferring execution control.

```
+------------------+       Verifies      +------------------+       Verifies      +------------------+
| Stage-0 Boot ROM | -----------------> | Stage-1 Bootloader| -----------------> |  Stage-2 Kernel  |
| (Immutable RoT)  |                     |   (SRAM / Flash) |                     |  (DRAM Execution)|
+------------------+                     +------------------+                     +------------------+
         |                                        |                                        |
    Reads PK Digest                          Reads Manifest                           Executes Main OS
    from OTP/eFuse                           from Storage
```

1. **Stage-0 Boot ROM (Hardware Root of Trust)**: Immutable read-only memory mask programmed during chip fabrication. Contains the initial execution code and the fundamental verification engine. The public key (or a cryptographic hash of the public key) is stored in One-Time Programmable (OTP) eFuse memory.
2. **Stage-1 Bootloader**: Stored in non-volatile flash memory. Loaded into internal Static RAM (SRAM) by Stage-0 after successful cryptographic verification. Responsible for basic hardware initialization (clocks, DRAM controllers, buses).
3. **Stage-2 Bootloader / Kernel**: Loaded into system DRAM by Stage-1 following verification. Includes operating system kernels (e.g., Linux, Zephyr, FreeRTOS) and application payloads.

### 1.2.2 Cryptographic Verification Pipeline

During boot, the execution target binary is formatted within a signed firmware manifest. The manifest contains:
- Image header (magic bytes, version counter, load address, entry point).
- Cryptographic hash (digest) of the binary payload (typically SHA-256 or SHA-512).
- Digital signature computed over the header and payload digest using the vendor's private signing key.
- Vendor public key or key certificate chain.

The bootloader computes the hash of the image, reconstructs the message digest, and verifies the signature using the hardware-anchored public key. If verification fails at any stage, the device halts execution, enters a secure recovery mode, or triggers a hardware reset to prevent compromised code execution.

---

## 1.3 The Quantum Threat to Classical Public-Key Cryptography

### 1.3.1 Mathematical Vulnerability of RSA and ECC

Classical signature algorithms derive their security from hard mathematical problems that are intractable for classical computers:
- **RSA**: Security relies on the hardness of factoring large composite integers `N = p * q`.
- **ECDSA / Ed25519**: Security relies on the Elliptic Curve Discrete Logarithm Problem (ECDLP)—given points `P` and `Q = [k]P` on an elliptic curve `E(F_q)`, finding the scalar `k`.

In 1994, Peter Shor formulated a quantum algorithm that solves both integer factorization and discrete logarithms in polynomial time on a quantum computer using quantum Fourier transforms.

#### Asymptotic Complexity Comparison

| Algorithm | Classical Hardness Assumption | Classical Best Complexity | Quantum Complexity (Shor's) |
| :--- | :--- | :--- | :--- |
| **RSA-2048** | Integer Factorization (IFP) | Sub-exponential (GNFS) | O((log N)^3) polynomial time |
| **RSA-3072** | Integer Factorization (IFP) | Sub-exponential (GNFS) | O((log N)^3) polynomial time |
| **ECDSA P-256**| Elliptic Curve Discrete Log (ECDLP) | O(2^128) (Pollard's rho) | O((log n)^3) polynomial time |
| **Ed25519** | Edwards Curve Discrete Log (ECDLP) | O(2^128) (Pollard's rho) | O((log n)^3) polynomial time |

#### Quantum Resource Requirements
Recent estimates in quantum cryptanalysis indicate that a CRQC equipped with approximately 2,000 to 4,000 logical (error-corrected) qubits could break RSA-2048 in hours. Breaking ECDSA P-256 requires roughly 1,500 to 2,300 logical qubits, as the quantum circuit for ECDLP on elliptic curves is even more efficient per key bit than integer factorization.

```
Classical Work Factor:   ECDSA P-256 ~ 2^128 operations (Intractable)
Quantum Work Factor:     ECDSA P-256 ~ O((256)^3) = ~1.6 * 10^7 quantum gates (Trivial)
```

---

## 1.4 Urgency and Architectural Challenges of PQC Transition in Firmware

### 1.4.1 Long-Lived Embedded Lifecycles

Unlike consumer web applications where TLS certificates and cryptographic ciphers can be updated dynamically over software layers, embedded hardware exhibits operational lifespans spanning 10 to 30 years. Key domains affected include:
- **Automotive Systems**: Electronic Control Units (ECUs) governed by ISO 26262 functional safety standards.
- **Aerospace and Defense**: Avionics controllers, satellite payloads, and tactical communication nodes.
- **Industrial Control Systems (ICS/SCADA)**: Energy grid infrastructure, water treatment, and manufacturing PLCs.
- **Medical Devices**: Implantable devices and diagnostic systems.

Devices deployed today will remain active well into the timeframe during which quantum computers are expected to reach cryptographically relevant thresholds.

### 1.4.2 The "Harvest/Store Now, Decrypt/Forge Later" Paradigm in Firmware

While confidentiality threats concern data interception today for decryption tomorrow, the threat to secure boot is immediate regarding **signature forgery**:
1. An adversary intercepts signed firmware binaries distributed over the air (OTA) or extracted from physical flash chips.
2. Once a CRQC becomes operational, the adversary computes the vendor's private key from the public key embedded in the firmware or device eFuses.
3. The adversary synthesizes malicious firmware updates signed with the derived private key.
4. The malicious binary passes classical verification on fielded devices, enabling global compromise of hardware fleets, physical bricking, or nation-state level infrastructure disruption.

### 1.4.3 Regulatory Mandates and Standardization

Recognizing this threat, international standards bodies and government organizations have issued strict transition timelines:

- **NIST PQC Standardization**:
  - **FIPS 204**: Module-Lattice-Based Digital Signature Standard (ML-DSA / CRYSTALS-Dilithium).
  - **FIPS 205**: Stateless Hash-Based Digital Signature Standard (SLH-DSA / SPHINCS+).
  - **FIPS 206**: FALCON (FN-DSA).
  - **NIST SP 800-208**: Recommendation for Stateful Hash-Based Signatures (LMS & XMSS).
- **NSA CNSA 2.0 (Commercial National Security Algorithm Suite 2.0)**:
  - Mandates stateful hash-based signatures (LMS/XMSS) for firmware and software signing immediately.
  - Mandates ML-DSA-87 / SLH-DSA-256 for general digital signatures by 2030.

---

## 1.5 Problem Statement and Research Objectives

### 1.5.1 Embedded Bootloader Constraints

Replacing RSA-2048 or ECDSA P-256 with PQC signature schemes introduces significant technical bottlenecks due to severe physical constraints in Stage-0 ROM and Stage-1 SRAM:

1. **Public Key and Signature Footprint Expansion**:
   - RSA-2048: Public key = 256 bytes, Signature = 256 bytes.
   - ECDSA P-256: Public key = 64 bytes, Signature = 64 bytes.
   - ML-DSA-65 (Lattice): Public key = 1,952 bytes (approx 30.5x), Signature = 3,309 bytes (approx 51.7x).
   - SLH-DSA-SHA2-128f (Stateless Hash): Public key = 32 bytes, Signature = 17,088 bytes (approx 267x).
2. **SRAM Buffer Boundaries**: Microcontrollers often possess only 16 KB to 64 KB of SRAM for Stage-1 execution. Storing large signature structures or intermediate polynomial vectors risks stack overflow and memory exhaustion.
3. **Execution Latency Budgets**: Industrial automotive boot sequences enforce strict real-time deadlines (e.g., boot completion within `< 50 ms`). Complex PQC operations (e.g., thousands of hash evaluations in SLH-DSA or rejection sampling loops in ML-DSA) must complete within allocated clock cycle budgets.
4. **Zero Dynamic Memory Allocation**: Secure boot environments strictly prohibit dynamic heap management (`malloc`/`free`, `new`/`delete`) to eliminate non-deterministic execution times, heap fragmentation, and memory corruption vulnerabilities.

### 1.5.2 Research Objectives

This thesis addresses these challenges by achieving the following objectives:
1. **Algorithmic Evaluation**: Provide a detailed comparative mathematical analysis of stateful hash-based (LMS/XMSS), lattice-based (ML-DSA), and stateless hash-based (SLH-DSA) algorithms focused on verification primitives.
2. **Hardware Root-of-Trust Integration**: Design an immutable Stage-0 secure boot architecture featuring Public Key Hashing (PKH) in eFuse to mitigate large public key storage requirements.
3. **Zero-Malloc Implementation**: Implement a deterministic C/C++ bare-metal secure bootloader engine with zero dynamic memory allocation.
4. **Cross-Platform Benchmarking**: Evaluate verification latency, CPU cycle count, peak RAM consumption (stack/BSS), and binary size across RISC-V (RV32/RV64), ARM Cortex-M3, and ARM Cortex-A targets.
5. **Architectural Guidelines**: Formulate definitive engineering trade-off matrices to guide industry selection of post-quantum signature schemes for embedded firmware authentication.
