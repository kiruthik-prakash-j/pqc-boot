cmake_minimum_required(VERSION 3.16)
project(PQC_Secure_Boot C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

include_directories(include)

# Host native runner executable
add_executable(pqc_boot_host
    src/main.c
    src/pqc_boot.c
    src/pqc_crypto.c
    src/rot_key.c
    src/sha256.c
    src/shake256.c
    src/ml_dsa.c
    src/sphincs_plus.c
    src/lms.c
    src/platform_host.c
)

target_compile_options(pqc_boot_host PRIVATE -Wall -Wextra -Werror)

# Platform targets conditional on cross compilers or built alongside
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/platform/riscv-virt/CMakeLists.txt")
    add_subdirectory(platform/riscv-virt EXCLUDE_FROM_ALL)
endif()

if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/platform/arm-cortex-m/CMakeLists.txt")
    add_subdirectory(platform/arm-cortex-m EXCLUDE_FROM_ALL)
endif()

if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/platform/arm-cortex-a/CMakeLists.txt")
    add_subdirectory(platform/arm-cortex-a EXCLUDE_FROM_ALL)
endif()
