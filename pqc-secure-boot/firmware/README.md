# Bare-Metal PQC Firmware & Verification Engine

This directory contains the zero dynamic memory allocation C reference implementation for Post-Quantum Cryptography (PQC) digital signature verification.

---

## Directory Layout

```text
firmware/
├── include/            # C headers for PQC algorithms, hashes, and RoT keys
│   ├── bootutil_pqc.h  # MCUboot / Host PQC verification headers
│   ├── lms.h           # LMS / LMOTS RFC 8554 definitions
│   ├── ml_dsa.h        # ML-DSA-44 NIST FIPS 204 definitions
│   ├── pqc_boot.h      # PQC Image Header & Boot status codes
│   ├── pqc_crypto.h    # Cryptographic dispatch API
│   ├── rot_key.h       # Root-of-Trust public key structures
│   ├── sha256.h        # SHA-256 hash context
│   ├── shake256.h      # SHAKE-256 extendable-output function
│   └── sphincs_plus.h  # SPHINCS+ NIST FIPS 205 definitions
├── src/                # C source files (Zero-malloc enforcement)
│   ├── lms.c           # LMS verification engine
│   ├── main.c          # Host test harness & sample signing
│   ├── ml_dsa.c        # ML-DSA-44 verification engine
│   ├── pqc_boot.c      # Bootloader header parser & verification loop
│   ├── pqc_crypto.c    # Algorithm dispatcher
│   ├── rot_key.c       # Embedded Root-of-Trust key table
│   ├── sha256.c        # SHA-256 implementation
│   ├── shake256.c      # SHAKE-256 implementation
│   └── sphincs_plus.c  # SPHINCS+ verification engine
├── platform/           # Linker scripts & QEMU launchers
│   ├── arm-cortex-m/   # mps2-an386.ld & run_qemu_cortex_m4.sh
│   └── arm-cortex-a/   # run_qemu_cortex_a57_smp.sh
└── CMakeLists.txt      # Firmware CMake build system
```

---

## Build & Test Instructions

```bash
# Build host runner executable
cmake -B build -S .
cmake --build build

# Execute host runner verification binary
./build/pqc_boot_host
```
