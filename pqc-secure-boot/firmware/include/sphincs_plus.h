#ifndef SPHINCS_PLUS_H
#define SPHINCS_PLUS_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define SPHINCS_N 16
#define SPHINCS_FULL_HEIGHT 60
#define SPHINCS_D 22
#define SPHINCS_FORS_HEIGHT 6
#define SPHINCS_FORS_TREES 33
#define SPHINCS_WOTS_W 16
#define SPHINCS_WOTS_LEN 35

#define SPHINCS_PK_BYTES (2 * SPHINCS_N)
#define SPHINCS_SK_BYTES (4 * SPHINCS_N)
#define SPHINCS_SIG_BYTES (SPHINCS_N + SPHINCS_FORS_TREES * (SPHINCS_FORS_HEIGHT + 1) * SPHINCS_N + SPHINCS_D * SPHINCS_WOTS_LEN * SPHINCS_N)

/* Verify SPHINCS+ signature over msg using pk */
bool sphincs_plus_verify(const uint8_t *sig, size_t siglen,
                         const uint8_t *msg, size_t msglen,
                         const uint8_t *pk, size_t pklen);

void sphincs_plus_keypair(uint8_t *pk, uint8_t *sk, const uint8_t seed[32]);
void sphincs_plus_sign(uint8_t *sig, const uint8_t *msg, size_t msglen, const uint8_t *sk);

#ifdef __cplusplus
}
#endif

#endif /* SPHINCS_PLUS_H */
