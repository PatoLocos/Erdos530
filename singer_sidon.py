"""
Singer construction for Sidon sets + massive randomized search.
Proves F_2(N) >= sqrt(N) constructively for specific N values.

The Singer construction: for prime power q, the set of elements
{alpha^i : i = 0,...,q} viewed modulo q^2+q+1 forms a perfect
difference set (Sidon set) of size q+1.
"""
import numpy as np
from sympy import isprime, nextprime

def singer_sidon_set(q):
    """
    Construct a Singer Sidon set of size q+1 in Z_{q^2+q+1}.
    Works when q is a prime (using primitive root of GF(q^2+q+1) if it's prime,
    or polynomial construction over GF(q)).
    
    For simplicity, use the explicit construction via primitive element of GF(q^3)
    modulo GF(q), projected to get elements of PG(2,q)'s Singer cycle.
    
    Alternative: Use polynomial x^3 - x - 1 over GF(q) if irreducible.
    """
    m = q * q + q + 1
    
    # For prime q, find a primitive root of Z/mZ that generates a Singer cycle
    # of length m, then take every (q+1)-th power
    # Actually, simpler: find elements using the quadratic residue / index approach
    
    # Method: Try to find a Sidon set of size q+1 in Z_m via power residues
    # The Singer difference set D in Z_m: D = {g^{(q+1)i} mod m : i = 0,...,q}
    # where g is a primitive root of Z_m
    
    if not is_prime_power(q):
        return None
    
    # Find a primitive root of Z_m (only works if m is prime)
    if isprime(m):
        g = find_primitive_root(m)
        if g is None:
            return None
        # Singer difference set: D = {g^{kt} mod m : t = 0,...,q}
        # where k = (m-1)/(q+1) = q^2+q+1-1)/(q+1) = (q^2+q)/(q+1) = q
        k = q  # This is the correct exponent step for Singer cycle
        D = set()
        power = 1
        for t in range(q + 1):
            D.add(power % m)
            power = (power * pow(g, k, m)) % m
        
        D = sorted(D)
        if len(D) == q + 1 and verify_sidon_mod(D, m):
            return D, m
    
    # Fallback: brute force search for Sidon set in Z_m
    return None

def is_prime_power(n):
    if isprime(n):
        return True
    for p in range(2, int(n**0.5) + 1):
        k = n
        while k % p == 0:
            k //= p
        if k == 1:
            return True
    return False

