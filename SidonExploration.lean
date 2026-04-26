import Mathlib.Data.Finset.Card
import Mathlib.Tactic
import Mathlib.Data.Finset.Powerset

/-!
# Sidon Set Exploration: The N^{1/3} Barrier

This file formalizes why the naive maximal-blocking argument toward Erdős
Problem 530 caps at N^{1/3}.

## Main Results

- `framework_reduction`: If |type1Only(A,S)| ≤ f(|S|), then |A| ≤ |S| + |S|² + f(|S|)
- `cube_root_from_framework`: f(k) = k³ recovers |A| ≤ 3|S|³, i.e., Ω(N^{1/3})
- `new_sums_per_step`: Adding element x to Sidon S creates ≤ |S|+1 new sums

The bridge lemma `blocked_element_form` is axiomatized here but fully
proven (axiom-free) in `KSS_Proven.lean`.

## Why N^{1/3} and Not √N?

The naive bound |type1Only| ≤ |S|³ comes from mapping each Type 1 element
to a triple in S³. This gives f(k) = k³ → N^{1/3}.

Within this framework, a hypothetical quadratic bound for `type1Only` would
already give a square-root lower bound. The actual KSS proof reaches the
square-root order by a different extraction argument, not by proving such a
bound for every arbitrary maximal Sidon subset.
- f(k) = k³  ⟹  N^{1/3}  (this file)
- f(k) = k²  ⟹  N^{1/2}  (hypothetical within this framework)
-/

/-! ## Definitions -/

def Finset.IsSidon (s : Finset ℕ) : Prop :=
  ∀ a b c d : ℕ, a ∈ s → b ∈ s → c ∈ s → d ∈ s →
    a + b = c + d → ({a, b} : Set ℕ) = {c, d}

def Finset.IsMaximalSidon (S : Finset ℕ) (A : Finset ℕ) : Prop :=
  S ⊆ A ∧ S.IsSidon ∧ ∀ x ∈ A, x ∉ S → ¬(insert x S).IsSidon

def sumset (S : Finset ℕ) : Finset ℕ :=
  (S ×ˢ S).image (fun p => p.1 + p.2)

def blockedType2 (A S : Finset ℕ) : Finset ℕ :=
  (A \ S).filter (fun x => ∃ a ∈ S, ∃ b ∈ S, 2 * x = a + b)

def isType2 (S : Finset ℕ) (x : ℕ) : Prop :=
  ∃ a ∈ S, ∃ b ∈ S, 2 * x = a + b

instance (S : Finset ℕ) (x : ℕ) : Decidable (isType2 S x) := by
  unfold isType2; exact inferInstance

def type1Only (A S : Finset ℕ) : Finset ℕ :=
  (A \ S).filter (fun x => ¬ isType2 S x)

def potentialBlocked (S : Finset ℕ) : Finset ℕ :=
  (S ×ˢ S ×ˢ S).image (fun t => t.1 + t.2.1 - t.2.2)

/-! ## Bridge Lemma (axiomatized; proven in KSS_Proven.lean) -/

axiom blocked_element_form (A S : Finset ℕ) (hMax : S.IsMaximalSidon A)
    (x : ℕ) (hx : x ∈ A) (hxS : x ∉ S) :
    (∃ a b c : ℕ, a ∈ S ∧ b ∈ S ∧ c ∈ S ∧ x + c = a + b) ∨
    (∃ a b : ℕ, a ∈ S ∧ b ∈ S ∧ x + x = a + b)

namespace SidonExploration

/-! ## Blocking Count Lemmas -/

lemma blockedType2_card_le (A S : Finset ℕ) :
    (blockedType2 A S).card ≤ S.card ^ 2 := by
  classical
  have hf_range : ∀ x ∈ blockedType2 A S, 2 * x ∈ sumset S := by
    intro x hx
    simp only [blockedType2, Finset.mem_filter, Finset.mem_sdiff] at hx
    obtain ⟨_, ⟨a, ha, b, hb, heq⟩⟩ := hx
    simp only [sumset, Finset.mem_image, Finset.mem_product]
    exact ⟨⟨a, b⟩, ⟨ha, hb⟩, by dsimp; omega⟩
  have hf_inj : ∀ x ∈ blockedType2 A S, ∀ y ∈ blockedType2 A S,
      2 * x = 2 * y → x = y := by intro x _ y _ h; omega
  calc (blockedType2 A S).card
      = ((blockedType2 A S).image (fun x => 2 * x)).card :=
        (Finset.card_image_of_injOn (by intro x hx y hy h; exact hf_inj x hx y hy h)).symm
    _ ≤ (sumset S).card := by
        apply Finset.card_le_card; intro y hy
        simp only [Finset.mem_image] at hy
        obtain ⟨x, hx, rfl⟩ := hy; exact hf_range x hx
    _ ≤ S.card ^ 2 := by
        unfold sumset
        calc ((S ×ˢ S).image _).card ≤ (S ×ˢ S).card := Finset.card_image_le
          _ = S.card ^ 2 := by rw [Finset.card_product]; ring

lemma card_blocked_partition (A S : Finset ℕ) :
    (A \ S).card = (blockedType2 A S).card + (type1Only A S).card := by
  unfold blockedType2 type1Only isType2
  exact (@Finset.card_filter_add_card_filter_not ℕ (A \ S)
    (fun x => ∃ a ∈ S, ∃ b ∈ S, 2 * x = a + b) _ _).symm

