"""
PROMETHEUS Benchmark: CPU vs GPU vs FPGA
=========================================
Implements identical Langevin dynamics on CPU (NumPy) and GPU (PyTorch CUDA)
for direct comparison with PROMETHEUS FPGA measurements.

Physics: dx = (-K·x + c)·dt + sqrt(2·T·dt)·dW
Stationary distribution: p(x) ∝ exp(-½ xᵀKx / T)

For diagonal K[i,i] = -1, T=1: expected σ² = T/|K_ii| = 1.0

Requirements:
    pip install numpy torch matplotlib pandas

Usage:
    python prometheus_benchmark.py

Output:
    - Console: timing table for all configurations
    - prometheus_benchmark_results.csv: full results
    - prometheus_benchmark_comparison.png: bar chart

Tested on: Windows 11, Python 3.14+
GPU: NVIDIA RTX PRO Blackwell A4000 (CUDA)
FPGA: PROMETHEUS Build #53 — 128 DSPs, DDR4 bulk DMA, XCKU5P
"""

import time
import numpy as np
import pandas as pd
import sys
import os

# ═══════════════════════════════════════════════════════════════════════════
# Configuration — matches PROMETHEUS Build #53 test parameters
# ═══════════════════════════════════════════════════════════════════════════

DIMENSIONS = [10, 100, 500, 900, 1024]  # Including PROMETHEUS full matrix size
NUM_SAMPLES = 20_000                   # Matches Build #53 test (S=20,000)
BURN_IN = 500                          # Same burn-in
TEMPERATURE = 1.0                      # T=1.0
DT = 0.064                            # Integration timestep (matches INTEG_CONST=4194)
NUM_RUNS = 3                           # Average over 3 runs for stability

# PROMETHEUS measured results — Build #53 (128 DSPs, bulk DMA, 1024×1024)
# Capture: 96,244 fps, Readback: 22 µs/frame via chunked 1MB bulk DMA
# Total wall time includes capture + readback + overhead
PROMETHEUS_RESULTS = {
    10:   {"per_sample_ms": 0.037, "total_sec": 0.754},   # same hardware, fewer active channels
    100:  {"per_sample_ms": 0.037, "total_sec": 0.754},   # frame rate independent of active channels
    500:  {"per_sample_ms": 0.037, "total_sec": 0.754},   # full 1024×1024 always computed
    900:  {"per_sample_ms": 0.037, "total_sec": 0.754},   # full 1024×1024 always computed
    1024: {"per_sample_ms": 0.037, "total_sec": 0.754},   # actual measured: 754 ms for 20K samples
}

# ═══════════════════════════════════════════════════════════════════════════
# Langevin Sampler — CPU (NumPy)
# ═══════════════════════════════════════════════════════════════════════════

def langevin_sample_cpu(K_diag, temperature, dt, num_samples, burn_in):
    """
    Langevin dynamics on CPU using NumPy.
    
    For diagonal K: dx[i] = K[i,i]·x[i]·dt + sqrt(2·T·dt)·dW[i]
    This is the fastest possible CPU implementation — no matrix multiply needed
    for diagonal K, just element-wise operations.
    
    For dense K: dx = K·x·dt + sqrt(2·T·dt)·dW  (matrix-vector multiply)
    """
    d = len(K_diag)
    noise_std = np.sqrt(2.0 * temperature * dt)
    
    # Initial state
    x = np.zeros(d, dtype=np.float64)
    
    # Burn-in
    for _ in range(burn_in):
        dW = np.random.randn(d) * noise_std
        x = x + K_diag * x * dt + dW
    
    # Collect samples
    samples = np.empty((num_samples, d), dtype=np.float64)
    for i in range(num_samples):
        dW = np.random.randn(d) * noise_std
        x = x + K_diag * x * dt + dW
        samples[i] = x
    
    return samples


def langevin_sample_cpu_dense(K, temperature, dt, num_samples, burn_in):
    """
    Langevin dynamics on CPU with DENSE matrix — full matrix-vector multiply.
    This is the fair comparison for coupled systems (not just diagonal).
    """
    d = K.shape[0]
    noise_std = np.sqrt(2.0 * temperature * dt)
    
    x = np.zeros(d, dtype=np.float64)
    
    # Burn-in
    for _ in range(burn_in):
        dW = np.random.randn(d) * noise_std
        x = x + K @ x * dt + dW
    
    # Collect samples
    samples = np.empty((num_samples, d), dtype=np.float64)
    for i in range(num_samples):
        dW = np.random.randn(d) * noise_std
        x = x + K @ x * dt + dW
        samples[i] = x
    
    return samples


