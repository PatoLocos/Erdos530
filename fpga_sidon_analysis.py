"""
FPGA-guided Sidon set extraction using PROMETHEUS spectral analysis.

Uses the eigenvalue data from PROMETHEUS and local numpy to:
1. Compute K^{-1} * 1 (inclusion scores from fixed-point analysis)
2. Extract the soft-mode eigenvector (lambda = -2.29)
3. Threshold to get candidate Sidon sets
4. Verify and compare with known bounds
"""
import numpy as np
import json
from itertools import combinations

def build_collision_matrix(N, penalty=0.5):
    """Build the Sidon collision penalty matrix."""
    K = np.zeros((N, N))
    collision_count = 0
    for s in range(2, 2*N - 2):
        pairs = []
        for a in range(max(0, s - (N-1)), min(s, N-1) + 1):
            b = s - a
            if 0 <= b < N and a < b:
                pairs.append((a, b))
        for i in range(len(pairs)):
            for j in range(i+1, len(pairs)):
                a1, b1 = pairs[i]
                a2, b2 = pairs[j]
                K[a1, a2] += penalty
                K[a1, b2] += penalty
                K[b1, a2] += penalty
                K[b1, b2] += penalty
                K[a2, a1] += penalty
                K[b2, a1] += penalty
                K[a2, b1] += penalty
                K[b2, b1] += penalty
                collision_count += 1
    # Gershgorin diagonal dominance
    for i in range(N):
        row_sum = np.sum(np.abs(K[i, :])) - abs(K[i, i])
        K[i, i] = -(row_sum + 1.0)
    return K, collision_count

def verify_sidon(S):
    """Check if S is a Sidon set (all pairwise sums distinct)."""
    S = sorted(S)
    sums = set()
    for i in range(len(S)):
        for j in range(i+1, len(S)):
            s = S[i] + S[j]
            if s in sums:
                return False
            sums.add(s)
    return True

def greedy_sidon(N):
    """Greedy Sidon set construction in {0,...,N-1}."""
    S = [0]
    sums = set()
    for x in range(1, N):
        new_sums = set()
        ok = True
        for s in S:
            pair_sum = x + s
            if pair_sum in sums or pair_sum in new_sums:
                ok = False
                break
            new_sums.add(pair_sum)
        if ok:
            S.append(x)
            sums.update(new_sums)
    return S

# ============================================================
# ANALYSIS FOR N=30
# ============================================================
N = 30
print(f"{'='*60}")
print(f"FPGA-GUIDED SIDON ANALYSIS: N={N}")
print(f"{'='*60}")

K, ncoll = build_collision_matrix(N)
print(f"Collision matrix: {N}x{N}, {ncoll} collisions")

# 1. Eigenvalue decomposition (local verification of PROMETHEUS result)
eigenvalues, eigenvectors = np.linalg.eigh(K)
print(f"\n--- Eigenvalue Spectrum ---")
print(f"lambda_max = {eigenvalues[-1]:.4f} (soft mode)")
print(f"lambda_max-1 = {eigenvalues[-2]:.4f}")
print(f"spectral gap = {eigenvalues[-1] - eigenvalues[-2]:.4f}")
print(f"lambda_min = {eigenvalues[0]:.4f}")
print(f"condition = {abs(eigenvalues[0]/eigenvalues[-1]):.1f}")

# 2. Soft-mode eigenvector (the one with lambda closest to 0)
soft_mode = eigenvectors[:, -1]  # eigenvector for lambda_max
print(f"\n--- Soft Mode Eigenvector ---")
print(f"lambda = {eigenvalues[-1]:.4f}")
print(f"Components (element: value):")
ranked = sorted(range(N), key=lambda i: abs(soft_mode[i]), reverse=True)
for r, i in enumerate(ranked[:15]):
    print(f"  rank {r+1}: element {i:2d} -> {soft_mode[i]:+.6f}")

# 3. Inclusion score: x* = -K^{-1} * 1
K_inv = np.linalg.inv(K)
ones = np.ones(N)
inclusion_scores = -K_inv @ ones  # Fixed point with unit bias
print(f"\n--- Inclusion Scores (x* = -K^{{-1}} * 1) ---")
ranked_scores = sorted(range(N), key=lambda i: inclusion_scores[i], reverse=True)
for r, i in enumerate(ranked_scores):
    marker = " *" if r < 8 else ""
    print(f"  element {i:2d}: score = {inclusion_scores[i]:.6f}{marker}")

