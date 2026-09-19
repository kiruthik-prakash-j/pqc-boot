# PQC Standards: NIST FIPS 204, FIPS 205, and RFC 8554

## Overview

The migration to post-quantum cryptography is governed by standards established by NIST (National Institute of Standards and Technology), the IETF (Internet Engineering Task Force), and national security agencies (e.g., NSA CNSA 2.0).

---

## 1. NIST FIPS 204: Module-Lattice Digital Signature Algorithm (ML-DSA)

NIST FIPS 204 specifies ML-DSA (derived from CRYSTALS-Dilithium), a lattice-based digital signature scheme.

### Key Characteristics
- **Hardness Assumption**: Module Learning With Errors (M-LWE) and Module Short Integer Solution (M-SIS).
- **Primary Strengths**: Fast key generation and verification, moderate signature size (2.4 KB to 4.6 KB).
- **Parameters**:
  - `ML-DSA-44`: Category 2 security (128-bit quantum). Public key: 1,312 B, Signature: 2,420 B.
  - `ML-DSA-65`: Category 3 security (192-bit quantum). Public key: 1,952 B, Signature: 3,309 B.
  - `ML-DSA-87`: Category 5 security (256-bit quantum). Public key: 2,592 B, Signature: 4,627 B.

---

## 2. NIST FIPS 205: Stateless Hash-Based Digital Signature Algorithm (SLH-DSA)

NIST FIPS 205 specifies SLH-DSA (derived from SPHINCS+), a stateless hash-based signature scheme.

### Key Characteristics
- **Hardness Assumption**: Security of underlying cryptographic hash functions (SHA-256 or SHAKE256).
- **Primary Strengths**: Ultra-compact public key (32 bytes), zero secret state management.
- **Trade-off**: Large signature sizes (7.8 KB to 49 KB) and higher verification latency.
- **Variants**:
  - `SLH-DSA-SHA2-128f`: Fast variant, 32 B public key, 17,088 B signature.
  - `SLH-DSA-SHA2-128s`: Small variant, 32 B public key, 7,856 B signature.

---

## 3. RFC 8554 & NIST SP 800-208: Leighton-Micali Signatures (LMS)

RFC 8554 and NIST SP 800-208 govern stateful hash-based digital signatures, specifically LMS and HSS (Hierarchical Signature Scheme).

### Key Characteristics
- **Hardness Assumption**: Hash function collision/preimage resistance.
- **Primary Strengths**: Minimal verification latency, small signature size (1.2 KB), tiny public key (32–60 B).
- **State Management**: Requires strict state tracking for signing; **verifiers (bootloaders) operate read-only and stateless**.
- **Mandate**: Recommended by NSA CNSA 2.0 for firmware and software signing.
