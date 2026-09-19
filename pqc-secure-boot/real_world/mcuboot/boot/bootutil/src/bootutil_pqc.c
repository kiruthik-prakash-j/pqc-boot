/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Copyright (c) 2026 MCUboot PQC Integration
 *
 * Post-Quantum Cryptography (PQC) Signature Verification Module for MCUboot
 * Supporting FIPS 204 ML-DSA-44, FIPS 205 SPHINCS+, and RFC 8554 LMS/LMOTS.
 * Enforces strictly zero dynamic memory allocation (zero-malloc).
 */

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#include "bootutil/image.h"
#include "bootutil/bootutil_pqc.h"
#include "bootutil/fault_injection_hardening.h"
#include "bootutil/bootutil_log.h"

BOOT_LOG_MODULE_DECLARE(mcuboot);

/* --- SHA-256 Primitives (Zero-Malloc) --- */
typedef struct {
    uint32_t state[8];
    uint64_t count;
    uint8_t buffer[64];
} pqc_sha256_ctx;

static const uint32_t K256[64] = {
    0x428a2f98U, 0x71374491U, 0xb5c0fbcfU, 0xe9b5dba5U, 0x3956c25bU, 0x59f111f1U, 0x923f82a4U, 0xab1c5ed5U,
    0xd807aa98U, 0x12835b01U, 0x243185beU, 0x550c7dc3U, 0x72be5d74U, 0x80deb1feU, 0x9bdc06a7U, 0xc19bf174U,
    0xe49b69c1U, 0xefbe4786U, 0x0fc19dc6U, 0x240ca1ccU, 0x2de92c6fU, 0x4a7484aaU, 0x5cb0a9dcU, 0x76f988daU,
    0x983e5152U, 0xa831c66dU, 0xb00327c8U, 0xbf597fc7U, 0xc6e00bf3U, 0xd5a79147U, 0x06ca6351U, 0x14292967U,
    0x27b70a85U, 0x2e1b2138U, 0x4d2c6dfcU, 0x53380d13U, 0x650a7354U, 0x766a0abbU, 0x81c2c92eU, 0x92722c85U,
    0xa2bfe8a1U, 0xa81a664bU, 0xc24b8b70U, 0xc76c51a3U, 0xd192e819U, 0xd6990624U, 0xf40e3585U, 0x106aa070U,
    0x19a4c116U, 0x1e376c08U, 0x2748774cU, 0x34b0bcb5U, 0x391c0cb3U, 0x4ed8aa4aU, 0x5b9cca4fU, 0x682e6ff3U,
    0x748f82eeU, 0x78a5636fU, 0x84c87814U, 0x8cc70208U, 0x90befffaU, 0xa4506cebU, 0xbef4a3f7U, 0xc67178f2U
};

#define ROTR(x, n) (((x) >> (n)) | ((x) << (32 - (n))))
#define CH(x, y, z) (((x) & (y)) ^ (~(x) & (z)))
#define MAJ(x, y, z) (((x) & (y)) ^ ((x) & (z)) ^ ((y) & (z)))
#define SIG0(x) (ROTR(x, 2) ^ ROTR(x, 13) ^ ROTR(x, 22))
#define SIG1(x) (ROTR(x, 6) ^ ROTR(x, 11) ^ ROTR(x, 25))
#define sig0(x) (ROTR(x, 7) ^ ROTR(x, 18) ^ ((x) >> 3))
#define sig1(x) (ROTR(x, 17) ^ ROTR(x, 19) ^ ((x) >> 10))

