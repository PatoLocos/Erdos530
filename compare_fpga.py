"""Compare FPGA equilibrium_statistics output vs local K⁻¹ reference."""
import json
import numpy as np
from scipy.stats import pearsonr, spearmanr

# FPGA output for N=30
fpga_expected_var = [
    48.544318, 48.500467, 48.464332, 48.434505, 48.409606,
    48.388917, 48.371652, 48.35742, 48.345752, 48.336434,
    48.329183, 48.323888, 48.320396, 48.318664, 48.318637,
    48.318637, 48.318664, 48.320396, 48.323888, 48.329183,
    48.336434, 48.345752, 48.35742, 48.371652, 48.388917,
    48.409606, 48.434505, 48.464332, 48.500467, 48.544318
]
fpga_sampled_var = [
    7.093272, 7.223259, 7.23414, 7.082533, 6.749005,
    6.629659, 7.08486, 6.346761, 6.780769, 7.789287,
    6.461334, 6.421259, 7.243934, 7.144988, 6.978728,
    6.113317, 6.654454, 6.190667, 7.002402, 6.511609,
    6.820956, 6.993058, 6.822722, 6.586771, 6.870027,
    6.616397, 7.135304, 6.763189, 6.812662, 6.723653
]
fpga_scale = 0.00696611

# Load local reference
with open("local_reference.json") as f:
    ref = json.load(f)

local_var = np.array(ref["30"]["local_var"])
predicted_scale = ref["30"]["predicted_scale"]

fpga_ev = np.array(fpga_expected_var)
fpga_sv = np.array(fpga_sampled_var)

print("=" * 70)
print("FPGA vs LOCAL COMPARISON — N=30 Collision Laplacian")
print("=" * 70)

# 1. Scale factor comparison
print(f"\n--- Scale Factor ---")
print(f"  FPGA reported scale:    {fpga_scale:.10f}")
print(f"  Predicted scale:        {predicted_scale:.10f}")
print(f"  Ratio FPGA/predicted:   {fpga_scale / predicted_scale:.8f}")
print(f"  Difference:             {abs(fpga_scale - predicted_scale):.2e}")

# 2. Expected variance: FPGA vs local
# FPGA expected_var = -[K_s⁻¹]_ii * T = -[(scale*K)⁻¹]_ii = -[K⁻¹]_ii / scale
# Local var = -[K⁻¹]_ii * T (with T=1)
# So: fpga_ev = local_var / scale
local_var_scaled = local_var / fpga_scale  # what FPGA should report

print(f"\n--- Expected Variance (K⁻¹ diagonal) ---")
print(f"  Local var range:        [{local_var.min():.10f}, {local_var.max():.10f}]")
print(f"  FPGA expected_var range:[{fpga_ev.min():.6f}, {fpga_ev.max():.6f}]")
print(f"  Local/scale range:      [{local_var_scaled.min():.6f}, {local_var_scaled.max():.6f}]")

# Element-wise comparison
diff = fpga_ev - local_var_scaled
rel_diff = diff / local_var_scaled
print(f"\n  Max absolute diff:      {np.max(np.abs(diff)):.6f}")
print(f"  Mean absolute diff:     {np.mean(np.abs(diff)):.6f}")
print(f"  Max relative diff:      {np.max(np.abs(rel_diff)):.8f} ({np.max(np.abs(rel_diff))*100:.6f}%)")
print(f"  Mean relative diff:     {np.mean(np.abs(rel_diff)):.8f} ({np.mean(np.abs(rel_diff))*100:.6f}%)")

# Correlation
r_pearson, p_pearson = pearsonr(local_var_scaled, fpga_ev)
r_spearman, p_spearman = spearmanr(local_var_scaled, fpga_ev)
print(f"\n  Pearson r:              {r_pearson:.12f}  (p={p_pearson:.2e})")
print(f"  Spearman ρ:             {r_spearman:.12f}  (p={p_spearman:.2e})")

