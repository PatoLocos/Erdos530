"""
Find exact maximum Sidon subset using OR-Tools CP-SAT.
This is a constraint satisfaction problem.
"""

from ortools.sat.python import cp_model
import time
import math

def is_sidon_check(S):
    """Verify a set is Sidon."""
    S = sorted(S)
    sums = set()
    for i, a in enumerate(S):
        for j, b in enumerate(S):
            if i <= j:
                s = a + b
                if s in sums:
                    return False
                sums.add(s)
    return True

def find_max_sidon_cpsat(N, time_limit=30):
    """
    Find maximum Sidon subset of {1, ..., N} using CP-SAT.
    
    Variables: x_i ∈ {0,1} for each i in {1,...,N}
    Constraint: For all (a,b,c,d) with a+b=c+d and {a,b}≠{c,d}:
                NOT (x_a ∧ x_b ∧ x_c ∧ x_d)
    Objective: Maximize Σ x_i
    """
    model = cp_model.CpModel()
    
    # Variables: x[i] = 1 iff element i is in the Sidon set
    x = {}
    for i in range(1, N+1):
        x[i] = model.NewBoolVar(f'x_{i}')
    
    # Find all collision 4-tuples: (a,b,c,d) with a+b=c+d, {a,b}≠{c,d}
    # For each such tuple, add constraint: NOT (x_a AND x_b AND x_c AND x_d)
    
    # Build sum -> pairs mapping
    sum_to_pairs = {}
    for a in range(1, N+1):
        for b in range(a, N+1):  # b >= a to avoid duplicates
            s = a + b
            if s not in sum_to_pairs:
                sum_to_pairs[s] = []
            sum_to_pairs[s].append((a, b))
    
    # For each sum with multiple pairs, add constraints
    num_constraints = 0
    for s, pairs in sum_to_pairs.items():
        if len(pairs) >= 2:
            for i, (a, b) in enumerate(pairs):
                for j, (c, d) in enumerate(pairs):
                    if i < j:  # different pairs
                        # {a,b} and {c,d} are different pairs with same sum
                        # Constraint: at most 3 of {a,b,c,d} can be selected
                        elements = list(set([a, b, c, d]))  # unique elements
                        if len(elements) == 4:
                            # All 4 distinct: x_a + x_b + x_c + x_d <= 3
                            model.Add(x[a] + x[b] + x[c] + x[d] <= 3)
                            num_constraints += 1
                        elif len(elements) == 3:
                            # 3 distinct (one shared): still can't have all 3 creating collision
                            # e.g., a+b = a+d means b=d (contradiction), so this case is impossible
                            # Or a+b = c+a means b=c, so pairs share one element
                            # If (a,b) and (a,c) with a+b = a+c, then b=c (contradiction)
                            # Actually if pairs share an element: (a,b) and (a,c) means a+b=a+c, so b=c
                            # That means they're the same pair, contradicting i<j.
                            # So len(elements) is always 4 for distinct collision pairs.
                            pass
    
    print(f"N={N}: Added {num_constraints} collision constraints")
    
    # Objective: maximize size of selected set
    model.Maximize(sum(x[i] for i in range(1, N+1)))
    
    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    
    start = time.time()
    status = solver.Solve(model)
    elapsed = time.time() - start
    
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        sidon_set = [i for i in range(1, N+1) if solver.Value(x[i]) == 1]
        size = len(sidon_set)
        
        # Verify
        if not is_sidon_check(sidon_set):
            print(f"ERROR: Solution is not Sidon!")
            return None
        
        return {
            'N': N,
            'size': size,
            'ratio': size / math.sqrt(N),
            'set': sidon_set,
            'time': elapsed,
            'optimal': status == cp_model.OPTIMAL
        }
    else:
        print(f"No solution found for N={N}")
        return None

if __name__ == "__main__":
    print("="*60)
    print("Maximum Sidon Subsets of {1,...,N} via CP-SAT")
    print("="*60)
    
    results = []
    for N in [10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100]:
        result = find_max_sidon_cpsat(N, time_limit=60)
        if result:
            results.append(result)
            opt_marker = "✓" if result['optimal'] else "~"
            print(f"N={N:3d}: |S|={result['size']:2d}, |S|/√N={result['ratio']:.4f} {opt_marker} [{result['time']:.2f}s]")
            print(f"       S = {result['set']}")
            print()
    
    print("\n" + "="*60)
    print("Summary Table")
    print("="*60)
    print(f"{'N':>5} {'|S|':>5} {'|S|/√N':>10} {'Optimal':>8} {'Time':>8}")
    print("-"*40)
    for r in results:
        opt = "Yes" if r['optimal'] else "No"
        print(f"{r['N']:5d} {r['size']:5d} {r['ratio']:10.4f} {opt:>8} {r['time']:7.2f}s")
