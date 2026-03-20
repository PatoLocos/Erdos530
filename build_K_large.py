"""Build K matrices for N=500 and N=1024 and export for FPGA."""
import numpy as np
import json, time, os, math, sys

def build_collision_weight_matrix(N):
    """Build collision weight matrix W[i,j] counting shared-sum collisions."""
    print(f"  Building collision matrix N={N}...")
    W = np.zeros((N, N))
    for s in range(2, 2*N - 2):
        pairs = []
        for a in range(max(0, s - (N-1)), min(s, N-1) + 1):
            b = s - a
            if 0 <= b < N and a < b:
                pairs.append((a, b))
        n_pairs = len(pairs)
        if n_pairs < 2:
            continue
        # Vectorized: for each pair of collision pairs, increment W
        for i in range(n_pairs):
            for j in range(i+1, n_pairs):
                a1, b1 = pairs[i]
                a2, b2 = pairs[j]
                for u in [a1, b1]:
                    for v in [a2, b2]:
                        if u != v:
                            W[u, v] += 1.0
        if s % 200 == 0:
            print(f"    sum {s}/{2*N-3}...")
    W = 0.5 * (W + W.T)
    return W

def build_K_matrix(N, epsilon=0.1):
    W = build_collision_weight_matrix(N)
    D = np.diag(np.sum(W, axis=1))
    L = D - W
    K = -(L + epsilon * np.eye(N))
    return K

def process_N(N):
    print(f"\n{'='*60}")
    print(f"N = {N}")
    print(f"{'='*60}")
    
    t0 = time.time()
    K = build_K_matrix(N)
    dt = time.time() - t0
    print(f"Built in {dt:.1f}s, shape={K.shape}")
    
    max_K = np.max(np.abs(K))
    pred_scale = 1.99 / max_K
    print(f"max|K| = {max_K:.1f}")
    print(f"Predicted scale = {pred_scale:.10f}")
    
    # Eigenvalues (full decomp is expensive for 1024 — use min/max only)
    print("Computing eigenvalues...")
    t1 = time.time()
    if N <= 500:
        eigvals = np.linalg.eigvalsh(K)
        lam_min, lam_max = eigvals[0], eigvals[-1]
        cond = lam_max / lam_min
    else:
        # For N=1024, use sparse eigsh for extremes
        from scipy.sparse.linalg import eigsh
        from scipy.sparse import csr_matrix
        K_sparse = csr_matrix(K)
        lam_mins = eigsh(K_sparse, k=1, which='SA', return_eigenvectors=False)
        lam_maxs = eigsh(K_sparse, k=1, which='LA', return_eigenvectors=False)
        lam_min, lam_max = float(lam_mins[0]), float(lam_maxs[0])
        cond = lam_max / lam_min
    dt_eig = time.time() - t1
    print(f"Eigenvalues in {dt_eig:.1f}s: [{lam_min:.3f}, {lam_max:.6f}], cond={cond:.3f}")
    
    # Local reference via K^-1 diagonal
    print("Computing K^-1 diagonal...")
    t2 = time.time()
    K_inv = np.linalg.inv(K)
    local_var = -np.diag(K_inv)
    dt_inv = time.time() - t2
    print(f"Inverted in {dt_inv:.1f}s, var range: [{local_var.min():.6f}, {local_var.max():.6f}]")
    
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
    
    upper = math.sqrt(N) + N**0.25 + 1
    lower = math.sqrt(N)
    print(f"Sidon set size: {len(S_sorted)} (bounds: {lower:.2f} – {upper:.2f})")
    print(f"Sidon set: {S_sorted}")
    
    # Export CSV
    fname = f"test_K{N}.csv"
    np.savetxt(fname, K, delimiter=",", fmt="%.10f")
    fsize = os.path.getsize(fname)
    print(f"Exported {fname} ({fsize:,} bytes, {fsize/1024/1024:.1f} MB)")
    
    # Save reference
    ref = {
        "N": N,
        "sidon_size": len(S_sorted),
        "sidon_set": S_sorted,
        "max_K": float(max_K),
        "predicted_scale": float(pred_scale),
        "var_range": [float(local_var.min()), float(local_var.max())],
        "eigval_range": [float(lam_min), float(lam_max)],
        "condition_number": float(cond),
        "build_time_s": dt,
    }
    ref_fname = f"local_reference_{N}.json"
    with open(ref_fname, "w") as f:
        json.dump(ref, f, indent=2)
    print(f"Saved {ref_fname}")
    
    return ref

if __name__ == "__main__":
    sizes = [500, 1024]
    if len(sys.argv) > 1:
        sizes = [int(x) for x in sys.argv[1:]]
    
    results = {}
    for N in sizes:
        results[N] = process_N(N)
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for N, r in results.items():
        print(f"N={N}: |S|={r['sidon_size']}, max|K|={r['max_K']:.1f}, "
              f"cond={r['condition_number']:.3f}, build={r['build_time_s']:.1f}s")
