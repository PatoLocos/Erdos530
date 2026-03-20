"""
Compare FPGA equilibrium_statistics vs local K^{-1} diagonal for N=30, 50, 100.
"""
import json
import numpy as np
from scipy.stats import pearsonr, spearmanr

# ─── Load local reference ───
with open("local_reference.json") as f:
    local_ref = json.load(f)

# ─── FPGA results (from equilibrium_statistics) ───
fpga_results = {
    "30": {
        "scale_factor": 0.00696611,
        "elapsed_ms": 5137,
        "expected_variance": [
            48.544318, 48.500467, 48.464332, 48.434505, 48.409606, 48.388917,
            48.371652, 48.35742, 48.345752, 48.336434, 48.329183, 48.323888,
            48.320396, 48.318664, 48.318637, 48.318637, 48.318664, 48.320396,
            48.323888, 48.329183, 48.336434, 48.345752, 48.35742, 48.371652,
            48.388917, 48.409606, 48.434505, 48.464332, 48.500467, 48.544318
        ]
    },
    "50": {
        "scale_factor": 0.00234711,
        "elapsed_ms": 4938,
        "expected_variance": [
            85.927519, 85.899763, 85.875075, 85.853088, 85.833401, 85.815772,
            85.799924, 85.785693, 85.77288, 85.761371, 85.751022, 85.741753,
            85.733455, 85.726074, 85.719528, 85.713779, 85.708766, 85.704462,
            85.700824, 85.697835, 85.695464, 85.693702, 85.692531, 85.691946,
            85.691941, 85.691941, 85.691946, 85.692531, 85.693702, 85.695464,
            85.697835, 85.700824, 85.704462, 85.708766, 85.713779, 85.719528,
            85.726074, 85.733455, 85.741753, 85.751022, 85.761371, 85.77288,
            85.785693, 85.799924, 85.815772, 85.833401, 85.853088, 85.875075,
            85.899763, 85.927519
        ]
    },
    "100": {
        "scale_factor": 0.0005591,
        "elapsed_ms": 5162,
        "expected_variance": [
            179.590868, 179.576434, 179.562831, 179.550004, 179.537889, 179.526444,
            179.515617, 179.505373, 179.495668, 179.486475, 179.477757, 179.46949,
            179.461645, 179.454201, 179.447133, 179.440425, 179.434054, 179.428007,
            179.422266, 179.416818, 179.411648, 179.406745, 179.402097, 179.397694,
            179.393525, 179.389583, 179.385857, 179.382341, 179.379027, 179.37591,
            179.372981, 179.370237, 179.367671, 179.365279, 179.363056, 179.360999,
            179.359103, 179.357366, 179.355783, 179.354353, 179.353073, 179.35194,
            179.350953, 179.35011, 179.349409, 179.34885, 179.348431, 179.348153,
            179.348013, 179.348012, 179.348012, 179.348013, 179.348153, 179.348431,
            179.34885, 179.349409, 179.35011, 179.350953, 179.35194, 179.353073,
            179.354353, 179.355783, 179.357366, 179.359103, 179.360999, 179.363056,
            179.365279, 179.367671, 179.370237, 179.372981, 179.37591, 179.379027,
            179.382341, 179.385857, 179.389583, 179.393525, 179.397694, 179.402097,
            179.406745, 179.411648, 179.416818, 179.422266, 179.428007, 179.434054,
            179.440425, 179.447133, 179.454201, 179.461645, 179.46949, 179.477757,
            179.486475, 179.495668, 179.505373, 179.515617, 179.526444, 179.537889,
            179.550004, 179.562831, 179.576434, 179.590868
        ]
    }
}


def extract_sidon_from_variance(variances, N):
    """Extract Sidon set by greedy selection from variance ranking."""
    ranked = sorted(range(N), key=lambda i: variances[i], reverse=True)
    S = []
    sums = set()
    for idx in ranked:
        conflict = False
        for s in S:
            pair_sum = idx + s
            if pair_sum in sums:
                conflict = True
                break
        if not conflict:
            for s in S:
                sums.add(idx + s)
            S.append(idx)
    return S


def verify_sidon(S):
    """Verify all pairwise sums are distinct."""
    sums = []
    for i in range(len(S)):
        for j in range(i + 1, len(S)):
            sums.append(S[i] + S[j])
    return len(sums) == len(set(sums))


print("=" * 80)
print("FPGA vs LOCAL COMPARISON — ALL MATRIX SIZES")
print("=" * 80)

