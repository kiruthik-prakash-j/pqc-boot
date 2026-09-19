/* SPDX-License-Identifier: GPL-2.0+ */
/*
 * Post-Quantum Cryptography (PQC) FIT Image Header
 * Supports ML-DSA-44, SPHINCS+, and LMS algorithms.
 */

#ifndef __PQC_FIT_H
#define __PQC_FIT_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifndef uint
typedef unsigned int uint;
#endif

#ifndef IMAGE_SIGN_INFO_DEFINED
#define IMAGE_SIGN_INFO_DEFINED

struct image_region {
	const void *data;
	int size;
};

struct checksum_algo {
	const char *name;
	int checksum_len;
	int der_len;
	const uint8_t *der_prefix;
	int (*calculate)(const char *name, const struct image_region region[],
			 int region_count, uint8_t *checksum);
};

struct padding_algo;
struct crypto_algo;

struct image_sign_info {
	const char *keydir;
	const char *keyname;
	const char *keyfile;
	const void *fit;
	int node_offset;
	const char *name;
	struct checksum_algo *checksum;
	struct padding_algo *padding;
	struct crypto_algo *crypto;
	const void *fdt_blob;
	int required_keynode;
	const char *require_keys;
	const char *engine_id;
	const void *key;
	int keylen;
};
#endif

#ifndef ML_DSA_44_PUBKEY_BYTES
#define ML_DSA_44_PUBKEY_BYTES    1312
#endif

#ifndef SPHINCS_PLUS_PUBKEY_BYTES
#define SPHINCS_PLUS_PUBKEY_BYTES 64
#endif

#ifndef LMS_PUBKEY_BYTES
#define LMS_PUBKEY_BYTES          56
#endif

#define ML_DSA_44_SIG_BYTES      2420
#define SPHINCS_PLUS_SIG_BYTES  17088
#define LMS_SIG_BYTES            2800

int pqc_fit_sign_mldsa44(struct image_sign_info *info,
			 const struct image_region region[],
			 int region_count, uint8_t **sigp, uint *sig_len);

int pqc_fit_sign_sphincs(struct image_sign_info *info,
			 const struct image_region region[],
			 int region_count, uint8_t **sigp, uint *sig_len);

int pqc_fit_sign_lms(struct image_sign_info *info,
		     const struct image_region region[],
		     int region_count, uint8_t **sigp, uint *sig_len);

int pqc_fit_verify_mldsa44(struct image_sign_info *info,
			   const struct image_region region[],
			   int region_count, uint8_t *sig, uint sig_len);

int pqc_fit_verify_sphincs(struct image_sign_info *info,
			   const struct image_region region[],
			   int region_count, uint8_t *sig, uint sig_len);

int pqc_fit_verify_lms(struct image_sign_info *info,
		       const struct image_region region[],
		       int region_count, uint8_t *sig, uint sig_len);

int pqc_add_verify_data(struct image_sign_info *info, void *keydest);

#endif /* __PQC_FIT_H */
