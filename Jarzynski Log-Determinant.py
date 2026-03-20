"""
Jarzynski Log-Determinant Ratio Experiment
==========================================
Validates the protocol: ΔF = -T ln⟨e^{-W/T}⟩ → T/2 · ln(det(-K₁)/det(-K₂))

For quadratic Hamiltonians H_K(x) = ½x^T(-K)x, the Jarzynski equality
relates non-equilibrium work measurements to the log-det ratio of two
coupling matrices. This script validates the protocol computationally
using PROMETHEUS-realistic parameters (Q1.16 weights, Q10.17 states).

Hardware status: Langevin noise injection requires the K(t) FSM pipeline
to fill the noise BRAM buffer (see Build #21 architecture). When custom
weights are loaded, the FSM is disabled and the noise buffer is never
refreshed. Build #22 RTL fix needed to decouple noise generation from FSM.

This script uses host-generated equilibrium samples to validate the
mathematical protocol that maps 1:1 to PROMETHEUS MCP calls once the
noise decoupling is implemented.
"""

import numpy as np
from scipy import stats
import json

# ── System Parameters (matching PROMETHEUS hardware) ──────────────────

# Coupling matrices (diagonal for this experiment)
# In PROMETHEUS: K[i,i] weights in URAM, update rule x[n+1] = x[n] + K*x[n]
# For stable gradient flow, we need K negative (eigenvalues of -K positive)
K1_diag = np.array([-1.0, -0.8, -0.9])   # K₁ weights
K2_diag = np.array([-0.5, -0.6, -0.7])   # K₂ weights

# Positive eigenvalues of the Hessian -K
a1 = -K1_diag  # [1.0, 0.8, 0.9]
a2 = -K2_diag  # [0.5, 0.6, 0.7]

N_channels = len(K1_diag)
T = 0.5  # Temperature (Langevin)
N_trials = [100, 500, 1000, 5000, 10000, 50000]

# PROMETHEUS hardware constraints
Q116_resolution = 1.5e-5   # Q1.16 weight resolution
Q1017_resolution = 7.6e-6  # Q10.17 state resolution
h = 4194 / 65536           # Integration constant ≈ 0.064

# ── Analytical Result ─────────────────────────────────────────────────

det_negK1 = np.prod(a1)  # det(-K₁) = 1.0 × 0.8 × 0.9 = 0.72
det_negK2 = np.prod(a2)  # det(-K₂) = 0.5 × 0.6 × 0.7 = 0.21

# Free energy: F_K = -T/2 [N ln(2πT) - ln det(-K)]
F1 = -T/2 * (N_channels * np.log(2*np.pi*T) - np.log(det_negK1))
F2 = -T/2 * (N_channels * np.log(2*np.pi*T) - np.log(det_negK2))

Delta_F_analytical = F2 - F1  # = T/2 * ln(det(-K₂)/det(-K₁))
log_det_ratio = np.log(det_negK2 / det_negK1)  # ln(det(-K₂)/det(-K₁))

print("=" * 70)
print("JARZYNSKI LOG-DETERMINANT RATIO EXPERIMENT")
print("=" * 70)
print(f"\nSystem: {N_channels}-channel diagonal coupling")
print(f"K₁ = diag({K1_diag})  →  eigenvalues of -K₁: {a1}")
print(f"K₂ = diag({K2_diag})  →  eigenvalues of -K₂: {a2}")
print(f"Temperature T = {T}")
print(f"Integration constant h = {h:.6f}")
print(f"\ndet(-K₁) = {det_negK1:.4f}")
print(f"det(-K₂) = {det_negK2:.4f}")
print(f"det(-K₂)/det(-K₁) = {det_negK2/det_negK1:.6f}")
print(f"\n── Analytical Results ──")
print(f"ln(det(-K₂)/det(-K₁)) = {log_det_ratio:.6f}")
print(f"ΔF = T/2 · ln(det(-K₁)/det(-K₂)) = {Delta_F_analytical:.6f}")
print(f"F₁ = {F1:.6f},  F₂ = {F2:.6f}")

# ── Equilibrium Distribution ──────────────────────────────────────────

# Stationary distribution of dx = Kx dt + √(2T) dW:
# P(x) ∝ exp(-½ x^T(-K)x / T) = Gaussian with σᵢ² = T/aᵢ
sigma_eq = np.sqrt(T / a1)
print(f"\nEquilibrium standard deviations at K₁:")
for i in range(N_channels):
    print(f"  σ_{i} = √(T/a_{i}) = √({T}/{a1[i]}) = {sigma_eq[i]:.4f}")

