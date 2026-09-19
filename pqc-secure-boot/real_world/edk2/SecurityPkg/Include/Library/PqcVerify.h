/** @file
  Post-Quantum Cryptography (PQC) UEFI Secure Boot Verification Interface.

  Copyright (c) 2026, PQC Secure Boot Infrastructure. All rights reserved.<BR>
  SPDX-License-Identifier: BSD-2-Clause-Patent

**/

#ifndef PQC_VERIFY_H_
#define PQC_VERIFY_H_

#include <Uefi.h>
#include <Library/BaseLib.h>

///
/// Object Identifiers (OIDs) for Post-Quantum Cryptography algorithms
///
#define OID_ML_DSA_44     "2.16.840.1.101.3.4.3.17"  ///< NIST FIPS 204 ML-DSA-44
#define OID_SPHINCS_PLUS  "2.16.840.1.101.3.4.3.20"  ///< NIST FIPS 205 SLH-DSA
#define OID_LMS_HASH      "1.2.840.113549.1.9.16.3.17" ///< RFC 8708 / RFC 8554 LMS

///
/// PQC Signature Verification Status Codes
///
typedef enum {
  PqcStatusSuccess = 0,
  PqcStatusInvalidParameter,
  PqcStatusSignatureMismatch,
  PqcStatusUnsupportedAlgorithm,
  PqcStatusBufferTooSmall
} PQC_STATUS;

/**
  Verifies a Post-Quantum Digital Signature over a PE/COFF image digest.

  @param[in]  AuthData       Pointer to PKCS#7 / PQC signed data container.
  @param[in]  AuthDataSize   Size of AuthData buffer in bytes.
  @param[in]  ImageDigest    Pointer to 32-byte SHA-256 image digest.
  @param[in]  DigestSize     Size of ImageDigest (must be 32).
  @param[in]  PublicKey      Pointer to Root-of-Trust PQC public key (`db` entry).
  @param[in]  PublicKeySize  Size of PublicKey buffer in bytes.

  @retval EFI_SUCCESS             Signature is valid and image is authentic.
  @retval EFI_SECURITY_VIOLATION  Signature verification failed or payload tampered.
  @retval EFI_INVALID_PARAMETER   Input pointer is NULL or length is invalid.

**/
EFI_STATUS
EFIAPI
Pkcs7VerifyPqc (
  IN CONST UINT8  *AuthData,
  IN UINTN        AuthDataSize,
  IN CONST UINT8  *ImageDigest,
  IN UINTN        DigestSize,
  IN CONST UINT8  *PublicKey,
  IN UINTN        PublicKeySize
  );

#endif
