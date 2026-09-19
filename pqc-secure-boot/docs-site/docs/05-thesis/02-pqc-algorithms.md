# Chapter 2: Post-Quantum Cryptographic Signature Algorithms

## 2.1 Introduction and Classification

Post-Quantum Cryptography (PQC) encompasses asymmetric cryptographic primitives designed to withstand cryptanalytic attacks executed by both classical and quantum computers. Standardized by the National Institute of Standards and Technology (NIST) and RFC specifications, PQC digital signature algorithms evaluated for secure boot fall into three primary mathematical families:

1. **Stateful Hash-Based Signature Schemes**: LMS (Leighton-Micali Signature, RFC 8554) and XMSS (eXtended Merkle Signature Scheme, RFC 8391 / NIST SP 800-208).
2. **Lattice-Based Signature Schemes**: ML-DSA (Module-Lattice-Based Digital Signature Algorithm / CRYSTALS-Dilithium, NIST FIPS 204).
3. **Stateless Hash-Based Signature Schemes**: SLH-DSA (Stateless Hash-Based Digital Signature Algorithm / SPHINCS+, NIST FIPS 205).

Each algorithm family presents distinct mathematical trade-offs regarding security assumptions, public key footprints, signature sizes, execution latency, and private key management requirements within embedded bootloaders.

---

## 2.2 Stateful Hash-Based Signature Schemes: LMS and XMSS

Stateful hash-based signature schemes build digital signatures exclusively from collision-resistant and preimage-resistant cryptographic hash functions (e.g., SHA-256 or SHAKE256).

### 2.2.1 One-Time Signature Primitives: Winternitz OTS+ (WOTS+)

The core building block of stateful hash-based signatures is the One-Time Signature (OTS) scheme. Standard WOTS+ operates by hashing secret keys in sequential chains.

#### Mathematical Formulation

Let `w` in `(2, 4, 16)` be the Winternitz parameter, specifying the number of bits processed per chain element. For `w = 16`, each digit represents a 4-bit nibble.

1. **Chain Length**:
   - `l1 = ceil((8 * n) / w)`
   - `l2 = floor((floor(log2(l1 * (2^w - 1))) + 1) / w) + 1`
   - `l = l1 + l2`
   - For `n = 32` bytes (SHA-256) and `w = 16`: `l1 = 64`, `l2 = 3`, giving `l = 67` total chains.

2. **Chain Function**:
   Given a secret key element `sk_i`, the chaining function `c^k(x)` applies `k` iterative hashes using a bitmask `K`:
   `c^0(x) = x`, `c^k(x) = H_K(c^{k-1}(x) XOR Delta_k)`

3. **Checksum Calculation**:
   To prevent an attacker from extending hash chains to forge signatures on modified messages, a checksum `C` is computed over the message nibbles:
   `C = sum(2^w - 1 - m_i)`
   The base `2^w` representation of `C` is appended to the message nibbles, creating the full vector `(m_1, ..., m_l1, c_1, ..., c_l2)`.

4. **WOTS+ Signature Verification**:
   Given signature chain ends `sigma_i = c^{m_i}(sk_i)`, the verifier computes the remaining iterations `(2^w - 1 - m_i)` to arrive at the public key chain tops `pk_i`.

```
Secret Key Element sk_i
      |
      v  Chain Iteration 0
    [ H ] -----------------> Message Nibble m_i = 2
      |
      v  Chain Iteration 2 (Signature Value sigma_i)
    [ H ]
      |
      v  Remaining (15 - 2 = 13) Hash Iterations
    [ H ] -> ... -> [ H ] -> Public Key Element pk_i
```

### 2.2.2 Merkle Tree Authentication Paths

To sign multiple messages without publishing `2^H` individual WOTS+ public keys, a binary Merkle tree of height `H` aggregates `2^H` WOTS+ key pairs at its leaves.

- **Leaf Computation**: `L_i = H(WOTS_PK_i)`.
- **Internal Nodes**: `N_{h,j} = H(N_{h-1,2j} || N_{h-1,2j+1})`.
- **Root Node**: The tree root `R` serves as the static, master public key.

An LMS/XMSS signature contains:
1. The leaf index `i` in `[0, 2^H - 1]`.
2. The WOTS+ signature for message `M`.
3. An authentication path consisting of `H` sibling node hashes `(A_0, A_1, ..., A_H-1)` enabling the verifier to recompute the root `R` from the leaf `L_i`.

```
                        Root (Public Key R)
                            /        \
                        N_1,0       N_1,1
                         /   \       /   \
                      L_0     L_1   L_2   L_3  (WOTS+ Public Keys)
```

### 2.2.3 The Stateful Key Dilemma in Firmware Verification

While LMS and XMSS feature exceptionally fast verification speeds (`O(l + H)` hash evaluations) and compact public keys (32 to 64 bytes), they impose strict **statefulness**:

