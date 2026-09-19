#include "shake256.h"
#include <string.h>

static const uint64_t KeccakF_RoundConstants[24] = {
    0x0000000000000001ULL, 0x0000000000008082ULL, 0x800000000000808aULL,
    0x8000000080008000ULL, 0x000000000000808bULL, 0x0000000080000001ULL,
    0x8000000080008081ULL, 0x8000000000008009ULL, 0x000000000000008aULL,
    0x0000000000000088ULL, 0x0000000080008009ULL, 0x000000008000000aULL,
    0x000000008000808bULL, 0x800000000000008bULL, 0x8000000000008089ULL,
    0x8000000000008003ULL, 0x8000000000008002ULL, 0x8000000000000080ULL,
    0x000000000000800aULL, 0x800000008000000aULL, 0x8000000080008081ULL,
    0x8000000000008080ULL, 0x0000000080000001ULL, 0x8000000080008008ULL
};

#define ROL64(x, y) (((x) << (y)) | ((x) >> (64 - (y))))

static void keccakf1600(uint64_t s[25]) {
    int i, round, j;
    uint64_t C[5], D[5], B[25];

    for (round = 0; round < 24; round++) {
        /* Theta */
        C[0] = s[0] ^ s[5] ^ s[10] ^ s[15] ^ s[20];
        C[1] = s[1] ^ s[6] ^ s[11] ^ s[16] ^ s[21];
        C[2] = s[2] ^ s[7] ^ s[12] ^ s[17] ^ s[22];
        C[3] = s[3] ^ s[8] ^ s[13] ^ s[18] ^ s[23];
        C[4] = s[4] ^ s[9] ^ s[14] ^ s[19] ^ s[24];

        D[0] = C[4] ^ ROL64(C[1], 1);
        D[1] = C[0] ^ ROL64(C[2], 1);
        D[2] = C[1] ^ ROL64(C[3], 1);
        D[3] = C[2] ^ ROL64(C[4], 1);
        D[4] = C[3] ^ ROL64(C[0], 1);

        for (i = 0; i < 5; i++) {
            s[i]      ^= D[i];
            s[i + 5]  ^= D[i];
            s[i + 10] ^= D[i];
            s[i + 15] ^= D[i];
            s[i + 20] ^= D[i];
        }

        /* Rho Pi */
        B[0]  = s[0];
        B[1]  = ROL64(s[6], 44);
        B[2]  = ROL64(s[12], 43);
        B[3]  = ROL64(s[18], 21);
        B[4]  = ROL64(s[24], 14);

        B[5]  = ROL64(s[3], 28);
        B[6]  = ROL64(s[9], 20);
        B[7]  = ROL64(s[10], 3);
        B[8]  = ROL64(s[16], 45);
        B[9]  = ROL64(s[22], 61);

        B[10] = ROL64(s[1], 1);
        B[11] = ROL64(s[7], 6);
        B[12] = ROL64(s[13], 25);
        B[13] = ROL64(s[19], 8);
        B[14] = ROL64(s[20], 18);

        B[15] = ROL64(s[4], 27);
        B[16] = ROL64(s[5], 36);
        B[17] = ROL64(s[11], 10);
        B[18] = ROL64(s[17], 15);
        B[19] = ROL64(s[23], 56);

        B[20] = ROL64(s[2], 62);
        B[21] = ROL64(s[8], 55);
        B[22] = ROL64(s[14], 39);
        B[23] = ROL64(s[15], 41);
        B[24] = ROL64(s[21], 2);

        /* Chi */
        for (j = 0; j < 25; j += 5) {
            for (i = 0; i < 5; i++) {
                s[j + i] = B[j + i] ^ ((~B[j + (i + 1) % 5]) & B[j + (i + 2) % 5]);
            }
        }

        /* Iota */
        s[0] ^= KeccakF_RoundConstants[round];
    }
}

void keccak_init(keccak_ctx *ctx, uint32_t rate) {
    memset(ctx->s, 0, sizeof(ctx->s));
    ctx->pos = 0;
    ctx->rate = rate;
}

void keccak_absorb(keccak_ctx *ctx, const uint8_t *in, size_t inlen) {
    size_t i;
    uint8_t *s8 = (uint8_t *)ctx->s;
    for (i = 0; i < inlen; i++) {
        s8[ctx->pos++] ^= in[i];
        if (ctx->pos == ctx->rate) {
            keccakf1600(ctx->s);
            ctx->pos = 0;
        }
    }
}

void keccak_finalize(keccak_ctx *ctx, uint8_t pad_byte) {
    uint8_t *s8 = (uint8_t *)ctx->s;
    s8[ctx->pos] ^= pad_byte;
    s8[ctx->rate - 1] ^= 0x80;
    keccakf1600(ctx->s);
    ctx->pos = 0;
}

void keccak_squeeze(keccak_ctx *ctx, uint8_t *out, size_t outlen) {
    size_t i;
    uint8_t *s8 = (uint8_t *)ctx->s;
    for (i = 0; i < outlen; i++) {
        if (ctx->pos == ctx->rate) {
            keccakf1600(ctx->s);
            ctx->pos = 0;
        }
        out[i] = s8[ctx->pos++];
    }
}

void shake256(const uint8_t *in, size_t inlen, uint8_t *out, size_t outlen) {
    keccak_ctx ctx;
    keccak_init(&ctx, SHAKE256_RATE);
    keccak_absorb(&ctx, in, inlen);
    keccak_finalize(&ctx, 0x1F);
    keccak_squeeze(&ctx, out, outlen);
}

void shake128(const uint8_t *in, size_t inlen, uint8_t *out, size_t outlen) {
    keccak_ctx ctx;
    keccak_init(&ctx, SHAKE128_RATE);
    keccak_absorb(&ctx, in, inlen);
    keccak_finalize(&ctx, 0x1F);
    keccak_squeeze(&ctx, out, outlen);
}
