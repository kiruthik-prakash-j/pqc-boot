# PQC Secure Boot Benchmarking Results

## Experimental Setup

- **Target Hardware Architecture**: RISC-V RV32IMAC @ 300 MHz (QEMU Emulated).
- **Compiler**: GCC 13.2.0 (`-O2 -ffreestanding -nostdlib`).
- **Memory Boundaries**: 64 KB SRAM, 64 MB DRAM.

---

## Performance Summary Table

| Algorithm | Public Key Size | Signature Size | Verification Time (ms) | Execution Cycles | Peak Stack RAM | Code Size (.text) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **LMS (SHA256_M32_H10)** | 60 B | 1,180 B | **0.18 ms** | 540,000 | **2.4 KB** | 8.4 KB |
| **ML-DSA-44** | 1,312 B | 2,420 B | **0.45 ms** | 1,350,000 | **8.2 KB** | 22.1 KB |
| **ML-DSA-87** | 2,592 B | 4,627 B | **0.92 ms** | 2,760,000 | **14.8 KB** | 28.6 KB |
| **SLH-DSA-SHA2-128f** | 32 B | 17,088 B | **12.40 ms** | 37,200,000 | **4.1 KB** | 14.2 KB |

---

## Detailed Analysis

1. **LMS**: Fastest verification time (0.18 ms) and smallest code footprint (8.4 KB). Ideal for Stage-0 Boot ROM.
2. **ML-DSA-44**: Excellent balance for Stage-1 SRAM bootloaders. NTT polynomial multiplication completes in 1.35M cycles.
3. **SLH-DSA-128f**: Very small public key footprint (32 B) minimizes eFuse storage requirements, but higher verification time (12.4 ms) due to tree traversal.
