#ifndef PQC_BOOT_H
#define PQC_BOOT_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#include "pqc_crypto.h"
#include "rot_key.h"
#include "platform.h"

#ifdef __cplusplus
extern "C" {
#endif

#define PQC_BOOT_MAGIC 0x50514342U /* "PQCB" */

typedef struct __attribute__((packed)) {
    uint32_t magic;           /* PQC_BOOT_MAGIC */
    uint32_t header_version;  /* 0x00010000 */
    uint32_t image_size;      /* Payload size in bytes */
    uint32_t entry_point;     /* Payload execution start address */
    uint32_t scheme;          /* pqc_scheme_t (ML-DSA=1, SPHINCS+=2, LMS=3) */
    uint32_t key_id;          /* Root of Trust key ID */
    uint8_t  pubkey_hash[32];  /* Hash of Root Public Key */
    uint32_t sig_len;         /* Length of PQC signature */
    uint8_t  signature[PQC_MAX_SIG_SIZE]; /* PQC Signature */
} pqc_image_header_t;

/* Boot result codes */
typedef enum {
    PQC_BOOT_SUCCESS = 0,
    PQC_BOOT_ERR_INVALID_MAGIC = -1,
    PQC_BOOT_ERR_KEY_NOT_FOUND = -2,
    PQC_BOOT_ERR_HASH_MISMATCH = -3,
    PQC_BOOT_ERR_SIG_VERIFY_FAILED = -4,
    PQC_BOOT_ERR_UNSUPPORTED_SCHEME = -5
} pqc_boot_status_t;

/* Zero dynamic memory static assertions */
#if defined(__STDC_VERSION__) && __STDC_VERSION__ >= 201112L
_Static_assert(sizeof(pqc_image_header_t) > 0, "Header size validation");
#endif

/* Secure bootloader initialization and payload execution entry point */
pqc_boot_status_t pqc_boot_verify_and_boot(const uint8_t *signed_image_buffer, size_t buffer_size);

#ifdef __cplusplus
}
#endif

#endif /* PQC_BOOT_H */
