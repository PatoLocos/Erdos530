"""
Hybrid Singer+Greedy Extension Analysis
========================================
The key experiment for Problem 530: start from a Singer difference set
(optimal at certain N), then greedily extend beyond those N values.

If extra elements added scale like c * N^{1/4}, the upper bound is tight.
If they stay O(1), then F_2(N) = sqrt(N) + O(1).
"""

import math, time, csv

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def singer_set_for_prime(q):
    """Construct Singer difference set for prime q via GF(q^3)."""
    p = q
    n = q * q + q + 1

    # Find irreducible cubic x^3 + ax + b over GF(p)
    irr = None
    for a in range(p):
        for b in range(1, p):
            has_root = any((x**3 + a * x + b) % p == 0 for x in range(p))
            if not has_root:
                irr = (a, b)
                break
        if irr:
            break
    if not irr:
        return None

    a_coeff, b_coeff = irr

    def mul_gf3(u, v):
        r = [0] * 5
        for i in range(3):
            for j in range(3):
                r[i + j] = (r[i + j] + u[i] * v[j]) % p
        for deg in [4, 3]:
            if r[deg] != 0:
                c = r[deg]
                r[deg] = 0
                r[deg - 2] = (r[deg - 2] - a_coeff * c) % p
                r[deg - 3] = (r[deg - 3] - b_coeff * c) % p
        return [r[0] % p, r[1] % p, r[2] % p]

    def pow_gf3(base, exp):
        result = [1, 0, 0]
        b = list(base)
        while exp > 0:
            if exp & 1:
                result = mul_gf3(result, b)
            b = mul_gf3(b, b)
            exp >>= 1
        return result

    order = p * p * p - 1
    alpha = None
    for c1 in range(p):
        for c2 in range(p):
            for c0 in range(p):
                g = [c0, c1, c2]
                if g == [0, 0, 0]:
                    continue
                temp = order
                factors = set()
                d = 2
                while d * d <= temp:
                    while temp % d == 0:
                        factors.add(d)
                        temp //= d
                    d += 1
                if temp > 1:
                    factors.add(temp)

                is_prim = all(pow_gf3(g, order // r) != [1, 0, 0] for r in factors)
                if is_prim:
                    alpha = g
                    break
            if alpha:
                break
        if alpha:
            break

    if not alpha:
        return None

    dset = []
    elem = [1, 0, 0]
    for j in range(n):
        if elem[2] == 0:
            dset.append(j)
        elem = mul_gf3(elem, alpha)

    return sorted(dset)


def greedy_extend(base_set, N):
    """Given a Sidon set in [0,M], greedily add elements from [0,N] maintaining B2."""
    result = sorted(base_set)
    sums = set()
    for i in range(len(result)):
        for j in range(i, len(result)):
            sums.add(result[i] + result[j])

    added = 0
    for c in range(N + 1):
        if c in set(result):
            continue
        ok = True
        for s in result:
            if (c + s) in sums:
                ok = False
                break
        if ok:
            for s in result:
                sums.add(c + s)
            sums.add(2 * c)
            result.append(c)
            added += 1

    return sorted(result), added


def greedy_from_scratch(N):
    """Pure greedy Sidon set in [0,N] (no Singer base)."""
    result = [0]
    sums = {0}
    for c in range(1, N + 1):
        ok = True
        for s in result:
            if (c + s) in sums:
                ok = False
                break
        if ok:
            for s in result:
                sums.add(c + s)
            sums.add(2 * c)
            result.append(c)
    return result


# ============================================================
# EXPERIMENT 1: Hybrid extension at Singer points
# ============================================================
print("EXPERIMENT 1: HYBRID SINGER+GREEDY AT SINGER POINTS")
print("=" * 78)
print()
print("Singer gives q+1 elements in [0, q^2+q]. What if we extend to N = q^2+q?")
print("(i.e., we ask: can we ADD any elements to Singer in its own range?)")
print()
print(f"{'q':>4} {'singer':>6} {'hybrid':>6} {'extra':>5} {'N':>8} {'sqrtN':>8} {'gap':>8}")
print("-" * 78)

rows1 = []
primes = [p for p in range(2, 80) if is_prime(p)]

for q in primes:
    singer = singer_set_for_prime(q)
    if singer is None or len(singer) != q + 1:
        continue
    
    N = q * q + q
    t0 = time.time()
    hybrid, extra = greedy_extend(singer, N)
    elapsed = time.time() - t0
    
    sqrtN = math.sqrt(N)
    gap = len(hybrid) - sqrtN
    
    print(f"{q:4d} {len(singer):6d} {len(hybrid):6d} {extra:5d} {N:8d} {sqrtN:8.2f} {gap:8.3f}")
    rows1.append({
        'q': q, 'singer': len(singer), 'hybrid': len(hybrid),
        'extra': extra, 'N': N, 'sqrtN': sqrtN, 'gap': gap,
        'time': elapsed
    })

# ============================================================
# EXPERIMENT 2: Extension beyond Singer range
# ============================================================
print()
print()
print("EXPERIMENT 2: EXTEND SINGER INTO [0, 2N] AND [0, 4N]")
print("=" * 78)
print()
print("Start from Singer in [0, q^2+q], extend to multiplied ranges.")
print("If extra/N^{1/4} stabilizes, the upper bound error term is real.")
print()
print(f"{'q':>4} {'N':>8} {'|S|':>5} {'2N_hyb':>7} {'2N_ext':>7} {'4N_hyb':>7} {'4N_ext':>7} {'2N_r':>7} {'4N_r':>7}")
print("-" * 78)

rows2 = []
for q in primes[:15]:  # up to q=47
    singer = singer_set_for_prime(q)
    if singer is None or len(singer) != q + 1:
        continue
    
    N0 = q * q + q
    
    # Extend to 2N
    N2 = 2 * N0
    hyb2, ext2 = greedy_extend(singer, N2)
    r2 = ext2 / (N2 ** 0.25) if N2 > 0 else 0
    
    # Extend to 4N
    N4 = 4 * N0
    hyb4, ext4 = greedy_extend(singer, N4)
    r4 = ext4 / (N4 ** 0.25) if N4 > 0 else 0
    
    print(f"{q:4d} {N0:8d} {q+1:5d} {len(hyb2):7d} {ext2:7d} {len(hyb4):7d} {ext4:7d} {r2:7.3f} {r4:7.3f}")
    rows2.append({
        'q': q, 'N0': N0, 'singer': q+1,
        'hyb2': len(hyb2), 'ext2': ext2, 'N2': N2,
        'hyb4': len(hyb4), 'ext4': ext4, 'N4': N4,
        'ratio2': r2, 'ratio4': r4
    })

# ============================================================
# EXPERIMENT 3: Pure greedy vs Singer at same N
# ============================================================
print()
print()
print("EXPERIMENT 3: GREEDY FROM SCRATCH vs SINGER vs HYBRID")
print("=" * 78)
print()
print(f"{'q':>4} {'N':>8} {'greedy':>7} {'singer':>7} {'hybrid':>7} {'G-S':>5} {'H-S':>5} {'H/sqrtN':>8}")
print("-" * 78)

rows3 = []
for q in primes[:12]:  # up to q=37
    singer = singer_set_for_prime(q)
    if singer is None or len(singer) != q + 1:
        continue
    
    N = q * q + q
    
    greedy = greedy_from_scratch(N)
    hybrid, ext = greedy_extend(singer, N)
    sqrtN = math.sqrt(N)
    
    print(f"{q:4d} {N:8d} {len(greedy):7d} {len(singer):7d} {len(hybrid):7d} {len(greedy)-len(singer):5d} {ext:5d} {len(hybrid)/sqrtN:8.4f}")
    rows3.append({
        'q': q, 'N': N, 'greedy': len(greedy), 'singer': len(singer),
        'hybrid': len(hybrid), 'extra': ext, 'ratio': len(hybrid)/sqrtN
    })

# ============================================================
# EXPERIMENT 4: Error term between Singer points
# ============================================================
print()
print()
print("EXPERIMENT 4: GREEDY F2(N) FOR N BETWEEN SINGER POINTS")
print("=" * 78)
print()
print("For N not at Singer points, measure greedy F2(N) and error = F2(N) - sqrt(N)")
print()
print(f"{'N':>7} {'greedy':>7} {'sqrtN':>8} {'error':>8} {'N^1/4':>7} {'err/N14':>8} {'nearest_S':>10}")
print("-" * 78)

# Singer N values for primes up to 47
singer_Ns = {}
for q in primes[:15]:
    s = singer_set_for_prime(q)
    if s and len(s) == q+1:
        singer_Ns[q*q+q] = q+1

# Test N values between Singer points and at midpoints
test_Ns = sorted(set(
    list(range(10, 200, 10)) +
    list(range(200, 1000, 50)) +
    list(range(1000, 3000, 100)) +
    list(singer_Ns.keys())
))

rows4 = []
for N in test_Ns:
    greedy = greedy_from_scratch(N)
    sqrtN = math.sqrt(N)
    err = len(greedy) - sqrtN
    Nq = N ** 0.25
    
    # Find nearest Singer point
    nearest = min(singer_Ns.keys(), key=lambda sn: abs(sn - N))
    is_singer = "SINGER" if N in singer_Ns else ""
    
    print(f"{N:7d} {len(greedy):7d} {sqrtN:8.2f} {err:8.3f} {Nq:7.2f} {err/Nq:8.4f} {is_singer:>10}")
    rows4.append({
        'N': N, 'greedy': len(greedy), 'sqrtN': sqrtN,
        'error': err, 'Nq': Nq, 'err_ratio': err/Nq,
        'is_singer': N in singer_Ns
    })

# ============================================================
# STATISTICAL SUMMARY
# ============================================================
print()
print()
print("=" * 78)
print("STATISTICAL SUMMARY")
print("=" * 78)
print()

# 1. Can we extend Singer in its own range?
if rows1:
    extras = [r['extra'] for r in rows1]
    print(f"1. Singer extensibility within [0, q^2+q]:")
    print(f"   Extra elements added: min={min(extras)}, max={max(extras)}, mean={sum(extras)/len(extras):.1f}")
    if max(extras) == 0:
        print(f"   >>> SINGER IS MAXIMAL IN ITS OWN RANGE (cannot add any elements)")
    else:
        print(f"   >>> Singer is NOT maximal — can be improved!")
    print()

# 2. Extension beyond range
if rows2:
    print(f"2. Extension ratios (extra / N^{{1/4}}):")
    for r in rows2:
        print(f"   q={r['q']:3d}: 2N ratio={r['ratio2']:.3f}, 4N ratio={r['ratio4']:.3f}")
    r2s = [r['ratio2'] for r in rows2 if r['ratio2'] > 0]
    r4s = [r['ratio4'] for r in rows2 if r['ratio4'] > 0]
    if r2s:
        print(f"   Mean 2N ratio: {sum(r2s)/len(r2s):.3f}")
    if r4s:
        print(f"   Mean 4N ratio: {sum(r4s)/len(r4s):.3f}")
    print()

# 3. Greedy vs Singer vs Hybrid
if rows3:
    print(f"3. Greedy vs Singer vs Hybrid at Singer points N = q^2+q:")
    for r in rows3:
        print(f"   q={r['q']:3d}: Greedy={r['greedy']}, Singer={r['singer']}, Hybrid={r['hybrid']}, Hybrid/sqrtN={r['ratio']:.4f}")
    print()

# 4. Error term statistics
if rows4:
    singer_errs = [r['error'] for r in rows4 if r['is_singer']]
    non_singer_errs = [r['error'] for r in rows4 if not r['is_singer'] and r['N'] >= 100]
    large_errs = [r['err_ratio'] for r in rows4 if r['N'] >= 500]
    
    print(f"4. Error term F2(N) - sqrt(N) analysis:")
    if singer_errs:
        print(f"   At Singer points: min={min(singer_errs):.3f}, max={max(singer_errs):.3f}, mean={sum(singer_errs)/len(singer_errs):.3f}")
    if non_singer_errs:
        print(f"   Between Singer pts: min={min(non_singer_errs):.3f}, max={max(non_singer_errs):.3f}, mean={sum(non_singer_errs)/len(non_singer_errs):.3f}")
    if large_errs:
        print(f"   err/N^{{1/4}} for N>=500: min={min(large_errs):.4f}, max={max(large_errs):.4f}, mean={sum(large_errs)/len(large_errs):.4f}")
    print()

# Save all data
with open('hybrid_analysis.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['q','singer','hybrid','extra','N','sqrtN','gap','time'])
    w.writeheader()
    w.writerows(rows1)

with open('extension_analysis.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['q','N0','singer','hyb2','ext2','N2','hyb4','ext4','N4','ratio2','ratio4'])
    w.writeheader()
    w.writerows(rows2)

with open('greedy_error_term.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['N','greedy','sqrtN','error','Nq','err_ratio','is_singer'])
    w.writeheader()
    w.writerows(rows4)

print("Data saved to: hybrid_analysis.csv, extension_analysis.csv, greedy_error_term.csv")
