"""
Real FPGA vs Local math test for Erdős Problem 530 (Sidon sets).

Builds K = -(L + εI) collision Laplacian at multiple sizes,
computes local K⁻¹ diagonal (expected variance), and exports
matrices for PROMETHEUS FPGA comparison.

The FPGA returns equilibrium_statistics: { means, variances } for each channel.
Theory: variance[i] = -[K⁻¹]_{ii} · T (at T=1.0)
But FPGA uses scaled matrix K_s = scale · K, so:
   variance_fpga[i] = -[(scale·K)⁻¹]_{ii} = -[K⁻¹]_{ii} / scale
"""
import numpy as np
from scipy import linalg
from scipy.stats import spearmanr, pearsonr
import json
import time
import csv
import os

# ─── Matrix Construction ───────────────────────────────────────────────

def build_collision_weight_matrix(N):
    """Build symmetric collision weight matrix W[i,j]."""
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
    """Build K = -(L + εI) from collision Laplacian."""
    W = build_collision_weight_matrix(N)
    D = np.diag(np.sum(W, axis=1))
    L = D - W
    K = -(L + epsilon * np.eye(N))
    return K

# ─── Local K⁻¹ Reference Computation ──────────────────────────────────

def compute_local_reference(K):
    """Compute local K⁻¹ diagonal and expected variances."""
    N = K.shape[0]
    K_inv = np.linalg.inv(K)
    kinv_diag = np.diag(K_inv)
    expected_var = -kinv_diag  # K negative-definite → K⁻¹ has negative diagonal
    
    eigvals = np.linalg.eigvalsh(K)
    cond = np.linalg.cond(K)
    
    return {
        'K_inv_diag': kinv_diag,
        'expected_var': expected_var,
        'eigvals_min': eigvals[0],
        'eigvals_max': eigvals[-1],
        'condition_number': cond,
    }

# ─── Sidon Set Extraction ─────────────────────────────────────────────

def verify_sidon(S):
    """Verify that S is a valid Sidon set (all pairwise sums distinct)."""
    S = sorted(S)
    sums = set()
    for i in range(len(S)):
        for j in range(i+1, len(S)):
            s = S[i] + S[j]
            if s in sums:
                return False
            sums.add(s)
    return True

def extract_sidon_from_variance(variances, N):
    """Extract Sidon set: rank by variance (highest=least constrained), greedy pick."""
    ranking = np.argsort(-variances)
    S = []
    sums = set()
    for x in ranking:
        ok = True
        new_sums = set()
        for s in S:
            ps = x + s
            if ps in sums or ps in new_sums:
                ok = False
                break
            new_sums.add(ps)
        if ok:
            S.append(x)
            sums |= new_sums
    return sorted(S)

def greedy_sidon(N):
    """Standard sequential greedy Sidon set."""
    S = [0]
    sums = set()
    for x in range(1, N):
        ok = True
        new_sums = set()
        for s in S:
            ps = x + s
            if ps in sums or ps in new_sums:
                ok = False
                break
            new_sums.add(ps)
        if ok:
            S.append(x)
            sums.update(new_sums)
    return S

# ─── Export Functions ──────────────────────────────────────────────────

def export_csv(K, filepath):
    """Export K matrix as CSV."""
    np.savetxt(filepath, K, delimiter=',', fmt='%.10f')
    print(f"  Exported CSV: {filepath} ({os.path.getsize(filepath):,} bytes)")

def export_npy(K, filepath):
    """Export K matrix as NPY."""
    np.save(filepath, K)
    print(f"  Exported NPY: {filepath} ({os.path.getsize(filepath):,} bytes)")

# ─── Main Analysis ─────────────────────────────────────────────────────

