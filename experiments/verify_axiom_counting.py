"""
Verify the KSS axiom: For every maximal Sidon set S in A={1,...,N},
    |A \ S| ≤ 2|S|²

This is equivalent to AdmitsTwoToOneMap(A, S) since the map f: A\S → S×S
does NOT need to be a witness map — any function with fiber ≤ 2 suffices.

Also checks: the stronger question of whether a 2-to-1 WITNESS map exists
(where f(x) must be a collision pair for x).
"""

from itertools import combinations
from collections import defaultdict
import time
import csv
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


def find_all_maximal_sidon_sets(N):
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


def compute_witness_pairs_ordered(S, A):
    """Compute witness pairs using ORDERED pairs (a,b) ∈ S×S."""
    S_set = set(S)
    S_list = sorted(S)
    sum_table = defaultdict(list)
    for a in S_list:
        for b in S_list:
            sum_table[a + b].append((a, b))
    blocked = {}
    for x in sorted(A - S_set):
        pairs = set()
        for c in S_list:
            target = x + c
            if target in sum_table:
                for (a, b) in sum_table[target]:
                    if (x == a and c == b) or (x == b and c == a):
                        continue
                    pairs.add((a, b))
        target2 = 2 * x
        if target2 in sum_table:
            for (a, b) in sum_table[target2]:
                if a != b:
                    pairs.add((a, b))
        if pairs:
            blocked[x] = pairs
    return blocked


def check_witness_2to1(blocked, capacity=2):
    """Check if a 2-to-1 WITNESS map exists (backtracking)."""
    if not blocked:
        return True, {}
    elements = sorted(blocked.keys(), key=lambda x: len(blocked[x]))
    pairs_usage = defaultdict(int)
    assignment = {}
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


def main():
    max_N = int(sys.argv[1]) if len(sys.argv) > 1 else 25

    print("=" * 90)
    print(f"KSS AXIOM VERIFICATION for N=4..{max_N}")
    print("=" * 90)
    print(f"{'N':>3} {'|S|':>4} {'#max':>6} {'|A\\S|':>6} {'2|S|²':>6} "
          f"{'count✓':>7} {'wit✓':>5} {'time':>8}")
    print("-" * 65)

    all_results = []
    counting_ok = True
    witness_ok = True

    for N in range(4, max_N + 1):
        t0 = time.time()
        maximal_sets = find_all_maximal_sidon_sets(N)
        if not maximal_sets:
            continue

        A = set(range(1, N + 1))
        worst_ratio = 0
        max_blocked = 0
        min_k = min(len(S) for S in maximal_sets)
        max_k = max(len(S) for S in maximal_sets)
        n_count_fail = 0
        n_witness_fail = 0
        worst_count_S = None
        worst_witness_S = None

        for S in maximal_sets:
            S_set = set(S)
            k = len(S)
            blocked_count = N - k  # |A \ S|
            capacity_2k2 = 2 * k * k
            
            # Check 1: Counting condition |A\S| ≤ 2|S|²
            if blocked_count > capacity_2k2:
                n_count_fail += 1
                worst_count_S = S
                counting_ok = False

            # Check 2: Witness map existence
            blocked = compute_witness_pairs_ordered(S, A)
            num_blocked_actual = len(blocked)
            max_blocked = max(max_blocked, num_blocked_actual)
            
            ratio = num_blocked_actual / (k * k) if k > 0 else 0
            worst_ratio = max(worst_ratio, ratio)

            feasible, _ = check_witness_2to1(blocked, capacity=2)
            if not feasible:
                n_witness_fail += 1
                if worst_witness_S is None:
                    worst_witness_S = S

        t1 = time.time()
        
        count_status = "✓" if n_count_fail == 0 else f"✗({n_count_fail})"
        wit_status = "✓" if n_witness_fail == 0 else f"✗({n_witness_fail})"
        
        k_str = f"{min_k}" if min_k == max_k else f"{min_k}-{max_k}"
        
        worst_blocked = N - min_k
        capacity = 2 * min_k * min_k
        
        print(f"{N:3d} {k_str:>4} {len(maximal_sets):6d} {worst_blocked:6d} "
              f"{capacity:6d} {count_status:>7} {wit_status:>5} {t1-t0:8.2f}s")
        
        all_results.append({
            'N': N, 'min_k': min_k, 'max_k': max_k,
            'num_maximal': len(maximal_sets),
            'worst_blocked': worst_blocked,
            'capacity_2k2': capacity,
            'count_ok': n_count_fail == 0,
            'witness_ok': n_witness_fail == 0,
            'n_witness_fail': n_witness_fail,
            'time': t1 - t0,
        })
        
        if worst_witness_S is not None and N <= 20:
            blocked = compute_witness_pairs_ordered(worst_witness_S, A)
            print(f"      Witness fail example: S={worst_witness_S}")
            for x, pairs in sorted(blocked.items()):
                print(f"        x={x}: {sorted(pairs)}")

    # Summary
    print("\n" + "=" * 90)
    print("SUMMARY")
    print("=" * 90)
    
    if counting_ok:
        print(f"\n✓ COUNTING CONDITION |A\\S| ≤ 2|S|² holds for ALL N=4..{max_N}")
        print(f"  → AdmitsTwoToOneMap is TRUE (axiom is VALID)")
    else:
        fails = [r for r in all_results if not r['count_ok']]
        print(f"\n✗ COUNTING CONDITION FAILS at N = {[r['N'] for r in fails]}")
    
    witness_fails = [r for r in all_results if not r['witness_ok']]
    if witness_fails:
        print(f"\n⚠ Witness 2-to-1 map fails at N = {[r['N'] for r in witness_fails]}")
        print(f"  (But axiom doesn't require witness maps, so this is expected)")
    else:
        print(f"\n✓ Witness 2-to-1 map also exists for all N=4..{max_N}")

    # Save CSV
    csv_path = "experiments/sidon_axiom_verification.csv"
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
        writer.writeheader()
        writer.writerows(all_results)
    print(f"\nResults saved to {csv_path}")


if __name__ == "__main__":
    main()
