# CMake Build Guide & Toolchain Configuration

## Overview

The PQC Secure Boot project uses CMake for cross-platform bare-metal compilation targeting RISC-V and ARM platforms.

---

## Toolchain File (`cmake/riscv32-toolchain.cmake`)

```cmake
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR riscv32)

set(CMAKE_C_COMPILER riscv64-unknown-elf-gcc)
set(CMAKE_CXX_COMPILER riscv64-unknown-elf-g++)
set(CMAKE_OBJCOPY riscv64-unknown-elf-objcopy)

set(ARCH_FLAGS "-march=rv32imac -mabi=ilp32")

set(CMAKE_C_FLAGS "${ARCH_FLAGS} -ffreestanding -nostdlib -O2 -Wall -Wextra" CACHE STRING "")
set(CMAKE_CXX_FLAGS "${ARCH_FLAGS} -ffreestanding -nostdlib -fno-exceptions -fno-rtti -O2" CACHE STRING "")
```

---

## Building the Bootloader

```bash
# 1. Create build directory
mkdir -p build && cd build

# 2. Configure with CMake
cmake -DCMAKE_TOOLCHAIN_FILE=../cmake/riscv32-toolchain.cmake \
      -DPQC_ALGO=ML-DSA-44 \
      -DENABLE_ZERO_MALLOC=ON ..

# 3. Compile binary
make -j$(nproc)

# 4. Generate raw binary file
riscv64-unknown-elf-objcopy -O binary pqc_bootloader.elf pqc_bootloader.bin
```

---

## CMake Configuration Flags

- `-DPQC_ALGO=[ML-DSA-44|ML-DSA-87|LMS|SLH-DSA]`: Selects PQC verification algorithm.
- `-DENABLE_ZERO_MALLOC=ON`: Enforces zero dynamic memory allocation check during linkage.
- `-DBENCHMARK_CYCLES=ON`: Includes hardware cycle counter read instructions for profiling.
