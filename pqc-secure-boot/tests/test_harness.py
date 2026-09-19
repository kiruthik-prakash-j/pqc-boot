#!/usr/bin/env python3
"""
PQC Secure Boot Test Harness
Provides helper classes, PQC firmware header construction, signature generation via native C binary,
and static memory enforcement analysis for E2E tests.
"""

import os
import sys
import re
import struct
import hashlib
import subprocess
import tempfile
from pathlib import Path

# Constants for PQC Image Header (matching pqc_boot.h)
PQC_BOOT_MAGIC = 0x50514342  # "PQCB" in ASCII (0x50514342)
MAGIC_PQC1 = PQC_BOOT_MAGIC  # Alias for backward compatibility

ALG_ML_DSA = 1           # ML-DSA-44 (NIST FIPS 204)
ALG_SPHINCS = 2          # SPHINCS+ (NIST FIPS 205)
ALG_LMS = 3              # LMS/LMOTS (RFC 8554)

ROT_KEY_PRIMARY_ID = 0x00010001
ROT_KEY_SPHINCS_ID = 0x00010002
ROT_KEY_LMS_ID = 0x00010003

PQC_MAX_SIG_SIZE = 18000
HEADER_STRUCT_SIZE = 18060  # 4*6 + 32 + 4 + 18000

# Error Codes for Authentication
AUTH_SUCCESS = 0
ERR_INVALID_MAGIC = 1
ERR_HEADER_TRUNCATED = 2
ERR_PAYLOAD_MISMATCH = 3
ERR_KEY_MISMATCH = 4
ERR_INVALID_SIGNATURE = 5

def get_project_paths():
    """Resolve workspace root and pqc-secure-boot root paths."""
    script_dir = Path(__file__).resolve().parent
    source_root = script_dir.parent
    workspace_root = source_root.parent
    return {
        'workspace_root': workspace_root,
        'source_root': source_root,
        'firmware_dir': source_root / 'firmware',
        'architecture_dir': source_root / 'architecture',
        'docs_site_dir': source_root / 'docs-site',
        'tests_dir': source_root / 'tests'
    }

def ensure_host_binary():
    """Ensure host C binary build/pqc_boot_host is built and up to date."""
    paths = get_project_paths()
    firmware_dir = paths['firmware_dir']
    build_dir = firmware_dir / 'build'
    host_bin = build_dir / 'pqc_boot_host'

    if not host_bin.exists():
        build_dir.mkdir(parents=True, exist_ok=True)
        res1 = subprocess.run(['cmake', '..'], cwd=str(build_dir), capture_output=True, text=True)
        if res1.returncode != 0:
            raise RuntimeError(f"CMake build failed:\n{res1.stderr}")
        res2 = subprocess.run(['make', 'pqc_boot_host'], cwd=str(build_dir), capture_output=True, text=True)
        if res2.returncode != 0:
            raise RuntimeError(f"Make build failed:\n{res2.stderr}")

    return host_bin

class PqcImageBuilder:
    """Utility to build and sign binary firmware images for E2E testing using C host binary."""

    @staticmethod
    def compute_rot_hash(rot_public_key: bytes) -> bytes:
        """Compute SHA-256 hash of RoT Public Key."""
        return hashlib.sha256(rot_public_key).digest()

    @classmethod
    def create_image(cls, payload: bytes, rot_public_key: bytes = None, rot_private_key: bytes = None, alg_id: int = ALG_ML_DSA, version: int = 1):
        """Construct full binary image: Header + Payload + PQC Signature using native C signer."""
        host_bin = ensure_host_binary()

        with tempfile.NamedTemporaryFile(delete=False) as tmp_in, \
             tempfile.NamedTemporaryFile(delete=False) as tmp_out:
            tmp_in_path = tmp_in.name
            tmp_out_path = tmp_out.name
            tmp_in.write(payload)
            tmp_in.flush()
            tmp_in.close()

        try:
            res = subprocess.run([str(host_bin), "--sign", str(alg_id), tmp_in_path, tmp_out_path],
                                 capture_output=True, text=True)
            if res.returncode != 0:
                raise RuntimeError(f"Signer binary failed: {res.stderr}")

            with open(tmp_out_path, 'rb') as f:
                signed_image = f.read()

        finally:
            if os.path.exists(tmp_in_path): os.remove(tmp_in_path)
            if os.path.exists(tmp_out_path): os.remove(tmp_out_path)

        header_len = HEADER_STRUCT_SIZE
        header = signed_image[:header_len]
        payload_data = signed_image[header_len:]
        sig_len = struct.unpack('<I', header[56:60])[0]
        signature = header[60 : 60 + sig_len]

        return header, payload_data, signature


class PqcBootAuthenticator:
    """Invokes compiled C firmware authentication engine (pqc_boot_host --verify)."""

    @classmethod
    def authenticate_file(cls, image_path: Path) -> int:
        """Execute compiled C host binary verification: ./pqc_boot_host --verify <image_file>"""
        host_bin = ensure_host_binary()
        res = subprocess.run([str(host_bin), "--verify", str(image_path)], capture_output=True, text=True)
        return res.returncode

    @classmethod
    def authenticate(cls, header: bytes, payload: bytes, signature: bytes = None, rot_public_key: bytes = None, rot_private_key: bytes = None) -> int:
        """Execute C host binary verification via temp file."""
        full_image = header + payload
        with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
            tmp_file.write(full_image)

        try:
            return cls.authenticate_file(tmp_path)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()


class StaticMemoryAnalyzer:
    """Static code analyzer to enforce Zero Dynamic Memory Allocation policy in firmware."""

    FORBIDDEN_FUNCTIONS = [
        'malloc', 'free', 'calloc', 'realloc', 'alloca',
        'new', 'delete', 'std::make_shared', 'std::make_unique'
    ]

    @classmethod
    def scan_directory(cls, dir_path: Path):
        """Scan C/C++/Assembly source files for dynamic memory allocation calls."""
        violations = []
        pattern = re.compile(r'\b(' + '|'.join(cls.FORBIDDEN_FUNCTIONS) + r')\s*\(')
        new_delete_pattern = re.compile(r'\b(new|delete)\b')

        if not dir_path.exists():
            return violations

        for ext in ['*.c', '*.cpp', '*.cc', '*.h', '*.hpp', '*.S']:
            for file_path in dir_path.rglob(ext):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        stripped = line.strip()
                        if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
                            continue

                        code_part = line.split('//')[0]
                        match = pattern.search(code_part) or new_delete_pattern.search(code_part)
                        if match:
                            violations.append({
                                'file': str(file_path),
                                'line': line_num,
                                'symbol': match.group(0),
                                'content': line.strip()
                            })
        return violations
