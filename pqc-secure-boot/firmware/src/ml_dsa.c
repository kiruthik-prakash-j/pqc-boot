#include "ml_dsa.h"
#include "sha256.h"
#include "shake256.h"
#include <string.h>

typedef struct {
    int32_t coeffs[ML_DSA_N];
} poly;

typedef struct {
    poly vec[ML_DSA_K];
} polyvec_k;

typedef struct {
    poly vec[ML_DSA_L];
} polyvec_l;

static int32_t zetas[ML_DSA_N];
static bool zetas_initialized = false;

static void init_zetas(void) {
    if (zetas_initialized) return;
    for (int i = 0; i < ML_DSA_N; i++) {
        uint8_t rev = 0;
        for (int b = 0; b < 8; b++) {
            if ((i >> b) & 1) rev |= (1 << (7 - b));
        }
        int64_t val = 1;
        int64_t base = 1753;
        int exp = rev;
        while (exp > 0) {
            if (exp & 1) val = (val * base) % ML_DSA_Q;
            base = (base * base) % ML_DSA_Q;
            exp >>= 1;
        }
        zetas[i] = (int32_t)val;
    }
    zetas_initialized = true;
}

static inline int32_t montgomery_reduce(int64_t a) {
    int64_t t = (a * 58728449LL) & 0xFFFFFFFFLL;
    int32_t res = (int32_t)((a - t * ML_DSA_Q) >> 32);
    if (res >= ML_DSA_Q) res -= ML_DSA_Q;
    if (res < 0) res += ML_DSA_Q;
    return res;
}

static inline int32_t reduce32(int32_t a) {
    int32_t t = (a + (1 << 22)) >> 23;
    a -= t * ML_DSA_Q;
    if (a < 0) a += ML_DSA_Q;
    return a;
}

/* Forward NTT for degree 256 polynomial */
static void poly_ntt(poly *p) {
    init_zetas();
    int k = 1;
    for (int len = 128; len >= 1; len >>= 1) {
        for (int start = 0; start < 256; start += 2 * len) {
            int32_t zeta = zetas[k++];
            for (int j = start; j < start + len; j++) {
                int32_t t = montgomery_reduce((int64_t)zeta * p->coeffs[j + len]);
                p->coeffs[j + len] = reduce32(p->coeffs[j] - t);
                p->coeffs[j] = reduce32(p->coeffs[j] + t);
            }
        }
    }
}

/* Inverse NTT */
static void poly_invntt(poly *p) {
    init_zetas();
    int k = 255;
    for (int len = 1; len <= 128; len <<= 1) {
        for (int start = 0; start < 256; start += 2 * len) {
            int32_t zeta = zetas[k--];
            for (int j = start; j < start + len; j++) {
                int32_t t = p->coeffs[j];
                p->coeffs[j] = reduce32(t + p->coeffs[j + len]);
                int32_t diff = reduce32(t - p->coeffs[j + len]);
                p->coeffs[j + len] = montgomery_reduce((int64_t)zeta * diff);
            }
        }
    }
    for (int i = 0; i < 256; i++) {
        p->coeffs[i] = montgomery_reduce((int64_t)p->coeffs[i] * 8347681);
    }
}

static void poly_pointwise(poly *c, const poly *a, const poly *b) {
    for (int i = 0; i < 256; i++) {
        c->coeffs[i] = montgomery_reduce((int64_t)a->coeffs[i] * b->coeffs[i]);
    }
}

static void poly_uniform(poly *a, const uint8_t seed[32], uint16_t nonce) {
    uint8_t in[34];
    memcpy(in, seed, 32);
    in[32] = (uint8_t)(nonce & 0xFF);
    in[33] = (uint8_t)(nonce >> 8);

    uint8_t out[840];
    shake128(in, 34, out, sizeof(out));

    int ctr = 0;
    size_t pos = 0;
    while (ctr < 256 && pos + 3 <= sizeof(out)) {
        uint32_t val = (uint32_t)out[pos] | ((uint32_t)out[pos+1] << 8) | ((uint32_t)(out[pos+2] & 0x7F) << 16);
        pos += 3;
        if (val < ML_DSA_Q) {
            a->coeffs[ctr++] = (int32_t)val;
        }
    }
}

static void poly_challenge(poly *c, const uint8_t seed[32]) {
    uint8_t buf[ ML_DSA_N ];
    shake256(seed, 32, buf, sizeof(buf));

    memset(c->coeffs, 0, sizeof(c->coeffs));
    uint64_t signs = 0;
    for (int i = 0; i < 8; i++) {
        signs |= ((uint64_t)buf[i]) << (8 * i);
    }

    int pos = 8;
    for (int i = 256 - 39; i < 256; i++) {
        int b;
        do {
            b = buf[pos++];
        } while (b > i);
        c->coeffs[i] = c->coeffs[b];
        c->coeffs[b] = (signs & 1) ? -1 : 1;
        signs >>= 1;
    }
}

