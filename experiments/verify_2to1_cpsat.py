"""
Systematic verification of the 2-to-1 map axiom for Erdős Problem 530
using OR-Tools CP-SAT solver.

For every maximal Sidon set S ⊂ [N], we verify existence of a function
f: (A\S) → S×S with fiber size ≤ 2.

This is the key axiom `kss_two_to_one_map_exists` in KSS_Proven.lean.
"""

from ortools.sat.python import cp_model
from itertools import combinations
from collections import defaultdict
import time
import sys
import csv


def is_sidon(S):
    """Check if S is a Sidon (B₂) set."""
    S = sorted(S)
    sums = set()
    for i in range(len(S)):
        for j in range(i, len(S)):
            s = S[i] + S[j]
            if s in sums:
                return False
            sums.add(s)
    return True


def find_all_maximal_sidon_sets(N):
    """Find all maximal Sidon subsets of {1,...,N} via backtracking."""
    results = []
    
    def backtrack(start, current):
        can_extend = False
        for x in range(start, N + 1):
            if is_sidon(current + [x]):
                can_extend = True
                current.append(x)
                backtrack(x + 1, current)
                current.pop()
        if not can_extend and len(current) >= 2:
            results.append(tuple(sorted(current)))
    
    backtrack(1, [])
    results = list(set(results))
    
    # Filter to truly maximal
    maximal = []
    for S in results:
        S_set = set(S)
        is_max = True
        for x in range(1, N + 1):
            if x not in S_set and is_sidon(list(S_set | {x})):
                is_max = False
                break
        if is_max:
            maximal.append(S)
    return maximal


def compute_witness_pairs(S, A):
    """
    For each blocked element x ∈ A\S, compute the witness pairs (a,b) ∈ S×S.
    
    x is blocked by S means S ∪ {x} is not Sidon.  
    This happens when ∃ collision: x + c = a + b with c ∈ S, a,b ∈ S.
    The witness pair is the unordered pair {a,b} (or (a,a) if a=b).
    
    We encode pairs as (min(a,b), max(a,b)) for canonicalization.
    """
    S_set = set(S)
    S_list = sorted(S)
    
    # Build sum table for S using ORDERED pairs (a,b) with a,b ∈ S
    # The axiom maps to S ×ˢ S (cartesian product = ordered pairs)
    sum_table = defaultdict(list)
    for a in S_list:
        for b in S_list:
            sum_table[a + b].append((a, b))
    
    blocked = {}
    
    for x in sorted(A - S_set):
        pairs = set()
        
        # x + c = a + b where c ∈ S, (a,b) ORDERED pair in S×S
        for c in S_list:
            target = x + c
            if target in sum_table:
                for (a, b) in sum_table[target]:
                    # Exclude trivial: if {x,c} = {a,b} as multisets
                    if (x == a and c == b) or (x == b and c == a):
                        continue
                    pairs.add((a, b))
        
        # Also check: x + x = a + b where a ≠ b, a,b ∈ S (both orderings)
        target2 = 2 * x
        if target2 in sum_table:
            for (a, b) in sum_table[target2]:
                if a != b:
                    pairs.add((a, b))
        
        if pairs:
            blocked[x] = pairs
    
    return blocked


def verify_two_to_one_cpsat(blocked, capacity=2, time_limit=10):
    """
    Use CP-SAT to check if a valid capacitated assignment exists.
    
    Variables: For each (x, pair), binary variable b_{x,pair}
    Constraints:
      - Assignment: each x mapped to exactly 1 pair (sum = 1)
      - Capacity: each pair receives ≤ capacity elements (sum ≤ capacity)
    
    Returns (feasible, assignment, stats).
    """
    if not blocked:
        return True, {}, {"time": 0, "branches": 0, "conflicts": 0}
    
    model = cp_model.CpModel()
    
    # Create indicator variables
    indicators = {}
    for x, pairs in blocked.items():
        for pair in pairs:
            indicators[(x, pair)] = model.NewBoolVar(f'b_{x}_{pair[0]}_{pair[1]}')
    
    # Assignment constraints: each x assigned to exactly one pair
    for x, pairs in blocked.items():
        model.Add(sum(indicators[(x, p)] for p in pairs) == 1)
    
    # Capacity constraints: each pair gets ≤ capacity elements
    all_pairs = set()
    for pairs in blocked.values():
        all_pairs.update(pairs)
    
    for pair in all_pairs:
        vars_for_pair = [indicators[(x, pair)] 
                         for x in blocked if pair in blocked[x]]
        if len(vars_for_pair) > capacity:
            model.Add(sum(vars_for_pair) <= capacity)
    
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    status = solver.Solve(model)
    
    stats = {
        "time": solver.WallTime(),
        "branches": solver.NumBranches(),
        "conflicts": solver.NumConflicts(),
    }
    
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        assignment = {}
        for x in blocked:
            for pair in blocked[x]:
                if solver.Value(indicators[(x, pair)]) == 1:
                    assignment[x] = pair
                    break
        return True, assignment, stats
    else:
        return False, None, stats


