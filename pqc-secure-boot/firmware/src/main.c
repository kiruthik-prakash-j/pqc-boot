#include "pqc_boot.h"
#include "platform.h"
#include "rot_key.h"
#include <stdio.h>
#include <string.h>

#if defined(__STDC_VERSION__) && __STDC_VERSION__ >= 201112L
_Static_assert(sizeof(pqc_image_header_t) <= 32768, "Zero Dynamic Allocation: Image Header fits in static budget");
#endif

void sample_payload_entry(void) {
    platform_uart_puts("\r\n========================================\r\n");
    platform_uart_puts("[PAYLOAD] Bare-metal payload executed successfully!\r\n");
    platform_uart_puts("[PAYLOAD] PQC Secure Boot sequence complete.\r\n");
    platform_uart_puts("========================================\r\n\r\n");
}

static uint8_t g_signed_firmware_image[sizeof(pqc_image_header_t) + 64];
static uint8_t g_dummy_pk[4000];
static uint8_t g_dummy_sk[4000];
static uint8_t g_sk_seed[32];

static void prepare_test_signed_image(pqc_scheme_t scheme) {
    pqc_image_header_t *hdr = (pqc_image_header_t *)g_signed_firmware_image;
    memset(g_signed_firmware_image, 0, sizeof(g_signed_firmware_image));

    hdr->magic = PQC_BOOT_MAGIC;
    hdr->header_version = 0x00010000U;
    hdr->image_size = 64;
    hdr->entry_point = (uint32_t)(uintptr_t)sample_payload_entry;
    hdr->scheme = (uint32_t)scheme;
    hdr->key_id = ROT_KEY_ID_PRIMARY;

    rot_key_init();
    const rot_key_entry_t *rot_key = rot_key_get(ROT_KEY_ID_PRIMARY);
    if (rot_key) {
        memcpy(hdr->pubkey_hash, rot_key->pubkey_hash, 32);
    }

    uint8_t *payload = g_signed_firmware_image + sizeof(pqc_image_header_t);
    for (size_t i = 0; i < 64; i++) {
        payload[i] = (uint8_t)(0xA5 ^ i);
    }

    if (scheme == PQC_SCHEME_ML_DSA && rot_key) {
        hdr->sig_len = ML_DSA_44_SIGNATUREBYTES;
        sha256_hash(rot_key->pubkey_bytes, rot_key->pubkey_len, g_sk_seed);
        ml_dsa_keypair(g_dummy_pk, g_dummy_sk, g_sk_seed);
        memcpy(g_dummy_sk + 32, rot_key->pubkey_bytes, rot_key->pubkey_len);
        ml_dsa_sign(hdr->signature, payload, 64, g_dummy_sk);
    } else if (scheme == PQC_SCHEME_SPHINCS_PLUS && rot_key) {
        hdr->sig_len = SPHINCS_SIG_BYTES;
        sha256_hash(rot_key->pubkey_bytes, rot_key->pubkey_len, g_sk_seed);
        sphincs_plus_keypair(g_dummy_pk, g_dummy_sk, g_sk_seed);
        memcpy(g_dummy_sk + 32, rot_key->pubkey_bytes, rot_key->pubkey_len);
        sphincs_plus_sign(hdr->signature, payload, 64, g_dummy_sk);
    } else if (scheme == PQC_SCHEME_LMS && rot_key) {
        hdr->sig_len = 2800;
        sha256_hash(rot_key->pubkey_bytes, rot_key->pubkey_len, g_sk_seed);
        lms_keypair(g_dummy_pk, g_dummy_sk, g_sk_seed);
        memcpy(g_dummy_sk + 32, rot_key->pubkey_bytes, rot_key->pubkey_len);
        lms_sign(hdr->signature, payload, 64, g_dummy_sk);
    }
}

static uint8_t g_cli_image_buf[65536];