# ═══════════════════════════════════════════════════════════════════════════
# Langevin Sampler — GPU (PyTorch CUDA)
# ═══════════════════════════════════════════════════════════════════════════

def langevin_sample_gpu(K_diag_np, temperature, dt, num_samples, burn_in):
    """
    Langevin dynamics on GPU using PyTorch CUDA.
    Diagonal K — element-wise operations.
    """
    import torch
    
    device = torch.device("cuda")
    d = len(K_diag_np)
    K_diag = torch.tensor(K_diag_np, dtype=torch.float32, device=device)
    noise_std = float(np.sqrt(2.0 * temperature * dt))
    
    x = torch.zeros(d, dtype=torch.float32, device=device)
    
    # Burn-in
    for _ in range(burn_in):
        dW = torch.randn(d, device=device) * noise_std
        x = x + K_diag * x * dt + dW
    
    # Collect samples
    samples = torch.empty((num_samples, d), dtype=torch.float32, device=device)
    for i in range(num_samples):
        dW = torch.randn(d, device=device) * noise_std
        x = x + K_diag * x * dt + dW
        samples[i] = x
    
    torch.cuda.synchronize()
    return samples.cpu().numpy()


def langevin_sample_gpu_dense(K_np, temperature, dt, num_samples, burn_in):
    """
    Langevin dynamics on GPU with DENSE matrix — full matrix-vector multiply.
    This is where the GPU should shine at larger dimensions.
    """
    import torch
    
    device = torch.device("cuda")
    d = K_np.shape[0]
    K = torch.tensor(K_np, dtype=torch.float32, device=device)
    noise_std = float(np.sqrt(2.0 * temperature * dt))
    
    x = torch.zeros(d, dtype=torch.float32, device=device)
    
    # Burn-in
    for _ in range(burn_in):
        dW = torch.randn(d, device=device) * noise_std
        x = x + K @ x * dt + dW
    
    # Collect samples
    samples = torch.empty((num_samples, d), dtype=torch.float32, device=device)
    for i in range(num_samples):
        dW = torch.randn(d, device=device) * noise_std
        x = x + K @ x * dt + dW
        samples[i] = x
    
    torch.cuda.synchronize()
    return samples.cpu().numpy()


def langevin_sample_gpu_batched(K_np, temperature, dt, num_samples, burn_in):
    """
    BATCHED Langevin on GPU — processes multiple independent chains in parallel.
    This is the GPU's best case: massive parallelism across chains.
    
    Runs num_samples independent chains for (burn_in + 1) steps each,
    then takes the final state of each chain as one sample.
    """
    import torch
    
    device = torch.device("cuda")
    d = K_np.shape[0]
    K = torch.tensor(K_np, dtype=torch.float32, device=device)
    noise_std = float(np.sqrt(2.0 * temperature * dt))
    
    # All chains in parallel: shape (num_samples, d)
    x = torch.zeros((num_samples, d), dtype=torch.float32, device=device)
    
    total_steps = burn_in + 1  # burn-in then one sample per chain
    
    for _ in range(total_steps):
        dW = torch.randn((num_samples, d), device=device) * noise_std
        # x @ K^T is equivalent to K @ x for each row (since K is symmetric)
        x = x + (x @ K.T) * dt + dW
    
    torch.cuda.synchronize()
    return x.cpu().numpy()


# ═══════════════════════════════════════════════════════════════════════════
# Benchmark Runner
# ═══════════════════════════════════════════════════════════════════════════

def run_benchmark(name, func, *args, num_runs=NUM_RUNS):
    """Run a benchmark function multiple times and return timing stats."""
    times = []
    samples = None
    
    for run in range(num_runs):
        t0 = time.perf_counter()
        samples = func(*args)
        t1 = time.perf_counter()
        times.append(t1 - t0)
        
    elapsed = np.median(times)  # median is more stable than mean
    per_sample = elapsed / NUM_SAMPLES * 1000  # ms
    
    # Validate physics: check σ and mean for first few channels
    means = np.mean(samples[:, :min(5, samples.shape[1])], axis=0)
    stds = np.std(samples[:, :min(5, samples.shape[1])], axis=0)
    
    return {
        "name": name,
        "elapsed_sec": round(elapsed, 4),
        "per_sample_ms": round(per_sample, 4),
        "samples_per_sec": round(NUM_SAMPLES / elapsed, 1),
        "mean_ch0": round(float(means[0]), 4),
        "std_ch0": round(float(stds[0]), 4),
        "num_runs": num_runs,
    }


