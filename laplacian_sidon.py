"""
Collision Graph Laplacian approach for PROMETHEUS FPGA.

The key insight: Gershgorin diagonal dominance DESTROYS collision information.
Instead, use the collision graph Laplacian L = D - W, then negate: K = -(L + εI)
to make it negative-definite while preserving spectral structure.

Also includes a refined QUBO with asymmetric bias to break the symmetry.
"""
import numpy as np
import json

def build_collision_weight_matrix(N):
    """Build the symmetric collision weight matrix W[i,j] = sum of collision involvements."""
    W = np.zeros((N, N))
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
                            W[u, v] += 1.0
    W = 0.5 * (W + W.T)  # Ensure exact symmetry
    return W

def build_fpga_matrix(N, epsilon=0.1):
    """
    Build FPGA-ready matrix K from collision Laplacian.
    
    L = D - W (graph Laplacian, positive semi-definite)
    K = -(L + εI)  (negative definite, preserves collision structure)
    
    The eigenvectors of K = eigenvectors of L (spectral structure preserved).
    """
    W = build_collision_weight_matrix(N)
    D = np.diag(np.sum(W, axis=1))
    L = D - W  # Graph Laplacian (PSD)
    K = -(L + epsilon * np.eye(N))  # Make neg-def
    return K, W, L

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
    S = [0]; sums = set()
    for x in range(1, N):
        new_sums = set()
        ok = True
        for s in S:
            ps = x + s
            if ps in sums or ps in new_sums:
                ok = False; break
            new_sums.add(ps)
        if ok:
            S.append(x); sums.update(new_sums)
    return S

def extract_sidon_from_scores(scores, N):
    """Extract Sidon set using element ordering from scores."""
    ranked = sorted(range(N), key=lambda i: scores[i], reverse=True)
    S = []; sums = set()
    for x in ranked:
        new_sums = set()
        ok = True
        for s in S:
            ps = x + s
            if ps in sums or ps in new_sums:
                ok = False; break
            new_sums.add(ps)
        if ok:
            S.append(x); sums.update(new_sums)
    return sorted(S)

# ============================================================
# Analysis across N values
# ============================================================
print("COLLISION LAPLACIAN ANALYSIS FOR PROMETHEUS")
print("=" * 70)

results = {}

for N in [30, 50, 100, 200, 500]:
    K, W, L = build_fpga_matrix(N)
    
    # Laplacian eigendecomposition
    L_evals, L_evecs = np.linalg.eigh(L)
    
    # K eigendecomposition
    K_evals = np.linalg.eigvalsh(K)
    
    # The Fiedler vector (2nd smallest Laplacian eigenvalue)
    fiedler = L_evecs[:, 1]
    
    # Inclusion score from K^{-1}: x* = -K^{-1} * bias
    # Use asymmetric bias: c_i = -(N - collision_count_i)
    # Elements with FEWER collisions get STRONGER inclusion incentive
    collision_count = np.sum(W, axis=1)
    max_coll = collision_count.max()
    bias = -(max_coll - collision_count + 1)  # Asymmetric: fewer collisions → stronger incentive
    
    K_inv = np.linalg.inv(K)
    x_star = -K_inv @ bias
    
    # Method 1: Asymmetric fixed-point ordering
    sidon_asym = extract_sidon_from_scores(x_star, N)
    
    # Method 2: Fiedler group + greedy
    pos_group = sorted([i for i in range(N) if fiedler[i] > 0])
    neg_group = sorted([i for i in range(N) if fiedler[i] <= 0])
    
    best_fiedler = []
    for group in [pos_group, neg_group]:
        S = []; sums = set()
        for x in group:
            new_sums = set()
            ok = True
            for s in S:
                ps = x + s
                if ps in sums or ps in new_sums:
                    ok = False; break
                new_sums.add(ps)
            if ok:
                S.append(x); sums.update(new_sums)
        if len(sorted(S)) > len(best_fiedler):
            best_fiedler = sorted(S)
    
    # Method 3: Inverse collision count (low-collision-first greedy)
    sidon_low_coll = extract_sidon_from_scores(-collision_count, N)
    
    # Method 4: K^{-1} diagonal (channel freedom) 
    K_inv_diag = np.diag(K_inv)
    sidon_kinv = extract_sidon_from_scores(-K_inv_diag, N)
    
    # Method 5: Multi-mode spectral embedding
    # Use first 5 non-trivial Laplacian eigenvectors
    n_modes = min(5, N-1)
    embedding = L_evecs[:, 1:n_modes+1]  # Skip trivial eigenvector
    # Elements "far" in embedding space are in different collision clusters
    # Use distances from embedding centroid
    centroid = embedding.mean(axis=0)
    distances = np.linalg.norm(embedding - centroid, axis=1)
    sidon_embed = extract_sidon_from_scores(distances, N)
    
    # Greedy baseline
    greedy = greedy_sidon(N)
    
    # Summary
    methods = {
        'asym-fixed-pt': sidon_asym,
        'fiedler-best': best_fiedler,
        'low-collision': sidon_low_coll,
        'K_inv-diag': sidon_kinv,
        'spectral-embed': sidon_embed,
        'greedy': greedy,
    }
    
    best_name = max(methods, key=lambda m: len(methods[m]))
    best_size = len(methods[best_name])
    
    print(f"\nN = {N}")
    print(f"  Laplacian gap (λ₁): {L_evals[1]:.2f}")
    print(f"  K eigenrange: [{K_evals[0]:.2f}, {K_evals[-1]:.2f}]")
    print(f"  Collision range: [{collision_count.min():.0f}, {collision_count.max():.0f}]")
    print(f"  F₂(N) bound: {np.sqrt(N)+1:.2f}")
    
    for name, S in methods.items():
        v = verify_sidon(S)
        marker = "✓" if v else "✗"
        if N <= 100:
            print(f"  {name:20s}: {S} (size {len(S)}) {marker}")
        else:
            print(f"  {name:20s}: size {len(S)} {marker}")
    
    print(f"  >>> BEST: {best_name} (size {best_size})")
    
    results[N] = {name: len(S) for name, S in methods.items()}

