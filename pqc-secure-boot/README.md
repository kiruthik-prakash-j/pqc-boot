# Post-Quantum Cryptography (PQC) Secure Boot Infrastructure

[![PQC Security Status](https://img.shields.io/badge/Security-Post--Quantum%20Resistant-brightgreen.svg)](#)
[![Zero Malloc](https://img.shields.io/badge/Memory-100%25%20Zero--Malloc-blue.svg)](#)
[![E2E Test Suite](https://img.shields.io/badge/Tests-23%2F23%20Passed-success.svg)](#)
[![Documentation](https://img.shields.io/badge/Docs-Docusaurus%20v3-purple.svg)](http://localhost:3000)

Comprehensive implementation, hardware emulation (QEMU), multi-agent peer audit, and institutional documentation for **Post-Quantum Cryptography (PQC) Secure Bootloaders** spanning three computing paradigms:

1. **IoT & Microcontrollers (ARM Cortex-M4)**: MCUboot bootloader with PQC TLV tags.
2. **Embedded Linux (RISC-V 64 / ARM)**: U-Boot FIT Image bootloader with `algo = "sha256,ml-dsa-44"` device tree signatures.
3. **Server & Enterprise Platforms (ARM Cortex-A 4-Core SMP)**: EDKII / UEFI SecurityPkg PE/COFF image verification via PKCS#7 OID extensions.

---

## Quick Start & Verification

### 1. Build Reference C Engine & Run Tests
```bash
# Navigate to workspace root
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

### 3. Launch Documentation Web Application
```bash
cd docs-site
npm run start -- --port 3000 --host 0.0.0.0
# Access site at http://localhost:3000
```

---

## Directory Architecture

```text
pqc-secure-boot/
├── firmware/                   # Bare-metal C/C++ PQC reference engine & platform startup
│   ├── src/                    # ML-DSA-44, SPHINCS+, LMS, SHA-256, SHAKE-256 engines
│   ├── include/                # Static header definitions and PQC structures
│   ├── platform/               # ARM Cortex-M, RISC-V, ARM Cortex-A QEMU scripts & linkers
│   └── CMakeLists.txt          # Firmware build system
├── real_world/                 # Real-World Bootloader Target Integrations
│   ├── mcuboot/                # MCUboot IoT PQC implementation & imgtool signing
│   ├── uboot/                  # U-Boot FIT PQC implementation & mkimage integration
│   └── edk2/                   # EDKII UEFI SecurityPkg PQC implementation & OIDs
├── tests/                      # 4-Tier Automated Test Harness Array (23 / 23 Tests)
├── docs-site/                  # Docusaurus documentation web application (React Playgrounds)
├── architecture/               # Formal threat modeling and trade-off matrices
└── .agents/                    # Multi-agent audit reports and persistent logs
```

---

## Supported Cryptographic Schemes

1. **ML-DSA-44 (NIST FIPS 204)**: Primary general-purpose lattice-based scheme (1,312B PK, 2,420B Sig).
2. **SPHINCS+ / SLH-DSA (NIST FIPS 205)**: Conservative stateless hash-based scheme (32B PK, 7,856B Sig).
3. **LMS / LMOTS (RFC 8554 / RFC 8708)**: Stateful hash-based scheme for low-RAM IoT chips (56B PK, 2,800B Sig).

---

## Verification & Audit Reports
Read the detailed peer-review audit reports compiled by 5 specialized subagents in [.agents/reports/](.agents/reports/):
- [SECURITY_REVIEW_REPORT.md](.agents/reports/SECURITY_REVIEW_REPORT.md)
- [EMBEDDED_ENGINEERING_REPORT.md](.agents/reports/EMBEDDED_ENGINEERING_REPORT.md)
- [SQA_PERFORMANCE_REPORT.md](.agents/reports/SQA_PERFORMANCE_REPORT.md)
- [SYSTEM_ENGINEERING_REPORT.md](.agents/reports/SYSTEM_ENGINEERING_REPORT.md)
- [TEST_ENGINEER_REPORT.md](.agents/reports/TEST_ENGINEER_REPORT.md)