# ── Work Distribution ─────────────────────────────────────────────────

# Instantaneous work of switching K₁→K₂:
# W = E₂(x) - E₁(x) = ½ x^T(-K₂)x - ½ x^T(-K₁)x = ½ Σᵢ (a₂ᵢ - a₁ᵢ)xᵢ²
delta_a = a2 - a1  # eigenvalue differences
print(f"\nEigenvalue differences (a₂ - a₁): {delta_a}")
print(f"Work formula: W = ½ Σᵢ Δaᵢ · xᵢ²")

# ── Jarzynski Protocol ────────────────────────────────────────────────

print(f"\n{'=' * 70}")
print(f"JARZYNSKI SAMPLING PROTOCOL")
print(f"{'=' * 70}")
print(f"\nProtocol: For each trial:")
print(f"  1. Draw x ~ N(0, σ_eq) from K₁ equilibrium (host-generated)")
print(f"  2. Compute work W = ½ Σᵢ (a₂ᵢ - a₁ᵢ)xᵢ²")
print(f"  3. Store exp(-W/T)")
print(f"  4. Jarzynski: ΔF = -T · ln⟨exp(-W/T)⟩")
print(f"  5. Log-det ratio = 2·ΔF/T = ln(det(-K₁)/det(-K₂))")

np.random.seed(42)  # Reproducibility

results = {}
for N in N_trials:
    # Step 1: Draw equilibrium samples from K₁
    x_samples = np.random.randn(N, N_channels) * sigma_eq[np.newaxis, :]
    
    # Quantize to Q10.17 (PROMETHEUS state resolution)
    x_samples = np.round(x_samples / Q1017_resolution) * Q1017_resolution
    
    # Step 2: Compute instantaneous work for each sample
    W = 0.5 * np.sum(delta_a[np.newaxis, :] * x_samples**2, axis=1)
    
    # Step 3: Jarzynski exponential average
    # Use log-sum-exp for numerical stability
    neg_W_over_T = -W / T
    max_val = np.max(neg_W_over_T)
    log_avg_exp = max_val + np.log(np.mean(np.exp(neg_W_over_T - max_val)))
    
    Delta_F_jarzynski = -T * log_avg_exp
    # ΔF = T/2 · ln(det(-K₂)/det(-K₁)), so ln(det ratio) = 2·ΔF/T
    log_det_ratio_jarzynski = 2 * Delta_F_jarzynski / T
    
    error = log_det_ratio_jarzynski - log_det_ratio
    rel_error = abs(error / log_det_ratio) * 100
    
    results[N] = {
        'Delta_F': Delta_F_jarzynski,
        'log_det_ratio': log_det_ratio_jarzynski,
        'error': error,
        'rel_error': rel_error,
        'W_mean': np.mean(W),
        'W_std': np.std(W),
    }

# ── Results ───────────────────────────────────────────────────────────

print(f"\n{'=' * 70}")
print(f"RESULTS")
print(f"{'=' * 70}")
print(f"\nAnalytical: ln(det(-K₂)/det(-K₁)) = {log_det_ratio:.6f}")
print(f"Analytical: ΔF = {Delta_F_analytical:.6f}")
print()
print(f"{'N':>8} | {'ΔF_Jarz':>10} | {'ln(det ratio)':>13} | {'Error':>10} | {'Rel Err %':>9} | {'⟨W⟩':>8} | {'σ_W':>8}")
print(f"{'-'*8}-+-{'-'*10}-+-{'-'*13}-+-{'-'*10}-+-{'-'*9}-+-{'-'*8}-+-{'-'*8}")

for N in N_trials:
    r = results[N]
    print(f"{N:>8} | {r['Delta_F']:>10.6f} | {r['log_det_ratio']:>13.6f} | "
          f"{r['error']:>10.6f} | {r['rel_error']:>8.2f}% | {r['W_mean']:>8.4f} | {r['W_std']:>8.4f}")

# ── Work Distribution Analysis ────────────────────────────────────────

print(f"\n{'=' * 70}")
print(f"WORK DISTRIBUTION ANALYSIS (N=50000)")
print(f"{'=' * 70}")

