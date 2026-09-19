#include "rot_key.h"
#include "sha256.h"
#include "pqc_crypto.h"
#include <string.h>

/* Pre-provisioned Root Public Key bytes for ML-DSA-44 */
const uint8_t g_rot_ml_dsa_pubkey[1312] = {
    0x01, 0x4D, 0x4C, 0x2D, 0x44, 0x53, 0x41, 0x2D, 0x52, 0x4F, 0x54, 0x2D, 0x4B, 0x45, 0x59, 0x30,
    0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x30, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46
};

/* Pre-provisioned Root Public Key bytes for SPHINCS+ */
const uint8_t g_rot_sphincs_pubkey[32] = {
    0x02, 0x53, 0x50, 0x48, 0x49, 0x4E, 0x43, 0x53, 0x2B, 0x2D, 0x52, 0x4F, 0x54, 0x2D, 0x4B, 0x45,
    0x59, 0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x30, 0x41, 0x42, 0x43, 0x44
};

/* Pre-provisioned Root Public Key bytes for LMS */
const uint8_t g_rot_lms_pubkey[56] = {
    0x00, 0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 0x03, 0x4C, 0x4D, 0x53, 0x2D, 0x52, 0x4F, 0x54, 0x2D,
    0x4B, 0x45, 0x59, 0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x30, 0x41, 0x42,
    0x43, 0x44, 0x45, 0x46, 0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x30, 0x41
};

static rot_key_entry_t g_rot_key_table[3];
static bool g_rot_initialized = false;

void rot_key_init(void) {
    if (g_rot_initialized) return;

    /* Entry 0: ML-DSA Primary Key */
    g_rot_key_table[0].key_id = ROT_KEY_ID_PRIMARY;
    g_rot_key_table[0].scheme = PQC_SCHEME_ML_DSA;
    g_rot_key_table[0].pubkey_len = sizeof(g_rot_ml_dsa_pubkey);
    g_rot_key_table[0].pubkey_bytes = g_rot_ml_dsa_pubkey;
    sha256_hash(g_rot_ml_dsa_pubkey, sizeof(g_rot_ml_dsa_pubkey), g_rot_key_table[0].pubkey_hash);

    /* Entry 1: SPHINCS+ Key */
    g_rot_key_table[1].key_id = 0x00010002U;
    g_rot_key_table[1].scheme = PQC_SCHEME_SPHINCS_PLUS;
    g_rot_key_table[1].pubkey_len = sizeof(g_rot_sphincs_pubkey);
    g_rot_key_table[1].pubkey_bytes = g_rot_sphincs_pubkey;
    sha256_hash(g_rot_sphincs_pubkey, sizeof(g_rot_sphincs_pubkey), g_rot_key_table[1].pubkey_hash);

    /* Entry 2: LMS Key */
    g_rot_key_table[2].key_id = 0x00010003U;
    g_rot_key_table[2].scheme = PQC_SCHEME_LMS;
    g_rot_key_table[2].pubkey_len = sizeof(g_rot_lms_pubkey);
    g_rot_key_table[2].pubkey_bytes = g_rot_lms_pubkey;
    sha256_hash(g_rot_lms_pubkey, sizeof(g_rot_lms_pubkey), g_rot_key_table[2].pubkey_hash);

    g_rot_initialized = true;
}

const rot_key_entry_t *rot_key_get(uint32_t key_id) {
    rot_key_init();
    for (size_t i = 0; i < sizeof(g_rot_key_table) / sizeof(g_rot_key_table[0]); i++) {
        if (g_rot_key_table[i].key_id == key_id) {
            return &g_rot_key_table[i];
        }
    }
    return NULL;
}

bool rot_key_verify_hash(uint32_t key_id, const uint8_t *hash_to_check) {
    const rot_key_entry_t *entry = rot_key_get(key_id);
    if (!entry) return false;
    return (memcmp(entry->pubkey_hash, hash_to_check, ROT_PUBKEY_HASH_LEN) == 0);
}
