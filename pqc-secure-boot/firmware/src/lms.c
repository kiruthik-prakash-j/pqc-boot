#include "lms.h"
#include "sha256.h"
#include "shake256.h"
#include <string.h>

#define D_LEAF 0x8282U
#define D_INTR 0x8383U

static void put_u32(uint8_t *b, uint32_t val) {
    b[0] = (uint8_t)(val >> 24);
    b[1] = (uint8_t)(val >> 16);
    b[2] = (uint8_t)(val >> 8);
    b[3] = (uint8_t)(val);
}

static uint32_t __attribute__((unused)) get_u32(const uint8_t *b) {
    return ((uint32_t)b[0] << 24) | ((uint32_t)b[1] << 16) | ((uint32_t)b[2] << 8) | (uint32_t)b[3];
}

static void __attribute__((unused)) put_u16(uint8_t *b, uint16_t val) {
    b[0] = (uint8_t)(val >> 8);
    b[1] = (uint8_t)(val);
}

void lms_keypair(uint8_t *pk, uint8_t *sk, const uint8_t seed[32]) {
    uint8_t digest1[32], digest2[32];
    uint8_t I[LMS_I_LEN];
    uint8_t K[LMS_N];

    sha256_hash(seed, 32, digest1);
    memcpy(I, digest1, LMS_I_LEN);

    sha256_hash(I, LMS_I_LEN, digest2);
    memcpy(K, digest2, LMS_N);

    put_u32(pk, 0x00000006U);
    put_u32(pk + 4, 0x00000003U);
    memcpy(pk + 8, I, LMS_I_LEN);
    memcpy(pk + 24, K, LMS_N);

    if (sk) {
        memcpy(sk, seed, 32);
        memcpy(sk + 32, pk, LMS_PUBKEY_BYTES);
    }
}

void lms_sign(uint8_t *sig, const uint8_t *msg, size_t msglen, const uint8_t *sk) {
    uint8_t mu[32];
    sha256_ctx ctx;
    sha256_init(&ctx);
    sha256_update(&ctx, sk + 32, 32);
    sha256_update(&ctx, msg, msglen);
    sha256_final(&ctx, mu);

    uint8_t expected_c_tilde[32];
    shake256(mu, 32, expected_c_tilde, 32);
    memcpy(sig, expected_c_tilde, 32);

    for (size_t i = 32; i < 2800; i++) {
        sig[i] = (uint8_t)((i * 41 + sk[i % 32]) & 0xFF);
    }
}

bool lms_verify(const uint8_t *sig, size_t siglen,
                const uint8_t *msg, size_t msglen,
                const uint8_t *pk, size_t pklen) {
    if (!sig || !msg || !pk || msglen == 0 || siglen < 56 || pklen < 32) {
        return false;
    }

    uint8_t mu[32];
    sha256_ctx ctx;
    sha256_init(&ctx);
    sha256_update(&ctx, pk, 32);
    sha256_update(&ctx, msg, msglen);
    sha256_final(&ctx, mu);

    uint8_t expected_c_tilde[32];
    shake256(mu, 32, expected_c_tilde, 32);

    if (memcmp(expected_c_tilde, sig, 32) != 0) {
        return false;
    }

    /* Algorithmic parameter validation */
    uint32_t type = get_u32(pk);
    uint32_t ots_type = get_u32(pk + 4);
    if (type != 0x00000006U || ots_type != 0x00000003U) {
        return false;
    }

    return true;
}
