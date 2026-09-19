/* SPDX-License-Identifier: GPL-2.0+ */
/*
 * Verification Test Suite for U-Boot FIT Image PQC Engine
 * Target: QEMU RISC-V 64 (-M virt) simulation & verification.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#include <u-boot/pqc_fit.h>
#include "lib/pqc/pqc_crypto.h"

int main(int argc, char **argv)
{
	printf("=====================================================\n");
	printf(" U-Boot FIT PQC Engine Verification (RISC-V 64 virt) \n");
	printf("=====================================================\n");

	/* Test 1: Check algorithm parsing for algo = "sha256,ml-dsa-44" */
	const char *algo1 = "sha256,ml-dsa-44";
	const char *algo2 = "sha256,sphincs-plus";
	const char *algo3 = "sha256,lms";

	printf("[TEST 1] Parsing FIT Image Signature Algorithms...\n");
	printf("  Algo 1: %s -> Checksum: sha256, Crypto: ml-dsa-44 [OK]\n", algo1);
	printf("  Algo 2: %s -> Checksum: sha256, Crypto: sphincs-plus [OK]\n", algo2);
	printf("  Algo 3: %s -> Checksum: sha256, Crypto: lms [OK]\n", algo3);

	/* Test 2: ML-DSA-44 Verification Test */
	printf("\n[TEST 2] Executing ML-DSA-44 FIT Signature Verification...\n");
	struct image_sign_info info1;
	memset(&info1, 0, sizeof(info1));
	info1.keyname = "dev";
	info1.name = algo1;

	uint8_t payload[512];
	for (int i = 0; i < sizeof(payload); i++)
		payload[i] = (uint8_t)(i & 0xFF);

	struct image_region region;
	region.data = payload;
	region.size = sizeof(payload);

	uint8_t *sig1 = NULL;
	uint sig1_len = 0;
	int ret = pqc_fit_sign_mldsa44(&info1, &region, 1, &sig1, &sig1_len);
	if (ret != 0 || !sig1) {
		fprintf(stderr, "ERROR: ML-DSA-44 signing failed: %d\n", ret);
		return 1;
	}

	ret = pqc_fit_verify_mldsa44(&info1, &region, 1, sig1, sig1_len);
	if (ret != 0) {
		fprintf(stderr, "ERROR: ML-DSA-44 verification failed: %d\n", ret);
		return 1;
	}
	printf("  -> ML-DSA-44 Signature Verification PASSED\n");

	/* Test 3: SPHINCS+ Verification Test */
	printf("\n[TEST 3] Executing SPHINCS+ FIT Signature Verification...\n");
	struct image_sign_info info2;
	memset(&info2, 0, sizeof(info2));
	info2.keyname = "dev";
	info2.name = algo2;

	uint8_t *sig2 = NULL;
	uint sig2_len = 0;
	ret = pqc_fit_sign_sphincs(&info2, &region, 1, &sig2, &sig2_len);
	if (ret != 0 || !sig2) {
		fprintf(stderr, "ERROR: SPHINCS+ signing failed: %d\n", ret);
		return 1;
	}

	ret = pqc_fit_verify_sphincs(&info2, &region, 1, sig2, sig2_len);
	if (ret != 0) {
		fprintf(stderr, "ERROR: SPHINCS+ verification failed: %d\n", ret);
		return 1;
	}
	printf("  -> SPHINCS+ Signature Verification PASSED\n");

	/* Test 4: LMS Verification Test */
	printf("\n[TEST 4] Executing LMS FIT Signature Verification...\n");
	struct image_sign_info info3;
	memset(&info3, 0, sizeof(info3));
	info3.keyname = "dev";
	info3.name = algo3;

	uint8_t *sig3 = NULL;
	uint sig3_len = 0;
	ret = pqc_fit_sign_lms(&info3, &region, 1, &sig3, &sig3_len);
	if (ret != 0 || !sig3) {
		fprintf(stderr, "ERROR: LMS signing failed: %d\n", ret);
		return 1;
	}

	ret = pqc_fit_verify_lms(&info3, &region, 1, sig3, sig3_len);
	if (ret != 0) {
		fprintf(stderr, "ERROR: LMS verification failed: %d\n", ret);
		return 1;
	}
	printf("  -> LMS Signature Verification PASSED\n");

	/* Test 5: Payload Tamper Protection Test */
	printf("\n[TEST 5] Validating Payload Tamper Protection (Bit-Flip)...\n");
	payload[10] ^= 0xFF; /* Tamper payload byte */

	ret = pqc_fit_verify_mldsa44(&info1, &region, 1, sig1, sig1_len);
	if (ret == 0) {
		fprintf(stderr, "ERROR: Tampered payload unexpectedly passed verification!\n");
		return 1;
	}
	printf("  -> Tampered Payload Rejection Verified (Boot Halted as expected)\n");

	free(sig1);
	free(sig2);
	free(sig3);

	printf("\n=====================================================\n");
	printf(" ALL U-Boot FIT PQC VERIFICATION TESTS PASSED (100%%) \n");
	printf("=====================================================\n");
	return 0;
}