lemma type1Only_subset_potentialBlocked (A S : Finset ℕ) (hMax : S.IsMaximalSidon A) :
    type1Only A S ⊆ potentialBlocked S := by
  intro x hx
  simp only [type1Only, Finset.mem_filter, Finset.mem_sdiff] at hx
  obtain ⟨⟨hxA, hxS⟩, hxNT2⟩ := hx
  have hBlocked := blocked_element_form A S hMax x hxA hxS
  cases hBlocked with
  | inl hType1 =>
    obtain ⟨a, b, c, ha, hb, hc, heq⟩ := hType1
    simp only [potentialBlocked, Finset.mem_image, Finset.mem_product]
    exact ⟨(a, (b, c)), ⟨ha, hb, hc⟩, by dsimp; omega⟩
  | inr hType2 =>
    exfalso
    obtain ⟨a, b, ha, hb, heq⟩ := hType2
    exact hxNT2 ⟨a, ha, b, hb, by omega⟩

/-! ## New Sums Per Step -/

/-- Adding x to a Sidon set S creates at most |S| + 1 new sums. -/
theorem new_sums_per_step (S : Finset ℕ) (x : ℕ) (hx : x ∉ S) :
    (sumset (insert x S)).card ≤ (sumset S).card + S.card + 1 := by
  classical
  set W := (insert x S).image (fun s => x + s) with hW_def
  have hW_card : W.card ≤ S.card + 1 := by
    calc W.card ≤ (insert x S).card := Finset.card_image_le
      _ = S.card + 1 := by rw [Finset.card_insert_eq_ite]; simp [hx]
  have hSub : sumset (insert x S) ⊆ sumset S ∪ W := by
    intro n hn
    simp only [sumset, Finset.mem_image, Finset.mem_product] at hn
    obtain ⟨⟨a, b⟩, ⟨ha, hb⟩, rfl⟩ := hn
    rcases Finset.mem_insert.mp ha with rfl | haS
    · apply Finset.mem_union_right
      exact Finset.mem_image_of_mem _ hb
    · rcases Finset.mem_insert.mp hb with hbx | hbS
      · apply Finset.mem_union_right
        have hab : a + b = x + a := by omega
        rw [hab]
        exact Finset.mem_image_of_mem _ (Finset.mem_insert_of_mem haS)
      · apply Finset.mem_union_left
        simp only [sumset, Finset.mem_image, Finset.mem_product]
        exact ⟨⟨a, b⟩, ⟨haS, hbS⟩, rfl⟩
  calc (sumset (insert x S)).card
      ≤ (sumset S ∪ W).card := Finset.card_le_card hSub
    _ ≤ (sumset S).card + W.card := Finset.card_union_le _ _
    _ ≤ (sumset S).card + (S.card + 1) := Nat.add_le_add_left hW_card _
    _ = (sumset S).card + S.card + 1 := by omega

/-! ## Framework Reduction Theorem -/

/-- **Maximal-blocking framework reduction**: If |type1Only(A,S)| ≤ f(|S|),
    then |A| ≤ |S| + |S|² + f(|S|).

    This reduces this particular maximal-blocking strategy to bounding
    |type1Only|. It is not a reduction of the full Erdős 530 problem.
-/
theorem framework_reduction (A S : Finset ℕ) (hMax : S.IsMaximalSidon A)
    (f : ℕ → ℕ) (hf : (type1Only A S).card ≤ f S.card) :
    A.card ≤ S.card + S.card ^ 2 + f S.card := by
  have hpart := card_blocked_partition A S
  have hT2 := blockedType2_card_le A S
  have hAS : A.card = S.card + (A \ S).card := by
    have := Finset.card_sdiff_add_card_eq_card hMax.1; omega
  omega

/-- Instantiating with f(k) = k³ recovers the N^{1/3} bound. -/
theorem cube_root_from_framework (A S : Finset ℕ) (hMax : S.IsMaximalSidon A)
    (hSge1 : S.card ≥ 1)
    (hType1 : (type1Only A S).card ≤ S.card ^ 3) :
    A.card ≤ 3 * S.card ^ 3 := by
  have h := framework_reduction A S hMax (fun k => k ^ 3) hType1
  simp only at h
  have h1 : S.card ≤ S.card ^ 3 := by nlinarith [hSge1]
  have h2 : S.card ^ 2 ≤ S.card ^ 3 := by nlinarith [hSge1]
  omega

/-! ## Discussion: The √N Barrier

The framework shows: **this maximal-blocking strategy reduces to bounding
|type1Only(A,S)|.**

| Bound on |type1Only| | Result | Method |
|---|---|---|
| f(k) = k³ | N^{1/3} | Naive: type1Only ⊆ image of S³ |
| f(k) = k² | N^{1/2} | Would give square-root order in this framework |
| f(k) = k | N^{1/2} | Stronger than needed here |

The naive bound f(k) = k³ arises because each Type 1 element x = a+b-c
is in the image of (a,b,c) ∈ S³ under the map (a,b,c) ↦ a+b-c,
so |type1Only| ≤ |S ×ˢ S ×ˢ S| = |S|³.

To improve: exploit that many triples (a,b,c) give the SAME x.
Sidon property says distinct pairs {a,b} give distinct sums a+b.
For fixed sum σ = a+b, the elements x = σ-c range over at most |S|
values (one per c). Since there are at most |S|²/2 distinct sums
(Sidon!), we get |type1Only| ≤ |S|² · |S| / something...
but this doesn't directly improve the bound without double-counting.

KSS (1975) achieves ℓ(N) ≥ c√N by a different extraction argument, not by the
false universal claim that every arbitrary maximal Sidon subset has only
O(|S|²) blocked elements.
-/

end SidonExploration
