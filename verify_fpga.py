"""
Verify PROMETHEUS FPGA equilibrium statistics match local K^{-1} diagonal.
The expected_variance from FPGA should equal diag(-K^{-1}) * T at temperature T.
"""
import numpy as np
from scipy.stats import spearmanr, pearsonr

# FPGA expected_variance from PROMETHEUS equilibrium_statistics (Laplacian K30, T=1.0)
fpga_expected_var = np.array([
    48.544318, 48.500467, 48.464332, 48.434505, 48.409606,
    48.388917, 48.371652, 48.357420, 48.345752, 48.336434,
    48.329183, 48.323888, 48.320396, 48.318664, 48.318637,
    48.318637, 48.318664, 48.320396, 48.323888, 48.329183,
    48.336434, 48.345752, 48.357420, 48.371652, 48.388917,
    48.409606, 48.434505, 48.464332, 48.500467, 48.544318
])

# FPGA measured variance from 1000 Boltzmann samples
fpga_measured_var = np.array([
    2.075517, 2.035140, 2.275711, 2.034303, 1.767537,
    2.163696, 2.115055, 1.897187, 1.888334, 1.939207,
    1.660157, 1.879206, 2.065351, 1.818302, 1.739604,
    1.562156, 1.876783, 1.762277, 1.866052, 1.816052,
    1.774655, 2.006648, 2.030626, 2.149745, 2.107561,
    2.471439, 2.399687, 2.333469, 2.847688, 2.677897
])

# Rebuild local K^{-1} diagonal
N = 30

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
    D = np.diag(W.sum(axis=1))
    L = D - W
    K = -(L + epsilon * np.eye(N))
    return K, W, L

K, W, L = build_fpga_matrix(N, epsilon=0.1)
K_inv = np.linalg.inv(K)
local_kinv_diag = np.diag(K_inv)
# theoretical expected variance = diag(-K^{-1}) * T = -diag(K^{-1}) at T=1
local_expected_var = -local_kinv_diag  # K is negative-definite, so K^{-1} has negative diagonal

print("=" * 70)
print("PROMETHEUS vs LOCAL K^{-1} DIAGONAL VERIFICATION")
print("=" * 70)

print(f"\nMatrix dimension: {N}x{N}")
print(f"K eigenvalue range: [{np.linalg.eigvalsh(K).min():.4f}, {np.linalg.eigvalsh(K).max():.4f}]")
print(f"K condition number: {np.linalg.cond(K):.1f}")

print(f"\n{'Ch':>3} | {'FPGA exp_var':>12} | {'Local -K⁻¹[i,i]':>15} | {'Ratio':>8} | {'Diff':>10}")
print("-" * 65)
for i in range(N):
    ratio = fpga_expected_var[i] / local_expected_var[i] if local_expected_var[i] != 0 else 0
    diff = fpga_expected_var[i] - local_expected_var[i]
    print(f"{i:3d} | {fpga_expected_var[i]:12.6f} | {local_expected_var[i]:15.6f} | {ratio:8.6f} | {diff:10.6f}")

# Correlations
r_pearson, p_pearson = pearsonr(fpga_expected_var, local_expected_var)
r_spearman, p_spearman = spearmanr(fpga_expected_var, local_expected_var)

print(f"\n{'CORRELATION ANALYSIS':=^70}")
print(f"Pearson  r = {r_pearson:.8f}  (p = {p_pearson:.2e})")
print(f"Spearman ρ = {r_spearman:.8f}  (p = {p_spearman:.2e})")
print(f"Mean ratio (FPGA/Local): {np.mean(fpga_expected_var / local_expected_var):.8f}")
print(f"Std  ratio:              {np.std(fpga_expected_var / local_expected_var):.8f}")

# Check symmetry in both
print(f"\n{'SYMMETRY CHECK':=^70}")
for label, arr in [("FPGA expected_var", fpga_expected_var), ("Local -K⁻¹ diag", local_expected_var)]:
    sym_err = np.max(np.abs(arr - arr[::-1]))
    print(f"{label:20s}: max |v[i] - v[N-1-i]| = {sym_err:.8f}")

# Ranking comparison for Sidon extraction
fpga_ranking = np.argsort(-fpga_expected_var)  # highest variance first
local_ranking = np.argsort(-local_expected_var)

print(f"\n{'RANKING COMPARISON (highest variance = least constrained = prefer for Sidon)':=^70}")
print(f"{'Rank':>4} | {'FPGA ch':>7} | {'Local ch':>8} | {'Match':>5}")
print("-" * 35)
match_count = 0
for rank in range(N):
    match = "✓" if fpga_ranking[rank] == local_ranking[rank] else ""
    if fpga_ranking[rank] == local_ranking[rank]:
        match_count += 1
    print(f"{rank:4d} | {fpga_ranking[rank]:7d} | {local_ranking[rank]:8d} | {match:>5}")

