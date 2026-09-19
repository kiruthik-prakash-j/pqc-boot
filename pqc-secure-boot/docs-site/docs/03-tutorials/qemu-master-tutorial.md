---
id: qemu-master-tutorial
title: "QEMU Master Tutorial: Setup, Execution, GDB Debugging & Tamper Testing"
sidebar_label: "QEMU Master Tutorial"
---

# QEMU Master Tutorial: Setup, Multitarget Execution, GDB Debugging & Tamper Verification

This comprehensive master tutorial provides complete step-by-step instructions for installing, configuring, running, debugging with GDB (`gdb-multiarch` / `arm-none-eabi-gdb`), and validating Post-Quantum Secure Boot on **QEMU emulators** across three target hardware architectures.

---

## 1. QEMU Architecture Overview & Target Hardware Emulation

QEMU (Quick Emulator) provides full system emulation for embedded hardware targets without requiring physical silicon. In this project, QEMU models the root-of-trust execution environment across three target platforms:

```mermaid
graph TD
    subgraph Host Development Workstation
        GDB[GDB Debugger / gdb-multiarch]
        CLI[Runner Scripts / Python Harness]
    end

    subgraph QEMU Full System Emulator Engine
        TCP[GDB Stub Server - TCP Port 1234]

        subgraph Target A: ARM Cortex-M4 (mps2-an386)
            M4_CPU[ARMv7E-M Cortex-M4 Core]
            M4_RAM[4KB Static SRAM / Stack]
            M4_NVRAM[Flash 0x00000000]
            M4_VERIF[MCUboot Verification Engine: bootutil_verify_pqc]
        end

        subgraph Target B: RISC-V 64 (virt)
            RV_CPU[RV64GC RISC-V Core M/S Mode]
            RV_RAM[256MB RAM]
            RV_PMP[Physical Memory Protection PMP]
            RV_VERIF[U-Boot FIT Verification Engine: pqc_crypto_verify_signature]
        end

        subgraph Target C: ARM Cortex-A57 (virt 4-Core SMP)
            A57_CPU[ARMv8-A AArch64 4-Core SMP]
            A57_GIC[GICv3 Interrupt Controller]
            A57_NVRAM[Secure NVRAM db/KEK/PK Store]
            A57_VERIF[EDKII / UEFI Verification Engine: Pkcs7VerifyPqc]
        end
    end

    GDB <-->|TCP Socket localhost:1234| TCP
    CLI -->|Exec Launch| QEMU
    TCP -.-> M4_CPU
    TCP -.-> RV_CPU
    TCP -.-> A57_CPU
```

### Architectural Breakdown of Target Hardware Emulators

| Parameter / Feature | Target A: MCUboot | Target B: U-Boot FIT | Target C: EDKII / UEFI |
| :--- | :--- | :--- | :--- |
| **Processor Target** | ARM Cortex-M4 | RISC-V 64-bit | ARM Cortex-A57 |
| **ISA / Architecture** | ARMv7E-M (32-bit Thumb-2) | RV64GC (64-bit RISC-V) | ARMv8-A AArch64 (64-bit) |
| **QEMU Machine Model** | `mps2-an386` (ARM MPS2 FPGA) | `virt` (QEMU RISC-V Virt) | `virt` (QEMU ARM Virt) |
| **CPU Topologies** | 1 Core | 1 Core | 4-Core SMP (`-smp 4`) |
| **Memory Constraints** | 4KB SRAM (Zero-malloc stack limit) | 256MB DRAM | 1024MB DRAM |
| **Secure NVRAM / Key Store**| Embedded Flash (`0x00000000`) | FIT Signature Public Key Node | UEFI Authenticated Variables (`db`) |
| **PQC Verification Entry**| `bootutil_verify_pqc()` | `pqc_crypto_verify_signature()` | `Pkcs7VerifyPqc()` |

---

## 2. Toolchain & QEMU Installation

Ensure all cross-compilers, QEMU system emulators, and debugging utilities are installed on your host system.

### Ubuntu / Debian Linux Installation
```bash
sudo apt-get update && sudo apt-get install -y \
    qemu-system-arm \
    qemu-system-misc \
    gdb-multiarch \
    gcc-arm-none-eabi \
    gcc-aarch64-linux-gnu \
    gcc-riscv64-linux-gnu \
    cmake \
    build-essential \
    python3 \
    python3-pip
```