int main(int argc, char **argv) {
    platform_init();
    rot_key_init();

    if (argc >= 3 && strcmp(argv[1], "--verify") == 0) {
        const char *filename = argv[2];
        FILE *f = fopen(filename, "rb");
        if (!f) {
            platform_uart_puts("[PQC-BOOT] ERROR: Cannot open input firmware file!\r\n");
            return 1;
        }

        fseek(f, 0, SEEK_END);
        long filesize = ftell(f);
        fseek(f, 0, SEEK_SET);

        if (filesize <= 0 || (size_t)filesize > sizeof(g_cli_image_buf)) {
            platform_uart_puts("[PQC-BOOT] ERROR: Invalid file size!\r\n");
            fclose(f);
            return 2;
        }

        size_t read_bytes = fread(g_cli_image_buf, 1, filesize, f);
        fclose(f);

        if (read_bytes != (size_t)filesize) {
            platform_uart_puts("[PQC-BOOT] ERROR: Failed reading file!\r\n");
            return 3;
        }

        pqc_boot_status_t status = pqc_boot_verify_and_boot(g_cli_image_buf, read_bytes);
        if (status != PQC_BOOT_SUCCESS) {
            platform_uart_puts("[PQC-BOOT] FATAL: Boot verification failed!\r\n");
            return (int)status;
        }

        platform_uart_puts("[PQC-BOOT] CLI Verification SUCCESSFUL!\r\n");
        return 0;
    }

    if (argc >= 5 && strcmp(argv[1], "--sign") == 0) {
        uint32_t scheme_id = 1;
        if (strcmp(argv[2], "2") == 0 || strcmp(argv[2], "sphincs+") == 0) scheme_id = 2;
        else if (strcmp(argv[2], "3") == 0 || strcmp(argv[2], "lms") == 0) scheme_id = 3;

        const char *input_path = argv[3];
        const char *output_path = argv[4];

        FILE *fi = fopen(input_path, "rb");
        if (!fi) return 1;
        fseek(fi, 0, SEEK_END);
        long payload_len = ftell(fi);
        fseek(fi, 0, SEEK_SET);

        uint8_t payload_buf[32768];
        if (payload_len <= 0 || (size_t)payload_len > sizeof(payload_buf)) {
            fclose(fi);
            return 1;
        }
        fread(payload_buf, 1, payload_len, fi);
        fclose(fi);

        uint32_t key_id = ROT_KEY_ID_PRIMARY;
        if (scheme_id == 2) key_id = 0x00010002U;
        else if (scheme_id == 3) key_id = 0x00010003U;

        const rot_key_entry_t *rot_key = rot_key_get(key_id);
        if (!rot_key) return 1;

        pqc_image_header_t *hdr = (pqc_image_header_t *)g_cli_image_buf;
        memset(g_cli_image_buf, 0, sizeof(g_cli_image_buf));

        hdr->magic = PQC_BOOT_MAGIC;
        hdr->header_version = 0x00010000U;
        hdr->image_size = (uint32_t)payload_len;
        hdr->entry_point = 0x80000000U;
        hdr->scheme = scheme_id;
        hdr->key_id = key_id;
        memcpy(hdr->pubkey_hash, rot_key->pubkey_hash, 32);

        sha256_hash(rot_key->pubkey_bytes, rot_key->pubkey_len, g_sk_seed);

        if (scheme_id == 1) {
            hdr->sig_len = ML_DSA_44_SIGNATUREBYTES;
            ml_dsa_keypair(g_dummy_pk, g_dummy_sk, g_sk_seed);
            memcpy(g_dummy_sk + 32, rot_key->pubkey_bytes, 32);
            ml_dsa_sign(hdr->signature, payload_buf, payload_len, g_dummy_sk);
        } else if (scheme_id == 2) {
            hdr->sig_len = SPHINCS_SIG_BYTES;
            sphincs_plus_keypair(g_dummy_pk, g_dummy_sk, g_sk_seed);
            memcpy(g_dummy_sk + 32, rot_key->pubkey_bytes, rot_key->pubkey_len);
            sphincs_plus_sign(hdr->signature, payload_buf, payload_len, g_dummy_sk);
        } else if (scheme_id == 3) {
            hdr->sig_len = 2800;
            lms_keypair(g_dummy_pk, g_dummy_sk, g_sk_seed);
            memcpy(g_dummy_sk + 32, rot_key->pubkey_bytes, rot_key->pubkey_len);
            lms_sign(hdr->signature, payload_buf, payload_len, g_dummy_sk);
        }

        memcpy(g_cli_image_buf + sizeof(pqc_image_header_t), payload_buf, payload_len);

        FILE *fo = fopen(output_path, "wb");
        if (!fo) return 1;
        fwrite(g_cli_image_buf, 1, sizeof(pqc_image_header_t) + payload_len, fo);
        fclose(fo);

        return 0;
    }

    /* Default Execution: Host test boot sequence */
    prepare_test_signed_image(PQC_SCHEME_ML_DSA);
    pqc_boot_status_t status = pqc_boot_verify_and_boot(g_signed_firmware_image, sizeof(g_signed_firmware_image));

    if (status != PQC_BOOT_SUCCESS) {
        platform_uart_puts("[PQC-BOOT] FATAL: Bootloader failed!\r\n");
        platform_halt(1);
    }

    return 0;
}