# ============================================================
# PROMETHEUS-ready matrix for N=30
# ============================================================
print("\n" + "=" * 70)
print("PROMETHEUS MATRIX PREPARATION (N=30)")
print("=" * 70)

N = 30
K, W, L = build_fpga_matrix(N, epsilon=0.1)

# Eigenvalue check
K_evals = np.linalg.eigvalsh(K)
print(f"K eigenrange: [{K_evals[0]:.4f}, {K_evals[-1]:.4f}]")
print(f"Neg-def: {all(e < 0 for e in K_evals)}")
print(f"Condition: {abs(K_evals[0]/K_evals[-1]):.1f}")

# Save compact JSON
K_list = K.tolist()
K_json = json.dumps(K_list, separators=(',', ':'))
print(f"Matrix size: {len(K_json)} chars")

# Asymmetric bias
collision_count = np.sum(W, axis=1)
max_coll = collision_count.max()
bias = -(max_coll - collision_count + 1)
bias_json = json.dumps(bias.tolist(), separators=(',', ':'))

print(f"Bias vector: [{bias[0]:.1f}, ..., {bias[N//2]:.1f}, ..., {bias[-1]:.1f}]")
print(f"Collision counts: min={collision_count.min():.0f} (elements {np.argmin(collision_count)},{N-1-np.argmin(collision_count)})")
print(f"                  max={collision_count.max():.0f} (elements {np.argmax(collision_count)})")

# Save for PROMETHEUS
with open("sidon_laplacian_K30.json", "w") as f:
    json.dump(K_list, f, separators=(',', ':'))

# Also prepare N=50 matrix
N2 = 50
K2, W2, L2 = build_fpga_matrix(N2, epsilon=0.1)
K2_list = K2.tolist()
K2_json = json.dumps(K2_list, separators=(',', ':'))
print(f"\nN=50 matrix size: {len(K2_json)} chars")
with open("sidon_laplacian_K50.json", "w") as f:
    json.dump(K2_list, f, separators=(',', ':'))

print(f"\nSaved: sidon_laplacian_K30.json, sidon_laplacian_K50.json")

# ============================================================
# Print the K30 matrix inline for PROMETHEUS
# ============================================================
with open("sidon_laplacian_K30_inline.txt", "w") as f:
    f.write(K_json)
print(f"Inline matrix written: {len(K_json)} chars")