- **Catastrophic Security Degradation**: Reusing a single WOTS+ leaf index `i` to sign two distinct messages exposes internal chain values, enabling an adversary to forge valid signatures for arbitrary payload binaries.
- **Firmware Update Implications**: Firmware signers must maintain persistent, transactional access to non-volatile state (e.g., eFuse counter or secure storage) during build pipelines.
- **Verifier Immunity**: Crucially for secure boot, the **verifier** (Stage-0 ROM / Stage-1 bootloader) operates strictly read-only. The bootloader hashes the incoming image, parses the authentication path, recomputes the Merkle root `R'`, and asserts equality with the hardware eFuse digest. Verifiers do not maintain state, making LMS/XMSS highly attractive for immutable bootloaders.

---

## 2.3 Lattice-Based Signature Schemes: ML-DSA (CRYSTALS-Dilithium)

ML-DSA (standardized in NIST FIPS 204) represents the primary general-purpose post-quantum signature algorithm. ML-DSA relies on the hardness of algebraic lattice problems over module rings.

### 2.3.1 Mathematical Foundations: M-LWE and M-SIS

ML-DSA operates over the polynomial ring `R_q = Z_q[X]/(X^n + 1)`, where:
- Degree parameter `n = 256`.
- Modulus `q = 8,380,417 = 2^23 - 2^13 + 1` (a prime satisfying `q == 1 mod 2n`).

Security relies on two computational lattice problems:
1. **Module Learning With Errors (M-LWE)**: Distinguishing `(A, A*s + e)` from `(A, u)`, where matrix `A` is in `R_q^(k x l)`, and `s, e` are short secret vectors.
2. **Module Short Integer Solution (M-SIS)**: Finding a non-zero short vector `y` such that `A*y = 0 mod q`.

### 2.3.2 Fiat-Shamir with Abort Framework

ML-DSA utilizes the Fiat-Shamir with Abort paradigm. To prevent private key leakage via signature coefficients, the signer selects a random masking vector `y`, computes commitment `w = A*y`, and sets challenge `c = H(w_1 || M)`. If the response `z = y + c*s` contains coefficients exceeding a strict norm bound `gamma_1 - beta`, the signer aborts and retries with a fresh `y`.

```
Signer (Fiat-Shamir with Abort)             Verifier (ML-DSA Verification)
-------------------------------+            -------------------------------
1. Sample random mask vector y |            1. Parse signature (z, h, c)
2. Compute commitment w1 = HighBits(A*y)     2. Reconstruct w1' = UseHint(h, A*z - c*t1 * 2^d)
3. Compute challenge c = H(mu || w1)         3. Verify c == H(mu || w1')
4. Compute z = y + c*s                       4. Check norm ||z||_inf < gamma1 - beta
5. If ||z||_inf >= gamma1 - beta -> ABORT
```

### 2.3.3 Parameter Sets and Dimensions

| Parameter Set | Security Level | Matrix Dim (k x l) | Public Key Size (Bytes) | Signature Size (Bytes) | Modulus q |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ML-DSA-44** | NIST Level 1 (AES-128 equivalent) | 4 x 4 | 1,312 | 2,420 | 8,380,417 |
| **ML-DSA-65** | NIST Level 3 (AES-192 equivalent) | 6 x 5 | 1,952 | 3,309 | 8,380,417 |
| **ML-DSA-87** | NIST Level 5 (AES-256 equivalent) | 8 x 7 | 2,592 | 4,627 | 8,380,417 |

### 2.3.4 Polynomial Multiplication via Number Theoretic Transform (NTT)

Polynomial multiplication in `R_q` represents the dominant computational bottleneck during verification (`A * z`). Direct `O(n^2)` multiplication requires 65,536 operations per polynomial pair.

ML-DSA utilizes the Number Theoretic Transform (NTT), the finite field analog of the Discrete Fourier Transform (DFT). Since `q == 1 mod 512`, `R_q` contains Primitive 512th roots of unity gamma.

1. **Forward NTT**: Converts a polynomial `p(X)` in `R_q` into point-value representation `p_hat = NTT(p)` in `O(n log n)` time (1,024 multiplications).
2. **Pointwise Multiplication**: `c_hat_i = a_hat_i * z_hat_i mod q` (`O(n)` complexity).
3. **Inverse NTT (NTT^-1)**: Converts result back to coefficient form.

Verification latency on embedded microcontrollers is heavily dictated by NTT acceleration (using vector extensions or optimized assembly instructions).

---

## 2.4 Stateless Hash-Based Signature Schemes: SLH-DSA (SPHINCS+)

SLH-DSA (NIST FIPS 205) eliminates state management vulnerabilities by combining multiple cryptographic hash structures into a stateless hierarchy.

### 2.4.1 Structural Composition: FORS and Hypertree

SLH-DSA relies on three layered components:

```
                            [ Master Public Key PK_root ]
                                          |
                                    +-----------+
                                    | Hypertree | (d layers of Merkle trees)
                                    +-----------+
                                          |
                                  [ Top WOTS+ Tree ]
                                          |
                                    +-----------+
                                    | FORS Tree | (Forest of Random Subtrees)
                                    +-----------+
                                          |
                                   [ Message Digest ]
```

