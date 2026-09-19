# Development Logbook & Engineering Timeline

## Project Chronology

### Milestone M1: Architecture & Cryptographic Primitives Setup
- Designed Hardware Root of Trust eFuse hash model.
- Integrated reference C implementations for ML-DSA (FIPS 204), SLH-DSA (FIPS 205), and LMS (RFC 8554).
- Established zero-malloc rules for embedded Stage-0 and Stage-1 bootloaders.

### Milestone M2: Bare-Metal QEMU Environment & Build Automation
- Created CMake toolchain files targeting `riscv32`, `riscv64`, and `arm-none-eabi`.
- Configured bare-metal memory maps for QEMU virt and lm3s6965evb platforms.
- Implemented boot manifest parser with anti-rollback counter enforcement.

### Milestone M3: Performance Benchmarking & Hardware Profiling
- Integrated hardware cycle counters (`rdcycle` on RISC-V, `DWT->CYCCNT` on ARM).
- Benchmark verification latency across ML-DSA-44, ML-DSA-87, SLH-DSA-128f, and LMS.
- Measured peak stack RAM usage and binary text/bss sizes.

### Milestone M4: Interactive Documentation & Visual Playground
- Built Docusaurus v3 documentation site with 5 core categories (`01-research`, `02-learning`, `03-implementation`, `04-logs`, `05-thesis`).
- Developed interactive React component `PqcBootPlayground` simulating step-by-step verification pipeline and live metrics.