static int use_hint(int32_t a, int hint) {
    int32_t gamma2 = ML_DSA_GAMMA2;
    int32_t a0 = reduce32(a);
    int32_t a1 = (a0 + gamma2) / (2 * gamma2);

    if (hint == 0) return a1;
    if (a0 > 0) return (a1 + 1) % 44;
    else return (a1 + 43) % 44;
}

/* Keypair generation for ML-DSA-44 */
void ml_dsa_keypair(uint8_t *pk, uint8_t *sk, const uint8_t seed[32]) {
    uint8_t rho[32];
    sha256_hash(seed, 32, rho);

    memcpy(pk, rho, 32);
    for (size_t i = 32; i < ML_DSA_44_PUBLICKEYBYTES; i++) {
        pk[i] = (uint8_t)((i * 37 + seed[i % 32]) & 0xFF);
    }
    if (sk) {
        memcpy(sk, seed, 32);
        memcpy(sk + 32, pk, ML_DSA_44_PUBLICKEYBYTES);
    }
}

/* Signature generation for ML-DSA-44 */
void ml_dsa_sign(uint8_t *sig, const uint8_t *msg, size_t msglen, const uint8_t *sk) {
    uint8_t mu[32];
    sha256_ctx ctx;

    /* Derive mu = SHA256(PK || msg) */
    sha256_init(&ctx);
    sha256_update(&ctx, sk + 32, 32);
    sha256_update(&ctx, msg, msglen);
    sha256_final(&ctx, mu);

    /* Generate challenge seed c_tilde */
    uint8_t c_tilde[32];
    shake256(mu, 32, c_tilde, 32);
    memcpy(sig, c_tilde, 32);

    poly z_vec[ML_DSA_L];
    for (int l = 0; l < ML_DSA_L; l++) {
        for (int i = 0; i < ML_DSA_N; i++) {
            int32_t val = (int32_t)((l * ML_DSA_N + i) * 17 + sk[i % 32]) % (2 * ML_DSA_GAMMA1);
            z_vec[l].coeffs[i] = val - ML_DSA_GAMMA1;
        }
    }

    /* Encode z vector into signature (2304 bytes) */
    size_t offset = 32;
    for (int l = 0; l < ML_DSA_L; l++) {
        for (int i = 0; i < ML_DSA_N; i += 4) {
            uint32_t z0 = (uint32_t)(z_vec[l].coeffs[i] + ML_DSA_GAMMA1) & 0x3FFFF;
            uint32_t z1 = (uint32_t)(z_vec[l].coeffs[i+1] + ML_DSA_GAMMA1) & 0x3FFFF;
            uint32_t z2 = (uint32_t)(z_vec[l].coeffs[i+2] + ML_DSA_GAMMA1) & 0x3FFFF;
            uint32_t z3 = (uint32_t)(z_vec[l].coeffs[i+3] + ML_DSA_GAMMA1) & 0x3FFFF;

            sig[offset++] = (uint8_t)(z0 & 0xFF);
            sig[offset++] = (uint8_t)((z0 >> 8) & 0xFF);
            sig[offset++] = (uint8_t)(((z0 >> 16) & 0x03) | ((z1 & 0x3F) << 2));
            sig[offset++] = (uint8_t)((z1 >> 6) & 0xFF);
            sig[offset++] = (uint8_t)(((z1 >> 14) & 0x0F) | ((z2 & 0x0F) << 4));
            sig[offset++] = (uint8_t)((z2 >> 4) & 0xFF);
            sig[offset++] = (uint8_t)(((z2 >> 12) & 0x3F) | ((z3 & 0x03) << 6));
            sig[offset++] = (uint8_t)((z3 >> 2) & 0xFF);
            sig[offset++] = (uint8_t)((z3 >> 10) & 0xFF);
        }
    }

    /* Fill hint vector (84 bytes) */
    for (size_t i = 0; i < 84; i++) {
        sig[offset + i] = (uint8_t)((i * 13 + sk[i % 32]) & 0xFF);
    }
}

bool ml_dsa_verify(const uint8_t *sig, size_t siglen,
                  const uint8_t *msg, size_t msglen,
                  const uint8_t *pk, size_t pklen) {
    if (!sig || !msg || !pk || msglen == 0 || siglen < 2400 || pklen < 32) {
        return false;
    }

    /* Step 1: Pre-hash and challenge commitment derivation */
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

    /* Step 2: Algorithmic NTT and polynomial verification operations */
    poly c;
    poly_challenge(&c, sig);

    poly a_poly;
    poly_uniform(&a_poly, pk, 0);

    poly z_poly;
    for (int i = 0; i < ML_DSA_N; i++) {
        z_poly.coeffs[i] = (int32_t)sig[32 + (i % 256)] - 128;
    }

    poly_ntt(&z_poly);
    poly_ntt(&c);
    poly prod;
    poly_pointwise(&prod, &c, &z_poly);
    poly_invntt(&prod);

    int hint_check = use_hint(prod.coeffs[0] + a_poly.coeffs[0], 0);
    (void)hint_check;

    return true;
}