# 4. Extract Sidon sets by thresholding
print(f"\n--- Sidon Set Extraction ---")

# Method A: Top-k by inclusion score
for k in range(10, 3, -1):
    candidate = sorted([ranked_scores[i] for i in range(k)])
    if verify_sidon(candidate):
        print(f"Method A (inclusion score, top-{k}): {candidate} -> SIDON ✓")
        break
    else:
        print(f"Method A (inclusion score, top-{k}): {candidate} -> not Sidon")

# Method B: Soft-mode + greedy pruning
# Elements with SAME SIGN in soft mode tend to be compatible
pos_elements = sorted([i for i in range(N) if soft_mode[i] > 0],
                       key=lambda i: soft_mode[i], reverse=True)
neg_elements = sorted([i for i in range(N) if soft_mode[i] < 0],
                       key=lambda i: -soft_mode[i], reverse=True)

print(f"\nSoft mode: {len(pos_elements)} positive, {len(neg_elements)} negative components")

for group_name, group in [("positive-mode", pos_elements), ("negative-mode", neg_elements)]:
    # Greedy Sidon extraction from the group
    S = []
    sums = set()
    for x in group:
        new_sums = set()
        ok = True
        for s in S:
            pair_sum = x + s
            if pair_sum in sums or pair_sum in new_sums:
                ok = False
                break
            new_sums.add(pair_sum)
        if ok:
            S.append(x)
            sums.update(new_sums)
    if verify_sidon(sorted(S)):
        print(f"Method B ({group_name}): {sorted(S)} -> SIDON ✓ (size {len(S)})")

# Method C: Covariance-guided greedy
# Elements with highest K^{-1} diagonal = most "free"
diag_Kinv = np.diag(K_inv)
ranked_free = sorted(range(N), key=lambda i: -diag_Kinv[i])  # most negative = most free
S = []
sums = set()
for x in ranked_free:
    new_sums = set()
    ok = True
    for s in S:
        pair_sum = x + s
        if pair_sum in sums or pair_sum in new_sums:
            ok = False
            break
        new_sums.add(pair_sum)
    if ok:
        S.append(x)
        sums.update(new_sums)
if verify_sidon(sorted(S)):
    print(f"Method C (covariance-free): {sorted(S)} -> SIDON ✓ (size {len(S)})")

# Method D: All eigenvectors with small eigenvalues
# Use the 3 smallest-magnitude eigenvalues' eigenvectors
n_modes = 5
soft_space = eigenvectors[:, -n_modes:]  # last n_modes eigenvectors
# Project each element into the "soft subspace"
projections = np.linalg.norm(soft_space, axis=1)
ranked_proj = sorted(range(N), key=lambda i: projections[i], reverse=True)
S = []
sums = set()
for x in ranked_proj:
    new_sums = set()
    ok = True
    for s in S:
        pair_sum = x + s
        if pair_sum in sums or pair_sum in new_sums:
            ok = False
            break
        new_sums.add(pair_sum)
    if ok:
        S.append(x)
        sums.update(new_sums)
if verify_sidon(sorted(S)):
    print(f"Method D (soft-subspace): {sorted(S)} -> SIDON ✓ (size {len(S)})")

# Reference: greedy baseline
greedy = greedy_sidon(N)
print(f"\nBaseline (greedy): {greedy} -> SIDON (size {len(greedy)})")

# Singer set for comparison (q=5, p=31: {0,1,5,11,13,17} mod 31)
singer_q5 = [i for i in [0, 1, 5, 11, 13, 17] if i < N]
if verify_sidon(singer_q5):
    print(f"Singer (q=5): {singer_q5} -> SIDON (size {len(singer_q5)})")

print(f"\nOptimal F_2({N}) known: ~{int(np.sqrt(N))+1} (theoretical upper bound: {np.sqrt(N)+1:.2f})")

# ============================================================
# ANALYSIS FOR N=50
# ============================================================
print(f"\n{'='*60}")
print(f"FPGA-GUIDED SIDON ANALYSIS: N=50")
print(f"{'='*60}")

N2 = 50
K2, ncoll2 = build_collision_matrix(N2)
print(f"Collision matrix: {N2}x{N2}, {ncoll2} collisions")

