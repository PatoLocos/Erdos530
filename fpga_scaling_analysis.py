"""
PROMETHEUS FPGA Scaling Analysis — Erdős Problem 530
Analyzes phase_transition + spectral_gap + equilibrium results across N=30,50,100,200,500,1024
FPGA hardware: Build #53, XCKU5P, 1024 channels, Q1.16 fixed-point
"""

import numpy as np
import json

# ════════════════════════════════════════════════════════════
# 1. Phase Transition Results (from FPGA sweeps)
# ════════════════════════════════════════════════════════════

phase_transition = {
    30: {
        "chi_peak_T": 0.100, "chi_peak_val": 13.81,
        "elapsed_s": 193.0,
        # Σσ² at selected temperatures
        "sigma2_T5": 11740.246, "sigma2_T1": 1885.168, "sigma2_T01": 410.466,
    },
    50: {
        "chi_peak_T": 0.100, "chi_peak_val": 25.90,
        "elapsed_s": 186.0,
        "sigma2_T5": 19991.333, "sigma2_T1": 7014.123, "sigma2_T01": 508.226,
    },
    100: {
        "chi_peak_T": 0.616, "chi_peak_val": 4.69,
        "elapsed_s": 183.0,
        "sigma2_T5": 18026.180, "sigma2_T1": 10359.480, "sigma2_T01": 1243.158,
    },
    200: {
        "chi_peak_T": 3.968, "chi_peak_val": 0.29,
        "elapsed_s": 202.0,
        "sigma2_T5": 46392.464, "sigma2_T1": 7553.432, "sigma2_T01": 2647.694,
    },
    500: {
        "chi_peak_T": 4.742, "chi_peak_val": 7.15,
        "elapsed_s": 201.0,
        "sigma2_T5": 37886.212, "sigma2_T1": 11033.618, "sigma2_T01": 10935.368,
    },
    1024: {
        "chi_peak_T": 0.358, "chi_peak_val": 0.00,
        "elapsed_s": 271.0,
        "sigma2_T5": 31663322.387, "sigma2_T1": 52864372.514, "sigma2_T01": 42325917.109,
    },
}

# ════════════════════════════════════════════════════════════
# 2. Spectral Gap Results
# ════════════════════════════════════════════════════════════

spectral_gap = {
    30:  {"gap": 0.010444, "r2": 0.9554, "tau_int": 78.46,
          "ESS": 12, "theo_gap_diag": 25.099, "acf1": 0.9458},
    50:  {"gap": 0.001773, "r2": 0.8576, "tau_int": 126.9,
          "ESS": 7,  "theo_gap_diag": 73.735, "acf1": 0.9275},
    100: {"gap": 0.005996, "r2": 0.9904, "tau_int": 82.01,
          "ESS": 12, "theo_gap_diag": 307.319, "acf1": 0.8801},
    200: {"gap": 0.001973, "r2": 0.9839, "tau_int": 139.77,
          "ESS": 7,  "theo_gap_diag": 1254.450, "acf1": 0.9448},
    500: {"gap": 0.004004, "r2": 0.9471, "tau_int": 80.52,
          "ESS": 12, "theo_gap_diag": 7935.566, "acf1": 0.7496},
    1024: {"gap": 0.001120, "r2": 0.9906, "tau_int": 180.62,
          "ESS": 5,  "theo_gap_diag": 33421.078, "acf1": 0.9911},
}

# ════════════════════════════════════════════════════════════
# 3. Sidon Set Results & Known Bounds
# ════════════════════════════════════════════════════════════

sidon_results = {
    30:  {"local_sidon": 7,  "sqrt_N": 5.477, "upper": 5.477 + 30**0.25 + 1},
    50:  {"local_sidon": 9,  "sqrt_N": 7.071, "upper": 7.071 + 50**0.25 + 1},
    100: {"local_sidon": 12, "sqrt_N": 10.0,  "upper": 10.0 + 100**0.25 + 1},
    200: {"local_sidon": 16, "sqrt_N": 14.142,"upper": 14.142 + 200**0.25 + 1},
    500: {"local_sidon": 23, "sqrt_N": 22.361,"upper": 22.361 + 500**0.25 + 1},
    1024: {"local_sidon": 30, "sqrt_N": 32.0,  "upper": 32.0 + 1024**0.25 + 1},
}

# ════════════════════════════════════════════════════════════
# 4. Eigenvalue / Conditioning
# ════════════════════════════════════════════════════════════

eigenvalues = {
    30:  {"lam_min": -300.106,  "lam_max": -0.431, "cond": 695.9,  "scale": 0.006716},
    50:  {"lam_min": None,      "lam_max": None,    "cond": None,   "scale": 0.002400},
    100: {"lam_min": None,      "lam_max": None,    "cond": None,   "scale": 0.000651},
    200: {"lam_min": -14692.8,  "lam_max": -5177.84,"cond": 2.838,  "scale": 0.000136},
    500: {"lam_min": -92877.1,  "lam_max": -49566.5, "cond": 1.874,  "scale": 0.0000215},
    1024: {"lam_min": -391426.0, "lam_max": -235014.0,"cond": 1.666,  "scale": 0.00000511},
}

