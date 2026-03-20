"""Build K matrix for N=200 and export for FPGA."""
import numpy as np
import json, time, os

def build_collision_weight_matrix(N):
    W = np.zeros((N, N))
    for s in range(2, 2*N - 2):
        pairs = []
        for a in range(max(0, s - (N-1)), min(s, N-1) + 1):
            b = s - a
            if 0 <= b < N and a < b:
                pairs.append((a, b))
        for i in range(len(pairs)):
            for j in range(i+1, len(pairs)):
                a1, b1 = pairs[i]
                a2, b2 = pairs[j]
                for u in [a1, b1]:
                    for v in [a2, b2]:
                        if u != v:
                            W[u, v] += 1.0
    W = 0.5 * (W + W.T)
    return W

def build_K_matrix(N, epsilon=0.1):
    W = build_collision_weight_matrix(N)
    D = np.diag(np.sum(W, axis=1))
    L = D - W
    K = -(L + epsilon * np.eye(N))
    return K

print("Building K for N=200...")
t0 = time.time()
K200 = build_K_matrix(200)
dt = time.time() - t0
print(f"Built in {dt:.1f}s, shape={K200.shape}")

max_K = np.max(np.abs(K200))
eigvals = np.linalg.eigvalsh(K200)
pred_scale = 1.99 / max_K
print(f"max|K|={max_K:.1f}, eigval range=[{eigvals[0]:.3f}, {eigvals[-1]:.6f}]")
print(f"Predicted scale = 1.99 / {max_K:.4f} = {pred_scale:.8f}")
print(f"Condition number = {eigvals[-1]/eigvals[0]:.1f}")

# Local reference
K_inv = np.linalg.inv(K200)
local_var = -np.diag(K_inv)
print(f"Local var range: [{local_var.min():.6f}, {local_var.max():.6f}]")

# Sidon extraction
ranking = np.argsort(-local_var)
S = []
sums = set()
for x in ranking:
    ok = True
    new_sums = set()
    for s_elem in S:
        ps = int(x) + int(s_elem)
        if ps in sums or ps in new_sums:
            ok = False
            break
        new_sums.add(ps)
    if ok:
        S.append(int(x))
        sums |= new_sums
S_sorted = sorted(S)
print(f"Local Sidon set size: {len(S_sorted)}")
print(f"Sidon set: {S_sorted}")

# Known bound comparison
import math
upper = math.sqrt(200) + 200**0.25 + 1
lower = math.sqrt(200)
print(f"Bounds: sqrt(N)={lower:.2f}, sqrt(N)+N^(1/4)+1={upper:.2f}")

# Export CSV
np.savetxt("test_K200.csv", K200, delimiter=",", fmt="%.10f")
fsize = os.path.getsize("test_K200.csv")
print(f"Exported test_K200.csv ({fsize:,} bytes)")

# Save reference
ref = {
    "N": 200,
    "local_var": local_var.tolist(),
    "sidon_size": len(S_sorted),
    "sidon_set": S_sorted,
    "max_K": float(max_K),
    "predicted_scale": float(pred_scale),
    "var_range": [float(local_var.min()), float(local_var.max())],
    "eigval_range": [float(eigvals[0]), float(eigvals[-1])],
    "condition_number": float(eigvals[-1]/eigvals[0]),
}
with open("local_reference_200.json", "w") as f:
    json.dump(ref, f)
print("Saved local_reference_200.json")
