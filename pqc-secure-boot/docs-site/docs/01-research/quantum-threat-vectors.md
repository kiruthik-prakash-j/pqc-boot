# Quantum Threat Vectors in Embedded Firmware

## Overview

Classical secure boot architectures rely heavily on asymmetric public-key cryptography—specifically RSA-2048, RSA-3072, and ECDSA (P-256 / Ed25519)—to verify digital signatures on bootloader and kernel binaries. The security of these algorithms depends on mathematical problems (Integer Factorization and Discrete Logarithms) that are computationally infeasible for classical hardware.

However, quantum computing advances introduce critical threat vectors that dismantle these fundamental security assumptions.

---

## 1. Shor's Algorithm and Asymmetric Crypto Collapse

Peter Shor's quantum algorithm (1994) solves both the Integer Factorization Problem (IFP) and the Elliptic Curve Discrete Logarithm Problem (ECDLP) in polynomial time:

- **RSA-2048**: Classical work factor ~ `2^112` operations -> Quantum complexity `O((log N)^3)` polynomial operations.
- **ECDSA P-256**: Classical work factor ~ `2^128` operations -> Quantum complexity `O((log n)^3)` polynomial operations.

A Cryptographically Relevant Quantum Computer (CRQC) with approximately 1,500 to 4,000 logical qubits can derive private signing keys from embedded public keys in hours.

---

## 2. Secure Boot Threat Scenario: Signature Forgery

Unlike confidentiality threats (where data can be decrypted retroactively), the threat to secure boot is **instantaneous signature forgery**:

```
[Adversary Intercepts Binary] ---> [CRQC Derives Vendor Private Key]
                                                |
                                                v
[Device Accepts Rogue Firmware] <--- [Adversary Forges PQC Manifest]
```

1. **Key Extraction**: The adversary reads the public key embedded in device Flash or OTP eFuse.
2. **Private Key Derivation**: Running Shor's algorithm on a CRQC extracts the secret key `d` (RSA) or `k` (ECDSA).
3. **Malicious Payload Signing**: The adversary packages malicious firmware (rootkit, persistent bootkit, disable safety checks) and signs it using the derived key.
4. **Permanent Subversion**: Target embedded hardware accepts the rogue binary as authentic, defeating the Chain of Trust.

---

## 3. Vulnerable Embedded Domains

Embedded devices have extended lifespans (10–30 years) and limited over-the-air (OTA) update capability:

- **Automotive ECUs**: ISO 26262 compliant controllers controlling steering, braking, and powertrains.
- **Industrial Control Systems (SCADA)**: Energy grid infrastructure, water distribution PLCs.
- **Aerospace & Defense**: Avionics, flight computers, military radios.
- **Medical Devices**: Pacemakers, infusion pumps, surgical robotics.

Devices deployed today without PQC-ready bootloaders will remain vulnerable to CRQC attacks during their active operational life.
