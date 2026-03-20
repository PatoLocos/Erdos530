"""
Comprehensive Singer + greedy extension comparison.
For each target N, constructs the best Singer set fitting in {0,...,N-1},
then greedily extends it. Compares against pure greedy and K^{-1} spectral.
"""
import numpy as np
from singer_gf_construction import singer_sidon_set, verify_sidon, prime_factors
from sympy import isprime
import time, sys

def greedy_sidon(universe, seed=None):
    """Standard greedy Sidon: add elements in random order if they don't create collision."""
    rng = np.random.RandomState(seed)
    elems = list(universe)
    rng.shuffle(elems)
    S = []
    sums = set()
    for x in elems:
        ok = True
        for s in S:
            pair_sum = x + s
            if pair_sum in sums:
                ok = False
                break
        if ok:
            new_sums = [x + s for s in S]
            new_sums.append(2*x)
            sums.update(new_sums)
            S.append(x)
    return sorted(S)

def extend_sidon_greedy(base_set, universe):
    """Extend a Sidon set greedily with elements from universe."""
    S = sorted(base_set)
    sums = set()
    for i in range(len(S)):
        sums.add(2*S[i])
        for j in range(i+1, len(S)):
            sums.add(S[i] + S[j])
    
    remaining = sorted(set(universe) - set(S))
    np.random.shuffle(remaining)
    
    for x in remaining:
        ok = True
        for s in S:
            if x + s in sums:
                ok = False
                break
        if ok:
            new_sums = [x + s for s in S] + [2*x]
            sums.update(new_sums)
            S.append(x)
    return sorted(S)

def kinv_sidon(N, epsilon=0.1):
    """K^{-1} diagonal spectral Sidon extraction from {0,...,N-1}."""
    W = np.zeros((N, N))
    for a in range(N):
        for b in range(a+1, N):
            s = a + b
            count = 0
            for c in range(N):
                d = s - c
                if 0 <= d < N and c < d and (c != a or d != b):
                    count += 1
            W[a, b] = count
            W[b, a] = count
    
    D = np.diag(W.sum(axis=1))
    L = D - W
    K = -(L + epsilon * np.eye(N))
    
    try:
        Kinv = np.linalg.inv(K)
    except np.linalg.LinAlgError:
        return greedy_sidon(range(N), seed=0)
    
    scores = np.abs(np.diag(Kinv))
    ranked = np.argsort(-scores)
    
    S = []
    sums = set()
    for idx in ranked:
        x = int(idx)
        ok = True
        for s in S:
            if x + s in sums:
                ok = False
                break
        if ok:
            new_sums = [x + s for s in S] + [2*x]
            sums.update(new_sums)
            S.append(x)
    return sorted(S)

# ============================================================
# Precompute Singer sets for all primes up to 71
# ============================================================
print("Precomputing Singer sets...")
singer_cache = {}
primes_to_try = [q for q in range(2, 72) if isprime(q)]

for q in primes_to_try:
    m = q*q + q + 1
    t0 = time.time()
    D, mod = singer_sidon_set(q)
    dt = time.time() - t0
    if D is not None and verify_sidon(D):
        singer_cache[q] = (D, m)
        print(f"  q={q:>2}: |D|={len(D):>3}, m={m:>5}, max={max(D):>5}, time={dt:.1f}s")
    else:
        print(f"  q={q:>2}: FAILED or not Sidon")

# ============================================================
# For each target N, find best Singer set + extension
# ============================================================
print("\n" + "="*90)
print("COMPREHENSIVE COMPARISON: Singer+Ext vs Greedy vs K_inv")
print("="*90)
print(f"{'N':>6} | {'√N':>6} | {'Singer':>6} | {'Sing+E':>6} | {'Greedy':>6} | "
      f"{'RndGr':>5} | {'K_inv':>5} | {'Best':>5} | {'ratio':>6} | {'Winner':>12}")
print("-"*90)

target_Ns = [25, 50, 100, 150, 200, 300, 400, 500, 750, 1000]
if "--large" in sys.argv:
    target_Ns.extend([1500, 2000, 3000, 5000])

for N in target_Ns:
    sqN = np.sqrt(N)
    universe = range(N)
    
    # 1. Best Singer set fitting in {0,...,N-1}
    best_singer = None
    best_q = None
    for q, (D, m) in singer_cache.items():
        if max(D) < N:
            if best_singer is None or len(D) > len(best_singer):
                best_singer = D
                best_q = q
    
    singer_size = len(best_singer) if best_singer else 0
    
    # 2. Singer + greedy extension
    if best_singer:
        singer_ext = extend_sidon_greedy(best_singer, universe)
        singer_ext_size = len(singer_ext)
    else:
        singer_ext_size = 0
    
    # 3. Pure greedy (best of sorted variants)
    greedy_sorted = greedy_sidon(universe, seed=None)
    greedy_size = len(greedy_sorted)
    
    # 4. Randomized greedy (50 trials)
    rnd_best = greedy_size
    for trial in range(50):
        rg = greedy_sidon(universe, seed=trial)
        rnd_best = max(rnd_best, len(rg))
    
    # 5. K^{-1} spectral (only for N <= 500, expensive)
    if N <= 500:
        kinv_set = kinv_sidon(N)
        kinv_size = len(kinv_set)
    else:
        kinv_size = 0  # too expensive
    
    # Best overall
    all_results = {
        'Singer': singer_size,
        'Sing+Ext': singer_ext_size,
        'Greedy': greedy_size,
        'RndGreedy': rnd_best,
    }
    if kinv_size > 0:
        all_results['K_inv'] = kinv_size
    
    best_size = max(all_results.values())
    winner = max(all_results, key=all_results.get)
    ratio = best_size / sqN
    
    kinv_str = f"{kinv_size:>5}" if kinv_size > 0 else "  N/A"
    check = ">=" if best_size >= sqN else "< "
    
    print(f"{N:>6} | {sqN:>6.2f} | {singer_size:>6} | {singer_ext_size:>6} | "
          f"{greedy_size:>6} | {rnd_best:>5} | {kinv_str} | {best_size:>5} | "
          f"{ratio:>6.3f} | {winner:>12} {check}")

# ============================================================
# Key theoretical results
# ============================================================
print("\n" + "="*90)
print("THEORETICAL ANALYSIS: Singer set as Sidon subset of {0,...,m-1}")
print("="*90)
print(f"{'q':>4} | {'m=q²+q+1':>10} | {'|D|=q+1':>8} | {'√m':>8} | {'|D|/√m':>8} | {'|D|≥√m?':>8}")
print("-"*60)

for q in sorted(singer_cache.keys()):
    D, m = singer_cache[q]
    sqm = np.sqrt(m)
    ratio = len(D) / sqm
    check = "YES ✓" if len(D) >= sqm else "NO"
    print(f"{q:>4} | {m:>10} | {len(D):>8} | {sqm:>8.2f} | {ratio:>8.4f} | {check:>8}")

# Asymptotic analysis
print(f"\nAsymptotic: |D|/√m = (q+1)/√(q²+q+1) → 1 as q → ∞")
print(f"For q=67: ratio = 68/√{67**2+67+1} = 68/{np.sqrt(67**2+67+1):.2f} = {68/np.sqrt(67**2+67+1):.4f}")
print(f"\nThis proves: for infinitely many N, F₂(N) ≥ (1-ε)√N for any ε > 0.")
print(f"(Take N = q²+q+1 for prime q → ∞)")
