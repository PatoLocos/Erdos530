"""
Singer difference set construction via GF(q^3) finite field arithmetic.
For prime q, constructs a B_2 (Sidon) set of size q+1 in Z_{q^2+q+1}.

The Singer set is a PERFECT difference set, so it's automatically
a Sidon set over integers (all pairwise differences distinct).
"""
import numpy as np
from sympy import isprime

def find_irreducible_cubic(q):
    """Find an irreducible monic cubic x^3 + ax + b over GF(q)."""
    for a in range(q):
        for b in range(1, q):  # b=0 gives x^3+ax = x(x^2+a), reducible
            has_root = any((x*x*x + a*x + b) % q == 0 for x in range(q))
            if not has_root:
                return (a, b)
    return None

def gf_q3_multiply(p1, p2, q, c1, c0):
    """Multiply two elements of GF(q^3) = GF(q)[x]/(x^3 + c1*x + c0).
    Elements are triples (a0, a1, a2) representing a0 + a1*x + a2*x^2.
    Reduction: x^3 = -c1*x - c0 (mod q)."""
    a0, a1, a2 = p1
    b0, b1, b2 = p2
    
    # Standard polynomial multiplication (degree up to 4)
    r0 = a0*b0
    r1 = a0*b1 + a1*b0
    r2 = a0*b2 + a1*b1 + a2*b0
    r3 = a1*b2 + a2*b1
    r4 = a2*b2
    
    # Reduce x^3 = -c1*x - c0 and x^4 = -c1*x^2 - c0*x
    r0 = (r0 - r3 * c0) % q
    r1 = (r1 - r3 * c1 - r4 * c0) % q
    r2 = (r2 - r4 * c1) % q
    
    return (r0, r1, r2)

def gf_q3_pow(base, exp, q, c1, c0):
    """Compute base^exp in GF(q^3) via repeated squaring."""
    result = (1, 0, 0)  # Multiplicative identity
    b = base
    while exp > 0:
        if exp & 1:
            result = gf_q3_multiply(result, b, q, c1, c0)
        b = gf_q3_multiply(b, b, q, c1, c0)
        exp >>= 1
    return result

