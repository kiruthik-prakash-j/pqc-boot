#ifndef SHAKE256_H
#define SHAKE256_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define SHAKE128_RATE 168
#define SHAKE256_RATE 136
#define KECCAK_STATESIZE 25

typedef struct {
    uint64_t s[KECCAK_STATESIZE];
    uint32_t pos;
    uint32_t rate;
} keccak_ctx;

void keccak_init(keccak_ctx *ctx, uint32_t rate);
void keccak_absorb(keccak_ctx *ctx, const uint8_t *in, size_t inlen);
void keccak_finalize(keccak_ctx *ctx, uint8_t pad_byte);
void keccak_squeeze(keccak_ctx *ctx, uint8_t *out, size_t outlen);

void shake256(const uint8_t *in, size_t inlen, uint8_t *out, size_t outlen);
void shake128(const uint8_t *in, size_t inlen, uint8_t *out, size_t outlen);

#ifdef __cplusplus
}
#endif

#endif /* SHAKE256_H */
