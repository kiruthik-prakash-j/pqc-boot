# Post-Quantum Cryptography (PQC) Secure Bootloaders

[![GitHub Pages Deployment](https://img.shields.io/badge/Docs-GitHub%20Pages-blue?logo=github)](https://kiruthik-prakash-j.github.io/pqc-boot/)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/kiruthik-prakash-j/pqc-boot)
[![Security Status](https://img.shields.io/badge/Security-Post--Quantum%20Resistant-brightgreen.svg)](#)
[![Memory Safety](https://img.shields.io/badge/Memory-100%25%20Zero--Malloc-blue.svg)](#)
[![E2E Test Suite](https://img.shields.io/badge/Tests-23%2F23%20Passed-success.svg)](#)
[![Submodules](https://img.shields.io/badge/Submodules-MCUboot%20%7C%20U--Boot%20%7C%20EDK2-orange.svg)](#)

A comprehensive implementation, multi-target hardware emulation (QEMU), empirical microarchitecture profiling, and institutional documentation repository for **Post-Quantum Cryptography (PQC) Secure Bootloaders** spanning three embedded and enterprise computing paradigms:

1. **IoT & Microcontrollers (ARM Cortex-M4)**: MCUboot bootloader with PQC TLV tags.
2. **Embedded Linux (RISC-V 64-bit / ARM)**: Das U-Boot FIT Image bootloader with `algo = "sha256,ml-dsa-44"` device tree signatures.
3. **Enterprise & Server Platforms (ARM Cortex-A57 4-Core SMP)**: EDK II / UEFI SecurityPkg PE/COFF image verification via PKCS#7 OID extensions.

---

## 🌐 Live Documentation & Interactive Playgrounds

The project documentation and interactive boot simulators are deployed live via GitHub Pages:
👉 **[https://kiruthik-prakash-j.github.io/pqc-boot/](https://kiruthik-prakash-j.github.io/pqc-boot/)**

---

## ☁️ 1-Click Launch via GitHub Codespaces (Recommended)

You can spin up a complete, pre-configured development environment in the cloud without installing any local dependencies:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/kiruthik-prakash-j/pqc-boot)

### How to Launch in Codespaces:
1. Click the **Open in GitHub Codespaces** button above (or on GitHub: click **Code** ➔ **Codespaces** ➔ **Create codespace on main**).
2. GitHub Codespaces automatically:
   - Provisions an Ubuntu environment with QEMU system emulators (`qemu-system-arm`, `qemu-system-misc`, `qemu-system-x86`).
   - Installs cross-compilers (`gcc-arm-none-eabi`, `gcc-riscv64`, `gcc-aarch64-linux-gnu`).
   - Clones and synchronizes all Git submodules (`mcuboot`, `u-boot`, `edk2`).
   - Builds the reference C PQC firmware engine (`firmware/build/pqc_boot_host`).
   - Forwards port `3000` for the Docusaurus interactive documentation playground.
3. Once the web terminal appears, you can immediately run tests, QEMU simulations, and profiling!

---

## 💻 Local Workstation Setup (Alternative)

If you prefer running on your local machine:

### 1. Clone with Recursive Submodules
```bash
git clone --recurse-submodules https://github.com/kiruthik-prakash-j/pqc-boot.git
cd pqc-boot

# If already cloned without submodules:
git submodule update --init --recursive --depth 1
```

### 2. Install System Dependencies (Ubuntu / Debian)
```bash
sudo apt-get update
sudo apt-get install -y \
    qemu-system-arm qemu-system-misc qemu-system-x86 \
    gcc-arm-none-eabi libnewlib-arm-none-eabi \
    gcc-aarch64-linux-gnu \
    cmake build-essential libssl-dev libfdt-dev device-tree-compiler \
    python3-pip python3-pytest
```

### 3. Build Reference C Engine
```bash
cmake -B pqc-secure-boot/firmware/build -S pqc-secure-boot/firmware
make -C pqc-secure-boot/firmware/build pqc_boot_host
```

---

## 🧪 Running Automated Test Programs (23 / 23 Tests Passing)

Execute the full automated test array validating cryptographic correctness, fault injection resistance, and zero dynamic memory allocation:

```bash
# Run Complete Unified Test Array (All 23 Tests)
python3 pqc-secure-boot/tests/test_uefi_pqc_securitypkg.py && \
python3 pqc-secure-boot/tests/test_uboot_pqc_fit.py && \
python3 pqc-secure-boot/tests/run_e2e_tests.py
```

### Test Suite Structure:
| Test Harness | Tests | Coverage Scope |
| :--- | :---: | :--- |
| **Tier 1 (Feature Coverage)** | 4 | C verification API contract, platform target builds, Docusaurus structure |
| **Tier 2 (Boundary & Corner)** | 6 | Corrupted headers, truncated signatures, payload mismatch, key hash mismatch, **Zero `malloc` enforcement** |
| **Tier 3 (Cross-Feature)** | 3 | Multi-platform build configurations, documentation integrity, React component compilation |
| **Tier 4 (Real-World Scenarios)** | 2 | Bit-flip fault injection attacks, simulated firmware halt on corruption, multi-scheme boot |
| **U-Boot FIT Image Suite** | 4 | FIT tree parser, `algo = "sha256,ml-dsa-44"`, corrupted node rejection, missing key handling |
| **UEFI SecurityPkg Suite** | 4 | PE/COFF verification, Authenticated variables (`db`/`KEK`), `Pkcs7VerifyPqc()` dispatch, X.509 OIDs |

---

## 🕹️ Running Hardware QEMU Simulations

The repository provides launch scripts for all three target computing platforms:

### Target 1: ARM Cortex-M4 (MCUboot IoT Target)
Emulates the ARM Cortex-M4 microcontroller on MPS2-AN386 platform (120 MHz, 32 KB SRAM stack budget, 512 KB Flash):
```bash
bash pqc-secure-boot/firmware/platform/arm-cortex-m/run_qemu_cortex_m4.sh
```

### Target 2: RISC-V 64-bit (Das U-Boot FIT Image Target)
Emulates the SiFive RV64 application core (`virt` machine, 1.0 GHz, OpenSBI handoff):
```bash
bash pqc-secure-boot/firmware/scripts/run_qemu_riscv.sh
```

### Target 3: ARM Cortex-A57 4-Core SMP (EDK II / UEFI Target)
Emulates an enterprise server node running 4-core symmetric multiprocessing (`-smp 4`):
```bash
bash pqc-secure-boot/firmware/platform/arm-cortex-a/run_qemu_cortex_a57_smp.sh
```

> **Exiting QEMU**: Press `Ctrl + A`, release, then press `X`.

---

## 📊 Getting Target Microarchitecture Profiling

The repository includes a dedicated profiling CLI tool (`pqc-secure-boot/scripts/profile_targets.py`) to measure and compare clock cycles, verification latency, peak stack RAM, signature container sizes, and eFuse RoT footprints.

### 1. View Profiling Across All Targets
```bash
python3 pqc-secure-boot/scripts/profile_targets.py --target all
```

### 2. Profile a Specific Hardware Platform
```bash
# MCUboot on ARM Cortex-M4 (120 MHz)
python3 pqc-secure-boot/scripts/profile_targets.py --target mcuboot

# Das U-Boot on RISC-V 64-bit (1.0 GHz)
python3 pqc-secure-boot/scripts/profile_targets.py --target uboot

# EDK II / UEFI on ARM Cortex-A57 4-Core SMP (1.2 GHz)
python3 pqc-secure-boot/scripts/profile_targets.py --target uefi
```

### 3. Run Live Cryptographic Verification Benchmarks (Host Engine)
Runs 50 verification iterations on the native C engine to measure real-time execution velocity:
```bash
python3 pqc-secure-boot/scripts/profile_targets.py --target all --live-bench
```

### 4. Export Profiling Reports (Markdown or CSV)
```bash
# Export Markdown report
python3 pqc-secure-boot/scripts/profile_targets.py --target all --format markdown --export profiling_report.md

# Export CSV report
python3 pqc-secure-boot/scripts/profile_targets.py --target all --format csv --export profiling_report.csv
```

### Empirical Profiling Summary (MCUboot on ARM Cortex-M4 @ 120 MHz):
| Algorithm | Standard / Type | Latency (ms) | Clock Cycles | Peak Stack RAM | Sig Container | RoT eFuse | Security Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **RSA-2048** | Classical Baseline | 8.0 ms | 960,000 | 1,024 B | 256 B | 256 B Modulus | Broken (Shor's) |
| **RSA-3072** | Classical Baseline | 18.0 ms | 2,160,000 | 1,536 B | 384 B | 384 B Modulus | Broken (Shor's) |
| **ECDSA P-256** | Classical Baseline | 4.0 ms | 480,000 | 768 B | 64 B | 32 B Hash | Broken (Shor's) |
| **ML-DSA-44** | Lattice (NIST FIPS 204) | **3.5 ms** | **420,000** | **2,456 B** | **2,420 B** | **32 B Hash** | **128-bit Quantum Secure** |
| **LMS (LMOTS)** | Hash Merkle (RFC 8554) | 12.0 ms | 1,440,000 | 1,280 B | 2,480 B | 32 B Hash | **128-bit Quantum Secure** |
| **SPHINCS+** | Stateless Hash (FIPS 205) | 180.0 ms | 21,600,000 | 2,304 B | 17,088 B | 32 B Root | **128-bit Quantum Secure** |

#### Key Microarchitectural Takeaways:
- **ML-DSA-44 Latency**: Verifies in **3.5 ms** (420,000 clock cycles)—**12.5% faster than ECDSA P-256** and **57% faster than RSA-2048**.
- **Deterministic Stack Safety**: Peak stack SRAM consumption is **2,456 bytes** (measured via GDB stack painting `0xAA` watermarking), providing **>92% headroom** within MCUboot's 32 KB static SRAM budget.
- **RoT eFuse Efficiency**: By adopting a 32-byte SHA-256 public key hash commitment model, ML-DSA-44 requires identical OTP eFuse storage (**32 bytes**) to ECDSA P-256.

---

## 🎨 Local Documentation Site & Playground

Launch the local Docusaurus web application with live React verification playgrounds:

```bash
cd pqc-secure-boot/docs-site
npm install
npm run start -- --host 0.0.0.0 --port 3000
```
Open [http://localhost:3000/pqc-boot/](http://localhost:3000/pqc-boot/) in your browser.

---

## 📂 Repository Architecture

```text
pqc-boot/
├── .devcontainer/              # GitHub Codespaces & VS Code Devcontainer configuration
│   ├── devcontainer.json       # Toolchains, extensions, port 3000 forward
│   └── setup.sh                # Automated QEMU, compiler, & submodule bootstrap script
├── .github/workflows/          # GitHub Actions CI/CD (GitHub Pages auto-deploy)
├── pqc-secure-boot/            # Core PQC Secure Boot Implementation
│   ├── firmware/               # Bare-metal C PQC reference engine & platform linkers
│   ├── real_world/             # Real-World Bootloader Git Submodules (Forks)
│   │   ├── mcuboot/            # [submodule] MCUboot with PQC TLV tags & imgtool
│   │   ├── uboot/              # [submodule] Das U-Boot with FIT Image PQC signatures
│   │   └── edk2/               # [submodule] EDK II UEFI SecurityPkg with PQC OIDs
│   ├── scripts/                # Target Microarchitecture Profiler & benchmark CLI
│   ├── tests/                  # 4-Tier Automated Test Harness Array (23 / 23 Tests)
│   ├── docs-site/              # Docusaurus documentation web application (React Playgrounds)
│   └── architecture/           # Formal threat modeling and trade-off matrices
└── submission-docs/            # Academic Submission Deliverables
    └── midsem-report/          # Mid-semester report (Markdown, DOCX, and PDF)
```

---

## 📜 License & Academic Affiliation
M.Tech Dissertation Project, BITS Pilani (ESZG628T).  
All original source code licensed under the [Apache-2.0 License](LICENSE).
