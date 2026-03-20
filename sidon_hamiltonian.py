"""
Sidon Set → Quadratic Hamiltonian for PROMETHEUS FPGA
======================================================

Encode the Maximum Sidon Set problem as:
  H(x) = ½ x^T K x + c^T x

where K penalizes elements that participate in sum collisions,
and c encourages inclusion of all elements.

The ground state of H approximates the maximum Sidon set indicator.
"""

import json, math, sys

def build_collision_matrix(N, penalty=1.0, diagonal=-1.0):
    """
    Build the N×N collision penalty matrix for Sidon sets in {0,...,N-1}.
    
    For each collision quadruple (a,b,c,d) with a+b=c+d, {a,b}≠{c,d}:
      K[a,c] += P, K[a,d] += P, K[b,c] += P, K[b,d] += P
      (and symmetric counterparts)
    
    Diagonal: K[i,i] = diagonal (negative for stability)
    """
    K = [[0.0] * N for _ in range(N)]
    
    # Set diagonal
    for i in range(N):
        K[i][i] = diagonal
    
    # Enumerate all sum collisions
    # Group pairs by their sum
    sum_groups = {}
    for a in range(N):
        for b in range(a, N):
            s = a + b
            if s not in sum_groups:
                sum_groups[s] = []
            sum_groups[s].append((a, b))
    
    collision_count = 0
    # For each sum with ≥2 representations, create penalties
    for s, pairs in sum_groups.items():
        if len(pairs) < 2:
            continue
        # For each pair of pairs that collide
        for i in range(len(pairs)):
            a, b = pairs[i]
            for j in range(i + 1, len(pairs)):
                c, d = pairs[j]
                collision_count += 1
                # Penalize cross-pairs: having elements from BOTH representations
                # (a,b) and (c,d) in the set simultaneously
                for u in [a, b]:
                    for v in [c, d]:
                        if u != v:
                            K[u][v] += penalty
                            K[v][u] += penalty
    
    # Make diagonal dominant enough for negative definiteness
    # Gershgorin: need |K[i,i]| > sum of |K[i,j]| for j≠i
    for i in range(N):
        row_sum = sum(abs(K[i][j]) for j in range(N) if j != i)
        if abs(K[i][i]) <= row_sum:
            K[i][i] = -(row_sum + 1.0)
    
    return K, collision_count


def verify_sidon(S):
    """Check if S is a Sidon (B2) set."""
    sums = set()
    for i in range(len(S)):
        for j in range(i, len(S)):
            s = S[i] + S[j]
            if s in sums:
                return False
            sums.add(s)
    return True


def threshold_to_sidon(x, threshold_percentile=75):
    """
    Given continuous solution x, threshold to get a Sidon set.
    Take elements with largest x_i, greedily ensure Sidon property.
    """
    N = len(x)
    # Sort by x_i descending (most "included" first)
    ranked = sorted(range(N), key=lambda i: x[i], reverse=True)
    
    result = []
    sums = set()
    for idx in ranked:
        # Try adding this element
        ok = True
        for s in result:
            if (idx + s) in sums:
                ok = False
                break
        if ok:
            for s in result:
                sums.add(idx + s)
            sums.add(2 * idx)
            result.append(idx)
    
    return sorted(result)


# Build matrices for several N values
for N in [20, 30, 50, 75, 100]:
    K, ncoll = build_collision_matrix(N, penalty=0.5, diagonal=-1.0)
    
    # Compute stats
    min_diag = min(K[i][i] for i in range(N))
    max_offdiag = max(K[i][j] for i in range(N) for j in range(N) if i != j)
    total_penalty = sum(K[i][j] for i in range(N) for j in range(N) if i != j) / 2
    
    print(f"N={N:3d}: {ncoll:6d} collisions, diag=[{min_diag:.1f}], max_off={max_offdiag:.1f}, total_penalty={total_penalty:.0f}")
    
    # Check negative definiteness via Gershgorin
    is_neg_def = True
    for i in range(N):
        row_sum = sum(abs(K[i][j]) for j in range(N) if j != i)
        if K[i][i] + row_sum >= 0:
            is_neg_def = False
            break
    print(f"       Negative definite (Gershgorin): {is_neg_def}")

# Save the N=50 matrix for PROMETHEUS
print("\nSaving N=50 collision matrix...")
N = 50
K, ncoll = build_collision_matrix(N, penalty=0.5, diagonal=-1.0)
bias = [-1.0] * N  # encourage all elements to be "included"

# Save matrix and bias
with open('D:/Erdos/sidon_K50.json', 'w') as f:
    json.dump(K, f)

with open('D:/Erdos/sidon_bias50.json', 'w') as f:
    json.dump(bias, f)

print(f"Saved: sidon_K50.json ({N}x{N} matrix, {ncoll} collisions)")

# Also save N=30 for quick validation
N = 30
K30, nc30 = build_collision_matrix(N, penalty=0.5, diagonal=-1.0)
bias30 = [-1.0] * N

with open('D:/Erdos/sidon_K30.json', 'w') as f:
    json.dump(K30, f)

print(f"Saved: sidon_K30.json ({N}x{N} matrix, {nc30} collisions)")

# Save N=100 for larger experiments
N = 100
K100, nc100 = build_collision_matrix(N, penalty=0.5, diagonal=-1.0)
with open('D:/Erdos/sidon_K100.json', 'w') as f:
    json.dump(K100, f)

print(f"Saved: sidon_K100.json ({N}x{N} matrix, {nc100} collisions)")