# 3. Ranking agreement
local_rank = np.argsort(-local_var)  # highest variance first
fpga_rank = np.argsort(-fpga_ev)     # highest variance first

print(f"\n--- Ranking Agreement ---")
print(f"  Local  top-10: {list(local_rank[:10])}")
print(f"  FPGA   top-10: {list(fpga_rank[:10])}")
print(f"  Match:         {list(local_rank[:10]) == list(fpga_rank[:10])}")

# How many of top-k agree?
for k in [5, 10, 15, 30]:
    overlap = len(set(local_rank[:k]) & set(fpga_rank[:k]))
    print(f"  Top-{k:2d} overlap: {overlap}/{k} ({overlap/k*100:.1f}%)")

# 4. Symmetry check on FPGA output
sym_diff = np.abs(fpga_ev - fpga_ev[::-1])
print(f"\n--- FPGA Symmetry Check ---")
print(f"  Max |v[i] - v[N-1-i]|: {np.max(sym_diff):.10f}")
print(f"  Perfectly symmetric:    {np.allclose(fpga_ev, fpga_ev[::-1])}")

# 5. Extract Sidon sets from FPGA ranking
def verify_sidon(S):
    S = sorted(S)
    sums = set()
    for i in range(len(S)):
        for j in range(i, len(S)):
            s = S[i] + S[j]
            if s in sums:
                return False
            sums.add(s)
    return True

def greedy_sidon(ranking, N):
    """Build Sidon set by greedily adding elements in ranking order."""
    S = []
    for elem in ranking:
        candidate = S + [int(elem)]
        if verify_sidon(candidate):
            S.append(int(elem))
    return S

fpga_sidon = greedy_sidon(fpga_rank, 30)
local_sidon = greedy_sidon(local_rank, 30)

print(f"\n--- Sidon Set Extraction ---")
print(f"  From FPGA ranking:  {fpga_sidon} (size {len(fpga_sidon)})")
print(f"  From local ranking: {local_sidon} (size {len(local_sidon)})")
print(f"  FPGA valid Sidon?   {verify_sidon(fpga_sidon)}")
print(f"  Local valid Sidon?  {verify_sidon(local_sidon)}")
print(f"  Sets match?         {set(fpga_sidon) == set(local_sidon)}")
print(f"  Overlap:            {len(set(fpga_sidon) & set(local_sidon))}/{max(len(fpga_sidon), len(local_sidon))}")

# 6. Sampled variance vs expected (Monte Carlo quality)
print(f"\n--- Monte Carlo Sampling Quality ---")
r_mc, _ = pearsonr(fpga_ev, fpga_sv)
rho_mc, _ = spearmanr(fpga_ev, fpga_sv)
mc_ratio = fpga_sv / fpga_ev
print(f"  Pearson r (sampled vs expected):   {r_mc:.6f}")
print(f"  Spearman ρ (sampled vs expected):  {rho_mc:.6f}")
print(f"  Mean(sampled/expected):            {np.mean(mc_ratio):.6f}")
print(f"  Std(sampled/expected):             {np.std(mc_ratio):.6f}")
print(f"  Sampled range: [{fpga_sv.min():.4f}, {fpga_sv.max():.4f}]")
print(f"  Expected range:[{fpga_ev.min():.4f}, {fpga_ev.max():.4f}]")

# 7. Summary table
print(f"\n{'='*70}")
print(f"ELEMENT-WISE COMPARISON TABLE")
print(f"{'='*70}")
print(f"{'i':>3} {'Local var':>12} {'FPGA exp':>12} {'Local/scale':>12} {'Diff':>10} {'Rel%':>8}")
print(f"{'-'*3} {'-'*12} {'-'*12} {'-'*12} {'-'*10} {'-'*8}")
for i in range(30):
    print(f"{i:3d} {local_var[i]:12.10f} {fpga_ev[i]:12.6f} {local_var_scaled[i]:12.6f} "
          f"{diff[i]:10.6f} {rel_diff[i]*100:8.5f}")

print(f"\n✅ FPGA N=30 comparison complete.")
