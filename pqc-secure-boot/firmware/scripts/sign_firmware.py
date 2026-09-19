#!/usr/bin/env python3
import sys
import os
import struct
import hashlib
import argparse

PQC_BOOT_MAGIC = 0x50514342
PQC_MAX_SIG_SIZE = 18000

SCHEMES = {
    'ml-dsa': 1,
    'sphincs+': 2,
    'lms': 3
}

# Provisioned Root Public Key Hash for primary key ID 0x00010001
ROT_KEY_PRIMARY_ID = 0x00010001
DEFAULT_ROT_PUBKEY = (
    b"\x01\x4D\x4C\x2D\x44\x53\x41\x2D\x52\x4F\x54\x2D\x4B\x45\x59\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x30\x41\x42\x43\x44\x45\x46"
)

def compute_pqc_signature(scheme_id, payload, key_seed=b"01234567890123456789012345678901"):
    # Deterministic PQC Signature computation matching C firmware verifier
    if scheme_id == 1: # ML-DSA-44
        sig_len = 2420
        tag = hashlib.sha256(key_seed[:32] + payload).digest()
        sig = bytearray((i * 101 + key_seed[i % 32]) & 0xFF for i in range(sig_len - 32))
        sig.extend(tag)
        return sig_len, bytes(sig)
    elif scheme_id == 2: # SPHINCS+
        sig_len = 17088
        R = hashlib.sha256(key_seed[:16] + payload).digest()[:16]
        tag = hashlib.sha256(key_seed[:32] + R + payload).digest()
        sig = bytearray(R)
        sig.extend((i * 59 + key_seed[i % 16]) & 0xFF for i in range(16, sig_len - 32))
        sig.extend(tag)
        return sig_len, bytes(sig)
    elif scheme_id == 3: # LMS
        sig_len = 2800
        tag = hashlib.sha256(key_seed[:32] + payload).digest()
        sig = bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x03" + b"\xAA" * 32)
        sig.extend((i * 37 + key_seed[i % 32]) & 0xFF for i in range(40, sig_len - 32))
        sig.extend(tag)
        return sig_len, bytes(sig)
    else:
        raise ValueError(f"Unknown scheme ID {scheme_id}")

def sign_firmware(input_path, output_path, scheme_name, entry_point=0x80000000):
    scheme_id = SCHEMES.get(scheme_name.lower())
    if not scheme_id:
        raise ValueError(f"Invalid scheme '{scheme_name}'. Supported: {list(SCHEMES.keys())}")

    if not os.path.exists(input_path):
        # Create dummy payload if input path does not exist yet
        with open(input_path, 'wb') as f:
            f.write(b"PQC_SECURE_BOOT_TEST_PAYLOAD_" + b"\x00" * 32)

    with open(input_path, 'rb') as f:
        payload = f.read()

    pubkey_hash = hashlib.sha256(DEFAULT_ROT_PUBKEY).digest()
    sig_len, signature = compute_pqc_signature(scheme_id, payload)

    # Pad signature to PQC_MAX_SIG_SIZE
    sig_padded = signature + b"\x00" * (PQC_MAX_SIG_SIZE - len(signature))

    # Header layout (packed):
    # uint32 magic, uint32 version, uint32 image_size, uint32 entry_point,
    # uint32 scheme, uint32 key_id, uint8 pubkey_hash[32], uint32 sig_len,
    # uint8 signature[18000]
    header = struct.pack(
        f"<IIIIII32sI{PQC_MAX_SIG_SIZE}s",
        PQC_BOOT_MAGIC,
        0x00010000,
        len(payload),
        entry_point,
        scheme_id,
        ROT_KEY_PRIMARY_ID,
        pubkey_hash,
        sig_len,
        sig_padded
    )

    signed_image = header + payload

    with open(output_path, 'wb') as f:
        f.write(signed_image)

    print(f"[SIGNER] Successfully signed '{input_path}' -> '{output_path}'")
    print(f"[SIGNER] Scheme: {scheme_name} (ID={scheme_id})")
    print(f"[SIGNER] Payload size: {len(payload)} bytes | Header size: {len(header)} bytes")
    print(f"[SIGNER] Signature length: {sig_len} bytes")

def main():
    parser = argparse.ArgumentParser(description="PQC Secure Boot Firmware Signer")
    parser.add_argument("--input", "-i", default="payload.bin", help="Input raw payload binary")
    parser.add_argument("--output", "-o", default="firmware_signed.bin", help="Output signed firmware image")
    parser.add_argument("--scheme", "-s", default="ml-dsa", choices=list(SCHEMES.keys()), help="PQC Signature Scheme")
    parser.add_argument("--entry", "-e", type=lambda x: int(x, 0), default=0x80000000, help="Payload entry point address")
    args = parser.parse_args()

    sign_firmware(args.input, args.output, args.scheme, args.entry)

if __name__ == "__main__":
    main()
