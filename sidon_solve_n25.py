"""
Solve F₂(25): Maximum Sidon (B₂) subset of {1, 2, ..., 25}
Uses OR-Tools CP-SAT solver with the exact ILP formulation verified on MCP tool.

A set S is Sidon iff all pairwise sums a+b (a<b) are distinct.
Equivalently: for every collision (a,b),(c,d) with a+b=c+d, at most 3 of {a,b,c,d} in S.
"""

from ortools.sat.python import cp_model
from itertools import combinations
import time

N = 25

model = cp_model.CpModel()

# Binary variables: e[i] = 1 iff i is in the Sidon set
e = {}
for i in range(1, N + 1):
    e[i] = model.new_bool_var(f"e{i}")

# Objective: maximize |S|
model.maximize(sum(e[i] for i in range(1, N + 1)))

# Collision constraints:
# For each sum s, find all pairs (a,b) with a<b, a+b=s, 1 ≤ a,b ≤ N
# For each pair of such pairs, add: e[a1]+e[b1]+e[a2]+e[b2] ≤ 3
constraint_count = 0
for s in range(3, 2 * N):
    pairs = []
    for a in range(max(1, s - N), s // 2 + 1):
        b = s - a
        if a < b and 1 <= b <= N:
            pairs.append((a, b))
    
    if len(pairs) >= 2:
        for (a1, b1), (a2, b2) in combinations(pairs, 2):
            elems = {a1, b1, a2, b2}
            assert len(elems) == 4, f"Shared element in pairs ({a1},{b1}) ({a2},{b2}) sum={s}"
            model.add(e[a1] + e[b1] + e[a2] + e[b2] <= 3)
            constraint_count += 1

print(f"N = {N}")
print(f"Variables: {N}")
print(f"Collision constraints: {constraint_count}")

# Solve
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 60.0
solver.parameters.log_search_progress = False

start = time.time()
status = solver.solve(model)
elapsed = time.time() - start

print(f"\nSolver status: {solver.status_name(status)}")
print(f"Solve time: {elapsed:.3f}s")

if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    opt = int(solver.objective_value)
    sidon_set = sorted([i for i in range(1, N + 1) if solver.value(e[i]) == 1])
    
    print(f"\n{'='*60}")
    print(f"F₂({N}) = {opt}")
    print(f"Optimal Sidon set: {sidon_set}")
    print(f"Set size: {len(sidon_set)}")
    print(f"{'='*60}")
    
    # Verification: check all pairwise sums are distinct
    pair_sums = {}
    all_distinct = True
    for a, b in combinations(sidon_set, 2):
        s = a + b
        if s in pair_sums:
            print(f"  ⚠ COLLISION: {a}+{b} = {pair_sums[s][0]}+{pair_sums[s][1]} = {s}")
            all_distinct = False
        pair_sums[s] = (a, b)
    
    print(f"\nVerification:")
    print(f"  Number of pairs: C({opt},2) = {opt*(opt-1)//2}")
    print(f"  Pairwise sums: {sorted(pair_sums.keys())}")
    print(f"  All sums distinct: {'✓ YES' if all_distinct else '✗ NO'}")
    
    # Ratio
    import math
    ratio = opt / math.sqrt(N)
    print(f"\nRatio F₂({N})/√{N} = {opt}/{math.sqrt(N):.4f} = {ratio:.4f}")
    
    # Additional info
    print(f"\nTheoretical bounds:")
    print(f"  √{N} = {math.sqrt(N):.4f}")
    print(f"  √{N} + √{N}^(1/4) ≈ {math.sqrt(N) + N**(1/4):.4f}")
    print(f"  Erdős-Turán upper bound: F₂(n) ≤ √n + O(n^(1/4))")
    
    if status == cp_model.OPTIMAL:
        print(f"\n✓ Solution is PROVEN OPTIMAL by CP-SAT solver")
    else:
        print(f"\n⚠ Solution is feasible but optimality not proven (time limit)")
else:
    print("No solution found!")
