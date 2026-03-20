"""
Test whether the axiom |A\S| ≤ 2|S|² can fail for GENERAL A ⊆ ℕ
(not just intervals {1,...,N}).

Strategy: Take a spread-out Sidon set S, compute ALL elements blocked by S,
set A = S ∪ {all blocked}, then check if |A\S| > 2|S|².
"""

from collections import defaultdict
import sys


def is_sidon(S):
    S = sorted(S)
    sums = set()
    for i in range(len(S)):
        for j in range(i, len(S)):
            s = S[i] + S[j]
            if s in sums:
                return False
            sums.add(s)
    return True


def count_all_blocked(S):
    """
    Count ALL natural numbers x ∉ S such that S ∪ {x} is not Sidon.
    Returns the set of blocked elements and their witnesses.
    """
    S = sorted(S)
    S_set = set(S)
    k = len(S)
    
    # Compute S+S (all pairwise sums including a+a)
    sum_pairs = {}  # σ → list of (a,b) with a ≤ b
    for i, a in enumerate(S):
        for j in range(i, k):
            b = S[j]
            sigma = a + b
            if sigma not in sum_pairs:
                sum_pairs[sigma] = []
            sum_pairs[sigma].append((a, b))
    
    blocked = set()
    
    # Type 1: x + c = a + b, where a,b,c ∈ S, x = a+b-c
    # Non-trivial: {x,c} ≠ {a,b} as multisets
    for sigma, pairs in sum_pairs.items():
        for (a, b) in pairs:
            for c in S:
                x = sigma - c
                if x < 0 or x in S_set:
                    continue
                # Check non-trivial: {x,c} ≠ {a,b}
                if (x == a and c == b) or (x == b and c == a):
                    continue
                if a == b and x == a:
                    continue
                blocked.add(x)
    
    # Type 2: 2x = a + b, a ≠ b, a,b ∈ S
    for sigma, pairs in sum_pairs.items():
        for (a, b) in pairs:
            if a != b and sigma % 2 == 0:
                x = sigma // 2
                if x not in S_set:
                    blocked.add(x)
    
    return blocked


def make_spread_sidon(k, spread="exponential"):
    """Create a Sidon set of size k with elements spread far apart."""
    if spread == "exponential":
        # Try powers of a base
        for base in [10, 7, 5, 3, 2]:
            S = [base**i for i in range(k)]
            if is_sidon(S):
                return S
    elif spread == "perfect":
        # Known perfect difference sets give dense Sidon sets
        # For comparison: {0,1,3,7,12,20} for k=6
        known = {
            3: [0, 1, 3],
            4: [0, 1, 3, 7],
            5: [0, 1, 3, 7, 12],
            6: [0, 1, 3, 7, 12, 20],
            7: [0, 1, 3, 7, 12, 20, 30],
        }
        if k in known:
            S = known[k]
            if is_sidon(S):
                return S
    elif spread == "quadratic":
        # Elements grow quadratically
        S = [i*i for i in range(k)]
        # Likely not Sidon for large k, but check
        if is_sidon(S):
            return S
    elif spread == "superexp":
        # Very spread out: 0, 1, M, M², M³, ...
        M = 1000
        S = [M**i if i > 0 else 0 for i in range(k)]
        S[1] = 1  # keep 0, 1
        if is_sidon(S):
            return S
    
    # Greedy construction with large gaps
    S = [0]
    gap = 1
    for _ in range(k - 1):
        candidate = S[-1] + gap
        while not is_sidon(S + [candidate]):
            candidate += 1
        S.append(candidate)
        gap = max(gap, candidate)  # exponentially growing gaps
    return S


def greedy_spread_sidon(k, min_gap=1):
    """Greedy Sidon set construction with minimum gap between elements."""
    S = [0]
    candidate = min_gap
    while len(S) < k:
        if is_sidon(S + [candidate]):
            S.append(candidate)
            candidate += min_gap
        else:
            candidate += 1
    return S


def main():
    print("=" * 80)
    print("TESTING AXIOM |A\\S| ≤ 2|S|² FOR GENERAL A (NOT JUST INTERVALS)")
    print("=" * 80)
    print()
    
    # Test different Sidon set constructions
    constructions = [
        ("Dense (greedy gap=1)", lambda k: greedy_spread_sidon(k, 1)),
        ("Medium (greedy gap=k)", lambda k: greedy_spread_sidon(k, k)),
        ("Spread (greedy gap=k²)", lambda k: greedy_spread_sidon(k, k*k)),
        ("Exponential (base 10)", lambda k: make_spread_sidon(k, "exponential")),
        ("Super-exp (base 1000)", lambda k: make_spread_sidon(k, "superexp")),
    ]
    
    max_k = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    
    print(f"{'Construction':<28} {'k':>3} {'|blocked|':>10} {'2k²':>6} "
          f"{'ratio':>7} {'status':>8} {'max(S)':>12}")
    print("-" * 90)
    
    found_counter = False
    
    for name, builder in constructions:
        for k in range(3, max_k + 1):
            try:
                S = builder(k)
            except Exception:
                continue
                
            if not is_sidon(S):
                continue
            
            blocked = count_all_blocked(S)
            b = len(blocked)
            cap = 2 * k * k
            ratio = b / cap if cap > 0 else 0
            status = "✓" if b <= cap else "✗ FAIL"
            
            if b > cap:
                found_counter = True
            
            print(f"{name:<28} {k:3d} {b:10d} {cap:6d} "
                  f"{ratio:7.3f} {status:>8} {max(S):12d}")
            
            if b > cap:
                print(f"  *** COUNTEREXAMPLE! S = {S}")
                print(f"  *** |blocked| = {b} > 2k² = {cap}")
                # Verify maximality
                A = set(S) | blocked
                S_set = set(S)
                is_max = True
                for x in A:
                    if x not in S_set and is_sidon(list(S_set | {x})):
                        is_max = False
                        print(f"  *** WARNING: x={x} can be added to S! NOT MAXIMAL!")
                        break
                if is_max:
                    print(f"  *** S IS maximal in A = S ∪ blocked. AXIOM IS FALSE!")
        print()
    
    if not found_counter:
        print("\n✓ No counterexample found. Axiom appears to hold for tested cases.")
    
    return found_counter


if __name__ == "__main__":
    main()
