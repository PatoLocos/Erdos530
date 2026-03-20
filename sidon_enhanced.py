"""
Enhanced Sidon subset extraction: hybrid K^{-1}-diag + local search.
Targets the gap between our algorithmic output and the theoretical √N bound.
"""
import numpy as np
import time
from itertools import combinations

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

def verify_sidon(S):
    S = sorted(S)
    sums = set()
    for i in range(len(S)):
        for j in range(i+1, len(S)):
            s = S[i] + S[j]
            if s in sums:
                return False
            sums.add(s)
    return True

def greedy_from_ranking(ranking, N):
    """Greedy Sidon extraction following a given element ranking."""
    S = []; sums = set()
    for x in ranking:
        new_sums = set()
        ok = True
        for s in S:
            ps = x + s
            if ps in sums or ps in new_sums:
                ok = False; break
            new_sums.add(ps)
        if ok:
            S.append(x); sums.update(new_sums)
    return sorted(S)

def greedy_sidon(N):
    return greedy_from_ranking(range(N), N)

def local_search_improve(S_init, N, max_iters=2000):
    """Try swapping elements to find larger Sidon set."""
    S = list(S_init)
    best = list(S)
    complement = [x for x in range(N) if x not in set(S)]
    
    for _ in range(max_iters):
        # Try adding a random element from complement
        np.random.shuffle(complement)
        for add_elem in complement:
            S_trial = sorted(S + [add_elem])
            if verify_sidon(S_trial):
                S = S_trial
                complement = [x for x in range(N) if x not in set(S)]
                if len(S) > len(best):
                    best = list(S)
                break
        else:
            # Can't add any element. Try swap: remove one, add two
            improved = False
            for remove_idx in range(len(S)):
                S_minus = S[:remove_idx] + S[remove_idx+1:]
                sums_minus = set()
                for i in range(len(S_minus)):
                    for j in range(i+1, len(S_minus)):
                        sums_minus.add(S_minus[i] + S_minus[j])
                
                additions = []
                for x in complement + [S[remove_idx]]:
                    if x == S[remove_idx]:
                        continue
                    new_sums = set()
                    ok = True
                    for s in S_minus:
                        ps = x + s
                        if ps in sums_minus or ps in new_sums:
                            ok = False; break
                        new_sums.add(ps)
                    if ok:
                        additions.append((x, new_sums))
                
                # Try pairs of additions
                for i in range(len(additions)):
                    x1, ns1 = additions[i]
                    test_sums = sums_minus | ns1
                    for j in range(i+1, len(additions)):
                        x2, ns2 = additions[j]
                        ps = x1 + x2
                        if ps in test_sums:
                            continue
                        ok = True
                        for s in S_minus + [x1]:
                            if x2 + s in test_sums:
                                ok = False; break
                        if ok:
                            S = sorted(S_minus + [x1, x2])
                            complement = [x for x in range(N) if x not in set(S)]
                            if len(S) > len(best):
                                best = list(S)
                            improved = True
                            break
                    if improved:
                        break
                if improved:
                    break
            if not improved:
                break
    
    return sorted(best)

def multi_start_kinv(K_inv_diag, N, epsilon_range=[0.01, 0.05, 0.1, 0.5, 1.0]):
    """Try multiple regularization strengths and keep best."""
    best = []
    for _ in range(10):
        # Add noise to break ties
        noise = np.random.randn(N) * 1e-6
        scores = -K_inv_diag + noise
        ranked = sorted(range(N), key=lambda i: scores[i], reverse=True)
        S = greedy_from_ranking(ranked, N)
        if len(S) > len(best):
            best = S
    return best

def edge_biased_kinv(K_inv_diag, collision_count, N, alpha=0.5):
    """Combine K^{-1} diagonal with edge bias (elements near 0 and N-1)."""
    edge_score = np.array([min(i, N-1-i) for i in range(N)], dtype=float)
    edge_score = 1.0 - edge_score / edge_score.max()  # 1.0 at edges, ~0 at center
    
    combined = -K_inv_diag + alpha * edge_score - 0.1 * collision_count / collision_count.max()
    ranked = sorted(range(N), key=lambda i: combined[i], reverse=True)
    return greedy_from_ranking(ranked, N)