if __name__ == '__main__':
    print("=" * 76)
    print("ERDŐS 530 — PROMETHEUS FPGA vs LOCAL MATH VALIDATION")
    print("=" * 76)
    
    test_sizes = [30, 50, 100]
    all_results = {}
    
    for N in test_sizes:
        print(f"\n{'─'*76}")
        print(f"  N = {N}")
        print(f"{'─'*76}")
        
        # Build K
        t0 = time.time()
        K = build_K_matrix(N, epsilon=0.1)
        build_time = time.time() - t0
        
        # Local reference
        t1 = time.time()
        ref = compute_local_reference(K)
        solve_time = time.time() - t1
        
        print(f"  Build time:       {build_time:.3f}s")
        print(f"  K⁻¹ solve time:  {solve_time:.3f}s")
        print(f"  Eigenvalue range: [{ref['eigvals_min']:.4f}, {ref['eigvals_max']:.4f}]")
        print(f"  Condition number: {ref['condition_number']:.1f}")
        print(f"  max(|K_ij|):      {np.max(np.abs(K)):.2f}")
        
        # FPGA scale factor prediction
        max_abs = np.max(np.abs(K))
        predicted_scale = 1.99 / max_abs
        print(f"  Predicted FPGA scale (1.99/max): {predicted_scale:.8f}")
        
        # Local variance stats
        var = ref['expected_var']
        print(f"\n  Local expected_var stats:")
        print(f"    min = {var.min():.6f},  max = {var.max():.6f}")
        print(f"    mean = {var.mean():.6f},  std = {var.std():.6f}")
        print(f"    Symmetric: {np.allclose(var, var[::-1])}")
        
        # Extract Sidon set from local variance ranking
        sidon_var = extract_sidon_from_variance(var, N)
        sidon_greedy = greedy_sidon(N)
        
        print(f"\n  Sidon set (variance ranking): size {len(sidon_var):3d}  {sidon_var}")
        print(f"  Sidon set (sequential greedy): size {len(sidon_greedy):3d}  {sidon_greedy}")
        print(f"  Both valid Sidon: var={verify_sidon(sidon_var)}, greedy={verify_sidon(sidon_greedy)}")
        
        # Export for FPGA
        csv_path = f"D:\\Erdos\\test_K{N}.csv"
        npy_path = f"D:\\Erdos\\test_K{N}.npy"
        export_csv(K, csv_path)
        export_npy(K, npy_path)
        
        # Save local reference for later FPGA comparison
        all_results[N] = {
            'K': K,
            'local_var': var,
            'sidon_var': sidon_var,
            'sidon_greedy': sidon_greedy,
            'predicted_scale': predicted_scale,
            'eigvals_range': (ref['eigvals_min'], ref['eigvals_max']),
            'condition_number': ref['condition_number'],
        }
    
    # Save local reference data for comparison after FPGA run
    ref_data = {}
    for N, r in all_results.items():
        ref_data[str(N)] = {
            'local_var': r['local_var'].tolist(),
            'sidon_var': [int(x) for x in r['sidon_var']],
            'sidon_greedy': [int(x) for x in r['sidon_greedy']],
            'predicted_scale': float(r['predicted_scale']),
        }
    
    with open('D:\\Erdos\\local_reference.json', 'w') as f:
        json.dump(ref_data, f, indent=2)
    print(f"\n  Saved local reference: D:\\Erdos\\local_reference.json")
    
    # ─── Theoretical upper bound comparison ────────────────────────────
    print(f"\n{'='*76}")
    print("SIDON SIZE vs THEORETICAL BOUNDS")
    print(f"{'='*76}")
    print(f"{'N':>5} | {'Variance':>8} | {'Greedy':>6} | {'√N':>6} | {'√N+√(N^(1/4))':>14}")
    print("-" * 50)
    for N in test_sizes:
        r = all_results[N]
        sqrt_n = np.sqrt(N)
        upper = np.sqrt(N) + np.power(N, 0.25)
        print(f"{N:5d} | {len(r['sidon_var']):8d} | {len(r['sidon_greedy']):6d} | {sqrt_n:6.2f} | {upper:14.2f}")
    
    print("\n✅ Local reference computation complete. Ready for FPGA comparison.")