1. **FORS (Forest of Random Subtrees)**: A few-time signature (FTS) scheme. Message hash bits select leaves across `k` independent binary trees of height `a`. The revealed leaf secret values and authentication paths sign the message digest.
2. **WOTS+ Layer**: Signs the root hashes of the FORS trees.
3. **Hypertree Structure**: A tree of height `h` split into `d` layers of Merkle trees (each of height `h' = h/d`). Each Merkle tree signs the public key of the tree below it, anchoring down to the master public key `PK_root`.

### 2.4.2 Stateless Pseudo-Random Seed Derivation

Instead of storing individual private keys for millions of WOTS+ and FORS leaves, SLH-DSA generates all secret values deterministically using a single master secret seed `SK.seed` combined with unique 32-byte sub-tree address structures (`ADRS`):

`Secret Value = PRF(SK.seed, ADRS)`

Because leaf values are regenerated deterministically on demand, SLH-DSA requires **zero private key state updating**, eliminating state reuse failure modes completely.

### 2.4.3 Parameter Variants and Trade-Offs

SLH-DSA provides two primary optimization profiles:
- **Fast (`-f`)**: Optimizes for lower signing and verification latency by using smaller trees, at the expense of larger signatures.
- **Small (`-s`)**: Optimizes for reduced signature size by increasing tree height and hash iterations, increasing execution latency.

| Parameter Set | Security Level | Hash Function | Public Key (Bytes) | Signature Size (Bytes) | Verification Latency |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SLH-DSA-SHA2-128f** | Level 1 | SHA-256 | 32 | 17,088 | Fast (approx 10x faster than 128s) |
| **SLH-DSA-SHA2-128s** | Level 1 | SHA-256 | 32 | 7,856 | Slow (high hash iteration count) |
| **SLH-DSA-SHA2-256f** | Level 5 | SHA-512 | 64 | 49,856 | Moderate |
| **SLH-DSA-SHAKE-128f**| Level 1 | SHAKE256 | 32 | 17,088 | Fast |

---

## 2.5 Comprehensive Comparative Taxonomy

The following matrix compares all primary post-quantum signature candidates against classical baselines across cryptanalytic, structural, and embedded performance vectors.

| Cryptographic Algorithm | Security Category / Level | Hardness Assumption | Public Key Size (Bytes) | Signature Size (Bytes) | Verifier State Requirement | Verification Complexity | SRAM Impact (Context Buffer) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RSA-2048** (Classical) | 112 bits | Integer Factorization | 256 | 256 | Stateless | O(log e) ModExp | Less than 1 KB |
| **ECDSA P-256** (Classical)| 128 bits | ECDLP | 64 | 64 | Stateless | O(1) Elliptic Point Mult | Less than 1 KB |
| **LMS (SHA256_M32_H10)** | NIST Level 1 / 128-bit | SHA-256 Preimage/Collision | 32 | 1,228 | Stateless (Verifier) | O(l + H) Hash Ops | Less than 2 KB |
| **XMSS (SHA2_10_256)** | NIST Level 1 / 128-bit | SHA-256 Preimage/Collision | 64 | 2,500 | Stateless (Verifier) | O(l + H) Hash Ops | Less than 3 KB |
| **ML-DSA-44** | NIST Level 1 / 128-bit | M-LWE / M-SIS | 1,312 | 2,420 | Stateless | O(k * l * n log n) NTT | approx 4-6 KB |
| **ML-DSA-65** | NIST Level 3 / 192-bit | M-LWE / M-SIS | 1,952 | 3,309 | Stateless | O(k * l * n log n) NTT | approx 8-12 KB |
| **SLH-DSA-SHA2-128f** | NIST Level 1 / 128-bit | SHA-256 Preimage/Collision | 32 | 17,088 | Stateless | O(k * 2^a + d * l) Hash Ops | approx 4 KB |
| **SLH-DSA-SHA2-128s** | NIST Level 1 / 128-bit | SHA-256 Preimage/Collision | 32 | 7,856 | Stateless | O(k * 2^a + d * l) Hash Ops | approx 4 KB |

---

## 2.6 Summary of Trade-Offs for Bootloader Architecture

1. **Stateful Hash-Based (LMS/XMSS)**: Superior fit for immutable Stage-0 ROM. Features a minimal public key footprint (32 bytes), small signature size (1.2–2.5 KB), and simple hash-based verification requiring minimal SRAM. Verifier operation is completely stateless.
2. **Lattice-Based (ML-DSA-65)**: Optimal balance for application-grade bootloaders (Cortex-A / RV64). Sub-millisecond verification latency via NTT acceleration, reasonable signature size (3.3 KB), but requires managing public keys near 2 KB.
3. **Stateless Hash-Based (SLH-DSA)**: Ideal where public key storage in eFuse is severely constrained (32 bytes) and lattice assumptions are eschewed. However, signature footprints (7.8–17 KB) incur significant memory bus overhead during payload loading.
