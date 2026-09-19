#include "pqc_crypto.h"
#include "platform.h"
#include <string.h>

const char *pqc_crypto_scheme_name(pqc_scheme_t scheme) {
    switch (scheme) {
        case PQC_SCHEME_ML_DSA:
            return "ML-DSA-44 (NIST FIPS 204)";
        case PQC_SCHEME_SPHINCS_PLUS:
            return "SPHINCS+ (NIST FIPS 205)";
        case PQC_SCHEME_LMS:
            return "LMS / LMOTS (RFC 8554)";
        default:
            return "UNKNOWN";
    }
}

bool pqc_crypto_verify_signature(pqc_scheme_t scheme,
                                 const uint8_t *pubkey, size_t pubkey_len,
                                 const uint8_t *payload, size_t payload_len,
                                 const uint8_t *sig, size_t sig_len) {
    if (!pubkey || !payload || !sig || pubkey_len == 0 || payload_len == 0 || sig_len == 0) {
        platform_uart_puts("[PQC-CRYPTO] ERROR: NULL or 0 length arg\r\n");
        return false;
    }

    switch (scheme) {
        case PQC_SCHEME_ML_DSA:
            return ml_dsa_verify(sig, sig_len, payload, payload_len, pubkey, pubkey_len);
        case PQC_SCHEME_SPHINCS_PLUS:
            return sphincs_plus_verify(sig, sig_len, payload, payload_len, pubkey, pubkey_len);
        case PQC_SCHEME_LMS:
            return lms_verify(sig, sig_len, payload, payload_len, pubkey, pubkey_len);
        default:
            platform_uart_puts("[PQC-CRYPTO] ERROR: Unknown scheme\r\n");
            return false;
    }
}
