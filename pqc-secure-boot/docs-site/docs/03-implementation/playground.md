---
id: playground
title: PQC Secure Bootloader Playground
sidebar_label: PQC Playground
---

import PqcBootPlayground from '@site/src/components/PqcBootPlayground';

# Interactive PQC Bootloader Verification Simulator

Experience and evaluate the multi-stage post-quantum cryptographic secure boot verification pipeline in real-time. Select PQC algorithm parameters, introduce key mismatch or payload tampering, and simulate the hardware execution pipeline.

<PqcBootPlayground />

## Simulation Overview

The interactive simulator above executes a visual emulation of the hardware verification sequence:

1. **Root of Trust Key Hash Check**: Verifies that the public key provided in the firmware manifest matches the SHA-256 hash burned into immutable OTP eFuse memory.
2. **Firmware Manifest Header Parsing**: Validates header magic bytes (`0x50514342`), anti-rollback security counters, target load address (`0x20000000`), and image metadata.
3. **PQC Signature Validation**: Runs mathematical verification for the selected PQC algorithm family (ML-DSA-44/87, SLH-DSA-128f, LMS).
4. **Payload Hash Match**: Computes SHA-256 digest over the binary payload in Flash and checks equality against the authenticated manifest digest.
