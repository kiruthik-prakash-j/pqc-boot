#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Target Profiling & Benchmark Runner Helper
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PQC_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Ensure host binary is built
if [ ! -f "${PQC_DIR}/firmware/build/pqc_boot_host" ]; then
    echo "[BUILD] Compiling reference C engine for live profiling..."
    mkdir -p "${PQC_DIR}/firmware/build"
    cmake -B "${PQC_DIR}/firmware/build" -S "${PQC_DIR}/firmware"
    make -C "${PQC_DIR}/firmware/build" pqc_boot_host
fi

python3 "${SCRIPT_DIR}/profile_targets.py" "$@"
