"""
QUBO-based Sidon set extraction for PROMETHEUS FPGA.

Problem: Find largest S ⊂ {0,...,N-1} such that all pairwise sums a+b are distinct.

QUBO encoding: maximize |S| subject to no sum collisions.
H(x) = -α * Σ x_i  +  β * Σ_{collision pairs} x_a * x_b * cross_terms
     = Σ_i h_i * x_i  +  Σ_{i<j} J_{ij} * x_i * x_j

For PROMETHEUS mapping: H(x) = ½ x^T Q x + c^T x
With Q encoding collision penalties and c encoding inclusion incentives.
"""
import numpy as np
import json

def build_qubo_sidon(N, alpha=1.0, beta=10.0):
    """
    Build QUBO matrix for Sidon set problem.
    
    H(x) = -alpha * sum(x_i) + beta * sum_collisions(x_a * x_c + x_a * x_d + x_b * x_c + x_b * x_d)
    
    For x ∈ {0,1}^N:
      - First term incentivizes inclusion (more elements = lower energy)
      - Second term penalizes collision pairs (Sidon violations = higher energy)
    
    For continuous relaxation on FPGA:
      Q_{ij} = collision penalty between elements i,j (positive = repulsive)
      c_i = -alpha (inclusion incentive)
    """
    # Build collision penalty matrix (off-diagonal only)
    Q = np.zeros((N, N))
    collision_count = 0
    
    for s in range(2, 2*N - 2):
        pairs = []
        for a in range(max(0, s - (N-1)), min(s, N-1) + 1):
            b = s - a
            if 0 <= b < N and a < b:
                pairs.append((a, b))
        
        # Each collision quadruple: pairs with same sum
        for i in range(len(pairs)):
            for j in range(i+1, len(pairs)):
                a1, b1 = pairs[i]
                a2, b2 = pairs[j]
                # Cross-pair penalties: including both pairs creates a sum collision
                # Penalty for (a1,b1) and (a2,b2) having same sum
                for u in [a1, b1]:
                    for v in [a2, b2]:
                        if u != v:
                            Q[u, v] += beta
                            Q[v, u] += beta
                collision_count += 1
    
    # Make negative-definite by subtracting diagonal dominance
    for i in range(N):
        row_sum = np.sum(np.abs(Q[i, :])) - abs(Q[i, i])
        Q[i, i] = -(row_sum + 0.1)  # Minimal dominance, preserving collision structure
    
    # Inclusion incentive bias
    c = np.full(N, -alpha)
    
    return Q, c, collision_count

def build_penalty_only_matrix(N, penalty=1.0):
    """
    Build PURE collision penalty matrix (no Gershgorin inflation).
    Off-diagonal: collision penalties. Diagonal: negative collision count per element.
    
    This is NOT necessarily negative-definite, but encodes the raw collision structure.
    """
    W = np.zeros((N, N))  # Collision weight matrix
    element_collisions = np.zeros(N)  # How many collisions involve each element
    
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
                for u in [a1, b1]:
                    for v in [a2, b2]:
                        if u != v:
                            W[u, v] += penalty
                            element_collisions[u] += penalty
                            element_collisions[v] += penalty
    
    # Symmetrize (already symmetric by construction, but ensure)
    W = 0.5 * (W + W.T)
    
    return W, element_collisions

def verify_sidon(S):
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

def spectral_sidon(N, n_modes=3):
    """Extract Sidon set using spectral analysis of collision graph."""
    W, elem_coll = build_penalty_only_matrix(N)
    
    # Graph Laplacian: L = D - W
    D = np.diag(np.sum(W, axis=1))
    L = D - W
    
    # Eigendecomposition of Laplacian
    eigenvalues, eigenvectors = np.linalg.eigh(L)
    
    # Fiedler vector (2nd smallest eigenvalue) gives best 2-partition
    fiedler = eigenvectors[:, 1]
    
    # Elements in the "positive" partition have fewer inter-collisions
    pos_elements = sorted([i for i in range(N) if fiedler[i] > 0])
    neg_elements = sorted([i for i in range(N) if fiedler[i] <= 0])
    
    results = {}
    
    # Greedy Sidon from each partition
    for name, group in [("fiedler+", pos_elements), ("fiedler-", neg_elements)]:
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
        results[name] = sorted(S)
    
    # Also try: rank elements by INVERSE collision count (least-colliding first)
    ranked_by_collisions = sorted(range(N), key=lambda i: elem_coll[i])
    S = []
    sums = set()
    for x in ranked_by_collisions:
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
    results["low-collision"] = sorted(S)
    
    # Multi-mode spectral: use first k Laplacian eigenvectors as embedding
    embedding = eigenvectors[:, :n_modes]  # first n_modes eigenvectors
    # K-means-like: find elements closest to origin in embedding space
    # (these are "central" elements with balanced collision profile)
    distances = np.linalg.norm(embedding, axis=1)
    ranked_central = sorted(range(N), key=lambda i: distances[i])
    S = []
    sums = set()
    for x in ranked_central:
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
    results["spectral-central"] = sorted(S)
    
    # Rank by fiedler absolute value (elements near the partition boundary are interesting)
    ranked_boundary = sorted(range(N), key=lambda i: abs(fiedler[i]))
    S = []
    sums = set()
    for x in ranked_boundary:
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
    results["fiedler-boundary"] = sorted(S)
    
    return results, eigenvalues[:5], fiedler, elem_coll

