/*
 * SPDX-License-Identifier: GPL-2.0+
 * Copyright (c) 2026 PQC FIT Verification Integration for U-Boot
 */

#ifndef _U_BOOT_PQC_FIT_H
#define _U_BOOT_PQC_FIT_H

#include <image.h>

/**
 * Verify PQC signature over FIT image regions (ML-DSA-44, SPHINCS+, LMS).
 *
 * @info: Image signing information (key, checksum, algorithm)
 * @region: Array of image memory regions to verify
 * @region_count: Number of regions
 * @sig: Signature byte buffer
 * @sig_len: Signature buffer length
 * Return: 0 if signature is valid, negative error code on failure
 */
int pqc_fit_verify(struct image_sign_info *info,
                   const struct image_region region[],
                   int region_count,
                   const uint8_t *sig,
                   uint sig_len);

#endif /* _U_BOOT_PQC_FIT_H */