print("ENHANCED SIDON EXTRACTION: HYBRID K^{-1} + LOCAL SEARCH")
print("=" * 75)

test_sizes = [100, 200, 300, 500, 750, 1000]

for N in test_sizes:
    t0 = time.time()
    print(f"\n{'='*60}")
    print(f"N = {N}, sqrt(N) = {np.sqrt(N):.2f}")
    print(f"{'='*60}")
    
    # Build collision structure
    W = build_collision_weight_matrix(N)
    D_diag = np.sum(W, axis=1)
    L = np.diag(D_diag) - W
    
    results = {}
    
    # Method 1: Standard greedy
    greedy = greedy_sidon(N)
    results['greedy'] = greedy
    print(f"  Greedy:          {len(greedy)}")
    
    # Method 2: Randomized greedy (200 trials)
    best_rand = []
    for _ in range(200):
        perm = np.random.permutation(N)
        S = greedy_from_ranking(perm, N)
        if len(S) > len(best_rand):
            best_rand = S
    results['rand_greedy'] = best_rand
    print(f"  RandGreedy(200): {len(best_rand)}")
    
    # Method 3+: K^{-1}-diag with different epsilon
    best_kinv = []
    best_eps = 0
    for eps in [0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0]:
        K = -(L + eps * np.eye(N))
        K_inv = np.linalg.inv(K)
        K_inv_diag = np.diag(K_inv)
        S = greedy_from_ranking(sorted(range(N), key=lambda i: K_inv_diag[i]), N)
        if len(S) > len(best_kinv):
            best_kinv = S
            best_eps = eps
    results['kinv_best'] = best_kinv
    print(f"  K_inv(eps={best_eps}):  {len(best_kinv)}")
    
    # Method 4: Edge-biased K^{-1}
    K_std = -(L + 0.1 * np.eye(N))
    K_inv_std = np.linalg.inv(K_std)
    K_inv_diag_std = np.diag(K_inv_std)
    for alpha in [0.1, 0.3, 0.5, 1.0, 2.0]:
        S = edge_biased_kinv(K_inv_diag_std, D_diag, N, alpha)
        if len(S) > len(best_kinv):
            best_kinv = S
            results['kinv_best'] = best_kinv
    print(f"  K_inv+edge:      {len(results['kinv_best'])}")
    
    # Method 5: Multi-start with noise
    S_multi = multi_start_kinv(K_inv_diag_std, N)
    results['kinv_multi'] = S_multi
    print(f"  K_inv(multi):    {len(S_multi)}")
    
    # Method 6: Spectral embedding (Fiedler + 2nd mode)
    L_evals, L_evecs = np.linalg.eigh(L)
    for n_modes in [2, 3, 5, 10, min(20, N-1)]:
        embedding = L_evecs[:, 1:n_modes+1]
        centroid = embedding.mean(axis=0)
        distances = np.linalg.norm(embedding - centroid, axis=1)
        S = greedy_from_ranking(sorted(range(N), key=lambda i: distances[i], reverse=True), N)
        if len(S) > len(results.get('embed_best', [])):
            results['embed_best'] = S
    print(f"  SpectralEmbed:   {len(results['embed_best'])}")
    
    # Local search post-processing on BEST result so far
    all_results = list(results.values())
    overall_best = max(all_results, key=len)
    
    improved = local_search_improve(overall_best, N, max_iters=500)
    results['local_search'] = improved
    print(f"  LocalSearch:     {len(improved)} (from {len(overall_best)})")
    
    # Also try local search from K_inv and greedy results
    for seed_name, seed_set in [('kinv', best_kinv), ('greedy', greedy)]:
        imp = local_search_improve(seed_set, N, max_iters=300)
        if len(imp) > len(improved):
            improved = imp
    results['best_improved'] = improved
    
    final_best = max(results.values(), key=len)
    
    elapsed = time.time() - t0
    ratio = len(final_best) / np.sqrt(N)
    above = ">=" if len(final_best) >= np.sqrt(N) else "< "
    
    print(f"\n  FINAL BEST: {len(final_best)} ({above} sqrt(N)={np.sqrt(N):.2f}, ratio={ratio:.3f}) [{elapsed:.1f}s]")
    print(f"  Set: {final_best[:15]}{'...' if len(final_best) > 15 else ''}")
    assert verify_sidon(final_best), "NOT SIDON!"
