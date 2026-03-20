import json

variables = [{"name": f"e{i}", "lowerBound": 0, "upperBound": 1, "type": "Binary"} for i in range(1, 21)]
objective = {"type": "Maximize", "coefficients": {f"e{i}": 1 for i in range(1, 21)}}

constraints = []
idx = 1
for s in range(3, 40):
    pairs = []
    for a in range(1, 21):
        b = s - a
        if a < b and 1 <= b <= 20:
            pairs.append((a, b))
    for i in range(len(pairs)):
        for j in range(i + 1, len(pairs)):
            a1, b1 = pairs[i]
            a2, b2 = pairs[j]
            constraints.append({
                "name": f"c{idx}",
                "coefficients": {f"e{a1}": 1, f"e{b1}": 1, f"e{a2}": 1, f"e{b2}": 1},
                "operator": "LessThanOrEqual",
                "rightHandSide": 3
            })
            idx += 1

problem = {"problem": {"variables": variables, "objective": objective, "constraints": constraints}}
with open(r"d:\Erdos\lp_problem.json", "w") as f:
    json.dump(problem, f)
print(f"Generated {len(constraints)} constraints")
