# Post-Quantum Cryptography (PQC) Secure Bootloaders

[![GitHub Pages Deployment](https://img.shields.io/badge/Docs-GitHub%20Pages-blue?logo=github)](https://kiruthik-prakash-j.github.io/pqc-boot/)
[![Security Status](https://img.shields.io/badge/Security-Post--Quantum%20Resistant-brightgreen.svg)](#)
[![Memory Safety](https://img.shields.io/badge/Memory-100%25%20Zero--Malloc-blue.svg)](#)
[![E2E Test Suite](https://img.shields.io/badge/Tests-23%2F23%20Passed-success.svg)](#)

A comprehensive implementation, hardware emulation (QEMU), multi-agent peer audit, and institutional documentation repository for **Post-Quantum Cryptography (PQC) Secure Bootloaders** spanning three computing paradigms:

1. **IoT & Microcontrollers (ARM Cortex-M4)**: MCUboot bootloader with PQC TLV tags.
2. **Embedded Linux (RISC-V 64 / ARM)**: Das U-Boot FIT Image bootloader with `algo = "sha256,ml-dsa-44"` device tree signatures.
3. **Enterprise & Server Platforms (ARM Cortex-A 4-Core SMP)**: EDKII / UEFI SecurityPkg PE/COFF image verification via PKCS#7 OID extensions.

---

## 🌐 Live Documentation & Verification Playgrounds

The project documentation is deployed as a static site via GitHub Pages:
**[https://kiruthik-prakash-j.github.io/pqc-boot/](https://kiruthik-prakash-j.github.io/pqc-boot/)**

---

## 🚀 Quick Start & Verification

### 1. Build Reference C Engine & Run Tests
```bash
# Navigate to firmware directory
cd pqc-secure-boot

# Build C Reference Host Executable
cmake -B firmware/build -S firmware
cmake --build firmware/build

# Execute Complete E2E & Platform Test Suite (23 / 23 Tests)
python3 tests/run_e2e_tests.py
python3 tests/test_uboot_pqc_fit.py
python3 tests/test_uefi_pqc_securitypkg.py
```

### 2. Run Hardware QEMU Emulators
```bash
# 1. MCUboot on ARM Cortex-M4 (mps2-an386)
./firmware/platform/arm-cortex-m/run_qemu_cortex_m4.sh

# 2. U-Boot FIT on RISC-V 64 (virt)
qemu-system-riscv64 -M virt -cpu rv64 -m 256M -nographic -bios none

# 3. EDKII / UEFI on ARM Cortex-A57 4-Core SMP (virt)
./firmware/platform/arm-cortex-a/run_qemu_cortex_a57_smp.sh
```

---

## 📂 Repository Architecture

```text
pqc-boot/
├── .github/workflows/          # GitHub Actions CI/CD (GitHub Pages auto-deploy)
├── pqc-secure-boot/            # Core PQC Secure Boot Implementation
│   ├── firmware/               # Bare-metal C PQC reference engine & platform linkers
│   ├── real_world/             # Real-World Bootloader Target Integrations
│   │   ├── mcuboot/            # MCUboot IoT PQC implementation & imgtool signing
│   │   ├── uboot/              # U-Boot FIT PQC implementation & mkimage integration
│   │   └── edk2/               # EDKII UEFI SecurityPkg PQC implementation & OIDs
│   ├── tests/                  # 4-Tier Automated Test Harness Array (23 / 23 Tests)
│   ├── docs-site/              # Docusaurus documentation web application (React Playgrounds)
│   ├── architecture/           # Formal threat modeling and trade-off matrices
│   └── .agents/                # Multi-agent audit reports and verification logs
└── submission-docs/            # Academic Submission Deliverables
    └── midsem-report/          # Mid-semester report (Markdown, DOCX, and PDF)
```

---

## 🔒 Supported Cryptographic Algorithms

- **ML-DSA-44 (NIST FIPS 204)**: Primary general-purpose lattice-based scheme (1,312B PK, 2,420B Sig).
- **SPHINCS+ / SLH-DSA (NIST FIPS 205)**: Conservative stateless hash-based scheme (32B PK, 7,856B Sig).
- **LMS / LMOTS (RFC 8554 / RFC 8708)**: Stateful hash-based scheme for low-RAM IoT chips (56B PK, 2,800B Sig).

---

## 📜 License & Academic Affiliation
M.Tech Dissertation Project, BITS Pilani (ESZG628T).
All source code licensed under the Apache-2.0 License.
