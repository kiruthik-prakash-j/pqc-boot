#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 EDKII / UEFI PQC Secure Boot Test Suite

import os
import sys
import unittest
import subprocess
from pathlib import Path

class TestUefiPqcSecurityPkg(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.root_dir = Path(__file__).resolve().parent.parent
        cls.edk2_dir = cls.root_dir / "real_world" / "edk2"

    def test_edk2_repo_structure(self):
        """Verify EDKII repository clone and SecurityPkg presence."""
        self.assertTrue(self.edk2_dir.exists(), f"EDKII directory missing at {self.edk2_dir}")
        self.assertTrue((self.edk2_dir / "SecurityPkg").exists(), "SecurityPkg missing in EDKII")
        self.assertTrue((self.edk2_dir / "ArmVirtPkg").exists(), "ArmVirtPkg missing in EDKII")

    def test_pqc_verify_header(self):
        """Verify PqcVerify.h interface and PQC Object Identifiers (OIDs)."""
        header_path = self.edk2_dir / "SecurityPkg" / "Include" / "Library" / "PqcVerify.h"
        self.assertTrue(header_path.exists(), "SecurityPkg/Include/Library/PqcVerify.h missing")

        content = header_path.read_text()
        self.assertIn("OID_ML_DSA_44", content)
        self.assertIn("OID_SPHINCS_PLUS", content)
        self.assertIn("OID_LMS_HASH", content)
        self.assertIn("Pkcs7VerifyPqc", content)

    def test_pkcs7_verify_pqc_c_module(self):
        """Verify Pkcs7VerifyPqc.c implementation in SecurityPkg/Library/DxeImageVerificationLib."""
        c_path = self.edk2_dir / "SecurityPkg" / "Library" / "DxeImageVerificationLib" / "Pkcs7VerifyPqc.c"
        inf_path = self.edk2_dir / "SecurityPkg" / "Library" / "DxeImageVerificationLib" / "DxeImageVerificationLib.inf"

        self.assertTrue(c_path.exists(), "Pkcs7VerifyPqc.c missing")
        self.assertTrue(inf_path.exists(), "DxeImageVerificationLib.inf missing")

        c_content = c_path.read_text()
        inf_content = inf_path.read_text()

        self.assertIn("Pkcs7VerifyPqc", c_content)
        self.assertIn("PqcVerifyDigestCommitment", c_content)
        self.assertIn("Pkcs7VerifyPqc.c", inf_content)

    def test_arm_cortex_a_smp_launcher(self):
        """Verify ARM Cortex-A57 4-Core SMP QEMU launcher script."""
        script_path = self.root_dir / "firmware" / "platform" / "arm-cortex-a" / "run_qemu_cortex_a57_smp.sh"
        self.assertTrue(script_path.exists(), "run_qemu_cortex_a57_smp.sh script missing")
        self.assertTrue(os.access(script_path, os.X_OK), "run_qemu_cortex_a57_smp.sh is not executable")

        res = subprocess.run([str(script_path)], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"SMP launcher failed with output:\n{res.stdout}\n{res.stderr}")
        self.assertIn("ARM Cortex-A57", res.stdout)
        self.assertIn("4-CORE SMP", res.stdout)

if __name__ == "__main__":
    unittest.main()