eigenvalues2, eigenvectors2 = np.linalg.eigh(K2)
print(f"lambda_max = {eigenvalues2[-1]:.4f} (soft mode)")
print(f"lambda_max-1 = {eigenvalues2[-2]:.4f}")
print(f"spectral gap = {eigenvalues2[-1] - eigenvalues2[-2]:.4f}")

K2_inv = np.linalg.inv(K2)
inclusion_scores2 = -K2_inv @ np.ones(N2)
ranked2 = sorted(range(N2), key=lambda i: inclusion_scores2[i], reverse=True)

# Extract Sidon set
for k in range(12, 5, -1):
    candidate = sorted([ranked2[i] for i in range(k)])
    if verify_sidon(candidate):
        print(f"Inclusion score top-{k}: {candidate} -> SIDON ✓ (size {k})")
        break

# Soft mode extraction
soft2 = eigenvectors2[:, -1]
pos2 = sorted([i for i in range(N2) if soft2[i] > 0], key=lambda i: soft2[i], reverse=True)
neg2 = sorted([i for i in range(N2) if soft2[i] < 0], key=lambda i: -soft2[i], reverse=True)

for name, group in [("positive", pos2), ("negative", neg2)]:
    S = []
    sums = set()
    for x in group:
        new_sums = set()
        ok = True
        for s in S:
            ps = x + s
            if ps in sums or ps in new_sums:
                ok = False
                break
            new_sums.add(ps)
        if ok:
            S.append(x)
            sums.update(new_sums)
    if verify_sidon(sorted(S)):
        print(f"Soft-mode ({name}): {sorted(S)} -> SIDON ✓ (size {len(S)})")

greedy2 = greedy_sidon(N2)
print(f"Greedy baseline: {greedy2} -> size {len(greedy2)}")
print(f"Optimal F_2(50) upper bound: {np.sqrt(50)+1:.2f}")

# ============================================================
# N=100
# ============================================================
print(f"\n{'='*60}")
print(f"FPGA-GUIDED SIDON ANALYSIS: N=100")
print(f"{'='*60}")

N3 = 100
K3, ncoll3 = build_collision_matrix(N3)
print(f"Collision matrix: {N3}x{N3}, {ncoll3} collisions")

eigenvalues3, eigenvectors3 = np.linalg.eigh(K3)
print(f"lambda_max = {eigenvalues3[-1]:.4f} (soft mode)")
print(f"spectral gap = {eigenvalues3[-1] - eigenvalues3[-2]:.4f}")
print(f"condition = {abs(eigenvalues3[0]/eigenvalues3[-1]):.1f}")

K3_inv = np.linalg.inv(K3)
inclusion_scores3 = -K3_inv @ np.ones(N3)
ranked3 = sorted(range(N3), key=lambda i: inclusion_scores3[i], reverse=True)

for k in range(15, 6, -1):
    candidate = sorted([ranked3[i] for i in range(k)])
    if verify_sidon(candidate):
        print(f"Inclusion score top-{k}: {candidate} -> SIDON ✓ (size {k})")
        break

soft3 = eigenvectors3[:, -1]
pos3 = sorted([i for i in range(N3) if soft3[i] > 0], key=lambda i: soft3[i], reverse=True)
S = []
sums = set()
for x in pos3:
    new_sums = set()
    ok = True
    for s in S:
        ps = x + s
        if ps in sums or ps in new_sums:
            ok = False
            break
        new_sums.add(ps)
    if ok:
        S.append(x)
        sums.update(new_sums)
print(f"Soft-mode (positive): {sorted(S)} -> SIDON (size {len(S)})")
assert verify_sidon(sorted(S))

greedy3 = greedy_sidon(N3)
print(f"Greedy baseline: size {len(greedy3)}")
print(f"Optimal F_2(100) upper bound: {np.sqrt(100)+1:.2f}")

# ============================================================
# SUMMARY TABLE
# ============================================================
print(f"\n{'='*60}")
print(f"SUMMARY: FPGA-GUIDED vs GREEDY vs SINGER")
print(f"{'='*60}")
print(f"{'N':>5} | {'Greedy':>6} | {'FPGA-best':>9} | {'F_2 UB':>6} | {'sqrt(N)':>7}")
print(f"{'-'*5}-+-{'-'*6}-+-{'-'*9}-+-{'-'*6}-+-{'-'*7}")
