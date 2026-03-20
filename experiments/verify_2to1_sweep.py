"""
Systematic verification of the 2-to-1 map axiom for Erdős Problem 530.

For every maximal Sidon set S ⊂ [N], verify that there exists a function
f: A\S → S×S (mapping blocked elements to witness pairs) with fiber ≤ 2.

Uses network-flow / backtracking to check existence of capacitated assignment.
"""

from itertools import combinations
from collections import defaultdict
import time


def is_sidon(S):
    """Check if S is a Sidon (B₂) set: all pairwise sums distinct."""
    S = sorted(S)
    sums = set()
    for i in range(len(S)):
        for j in range(i, len(S)):
            s = S[i] + S[j]
            if s in sums:
                return False
            sums.add(s)
    return True


def sum_set(S):
    """Compute S+S = {a+b : a,b ∈ S} as a dict mapping sum → set of pairs."""
    S = sorted(S)
    result = defaultdict(list)
    for a in S:
        for b in S:
            result[a + b].append((a, b))
    return result


def find_maximal_sidon_sets(N):
    """Find all maximal Sidon sets in {1,...,N} via backtracking."""
    elements = list(range(1, N + 1))
    maximal_sets = []
    all_sidon = []

    # Generate all Sidon sets by backtracking
    def backtrack(start, current):
        # Check if current can be extended
        can_extend = False
        for x in range(start, N + 1):
            if is_sidon(current + [x]):
                can_extend = True
                current.append(x)
                backtrack(x + 1, current)
                current.pop()
        if not can_extend and len(current) >= 2:
            all_sidon.append(tuple(sorted(current)))

    backtrack(1, [])
    # Remove duplicates and non-maximal
    all_sidon = list(set(all_sidon))
    
    # Filter to truly maximal (not contained in any larger Sidon set in [N])
    maximal = []
    for S in all_sidon:
        S_set = set(S)
        is_max = True
        for x in range(1, N + 1):
            if x not in S_set:
                if is_sidon(list(S_set | {x})):
                    is_max = False
                    break
        if is_max:
            maximal.append(S)
    
    return maximal


def compute_witness_pairs(S, N):
    """
    For each blocked element x ∈ {1,...,N} \ S, compute the set of
    witness pairs (a,b) ∈ S×S that justify blocking x.
    
    x is blocked if S ∪ {x} is not Sidon, meaning ∃ collision:
      x + c = a + b  where c ∈ S, {a,b} ⊆ S, {x,c} ≠ {a,b} as multisets
      (or x + x = a + b if a ≠ b)
    
    The witness pair we charge x to is (a,b).
    """
    S_set = set(S)
    S_list = sorted(S)
    ss = sum_set(S_list)
    
    blocked = {}  # x → set of witness pairs (a,b)
    
    for x in range(1, N + 1):
        if x in S_set:
            continue
        
        # Check if x is blocked (S ∪ {x} not Sidon)
        if is_sidon(list(S_set | {x})):
            continue
        
        pairs = set()
        
        # Type 1: x + c = a + b where c ∈ S, (a,b) ∈ S×S
        for c in S_list:
            target = x + c
            if target in ss:
                for (a, b) in ss[target]:
                    # Exclude trivial: if x=a and c=b, or x=b and c=a
                    if (x == a and c == b) or (x == b and c == a):
                        continue
                    # Also exclude c=a=b (c appears twice) unless genuinely blocked
                    pairs.add((a, b))
        
        # Type 2: x + x = a + b where a,b ∈ S, a ≠ b
        target2 = 2 * x
        if target2 in ss:
            for (a, b) in ss[target2]:
                if a != b:  # Need distinct elements
                    pairs.add((a, b))
                elif a == b and a in S_set:
                    # 2x = 2a means x = a, but x ∉ S, contradiction
                    pass
        
        if pairs:
            blocked[x] = pairs
    
    return blocked


