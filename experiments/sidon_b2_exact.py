"""
Exact B₂ (Sidon) set computation via CP-SAT.

B₂ definition: All sums a+b with a ≤ b (INCLUDING a=b) are distinct.
This is STRICTER than "all pairwise sums a+b with a<b are distinct".

The difference: B₂ also requires 2a ≠ b+c for distinct elements.
"""

from ortools.sat.python import cp_model
import math
import sys
import csv

def max_b2_subset(N: int, time_limit: int = 120) -> tuple[int, list[int]]:
    """Find maximum B₂ (Sidon) subset of {1,...,N} using CP-SAT.
    
    B₂ condition: for all a ≤ b and c ≤ d in S with (a,b) ≠ (c,d): a+b ≠ c+d.
    This includes self-sums: 2a must differ from all b+c (b<c).
    """
    model = cp_model.CpModel()
    
    # Binary variables: x[i] = 1 iff element i is in the Sidon set
    x = {}
    for i in range(1, N + 1):
        x[i] = model.new_bool_var(f'x_{i}')
    
    # Build ALL sum representations: for each sum s, collect all pairs (a,b) with a ≤ b
    sum_to_pairs = {}
    for a in range(1, N + 1):
        for b in range(a, N + 1):  # b ≥ a (includes b = a for self-sums)
            s = a + b
            if s not in sum_to_pairs:
                sum_to_pairs[s] = []
            sum_to_pairs[s].append((a, b))
    
    # For each sum with ≥ 2 representations, add exclusion constraints
    num_constraints = 0
    for s, pairs in sum_to_pairs.items():
        if len(pairs) >= 2:
            for i in range(len(pairs)):
                for j in range(i + 1, len(pairs)):
                    a, b = pairs[i]
                    c, d = pairs[j]
                    # Can't have all elements of {a,b,c,d} in S
                    elements = list(set([a, b, c, d]))
                    # At least one must be excluded
                    model.add_bool_or([x[e].Not() for e in elements])
                    num_constraints += 1
    
    # Maximize subset size
    model.maximize(sum(x[i] for i in range(1, N + 1)))
    
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    status = solver.solve(model)
    
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        size = int(solver.objective_value)
        subset = sorted([i for i in range(1, N + 1) if solver.value(x[i])])
        return size, subset
    return 0, []


def verify_b2(S: list[int]) -> bool:
    """Verify S is a B₂ set (all sums a+b with a ≤ b are distinct)."""
    sums = set()
    for i, a in enumerate(S):
        for b in S[i:]:  # b ≥ a
            s = a + b
            if s in sums:
                return False
            sums.add(s)
    return True


def compute_singer_bound(N: int) -> float:
    """Compute the Singer extraction bound: N / (3*sqrt(N) + 1)."""
    return N / (3 * math.sqrt(N) + 1)


def main():
    N_values = [5, 8, 10, 13, 15, 17, 20, 25, 30, 35, 40, 45, 50, 55, 60, 70, 80, 90, 100]
    
    results = []
    
    print(f"{'N':>4} | {'F₂(N)':>5} | {'√N':>6} | {'F₂/√N':>6} | {'Singer':>6} | {'Ratio':>6} | {'Set':>30} | {'B₂?':>4}")
    print("-" * 110)
    
    for N in N_values:
        # Set time limit based on N
        time_limit = min(300, max(30, N * 3))
        
        size, subset = max_b2_subset(N, time_limit=time_limit)
        is_b2 = verify_b2(subset) if subset else False
        sqrt_n = math.sqrt(N)
        ratio = size / sqrt_n if sqrt_n > 0 else 0
        singer = compute_singer_bound(N)
        singer_ratio = singer / sqrt_n if sqrt_n > 0 else 0
        
        set_str = str(subset[:8]) + ('...' if len(subset) > 8 else '')
        
        print(f"{N:>4} | {size:>5} | {sqrt_n:>6.2f} | {ratio:>6.3f} | {singer:>6.2f} | {singer_ratio:>6.3f} | {set_str:>30} | {'✓' if is_b2 else '✗':>4}")
        
        results.append({
            'N': N,
            'F2_B2': size,
            'sqrt_N': round(sqrt_n, 4),
            'ratio': round(ratio, 4),
            'singer_bound': round(singer, 4),
            'singer_ratio': round(singer_ratio, 4), 
            'sidon_set': subset,
            'verified_b2': is_b2
        })
        
        sys.stdout.flush()
    
    # Write CSV
    with open('experiments/sidon_b2_exact.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['N', 'F2_B2', 'sqrt_N', 'ratio', 'singer_bound', 'singer_ratio', 'verified_b2'])
        writer.writeheader()
        for r in results:
            row = {k: v for k, v in r.items() if k != 'sidon_set'}
            writer.writerow(row)
    
    print("\nResults saved to experiments/sidon_b2_exact.csv")
    
    # Summary statistics
    print("\n=== Key Findings ===")
    print(f"F₂(N)/√N ranges from {min(r['ratio'] for r in results):.3f} to {max(r['ratio'] for r in results):.3f}")
    print(f"Singer bound / √N ≈ {results[-1]['singer_ratio']:.3f} (converges to 1/3)")
    print(f"Gap: F₂(N) is {results[-1]['ratio']/results[-1]['singer_ratio']:.1f}x the Singer bound for N={results[-1]['N']}")


if __name__ == '__main__':
    main()
