#include "pqc_boot.h"
#include "platform.h"
#include <string.h>
#include <stdio.h>

pqc_boot_status_t pqc_boot_verify_and_boot(const uint8_t *signed_image_buffer, size_t buffer_size) {
    platform_uart_puts("[PQC-BOOT] Initializing Root of Trust...\r\n");

    if (buffer_size < sizeof(pqc_image_header_t)) {
        platform_uart_puts("[PQC-BOOT] ERROR: Image buffer smaller than header!\r\n");
        return PQC_BOOT_ERR_INVALID_MAGIC;
    }

    const pqc_image_header_t *hdr = (const pqc_image_header_t *)signed_image_buffer;

    if (hdr->magic != PQC_BOOT_MAGIC) {
        platform_uart_puts("[PQC-BOOT] ERROR: Invalid image magic number!\r\n");
        return PQC_BOOT_ERR_INVALID_MAGIC;
    }

    platform_uart_puts("[PQC-BOOT] Target Platform: ");
    platform_uart_puts(platform_get_name());
    platform_uart_puts("\r\n");

    const rot_key_entry_t *rot_key = rot_key_get(hdr->key_id);
    if (!rot_key) {
        platform_uart_puts("[PQC-BOOT] ERROR: Root key ID not found in ROM!\r\n");
        return PQC_BOOT_ERR_KEY_NOT_FOUND;
    }

    if (!rot_key_verify_hash(hdr->key_id, hdr->pubkey_hash)) {
        platform_uart_puts("[PQC-BOOT] ERROR: Root public key hash mismatch!\r\n");
        return PQC_BOOT_ERR_HASH_MISMATCH;
    }

    platform_uart_puts("[PQC-BOOT] Scheme: ");
    platform_uart_puts(pqc_crypto_scheme_name((pqc_scheme_t)hdr->scheme));
    platform_uart_puts("\r\n");

    const uint8_t *payload = signed_image_buffer + sizeof(pqc_image_header_t);
    size_t payload_len = hdr->image_size;

    if (sizeof(pqc_image_header_t) + payload_len != buffer_size) {
        platform_uart_puts("[PQC-BOOT] ERROR: Image payload size mismatch with buffer bounds!\r\n");
        return PQC_BOOT_ERR_INVALID_MAGIC;
    }

    platform_uart_puts("[PQC-BOOT] Running PQC Signature Verification engine...\r\n");

    bool verified = pqc_crypto_verify_signature((pqc_scheme_t)hdr->scheme,
                                               rot_key->pubkey_bytes,
                                               rot_key->pubkey_len,
                                               payload,
                                               payload_len,
                                               hdr->signature,
                                               hdr->sig_len);

    if (!verified) {
        platform_uart_puts("[PQC-BOOT] ERROR: Signature Verification FAILED!\r\n");
        return PQC_BOOT_ERR_SIG_VERIFY_FAILED;
    }

    /* Print specified log outputs per scheme */
    switch ((pqc_scheme_t)hdr->scheme) {
        case PQC_SCHEME_ML_DSA:
            platform_uart_puts("[PQC-BOOT] ML-DSA Signature Verification PASSED\r\n");
            break;
        case PQC_SCHEME_SPHINCS_PLUS:
            platform_uart_puts("[PQC-BOOT] SPHINCS+ Signature Verification PASSED\r\n");
            break;
        case PQC_SCHEME_LMS:
            platform_uart_puts("[PQC-BOOT] LMS Signature Verification PASSED\r\n");
            break;
        default:
            platform_uart_puts("[PQC-BOOT] PQC Signature Verification PASSED\r\n");
            break;
    }

    platform_uart_puts("[PQC-BOOT] Booting payload...\r\n");

    /* Execution handoff to entry point or function payload */
#if defined(__x86_64__) || defined(_M_X64)
    platform_uart_puts("[PQC-BOOT] Host execution: Image authenticated successfully. Handoff to stage-1 simulated.\r\n");
#else
    if (hdr->entry_point != 0 && hdr->entry_point != 0x80000000U) {
        typedef void (*entry_func_t)(void);
        entry_func_t entry = (entry_func_t)(uintptr_t)hdr->entry_point;
        entry();
    }
#endif

    return PQC_BOOT_SUCCESS;
}