def check_two_to_one_map(blocked, capacity=2):
    """
    Check if there exists an assignment f: blocked_elements → pairs
    where each blocked element maps to one of its witness pairs,
    and each pair receives at most `capacity` elements.
    
    Uses backtracking with constraint propagation.
    Returns (True, assignment_dict) or (False, None).
    """
    if not blocked:
        return True, {}
    
    elements = sorted(blocked.keys())
    pairs_usage = defaultdict(int)
    assignment = {}
    
    # Sort by number of choices (most constrained first = MRV heuristic)
    elements.sort(key=lambda x: len(blocked[x]))
    
    def backtrack(idx):
        if idx == len(elements):
            return True
        
        x = elements[idx]
        for pair in sorted(blocked[x]):
            if pairs_usage[pair] < capacity:
                pairs_usage[pair] += 1
                assignment[x] = pair
                if backtrack(idx + 1):
                    return True
                pairs_usage[pair] -= 1
                del assignment[x]
        
        return False
    
    if backtrack(0):
        return True, dict(assignment)
    return False, None


def analyze_fibers(assignment):
    """Compute fiber sizes for an assignment."""
    fibers = defaultdict(list)
    for x, pair in assignment.items():
        fibers[pair].append(x)
    max_fiber = max(len(v) for v in fibers.values()) if fibers else 0
    return max_fiber, dict(fibers)


def main():
    print("=" * 70)
    print("SYSTEMATIC VERIFICATION: 2-to-1 Map Axiom for Erdős 530")
    print("=" * 70)
    
    results = []
    
    for N in range(4, 31):
        t0 = time.time()
        maximal_sets = find_maximal_sidon_sets(N)
        t1 = time.time()
        
        all_feasible = True
        max_blocked = 0
        max_pairs_needed = 0
        worst_case = None
        num_sets = len(maximal_sets)
        
        for S in maximal_sets:
            S_set = set(S)
            blocked = compute_witness_pairs(S, N)
            num_blocked = len(blocked)
            max_blocked = max(max_blocked, num_blocked)
            
            if num_blocked == 0:
                continue
            
            feasible, assignment = check_two_to_one_map(blocked, capacity=2)
            
            if not feasible:
                all_feasible = False
                worst_case = S
                print(f"\n  *** COUNTEREXAMPLE at N={N}, S={S} ***")
                print(f"      Blocked: {sorted(blocked.keys())}")
                for x, pairs in sorted(blocked.items()):
                    print(f"      x={x}: {sorted(pairs)}")
                break
            else:
                max_fiber, fibers = analyze_fibers(assignment)
                # Count how many pairs have fiber = 2
                pairs_at_2 = sum(1 for v in fibers.values() if len(v) == 2)
                max_pairs_needed = max(max_pairs_needed, pairs_at_2)
        
        t2 = time.time()
        
        status = "✓" if all_feasible else "✗"
        ratio = max_blocked / (len(maximal_sets[0]) ** 2) if maximal_sets else 0
        
        print(f"N={N:3d}: {status}  |S|={len(maximal_sets[0]) if maximal_sets else 0:2d}, "
              f"#maximal={num_sets:4d}, max_blocked={max_blocked:3d}, "
              f"|blocked|/|S|²={ratio:.2f}, "
              f"time={t2-t0:.2f}s")
        
        results.append({
            'N': N,
            'feasible': all_feasible,
            'num_maximal': num_sets,
            'S_size': len(maximal_sets[0]) if maximal_sets else 0,
            'max_blocked': max_blocked,
            'ratio': ratio,
            'time': t2 - t0,
        })
        
        if not all_feasible:
            break
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if all(r['feasible'] for r in results):
        print(f"\n✓ 2-to-1 map EXISTS for ALL maximal Sidon sets in [N], N=4..{results[-1]['N']}")
        print(f"\nKey statistics:")
        print(f"  Max |blocked|/|S|² ratio: {max(r['ratio'] for r in results):.3f}")
        print(f"  (Must be ≤ 2.0 for the axiom to hold)")
    else:
        print(f"\n✗ COUNTEREXAMPLE FOUND - the axiom is FALSE!")
    
    # Print detailed table
    print(f"\n{'N':>3} {'|S|':>4} {'#max':>6} {'max_bl':>7} {'ratio':>7} {'time':>8}")
    print("-" * 45)
    for r in results:
        print(f"{r['N']:3d} {r['S_size']:4d} {r['num_maximal']:6d} "
              f"{r['max_blocked']:7d} {r['ratio']:7.3f} {r['time']:8.2f}s")
    
    # Analysis: check if blocked / |S|² ≤ 2 always holds
    print(f"\nCritical ratio max(|blocked|/|S|²) = {max(r['ratio'] for r in results):.4f}")
    print(f"The axiom requires this to be achievable with fiber ≤ 2.")
    
    return results


if __name__ == "__main__":
    main()
