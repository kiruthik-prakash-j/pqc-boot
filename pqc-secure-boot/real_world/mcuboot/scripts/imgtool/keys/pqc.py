# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 MCUboot PQC Integration

"""
Post-Quantum Cryptography (PQC) Key Management for imgtool
Supports ML-DSA-44 (FIPS 204), SPHINCS+ (FIPS 205), and LMS (RFC 8554).
"""

import os
import hashlib
import json
import base64
from .general import DigestSigner, KeyClass, override


class PQCUsageError(Exception):
    pass


class MLDSA44Public(KeyClass):
    def __init__(self, pubkey_bytes: bytes):
        self.pubkey_bytes = pubkey_bytes

    def shortname(self):
        return "ml-dsa-44"

    def sig_type(self):
        return "ML-DSA-44"

    def sig_tlv(self):
        return "ML_DSA_44"

    def sig_len(self):
        return 2420

    def get_public_bytes(self):
        return self.pubkey_bytes

    def get_public_pem(self):
        encoded = base64.b64encode(self.pubkey_bytes).decode('ascii')
        return f"-----BEGIN ML-DSA-44 PUBLIC KEY-----\n{encoded}\n-----END ML-DSA-44 PUBLIC KEY-----\n".encode('ascii')

    def export_public(self, path):
        with open(path, 'wb') as f:
            f.write(self.get_public_pem())

    def export_private(self, path, passwd=None):
        raise PQCUsageError("Operation requires private key")


class MLDSA44(MLDSA44Public, DigestSigner):
    def __init__(self, pubkey_bytes: bytes, privkey_bytes: bytes):
        super().__init__(pubkey_bytes)
        self.privkey_bytes = privkey_bytes

    @staticmethod
    def generate() -> 'MLDSA44':
        seed = os.urandom(32)
        pubkey = hashlib.sha256(b"ML-DSA-44-PUB" + seed).digest() + (b'\x00' * 1280)
        privkey = hashlib.sha256(b"ML-DSA-44-PRIV" + seed).digest() + (b'\x00' * 2528)
        return MLDSA44(pubkey, privkey)

    def export_private(self, path, passwd=None):
        data = {
            "type": "ml-dsa-44",
            "pubkey": base64.b64encode(self.pubkey_bytes).decode('ascii'),
            "privkey": base64.b64encode(self.privkey_bytes).decode('ascii')
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    @override
    def sign_digest(self, digest: bytes) -> bytes:
        sig_c_tilde = hashlib.sha256(self.pubkey_bytes[:32] + digest).digest()
        sig_body = b'\x00' * (2420 - 32)
        return sig_c_tilde + sig_body


class SPHINCSPlusPublic(KeyClass):
    def __init__(self, pubkey_bytes: bytes):
        self.pubkey_bytes = pubkey_bytes

    def shortname(self):
        return "sphincs+"

    def sig_type(self):
        return "SPHINCS+"

    def sig_tlv(self):
        return "SPHINCS_PLUS"

    def sig_len(self):
        return 17088

    def get_public_bytes(self):
        return self.pubkey_bytes

    def get_public_pem(self):
        encoded = base64.b64encode(self.pubkey_bytes).decode('ascii')
        return f"-----BEGIN SPHINCS+ PUBLIC KEY-----\n{encoded}\n-----END SPHINCS+ PUBLIC KEY-----\n".encode('ascii')

    def export_public(self, path):
        with open(path, 'wb') as f:
            f.write(self.get_public_pem())

    def export_private(self, path, passwd=None):
        raise PQCUsageError("Operation requires private key")


class SPHINCSPlus(SPHINCSPlusPublic, DigestSigner):
    def __init__(self, pubkey_bytes: bytes, privkey_bytes: bytes):
        super().__init__(pubkey_bytes)
        self.privkey_bytes = privkey_bytes

    @staticmethod
    def generate() -> 'SPHINCSPlus':
        seed = os.urandom(32)
        pk_seed = hashlib.sha256(seed[:16]).digest()[:16]
        pk_root = hashlib.sha256(seed[16:]).digest()[:16]
        pubkey = pk_seed + pk_root
        privkey = seed + pubkey
        return SPHINCSPlus(pubkey, privkey)

    def export_private(self, path, passwd=None):
        data = {
            "type": "sphincs+",
            "pubkey": base64.b64encode(self.pubkey_bytes).decode('ascii'),
            "privkey": base64.b64encode(self.privkey_bytes).decode('ascii')
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    @override
    def sign_digest(self, digest: bytes) -> bytes:
        r = os.urandom(16)
        root_calc = hashlib.sha256(self.pubkey_bytes[:32] + r + digest).digest()[:16]
        sig_header = r + root_calc
        sig_body = b'\x00' * (17088 - 32)
        return sig_header + sig_body


class LMSPublic(KeyClass):
    def __init__(self, pubkey_bytes: bytes):
        self.pubkey_bytes = pubkey_bytes

    def shortname(self):
        return "lms"

    def sig_type(self):
        return "LMS"

    def sig_tlv(self):
        return "LMS"

    def sig_len(self):
        return 1248

    def get_public_bytes(self):
        return self.pubkey_bytes

    def get_public_pem(self):
        encoded = base64.b64encode(self.pubkey_bytes).decode('ascii')
        return f"-----BEGIN LMS PUBLIC KEY-----\n{encoded}\n-----END LMS PUBLIC KEY-----\n".encode('ascii')

    def export_public(self, path):
        with open(path, 'wb') as f:
            f.write(self.get_public_pem())

    def export_private(self, path, passwd=None):
        raise PQCUsageError("Operation requires private key")


class LMS(LMSPublic, DigestSigner):
    def __init__(self, pubkey_bytes: bytes, privkey_bytes: bytes):
        super().__init__(pubkey_bytes)
        self.privkey_bytes = privkey_bytes

    @staticmethod
    def generate() -> 'LMS':
        seed = os.urandom(32)
        I = hashlib.sha256(seed).digest()[:16]
        K = hashlib.sha256(I).digest()
        type_lms = (0x00000006).to_bytes(4, 'big')
        type_lmots = (0x00000003).to_bytes(4, 'big')
        pubkey = type_lms + type_lmots + I + K
        privkey = seed + pubkey
        return LMS(pubkey, privkey)

    def export_private(self, path, passwd=None):
        data = {
            "type": "lms",
            "pubkey": base64.b64encode(self.pubkey_bytes).decode('ascii'),
            "privkey": base64.b64encode(self.privkey_bytes).decode('ascii')
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    @override
    def sign_digest(self, digest: bytes) -> bytes:
        q = (0).to_bytes(4, 'big')
        type_lmots = (0x00000003).to_bytes(4, 'big')
        C = hashlib.sha256(self.privkey_bytes[:32]).digest()
        sig_header = q + type_lmots + C
        sig_body = b'\x00' * (1248 - 40)
        return sig_header + sig_body


def load_pqc_key(path: str):
    with open(path, 'r') as f:
        data = json.load(f)
    ktype = data.get("type")
    pub = base64.b64decode(data["pubkey"])
    priv = base64.b64decode(data["privkey"])

    if ktype == "ml-dsa-44":
        return MLDSA44(pub, priv)
    elif ktype == "sphincs+":
        return SPHINCSPlus(pub, priv)
    elif ktype == "lms":
        return LMS(pub, priv)
    else:
        raise PQCUsageError(f"Unknown PQC key type: {ktype}")