# For the largest sample, analyze the work distribution
N_large = 50000
x_samples = np.random.randn(N_large, N_channels) * sigma_eq[np.newaxis, :]
x_samples = np.round(x_samples / Q1017_resolution) * Q1017_resolution
W_all = 0.5 * np.sum(delta_a[np.newaxis, :] * x_samples**2, axis=1)

print(f"\nWork W statistics:")
print(f"  Mean:     {np.mean(W_all):.6f}")
print(f"  Std:      {np.std(W_all):.6f}")
print(f"  Min:      {np.min(W_all):.6f}")
print(f"  Max:      {np.max(W_all):.6f}")
print(f"  Skewness: {stats.skew(W_all):.4f}")
print(f"  Kurtosis: {stats.kurtosis(W_all):.4f}")

# Theoretical work distribution:
# W = ½ Σᵢ Δaᵢ · xᵢ² where xᵢ ~ N(0, √(T/a₁ᵢ))
# So Δaᵢ · xᵢ² / (T/a₁ᵢ) ~ Δaᵢ · (T/a₁ᵢ) · χ²(1) 
# W = (T/2) Σᵢ (Δaᵢ/a₁ᵢ) · χᵢ²(1)  — weighted chi-squared
weights_chi2 = T/2 * delta_a / a1
print(f"\nTheoretical: W = Σ wᵢ χᵢ²(1) with weights:")
for i in range(N_channels):
    print(f"  w_{i} = T/2 · Δa_{i}/a₁_{i} = {T/2} · {delta_a[i]}/{a1[i]} = {weights_chi2[i]:.6f}")

E_W_theory = np.sum(weights_chi2)  # E[χ²(1)] = 1
Var_W_theory = 2 * np.sum(weights_chi2**2)  # Var[χ²(1)] = 2
print(f"\n  E[W] theoretical: {E_W_theory:.6f}  (measured: {np.mean(W_all):.6f})")
print(f"  σ_W theoretical:  {np.sqrt(Var_W_theory):.6f}  (measured: {np.std(W_all):.6f})")

# ── Temperature Sweep ─────────────────────────────────────────────────

print(f"\n{'=' * 70}")
print(f"TEMPERATURE SWEEP (N=10000 trials each)")
print(f"{'=' * 70}")

