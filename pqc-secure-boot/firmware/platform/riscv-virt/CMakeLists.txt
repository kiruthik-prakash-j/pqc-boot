cmake_minimum_required(VERSION 3.16)

add_executable(pqc_boot_riscv
    ../../src/main.c
    ../../src/pqc_boot.c
    ../../src/pqc_crypto.c
    ../../src/rot_key.c
    ../../src/sha256.c
    ../../src/shake256.c
    ../../src/ml_dsa.c
    ../../src/sphincs_plus.c
    ../../src/lms.c
    ../../src/startup_riscv.c
    platform_riscv.c
)

target_include_directories(pqc_boot_riscv PRIVATE ../../include)

target_compile_options(pqc_boot_riscv PRIVATE
    -ffreestanding
    -nostdlib
    -fno-builtin
    -Wall
    -Wextra
)

target_link_options(pqc_boot_riscv PRIVATE
    -T ${CMAKE_CURRENT_SOURCE_DIR}/riscv-virt.ld
    -nostdlib
    -Wl,--gc-sections
)
