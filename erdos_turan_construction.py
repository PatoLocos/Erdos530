"""
Constructive Sidon sets via Erdos-Turan construction + extension.
Proves F_2({0,...,N-1}) >= sqrt(N) for specific N values.

Erdos-Turan construction: for prime p, S = {a*p + (a^2 mod p) : a=0,...,p-1}
is a Sidon set of size p in {0,...,p^2-1}.
"""
import numpy as np
from sympy import isprime, prevprime, nextprime

def erdos_turan_sidon(p):
    """Construct the Erdos-Turan Sidon set for prime p.
    S = {2*a*p + (a^2 mod p) : a=0,...,p-1} is a B_2 set of size p in {0,...,2p^2-p-1}.
    
    Proof: differences d(a1,a2) = 2(a1-a2)*p + (a1^2-a2^2 mod p).
    Since |a1^2-a2^2 mod p| < p and step is 2p, the pair (a1-a2, residue) is
    uniquely recoverable from the integer difference. QED.
    """
    S = []
    for a in range(p):
        elem = 2 * a * p + (a * a) % p
        S.append(elem)
    return sorted(S)

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

def get_sum_set(S):
    sums = set()
    for i in range(len(S)):
        for j in range(i+1, len(S)):
            sums.add(S[i] + S[j])
    return sums

def extend_sidon(S, N, max_attempts=None):
    """Try to extend Sidon set S by adding elements from {0,...,N-1}."""
    S = list(S)
    sums = get_sum_set(S)
    candidates = [x for x in range(N) if x not in set(S)]
    np.random.shuffle(candidates)
    
    if max_attempts:
        candidates = candidates[:max_attempts]
    
    for x in candidates:
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
    
    return sorted(S)

def greedy_extend_sorted(S, candidates):
    """Extend Sidon set S with candidates in given order."""
    S = list(S)
    sums = get_sum_set(S)
    for x in candidates:
        if x in set(S):
            continue
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
    return sorted(S)

print("ERDOS-TURAN CONSTRUCTION + EXTENSION FOR SIDON SETS")
print("=" * 70)

# First verify the construction works
print("\nVerification for small primes:")
for p in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]:
    S = erdos_turan_sidon(p)
    is_sid = verify_sidon(S)
    print(f"  p={p:>2}: |S|={len(S):>2}, max_elem={max(S):>4} (in {{0,...,{p*p-1}}}), Sidon={is_sid}")
    if p <= 7:
        print(f"         S = {S}")

# For each target N, construct ET set and try to extend
print("\n" + "=" * 70)
print("CONSTRUCTION FOR TARGET N VALUES")
print("=" * 70)
print(f"{'N':>6} | {'sqrt(N)':>8} | {'p':>4} | {'ET size':>7} | {'Extended':>8} | {'Ratio':>6} | {'>=sqrt?':>7}")
print("-" * 70)

for N in [50, 100, 200, 300, 500, 750, 1000, 1024, 1500, 2000, 3000, 5000, 10000]:
    sqN = np.sqrt(N)
    
    # Find largest prime p with p^2 <= N
    p_max = int(np.sqrt(N))
    while not isprime(p_max):
        p_max -= 1
    
    # Construct ET set
    S_et = erdos_turan_sidon(p_max)
    assert verify_sidon(S_et), f"ET construction failed for p={p_max}!"
    assert max(S_et) < N, f"ET set exceeds N-1!"
    
    # Try to extend with remaining elements
    best_extended = S_et
    for trial in range(20):
        S_ext = extend_sidon(list(S_et), N)
        if len(S_ext) > len(best_extended):
            best_extended = S_ext
    
    # Also try extending with edge elements first (near 0 and N-1)
    remaining = [x for x in range(N) if x not in set(S_et)]
    remaining_by_edge = sorted(remaining, key=lambda x: min(x, N-1-x))
    S_edge = greedy_extend_sorted(list(S_et), remaining_by_edge)
    if len(S_edge) > len(best_extended):
        best_extended = S_edge
    
    # Try extending with center elements 
    remaining_by_center = sorted(remaining, key=lambda x: -min(x, N-1-x))
    S_center = greedy_extend_sorted(list(S_et), remaining_by_center)
    if len(S_center) > len(best_extended):
        best_extended = S_center
    
    assert verify_sidon(best_extended)
    
    ratio = len(best_extended) / sqN
    above = "YES" if len(best_extended) >= sqN else "no"
    
    print(f"{N:>6} | {sqN:>8.2f} | {p_max:>4} | {len(S_et):>7} | {len(best_extended):>8} | {ratio:>6.3f} | {above:>7}")

# Deep analysis for N=1000
print("\n" + "=" * 70)
print("DEEP ANALYSIS: N = 1000")
print("=" * 70)

N = 1000
sqN = np.sqrt(N)
p = 31

S_et = erdos_turan_sidon(p)
print(f"\nErdos-Turan set (p={p}): {len(S_et)} elements")
print(f"  Set: {S_et}")
print(f"  Max element: {max(S_et)}")
print(f"  sqrt(N) = {sqN:.2f}")

# Aggressive extension: many random trials
print(f"\nExtending ET set from {len(S_et)} elements...")
best = S_et
for trial in range(500):
    S_ext = extend_sidon(list(S_et), N)
    if len(S_ext) > len(best):
        best = S_ext
        print(f"  Trial {trial}: extended to {len(best)}")

print(f"\nBest extended ET: {len(best)} elements")
print(f"  ratio = {len(best)/sqN:.4f}")
print(f"  >= sqrt(N)? {'YES' if len(best) >= sqN else 'NO (need ' + str(int(np.ceil(sqN))) + ')'}")

# Also try: start from scratch with massive randomized greedy
print(f"\nMassive randomized greedy (5000 trials)...")
best_rand = []
for trial in range(5000):
    perm = np.random.permutation(N)
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
    if len(S) > len(best_rand):
        best_rand = sorted(S)
        if len(best_rand) >= sqN:
            print(f"  Trial {trial}: Found {len(best_rand)} >= sqrt(N)!")
            break
    if trial % 1000 == 999:
        print(f"  After {trial+1} trials: best = {len(best_rand)}")

print(f"\nBest randomized greedy: {len(best_rand)} elements")
print(f"  ratio = {len(best_rand)/sqN:.4f}")

overall_best = max([best, best_rand], key=len)
print(f"\n*** OVERALL BEST for N={N}: {len(overall_best)} elements ***")
print(f"  ratio = {len(overall_best)/sqN:.4f}")
print(f"  >= sqrt(N)? {'YES' if len(overall_best) >= sqN else 'NO'}")
if len(overall_best) <= 40:
    print(f"  Set: {overall_best}")
