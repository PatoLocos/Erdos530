# Line Sidon Sets (Patry & Warren, 2023)

**Source**: INTEGERS 23 (2023), Article A15
**Authors**: Miriam Patry, Audie Warren
**DOI**: 10.5281/zenodo.7625119

---

## Key Quote: The KSS Theorem (Theorem 1)

> **Theorem 1 (Komlós, Sulyok, Szemerédi).** For all finite sets $A \subseteq \mathbb{Z}$ there is a subset $B \subseteq A$ which is additive Sidon. The size of $B$ satisfies $|B| \gg |A|^{\frac{1}{2}}$.

This is the exact statement we need for our Lean formalization!

### Context from the paper:

> "Sidon sets are highly studied objects in combinatorial number theory, with much research being focused on finding the size of the largest additive Sidon subsets of $[n] := \{1, 2, \ldots, n\}$, which is known to be $\Theta(n^{1/2})$."

> "The case of the first $n$ integers turns out to be a minimizer (up to multiplicative constants) for finding large additive Sidon subsets"

### Extension mentioned:
> "Theorem 1 has since been extended to apply to sets of real numbers [5]"
> (Reference [5] = O. Raz, "A note on distinct differences", Combinator. Probab. Comp. 29 (2020), 650-663)

---

## Original Reference

**[2] J. Komlós, M. Sulyok, and E. Szemerédi**, "Linear problems in combinatorial number theory", *Acta Math. Acad. Sci. Hungar.* **26** (1975), 113-121.

---

## Notation

- $X \ll Y$ means there exists an absolute constant $c$ such that $X \leq cY$
- $Y \gg X$ means $X \ll Y$  
- $X = \Theta(Y)$ means both $X \ll Y$ and $Y \ll X$

---

## Application in this Paper

The paper uses KSS to prove that any set of $n$ lines contains a "line Sidon" subset of size $n^{1/3 + 1/24}$.

The proof reduces to the classical KSS theorem:
- For **parallel lines**: reduces to additive Sidon (apply KSS directly)
- For **concurrent lines**: reduces to multiplicative Sidon (apply KSS to $\log A$)

---

## For Lean Formalization

The KSS theorem as stated in this paper:

```lean
theorem kss_sidon_extraction (A : Finset ℤ) (hA : A.Nonempty) :
    ∃ B : Finset ℤ, B ⊆ A ∧ B.IsSidon ∧ 
    ∃ c : ℝ, c > 0 ∧ (B.card : ℝ) ≥ c * Real.sqrt A.card
```

Key insight: The theorem says **any finite set** contains a Sidon subset of size $\Omega(\sqrt{|A|})$. 

For $A = \{1, \ldots, N\}$, this gives $|B| \geq c\sqrt{N}$, which is the lower bound for Erdős Problem 530.
