#ifndef ML_DSA_H
#define ML_DSA_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define ML_DSA_44_PUBLICKEYBYTES 1312
#define ML_DSA_44_SIGNATUREBYTES 2420
#define ML_DSA_44_SECRETKEYBYTES 2560

#define ML_DSA_N 256
#define ML_DSA_Q 8380417
#define ML_DSA_K 4
#define ML_DSA_L 4
#define ML_DSA_D 13
#define ML_DSA_GAMMA1 (1 << 17)
#define ML_DSA_GAMMA2 ((ML_DSA_Q - 1) / 88)
#define ML_DSA_BETA 78

/* Verify ML-DSA-44 signature over msg using pk */
bool ml_dsa_verify(const uint8_t *sig, size_t siglen,
                  const uint8_t *msg, size_t msglen,
                  const uint8_t *pk, size_t pklen);

/* Generate a valid keypair and signature for testing / firmware signing */
void ml_dsa_keypair(uint8_t *pk, uint8_t *sk, const uint8_t seed[32]);
void ml_dsa_sign(uint8_t *sig, const uint8_t *msg, size_t msglen, const uint8_t *sk);

#ifdef __cplusplus
}
#endif

#endif /* ML_DSA_H */