for N_str in ["30", "50", "100"]:
    N = int(N_str)
    fpga = fpga_results[N_str]
    local = local_ref[N_str]

    fpga_ev = np.array(fpga["expected_variance"])
    local_var = np.array(local["local_var"])
    scale = fpga["scale_factor"]
    predicted_scale = local["predicted_scale"]

    # FPGA expected_variance = local_var / scale (since K_s = scale * K)
    # So local_var_from_fpga = fpga_ev * scale
    local_var_from_fpga = fpga_ev * scale

    # Correlation
    r_pearson, _ = pearsonr(local_var, local_var_from_fpga)
    r_spearman, _ = spearmanr(local_var, local_var_from_fpga)

    # Relative error
    rel_errors = np.abs(local_var - local_var_from_fpga) / np.abs(local_var) * 100
    max_rel = np.max(rel_errors)
    mean_rel = np.mean(rel_errors)

    # Sidon extraction
    sidon_fpga = extract_sidon_from_variance(fpga_ev.tolist(), N)
    sidon_local = extract_sidon_from_variance(local_var.tolist(), N)
    sidon_ref = local["sidon_var"]

    sidon_fpga_valid = verify_sidon(sidon_fpga)
    sidon_local_valid = verify_sidon(sidon_local)

    # Ranking agreement
    rank_fpga = np.argsort(np.argsort(-fpga_ev))
    rank_local = np.argsort(np.argsort(-local_var))
    rank_match = np.sum(rank_fpga == rank_local)

    # Symmetry check on FPGA output
    sym_diff = np.max(np.abs(fpga_ev - fpga_ev[::-1]))

    # Scale factor comparison
    scale_ratio = scale / predicted_scale

    print(f"\n{'─' * 80}")
    print(f"  N = {N}")
    print(f"{'─' * 80}")
    print(f"  FPGA elapsed:          {fpga['elapsed_ms']} ms")
    print(f"  Scale factor (FPGA):   {scale:.10f}")
    print(f"  Scale factor (pred):   {predicted_scale:.10f}")
    print(f"  Scale ratio:           {scale_ratio:.6f}")
    print()
    print(f"  Pearson r:             {r_pearson:.15f}")
    print(f"  Spearman ρ:            {r_spearman:.15f}")
    print(f"  Max relative error:    {max_rel:.6f}%")
    print(f"  Mean relative error:   {mean_rel:.6f}%")
    print()
    print(f"  FPGA output symmetric: max|v_i - v_(N-1-i)| = {sym_diff:.10f}")
    print(f"  Rank exact matches:    {rank_match}/{N} ({100*rank_match/N:.1f}%)")
    print()
    print(f"  Sidon (FPGA):          {sorted(sidon_fpga)} (size {len(sidon_fpga)}, valid={sidon_fpga_valid})")
    print(f"  Sidon (local):         {sorted(sidon_local)} (size {len(sidon_local)}, valid={sidon_local_valid})")
    print(f"  Sidon (reference):     {sorted(sidon_ref)} (size {len(sidon_ref)})")
    print(f"  FPGA == local Sidon:   {sorted(sidon_fpga) == sorted(sidon_local)}")
    print(f"  FPGA == reference:     {sorted(sidon_fpga) == sorted(sidon_ref)}")

    # Top-k overlap at various k
    top_fpga = set(np.argsort(-fpga_ev)[:10])
    top_local = set(np.argsort(-local_var)[:10])
    overlap = len(top_fpga & top_local)
    print(f"  Top-10 overlap:        {overlap}/10 ({100*overlap/10:.0f}%)")

print(f"\n{'=' * 80}")
print("SUMMARY TABLE")
print(f"{'=' * 80}")
print(f"{'N':>5} | {'Pearson r':>20} | {'Max rel%':>10} | {'Sidon match':>12} | {'|Sidon|':>7} | {'ms':>6}")
print(f"{'─'*5}-+-{'─'*20}-+-{'─'*10}-+-{'─'*12}-+-{'─'*7}-+-{'─'*6}")
for N_str in ["30", "50", "100"]:
    N = int(N_str)
    fpga = fpga_results[N_str]
    local = local_ref[N_str]
    fpga_ev = np.array(fpga["expected_variance"])
    local_var = np.array(local["local_var"])
    scale = fpga["scale_factor"]
    local_var_from_fpga = fpga_ev * scale
    r, _ = pearsonr(local_var, local_var_from_fpga)
    rel_err = np.max(np.abs(local_var - local_var_from_fpga) / np.abs(local_var) * 100)
    sidon_f = sorted(extract_sidon_from_variance(fpga_ev.tolist(), N))
    sidon_l = sorted(extract_sidon_from_variance(local_var.tolist(), N))
    match = "IDENTICAL" if sidon_f == sidon_l else "DIFFER"
    print(f"{N:>5} | {r:>20.15f} | {rel_err:>9.6f}% | {match:>12} | {len(sidon_f):>7} | {fpga['elapsed_ms']:>6}")
