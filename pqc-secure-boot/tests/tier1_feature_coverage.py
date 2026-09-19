#!/usr/bin/env python3
"""
Tier 1: Feature Coverage E2E Test Suite
Verifies target platform configs, PQC signature verification contracts,
Docusaurus site configuration, and academic thesis chapters presence.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add tests directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_harness import get_project_paths, PqcBootAuthenticator, PqcImageBuilder, ALG_ML_DSA, AUTH_SUCCESS


class TestTier1FeatureCoverage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.paths = get_project_paths()

    def test_qemu_platform_targets_configured(self):
        """Verify build system and directory structure for riscv-virt, mps2-an385, and arm-virt."""
        firmware_dir = self.paths['firmware_dir']
        cmake_file = firmware_dir / 'CMakeLists.txt'
        self.assertTrue(cmake_file.exists(), f"CMakeLists.txt missing at {cmake_file}")

        with open(cmake_file, 'r', encoding='utf-8') as f:
            cmake_content = f.read()

        # Verify cmake minimum version and project name
        self.assertIn("cmake_minimum_required", cmake_content)
        self.assertIn("project(PQC_Secure_Boot", cmake_content)

        # Verify platform directories
        platform_dir = firmware_dir / 'platform'
        self.assertTrue(platform_dir.exists(), f"Platform directory missing at {platform_dir}")

        riscv_dir = platform_dir / 'riscv-virt'
        cortex_m_dir = platform_dir / 'arm-cortex-m'
        cortex_a_dir = platform_dir / 'arm-cortex-a'

        self.assertTrue(riscv_dir.exists(), f"riscv-virt platform dir missing at {riscv_dir}")
        self.assertTrue(cortex_m_dir.exists(), f"arm-cortex-m (mps2-an385) platform dir missing at {cortex_m_dir}")
        self.assertTrue(cortex_a_dir.exists(), f"arm-cortex-a (arm-virt) platform dir missing at {cortex_a_dir}")

    def test_pqc_signature_verification_api(self):
        """Verify PQC signature verification contract using compiled C binary host executable."""
        payload = b"BARE_METAL_FIRMWARE_PAYLOAD_IMAGE_DATA_TIER1"

        header, payload_data, signature = PqcImageBuilder.create_image(
            payload=payload,
            alg_id=ALG_ML_DSA
        )

        with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as tmp:
            tmp.write(header + payload_data)
            tmp_path = Path(tmp.name)

        try:
            res = PqcBootAuthenticator.authenticate_file(tmp_path)
            self.assertEqual(res, AUTH_SUCCESS, f"PQC signature verification failed with exit code {res}")
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_docusaurus_config_and_structure(self):
        """Verify Docusaurus site configuration file and documentation layout."""
        docs_site_dir = self.paths['docs_site_dir']
        config_file = docs_site_dir / 'docusaurus.config.js'
        self.assertTrue(config_file.exists(), f"docusaurus.config.js missing at {config_file}")

        with open(config_file, 'r', encoding='utf-8') as f:
            config_content = f.read()

        self.assertIn("PQC Secure Boot Documentation", config_content)
        self.assertIn("preset-classic", config_content)

        docs_dir = docs_site_dir / 'docs'
        required_dirs = ['01-research', '02-learning', '03-implementation', '04-logs', '05-thesis']
        for d in required_dirs:
            sub_dir = docs_dir / d
            self.assertTrue(sub_dir.exists(), f"Documentation directory {d} missing at {sub_dir}")

    def test_thesis_chapters_presence(self):
        """Verify academic thesis directory presence in docs-site/docs/05-thesis."""
        thesis_dir = self.paths['docs_site_dir'] / 'docs' / '05-thesis'
        self.assertTrue(thesis_dir.exists(), f"Thesis directory missing at {thesis_dir}")


if __name__ == '__main__':
    unittest.main()