### Arch Linux Installation
```bash
sudo pacman -Syu --needed \
    qemu-system-arm \
    qemu-system-riscv \
    qemu-system-aarch64 \
    gdb \
    arm-none-eabi-gcc \
    aarch64-linux-gnu-gcc \
    riscv64-linux-gnu-gcc \
    cmake \
    python
```

### macOS (Homebrew) Installation
```bash
brew update && brew install \
    qemu \
    gdb \
    arm-none-eabi-gcc \
    aarch64-elf-gcc \
    riscv64-elf-gcc \
    cmake \
    python3
```

### Toolchain Verification
Verify toolchain binaries are properly exported in your PATH:
```bash
qemu-system-arm --version
qemu-system-riscv64 --version
qemu-system-aarch64 --version
gdb-multiarch --version || arm-none-eabi-gdb --version
```

---

## 3. Target Hardware Emulation Execution Commands

### Target A: MCUboot on ARM Cortex-M4 (`mps2-an386`)

#### Automated Runner Script:
```bash
firmware/platform/arm-cortex-m/run_qemu_cortex_m4.sh
```

#### Raw QEMU Command:
```bash
qemu-system-arm \
    -machine mps2-an386 \
    -cpu cortex-m4 \
    -nographic \
    -kernel firmware/build/pqc_boot_host
```

---

### Target B: U-Boot FIT on RISC-V 64 (`virt`)

#### Automated Runner Script:
```bash
firmware/platform/riscv64/run_qemu_riscv64.sh
```

#### Raw QEMU Command:
```bash
qemu-system-riscv64 \
    -M virt \
    -cpu rv64 \
    -m 256M \
    -nographic \
    -bios none \
    -kernel firmware/build/pqc_boot_host
```

---

### Target C: EDKII / UEFI on ARM Cortex-A57 4-Core SMP (`virt`)

#### Automated Runner Script:
```bash
firmware/platform/arm-cortex-a/run_qemu_cortex_a57_smp.sh
```

#### Raw QEMU Command:
```bash
qemu-system-aarch64 \
    -M virt \
    -cpu cortex-a57 \
    -smp 4 \
    -m 1024M \
    -nographic \
    -kernel firmware/build/pqc_boot_host
```

#### QEMU Flag Descriptions:
- `-machine` / `-M`: Selects the target motherboard architecture emulation model.
- `-cpu`: Specifies exact CPU core architecture (Cortex-M4, RV64GC, Cortex-A57).
- `-smp 4`: Configures 4-core Symmetric Multiprocessing for ARM Cortex-A57.
- `-nographic`: Disables graphical window creation; redirects serial UART output to host terminal stdin/stdout.
- `-s`: Opens GDB stub server listening on TCP port `1234`.
- `-S`: Freezes target CPU at boot reset vector, waiting for GDB `continue` command.

---

## 4. Advanced GDB Debugging Workflows

Attach `gdb-multiarch` or `arm-none-eabi-gdb` to inspect PQC verification routines, examine CPU register states, and analyze static memory allocations.

### Step 1: Launch QEMU with GDB Server Enabled (`-s -S`)
```bash
# Example: Launch ARM Cortex-M4 target frozen at reset
qemu-system-arm \
    -machine mps2-an386 \
    -cpu cortex-m4 \
    -nographic \
    -kernel ./firmware/build/pqc_boot_host \
    -s -S
```

### Step 2: Connect GDB Client
In a second terminal window, start GDB loading the target ELF binary symbols:
```bash
gdb-multiarch ./firmware/build/pqc_boot_host
```

Connect to the QEMU GDB stub:
```text
(gdb) target remote localhost:1234
Remote debugging using localhost:1234
0x00000000 in Reset_Handler ()
```

### Step 3: Setting Breakpoints on PQC Verification Engines

Set breakpoints on the core signature verification functions across all three firmware targets:

