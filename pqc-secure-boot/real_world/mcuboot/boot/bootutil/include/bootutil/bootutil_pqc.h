/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Copyright (c) 2026 MCUboot PQC Integration
 */

#ifndef H_BOOTUTIL_PQC_
#define H_BOOTUTIL_PQC_

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include "bootutil/image.h"
#include "bootutil/fault_injection_hardening.h"

#ifdef __cplusplus
extern "C" {
#endif

#define PQC_MAX_PUBKEY_LEN 2048
#define PQC_MAX_SIG_LEN    18000

/**
 * Verify a Post-Quantum Cryptography (PQC) digital signature.
 * Supports ML-DSA-44 (0x30), SPHINCS+ (0x31), and LMS (0x32).
 * Enforces zero dynamic memory allocation.
 */
fih_ret bootutil_verify_pqc(uint16_t tlv_type,
                            const uint8_t *msg, uint32_t mlen,
                            const uint8_t *sig, size_t slen,
                            const uint8_t *pk, size_t pklen);

#ifdef __cplusplus
}
#endif

#endif /* H_BOOTUTIL_PQC_ */
