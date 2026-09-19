# Specification 05: End-to-End Key Lifecycle Management & Offline Signing Ceremonies

## 1. Lifecycle Overview & Cryptographic States

Key Lifecycle Management encompasses the complete operational life of post-quantum public/private key pairs—from initial hardware entropy generation to eventual retirement or emergency field revocation.

```
  +-----------------------+
  |  1. KEY GENERATION    |  (Air-Gapped HSM / TRNG / Dual Control)
  +-----------+-----------+
              |
              v
  +-----------------------+
  |  2. PROVISIONING      |  (Factory Line OTP/eFuse Burning & Locking)
  +-----------+-----------+
              |
              v
  +-----------------------+
  |  3. ACTIVE OPERATION  |  (Offline Signing Ceremonies & Firmware Verification)
  +-----------+-----------+
              |
      +-------+-------+
      |               |
      v               v
+-----------+   +-----------+
| 4. FIELD  |   | 5. RETIRE-|
| REVOCATION|   |    MENT   | (eFuse Bit Blowing & Key Expiry)
+-----------+   +-----------+
```

---

## 2. Key Pair Generation Protocols

### 2.1 Random Number Generation Standards
All PQC key generation seeds MUST be sourced from a physical True Random Number Generator (TRNG) compliant with **NIST SP 800-90A/B/C** and certified to **FIPS 140-3 Level 3** hardware security standards:
- **Entropy Source**: Continuous health testing (Repetition Count Test and Adaptive Proportion Test) running on hardware TRNG noise blocks.
- **Deterministic Random Bit Generator (DRBG)**: HMAC-SHA256 DRBG re-seeded with 256 bits of true physical entropy every 1,000 requests.

### 2.2 Key Storage Classification
- **Primary Root Private Key**: Stored exclusively inside air-gapped FIPS 140-3 Level 4 Hardware Security Modules (HSMs). The private key MUST NEVER leave the HSM boundary in plaintext.
- **LMS Private Key State Tracking**: If LMS/XMSS stateful signatures are generated, the HSM MUST enforce atomic incrementing of non-volatile monotonic state counters to prevent leaf index reuse.

---

## 3. Offline Signing Ceremony Protocol

To maintain the absolute integrity of the Primary Root of Trust, firmware image signing is performed exclusively within a formal, air-gapped **Key Signing Ceremony**.

```
+-----------------------------------------------------------------------------------+
| AIR-GAPPED KEY SIGNING CEREMONY ENVIRONMENT                                       |
+-----------------------------------------------------------------------------------+
|  [ Ceremony Master ]   [ Crypto Officer 1 ]   [ Crypto Officer 2 ]  [ Auditor ]   |
+-----------------------------------------------------------------------------------+
                                         |
                       Authenticates via Smartcard (2-of-3)
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| AIR-GAPPED SIGNING WORKSTATION & HSM (FIPS 140-3 Level 4)                         |
|  1. Read Firmware Payload Hash from Read-Only Optical / USB Media                 |
|  2. Compute ML-DSA-44 Signature inside HSM Boundary                               |
|  3. Inject Signature & Public Key into Firmware Header Structure                  |
|  4. Export Signed Firmware Image to Output Media                                  |
+-----------------------------------------------------------------------------------+
```

### 3.1 Ceremony Roles & Split-Knowledge (M-of-N Control)
- **Ceremony Master (CM)**: Coordinates the ceremony, logs event timestamps, and directs protocol execution.
- **Crypto Officers (CO1, CO2, CO3)**: Custodians of HSM smartcard key shares. A minimum threshold of **2-of-3 Crypto Officers** must present physical smartcards and PINs to activate the signing HSM.
- **Independent Auditor (IA)**: Verifies compliance with the Ceremony Script and signs the audit attestation log.

### 3.2 Step-by-Step Signing Workflow
1. **Payload Extraction**: The release engineering team builds the production binary and generates a SHA-256 digest $\text{H}_{\text{fw}}$. The digest is transferred to read-only write-once optical media (CD-R) or a hardware-write-protected USB drive.
2. **Environment Audit**: The Auditor verifies that the signing workstation has no network connectivity (Wi-Fi, Bluetooth, Ethernet disabled) and that memory isolation controls are active.
3. **HSM Activation**: CO1 and CO2 insert their smartcards and enter PINs to unlock the ML-DSA-44 signing key inside the HSM.
4. **Signature Generation**: The HSM receives $\text{H}_{\text{fw}}$, appends the header fields, computes the PQC signature $\sigma_{\text{pqc}}$, and formats the 256-byte `pqc_boot_header_t`.
5. **Verification & Audit**: The workstation runs an independent verification tool on the newly signed image using the public key. Once verified, the signed binary is exported and the HSM key session is cleared.

