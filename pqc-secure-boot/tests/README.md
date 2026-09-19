# PQC Secure Boot End-to-End (E2E) Test Suite

## Overview
This directory contains the comprehensive opaque-box E2E test suite for the Post-Quantum Firmware Authentication (`pqc-boot`) project.

## Suite Architecture (4 Tiers)

1. **Tier 1: Feature Coverage (`tier1_feature_coverage.py`)**
   - QEMU target platform configuration checks (`riscv-virt`, `mps2-an385`, `arm-virt`).
   - PQC Signature Verification API contract (`pqc_boot_authenticate` & `get_rot_public_key`).
   - Docusaurus application config & documentation directory tree structure.
   - Academic thesis directory structure (`docs-site/docs/05-thesis`).

2. **Tier 2: Boundary & Corner Cases (`tier2_boundary_corner.py`)**
   - Rejection of corrupted image headers (invalid magic numbers, truncation, size mismatch).
   - Rejection of tampered / invalid PQC signatures.
   - Rejection of key mismatches against Root-of-Trust (RoT) public key.
   - Static analysis enforcing Zero Dynamic Memory Allocation policy (`malloc`/`free`, `new`/`delete`).

3. **Tier 3: Cross-Feature Combinations (`tier3_cross_feature.py`)**
   - Automated multi-platform CMake build configuration structure.
   - React `<PqcBootPlayground />` visual simulator component structure.
   - Documentation integrity and cross-references.

4. **Tier 4: Real-World Scenarios (`tier4_real_world.py`)**
   - Tampered firmware boot halt simulation (payload bit-flip triggers authentication refusal).
   - Valid signed firmware boot success simulation (ML-DSA, SPHINCS+, LMS).

## How to Run Tests

### Run Full E2E Test Suite
```bash
python3 tests/run_e2e_tests.py
# OR
./tests/run_tests.sh
```

### Run Specific Tier Test
```bash
python3 -m unittest tests/tier1_feature_coverage.py
python3 -m unittest tests/tier2_boundary_corner.py
python3 -m unittest tests/tier3_cross_feature.py
python3 -m unittest tests/tier4_real_world.py
```