```text
# Breakpoint 1: Generic PQC Verification Engine (pqc_crypto.c)
(gdb) break pqc_crypto_verify_signature
Breakpoint 1 at 0x8001124: file firmware/src/pqc_crypto.c, line 42.

# Breakpoint 2: MCUboot Image Verification Entry Point (bootutil_pqc.c)
(gdb) break bootutil_verify_pqc
Breakpoint 2 at 0x8001488: file real_world/mcuboot/boot/bootutil/src/bootutil_pqc.c, line 85.

# Breakpoint 3: EDKII / UEFI SecurityPkg PKCS#7 Engine (Pkcs7VerifyPqc)
(gdb) break Pkcs7VerifyPqc
Breakpoint 3 at 0x8002100: file real_world/edk2/CryptoPkg/Library/BaseCryptLib/Pkcs7VerifyPqc.c, line 110.

# Resume CPU Execution
(gdb) continue
Continuing.
Breakpoint 1, pqc_crypto_verify_signature (public_key=0x20000100, message=0x20000800, msg_len=1024, sig=0x20000c00, sig_len=2420, scheme=PQC_SCHEME_ML_DSA_44) at firmware/src/pqc_crypto.c:42
```

---

### Step 4: CPU Register Inspection across Target Architectures

When a breakpoint hits, inspect target CPU registers:

#### ARM 32-bit Cortex-M4 Register Inspection:
```text
(gdb) info registers
r0             0x20000100          536871168    (public_key pointer)
r1             0x20000800          536872960    (message pointer)
r2             0x400               1024         (msg_len)
r3             0x20000c00          536873984    (sig pointer)
r4             0x0                 0
r12            0x0                 0
sp             0x20003fc0          0x20003fc0   (Main Stack Pointer)
lr             0x8000845           134219845    (Return Address)
pc             0x8001124           0x8001124 <pqc_crypto_verify_signature>
xPSR           0x61000000          1627389952
```

#### RISC-V 64-bit Register Inspection:
```text
(gdb) info registers
ra             0x800001a2          Return Address
sp             0x8003f000          Stack Pointer
a0             0x80010000          Arg 0: public_key
a1             0x80010800          Arg 1: message
a2             0x400               Arg 2: msg_len
a3             0x80011000          Arg 3: sig
pc             0x80002104          Program Counter
mstatus        0x8000000a00001800  Machine Status
mcause         0x0                 Trap Cause
```

#### ARM 64-bit Cortex-A57 Register Inspection:
```text
(gdb) info registers
x0             0x40000100          Arg 0: public_key
x1             0x40000800          Arg 1: message
x2             0x400               Arg 2: msg_len
x3             0x40000c00          Arg 3: sig
x29            0x4003fa00          Frame Pointer
x30            0x400018b0          Link Register (LR)
sp             0x4003f9e0          Stack Pointer
pc             0x40002100          Program Counter
pstate         0x60000005          EL1h Mode
```

---

### Step 5: Static Stack Frame Analysis & Memory Dumping

To enforce zero-malloc embedded RAM constraints (`< 4KB` stack utilization), verify stack layout and inspect memory contents:

#### Stack Frame Backtrace:
```text
(gdb) backtrace
#0  pqc_crypto_verify_signature (public_key=0x20000100, message=0x20000800, msg_len=1024, sig=0x20000c00, sig_len=2420, scheme=PQC_SCHEME_ML_DSA_44) at firmware/src/pqc_crypto.c:42
#1  0x080014aa in bootutil_verify_pqc (ctx=0x20000050) at real_world/mcuboot/boot/bootutil/src/bootutil_pqc.c:95
#2  0x08000846 in main () at firmware/src/pqc_boot.c:110

(gdb) info frame
Stack level 0, frame at 0x20003fd0:
 pc = 0x8001124 in pqc_crypto_verify_signature (firmware/src/pqc_crypto.c:42); saved pc = 0x80014aa
 called by frame at 0x20003ff0
 source language c.
 Arglist at 0x20003fc0, args: public_key=0x20000100, message=0x20000800, msg_len=1024, sig=0x20000c00, sig_len=2420, scheme=PQC_SCHEME_ML_DSA_44
 Locals at 0x20003fc0, Previous frame's sp is 0x20003fd0
```

#### Memory Hex Dumps:
```text
# Dump top 32 words of Stack Pointer (SP) to verify stack usage
(gdb) x/32wx $sp

# Dump first 32 bytes of signature buffer in Hexadecimal format
(gdb) x/32xb sig
0x20000c00: 0x4f 0xa2 0x11 0x9b 0xbc 0x3d 0xee 0x01
0x20000c08: 0x77 0x89 0x22 0x54 0xfa 0xc1 0x00 0x12
0x20000c10: 0xaa 0xbb 0xcc 0xdd 0xee 0xff 0x00 0x11
0x20000c18: 0x22 0x33 0x44 0x55 0x66 0x77 0x88 0x99

# Print MCUboot Image Header structure
(gdb) print/x *(struct image_header*)message
$1 = {
  ih_magic = 0x96f3b83d,
  ih_load_addr = 0x20008000,
  ih_hdr_size = 0x200,
  ih_protect_tlv_size = 0x40,
  ih_img_size = 0x4000,
  ih_flags = 0x0,
  ih_ver = {
    iv_major = 0x1,
    iv_minor = 0x0,
    iv_revision = 0x0,
    iv_build = 0x0
  }
}
```