# ============================================================
# ANALYSIS
# ============================================================
for N in [30, 50, 100, 200, 500]:
    print(f"\n{'='*70}")
    print(f"N = {N}")
    print(f"{'='*70}")
    
    results, laplacian_eigs, fiedler, elem_coll = spectral_sidon(N)
    greedy = greedy_sidon(N)
    
    print(f"Laplacian eigenvalues [0..4]: {[f'{e:.2f}' for e in laplacian_eigs]}")
    print(f"Collision range: [{elem_coll.min():.0f}, {elem_coll.max():.0f}]")
    print(f"sqrt(N) = {np.sqrt(N):.2f},  F_2(N) bound ≈ {np.sqrt(N)+1:.2f}")
    print()
    
    best_method = ""
    best_size = 0
    
    for name, S in results.items():
        is_sidon = verify_sidon(S)
        marker = "✓" if is_sidon else "✗"
        if is_sidon and len(S) > best_size:
            best_size = len(S)
            best_method = name
        if N <= 100:
            print(f"  {name:20s}: {S} -> size {len(S)} {marker}")
        else:
            print(f"  {name:20s}: size {len(S)} {marker}")
    
    print(f"  {'greedy':20s}: size {len(greedy)} ✓", end="")
    if N <= 50:
        print(f"  {greedy}")
    else:
        print()
    
    print(f"\n  BEST spectral method: {best_method} (size {best_size})")
    print(f"  vs greedy: {len(greedy)}")
    improvement = best_size - len(greedy)
    print(f"  improvement: {improvement:+d}")

# ============================================================
# QUBO MATRIX PREPARATION FOR PROMETHEUS
# ============================================================
print(f"\n{'='*70}")
print("QUBO MATRIX FOR PROMETHEUS (N=30)")
print(f"{'='*70}")

Q, c, ncoll = build_qubo_sidon(30, alpha=50.0, beta=1.0)
evals = np.linalg.eigvalsh(Q)
print(f"Collisions: {ncoll}")
print(f"Q eigenvalues: min={evals[0]:.2f}, max={evals[-1]:.2f}")
print(f"Neg-def: {all(e < 0 for e in evals)}")
print(f"Bias vector c: [{c[0]:.1f}, ..., {c[-1]:.1f}]")

# Fixed point x* = -Q^{-1} * c
Q_inv = np.linalg.inv(Q)
x_star = -Q_inv @ c
print(f"\nFixed point x* = -Q^{{-1}}·c:")
ranked = sorted(range(30), key=lambda i: x_star[i], reverse=True)
for i, idx in enumerate(ranked):
    marker = " <<<" if i < 8 else ""
    print(f"  element {idx:2d}: x* = {x_star[idx]:.6f}{marker}")

# Extract Sidon set from x*
print(f"\nThresholding x* for Sidon sets:")
for percentile in [90, 80, 75, 70, 60, 50]:
    threshold = np.percentile(x_star, percentile)
    candidate = sorted([i for i in range(30) if x_star[i] >= threshold])
    is_sidon = verify_sidon(candidate)
    marker = "✓ SIDON" if is_sidon else "  not Sidon"
    print(f"  p{percentile}: threshold={threshold:.6f}, set={candidate}, size={len(candidate)} {marker}")

# Save compact Q matrix for PROMETHEUS
Q_list = Q.tolist()
Q_json = json.dumps(Q_list, separators=(',', ':'))
print(f"\nQUBO matrix size: {len(Q_json)} chars")
with open("sidon_qubo30.json", "w") as f:
    json.dump(Q_list, f, separators=(',', ':'))
print("Saved: sidon_qubo30.json")

c_json = json.dumps(c.tolist(), separators=(',', ':'))
print(f"Bias vector size: {len(c_json)} chars")
with open("sidon_bias30.json", "w") as f:
    json.dump(c.tolist(), f, separators=(',', ':'))
print("Saved: sidon_bias30.json")