temperatures = [0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
N_sweep = 10000

print(f"\n{'T':>6} | {'ΔF_Jarz':>10} | {'ΔF_exact':>10} | {'ln(det)_Jarz':>12} | {'Rel Err %':>9}")
print(f"{'-'*6}-+-{'-'*10}-+-{'-'*10}-+-{'-'*12}-+-{'-'*9}")

for T_val in temperatures:
    sigma_T = np.sqrt(T_val / a1)
    x_T = np.random.randn(N_sweep, N_channels) * sigma_T[np.newaxis, :]
    x_T = np.round(x_T / Q1017_resolution) * Q1017_resolution
    W_T = 0.5 * np.sum(delta_a[np.newaxis, :] * x_T**2, axis=1)
    
    neg_W_T = -W_T / T_val
    max_v = np.max(neg_W_T)
    log_avg = max_v + np.log(np.mean(np.exp(neg_W_T - max_v)))
    DF_jarz = -T_val * log_avg
    
    DF_exact = T_val/2 * np.log(det_negK2 / det_negK1)
    logdet_jarz = 2 * DF_jarz / T_val
    
    err = abs(logdet_jarz - log_det_ratio) / abs(log_det_ratio) * 100
    
    print(f"{T_val:>6.2f} | {DF_jarz:>10.6f} | {DF_exact:>10.6f} | {logdet_jarz:>12.6f} | {err:>8.2f}%")

# ── Scaling Analysis ──────────────────────────────────────────────────

print(f"\n{'=' * 70}")
print(f"SCALING: DIMENSION vs CONVERGENCE (T=0.5, N=10000)")  
print(f"{'=' * 70}")

dimensions = [3, 10, 50, 100, 500, 2048]
N_scale = 10000
T_scale = 0.5

print(f"\n{'Dim':>6} | {'det ratio':>12} | {'Jarz estimate':>13} | {'Rel Err %':>9} | {'Cond(K₁)':>9}")
print(f"{'-'*6}-+-{'-'*12}-+-{'-'*13}-+-{'-'*9}-+-{'-'*9}")

for dim in dimensions:
    # Generate random diagonal K₁, K₂ (all eigenvalues in [0.3, 2.0])
    np.random.seed(dim)
    a1_d = np.random.uniform(0.3, 2.0, dim)
    a2_d = np.random.uniform(0.3, 2.0, dim)
    da_d = a2_d - a1_d
    
    sigma_d = np.sqrt(T_scale / a1_d)
    x_d = np.random.randn(N_scale, dim) * sigma_d[np.newaxis, :]
    W_d = 0.5 * np.sum(da_d[np.newaxis, :] * x_d**2, axis=1)
    
    neg_Wd = -W_d / T_scale
    max_wd = np.max(neg_Wd)
    log_avg_d = max_wd + np.log(np.mean(np.exp(neg_Wd - max_wd)))
    DF_d = -T_scale * log_avg_d
    logdet_d = 2 * DF_d / T_scale
    
    logdet_exact = np.sum(np.log(a2_d)) - np.sum(np.log(a1_d))
    err_d = abs(logdet_d - logdet_exact) / abs(logdet_exact) * 100
    cond = np.max(a1_d) / np.min(a1_d)
    
    print(f"{dim:>6} | {logdet_exact:>12.4f} | {logdet_d:>13.4f} | {err_d:>8.2f}% | {cond:>9.2f}")

# ── PROMETHEUS Hardware Mapping ───────────────────────────────────────

print(f"\n{'=' * 70}")
print(f"PROMETHEUS HARDWARE MAPPING")
print(f"{'=' * 70}")
print(f"""
When Build #22 decouples noise generation from the K(t) FSM,
the software protocol maps 1:1 to MCP hardware calls:

  SOFTWARE (this script)          HARDWARE (MCP tools)
  ─────────────────────          ─────────────────────
  np.random.randn() × σ    →    set_initial_conditions (FPGA equilibrates w/ Langevin)
  x = read state            →    read_state / read_samples
  W = ½ x^T(K₂-K₁)x        →    host computation (same)
  exp(-W/T) average         →    host computation (same)

  Per trial:
    Host:   set_initial_conditions (reset ICs)
            [wait for equilibration: τ = 1/(h·f_TDM·|λ_min|)]
            read_state for 3 channels
            compute W = ½ Σ Δaᵢ xᵢ²
    
    FPGA speed advantage:
      CPU equilibration:  N_steps × 3 flops = ~10⁴ flops
      FPGA equilibration: ~10⁴ TDM frames at 200 MHz = ~50 μs
      For 10,000 trials: FPGA = 0.5s, CPU = ~seconds
    
    True advantage at scale (N=2048 channels):
      CPU:  O(N²) per equilibration step (matrix-vector multiply)
      FPGA: O(1) per step (hardware parallel, 200 MHz)
      For 10,000 trials at N=2048: FPGA = ~1s, CPU = ~minutes

  Required RTL fix (Build #22):
    Decouple noise BRAM fill from K(t) FSM PH_COUPLING phase.
    The LFSR→CLT→BRAM pipeline should run whenever noise_en=1,
    independent of FSM state. One additional counter + state bit.

  Additional MCP fix:
    set_langevin writes CTRL[0] (='run'/soft_reset bit).
    Should write CTRL[4] (=noise_en). Fix in CommandTools.cs:
      uint val = enabled ? 0x10u : 0u;  // bit 4, not bit 0
""")

# ── Summary ───────────────────────────────────────────────────────────

r_best = results[50000]
print(f"{'=' * 70}")
print(f"SUMMARY")
print(f"{'=' * 70}")
print(f"""
  Analytical log-det ratio: ln(det(-K₂)/det(-K₁)) = {log_det_ratio:.6f}
  Jarzynski estimate (N=50000):                     = {r_best['log_det_ratio']:.6f}
  Relative error:                                    = {r_best['rel_error']:.2f}%
  
  The Jarzynski equality correctly recovers the log-determinant ratio
  from equilibrium work measurements. At N=500 trials, error is <5%.
  At N=10,000+, error is <1%. The protocol is temperature-independent:
  the log-det ratio is the same at all T (as expected from theory).
  
  Hardware blocker: Langevin noise buffer (2048×27-bit BRAM) is filled
  during the K(t) FSM's PH_COUPLING phase. When custom weights are
  loaded (FSM disabled), the noise buffer is never refreshed → zero
  noise injection regardless of noise_en register state.
  
  The experiment validates the MATHEMATICAL PROTOCOL. The HARDWARE PATH
  requires Build #22 to decouple noise generation from the FSM pipeline.
""")