# ════════════════════════════════════════════════════════════
# ANALYSIS
# ════════════════════════════════════════════════════════════

Ns = [30, 50, 100, 200, 500, 1024]

print("=" * 80)
print("PROMETHEUS FPGA — Erdős 530 Scaling Analysis")
print("=" * 80)

# A) Sidon Set Scaling
print("\n── Sidon Set |S|(N) vs Bounds ──")
print(f"{'N':>6} {'|S|':>5} {'√N':>7} {'√N+N^¼+1':>10} {'|S|/√N':>8}")
print("-" * 42)
for N in Ns:
    s = sidon_results[N]
    ratio = s["local_sidon"] / s["sqrt_N"]
    print(f"{N:>6} {s['local_sidon']:>5} {s['sqrt_N']:>7.3f} {s['upper']:>10.3f} {ratio:>8.3f}")

# B) Spectral Gap Scaling
print("\n── Spectral Gap Δ(N) — MCMC Mixing ──")
print(f"{'N':>6} {'Δ':>10} {'R²':>8} {'τ_int':>8} {'ESS':>5} {'Δ_theo':>10} {'ρ(1)':>7}")
print("-" * 60)
for N in Ns:
    g = spectral_gap[N]
    print(f"{N:>6} {g['gap']:>10.6f} {g['r2']:>8.4f} {g['tau_int']:>8.2f} "
          f"{g['ESS']:>5} {g['theo_gap_diag']:>10.3f} {g['acf1']:>7.4f}")

# C) Phase Transition
print("\n── Phase Transition χ_peak ──")
print(f"{'N':>6} {'T_c (χ peak)':>14} {'χ_max':>8} {'Σσ²(T→0)':>12}")
print("-" * 45)
for N in Ns:
    p = phase_transition[N]
    print(f"{N:>6} {p['chi_peak_T']:>14.3f} {p['chi_peak_val']:>8.2f} {p['sigma2_T01']:>12.1f}")

# D) Scale Factor / Condition Number
print("\n── Conditioning & Scale ──")
print(f"{'N':>6} {'scale':>12} {'cond':>8} {'max|K|':>10}")
print("-" * 40)
max_K = {30: 296.1, 50: 830.6, 100: 3059.4, 200: 14652.1, 500: 92877.1, 1024: 391426.0}
for N in Ns:
    e = eigenvalues[N]
    cond_str = f"{e['cond']:.1f}" if e['cond'] else "N/A"
    print(f"{N:>6} {e['scale']:>12.6f} {cond_str:>8} {max_K[N]:>10.1f}")

# E) Computation Time
print("\n── FPGA Compute Time ──")
print(f"{'N':>6} {'phase_trans':>12} {'spectral':>10}")
print("-" * 32)
for N in Ns:
    pt = phase_transition[N]["elapsed_s"]
    sg_ms = {30: 5306, 50: 5671, 100: 5813, 200: 6194, 500: 8510, 1024: 16864}[N]
    print(f"{N:>6} {pt:>10.0f}s {sg_ms/1000:>8.1f}s")

# F) Key Findings
print("\n" + "=" * 80)
print("KEY FINDINGS")
print("=" * 80)
print("""
1. SIDON SCALING: |S|/√N ratios = {:.3f} → {:.3f} → {:.3f} → {:.3f} → {:.3f} → {:.3f}
   Above 1.0 for N≤500, but DROPS to 0.938 at N=1024!
   First instance where greedy-from-variance falls BELOW Singer √N bound.
   The variance landscape becomes too flat for greedy extraction at large N.
   
2. SPECTRAL GAP: Non-monotonic, but 1024 is hardest.
   N=30: Δ=0.0104, N=500: Δ=0.0040, N=1024: Δ=0.0011
   N=1024 has slowest mixing: τ_int=180.6, ESS=5, ρ(1)=0.99.
   
3. PHASE TRANSITION: Extreme Σσ² at N=1024.
   N=30-500: Σσ² in thousands. N=1024: Σσ² ~ 50 million.
   The system variance explodes — collision landscape is extremely rough.
   χ peak vanishes (χ=0.00) — no clear phase transition detected.

4. FPGA NEAR-CONSTANT TIME: Phase transition sweep scales very gently.
   N=30: 193s, N=500: 201s, N=1024: 271s.
   Only 40% overhead for 1166× more dimensions. True parallel sampling.
   Spectral gap: 5.3s → 16.9s. Still sub-linear in dimension.

5. CONDITION NUMBER: Monotonically improving.
   N=30: cond=695.9 → N=200: 2.84 → N=500: 1.87 → N=1024: 1.67
   Collision Laplacian eigenvalues cluster tighter as N grows.
   Better conditioning → better FPGA fixed-point accuracy.

6. FPGA AT FULL CAPACITY: All 1024 channels utilized.
   N=1024 loads 1,048,574 non-zero weights into 262,144 URAM rows.
   Scale factor = 5.11e-6 (extreme compression into Q1.16).
""".format(*[sidon_results[N]["local_sidon"]/sidon_results[N]["sqrt_N"] for N in Ns]))