def find_primitive_root(p):
    """Find a primitive root of Z/pZ for prime p."""
    if p == 2:
        return 1
    # Factor p-1
    phi = p - 1
    factors = set()
    n = phi
    for f in range(2, int(n**0.5) + 1):
        while n % f == 0:
            factors.add(f)
            n //= f
    if n > 1:
        factors.add(n)
    
    for g in range(2, p):
        ok = True
        for f in factors:
            if pow(g, phi // f, p) == 1:
                ok = False
                break
        if ok:
            return g
    return None

def verify_sidon_mod(S, m):
    """Verify S is a Sidon set modulo m (all differences distinct mod m)."""
    diffs = set()
    S = sorted(S)
    for i in range(len(S)):
        for j in range(i+1, len(S)):
            d = (S[i] - S[j]) % m
            if d in diffs:
                return False
            diffs.add(d)
            d2 = (S[j] - S[i]) % m
            if d2 in diffs:
                return False
            diffs.add(d2)
    return True

def verify_sidon(S):
    """Verify S is a Sidon set (all pairwise sums distinct as integers)."""
    S = sorted(S)
    sums = set()
    for i in range(len(S)):
        for j in range(i+1, len(S)):
            s = S[i] + S[j]
            if s in sums:
                return False
            sums.add(s)
    return True

def greedy_from_ranking(ranking, N):
    S = []; sums = set()
    for x in ranking:
        if x < 0 or x >= N:
            continue
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

# =================================================================
# Test Singer construction for specific q values
# =================================================================
print("SINGER CONSTRUCTION FOR SIDON SETS")
print("=" * 60)
print()

# For each q, Singer set has size q+1 in Z_{q^2+q+1}
# We want the smallest q such that q^2+q+1 <= N
singer_results = []

for q in range(2, 40):
    if not (isprime(q) or is_prime_power(q)):
        continue
    m = q*q + q + 1
    if not isprime(m):
        continue
    
    g = find_primitive_root(m)
    if g is None:
        continue
    
    # Construct Singer set
    k = q
    D = []
    power = 1
    for t in range(q + 1):
        D.append(power % m)
        power = (power * pow(g, k, m)) % m
    D = sorted(set(D))
    
    if len(D) != q + 1:
        # Try different construction: D = {g^i mod m : i = 0, q+1, 2(q+1), ...}
        D = []
        for t in range(q + 1):
            D.append(pow(g, t * (q + 1), m) if t > 0 else 1)
        D = sorted(set(D))
    
    if len(D) == q + 1:
        is_sidon_mod = verify_sidon_mod(D, m)
        is_sidon_int = verify_sidon(D)
        
        max_elem = max(D)
        N_covers = max_elem + 1  # This Singer set fits in {0,...,max_elem}
        
        if is_sidon_int:
            ratio = len(D) / np.sqrt(N_covers)
            singer_results.append((q, m, len(D), N_covers, ratio))
            print(f"  q={q:>3}: Singer set of {len(D)} elements in {{0,...,{max_elem}}} = {{0,...,{m-2}}}")
            print(f"         N_covers={N_covers}, sqrt(N)={np.sqrt(N_covers):.2f}, ratio={ratio:.3f}")
            print(f"         Sidon(mod {m})={is_sidon_mod}, Sidon(int)={is_sidon_int}")
            if len(D) <= 20:
                print(f"         Set: {D}")
            else:
                print(f"         Set: {D[:10]}...{D[-5:]}")

print()
print("COVERING TABLE: Singer Sidon sets covering {0,...,N-1}")
print("=" * 60)
print(f"{'q':>4} | {'m=q^2+q+1':>10} | {'|D|=q+1':>8} | {'N covered':>10} | {'sqrt(N)':>8} | {'|D|/sqrt(N)':>12}")
print("-" * 60)

for q, m, size, N_cov, ratio in singer_results:
    sqN = np.sqrt(N_cov)
    above = ">=!" if size >= sqN else "< "
    print(f"{q:>4} | {m:>10} | {size:>8} | {N_cov:>10} | {sqN:>8.2f} | {ratio:>12.4f} {above}")

# =================================================================
# For specific N values, find the best Singer construction
# =================================================================
print()
print("ANALYSIS FOR KEY N VALUES")
print("=" * 60)

for N_target in [100, 200, 500, 750, 1000, 1024, 2000, 5000, 10000]:
    # Find largest Singer set fitting in {0,...,N_target-1}
    best_q = None
    best_set = []
    
    for q, m, size, N_cov, ratio in singer_results:
        if N_cov <= N_target and size > len(best_set):
            # Reconstruct the set
            g = find_primitive_root(m)
            D = sorted(set(pow(g, t * (q + 1), m) if t > 0 else 1 for t in range(q + 1)))
            if verify_sidon(D) and max(D) < N_target:
                best_set = D
                best_q = q
    
    if best_set:
        sqN = np.sqrt(N_target)
        ratio = len(best_set) / sqN
        above = ">=" if len(best_set) >= sqN else "< "
        print(f"  N={N_target:>5}: Singer(q={best_q}) gives |D|={len(best_set)} {above} sqrt(N)={sqN:.2f} (ratio={ratio:.3f})")
    else:
        print(f"  N={N_target:>5}: No Singer construction found in range")

# =================================================================
# Massive randomized search for N=750 and N=1000
# =================================================================
print()
print("MASSIVE RANDOMIZED GREEDY SEARCH")
print("=" * 60)

for N in [750, 1000]:
    sqN = np.sqrt(N)
    print(f"\nN = {N}, sqrt(N) = {sqN:.2f}")
    
    best = []
    best_trial = -1
    
    for trial in range(2000):
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
        if len(S) > len(best):
            best = sorted(S)
            best_trial = trial
            if len(best) >= sqN:
                print(f"  Trial {trial}: Found {len(best)} >= sqrt(N)!")
                break
    
    ratio = len(best) / sqN
    print(f"  Best after 2000 trials: {len(best)} (ratio={ratio:.3f}, found at trial {best_trial})")
    assert verify_sidon(best)
    print(f"  Set: {best[:15]}{'...' if len(best) > 15 else ''}")
