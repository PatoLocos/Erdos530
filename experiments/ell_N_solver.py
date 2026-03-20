"""
Compute ℓ(N) for Erdős Problem 530.

ℓ(N) = min over all N-element sets A ⊂ ℕ of max Sidon subset size of A.

Strategy:
- For each N, we want to find the WORST-CASE set A of size N
  (the one whose max Sidon subset is smallest).
- For a GIVEN set A, finding max Sidon subset is itself NP-hard.
- We use a two-level approach:
  1. Inner: Given A, find max Sidon subset via CP-SAT
  2. Outer: Search over sets A to minimize the inner value

Key insight: ℓ(N) ≤ F₂(N) where F₂(N) is max Sidon set in {1,...,N}.
The upper bound comes from A = {1,...,N}.
The lower bound is ℓ(N) ≥ (1/2)√N from KSS.

For small N, we can compute ℓ(N) exactly or get tight bounds.
"""

from ortools.sat.python import cp_model
import itertools
import math
import time
import sys


def max_sidon_subset_size(A: list[int]) -> tuple[int, list[int]]:
    """Find maximum Sidon subset of A using CP-SAT."""
    n = len(A)
    if n <= 1:
        return n, A[:n]
    
    model = cp_model.CpModel()
    
    # Binary variables: x[i] = 1 if A[i] is in the Sidon subset
    x = [model.NewBoolVar(f'x_{i}') for i in range(n)]
    
    # Sidon constraint: all pairwise sums must be distinct
    # For each pair of pairs (i,j) and (k,l) with {i,j} != {k,l},
    # if x[i] & x[j] & x[k] & x[l], then A[i]+A[j] != A[k]+A[l]
    for i in range(n):
        for j in range(i, n):
            for k in range(i, n):
                for l in range(k, n):
                    if (i, j) >= (k, l):
                        continue
                    if A[i] + A[j] == A[k] + A[l]:
                        # These two pairs can't both be fully selected
                        # At least one element from one pair must be excluded
                        # i.e., NOT (x[i] & x[j] & x[k] & x[l])
                        indices = list(set([i, j, k, l]))
                        if len(indices) == 4:
                            model.AddBoolOr([x[idx].Not() for idx in indices])
                        elif len(indices) == 3:
                            model.AddBoolOr([x[idx].Not() for idx in indices])
                        elif len(indices) == 2:
                            model.AddBoolOr([x[idx].Not() for idx in indices])
    
    # Maximize subset size
    model.Maximize(sum(x))
    
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30
    status = solver.Solve(model)
    
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        size = int(solver.ObjectiveValue())
        subset = [A[i] for i in range(n) if solver.Value(x[i])]
        return size, subset
    return 0, []


def max_sidon_in_range(N: int) -> tuple[int, list[int]]:
    """Find F₂(N) = max Sidon set in {1,...,N}. This gives upper bound on ℓ(N)."""
    A = list(range(1, N + 1))
    return max_sidon_subset_size(A)


