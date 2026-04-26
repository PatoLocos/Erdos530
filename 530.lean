/-
Copyright 2026 Norway Analytics
SPDX-License-Identifier: Apache-2.0

Statement layer for Erdos Problem 530.
-/

import Mathlib.Data.Finset.Card
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Topology.Basic
import Mathlib.Order.Filter.AtTopBot.Basic
import Mathlib.Tactic

/-!
# Erdos Problem 530: Sidon Subsets

The official problem asks about finite subsets of `R`, not just intervals and
not just maximal Sidon subsets of `{1, ..., N}`.

For `N : Nat`, let `ell N` be the largest `m` such that every `N`-element
finite subset of `R` contains a Sidon subset of size at least `m`. The known
classical result is `ell N = Theta(sqrt N)` by Komlos-Sulyok-Szemeredi and the
standard interval upper bound. The open part recorded on erdosproblems.com is
the sharper asymptotic question `ell N ~ sqrt N`.

The axiom-free theorem proved in `KSS_Proven.lean` is a weaker natural-number
partial result: every finite `A : Finset Nat` has a Sidon subset `B` with
`A.card <= 3 * B.card ^ 3`, i.e. an `Omega(N^(1/3))` lower bound in that
setting. It should not be confused with either the KSS square-root theorem or
the open exact-asymptotic problem.
-/

namespace Erdos530

/-! ## Definitions -/

/-- A finite set is Sidon if pairwise sums determine the unordered pair. -/
def IsSidon {alpha : Type*} [Add alpha] (S : Finset alpha) : Prop :=
  ∀ a b c d : alpha, a ∈ S → b ∈ S → c ∈ S → d ∈ S →
    a + b = c + d → ({a, b} : Set alpha) = {c, d}

/-- The empty set is Sidon. -/
lemma empty_isSidon {alpha : Type*} [Add alpha] :
    IsSidon (∅ : Finset alpha) := by
  intro a b c d ha _ _ _ _
  simp at ha

/--
`GuaranteesSidonSubset N m` means every `N`-element finite subset of `R`
contains a Sidon subset of cardinality at least `m`.
-/
def GuaranteesSidonSubset (N m : Nat) : Prop :=
  ∀ A : Finset Real, A.card = N →
    ∃ S : Finset Real, S ⊆ A ∧ IsSidon S ∧ m ≤ S.card

/-- The guarantee with `m = 0` is always true. -/
lemma guarantees_zero (N : Nat) : GuaranteesSidonSubset N 0 := by
  intro A _
  exact ⟨∅, by simp, empty_isSidon, Nat.zero_le _⟩

/--
The official `ell(N)`: the largest guaranteed Sidon-subset size among all
`N`-element finite subsets of `R`.

The maximum is taken over `0, ..., N`; this finite set is nonempty because
`0` is always guaranteed.
-/
noncomputable def ell (N : Nat) : Nat :=
  by
  classical
  exact ((Finset.range (N + 1)).filter (fun m => GuaranteesSidonSubset N m)).max' (by
    refine ⟨0, ?_⟩
    rw [Finset.mem_filter, Finset.mem_range]
    exact ⟨Nat.zero_lt_succ N, guarantees_zero N⟩)

/-! ## Problem Statements -/

/-- The known order-of-magnitude form `ell(N) = Theta(sqrt N)`. -/
def orderOfMagnitudeStatement : Prop :=
  ∃ c1 c2 : Real, c1 > 0 ∧ c2 > 0 ∧
    Filter.Eventually (fun N : Nat =>
      c1 * Real.sqrt (N : Real) ≤ (ell N : Real) ∧
        (ell N : Real) ≤ c2 * Real.sqrt (N : Real)) Filter.atTop

/-- The open exact-asymptotic form asked on erdosproblems.com. -/
def exactAsymptoticConjecture : Prop :=
  Filter.Tendsto
    (fun N : Nat => (ell N : Real) / Real.sqrt (N : Real))
    Filter.atTop
    (nhds (1 : Real))

/-- The axiom-free cube-root theorem proved in `KSS_Proven.lean`, as a statement. -/
def cubeRootLowerBoundOverNatStatement : Prop :=
  ∀ A : Finset Nat, A.card ≥ 1 →
    ∃ B : Finset Nat, B ⊆ A ∧ IsSidon B ∧ A.card ≤ 3 * B.card ^ 3

end Erdos530
