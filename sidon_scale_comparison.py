"""
Comprehensive scaling comparison: K^{-1}-diagonal vs greedy for Sidon subset extraction.
Tests on A = {0, ..., N-1} (arithmetic progression — worst-case collision density).

Erdős 530: Does every N-element set contain a Sidon subset of size Ω(√N)?
"""
import numpy as np
import time
import sys

def build_collision_weight_matrix(N):
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
    W = 0.5 * (W + W.T)
    return W

def build_laplacian_K(N, epsilon=0.1):
    W = build_collision_weight_matrix(N)
    D = np.diag(np.sum(W, axis=1))
    L = D - W
    K = -(L + epsilon * np.eye(N))
    return K, W

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

def randomized_greedy(N, trials=50):
    """Best of multiple random-order greedy attempts."""
    best = []
    elems = list(range(N))
    for _ in range(trials):
        perm = np.random.permutation(elems)
        S = []; sums = set()
        for x in perm:
            new_sums = set()
            ok = True
            for s in S:
                ps = x + s
                if ps in sums or ps in new_sums:
                    ok = False; break
                new_sums.add(ps)
            if ok:
                S.append(x); sums.update(new_sums)
        if len(S) > len(best):
            best = sorted(S)
    return best

print("ERDOS 530: K^{-1}-DIAGONAL vs GREEDY SCALING COMPARISON")
print("=" * 75)
print(f"{'N':>6} | {'sqrt(N)':>8} | {'Greedy':>7} | {'RandGr50':>8} | {'K_inv':>6} | {'LowColl':>7} | {'SpEmbed':>7} | {'Best':>7} | {'Winner':>12} | {'Time':>6}")
print("-" * 75)

results = []
test_sizes = [25, 30, 50, 75, 100, 150, 200, 300, 500]

# Check if we should try larger sizes
if '--large' in sys.argv:
    test_sizes.extend([750, 1000])

for N in test_sizes:
    t0 = time.time()
    
    # Build collision Laplacian
    K, W = build_laplacian_K(N)
    
    # K^{-1} diagonal
    K_inv = np.linalg.inv(K)
    K_inv_diag = np.diag(K_inv)
    sidon_kinv = extract_sidon_from_scores(-K_inv_diag, N)
    
    # Low-collision greedy
    collision_count = np.sum(W, axis=1)
    sidon_lowcoll = extract_sidon_from_scores(-collision_count, N)
    
    # Spectral embedding
    L = np.diag(np.sum(W, axis=1)) - W
    L_evals, L_evecs = np.linalg.eigh(L)
    n_modes = min(5, N - 1)
    embedding = L_evecs[:, 1:n_modes + 1]
    centroid = embedding.mean(axis=0)
    distances = np.linalg.norm(embedding - centroid, axis=1)
    sidon_embed = extract_sidon_from_scores(distances, N)
    
    # Standard greedy
    greedy = greedy_sidon(N)
    
    # Randomized greedy (50 trials)
    rand_greedy = randomized_greedy(N, trials=50)
    
    elapsed = time.time() - t0
    sqrtN = np.sqrt(N)
    
    # Verify all
    for name, S in [('K_inv', sidon_kinv), ('LowColl', sidon_lowcoll), 
                     ('SpEmbed', sidon_embed), ('Greedy', greedy), ('RandGr', rand_greedy)]:
        assert verify_sidon(S), f"{name} at N={N} is not Sidon!"
    
    sizes = {
        'greedy': len(greedy),
        'rand_greedy': len(rand_greedy),
        'kinv': len(sidon_kinv),
        'lowcoll': len(sidon_lowcoll),
        'embed': len(sidon_embed),
    }
    
    best_method = max(sizes, key=lambda k: sizes[k])
    best_size = sizes[best_method]
    
    winner_name = {'greedy': 'Greedy', 'rand_greedy': 'RandGr50', 'kinv': 'K_inv', 
                   'lowcoll': 'LowColl', 'embed': 'SpEmbed'}[best_method]
    
    print(f"{N:>6} | {sqrtN:>8.2f} | {sizes['greedy']:>7} | {sizes['rand_greedy']:>8} | {sizes['kinv']:>6} | {sizes['lowcoll']:>7} | {sizes['embed']:>7} | {best_size:>7} | {winner_name:>12} | {elapsed:>5.1f}s")
    
    results.append({
        'N': N, 'sqrtN': sqrtN, **sizes, 'best': best_size, 'winner': winner_name, 'time': elapsed
    })

print()
print("ANALYSIS")
print("=" * 75)
print()
print("Key questions for Erdos 530:")
print("1. Does best Sidon subset size >= sqrt(N) for all N tested?")
print("2. At what N does K_inv-diag start beating standard greedy?")
print("3. Does the ratio best/sqrt(N) converge to a constant > 1?")
print()

for r in results:
    ratio = r['best'] / r['sqrtN']
    kinv_ratio = r['kinv'] / r['sqrtN']
    above = "YES" if r['best'] >= r['sqrtN'] else "NO"
    print(f"  N={r['N']:>5}: best/sqrt(N) = {ratio:.3f}  K_inv/sqrt(N) = {kinv_ratio:.3f}  >= sqrt(N)? {above}")

print()
print("K_inv-diag advantage over standard greedy:")
for r in results:
    diff = r['kinv'] - r['greedy']
    pct = (r['kinv'] / r['greedy'] - 1) * 100 if r['greedy'] > 0 else 0
    marker = ">>>" if diff > 0 else ("===" if diff == 0 else "   ")
    print(f"  {marker} N={r['N']:>5}: K_inv={r['kinv']}, greedy={r['greedy']}, diff={diff:+d} ({pct:+.1f}%)")
