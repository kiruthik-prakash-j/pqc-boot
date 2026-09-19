# MCUboot Post-Quantum Cryptography (PQC) Integration

This directory contains the official **MCUboot** repository extended with Post-Quantum Cryptography (PQC) image authentication for ARM Cortex-M microcontrollers.

---

## Technical Specifications

- **Target Architecture**: ARM Cortex-M4 (`mps2-an386` FPGA target in QEMU).
- **Linker Script**: `firmware/platform/arm-cortex-m/mps2-an386.ld` (32 KB static stack).
- **PQC TLV Trailer Tags** (`boot/bootutil/include/bootutil/image.h`):
  - `IMAGE_TLV_ML_DSA_44` = `0x80`
  - `IMAGE_TLV_SPHINCS_PLUS` = `0x81`
  - `IMAGE_TLV_LMS` = `0x82`
  - `IMAGE_TLV_PQC_PUBKEY` = `0x88`
- **Signing Tool**: Extended `scripts/imgtool/main.py` supporting `imgtool keygen` and `imgtool sign`.

---

## How to Sign and Verify Firmware Images

```bash
# 1. Key Generation
python3 scripts/imgtool/main.py keygen -k keys/ml_dsa_key.json -t ml-dsa-44

# 2. Sign Image with PQC TLV
python3 scripts/imgtool/main.py sign \
    -k keys/ml_dsa_key.json \
    --header-size 0x200 \
    --align 4 \
    --version 1.0.0+0 \
    --pad-header \
    ../../firmware/build/pqc_boot_host signed_m4.bin

# 3. Emulate on QEMU ARM Cortex-M4
../../firmware/platform/arm-cortex-m/run_qemu_cortex_m4.sh
```
