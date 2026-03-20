# Komlós–Sulyok–Szemerédi 1975: Linear Problems in Combinatorial Number Theory

## Bibliographic Information

- **Authors**: János Komlós, Miklós Sulyok, Endre Szemerédi
- **Title**: "Linear problems in combinatorial number theory"
- **Journal**: Acta Mathematica Academiae Scientiarum Hungaricae
- **Volume**: 26
- **Pages**: 113–121
- **Year**: 1975
- **DOI**: [10.1007/BF01895954](https://doi.org/10.1007/BF01895954)
- **zbMATH**: [Zbl 0303.10058](https://zbmath.org/0303.10058)
- **MathSciNet**: MR0369312 (51 #5547)

## Main Result: The √N Lower Bound for Sidon Sets

### Definitions

A **B₂-sequence** (Sidon set) is a sequence $a_1 < a_2 < \cdots < a_k$ such that all pairwise sums $a_i + a_j$ (with $i \leq j$) are distinct.

Let $F_2(N)$ denote the maximum size of a Sidon set contained in $\{1, 2, \ldots, N\}$.

### The KSS Lower Bound Theorem

**Theorem (KSS 1975)**: There exists a constant $c > 0$ such that
$$F_2(N) \geq c\sqrt{N}$$

Combined with the classical Erdős–Turán upper bound $F_2(N) \leq \sqrt{N} + O(N^{1/4})$, this gives:
$$F_2(N) = \Theta(\sqrt{N})$$

### Historical Context

| Bound | Result | Authors | Year |
|-------|--------|---------|------|
| Upper | $F_2(N) \leq \sqrt{N} + N^{1/4} + 1$ | Erdős–Turán | 1941 |
| Upper | $F_2(N) \leq \sqrt{N} + N^{1/4} + 1$ | Lindström | 1969 |
| Upper | $F_2(N) \leq \sqrt{N} + 0.998N^{1/4}$ | Balogh–Füredi–Roy | 2023 |
| Lower | $F_2(N) \geq (1-o(1))\sqrt{N}$ | Singer, Bose | 1938–1942 |
| **Lower** | **$F_2(N) \geq c\sqrt{N}$ (any maximal Sidon set)** | **KSS** | **1975** |

### The KSS Proof Approach

The key insight of KSS is that **any maximal Sidon set** has size at least $c\sqrt{N}$. This is much stronger than explicit constructions because it shows the lower bound holds for the greedy algorithm as well.

#### Key Idea: Maximal Sets Are Large

If $S \subseteq \{1, \ldots, N\}$ is a **maximal** Sidon set (meaning no element of $\{1, \ldots, N\} \setminus S$ can be added while preserving the Sidon property), then $|S| \geq c\sqrt{N}$.

#### Proof Sketch (from zbMATH review)

The paper addresses "linear problems in combinatorial number theory" where the goal is to estimate the density of sequences where certain linear relations do not hold for subsets.

For Sidon sets, the restriction is: $a_i + a_j = a_k + a_\ell$ implies $\{a_i, a_j\} = \{a_k, a_\ell\}$.

The KSS argument shows that the case $\{1, 2, \ldots, N\}$ is "the worst case" - meaning if you pick integers from *any* set, the resulting density cannot be worse than picking from consecutive integers.

**Key technical lemmas involve:**
1. **Counting collisions**: Bounding the number of "bad" quadruples $(a, b, c, d)$ where $a + b = c + d$
2. **Graph-theoretic arguments**: Constructing a "collision graph" where edges represent potential conflicts
3. **Degree bounds**: If a set $S$ has size $|S| = k$, and is maximal, then each element of $\{1, \ldots, N\} \setminus S$ must create a collision with some pair in $S$

## Connection to Erdős Problem 530

**Erdős Problem 530** asks to determine $\ell(N)$, the maximum size of a Sidon subset of $\{1, \ldots, N\}$.

The KSS 1975 result, combined with earlier upper bounds, **completely resolves** this problem by establishing:
$$\ell(N) = \Theta(\sqrt{N})$$

### Status of Erdős Problem 530

| Component | Status | Reference |
|-----------|--------|-----------|
| Upper bound: $\ell(N) \leq \sqrt{2N} + O(1)$ | ✅ Proved | Erdős–Turán 1941, Lindström 1969 |
| Lower bound: $\ell(N) \geq c\sqrt{N}$ | ✅ Proved | KSS 1975 |
| **Conclusion: $\ell(N) = \Theta(\sqrt{N})$** | ✅ **SOLVED** | Combined |

## References from the KSS Paper

1. H. Halberstam and K.F. Roth, *Sequences*, Vol. I (Oxford, Clarendon Press, 1966)
2. K.F. Roth, "On certain sets of integers, II", *J. London Math. Soc.* 29 (1954), 20–26
3. F.A. Behrend, "On sets of integers which contain no three terms in arithmetical progression", *Proc. Nat. Acad. Sci. USA* 28 (1942), 561–563
4. E. Szemerédi, "On sets of integers containing no four elements in arithmetic progression", *Acta Math. Acad. Sci. Hungar.* 20 (1969), 89–104
5. E. Szemerédi, "On sets of integers containing no k elements in arithmetic progression", *Acta Arithmetica* (to appear)
6. J. Komlós, M. Sulyok, E. Szemerédi, "A lemma of combinatorial number theory", *Matematikai Lapok* (to appear) — zbMATH: Zbl 0288.10019

## Related Works

- **O'Bryant (2004)**: "A Complete Annotated Bibliography of Work Related to Sidon Sequences" — *Electronic Journal of Combinatorics*, DS11 — [DOI: 10.37236/32](https://doi.org/10.37236/32)

- **Wikipedia**: [Sidon sequence](https://en.wikipedia.org/wiki/Sidon_sequence)

## For Lean Formalization

The key lemma to formalize is:

```
theorem kss_sqrt_bound (N : ℕ) (hN : N ≥ 2) (S : Finset ℕ) 
    (hS : ∀ x ∈ S, x ∈ Finset.range (N + 1))
    (hSidon : S.IsSidon)
    (hMaximal : ∀ x ∈ Finset.range (N + 1), x ∉ S → 
                ¬(insert x S).IsSidon) :
    ∃ (c : ℝ), c > 0 ∧ (S.card : ℝ) ≥ c * Real.sqrt N
```

The proof requires showing that if $S$ is maximal and $|S| = k$, then each of the $N - k$ elements outside $S$ is "blocked" by some collision. Each collision involves at most $O(k)$ elements, leading to $N - k \leq O(k^2)$, which gives $k = \Omega(\sqrt{N})$.
