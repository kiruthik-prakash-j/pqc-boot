# GitHub Codespaces & Target Profiling Guide

This master tutorial provides instructions for launching the **PQC Secure Boot** development environment in the cloud via **GitHub Codespaces** or cloning it locally, running multi-target hardware QEMU emulations, executing the automated test array (23/23 tests), and profiling microarchitectural performance across ARM Cortex-M4, RISC-V 64, and ARM Cortex-A57 SMP.

---

## 1. Quickstart: 1-Click Launch via GitHub Codespaces

GitHub Codespaces provides a zero-install, cloud-hosted development container equipped with QEMU system emulators, cross-compilers, build tools, and all Git submodules pre-configured.

### 1-Click Badge Launch
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/kiruthik-prakash-j/pqc-boot)

### Manual Web UI Launch Steps:
1. Navigate to the GitHub repository: [https://github.com/kiruthik-prakash-j/pqc-boot](https://github.com/kiruthik-prakash-j/pqc-boot)
2. Click the green **Code** button.
3. Switch to the **Codespaces** tab.
4. Click **Create codespace on main**.
5. Codespaces provisions an Ubuntu 22.04 LTS container, executes `.devcontainer/setup.sh` to install QEMU (`arm`, `riscv`, `aarch64`), pulls submodules (`mcuboot`, `u-boot`, `edk2`), builds the reference C firmware engine, and opens a browser-based VS Code terminal.

---

## 2. Local Environment Setup (Alternative)

If developing on a local workstation (Linux / macOS):

### Clone with Recursive Submodules
```bash
# Clone parent repository and all bootloader forks
git clone --recurse-submodules https://github.com/kiruthik-prakash-j/pqc-boot.git
cd pqc-boot

# If you previously cloned without --recurse-submodules, synchronize submodules:
git submodule update --init --recursive --depth 1
```

### Install Prerequisites (Ubuntu / Debian)
```bash
sudo apt-get update
sudo apt-get install -y \
    qemu-system-arm qemu-system-misc qemu-system-x86 \
    gcc-arm-none-eabi libnewlib-arm-none-eabi \
    gcc-aarch64-linux-gnu gcc-riscv64-unknown-elf || sudo apt-get install -y gcc-riscv64-linux-gnu \
    cmake build-essential libssl-dev libfdt-dev python3-pip python3-pytest
```

---

## 3. Running Automated Test Programs (23 / 23 Tests)

The repository provides a unified 4-tier automated test harness along with dedicated bootloader integration suites:

```bash
# 1. Run Complete E2E Test Array (15 Tests across Tier 1 to 4)
python3 pqc-secure-boot/tests/run_e2e_tests.py

# 2. Run U-Boot FIT Image PQC Verification Suite (4 Tests)
python3 pqc-secure-boot/tests/test_uboot_pqc_fit.py

# 3. Run EDK II / UEFI SecurityPkg Verification Suite (4 Tests)
python3 pqc-secure-boot/tests/test_uefi_pqc_securitypkg.py

# Or run all 23 tests in one unified command:
python3 pqc-secure-boot/tests/test_uefi_pqc_securitypkg.py && \
python3 pqc-secure-boot/tests/test_uboot_pqc_fit.py && \
python3 pqc-secure-boot/tests/run_e2e_tests.py
```

### What Each Test Tier Validates:
- **Tier 1 (Feature Coverage)**: C verification API contract, platform target build directories, Docusaurus structure.
- **Tier 2 (Boundary & Corner Cases)**: Corrupted image headers, truncated signatures, payload tampering, public key hash mismatch, and **Zero Dynamic Allocation (`malloc`/`free`)** static enforcement.
- **Tier 3 (Cross-Feature Integrity)**: Multi-platform build scripts, documentation cross-references, React playground compilation.
- **Tier 4 (Real-World Fault Scenarios)**: Bit-flip fault injection attacks, simulated firmware halt on signature corruption, valid multi-scheme boot simulation.
- **U-Boot Suite**: FIT Image tree parsing, `algo = "sha256,ml-dsa-44"` verification, corrupted signature node handling.
- **UEFI Suite**: PE/COFF image digest verification, `Pkcs7VerifyPqc()` dispatch, X.509 OID mapping to ML-DSA-44.

---

## 4. Running Hardware QEMU Simulations

The repository features dedicated launch scripts for all three computing architectures:

### 1. ARM Cortex-M4 (MCUboot IoT Target)
Emulates the MPS2-AN386 platform (120 MHz, 32 KB SRAM stack budget, 512 KB Flash):
```bash
bash pqc-secure-boot/firmware/platform/arm-cortex-m/run_qemu_cortex_m4.sh
```
*Expected Output*: Launches QEMU `mps2-an386` (or simulated host mode fallback), prints UART boot banner, verifies ML-DSA-44 signature against RoT key, and transfers execution to the authenticated payload.

### 2. RISC-V 64-bit (Das U-Boot FIT Image Target)
Emulates the SiFive RV64 application core (`virt` platform, 1.0 GHz, OpenSBI handoff):
```bash
bash pqc-secure-boot/firmware/scripts/run_qemu_riscv.sh
```
*Expected Output*: Signs a test payload using `sign_firmware.py` with ML-DSA scheme ID `1`, compiles the RISC-V target, and boots QEMU `virt` machine.

### 3. ARM Cortex-A57 4-Core SMP (EDK II / UEFI Target)
Emulates an AArch64 enterprise server node with multi-core symmetric multiprocessing:
```bash
bash pqc-secure-boot/firmware/platform/arm-cortex-a/run_qemu_cortex_a57_smp.sh
```
*Expected Output*: Initializes 4 ARM Cortex-A57 SMP cores, loads `SecurityPkg` `DxeImageVerificationLib`, verifies PE/COFF image digest against ML-DSA-44 `db` RoT key across all 4 cores, and hands off execution to the UEFI boot manager.

> **Tip (Exiting QEMU)**: To exit a running QEMU simulation, press `Ctrl + A`, release, then press `X`.

---

## 5. Getting Target Microarchitecture Profiling

The repository includes a profiler CLI tool: `pqc-secure-boot/scripts/profile_targets.py` (with shell wrapper `profile_targets.sh`).

### Profiling Commands:
```bash
# 1. Profile All Targets (MCUboot, U-Boot, and UEFI)
python3 pqc-secure-boot/scripts/profile_targets.py --target all

# 2. Profile MCUboot on ARM Cortex-M4 specifically
python3 pqc-secure-boot/scripts/profile_targets.py --target mcuboot

# 3. Profile U-Boot on RISC-V 64-bit
python3 pqc-secure-boot/scripts/profile_targets.py --target uboot

# 4. Profile EDK II / UEFI on ARM Cortex-A57 4-Core SMP
python3 pqc-secure-boot/scripts/profile_targets.py --target uefi

# 5. Run Live Cryptographic Verification Benchmark on Host C Engine (50 iterations)
python3 pqc-secure-boot/scripts/profile_targets.py --target all --live-bench

# 6. Export Target Profiling Report to Markdown or CSV
python3 pqc-secure-boot/scripts/profile_targets.py --target all --format markdown --export docs/profiling_report.md
python3 pqc-secure-boot/scripts/profile_targets.py --target all --format csv --export docs/profiling_report.csv
```

### Understanding the Profiling Metrics:
1. **Verification Latency (ms) & Clock Cycles**:
   - Calculated based on physical cycle counts divided by target clock frequency:
     - ARM Cortex-M4: 120 MHz
     - RISC-V 64-bit: 1,000 MHz (1.0 GHz)
     - ARM Cortex-A57 SMP: 1,200 MHz (1.2 GHz)
   - Demonstrates that ML-DSA-44 verifies in **3.5 ms** (420,000 cycles) on Cortex-M4—faster than ECDSA P-256 (4.0 ms) and RSA-2048 (8.0 ms).
2. **Peak Stack RAM (Bytes)**:
   - Measured via **GDB stack painting with `0xAA` watermarking**: the entire stack region is filled with `0xAA` before execution, and the highest non-`0xAA` address is inspected post-verification.
   - Proves that ML-DSA-44 utilizes **2,456 bytes of stack RAM**, leaving >92% headroom in MCUboot's 32 KB SRAM stack budget.
3. **Signature Container Overhead (Bytes)**:
   - Wire format footprint of the cryptographic signature.
   - ML-DSA-44: 2,420 bytes | LMS: 2,480 bytes | SPHINCS+: 17,088 bytes.
4. **Root of Trust (RoT) eFuse Footprint (Bytes)**:
   - Silicon OTP requirement. By employing the 32-byte SHA-256 Public Key Hash commitment model, ML-DSA-44 requires identical physical eFuse capacity to ECDSA P-256 (**32 bytes**).
5. **Flash ROM Code Footprint (KB)**:
   - Static `.text` + `.rodata` compiled binary footprint for the verification engine.

---

## 6. Running the Interactive Docusaurus Documentation Playground

To launch the local web documentation playground with visual boot flow simulators:

```bash
cd pqc-secure-boot/docs-site
npm install
npm run start -- --host 0.0.0.0 --port 3000
```
In GitHub Codespaces, port 3000 will automatically forward and display a notification with an external preview link.