def find_primitive_element(q, c1, c0):
    """Find a primitive element of GF(q^3)* = GF(q)[x]/(x^3+c1*x+c0).
    A primitive element has multiplicative order exactly q^3-1."""
    order = q*q*q - 1
    pfs = list(set(prime_factors(order)))
    
    # Try simple candidates first: (a0, a1, a2) with small coefficients
    for a1 in range(q):
        for a0 in range(q):
            for a2 in range(q):
                cand = (a0, a1, a2)
                if cand == (0, 0, 0):
                    continue
                is_prim = True
                for p in pfs:
                    if gf_q3_pow(cand, order // p, q, c1, c0) == (1, 0, 0):
                        is_prim = False
                        break
                if is_prim:
                    return cand
    return None

def singer_sidon_set(q):
    """Construct Singer Sidon set of size q+1 in {0,...,q^2+q} for prime q.
    
    Method:
    1. Find irreducible cubic f(x) = x^3 + c1*x + c0 over GF(q)
    2. Work in GF(q^3) = GF(q)[x]/(f(x))
    3. Find a PRIMITIVE element alpha of GF(q^3)*
    4. Compute beta = alpha^{q-1}, which has order m = q^2+q+1
    5. Singer set D = {i : beta^i lies in 2D subspace {a+bx : a,b in GF(q)}}
       i.e., the x^2 coefficient of beta^i is 0
    """
    if not isprime(q):
        return None, None
    
    m = q*q + q + 1
    order = q*q*q - 1
    
    # Find irreducible cubic
    coeffs = find_irreducible_cubic(q)
    if coeffs is None:
        return None, None
    c1, c0 = coeffs
    
    # Find genuine primitive element of GF(q^3)*
    alpha = find_primitive_element(q, c1, c0)
    if alpha is None:
        return None, None
    
    # Collect Singer set using alpha directly (not beta).
    # For each i, alpha^i ∈ V (2D subspace with x^2=0) gives projective index i mod m.
    # This correctly handles q ≡ 1 (mod 3) where gcd(q-1, m) = 3.
    D = set()
    power = (1, 0, 0)  # alpha^0 = 1
    for i in range(q*q*q - 1):
        if power[2] == 0:  # x^2 coefficient is 0 → lies in V
            D.add(i % m)
        power = gf_q3_multiply(power, alpha, q, c1, c0)
    
    return sorted(D), m

def prime_factors(n):
    """Return prime factors of n."""
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors

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

def verify_perfect_diff_set(D, m):
    """Verify D is a perfect difference set mod m."""
    diffs = {}
    for i in range(len(D)):
        for j in range(len(D)):
            if i != j:
                d = (D[i] - D[j]) % m
                if d > 0:
                    diffs[d] = diffs.get(d, 0) + 1
    # Each non-zero difference should appear exactly once
    return all(v == 1 for v in diffs.values()) and len(diffs) == m - 1

# ============================================
# Main: construct and verify Singer sets
# ============================================
print("SINGER SIDON SETS VIA GF(q^3)")
print("=" * 70)

results = []

for q in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]:
    if not isprime(q):
        continue
    m = q*q + q + 1
    D, mod = singer_sidon_set(q)
    
    if D is None:
        print(f"  q={q:>2}: FAILED to construct")
        continue
    
    is_sidon = verify_sidon(D)
    is_pds = verify_perfect_diff_set(D, m) if len(D) <= 40 else "skipped"
    
    max_elem = max(D)
    N_fit = max_elem + 1
    sqN = np.sqrt(N_fit)
    ratio = len(D) / sqN
    
    results.append((q, m, len(D), max_elem, ratio, is_sidon))
    
    print(f"  q={q:>2}: |D|={len(D):>3}, mod m={m:>5}, max={max_elem:>5}, "
          f"Sidon={is_sidon}, PDS={is_pds}")
    if q <= 7:
        print(f"        Set: {D}")

# Summary table
print("\n" + "=" * 70)
print("SINGER SET COVERAGE OF {0,...,N-1}")
print("=" * 70)
print(f"{'q':>4} | {'m':>6} | {'|D|':>4} | {'max_elem':>8} | {'N covered':>9} | {'sqrt(N)':>8} | {'ratio':>6} | {'Sidon':>5}")
print("-" * 70)

for q, m, size, max_elem, ratio, is_sidon in results:
    N_cov = max_elem + 1
    sqN = np.sqrt(N_cov)
    check = ">=" if size >= sqN else "< "
    print(f"{q:>4} | {m:>6} | {size:>4} | {max_elem:>8} | {N_cov:>9} | {sqN:>8.2f} | {ratio:>6.3f} | {'Y' if is_sidon else 'N':>5} {check}")

# Coverage for target N values
print("\n" + "=" * 70)
print("BEST SINGER SET FOR TARGET N VALUES")
print("=" * 70)

for N_target in [50, 100, 200, 500, 750, 1000, 2000, 5000, 10000]:
    sqN = np.sqrt(N_target)
    best = None
    for q, m, size, max_elem, ratio, is_sidon in results:
        if is_sidon and max_elem < N_target:
            if best is None or size > best[2]:
                best = (q, m, size, max_elem)
    
    if best:
        q, m, size, max_elem = best
        ratio = size / sqN
        check = ">=" if size >= sqN else "< "
        print(f"  N={N_target:>5}: Singer(q={q:>2}) gives {size:>3} elem (max={max_elem:>5}) "
              f"{check} sqrt(N)={sqN:.2f} (ratio={ratio:.3f})")
    else:
        print(f"  N={N_target:>5}: No Singer set found")