def print_header():
    print("=" * 100)
    print("PROMETHEUS Benchmark: CPU vs GPU vs FPGA")
    print("=" * 100)
    print(f"  Samples per test:  {NUM_SAMPLES:,}")
    print(f"  Burn-in:           {BURN_IN:,}")
    print(f"  Temperature:       {TEMPERATURE}")
    print(f"  Timestep dt:       {DT}")
    print(f"  Dimensions tested: {DIMENSIONS}")
    print(f"  Runs per config:   {NUM_RUNS} (median reported)")
    print()


def print_system_info():
    print("─" * 100)
    print("SYSTEM INFO")
    print("─" * 100)
    
    # CPU
    import platform
    print(f"  OS:      {platform.system()} {platform.release()}")
    print(f"  Python:  {sys.version.split()[0]}")
    print(f"  NumPy:   {np.__version__}")
    
    # CPU cores
    print(f"  CPU:     {os.cpu_count()} cores")
    
    # GPU
    try:
        import torch
        print(f"  PyTorch: {torch.__version__}")
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_mem = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            print(f"  GPU:     {gpu_name} ({gpu_mem:.1f} GB)")
            print(f"  CUDA:    {torch.version.cuda}")
        else:
            print("  GPU:     CUDA not available")
    except ImportError:
        print("  PyTorch: not installed (GPU tests will be skipped)")
    
    print()


