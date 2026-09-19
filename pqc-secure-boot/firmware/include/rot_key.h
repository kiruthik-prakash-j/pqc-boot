#ifndef ROT_KEY_H
#define ROT_KEY_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define ROT_KEY_ID_PRIMARY 0x00010001U
#define ROT_PUBKEY_HASH_LEN 32

/* Root of Trust key structure */
typedef struct {
    uint32_t key_id;
    uint32_t scheme; /* PQC Scheme ID */
    size_t pubkey_len;
    const uint8_t *pubkey_bytes;
    uint8_t pubkey_hash[ROT_PUBKEY_HASH_LEN];
} rot_key_entry_t;

/* Initialize and retrieve Root of Trust Key */
void rot_key_init(void);
const rot_key_entry_t *rot_key_get(uint32_t key_id);
bool rot_key_verify_hash(uint32_t key_id, const uint8_t *hash_to_check);

/* Expose default provisioned keys for test vectors / verification */
extern const uint8_t g_rot_ml_dsa_pubkey[1312];
extern const uint8_t g_rot_sphincs_pubkey[32];
extern const uint8_t g_rot_lms_pubkey[56];

#ifdef __cplusplus
}
#endif

#endif /* ROT_KEY_H */