---

## 4. Root of Trust Provisioning Protocol (Factory Line)

During high-volume manufacturing (HVM), the device eFuse array must be securely provisioned with the Root Public Key Hash (PKH).

```
+-----------------------------------------------------------------------------------+
| FACTORY LINE PROVISIONING FLOW                                                    |
+-----------------------------------------------------------------------------------+
  [ STEP 1: CHIP UNBLOWN BLANK eFUSE CHECK ]
                 |
                 v
  [ STEP 2: INJECT 32-BYTE SHA-256 PKH INTO eFUSE REGISTER 0x000 ]
                 |
                 v
  [ STEP 3: READ-BACK VERIFICATION & HASH MATCH CHECK ]
                 |
                 v
  [ STEP 4: APPLY HIGH-VOLTAGE VPP PULSE TO BURN "PKH_LOCKED" BIT ]
                 |
                 v
  [ STEP 5: BURN "JTAG_DISABLE" & "SECURE_BOOT_EN" HARDWARE BITS ]
```

1. **Blank State Check**: Tester reads eFuse registers `0x000` to `0x01F` to confirm all bits are unprogrammed (`0x00`).
2. **PKH Ingestion**: Tester writes the 32-byte SHA-256 digest of the Primary Root Public Key to register `0x000`.
3. **Readback Validation**: Tester performs a readback check to verify the written values match the expected PKH.
4. **Lock Fuse Blowing**: Tester triggers programming voltage $V_{PP}$ to set `PKH_LOCKED` (Bit 2 of Security Register `0x048`), permanently preventing write access to the PKH slot.
5. **Security Hardening**: Tester burns `JTAG_DISABLE` (Bit 0) and `SECURE_BOOT_EN` (Bit 1) eFuses to enforce locked secure execution.

---

## 5. Field Key Revocation & Firmware Anti-Rollback

### 5.1 Revocation Procedure
If a secondary signing key is compromised or a severe vulnerability is identified in an active firmware release:
1. **Revocation Manifest Generation**: The primary Root CA issues a signed **Revocation Manifest** containing:
   - Target Key Index to be revoked.
   - New minimum security version counter.
   - Primary Root Signature.
2. **eFuse Bit Vector Update**: Upon ingesting the signed update package, Stage 0 / Stage 1 bootloader verifies the Primary Root Signature, then burns the corresponding revocation bit in eFuse offset `0x040`.

### 5.2 Anti-Rollback Counter Enforcement
Anti-rollback protection prevents adversaries from reflashing old, vulnerable firmware binaries that carry valid historical signatures.

```
       eFuse Monotonic Counter Bank (Offset 0x044 - 32-Bit Vector)
       +---+---+---+---+---+---+---+---+---------------------------+
       | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | ...                       |
       +---+---+---+---+---+---+---+---+---------------------------+
         Current Version = 4 (4 Bits Burned)

   Attempting Flash Update:
   - Header Version = 3  ---> REJECTED (3 < 4, Rollback Attack)
   - Header Version = 4  ---> ACCEPTED (4 == 4, Standard Boot)
   - Header Version = 5  ---> ACCEPTED & UPDATE eFUSE (5 > 4, Burn Bit 5)
```

---

## 6. Emergency Incident Response Plan for PQC Vulnerabilities

In the event of a theoretical or cryptanalytic breakthrough against a PQC scheme (e.g., side-channel attack on ML-DSA lattice reductions or structural vulnerability discovery):

### 6.1 Algorithm Agility Response Matrix

| Vulnerability Severity | Trigger Condition | Architectural Action |
| :--- | :--- | :--- |
| **LOW** | Minor side-channel leak in specific implementation. | Issue firmware update with constant-time mask patches under existing ML-DSA key. |
| **MEDIUM** | Weak parameter set discovered in ML-DSA-44. | Upgrade bootloader configuration to require **ML-DSA-65** (`sig_alg_id = 0x11`) via signed Key Manifest update. |
| **HIGH / CRITICAL** | Fundamental mathematical breakdown of M-LWE lattice problem. | Activate **Dual-Algorithm Fallback**: Bootloader switches signature algorithm field `sig_alg_id` to **LMS (RFC 8554)** hash-based signatures, completely bypassing lattice math. |

### 6.2 Dual-Header Hybrid Verification Mode
To support seamless emergency migration, the bootloader image structure supports a **Hybrid Header Mode** where the binary contains both an ML-DSA-44 signature and an LMS signature. Stage 0 ROM can be configured via eFuse security flag `0x048` Bit 7 (`HYBRID_STRICT_EN`) to require **both signatures to pass** before granting boot execution rights.