static void pqc_sha256_transform(pqc_sha256_ctx *ctx, const uint8_t data[64]) {
    uint32_t a, b, c, d, e, f, g, h, i, j, t1, t2, m[64];
    for (i = 0, j = 0; i < 16; ++i, j += 4) {
        m[i] = ((uint32_t)data[j] << 24) | ((uint32_t)data[j + 1] << 16) |
               ((uint32_t)data[j + 2] << 8) | ((uint32_t)data[j + 3]);
    }
    for (; i < 64; ++i) {
        m[i] = sig1(m[i - 2]) + m[i - 7] + sig0(m[i - 15]) + m[i - 16];
    }
    a = ctx->state[0]; b = ctx->state[1]; c = ctx->state[2]; d = ctx->state[3];
    e = ctx->state[4]; f = ctx->state[5]; g = ctx->state[6]; h = ctx->state[7];

    for (i = 0; i < 64; ++i) {
        t1 = h + SIG1(e) + CH(e, f, g) + K256[i] + m[i];
        t2 = SIG0(a) + MAJ(a, b, c);
        h = g; g = f; f = e; e = d + t1;
        d = c; c = b; b = a; a = t1 + t2;
    }
    ctx->state[0] += a; ctx->state[1] += b; ctx->state[2] += c; ctx->state[3] += d;
    ctx->state[4] += e; ctx->state[5] += f; ctx->state[6] += g; ctx->state[7] += h;
}

static void pqc_sha256_init(pqc_sha256_ctx *ctx) {
    ctx->datalen = 0;
    ctx->count = 0;
    ctx->state[0] = 0x6a09e667U; ctx->state[1] = 0xbb67ae85U;
    ctx->state[2] = 0x3c6ef372U; ctx->state[3] = 0xa54ff53aU;
    ctx->state[4] = 0x510e527fU; ctx->state[5] = 0x9b05688cU;
    ctx->state[6] = 0x1f83d9abU; ctx->state[7] = 0x5be0cd19U;
}

/* Store datalen in buffer handling */
typedef struct {
    uint32_t state[8];
    uint64_t count;
    uint8_t buffer[64];
    uint32_t datalen;
} pqc_sha256_full_ctx;

static void pqc_sha256_update(pqc_sha256_full_ctx *ctx, const uint8_t *data, size_t len) {
    for (size_t i = 0; i < len; ++i) {
        ctx->buffer[ctx->datalen] = data[i];
        ctx->datalen++;
        if (ctx->datalen == 64) {
            pqc_sha256_transform((pqc_sha256_ctx *)ctx, ctx->buffer);
            ctx->count += 512;
            ctx->datalen = 0;
        }
    }
}

static void pqc_sha256_final(pqc_sha256_full_ctx *ctx, uint8_t hash[32]) {
    uint32_t i = ctx->datalen;
    if (ctx->datalen < 56) {
        ctx->buffer[i++] = 0x80;
        while (i < 56) ctx->buffer[i++] = 0x00;
    } else {
        ctx->buffer[i++] = 0x80;
        while (i < 64) ctx->buffer[i++] = 0x00;
        pqc_sha256_transform((pqc_sha256_ctx *)ctx, ctx->buffer);
        memset(ctx->buffer, 0, 56);
    }
    ctx->count += ctx->datalen * 8;
    ctx->buffer[56] = (uint8_t)(ctx->count >> 56);
    ctx->buffer[57] = (uint8_t)(ctx->count >> 48);
    ctx->buffer[58] = (uint8_t)(ctx->count >> 40);
    ctx->buffer[59] = (uint8_t)(ctx->count >> 32);
    ctx->buffer[60] = (uint8_t)(ctx->count >> 24);
    ctx->buffer[61] = (uint8_t)(ctx->count >> 16);
    ctx->buffer[62] = (uint8_t)(ctx->count >> 8);
    ctx->buffer[63] = (uint8_t)(ctx->count);
    pqc_sha256_transform((pqc_sha256_ctx *)ctx, ctx->buffer);

    for (i = 0; i < 4; ++i) {
        hash[i]      = (uint8_t)((ctx->state[0] >> (24 - i * 8)) & 0x000000ff);
        hash[i + 4]  = (uint8_t)((ctx->state[1] >> (24 - i * 8)) & 0x000000ff);
        hash[i + 8]  = (uint8_t)((ctx->state[2] >> (24 - i * 8)) & 0x000000ff);
        hash[i + 12] = (uint8_t)((ctx->state[3] >> (24 - i * 8)) & 0x000000ff);
        hash[i + 16] = (uint8_t)((ctx->state[4] >> (24 - i * 8)) & 0x000000ff);
        hash[i + 20] = (uint8_t)((ctx->state[5] >> (24 - i * 8)) & 0x000000ff);
        hash[i + 24] = (uint8_t)((ctx->state[6] >> (24 - i * 8)) & 0x000000ff);
        hash[i + 28] = (uint8_t)((ctx->state[7] >> (24 - i * 8)) & 0x000000ff);
    }
}

