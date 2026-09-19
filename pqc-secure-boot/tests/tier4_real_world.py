#!/usr/bin/env python3
"""
Tier 4: Real-World Scenarios E2E Test Suite
Simulates end-to-end operational scenarios:
1. Boot halt simulation when firmware binary or signature is tampered.
2. Boot success simulation when firmware binary and signature match RoT key.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add tests directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_harness import (
    get_project_paths,
    PqcBootAuthenticator,
    PqcImageBuilder,
    ALG_ML_DSA,
    ALG_SPHINCS,
    ALG_LMS,
    AUTH_SUCCESS
)


class TestTier4RealWorldScenarios(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.paths = get_project_paths()
        cls.firmware_code = b"\x7fELF\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00" + b"REAL_WORLD_BARE_METAL_FIRMWARE_PAYLOAD"

    def test_valid_signed_firmware_boot_success_simulation(self):
        """Simulate loading a valid signed firmware image across all supported algorithms."""
        algorithms = [
            ("ML-DSA", ALG_ML_DSA),
            ("SPHINCS+", ALG_SPHINCS),
            ("LMS", ALG_LMS)
        ]

        for alg_name, alg_id in algorithms:
            with self.subTest(algorithm=alg_name):
                header, payload, signature = PqcImageBuilder.create_image(
                    payload=self.firmware_code,
                    alg_id=alg_id
                )

                with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as tmp:
                    tmp.write(header + payload)
                    tmp_path = Path(tmp.name)

                try:
                    auth_result = PqcBootAuthenticator.authenticate_file(tmp_path)
                    self.assertEqual(auth_result, AUTH_SUCCESS, f"Valid boot failed for algorithm {alg_name} with status {auth_result}")
                finally:
                    if tmp_path.exists():
                        tmp_path.unlink()

    def test_tampered_firmware_boot_halt_simulation(self):
        """Simulate loading a tampered firmware image where a single byte of payload is altered."""
        header, payload, signature = PqcImageBuilder.create_image(
            payload=self.firmware_code,
            alg_id=ALG_ML_DSA
        )

        # Alter a single byte in firmware payload (simulating flash corruption or malicious injection)
        tampered_payload = bytearray(payload)
        tampered_payload[10] ^= 0xFF
        tampered_payload = bytes(tampered_payload)

        with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as tmp:
            tmp.write(header + tampered_payload)
            tmp_path = Path(tmp.name)

        try:
            auth_result = PqcBootAuthenticator.authenticate_file(tmp_path)
            self.assertNotEqual(
                auth_result, AUTH_SUCCESS,
                "Security Failure: Bootloader accepted tampered firmware image!"
            )
        finally:
            if tmp_path.exists():
                tmp_path.unlink()


if __name__ == '__main__':
    unittest.main()
