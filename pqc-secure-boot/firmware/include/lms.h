#ifndef PQC_LMS_H
#define PQC_LMS_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define LMS_TYPE_SHA256_M32_H10 0x00000006U
#define LMOTS_TYPE_SHA256_N32_W4 0x00000003U

#define LMS_I_LEN 16
#define LMS_N 32
#define LMS_P 67
#define LMS_H 10

#define LMS_PUBKEY_BYTES 56
#define LMS_SIG_MAX_BYTES 3000

/* Verify LMS signature over msg using pk */
bool lms_verify(const uint8_t *sig, size_t siglen,
                const uint8_t *msg, size_t msglen,
                const uint8_t *pk, size_t pklen);

void lms_keypair(uint8_t *pk, uint8_t *sk, const uint8_t seed[32]);
void lms_sign(uint8_t *sig, const uint8_t *msg, size_t msglen, const uint8_t *sk);

#ifdef __cplusplus
}
#endif

#endif /* PQC_LMS_H */
