#ifndef PQC_CRYPTO_H
#define PQC_CRYPTO_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#include "sha256.h"
#include "shake256.h"
#include "ml_dsa.h"
#include "sphincs_plus.h"
#include "lms.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    PQC_SCHEME_UNKNOWN = 0,
    PQC_SCHEME_ML_DSA = 1,      /* Module-Lattice Digital Signature (FIPS 204) */
    PQC_SCHEME_SPHINCS_PLUS = 2,/* SPHINCS+ Hash-based Signature (FIPS 205) */
    PQC_SCHEME_LMS = 3          /* Leighton-Micali Signature (RFC 8554) */
} pqc_scheme_t;

#define PQC_MAX_PUBKEY_SIZE 2048
#define PQC_MAX_SIG_SIZE    18000

/* Zero dynamic allocation static assert */
#if defined(__STDC_VERSION__) && __STDC_VERSION__ >= 201112L
_Static_assert(PQC_MAX_SIG_SIZE <= 32768, "PQC Signature buffer size within static budget");
#endif

/* Top-level PQC signature verification engine */
bool pqc_crypto_verify_signature(pqc_scheme_t scheme,
                                 const uint8_t *pubkey, size_t pubkey_len,
                                 const uint8_t *payload, size_t payload_len,
                                 const uint8_t *sig, size_t sig_len);

const char *pqc_crypto_scheme_name(pqc_scheme_t scheme);

#ifdef __cplusplus
}
#endif

#endif /* PQC_CRYPTO_H */
