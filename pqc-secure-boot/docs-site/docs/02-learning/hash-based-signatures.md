# Hash-Based Signatures: LMS and SLH-DSA

## Fundamentals of Hash-Based Signatures

Hash-based digital signatures build authenticity guarantees using only symmetric cryptographic hash functions (such as SHA-256 or SHAKE256).

---

## 1. Winternitz One-Time Signatures (WOTS+)

WOTS+ forms the core building block of hash-based schemes.

- **Private Key**: A sequence of random secret seeds.
- **Public Key**: The ends of iterative hash chains calculated from the secret seeds.
- **Signature**: Intermediate values along the hash chains determined by the message nibbles.
- **Verification**: The verifier completes the hash chains from the signature values to reach the public key chain ends.

```
Secret Seed  ---> [ H ] ---> [ H ] ---> [ H ] (Signature Value) ---> [ H ] ---> [ H ] (Public Key Top)
```

---

## 2. Stateful Hash-Based Signatures (LMS / XMSS)

To sign multiple messages without storing multiple public keys, a binary **Merkle Tree** aggregates $2^H$ WOTS+ key pairs at its leaves.

- **Public Key**: Root of the Merkle Tree.
- **Signature**: Index $i$, WOTS+ signature, and authentication path (sibling hashes up to root).
- **Verifier Role**: The verifier computes the leaf from WOTS+, traverses the authentication path to recompute the root, and compares it with the stored eFuse digest. **The verifier is completely stateless and read-only.**

---

## 3. Stateless Hash-Based Signatures (SLH-DSA)

SLH-DSA (SPHINCS+) eliminates state management during signing by using:
1. **FORS (Forest of Random Subtrees)**: A few-time signature scheme.
2. **Hypertree**: Multiple layers of Merkle trees signing sub-trees.
3. **Deterministic PRF Generation**: All secret values are generated from a master seed and tree address vectors `ADRS`.

Result: **Stateless operation for both signers and verifiers**, at the expense of signature size (17 KB for `SLH-DSA-128f`).