def analyze_assignment(assignment):
    """Compute fiber sizes and statistics."""
    fibers = defaultdict(list)
    for x, pair in assignment.items():
        fibers[pair].append(x)
    
    max_fiber = max(len(v) for v in fibers.values()) if fibers else 0
    pairs_at_max = sum(1 for v in fibers.values() if len(v) == max_fiber)
    total_pairs_used = len(fibers)
    
    return {
        "max_fiber": max_fiber,
        "pairs_at_max": pairs_at_max,
        "total_pairs_used": total_pairs_used,
        "fibers": dict(fibers),
    }


def main():
    max_N = int(sys.argv[1]) if len(sys.argv) > 1 else 25
    capacity = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    
    print("=" * 75)
    print(f"VERIFICATION: 2-to-1 Map Axiom (capacity={capacity}) for N=4..{max_N}")
    print("=" * 75)
    print(f"{'N':>3} {'|S|':>4} {'#max':>6} {'max_bl':>7} {'bl/|S|²':>8} {'feas':>5} {'time':>8}")
    print("-" * 55)
    
    all_results = []
    all_feasible = True
    
    for N in range(4, max_N + 1):
        t0 = time.time()
        maximal_sets = find_all_maximal_sidon_sets(N)
        
        if not maximal_sets:
            print(f"N={N:3d}: no maximal Sidon sets found")
            continue
        
        n_feasible = 0
        n_infeasible = 0
        max_blocked = 0
        worst_S = None
        worst_ratio = 0
        
        A = set(range(1, N + 1))
        
        for S in maximal_sets:
            S_set = set(S)
            blocked = compute_witness_pairs(S, A)
            num_blocked = len(blocked)
            max_blocked = max(max_blocked, num_blocked)
            
            ratio = num_blocked / (len(S) ** 2) if len(S) > 0 else 0
            if ratio > worst_ratio:
                worst_ratio = ratio
                worst_S = S
            
            if num_blocked == 0:
                n_feasible += 1
                continue
            
            feasible, assignment, stats = verify_two_to_one_cpsat(blocked, capacity)
            
            if feasible:
                n_feasible += 1
                info = analyze_assignment(assignment)
            else:
                n_infeasible += 1
                all_feasible = False
                print(f"\n  *** COUNTEREXAMPLE at N={N}, S={S} ***")
                print(f"      #blocked = {num_blocked}")
                for x, pairs in sorted(blocked.items()):
                    print(f"      x={x}: options={sorted(pairs)}")
        
        t1 = time.time()
        s_size = len(maximal_sets[0])
        status = "✓" if n_infeasible == 0 else "✗"
        
        print(f"{N:3d} {s_size:4d} {len(maximal_sets):6d} "
              f"{max_blocked:7d} {worst_ratio:8.3f} "
              f"{status:>5} {t1-t0:8.2f}s")
        
        all_results.append({
            'N': N,
            'S_size': s_size,
            'num_maximal': len(maximal_sets),
            'max_blocked': max_blocked,
            'worst_ratio': worst_ratio,
            'all_feasible': n_infeasible == 0,
            'time': t1 - t0,
        })
        
        if n_infeasible > 0:
            break
    
    # Summary
    print("\n" + "=" * 75)
    if all_feasible:
        max_ratio = max(r['worst_ratio'] for r in all_results)
        print(f"✓ AXIOM VERIFIED: 2-to-{capacity} map exists for ALL maximal Sidon sets")
        print(f"  N range: 4..{all_results[-1]['N']}")
        print(f"  Max |blocked|/|S|² ratio: {max_ratio:.4f}")
        print(f"  (Axiom requires feasible assignment with fiber ≤ {capacity})")
    else:
        print(f"✗ COUNTEREXAMPLE FOUND at N={all_results[-1]['N']}")
    
    # Save to CSV
    csv_path = "experiments/sidon_2to1_verification.csv"
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
        writer.writeheader()
        writer.writerows(all_results)
    print(f"\nResults saved to {csv_path}")
    
    return all_results


if __name__ == "__main__":
    main()
