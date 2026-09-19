#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 U-Boot FIT PQC Verification Test Suite

import os
import sys
import unittest
from pathlib import Path

class TestUBootPqcFit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.root_dir = Path(__file__).resolve().parent.parent
        cls.uboot_dir = cls.root_dir / "real_world" / "uboot"

    def test_uboot_repo_presence(self):
        """Verify U-Boot repository clone layout."""
        self.assertTrue(self.uboot_dir.exists(), f"U-Boot directory does not exist at {self.uboot_dir}")
        self.assertTrue((self.uboot_dir / "Makefile").exists(), "U-Boot root Makefile missing")
        self.assertTrue((self.uboot_dir / "boot" / "image-sig.c").exists(), "U-Boot boot/image-sig.c missing")

    def test_pqc_fit_verify_module(self):
        """Verify lib/pqc/pqc-verify.c and include/u-boot/pqc-fit.h."""
        pqc_c = self.uboot_dir / "lib" / "pqc" / "pqc-verify.c"
        pqc_h = self.uboot_dir / "include" / "u-boot" / "pqc-fit.h"
        pqc_mk = self.uboot_dir / "lib" / "pqc" / "Makefile"

        self.assertTrue(pqc_c.exists(), "lib/pqc/pqc-verify.c missing")
        self.assertTrue(pqc_h.exists(), "include/u-boot/pqc-fit.h missing")
        self.assertTrue(pqc_mk.exists(), "lib/pqc/Makefile missing")

        content = pqc_c.read_text()
        self.assertIn('U_BOOT_CRYPTO_ALGO(ml_dsa_44)', content)
        self.assertIn('U_BOOT_CRYPTO_ALGO(sphincs_plus)', content)
        self.assertIn('U_BOOT_CRYPTO_ALGO(lms)', content)
        self.assertIn('pqc_fit_verify', content)

    def test_its_device_tree_format(self):
        """Verify FIT .its specification schema for PQC algorithms."""
        its_template = """/dts-v1/;
/ {
    description = "PQC-Authenticated RISC-V Linux Kernel FIT Image";
    #address-cells = <1>;
    images {
        kernel-1 {
            description = "RISC-V 64 Linux Kernel";
            data = /incbin/("./Image");
            type = "kernel";
            arch = "riscv";
            os = "linux";
            signature-1 {
                algo = "sha256,ml-dsa-44";
                key-name-hint = "rot_pqc_key";
            };
        };
    };
};
"""
        self.assertIn('algo = "sha256,ml-dsa-44";', its_template)
        self.assertIn('key-name-hint = "rot_pqc_key";', its_template)

    def test_qemu_riscv64_config(self):
        """Verify QEMU RISC-V 64 configuration for U-Boot."""
        defconfig = self.uboot_dir / "configs" / "qemu-riscv64_defconfig"
        self.assertTrue(defconfig.exists(), "qemu-riscv64_defconfig missing")

if __name__ == "__main__":
    unittest.main()
