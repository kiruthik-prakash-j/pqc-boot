---
id: secure-boot-threat-model
title: "Institutional Guide: Secure Boot Threat Model & Root of Trust"
sidebar_label: "Threat Model & RoT"
---

# Institutional Guide: Secure Boot Threat Model & Root of Trust

This document defines the security architecture, threat boundaries, and trust anchors for **Post-Quantum Secure Boot systems**.

---

## 1. Secure Boot Trust Chain

```mermaid
sequenceDiagram
    autonumber
    participant ROM as Stage 0 Mask ROM (Hardware RoT)
    participant BL as Stage 1 Bootloader (MCUboot / U-Boot / UEFI)
    participant OS as Stage 2 Operating System (Linux Kernel)

    ROM->>ROM: Read immutable Root-of-Trust Public Key Hash (eFuse)
    ROM->>BL: Verify Stage 1 PQC Signature (ML-DSA-44)
    alt Stage 1 Valid
        ROM->>BL: Execution Transfer to Bootloader
        BL->>BL: Read Authenticated Key Store (db / FIT keys)
        BL->>OS: Verify OS Kernel Image PQC Signature
        alt Stage 2 Valid
            BL->>OS: Execution Transfer to OS Kernel
        else Stage 2 Invalid
            BL->>BL: Halt Execution & Trigger Emergency Recovery
        end
    else Stage 1 Invalid
        ROM->>ROM: Halt CPU Core & Lock Buses
    end
```

---

## 2. Threat Vector & Mitigation Matrix

| Threat Vector | Attack Mechanism | Countermeasure in `pqc-boot` |
| :--- | :--- | :--- |
| **Quantum Forgery** | Attackers compute classic RSA/ECC private keys using quantum hardware. | Use NIST FIPS 204 ML-DSA-44 / FIPS 205 SPHINCS+ / RFC 8554 LMS signatures. |
| **Payload Tampering** | Altering 1 bit of image binary in Flash/RAM. | SHA-256 pre-hash verification & PQC signature verification failure triggers secure boot halt. |
| **Public Key Substitution** | Attacker replaces public key in image header with their own key. | Bootloader computes `SHA256(PK)` and compares against hardware eFuse / BSS Root-of-Trust key hash. |
| **Rollback Attack** | Flashing an older, vulnerable (yet validly signed) firmware version. | Monotonic anti-rollback counters (`header_version` / security counters). |
| **Buffer Overflow** | Exploiting `malloc` heap fragmentation or dynamic memory bounds. | **Strict 100% Zero-Malloc Policy**: All memory allocated on static stack or `.bss`. |
