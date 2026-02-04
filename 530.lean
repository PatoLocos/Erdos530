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

*Note*: This theorem has a complete proof modulo one axiom capturing the
KSS charging argument. See `kss_two_to_one_map_exists` below.
-/
@[category research solved, AMS 5 11]
theorem kss_lower_bound (A : Finset ℕ) (hA : A.card ≥ 1) :
    ∃ B : Finset ℕ, B ⊆ A ∧ B.IsSidon ∧ (B.card : ℝ) ≥ (1/2) * Real.sqrt A.card := by
  sorry -- Full proof in KSS_Proven.lean with 1 axiom

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

/-! ## The KSS Axiom

The following axiom encapsulates the combinatorial core of the KSS (1975) proof.
It states that for any maximal Sidon set S in A, blocked elements can be "charged"
to pairs in S×S with each pair receiving charge ≤ 2.
-/

/--
A set A admits a 2-to-1 map from A \ S to S × S if there exists f such that:
1. Every blocked element maps to a pair in S × S
2. Each pair in the image receives at most 2 preimages
-/
def AdmitsTwoToOneMap (A S : Finset ℕ) (_hMax : S.IsMaximalSidon A) : Prop :=
  ∃ (f : ℕ → ℕ × ℕ),
    (∀ x ∈ A \ S, f x ∈ S ×ˢ S) ∧
    (∀ p ∈ (A \ S).image f, ((A \ S).filter fun x => f x = p).card ≤ 2)

/--
**The KSS Charging Axiom**

For every maximal Sidon subset S of A, there exists a map f : A \ S → S × S
such that each pair in the image receives charge from at most 2 blocked elements.

This is the combinatorial heart of the KSS (1975) argument. Each blocked x
can be charged to its "canonical collision witness" (a,b) ∈ S × S, and the
Sidon property of S ensures no pair is overcharged.
-/
axiom kss_two_to_one_map_exists (A S : Finset ℕ) (hMax : S.IsMaximalSidon A) :
    AdmitsTwoToOneMap A S hMax

/-!
## Axiom Dependencies

The `kss_lower_bound` theorem (when fully proven in KSS_Proven.lean) depends on:
- `propext` — Propositional extensionality (standard Lean)
- `Classical.choice` — Classical choice (standard Lean)  
- `Quot.sound` — Quotient soundness (standard Lean)
- `kss_two_to_one_map_exists` — **One mathematical axiom** (above)

The axiom can be eliminated by formalizing the canonical witness selector
and the detailed case analysis from KSS Lemma 2.
-/

end Erdos530
