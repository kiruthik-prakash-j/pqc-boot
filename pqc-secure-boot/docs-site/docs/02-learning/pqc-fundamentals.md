# Post-Quantum Cryptography Fundamentals

## Introduction

Post-Quantum Cryptography (PQC) refers to cryptographic algorithms (usually public-key algorithms) that are thought to be secure against an attack by a quantum computer. Unlike classical algorithms like RSA and ECC, PQC algorithms are built on hard mathematical problems that cannot be efficiently solved by quantum algorithms such as Shor's or Grover's algorithms.

---

## Hard Mathematical Families in PQC

PQC digital signatures are categorized by their underlying hardness assumptions:

```
                      Post-Quantum Signature Families
                                   |
        +--------------------------+--------------------------+
        |                                                     |
  Lattice-Based                                          Hash-Based
 (M-LWE / M-SIS)                                  (Preimage / Collision)
        |                                                     |
   +----+----+                                           +----+----+
   |         |                                           |         |
ML-DSA     FALCON                                    Stateful   Stateless
(FIPS 204) (FIPS 206)                                 (LMS)    (SLH-DSA)
```

1. **Lattice-Based Cryptography**:
   - Security relies on the hardness of high-dimensional lattice problems (M-LWE, M-SIS).
   - Offers balanced key sizes and verification speeds.

2. **Hash-Based Cryptography**:
   - Security relies solely on the security of cryptographic hash functions (SHA-256, SHAKE256).
   - Considered the most conservative security model (no complex algebraic assumptions).

3. **Multivariate & Code-Based Cryptography**:
   - Used predominantly for Encryption/KEMs (e.g., Classic McEliece) or specialized signature schemes.

---

## Security Levels in NIST PQC Standardization

NIST defined five security levels corresponding to the difficulty of breaking symmetric ciphers:

- **Category 1**: Equivalent to breaking AES-128 (e.g., ML-DSA-44, SLH-DSA-128f).
- **Category 2**: Equivalent to breaking SHA-256 collision resistance.
- **Category 3**: Equivalent to breaking AES-192 (e.g., ML-DSA-65).
- **Category 5**: Equivalent to breaking AES-256 (e.g., ML-DSA-87, SLH-DSA-256f).
