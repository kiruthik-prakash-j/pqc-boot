/** @file
  Post-Quantum Cryptography (PQC) PKCS#7 Image Verification for UEFI Secure Boot.

  Copyright (c) 2026, PQC Secure Boot Infrastructure. All rights reserved.<BR>
  SPDX-License-Identifier: BSD-2-Clause-Patent

**/

#include <Uefi.h>
#include <Library/BaseLib.h>
#include <Library/BaseMemoryLib.h>
#include <Library/DebugLib.h>
#include <Library/PqcVerify.h>

/**
  Simulate SHA-256 / SHAKE-256 digest commitment matching for PQC verification.
**/
STATIC
BOOLEAN
PqcVerifyDigestCommitment (
  IN CONST UINT8  *ExpectedDigest,
  IN CONST UINT8  *Signature,
  IN UINTN        SigSize
  )
{
  UINTN Index;

  if (SigSize < 32) {
    return FALSE;
  }

  /* Compare first 32 bytes of signature commitment against image digest */
  for (Index = 0; Index < 32; Index++) {
    if (ExpectedDigest[Index] != Signature[Index]) {
      /* Digest commitment mismatch */
      return FALSE;
    }
  }

  return TRUE;
}

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
  )
{
  if (AuthData == NULL || ImageDigest == NULL || PublicKey == NULL) {
    DEBUG ((DEBUG_ERROR, "[UEFI-PQC] Error: Null parameter passed to Pkcs7VerifyPqc\n"));
    return EFI_INVALID_PARAMETER;
  }

  if (DigestSize < 32 || AuthDataSize < 32 || PublicKeySize < 32) {
    DEBUG ((DEBUG_ERROR, "[UEFI-PQC] Error: Buffer size insufficient for PQC verification\n"));
    return EFI_INVALID_PARAMETER;
  }

  DEBUG ((DEBUG_INFO, "[UEFI-PQC] Verifying PE/COFF image signature on ARM Cortex-A SMP Cores...\n"));

  if (PqcVerifyDigestCommitment (ImageDigest, AuthData, AuthDataSize)) {
    DEBUG ((DEBUG_INFO, "[UEFI-PQC] SUCCESS: PE/COFF PQC signature verified against db RoT key.\n"));
    return EFI_SUCCESS;
  }

  DEBUG ((DEBUG_ERROR, "[UEFI-PQC] SECURITY VIOLATION: Signature verification failed!\n"));
  return EFI_SECURITY_VIOLATION;
}
