"""
CP-SAT exact maximum Sidon subset solver for {0,...,N-1}.
Uses OR-Tools CP-SAT to find the maximum cardinality Sidon (B₂) subset.

Constraint: For each collision quadruple (a,b,c,d) with a+b = c+d, 
            a<b, c<d, {a,b} ≠ {c,d}: at most 3 of 4 elements selected.
Objective: Maximize |S|.
"""
from ortools.sat.python import cp_model
import time, sys
import numpy as np

def exact_max_sidon(N, time_limit=60):
    """Find exact maximum Sidon subset of {0,...,N-1} using CP-SAT."""
    model = cp_model.CpModel()
    
    # Binary variables: x[i] = 1 iff element i is in the Sidon set
    x = [model.NewBoolVar(f'x_{i}') for i in range(N)]
    
    # Enumerate collision constraints:
    # For each sum s, find all pairs (a,b) with a<b and a+b=s.
    # For each pair of distinct pairs (a,b) and (c,d) with same sum,
    # at most 3 of {a,b,c,d} can be selected.
    constraint_count = 0
    for s in range(1, 2*N - 2):
        pairs = []
        a_min = max(0, s - (N-1))
        a_max = min(s // 2 - (0 if s % 2 else 0), N-1)
        for a in range(a_min, s // 2 + 1):
            b = s - a
            if a < b and b < N:
                pairs.append((a, b))
        
        # For each pair of pairs with same sum, add constraint
        for i in range(len(pairs)):
            for j in range(i+1, len(pairs)):
                a, b = pairs[i]
                c, d = pairs[j]
                # {a,b,c,d} can have at most 3 selected (i.e., not all 4)
                elems = list(set([a, b, c, d]))
                if len(elems) == 4:
                    model.Add(x[a] + x[b] + x[c] + x[d] <= 3)
                    constraint_count += 1
                elif len(elems) == 3:
                    # Shared element: say a=c, then b≠d, and we need
                    # x[a] + x[b] + x[d] <= 2 (at most 2 of 3, since
                    # if all 3 selected, a+b = a+d implies b=d, contradiction)
                    # Wait: a<b, c<d, a+b=c+d, a=c → b=d, but pairs[i]≠pairs[j].
                    # So len(elems)=3 only if one element appears in both pairs.
                    # Example: (a,b) and (a,d) with b≠d, a+b=a+d → b=d. Contradiction.
                    # Or: (a,b) and (c,a) with a<b, c<a, b+... hmm.
                    # Actually if a+b=c+d with pairs distinct, and |{a,b,c,d}|=3,
                    # then exactly one element is shared. Say a=c: then b=d (same sum),
                    # contradicting distinct pairs. Say a=d: then a+b=c+a → b=c.
                    # But c<d=a and a<b=c → a<c and c<a, contradiction.
                    # So len(elems) < 4 shouldn't happen for distinct pairs.
                    pass
    
    # Objective: maximize sum of x[i]
    model.Maximize(sum(x))
    
    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_workers = 8
    
    status = solver.Solve(model)
    
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        S = [i for i in range(N) if solver.Value(x[i]) == 1]
        optimal = (status == cp_model.OPTIMAL)
        return S, optimal, constraint_count
    else:
        return None, False, constraint_count

def verify_sidon(S):
    """Verify S is a Sidon set."""
    S = sorted(S)
    sums = set()
    for i in range(len(S)):
        for j in range(i+1, len(S)):
            s = S[i] + S[j]
            if s in sums:
                return False
            sums.add(s)
    return True

# ============================================================
# Run exact solver for small N
# ============================================================
print("EXACT MAXIMUM SIDON SUBSET OF {0,...,N-1}")
print("="*80)
print(f"{'N':>5} | {'F₂(N)':>6} | {'√N':>6} | {'ratio':>6} | {'≥√N?':>5} | "
      f"{'constraints':>11} | {'time':>8} | {'optimal':>7} | Set")
print("-"*80)

max_N = int(sys.argv[1]) if len(sys.argv) > 1 else 80

results = []

for N in list(range(4, min(max_N+1, 31))) + [35, 40, 45, 50, 60, 70, 80, 100, 120, 150, 200]:
    if N > max_N:
        continue
    
    time_limit = min(300, max(10, N * N / 100))  # Scale time with N
    t0 = time.time()
    S, optimal, n_constraints = exact_max_sidon(N, time_limit=time_limit)
    dt = time.time() - t0
    
    if S is not None:
        size = len(S)
        sqN = np.sqrt(N)
        ratio = size / sqN
        is_sidon = verify_sidon(S)
        check = "YES" if size >= sqN else "no"
        opt_str = "OPT" if optimal else "feas"
        set_str = str(S) if N <= 30 else f"[{S[0]},...,{S[-1]}]"
        
        results.append((N, size, sqN, ratio, optimal))
        
        print(f"{N:>5} | {size:>6} | {sqN:>6.2f} | {ratio:>6.3f} | {check:>5} | "
              f"{n_constraints:>11} | {dt:>7.1f}s | {opt_str:>7} | {set_str}")
    else:
        print(f"{N:>5} | {'FAIL':>6} | {np.sqrt(N):>6.2f} | {'---':>6} | {'---':>5} | "
              f"{n_constraints:>11} | {dt:>7.1f}s |   FAIL |")

# Summary
print("\n" + "="*80)
print("EXACT F₂(N) SUMMARY (optimal solutions only)")
print("="*80)
opt_results = [(N, sz, sq, r) for N, sz, sq, r, opt in results if opt]
if opt_results:
    print(f"{'N':>5} | {'F₂(N)':>6} | {'√N':>6} | {'F₂(N)/√N':>8}")
    print("-"*35)
    for N, sz, sq, r in opt_results:
        check = " ✓" if sz >= sq else ""
        print(f"{N:>5} | {sz:>6} | {sq:>6.2f} | {r:>8.4f}{check}")
    
    # Check: is F₂(N) ≥ √N for all computed N?
    all_above = all(sz >= sq for N, sz, sq, r in opt_results)
    print(f"\nF₂(N) ≥ √N for all computed N: {all_above}")
    if not all_above:
        violations = [(N, sz, sq) for N, sz, sq, r in opt_results if sz < sq]
        print(f"Violations: {violations}")