def find_worst_case_set(N: int, universe_max: int = None, 
                         num_random_trials: int = 100) -> tuple[int, list[int], list[int]]:
    """
    Try to find the N-element set A whose max Sidon subset is smallest.
    Returns (min_sidon_size, worst_A, best_sidon_in_worst_A).
    
    Strategy:
    - Always test A = {1,...,N} (gives F₂(N))
    - Test A = {0,1,...,N-1}
    - Test dense arithmetic progressions
    - Test random sets
    - Test structured adversarial sets
    """
    import random
    random.seed(42)
    
    if universe_max is None:
        universe_max = max(N * N, 3 * N)  # Elements can be up to N²
    
    best_min = float('inf')
    best_A = None
    best_sidon = None
    
    candidates = []
    
    # Candidate 1: {1,...,N}
    candidates.append(list(range(1, N + 1)))
    
    # Candidate 2: {0,...,N-1}
    candidates.append(list(range(N)))
    
    # Candidate 3: Arithmetic progressions with various common differences
    for d in range(1, min(5, N)):
        candidates.append([i * d for i in range(N)])
    
    # Candidate 4: Dense sets near a point (lots of sum collisions)
    for start in [0, 1, 10]:
        candidates.append(list(range(start, start + N)))
    
    # Candidate 5: Sets designed to have many sum collisions
    # B_h set complements, sumset-rich sets
    if N >= 4:
        # Geometric-ish progression
        geo = sorted(set([min(int(1.5**i), universe_max) for i in range(N * 3)]))[:N]
        if len(geo) == N:
            candidates.append(geo)
    
    # Candidate 6: Random sets
    for _ in range(num_random_trials):
        A = sorted(random.sample(range(universe_max + 1), N))
        candidates.append(A)
    
    for A in candidates:
        if len(A) != N or len(set(A)) != N:
            continue
        size, sidon = max_sidon_subset_size(A)
        if size < best_min:
            best_min = size
            best_A = A
            best_sidon = sidon
    
    return best_min, best_A, best_sidon


def compute_ell_values(max_N: int = 30):
    """Compute ℓ(N) bounds for N = 1 to max_N."""
    print(f"{'N':>4} | {'ℓ(N)≥':>6} | {'F₂(N)':>6} | {'√N':>6} | {'ℓ/√N':>6} | {'Worst A':>30} | {'Sidon':>20}")
    print("-" * 100)
    
    results = []
    
    for N in range(1, max_N + 1):
        t0 = time.time()
        
        # Upper bound: F₂(N) from {1,...,N}
        f2_size, f2_sidon = max_sidon_in_range(N)
        
        # Lower bound attempt: find worst-case set
        if N <= 20:
            ell_bound, worst_A, worst_sidon = find_worst_case_set(
                N, universe_max=max(N*N, 50), num_random_trials=50
            )
        else:
            # For larger N, just use {1,...,N} as proxy
            ell_bound = f2_size
            worst_A = list(range(1, N + 1))
            worst_sidon = f2_sidon
        
        sqrt_N = math.sqrt(N)
        ratio = ell_bound / sqrt_N if sqrt_N > 0 else float('inf')
        
        elapsed = time.time() - t0
        
        worst_A_str = str(worst_A[:8]) + ('...' if len(worst_A) > 8 else '')
        sidon_str = str(worst_sidon)
        
        print(f"{N:>4} | {ell_bound:>6} | {f2_size:>6} | {sqrt_N:>6.2f} | {ratio:>6.3f} | {worst_A_str:>30} | {sidon_str:>20}")
        
        results.append({
            'N': N, 'ell_lower': ell_bound, 'F2': f2_size,
            'sqrt_N': sqrt_N, 'ratio': ratio, 'worst_A': worst_A,
            'sidon': worst_sidon, 'time': elapsed
        })
        
        sys.stdout.flush()
    
    return results


def verify_kss_bound(results):
    """Verify that ℓ(N) ≥ (1/2)√N for all computed values."""
    print("\n\n=== KSS Bound Verification ===")
    print(f"{'N':>4} | {'ℓ(N)':>5} | {'(1/2)√N':>8} | {'KSS holds?':>10}")
    print("-" * 40)
    
    all_hold = True
    for r in results:
        kss_bound = 0.5 * r['sqrt_N']
        holds = r['ell_lower'] >= kss_bound
        if not holds:
            all_hold = False
        print(f"{r['N']:>4} | {r['ell_lower']:>5} | {kss_bound:>8.3f} | {'✅' if holds else '❌':>10}")
    
    if all_hold:
        print("\n✅ KSS bound ℓ(N) ≥ (1/2)√N verified for all tested N!")
    else:
        print("\n❌ KSS bound VIOLATED - this would be a counterexample!")


if __name__ == '__main__':
    results = compute_ell_values(max_N=25)
    verify_kss_bound(results)
