"""
Generate compact inline JSON for Laplacian FPGA matrix at N=50.
Round to 1 decimal to keep payload manageable.
"""
import numpy as np
import json

N = 50

def build_collision_weight_matrix(N):
    W = np.zeros((N, N))
    for a in range(N):
        for b in range(a+1, N):
            s = a + b
            for c in range(N):
                d = s - c
                if 0 <= d < N and c < d and (c, d) != (a, b):
                    pairs = {a, b}
                    cross = {c, d}
                    if pairs != cross:
                        for i in pairs:
                            for j in cross:
                                if i != j:
                                    W[i, j] += 0.5
                                    W[j, i] += 0.5
    return W

def build_fpga_matrix(N, epsilon=0.1):
    W = build_collision_weight_matrix(N)
    # Force exact symmetry (floating-point accumulation can drift)
    W = (W + W.T) / 2.0
    D = np.diag(W.sum(axis=1))
    L = D - W
    K = -(L + epsilon * np.eye(N))
    return K, W, L

print(f"Building Laplacian FPGA matrix for N={N}...")
K, W, L = build_fpga_matrix(N, epsilon=0.1)

# Round to 1 decimal for compact representation
K_rounded = np.round(K, 1)

# Build inline JSON
rows = []
for i in range(N):
    row = [float(K_rounded[i, j]) for j in range(N)]
    rows.append(row)

inline = json.dumps(rows, separators=(',', ':'))
print(f"Matrix size: {N}x{N}")
print(f"Inline JSON length: {len(inline)} chars")
print(f"K eigenvalue range: [{np.linalg.eigvalsh(K).min():.4f}, {np.linalg.eigvalsh(K).max():.4f}]")
print(f"K condition number: {np.linalg.cond(K):.1f}")

# Also compute local K^{-1} diagonal for later verification
K_inv = np.linalg.inv(K)
local_diag = -np.diag(K_inv)
print(f"\nLocal -K⁻¹ diagonal range: [{local_diag.min():.6f}, {local_diag.max():.6f}]")
print(f"Edge/center ratio: {local_diag[0] / local_diag[N//2]:.6f}")

# Save inline
with open(f"sidon_laplacian_K{N}_inline.txt", "w") as f:
    f.write(inline)
print(f"Saved to sidon_laplacian_K{N}_inline.txt")

# Save local K^{-1} diagonal for later comparison
np.save(f"sidon_kinv_diag_{N}.npy", local_diag)
print(f"Saved local K⁻¹ diagonal to sidon_kinv_diag_{N}.npy")
