import json

k = 11
n = 50

variables = []
constraints = []

# Element variables a1..a11
for i in range(1, k+1):
    variables.append({"Name": f"a{i}", "LowerBound": 1, "UpperBound": n, "Type": 0, "Domain": []})

# Sum variables s_i_j for all pairs (i,j) with i<j
pairs = []
for i in range(1, k+1):
    for j in range(i+1, k+1):
        name = f"s{i}_{j}"
        variables.append({"Name": name, "LowerBound": 2, "UpperBound": 2*n, "Type": 0, "Domain": []})
        pairs.append((i, j, name))

# Ordering constraints: a_{i+1} - a_i >= 1
for i in range(1, k):
    constraints.append({
        "Name": f"ord{i}_{i+1}",
        "Type": 0,
        "Coefficients": {f"a{i+1}": 1, f"a{i}": -1},
        "Target": 1,
        "Operator": 2,
        "VariableNames": []
    })

# Sum equality constraints: s_i_j - a_i - a_j = 0
for i, j, name in pairs:
    constraints.append({
        "Name": f"eq{i}_{j}",
        "Type": 0,
        "Coefficients": {name: 1, f"a{i}": -1, f"a{j}": -1},
        "Target": 0,
        "Operator": 1,
        "VariableNames": []
    })

# AllDifferent constraint on all sum variables
all_sum_names = [name for _, _, name in pairs]
constraints.append({
    "Name": "sidon",
    "Type": 1,
    "Coefficients": {},
    "Target": 0,
    "Operator": 1,
    "VariableNames": all_sum_names
})

problem = {
    "problem": {
        "Variables": variables,
        "Constraints": constraints,
        "Objective": None,
        "Options": {"TimeLimit": 120}
    }
}

params_json = json.dumps(problem, separators=(',', ':'))
print(params_json)

# Also save to file for reference
with open("sidon_cpsat_k11.json", "w") as f:
    json.dump(problem, f, separators=(',', ':'))

print(f"\n---\nVariables: {len(variables)} ({k} elements + {len(pairs)} sums)")
print(f"Constraints: {len(constraints)} ({k-1} ordering + {len(pairs)} equalities + 1 AllDifferent)")
print(f"Pairs: {len(pairs)}")
