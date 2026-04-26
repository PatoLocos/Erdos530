# Erdos Problem 530: Sidon Subset Formalization

A Lean 4 workspace for formalizing results around [Erdos Problem 530](https://www.erdosproblems.com/530).

The official problem defines `ell(N)` as the largest integer `m` such that every `N`-element finite subset of `R` contains a Sidon subset of size at least `m`. The known classical order is `ell(N) = Theta(sqrt N)`; the open question emphasized on the problem page is the sharper asymptotic `ell(N) ~ sqrt N`.

## Verified Core

[KSS_Proven.lean](KSS_Proven.lean) is the checked axiom-free core of this repo. It proves the following natural-number partial result:

```lean
∀ A : Finset Nat, A.card ≥ 1 →
  ∃ B : Finset Nat, B ⊆ A ∧ B.IsSidon ∧ A.card ≤ 3 * B.card ^ 3
```

In mathematical notation: every finite `A subset Nat` has a Sidon subset `B` with `|A| <= 3|B|^3`, hence `|B| = Omega(|A|^(1/3))`.

MCP Lean verification reports:

```text
KSS_Proven.lean: SUCCESS
All proofs complete - no sorries
Axiom audit: propext, Classical.choice, Quot.sound only
```

These are standard Lean/Mathlib foundations, not custom mathematical axioms.

## Repository Files

| File | Role | Status |
|---|---|---|
| [530.lean](530.lean) | Official statement layer for `ell(N)` over finite subsets of `R` | Mathlib-checkable definitions, no proof of open conjecture |
| [KSS_Proven.lean](KSS_Proven.lean) | Axiom-free cube-root lower bound over `Nat` | Fully checked, no sorries |
| [SidonExploration.lean](SidonExploration.lean) | Explains the maximal-blocking `N^(1/3)` barrier | Exploratory; uses a bridge axiom documented as proven in [KSS_Proven.lean](KSS_Proven.lean) |
| [SingerExtraction.lean](SingerExtraction.lean) | Conditional Singer-partition model for dense initial segments | Exploratory; uses explicit axioms and is not the KSS arbitrary-set theorem |

## What Is Not Proved Here

This repo does not yet formalize the classical KSS square-root lower bound for arbitrary finite sets, and it does not prove the open exact asymptotic `ell(N) ~ sqrt N`.

A previous approach tried to axiomatize a universal quadratic blocking claim of the form `|A \ S| <= O(|S|^2)` for arbitrary maximal Sidon `S subset A`. That shortcut is false in full generality, even though the KSS theorem itself is correct. The checked proof in [KSS_Proven.lean](KSS_Proven.lean) avoids that false claim and keeps the weaker cubic Type 1 bound.

The ChatGPT shared-link proof about primitive sets and sums of `1 / (a log a)` concerns a different Erdos-style problem. It uses divisibility-poset structure and does not directly address Problem 530, which is additive and Sidon-based.

## Building

From an environment with Lean 4 and Mathlib available:

```powershell
lake env lean KSS_Proven.lean
```

The MCP Lean checker has also been used directly on the core file.

## References

- [Erdos Problem 530](https://www.erdosproblems.com/530)
- Komlos, Sulyok, Szemeredi. "Linear problems in combinatorial number theory." Acta Math. Acad. Sci. Hung. 26 (1975), 113-121.
