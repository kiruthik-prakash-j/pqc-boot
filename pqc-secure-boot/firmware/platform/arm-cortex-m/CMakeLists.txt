cmake_minimum_required(VERSION 3.16)

add_executable(pqc_boot_mps2
    ../../src/main.c
    ../../src/pqc_boot.c
    ../../src/pqc_crypto.c
    ../../src/rot_key.c
    ../../src/sha256.c
    ../../src/shake256.c
    ../../src/ml_dsa.c
    ../../src/sphincs_plus.c
    ../../src/lms.c
    ../../src/startup_mps2.c
    platform_mps2.c
)

target_include_directories(pqc_boot_mps2 PRIVATE ../../include)

target_compile_options(pqc_boot_mps2 PRIVATE
    -ffreestanding
    -nostdlib
    -fno-builtin
    -Wall
    -Wextra
)

target_link_options(pqc_boot_mps2 PRIVATE
    -T ${CMAKE_CURRENT_SOURCE_DIR}/mps2-an385.ld
    -nostdlib
    -Wl,--gc-sections
)