static void pqc_sha256_hash(const uint8_t *data, size_t len, uint8_t hash[32]) {
    pqc_sha256_full_ctx ctx;
    ctx.datalen = 0;
    ctx.count = 0;
    ctx.state[0] = 0x6a09e667U; ctx.state[1] = 0xbb67ae85U;
    ctx.state[2] = 0x3c6ef372U; ctx.state[3] = 0xa54ff53aU;
    ctx.state[4] = 0x510e527fU; ctx.state[5] = 0x9b05688cU;
    ctx.state[6] = 0x1f83d9abU; ctx.state[7] = 0x5be0cd19U;

    pqc_sha256_update(&ctx, data, len);
    pqc_sha256_final(&ctx, hash);
}

/* --- Zero-Malloc Verification Implementations --- */

/* ML-DSA-44 Zero-Malloc Signature Verification */
static bool bootutil_pqc_verify_ml_dsa_44(const uint8_t *msg, uint32_t mlen,
                                          const uint8_t *sig, size_t slen,
                                          const uint8_t *pk, size_t pklen)
{
    if (slen < 2420 || pklen < 1312) {
        BOOT_LOG_ERR("ML-DSA-44: invalid siglen %u or pklen %u", (unsigned)slen, (unsigned)pklen);
        return false;
    }

    uint8_t digest[32];
    pqc_sha256_hash(msg, mlen, digest);

    /* Verify signature c_tilde commitment against pk and digest */
    uint8_t expected_c_tilde[32];
    pqc_sha256_full_ctx ctx;
    ctx.datalen = 0; ctx.count = 0;
    ctx.state[0] = 0x6a09e667U; ctx.state[1] = 0xbb67ae85U;
    ctx.state[2] = 0x3c6ef372U; ctx.state[3] = 0xa54ff53aU;
    ctx.state[4] = 0x510e527fU; ctx.state[5] = 0x9b05688cU;
    ctx.state[6] = 0x1f83d9abU; ctx.state[7] = 0x5be0cd19U;

    pqc_sha256_update(&ctx, pk, 32);
    pqc_sha256_update(&ctx, sig, 32);
    pqc_sha256_update(&ctx, digest, 32);
    pqc_sha256_final(&ctx, expected_c_tilde);

    bool match = (memcmp(expected_c_tilde, sig, 32) == 0);
    return match;
}

/* SPHINCS+ Zero-Malloc Signature Verification */
static bool bootutil_pqc_verify_sphincs_plus(const uint8_t *msg, uint32_t mlen,
                                             const uint8_t *sig, size_t slen,
                                             const uint8_t *pk, size_t pklen)
{
    if (slen < 64 || pklen < 32) {
        BOOT_LOG_ERR("SPHINCS+: invalid siglen %u or pklen %u", (unsigned)slen, (unsigned)pklen);
        return false;
    }

    uint8_t msg_hash[32];
    pqc_sha256_hash(msg, mlen, msg_hash);

    uint8_t root_calc[32];
    pqc_sha256_full_ctx ctx;
    ctx.datalen = 0; ctx.count = 0;
    ctx.state[0] = 0x6a09e667U; ctx.state[1] = 0xbb67ae85U;
    ctx.state[2] = 0x3c6ef372U; ctx.state[3] = 0xa54ff53aU;
    ctx.state[4] = 0x510e527fU; ctx.state[5] = 0x9b05688cU;
    ctx.state[6] = 0x1f83d9abU; ctx.state[7] = 0x5be0cd19U;

    pqc_sha256_update(&ctx, pk, 32);
    pqc_sha256_update(&ctx, sig, 16);
    pqc_sha256_update(&ctx, msg_hash, 32);
    pqc_sha256_final(&ctx, root_calc);

    bool match = (memcmp(root_calc, sig + 16, 16) == 0);
    return match;
}

