#!/usr/bin/env python3
"""
Tier 2: Boundary & Corner Cases E2E Test Suite
Verifies error handling for corrupted image headers, invalid PQC signatures,
key mismatches, and static memory enforcement (zero dynamic allocation).
"""

import os
import sys
import unittest
import struct
import tempfile
from pathlib import Path

# Add tests directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_harness import (
    get_project_paths,
    PqcBootAuthenticator,
    PqcImageBuilder,
    StaticMemoryAnalyzer,
    ALG_ML_DSA,
    AUTH_SUCCESS
)


class TestTier2BoundaryCorner(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.paths = get_project_paths()
        cls.payload = b"PAYLOAD_DATA_FOR_BOUNDARY_TESTS"

    def test_corrupted_image_header_magic(self):
        """Test rejection when image header has invalid magic value."""
        header, payload, signature = PqcImageBuilder.create_image(
            payload=self.payload,
            alg_id=ALG_ML_DSA
        )
        # Corrupt magic number (change 0x50514342 to 0xDEADBEEF)
        corrupted_header = struct.pack('<I', 0xDEADBEEF) + header[4:]

        with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as tmp:
            tmp.write(corrupted_header + payload)
            tmp_path = Path(tmp.name)

        try:
            res = PqcBootAuthenticator.authenticate_file(tmp_path)
            self.assertNotEqual(res, AUTH_SUCCESS, "Authenticator failed to reject invalid magic header")
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_corrupted_image_header_truncated(self):
        """Test rejection when header is truncated (< sizeof(pqc_image_header_t))."""
        header, payload, signature = PqcImageBuilder.create_image(
            payload=self.payload,
            alg_id=ALG_ML_DSA
        )
        truncated_header = header[:32]

        with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as tmp:
            tmp.write(truncated_header + payload)
            tmp_path = Path(tmp.name)

        try:
            res = PqcBootAuthenticator.authenticate_file(tmp_path)
            self.assertNotEqual(res, AUTH_SUCCESS, "Authenticator failed to reject truncated header")
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_corrupted_image_payload_mismatch(self):
        """Test rejection when payload length does not match header declaration."""
        header, payload, signature = PqcImageBuilder.create_image(
            payload=self.payload,
            alg_id=ALG_ML_DSA
        )
        tampered_payload = payload + b"_EXTRA_BYTES"

        with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as tmp:
            tmp.write(header + tampered_payload)
            tmp_path = Path(tmp.name)

        try:
            res = PqcBootAuthenticator.authenticate_file(tmp_path)
            self.assertNotEqual(res, AUTH_SUCCESS, "Authenticator failed to reject payload length mismatch")
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_invalid_pqc_signature(self):
        """Test rejection when PQC signature payload is tampered/invalid."""
        header, payload, signature = PqcImageBuilder.create_image(
            payload=self.payload,
            alg_id=ALG_ML_DSA
        )
        # Flip bytes in signature field (signature starts at offset 60)
        hdr_ba = bytearray(header)
        for i in range(60, 60 + 2420):
            hdr_ba[i] ^= 0xFF
        corrupted_header = bytes(hdr_ba)

        with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as tmp:
            tmp.write(corrupted_header + payload)
            tmp_path = Path(tmp.name)

        try:
            res = PqcBootAuthenticator.authenticate_file(tmp_path)
            self.assertNotEqual(res, AUTH_SUCCESS, "Authenticator failed to reject invalid signature")
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_public_key_mismatch(self):
        """Test rejection when verifying image against non-matching RoT public key hash."""
        header, payload, signature = PqcImageBuilder.create_image(
            payload=self.payload,
            alg_id=ALG_ML_DSA
        )
        # Corrupt pubkey_hash field in header (offset 24 to 56)
        hdr_ba = bytearray(header)
        for i in range(24, 56):
            hdr_ba[i] ^= 0xFF
        corrupted_header = bytes(hdr_ba)

        with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as tmp:
            tmp.write(corrupted_header + payload)
            tmp_path = Path(tmp.name)

        try:
            res = PqcBootAuthenticator.authenticate_file(tmp_path)
            self.assertNotEqual(res, AUTH_SUCCESS, "Authenticator failed to reject key mismatch")
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_static_memory_enforcement(self):
        """Verify firmware source code contains zero dynamic memory allocation calls."""
        firmware_dir = self.paths['firmware_dir']
        violations = StaticMemoryAnalyzer.scan_directory(firmware_dir)
        self.assertEqual(
            len(violations), 0,
            f"Zero Dynamic Allocation Policy Violated! Found {len(violations)} dynamic memory call(s): {violations}"
        )


if __name__ == '__main__':
    unittest.main()