---

## 5. Bit-Flip Tamper Rejection & Fault Injection Protocol

To empirically prove that the secure bootloader halts on tampered binary payloads, follow this bit-flip corruption protocol:

### Step 1: Generate Legitimate Signed Payload
```bash
cd pqc-secure-boot

# Sign clean binary payload with ML-DSA-44 key
python3 real_world/mcuboot/scripts/imgtool/main.py sign \
    -k real_world/mcuboot/keys/ml_dsa_key.json \
    --header-size 0x200 \
    --align 4 \
    --version 1.0.0+0 \
    --pad-header \
    firmware/build/pqc_boot_host signed_firmware.bin
```

### Step 2: Inject Programmatic Bit-Flip Tamper
Run Python script to flip a single bit (XOR `0xFF`) at offset `0x210` in the payload body:

```bash
python3 -c "
with open('signed_firmware.bin', 'r+b') as f:
    f.seek(0x210)
    orig = f.read(1)
    f.seek(0x210)
    corrupted = bytes([orig[0] ^ 0xFF])
    f.write(corrupted)
    print(f'[TAMPER INJECTED] Byte at 0x210 modified from {orig.hex()} to {corrupted.hex()}')
"
```

### Step 3: Run QEMU Emulation & Observe Rejection

Execute the target QEMU emulator with the tampered binary:

```bash
firmware/platform/arm-cortex-m/run_qemu_cortex_m4.sh
```

#### Verified Console Log Output (Tamper Security Halt):
```text
[PQC-BOOT] Initializing Root of Trust...
[PQC-BOOT] Target Platform: ARM MPS2 FPGA (Cortex-M4 / mps2-an386)
[PQC-BOOT] Scheme: ML-DSA-44 (NIST FIPS 204)
[PQC-BOOT] Running PQC Signature Verification engine...
[PQC-BOOT] ERROR: Signature Verification FAILED! (Status Code: -2)
[PQC-BOOT] FATAL: Bootloader failed! Integrity violation detected.
[PQC-BOOT] System Halted.
```

### Step 4: GDB Live Tamper Verification
Attach GDB to step through polynomial verification loop failure:

```text
(gdb) break pqc_crypto_verify_signature
(gdb) continue
(gdb) finish
Run till exit from #0  pqc_crypto_verify_signature (...) at firmware/src/pqc_crypto.c:98
Value returned is $2 = -2 (PQC_ERR_VERIFY_FAILED)
(gdb) print/x $r0
$3 = 0xfffffffe   (-2 in 32-bit Two's Complement)
```
The non-zero error status code `-2` triggers the bootloader's security exception handler, halting CPU execution before jumping to the untrusted kernel code address.

---

## 6. Troubleshooting & Diagnostic Matrix

| Issue / Error Symptom | Cause | Resolution |
| :--- | :--- | :--- |
| `gdb: Connection refused (localhost:1234)` | QEMU was launched without `-s` or closed prematurely. | Re-launch QEMU command including `-s -S` flags prior to running GDB `target remote`. |
| `qemu-system-arm: command not found` | QEMU ARM system emulator package missing. | Run `sudo apt-get install qemu-system-arm qemu-system-misc`. |
| `Remote 'g' packet reply is too long` | GDB architecture mismatch between target ELF and GDB client. | Use `gdb-multiarch` instead of single-arch `gdb`, or execute `(gdb) set architecture armv7e-m` / `set architecture riscv:rv64` / `set architecture aarch64`. |
| `QEMU Triple Fault / Infinite Reset Loop` | Firmware vector table unaligned or stack pointer `SP` corrupted. | Verify linker script `ORIGIN(SRAM)` and ensure `-header-size 0x200` is aligned to 4 bytes in `imgtool`. |
| `No serial console output` | QEMU stdout redirection missing. | Add `-nographic` flag to QEMU CLI invocation. |
