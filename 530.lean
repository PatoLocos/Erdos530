/-
Copyright 2026 Norway Analytics
SPDX-License-Identifier: Apache-2.0

Formalization of Erdős Problem 530: Sidon set bounds ℓ(N).
-/

import FormalConjectures.Util.ProblemImports

/-!
# Erdős Problem 530: Sidon Sets and ℓ(N) = Θ(√N)

## Problem Statement

For N ∈ ℕ, let ℓ(N) denote the minimum size of a maximal Sidon subset of {1, ..., N}.
Show that ℓ(N) = Θ(√N).

## Background

A Sidon set (or B₂-sequence) is a set where all pairwise sums are distinct.
Equivalently, if a + b = c + d for elements of the set, then {a, b} = {c, d}.

The upper bound ℓ(N) ≤ (1 + o(1))√N is trivial: any Sidon subset of {1,...,N}
has at most ~√2N elements (since sums range to 2N and are distinct).

The lower bound ℓ(N) ≥ (1/2)√N was proven by Komlós, Sulyok, and Szemerédi (1975)
using a charging argument that shows blocking in maximal Sidon sets is limited.

## References

* <https://www.erdosproblems.com/530>
* Komlós, Sulyok, Szemerédi. "Linear problems in combinatorial number theory."
  Acta Math. Acad. Sci. Hung. 26 (1975), 113-121.
* Ruzsa, I. Z. "Solving a linear equation in a set of integers I."
  Acta Arith. 65 (1993), 259-282.
-/

namespace Erdos530

/-! ## Definitions -/

/--
A finite set S of natural numbers is Sidon if all pairwise sums are distinct:
a + b = c + d with a,b,c,d ∈ S implies {a, b} = {c, d} as sets.
-/
def Finset.IsSidon (S : Finset ℕ) : Prop :=
  ∀ a b c d : ℕ, a ∈ S → b ∈ S → c ∈ S → d ∈ S →
    a + b = c + d → ({a, b} : Set ℕ) = {c, d}

/--
A Sidon set S is maximal in A if:
1. S ⊆ A
2. S is Sidon
3. No larger Sidon subset of A contains S
-/
def Finset.IsMaximalSidon (S A : Finset ℕ) : Prop :=
  S ⊆ A ∧ S.IsSidon ∧ ∀ x ∈ A, x ∉ S → ¬(insert x S).IsSidon

/--
ℓ(N) is the minimum cardinality of a maximal Sidon subset of {1, ..., N}.
-/
noncomputable def ell (N : ℕ) : ℕ :=
  Finset.Icc 1 N |>.powerset.filter (fun S =>
    S.IsMaximalSidon (Finset.Icc 1 N)) |>.image (fun S => S.card) |>.min' (by
      -- The empty set is never maximal (can always add an element if N ≥ 1)
      -- For N = 0, Icc 1 0 = ∅ and the powerset/filter is tricky
      -- We show there's always at least one maximal Sidon set
      sorry)

/-! ## The Main Conjecture -/

/--
**Erdős Problem 530: ℓ(N) = Θ(√N)**

The exact statement: there exist constants c₁, c₂ > 0 such that for all
sufficiently large N:
    c₁ √N ≤ ℓ(N) ≤ c₂ √N

*Status*: The lower bound ℓ(N) ≥ (1/2)√N was proven by KSS (1975).
The upper bound ℓ(N) ≤ (1+o(1))√N is trivial. The exact asymptotics
(whether ℓ(N)/√N converges, and to what value) remain open.
-/
@[category research open, AMS 5 11]
theorem erdos530_sidon_bound : ∃ c₁ c₂ : ℝ, c₁ > 0 ∧ c₂ > 0 ∧
    ∀ᶠ N in Filter.atTop, c₁ * Real.sqrt N ≤ ell N ∧ (ell N : ℝ) ≤ c₂ * Real.sqrt N :=
  answer(sorry)

/-! ## Partial Results -/

/--
**KSS Lower Bound (1975)**

For any finite A ⊆ ℕ, there exists a Sidon subset B ⊆ A with |B| ≥ (1/2)√|A|.

This implies ℓ(N) ≥ (1/2)√N (take A = {1,...,N}).

*Note*: The original KSS charging argument (2-to-1 map from A\S to S×S) was found
to be FALSE under universal quantification over A. A weaker cube root bound
(|A| ≤ 3|B|³) is fully proven axiom-free in `KSS_Proven.lean`.
-/
@[category research solved, AMS 5 11]
theorem kss_lower_bound (A : Finset ℕ) (hA : A.card ≥ 1) :
    ∃ B : Finset ℕ, B ⊆ A ∧ B.IsSidon ∧ (B.card : ℝ) ≥ (1/2) * Real.sqrt A.card := by
  sorry -- Full √N bound requires different technique; cube root bound proven in KSS_Proven.lean

/--
**Trivial Upper Bound**

Any maximal Sidon subset of {1,...,N} has at most ~(1+o(1))√(2N) elements.

Proof: A Sidon set S has |S|(|S|+1)/2 distinct pairwise sums.
If S ⊆ {1,...,N}, these sums lie in {2,...,2N}, giving |S|² ≲ 4N.
-/
@[category research solved, AMS 5 11]
theorem sidon_upper_bound (N : ℕ) (S : Finset ℕ) (hS : S ⊆ Finset.Icc 1 N) 
    (hSidon : S.IsSidon) :
    (S.card : ℝ) ≤ Real.sqrt (2 * N) + 1 := by
  sorry

/-! ## Proven Partial Result: Cube Root Bound

The following weaker bound IS fully proven (axiom-free) in `KSS_Proven.lean`.
It uses a direct blocking count argument: each blocked element in A \ S
corresponds to a collision that can be traced to at most |S|² + |S|³ cases.
-/

/--
**Cube Root Bound (Proven)**

For any finite A ⊆ ℕ with |A| ≥ 1, there exists a Sidon subset B ⊆ A
with |A| ≤ 3|B|³.

This gives ℓ(N) ≥ Ω(N^{1/3}), weaker than the conjectured Ω(√N) but
fully formalized with no custom axioms.

Full proof: `KSS_Proven.lean` → `erdos_cube_root_bound`
-/
@[category research solved, AMS 5 11]
theorem cube_root_lower_bound (A : Finset ℕ) (hA : A.card ≥ 1) :
    ∃ B : Finset ℕ, B ⊆ A ∧ B.IsSidon ∧ A.card ≤ 3 * B.card ^ 3 := by
  sorry -- Full axiom-free proof in KSS_Proven.lean (erdos_cube_root_bound)

/-!
## Axiom Status

All results in `KSS_Proven.lean` depend only on standard Lean axioms:
- `propext` — Propositional extensionality
- `Classical.choice` — Classical choice
- `Quot.sound` — Quotient soundness

**No custom axioms.** A previous axiom (`kss_two_to_one_map_exists`) positing
a 2-to-1 charging map from A \ S to S × S was removed after computational
verification showed it is FALSE for general A ⊆ ℕ (counterexample: spread-out
Sidon sets where |A \ S| grows as Θ(|S|³) > 2|S|²).

The full √N lower bound requires a different formalization strategy.
-/

end Erdos530
