"""Generate LP problem JSON for F_2(25) — maximum Sidon set in {1,...,25}."""
import json
from itertools import combinations

N = 25

# Variables: binary e1..e25
variables = [{"name": f"e{i}", "lowerBound": 0, "upperBound": 1, "type": "Binary"} for i in range(1, N+1)]

# Objective: maximize sum of all e_i
objective = {"type": "Maximize", "coefficients": {f"e{i}": 1 for i in range(1, N+1)}}

# Constraints: for each sum s, find all pairs (a,b) with a<b, a+b=s
# Then for each pair of such pairs, add constraint ea+eb+ec+ed <= 3
constraints = []
cid = 0

for s in range(3, 2*N):  # s from 3 to 49
    # Find all pairs (a,b) with 1 <= a < b <= N and a+b = s
    pairs = []
    for a in range(max(1, s - N), s // 2 + 1):
        b = s - a
        if a < b and 1 <= b <= N:
            pairs.append((a, b))
    
    # For each pair of pairs, generate a constraint
    if len(pairs) >= 2:
        for (a1, b1), (a2, b2) in combinations(pairs, 2):
            cid += 1
            elems = {a1, b1, a2, b2}
            coeffs = {f"e{x}": 1 for x in elems}
            # If pairs share an element, that element appears once with coeff 1
            # but the constraint is still: sum of indicators <= 3
            # Actually for distinct elements it's 4 vars each with coeff 1 <= 3
            # If they share an element, it's 3 vars, but we still need <= 3
            # which is always true for 3 binary vars (max sum = 3)
            # So we only need constraints when all 4 elements are distinct
            if len(elems) == 4:
                constraints.append({
                    "name": f"s{s}_{cid}",
                    "coefficients": coeffs,
                    "operator": "LessThanOrEqual",
                    "rightHandSide": 3
                })

print(f"Generated {len(constraints)} constraints for N={N}")
print(f"Variables: {len(variables)}")

problem = {
    "problem": {
        "variables": variables,
        "objective": objective,
        "constraints": constraints,
        "options": {"solver": "SCIP"}
    }
}

with open("sidon_lp_n25.json", "w") as f:
    json.dump(problem, f)

print(f"JSON written to sidon_lp_n25.json ({len(json.dumps(problem))} chars)")
