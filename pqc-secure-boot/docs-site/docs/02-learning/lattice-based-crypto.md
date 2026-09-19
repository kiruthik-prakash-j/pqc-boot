# Lattice-Based Cryptography & ML-DSA

## What is a Lattice?

A **lattice** L in R^n is a discrete additive subgroup defined by all integer linear combinations of a set of linearly independent basis vectors `b_1, b_2, ..., b_k`:

```
L = { sum_{i=1}^k z_i * b_i  |  z_i in Z }
```

Hard lattice problems in high dimensions (`n = 256, 512, 1024`) include:
- **Shortest Vector Problem (SVP)**: Find the shortest non-zero vector in L.
- **Closest Vector Problem (CVP)**: Given a point in R^n, find the closest lattice point in L.

---

## Module Ring R_q and ML-DSA

ML-DSA operates over polynomials in the ring:

`R_q = Z_q[X] / (X^256 + 1)`

where `q = 8,380,417`.

### Key Operations during Verification

ML-DSA signature verification involves:
1. Recomputing the matrix-vector polynomial multiplication `A * z mod q`.
2. Applying Number Theoretic Transform (NTT) to reduce polynomial multiplication from `O(n^2)` to `O(n log n)`.
3. Reconstructing the hint bits `h` and checking challenge `c = H(mu || w_1')`.
4. Checking coefficient norm bounds: `||z||_inf < gamma_1 - beta`.

```
Public Key: (seed_A, t1)
Signature:  (c_tilde, z, h)

Verifier Steps:
1. Expand seed_A to matrix A using SHAKE128
2. Compute NTT(z) and NTT(c)
3. Compute w1' = UseHint(h, A * z - c * t1 * 2^d)
4. Verify c_tilde == H(Message || w1')
```