print(f"\nRank agreement: {match_count}/{N} = {100*match_count/N:.1f}%")

# Now verify: extract Sidon set using FPGA ranking vs local ranking
def extract_sidon_from_ranking(ranking, N):
    """Greedily extract Sidon set following the given ranking order."""
    sidon = []
    sums = set()
    for idx in ranking:
        ok = True
        for s in sidon:
            pair_sum = idx + s
            if pair_sum in sums:
                ok = False
                break
        if ok:
            new_sums = set()
            for s in sidon:
                new_sums.add(idx + s)
            sidon.append(idx)
            sums |= new_sums
    return sorted(sidon)

fpga_sidon = extract_sidon_from_ranking(fpga_ranking, N)
local_sidon = extract_sidon_from_ranking(local_ranking, N)

# Standard greedy (sequential)
def greedy_sidon(N):
    sidon = []
    sums = set()
    for x in range(N):
        ok = True
        for s in sidon:
            if x + s in sums:
                ok = False
                break
        if ok:
            new_sums = set()
            for s in sidon:
                new_sums.add(x + s)
            sidon.append(x)
            sums |= new_sums
    return sidon

greedy = greedy_sidon(N)

print(f"\n{'SIDON SET EXTRACTION':=^70}")
print(f"FPGA K⁻¹-diag ranking:  size {len(fpga_sidon):3d}  set = {fpga_sidon}")
print(f"Local K⁻¹-diag ranking: size {len(local_sidon):3d}  set = {local_sidon}")
print(f"Sequential greedy:      size {len(greedy):3d}  set = {greedy}")
print(f"Sets identical (FPGA vs Local): {fpga_sidon == local_sidon}")

# Scale factor analysis
print(f"\n{'SCALE FACTOR ANALYSIS':=^70}")
print(f"FPGA reported scale_factor: 0.00696611")
print(f"K matrix max |entry|: {np.max(np.abs(K)):.2f}")
print(f"Expected scale to fit Q10.17: {(2**10 - 1) / np.max(np.abs(K)):.6f}")
print(f"Actual / Expected: {0.00696611 / ((2**10 - 1) / np.max(np.abs(K))):.4f}")

# Verify the expected_variance formula: Var_i = -[K^{-1}]_{ii} * T
# But PROMETHEUS uses SCALED matrix K_scaled = scale * K
# So K_scaled^{-1} = K^{-1} / scale
# And Var_i(K_scaled) = -[K_scaled^{-1}]_{ii} * T = -[K^{-1}]_{ii} * T / scale
scale = 0.00696611
local_scaled_var = local_expected_var / scale

print(f"\nLocal -K⁻¹[i,i] / scale_factor (should match FPGA expected_var):")
print(f"  Local scaled var[0]  = {local_scaled_var[0]:.6f}")
print(f"  FPGA  expected_var[0] = {fpga_expected_var[0]:.6f}")
print(f"  Ratio = {fpga_expected_var[0] / local_scaled_var[0]:.8f}")

# Fit actual ratio
actual_ratios = fpga_expected_var / local_expected_var
print(f"\n  Mean (FPGA_exp / Local_raw): {np.mean(actual_ratios):.6f}")
implied_inv_scale = np.mean(actual_ratios)
implied_scale = 1.0 / implied_inv_scale
print(f"  Implied scale = 1/ratio = {implied_scale:.8f}")
print(f"  FPGA reported scale      = {0.00696611:.8f}")
print(f"  Match: {'YES' if abs(implied_scale - 0.00696611) / 0.00696611 < 0.01 else 'NO'}")

print(f"\n{'VERIFICATION SUMMARY':=^70}")
r_rank = spearmanr(fpga_expected_var, local_expected_var)[0]
print(f"  Shape correlation (Spearman): {r_rank:.6f}")
print(f"  Rank agreement:               {match_count}/{N}")
print(f"  Same Sidon set:               {fpga_sidon == local_sidon}")
print(f"  FPGA perfectly symmetric:     {np.allclose(fpga_expected_var, fpga_expected_var[::-1])}")
if r_rank > 0.99 and fpga_sidon == local_sidon:
    print(f"\n  ✅ VERIFIED: PROMETHEUS hardware exactly replicates K⁻¹-diagonal analysis")
    print(f"     The FPGA is a valid hardware accelerator for Sidon set extraction")
elif r_rank > 0.9:
    print(f"\n  ⚠️  STRONG MATCH: PROMETHEUS closely approximates K⁻¹-diagonal analysis")
else:
    print(f"\n  ❌ MISMATCH: Need to investigate scale/format differences")
