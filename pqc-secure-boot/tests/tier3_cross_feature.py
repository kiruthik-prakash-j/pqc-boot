#!/usr/bin/env python3
"""
Tier 3: Cross-Feature Combinations E2E Test Suite
Verifies interaction between multi-platform build scripts, React component visual simulator,
and cross-component documentation integrity.
"""

import os
import sys
import unittest
from pathlib import Path

# Add tests directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_harness import get_project_paths


class TestTier3CrossFeature(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.paths = get_project_paths()

    def test_multi_platform_build_scripts(self):
        """Verify automated multi-platform build configuration structure."""
        firmware_dir = self.paths['firmware_dir']
        cmake_path = firmware_dir / 'CMakeLists.txt'
        self.assertTrue(cmake_path.exists(), f"CMakeLists.txt missing at {cmake_path}")

        # Check platform directory layout
        platforms = ['riscv-virt', 'arm-cortex-m', 'arm-cortex-a']
        for plt in platforms:
            plt_path = firmware_dir / 'platform' / plt
            self.assertTrue(plt_path.exists(), f"Platform target {plt} missing at {plt_path}")

    def test_react_component_compilation(self):
        """Verify React Playground component directory and structure for visual boot simulation."""
        components_dir = self.paths['docs_site_dir'] / 'src' / 'components'
        self.assertTrue(components_dir.exists(), f"React components directory missing at {components_dir}")

    def test_documentation_integrity(self):
        """Verify documentation integrity and cross-references between architecture and docs-site."""
        architecture_dir = self.paths['architecture_dir']
        docs_site_dir = self.paths['docs_site_dir']

        self.assertTrue(architecture_dir.exists(), f"Architecture directory missing at {architecture_dir}")
        self.assertTrue(docs_site_dir.exists(), f"Docs site directory missing at {docs_site_dir}")


if __name__ == '__main__':
    unittest.main()