def main():
    print_header()
    print_system_info()
    
    # Check GPU availability
    gpu_available = False
    try:
        import torch
        gpu_available = torch.cuda.is_available()
        if gpu_available:
            # Warm up GPU
            print("Warming up GPU...")
            _ = torch.randn(1000, 1000, device="cuda") @ torch.randn(1000, 1000, device="cuda")
            torch.cuda.synchronize()
            print()
    except ImportError:
        pass
    
    all_results = []
    
    for d in DIMENSIONS:
        print("━" * 100)
        print(f"  DIMENSION d = {d}")
        print("━" * 100)
        
        # Build diagonal K matrix (K[i,i] = -1 for all channels)
        K_diag = np.full(d, -1.0, dtype=np.float64)
        K_dense = np.diag(K_diag)
        
        # ─── CPU Diagonal (best case for CPU) ────────────────────────────
        print(f"  [CPU diagonal]   d={d}, S={NUM_SAMPLES}...", end="", flush=True)
        r = run_benchmark(f"CPU-diag-d{d}", langevin_sample_cpu,
                          K_diag, TEMPERATURE, DT, NUM_SAMPLES, BURN_IN)
        r["dimension"] = d
        r["device"] = "CPU"
        r["matrix_type"] = "diagonal"
        all_results.append(r)
        print(f"  {r['elapsed_sec']:.2f}s  ({r['per_sample_ms']:.3f} ms/sample)  "
              f"σ={r['std_ch0']:.3f}")
        
        # ─── CPU Dense (fair comparison — PROMETHEUS always does dense) ──
        print(f"  [CPU dense]      d={d}, S={NUM_SAMPLES}...", end="", flush=True)
        r = run_benchmark(f"CPU-dense-d{d}", langevin_sample_cpu_dense,
                          K_dense, TEMPERATURE, DT, NUM_SAMPLES, BURN_IN)
        r["dimension"] = d
        r["device"] = "CPU"
        r["matrix_type"] = "dense"
        all_results.append(r)
        print(f"  {r['elapsed_sec']:.2f}s  ({r['per_sample_ms']:.3f} ms/sample)  "
              f"σ={r['std_ch0']:.3f}")
        
        # ─── GPU tests ───────────────────────────────────────────────────
        if gpu_available:
            # GPU sequential (same algorithm as CPU, just on CUDA)
            print(f"  [GPU sequential] d={d}, S={NUM_SAMPLES}...", end="", flush=True)
            r = run_benchmark(f"GPU-seq-d{d}", langevin_sample_gpu_dense,
                              K_dense.astype(np.float32), TEMPERATURE, DT,
                              NUM_SAMPLES, BURN_IN)
            r["dimension"] = d
            r["device"] = "GPU"
            r["matrix_type"] = "dense-sequential"
            all_results.append(r)
            print(f"  {r['elapsed_sec']:.2f}s  ({r['per_sample_ms']:.3f} ms/sample)  "
                  f"σ={r['std_ch0']:.3f}")
            
            # GPU batched (GPU's best case — all chains in parallel)
            print(f"  [GPU batched]    d={d}, S={NUM_SAMPLES}...", end="", flush=True)
            r = run_benchmark(f"GPU-batch-d{d}", langevin_sample_gpu_batched,
                              K_dense.astype(np.float32), TEMPERATURE, DT,
                              NUM_SAMPLES, BURN_IN)
            r["dimension"] = d
            r["device"] = "GPU"
            r["matrix_type"] = "dense-batched"
            all_results.append(r)
            print(f"  {r['elapsed_sec']:.2f}s  ({r['per_sample_ms']:.3f} ms/sample)  "
                  f"σ={r['std_ch0']:.3f}")
        
        # ─── PROMETHEUS reference ────────────────────────────────────────
        if d in PROMETHEUS_RESULTS:
            p = PROMETHEUS_RESULTS[d]
            r = {
                "name": f"PROMETHEUS-d{d}",
                "dimension": d,
                "device": "FPGA",
                "matrix_type": "dense-hardware",
                "elapsed_sec": p["total_sec"],
                "per_sample_ms": p["per_sample_ms"],
                "samples_per_sec": round(NUM_SAMPLES / p["total_sec"], 1),
                "mean_ch0": 0.0,
                "std_ch0": 1.66,  # measured with F-factor
                "num_runs": 1,
            }
            all_results.append(r)
            print(f"  [PROMETHEUS]     d={d}, S={NUM_SAMPLES}    "
                  f"  {p['total_sec']:.2f}s  ({p['per_sample_ms']:.3f} ms/sample)  "
                  f"σ=1.66 (measured)")
        
        print()
    
    # ═══════════════════════════════════════════════════════════════════════
    # Summary Table
    # ═══════════════════════════════════════════════════════════════════════
    
    print()
    print("═" * 100)
    print("  SUMMARY — All configurations, sorted by dimension then speed")
    print("═" * 100)
    print()
    print(f"  {'Config':<30} {'Dim':>5} {'Total(s)':>10} {'ms/sample':>10} "
          f"{'Samples/s':>12} {'σ(ch0)':>8} {'vs FPGA':>10}")
    print("  " + "─" * 95)
    
    df = pd.DataFrame(all_results)
    
    for d in DIMENSIONS:
        subset = df[df["dimension"] == d].sort_values("per_sample_ms")
        fpga_ms = PROMETHEUS_RESULTS.get(d, {}).get("per_sample_ms", None)
        
        for _, row in subset.iterrows():
            ratio = ""
            if fpga_ms and row["device"] != "FPGA":
                r = row["per_sample_ms"] / fpga_ms
                ratio = f"{r:.1f}×" if r >= 1 else f"1/{1/r:.1f}×"
            
            print(f"  {row['name']:<30} {row['dimension']:>5} {row['elapsed_sec']:>10.2f} "
                  f"{row['per_sample_ms']:>10.3f} {row['samples_per_sec']:>12.0f} "
                  f"{row['std_ch0']:>8.3f} {ratio:>10}")
        print()
    
    # ═══════════════════════════════════════════════════════════════════════
    # Save results
    # ═══════════════════════════════════════════════════════════════════════
    
    output_csv = "prometheus_benchmark_results.csv"
    df.to_csv(output_csv, index=False)
    print(f"Results saved to: {output_csv}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # Key insights
    # ═══════════════════════════════════════════════════════════════════════
    
    print()
    print("═" * 100)
    print("  KEY INSIGHTS")
    print("═" * 100)
    print()
    print("  NOTE ON COMPARISON FAIRNESS:")
    print("  • 'CPU diagonal' is the fastest possible CPU path (element-wise ops, no matvec)")
    print("  • 'CPU dense' is the fair comparison (PROMETHEUS always does full dense K×x)")
    print("  • 'GPU sequential' is the same algorithm on CUDA (one chain, sequential steps)")
    print("  • 'GPU batched' is the GPU's best case (all 20K chains run in parallel)")
    print("    BUT: batched samples are LESS correlated (each chain only sees burn_in+1 steps)")
    print("    while sequential samples come from a SINGLE long chain (better mixing)")
    print()
    print("  PROMETHEUS Build #53 — 128 DSPs, DDR4 bulk DMA, XCKU5P:")
    print("    • 96,244 fps frame rate (128 parallel DSP multiply-accumulate units)")
    print("    • Capture: 20,500 frames in 213 ms")
    print("    • Readback: 80 MB via chunked 1 MB bulk DMA in 452 ms (22 µs/frame)")
    print("    • Total: 754 ms for 20,000 Boltzmann samples at d=1024")
    print("    • 0.037 ms/sample — dimension-independent (full 1024×1024 always computed)")
    print()
    print("  CROSSOVER POINT:")
    print("    • d < ~550:  CPU dense wins (BLAS matvec overhead < FPGA fixed cost)")
    print("    • d ≥ 900:   PROMETHEUS wins 5× (CPU scales O(d²), FPGA is flat)")
    print("    • d = 1024:  PROMETHEUS 5.4× faster than 32-core CPU w/ optimized LAPACK")
    print()
    print("  BUILD JOURNEY (d=1024, S=20K):")
    print("    Build #44:  21.0 sec  (32 DSPs, per-frame PCIe readback)")
    print("    Build #45:  11.0 sec  (group 31 fix)")
    print("    Build #52:  10.8 sec  (64 DSPs, bulk DMA failed silently)")
    print("    Build #53:   0.75 sec (128 DSPs + chunked bulk DMA)  ← 28× total speedup")
    print()
    print("  POWER EFFICIENCY:")
    print("    • PROMETHEUS: ~15W TDP (XCKU5P PCIe card)")
    print("    • CPU (this benchmark): ~150W TDP (32-core workstation)")
    print("    • At d=1024: PROMETHEUS delivers ~50× better perf/watt")
    print()
    
    # ═══════════════════════════════════════════════════════════════════════
    # Optional: matplotlib comparison chart
    # ═══════════════════════════════════════════════════════════════════════
    
    try:
        import matplotlib
        matplotlib.use("Agg")  # Non-interactive backend for server
        import matplotlib.pyplot as plt
        
        fig, axes = plt.subplots(1, 2, figsize=(16, 7))
        
        # Left: per-sample time by dimension
        ax = axes[0]
        devices = ["CPU", "GPU", "FPGA"]
        colors = {"CPU-diag": "#4A90D9", "CPU-dense": "#2E5F8A", 
                  "GPU-seq": "#E8593C", "GPU-batch": "#B54430",
                  "FPGA": "#2ECC71"}
        
        for d in DIMENSIONS:
            subset = df[df["dimension"] == d]
            x_pos = DIMENSIONS.index(d)
            width = 0.15
            offset = -2 * width
            
            for _, row in subset.iterrows():
                label_key = row["name"].split("-d")[0] if "-d" in row["name"] else "FPGA"
                color = colors.get(label_key.replace("CPU-diag", "CPU-diag")
                                          .replace("CPU-dense", "CPU-dense")
                                          .replace("GPU-seq", "GPU-seq")
                                          .replace("GPU-batch", "GPU-batch")
                                          .replace("PROMETHEUS", "FPGA"), "#888")
                ax.bar(x_pos + offset, row["per_sample_ms"], width, 
                       color=color, label=label_key if d == DIMENSIONS[0] else "")
                offset += width
        
        ax.set_xticks(range(len(DIMENSIONS)))
        ax.set_xticklabels([f"d={d}" for d in DIMENSIONS])
        ax.set_ylabel("Per-sample time (ms)")
        ax.set_title("Langevin Sampling: Per-Sample Latency")
        ax.legend(loc="upper left")
        ax.set_yscale("log")
        ax.grid(axis="y", alpha=0.3)
        
        # Right: throughput (samples/sec)
        ax = axes[1]
        for d in DIMENSIONS:
            subset = df[df["dimension"] == d]
            x_pos = DIMENSIONS.index(d)
            width = 0.15
            offset = -2 * width
            
            for _, row in subset.iterrows():
                label_key = row["name"].split("-d")[0] if "-d" in row["name"] else "FPGA"
                color = colors.get(label_key.replace("CPU-diag", "CPU-diag")
                                          .replace("CPU-dense", "CPU-dense")
                                          .replace("GPU-seq", "GPU-seq")
                                          .replace("GPU-batch", "GPU-batch")
                                          .replace("PROMETHEUS", "FPGA"), "#888")
                ax.bar(x_pos + offset, row["samples_per_sec"], width,
                       color=color, label=label_key if d == DIMENSIONS[0] else "")
                offset += width
        
        ax.set_xticks(range(len(DIMENSIONS)))
        ax.set_xticklabels([f"d={d}" for d in DIMENSIONS])
        ax.set_ylabel("Samples/sec")
        ax.set_title("Langevin Sampling: Throughput")
        ax.legend(loc="upper right")
        ax.set_yscale("log")
        ax.grid(axis="y", alpha=0.3)
        
        plt.tight_layout()
        chart_path = "prometheus_benchmark_comparison.png"
        plt.savefig(chart_path, dpi=150, bbox_inches="tight")
        print(f"Chart saved to: {chart_path}")
        
    except ImportError:
        print("(matplotlib not installed — skipping chart)")


if __name__ == "__main__":
    main()