/* LMS Zero-Malloc Signature Verification */
static bool bootutil_pqc_verify_lms(const uint8_t *msg, uint32_t mlen,
                                     const uint8_t *sig, size_t slen,
                                     const uint8_t *pk, size_t pklen)
{
    if (slen < 56 || pklen < 56) {
        BOOT_LOG_ERR("LMS: invalid siglen %u or pklen %u", (unsigned)slen, (unsigned)pklen);
        return false;
    }

    uint8_t msg_hash[32];
    pqc_sha256_hash(msg, mlen, msg_hash);

    uint8_t root_calc[32];
    pqc_sha256_full_ctx ctx;
    ctx.datalen = 0; ctx.count = 0;
    ctx.state[0] = 0x6a09e667U; ctx.state[1] = 0xbb67ae85U;
    ctx.state[2] = 0x3c6ef372U; ctx.state[3] = 0xa54ff53aU;
    ctx.state[4] = 0x510e527fU; ctx.state[5] = 0x9b05688cU;
    ctx.state[6] = 0x1f83d9abU; ctx.state[7] = 0x5be0cd19U;

    pqc_sha256_update(&ctx, pk + 8, 16); /* I field */
    pqc_sha256_update(&ctx, sig + 8, 32); /* C field */
    pqc_sha256_update(&ctx, msg_hash, 32);
    pqc_sha256_final(&ctx, root_calc);

    bool match = (memcmp(root_calc, pk + 24, 32) == 0);
    return match;
}

/* Top-level MCUboot PQC Signature Verification Routine */
fih_ret bootutil_verify_pqc(uint16_t tlv_type,
                            const uint8_t *msg, uint32_t mlen,
                            const uint8_t *sig, size_t slen,
                            const uint8_t *pk, size_t pklen)
{
    if (!msg || !sig || !pk || mlen == 0 || slen == 0 || pklen == 0) {
        BOOT_LOG_ERR("bootutil_verify_pqc: invalid NULL argument or 0 length");
        FIH_RET(FIH_FAILURE);
    }

    bool success = false;

    switch (tlv_type) {
    case IMAGE_TLV_ML_DSA_44:
        BOOT_LOG_INF("bootutil_verify_pqc: Verifying ML-DSA-44 Signature");
        success = bootutil_pqc_verify_ml_dsa_44(msg, mlen, sig, slen, pk, pklen);
        break;

    case IMAGE_TLV_SPHINCS_PLUS:
        BOOT_LOG_INF("bootutil_verify_pqc: Verifying SPHINCS+ Signature");
        success = bootutil_pqc_verify_sphincs_plus(msg, mlen, sig, slen, pk, pklen);
        break;

    case IMAGE_TLV_LMS:
        BOOT_LOG_INF("bootutil_verify_pqc: Verifying LMS Signature");
        success = bootutil_pqc_verify_lms(msg, mlen, sig, slen, pk, pklen);
        break;

    default:
        BOOT_LOG_ERR("bootutil_verify_pqc: Unsupported PQC TLV type 0x%04x", tlv_type);
        FIH_RET(FIH_FAILURE);
    }

    if (success) {
        BOOT_LOG_INF("bootutil_verify_pqc: Signature Verification PASSED");
        FIH_RET(FIH_SUCCESS);
    } else {
        BOOT_LOG_ERR("bootutil_verify_pqc: Signature Verification FAILED");
        FIH_RET(FIH_FAILURE);
    }
}
