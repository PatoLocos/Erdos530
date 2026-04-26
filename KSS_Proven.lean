/-
  Sidon Set Blocking Bounds (Formalization)
  =========================================
  
  This file contains a formal proof that every finite set A ⊆ ℕ contains
  a Sidon subset of size Ω(|A|^{1/3}).

  ## Main Results
  
  **Theorem** (`blocking_bound_cubic`): For any maximal Sidon S ⊆ A,
  |A \ S| ≤ |S|² + |S|³.
  
  **Corollary** (`erdos_cube_root_bound`): For any finite A ⊆ ℕ with |A| ≥ 1,
  there exists a Sidon B ⊆ A with |A| ≤ 3|B|³.
  
  ## What This Proves

  **This file proves a natural-number partial result toward Erdős Problem 530:**
  - Partial lower bound: every finite A ⊆ ℕ contains a Sidon subset B with
    |A| ≤ 3|B|³, i.e. |B| = Ω(|A|^{1/3}).
  - The official problem is stated for arbitrary finite A ⊆ ℝ and asks about
    the exact asymptotic behavior of the best guaranteed Sidon subset size.

  **Known classically (not formalized here):**
  - KSS (1975) proved ℓ(N) ≥ c√N for an absolute constant c > 0.
    Combined with the trivial upper bound ℓ(N) ≤ (1+o(1))√N, this gives
    ℓ(N) = Θ(√N). The KSS result is correct; however, our earlier
    axiomatization of an intermediate step (a universal 2-to-1 charging map
    from A \ S to S × S for arbitrary A) was an overstrong claim that is
    FALSE in full generality. The axiom was removed.
  - Formalizing the real √N bound requires encoding the actual KSS argument
    (which may not pass through bounding |A \ S| for an arbitrary maximal
    Sidon S in an arbitrary A).

  **Still OPEN in the literature:**
  - Exact asymptotics: ℓ(N) ~ √N? (i.e., does ℓ(N)/√N → 1?)

  ## Status: ✅ COMPLETE (fully proven, no custom axioms)

  ✅ PROVEN (axiom-free):
    - `singleton_isSidon`: Singleton sets are Sidon
    - `exists_maximal_sidon`: Maximal Sidon subsets exist (finite maximality)
    - `maximal_sidon_nonempty`: Maximal Sidon subsets are nonempty
    - `collision_involves_x`: Any collision in insert x S involves x
    - `blocked_element_form`: Blocked elements have specific algebraic form (16 cases)
    - `blockedType2_card_le`: |Type 2 blocked| ≤ |S|² (injection into sumset)
    - `type1Only_card_le_cube`: |Type 1 only blocked| ≤ |S|³ (subset of S³ image)
    - `blocking_bound_cubic`: |A \ S| ≤ |S|² + |S|³ (main blocking bound)
    - `axiom_free_cube_bound`: |A| ≤ 3|S|³ (cube root bound)
    - `erdos_cube_root_bound`: ∃ Sidon B ⊆ A with |A| ≤ 3|B|³ (main theorem)

  ## References
  - Komlós, Sulyok, Szemerédi. "Linear problems in combinatorial number theory." 
    Acta Math. Acad. Sci. Hung. 26 (1975), 113-121.
  - DOI: 10.1007/BF01895954
  
  Author: Formalized with Lean 4 + Mathlib, February 2026
-/

import Mathlib.Data.Finset.Card
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Data.Real.Sqrt
import Mathlib.Data.Set.Finite.Basic
import Mathlib.Order.Interval.Finset.Nat
import Mathlib.Tactic
import Mathlib.Data.Finset.Powerset

/-! ## Part 1: Definitions -/

/-- A finite set of natural numbers is Sidon if all pairwise sums are distinct. -/
def Finset.IsSidon (s : Finset ℕ) : Prop :=
  ∀ a b c d : ℕ, a ∈ s → b ∈ s → c ∈ s → d ∈ s →
    a + b = c + d → ({a, b} : Set ℕ) = {c, d}

/-- A Sidon subset S of A is maximal if no element of A \ S can be added. -/
def Finset.IsMaximalSidon (S : Finset ℕ) (A : Finset ℕ) : Prop :=
  S ⊆ A ∧ S.IsSidon ∧ ∀ x ∈ A, x ∉ S → ¬(insert x S).IsSidon

namespace KSSProven

/-! ## Part 2: Proven Infrastructure Lemmas -/

/-- Singleton set is Sidon. ✅ PROVEN -/
lemma singleton_isSidon (x : ℕ) : ({x} : Finset ℕ).IsSidon := by
  intro a b c d ha hb hc hd _
  simp only [Finset.mem_singleton] at ha hb hc hd
  subst ha hb hc hd
  rfl

/-- Existence of maximal Sidon subsets via finite cardinality argument. ✅ PROVEN -/
lemma exists_maximal_sidon (A : Finset ℕ) (hA : A.Nonempty) :
    ∃ S : Finset ℕ, S.IsMaximalSidon A := by
  obtain ⟨x, hx⟩ := hA
  classical
  let sidonSubsets := A.powerset.filter Finset.IsSidon
  have hFinite : sidonSubsets.Nonempty := by
    use {x}
    rw [Finset.mem_filter, Finset.mem_powerset]
    exact ⟨Finset.singleton_subset_iff.mpr hx, singleton_isSidon x⟩
  obtain ⟨S, hS, hSmax⟩ := sidonSubsets.exists_max_image Finset.card hFinite
  rw [Finset.mem_filter, Finset.mem_powerset] at hS
  use S
  refine ⟨hS.1, hS.2, ?_⟩
  intro y hy hyS hSidon
  have hInsertInA : insert y S ⊆ A := Finset.insert_subset hy hS.1
  have hInsertIn : insert y S ∈ sidonSubsets := by
    rw [Finset.mem_filter, Finset.mem_powerset]
    exact ⟨hInsertInA, hSidon⟩
  have hCardLarger : (insert y S).card > S.card := by
    simp only [Finset.card_insert_eq_ite, if_neg hyS]
    omega
  have hContra := hSmax (insert y S) hInsertIn
  omega

/-- Any maximal Sidon subset is nonempty when A is nonempty. ✅ PROVEN -/
lemma maximal_sidon_nonempty (A S : Finset ℕ) (hA : A.Nonempty)
    (hMax : S.IsMaximalSidon A) : S.Nonempty := by
  by_contra hS
  simp only [Finset.not_nonempty_iff_eq_empty] at hS
  obtain ⟨x, hx⟩ := hA
  have hxnotS : x ∉ S := by simp [hS]
  have hnotSidon := hMax.2.2 x hx hxnotS
  have hSingletonSidon : (insert x S).IsSidon := by
    simp only [hS, Finset.insert_empty]
    exact singleton_isSidon x
  exact hnotSidon hSingletonSidon

/-! ## Part 3: The Key Algebraic Lemma -/

/-- Key algebraic lemma: from N ≤ 3k², derive k ≥ (1/2)√N. ✅ PROVEN -/
lemma sqrt_bound_from_quadratic (N k : ℝ) (hk : k ≥ 1) (h : N ≤ 3 * k ^ 2) :
    k ≥ (1/2) * Real.sqrt N := by
  have hk_pos : 0 < k := by linarith
  have h1 : Real.sqrt N ≤ Real.sqrt (3 * k ^ 2) := Real.sqrt_le_sqrt h
  have h2 : Real.sqrt (3 * k ^ 2) = Real.sqrt 3 * k := by
    rw [Real.sqrt_mul (by norm_num : (3:ℝ) ≥ 0)]
    rw [Real.sqrt_sq (by linarith : k ≥ 0)]
  rw [h2] at h1
  have sqrt3_bound : Real.sqrt 3 < 2 := by
    have h3 : (3 : ℝ) < 4 := by norm_num
    have h4 : Real.sqrt 3 < Real.sqrt 4 := Real.sqrt_lt_sqrt (by norm_num) h3
    have h5 : Real.sqrt 4 = 2 := by norm_num
    linarith
  have h3 : Real.sqrt N < 2 * k := by
    calc Real.sqrt N ≤ Real.sqrt 3 * k := h1
      _ < 2 * k := by nlinarith
  linarith

/-- Natural number version of the √N bound. ✅ PROVEN -/
lemma enough_for_sqrt (N k : ℕ) (hk : k ≥ 1) (h : N ≤ k + 2 * k^2) :
    (k : ℝ) ≥ (1/2) * Real.sqrt (N : ℝ) := by
  have hkr : (k : ℝ) ≥ 1 := Nat.one_le_cast.mpr hk
  have h1 : (N : ℝ) ≤ ((k + 2 * k^2 : ℕ) : ℝ) := Nat.cast_le.mpr h
  have h2 : ((k + 2 * k^2 : ℕ) : ℝ) = (k : ℝ) + 2 * (k : ℝ) ^ 2 := by push_cast; ring
  have h3 : (k : ℝ) + 2 * (k : ℝ) ^ 2 ≤ 3 * (k : ℝ) ^ 2 := by
    have hk2 : (k : ℝ) ≤ (k : ℝ) ^ 2 := by nlinarith [sq_nonneg (k : ℝ)]
    linarith
  have h3k2 : (N : ℝ) ≤ 3 * (k : ℝ) ^ 2 := by linarith [h1, h2, h3]
  have hk_pos : 0 < (k : ℝ) := by linarith
  have hsqrt1 : Real.sqrt (N : ℝ) ≤ Real.sqrt (3 * (k : ℝ) ^ 2) := Real.sqrt_le_sqrt h3k2
  have hsqrt2 : Real.sqrt (3 * (k : ℝ) ^ 2) = Real.sqrt 3 * (k : ℝ) := by
    rw [Real.sqrt_mul (by norm_num : (3:ℝ) ≥ 0)]
    rw [Real.sqrt_sq (by linarith : (k : ℝ) ≥ 0)]
  rw [hsqrt2] at hsqrt1
  have sqrt3_bound : Real.sqrt 3 < 2 := by
    have h3 : (3 : ℝ) < 4 := by norm_num
    have h4 : Real.sqrt 3 < Real.sqrt 4 := Real.sqrt_lt_sqrt (by norm_num) h3
    have h5 : Real.sqrt 4 = 2 := by norm_num
    linarith
  have hfinal : Real.sqrt (N : ℝ) < 2 * (k : ℝ) := by
    calc Real.sqrt (N : ℝ) ≤ Real.sqrt 3 * (k : ℝ) := hsqrt1
      _ < 2 * (k : ℝ) := by nlinarith
  linarith

/-! ## Part 4: The Blocking Count Argument -/

/-!
### The Blocking Count Argument (Axiom-Free)

Let S be a maximal Sidon subset of A. Every x ∈ A \ S is "blocked" in the sense
that insert x S is not Sidon, so there is a collision involving x.

We classify blocked elements:
- Type 2: 2x = a + b for some a,b ∈ S. These inject into S+S, so there are ≤ |S|².
- Type 1 only: x + c = a + b for some a,b,c ∈ S but x is not Type 2. These lie in
  the image of S³ under (a,b,c) ↦ a+b−c, hence ≤ |S|³.

Thus |A \ S| ≤ |S|² + |S|³, and so |A| ≤ |S| + |S|² + |S|³ ≤ 3|S|³ for |S| ≥ 1.
This yields a Sidon subset of size Ω(|A|^{1/3}) for arbitrary finite A ⊆ ℕ.

Stronger √|A| bounds (KSS 1975) require a different extraction argument; they do
not follow from this "arbitrary maximal Sidon set" counting method alone.
-/

/-- Helper: Any collision in insert x S must involve x when S is Sidon. -/
lemma collision_involves_x (S : Finset ℕ) (x : ℕ) (hSSidon : S.IsSidon)
    (a b c d : ℕ) (ha : a ∈ insert x S) (hb : b ∈ insert x S) 
    (hc : c ∈ insert x S) (hd : d ∈ insert x S)
    (hSum : a + b = c + d) (hNeq : ({a, b} : Set ℕ) ≠ {c, d}) :
    a = x ∨ b = x ∨ c = x ∨ d = x := by
  by_contra hall
  push_neg at hall
  have haS : a ∈ S := by
    simp only [Finset.mem_insert] at ha
    cases ha with | inl h => exact absurd h hall.1 | inr h => exact h
  have hbS : b ∈ S := by
    simp only [Finset.mem_insert] at hb
    cases hb with | inl h => exact absurd h hall.2.1 | inr h => exact h
  have hcS : c ∈ S := by
    simp only [Finset.mem_insert] at hc
    cases hc with | inl h => exact absurd h hall.2.2.1 | inr h => exact h
  have hdS : d ∈ S := by
    simp only [Finset.mem_insert] at hd
    cases hd with | inl h => exact absurd h hall.2.2.2 | inr h => exact h
  exact hNeq (hSSidon a b c d haS hbS hcS hdS hSum)

/-- A blocked element x satisfies: ∃ a,b,c ∈ S such that x + c = a + b OR 2x = a + b -/
lemma blocked_element_form (A S : Finset ℕ) (hMax : S.IsMaximalSidon A)
    (x : ℕ) (hx : x ∈ A) (hxS : x ∉ S) :
    (∃ a b c : ℕ, a ∈ S ∧ b ∈ S ∧ c ∈ S ∧ x + c = a + b) ∨
    (∃ a b : ℕ, a ∈ S ∧ b ∈ S ∧ x + x = a + b) := by
  have hNotSidon := hMax.2.2 x hx hxS
  unfold Finset.IsSidon at hNotSidon
  push_neg at hNotSidon
  obtain ⟨a, b, c, d, ha, hb, hc, hd, hSum, hNeq⟩ := hNotSidon
  have hInv := collision_involves_x S x hMax.2.1 a b c d ha hb hc hd hSum hNeq
  simp only [Finset.mem_insert] at ha hb hc hd
  -- Case split on which elements equal x (16 cases)
  rcases ha with ha_eq | haS <;> rcases hb with hb_eq | hbS <;>
  rcases hc with hc_eq | hcS <;> rcases hd with hd_eq | hdS
  -- Case 1: a=b=c=d=x
  · simp only [ha_eq, hb_eq, hc_eq, hd_eq] at hNeq; exfalso; exact hNeq rfl
  -- Case 2: a=b=c=x, d∈S
  · simp only [ha_eq, hb_eq, hc_eq] at hSum
    have hxd : x = d := by omega
    exact absurd (hxd ▸ hdS) hxS
  -- Case 3: a=b=d=x, c∈S
  · simp only [ha_eq, hb_eq, hd_eq] at hSum  
    have hxc : x = c := by omega
    exact absurd (hxc ▸ hcS) hxS
  -- Case 4: a=b=x, c∈S, d∈S => 2x = c + d
  · simp only [ha_eq, hb_eq] at hSum
    right; exact ⟨c, d, hcS, hdS, hSum⟩
  -- Case 5: a=c=d=x, b∈S
  · simp only [ha_eq, hc_eq, hd_eq] at hSum
    have hxb : x = b := by omega
    exact absurd (hxb ▸ hbS) hxS
  -- Case 6: a=c=x, b∈S, d∈S => x+b=x+d => b=d, {x,b}={x,d} becomes {x,b}={x,b}
  · simp only [ha_eq, hc_eq] at hSum hNeq
    have hbd : b = d := by omega
    subst hbd
    exfalso; exact hNeq rfl
  -- Case 7: a=d=x, b∈S, c∈S => x+b=c+x => b=c, {x,b}={c,x} needs Set.pair_comm
  · simp only [ha_eq, hd_eq] at hSum hNeq  
    have hbc : b = c := by omega
    subst hbc
    exfalso; exact hNeq (Set.pair_comm x b)
  -- Case 8: a=x, b∈S, c∈S, d∈S => x+b=c+d
  · simp only [ha_eq] at hSum
    left; exact ⟨c, d, b, hcS, hdS, hbS, hSum⟩
  -- Case 9: b=c=d=x, a∈S
  · simp only [hb_eq, hc_eq, hd_eq] at hSum
    have hxa : x = a := by omega
    exact absurd (hxa ▸ haS) hxS
  -- Case 10: b=c=x, a∈S, d∈S => a+x=x+d => a=d, {a,x}={x,d} needs Set.pair_comm
  · simp only [hb_eq, hc_eq] at hSum hNeq
    have had : a = d := by omega
    subst had
    exfalso; exact hNeq (Set.pair_comm a x)
  -- Case 11: b=d=x, a∈S, c∈S => a+x=c+x => a=c, {a,x}={c,x} becomes {a,x}={a,x}
  · simp only [hb_eq, hd_eq] at hSum hNeq
    have hac : a = c := by omega
    subst hac
    exfalso; exact hNeq rfl
  -- Case 12: b=x, a∈S, c∈S, d∈S => a+x=c+d
  · simp only [hb_eq] at hSum
    left; exact ⟨c, d, a, hcS, hdS, haS, by omega⟩
  -- Case 13: c=d=x, a∈S, b∈S => a+b=2x
  · simp only [hc_eq, hd_eq] at hSum
    right; exact ⟨a, b, haS, hbS, by omega⟩
  -- Case 14: c=x, a∈S, b∈S, d∈S => a+b=x+d
  · simp only [hc_eq] at hSum
    left; exact ⟨a, b, d, haS, hbS, hdS, by omega⟩
  -- Case 15: d=x, a∈S, b∈S, c∈S => a+b=c+x
  · simp only [hd_eq] at hSum
    left; exact ⟨a, b, c, haS, hbS, hcS, by omega⟩
  -- Case 16: All in S - contradicts hInv (x must participate)
  · exfalso
    rcases hInv with hax | hbx | hcx | hdx
    · rw [hax] at haS; exact hxS haS
    · rw [hbx] at hbS; exact hxS hbS  
    · rw [hcx] at hcS; exact hxS hcS
    · rw [hdx] at hdS; exact hxS hdS

/-!
### A False Quadratic Blocking Shortcut

An earlier draft tried to use the following tempting statement:

**False in this generality:** If S is an arbitrary maximal Sidon subset of A,
then |A \ S| ≤ 2|S|².

The Type 2 part below really does satisfy |Type 2| ≤ |S|², but the analogous
quadratic bound for Type 1 elements does not follow from this naive blocking
classification. Spread-out examples can make the Type 1 image have cubic size.

Thus the verified proof deliberately keeps the weaker Type 1 bound |S|³. The
classical KSS square-root lower bound is correct, but formalizing it requires
their actual extraction argument rather than this overstrong maximal-blocking
shortcut.
-/

/-- The sumset S + S as a Finset. -/
def sumset (S : Finset ℕ) : Finset ℕ :=
  (S ×ˢ S).image (fun p => p.1 + p.2)

/-- The sumset has at most |S|² elements (simple bound). -/
lemma sumset_card_le_sq (S : Finset ℕ) : (sumset S).card ≤ S.card ^ 2 := by
  unfold sumset
  have h1 : ((S ×ˢ S).image (fun p => p.1 + p.2)).card ≤ (S ×ˢ S).card := Finset.card_image_le
  have h2 : (S ×ˢ S).card = S.card * S.card := Finset.card_product S S
  have h3 : S.card * S.card = S.card ^ 2 := (sq S.card).symm
  omega

/-- Elements in the sumset are sums of two elements from S. -/
lemma mem_sumset_iff (S : Finset ℕ) (n : ℕ) : 
    n ∈ sumset S ↔ ∃ a b, a ∈ S ∧ b ∈ S ∧ a + b = n := by
  unfold sumset
  simp only [Finset.mem_image, Finset.mem_product]
  constructor
  · rintro ⟨⟨a, b⟩, ⟨ha, hb⟩, rfl⟩
    exact ⟨a, b, ha, hb, rfl⟩
  · rintro ⟨a, b, ha, hb, rfl⟩
    exact ⟨⟨a, b⟩, ⟨ha, hb⟩, rfl⟩

/-- The set of Type 2 blocked elements (those with 2x = a + b for a,b ∈ S). -/
def blockedType2 (A S : Finset ℕ) : Finset ℕ :=
  (A \ S).filter (fun x => ∃ a ∈ S, ∃ b ∈ S, 2 * x = a + b)

/-- Type 2 blocked elements inject into the sumset via x ↦ 2x. -/
lemma blockedType2_card_le (A S : Finset ℕ) : 
    (blockedType2 A S).card ≤ S.card ^ 2 := by
  classical
  -- The map x ↦ 2x from blockedType2 to sumset is injective
  let f : ℕ → ℕ := fun x => 2 * x
  -- The image of blockedType2 under f is contained in sumset S
  have hf_range : ∀ x ∈ blockedType2 A S, f x ∈ sumset S := by
    intro x hx
    simp only [blockedType2, Finset.mem_filter, Finset.mem_sdiff] at hx
    obtain ⟨_, ⟨a, ha, b, hb, heq⟩⟩ := hx
    rw [mem_sumset_iff]
    exact ⟨a, b, ha, hb, heq.symm⟩
  -- Injectivity of f on ℕ
  have hf_inj : Function.Injective f := fun x y h => by simp only [f] at h; omega
  -- |blockedType2| = |image f blockedType2| since f is injective
  have h1 : (blockedType2 A S).card = ((blockedType2 A S).image f).card := by
    exact (Finset.card_image_of_injective (blockedType2 A S) hf_inj).symm
  -- |image f blockedType2| ≤ |sumset S| since image ⊆ sumset  
  have h2 : ((blockedType2 A S).image f).card ≤ (sumset S).card := by
    apply Finset.card_le_card
    intro y hy
    simp only [Finset.mem_image] at hy
    obtain ⟨x, hx, rfl⟩ := hy
    exact hf_range x hx
  calc (blockedType2 A S).card = ((blockedType2 A S).image f).card := h1
    _ ≤ (sumset S).card := h2
    _ ≤ S.card ^ 2 := sumset_card_le_sq S

/-- The set of elements that could be blocked via Type 1 (x = a + b - c for a,b,c ∈ S). -/
def potentialBlocked (S : Finset ℕ) : Finset ℕ :=
  (S ×ˢ S ×ˢ S).image (fun t => t.1 + t.2.1 - t.2.2)

/-- Type 1 blocked elements are in potentialBlocked (when a + b ≥ c). -/
lemma type1_in_potential (A S : Finset ℕ) (x : ℕ) (_hx : x ∈ A \ S) 
    (hType1 : ∃ a b c : ℕ, a ∈ S ∧ b ∈ S ∧ c ∈ S ∧ x + c = a + b) :
    x ∈ potentialBlocked S := by
  obtain ⟨a, b, c, ha, hb, hc, heq⟩ := hType1
  simp only [potentialBlocked, Finset.mem_image, Finset.mem_product]
  use (a, (b, c))
  constructor
  · exact ⟨ha, hb, hc⟩
  · -- From x + c = a + b and x : ℕ, we have x = a + b - c (when a + b ≥ c)
    -- heq : x + c = a + b, so a + b ≥ c (since x ≥ 0)
    have hab_ge_c : a + b ≥ c := by
      have : x + c = a + b := heq
      omega
    -- Now show x = a + b - c
    have hx_eq : x = a + b - c := by omega
    simp only at hx_eq ⊢
    exact hx_eq.symm

/-- The potential blocked set has at most |S|³ elements. -/
lemma potentialBlocked_card_le (S : Finset ℕ) : 
    (potentialBlocked S).card ≤ S.card ^ 3 := by
  unfold potentialBlocked
  have h1 : ((S ×ˢ S ×ˢ S).image (fun t => t.1 + t.2.1 - t.2.2)).card ≤ (S ×ˢ S ×ˢ S).card := 
    Finset.card_image_le
  have h2 : (S ×ˢ S ×ˢ S).card = S.card * (S.card * S.card) := by simp only [Finset.card_product]
  have h3 : S.card * (S.card * S.card) = S.card ^ 3 := by ring
  omega

/-
Key refinement: For Type 1 elements, we can bound by |S|² using Sidon property.

The crucial observation: for each sum σ = a + b (with a, b ∈ S), and each c ∈ S,
there is at most one potential x = σ - c. Since S is Sidon, the number of 
distinct sums σ is at most |S|(|S|+1)/2. Combined with |S| choices for c,
this gives O(|S|² · 1) total potential Type 1 elements per sum, but since
each x can come from multiple (sum, c) pairs, we need a different argument.

Alternative: Each x ∈ Type 1 only corresponds to at least one triple (a,b,c).
We show the number of valid triples that produce elements in A \ S is ≤ |S|³,
but crucially, we can refine: for a FIXED x, how many triples witness it?
If x + c₁ = a₁ + b₁ and x + c₂ = a₂ + b₂ with c₁ ≠ c₂, then...

The cleanest argument: bound by |S|² using the fact that each blocked element 
x (Type 1 only) has x + c ∈ S + S for some c. The set {x : x + c ∈ S + S} for 
fixed c has at most |S + S| ≤ |S|² elements. But we still union over c ∈ S.

For a tighter bound: Type 1 only elements have x = σ - c where σ ∈ S + S.
The map x ↦ x + c is injective, so for each (σ, c), at most one x.
Total: |S + S| · |S| triples, but many give the same x or x ∉ A.

FINAL APPROACH: We use a weaker but sufficient bound. Each blocked element 
(Type 1 or Type 2) satisfies x = a + b - c for some a,b,c ∈ S (where c might 
equal a or b, or where a = b for Type 2). The set of such x has cardinality 
at most |S|³. This gives the axiom-free bound |A\S| ≤ |S|² + |S|³ (see Part 5).
-/

-- Note: The exact formula (sumset S).card = |S|(|S|+1)/2 for Sidon sets is not needed
-- for the main theorem. We only need the weaker bound (sumset S).card ≤ |S|² which
-- is proven in sumset_card_le_sq.

/-- Refined bound: For Sidon S, sumset has ≤ |S|² elements. ✅ PROVEN -/  
lemma sidon_sumset_card_le_sq (S : Finset ℕ) (_hS : S.IsSidon) :
    (sumset S).card ≤ S.card ^ 2 := sumset_card_le_sq S

/-! ## Part 5: The Main Results — Blocking Bound and Cube Root Bound

The fully proven blocking bound: |A \ S| ≤ |S|² + |S|³, giving an
Ω(N^{1/3}) lower bound for finite natural-number sets.

This uses only proven lemmas (blocked_element_form, blockedType2_card_le,
type1_in_potential, potentialBlocked_card_le). No custom axioms.
-/

/-- The "Type 2" predicate: x is blocked via 2x = a + b for some a,b ∈ S. -/
def isType2 (S : Finset ℕ) (x : ℕ) : Prop :=
  ∃ a ∈ S, ∃ b ∈ S, 2 * x = a + b

instance (S : Finset ℕ) (x : ℕ) : Decidable (isType2 S x) := by
  unfold isType2; exact inferInstance

/-- Type 1 only elements: blocked elements that are NOT Type 2. -/
def type1Only (A S : Finset ℕ) : Finset ℕ :=
  (A \ S).filter (fun x => ¬ isType2 S x)

/-- The partition of A \ S into Type 2 and Type 1 only. -/
lemma card_blocked_partition (A S : Finset ℕ) :
    (A \ S).card = (blockedType2 A S).card + (type1Only A S).card := by
  unfold blockedType2 type1Only isType2
  exact (@Finset.card_filter_add_card_filter_not ℕ (A \ S)
    (fun x => ∃ a ∈ S, ∃ b ∈ S, 2 * x = a + b) _ _).symm

/-- Type 1 only elements are in potentialBlocked when S is maximal Sidon. 

    Proof: x ∈ type1Only means x is blocked but NOT Type 2.
    By blocked_element_form, x must be Type 1.
    By type1_in_potential, x ∈ potentialBlocked S.
-/
lemma type1Only_subset_potentialBlocked (A S : Finset ℕ) (hMax : S.IsMaximalSidon A) :
    type1Only A S ⊆ potentialBlocked S := by
  intro x hx
  simp only [type1Only, Finset.mem_filter, Finset.mem_sdiff] at hx
  obtain ⟨⟨hxA, hxS⟩, hxNotType2⟩ := hx
  -- x is blocked: it's Type 1 or Type 2 by blocked_element_form
  have hBlocked := blocked_element_form A S hMax x hxA hxS
  cases hBlocked with
  | inl hType1 =>
    -- x is Type 1: ∃ a b c ∈ S with x + c = a + b
    -- By type1_in_potential, x ∈ potentialBlocked S
    exact type1_in_potential A S x (Finset.mem_sdiff.mpr ⟨hxA, hxS⟩) hType1
  | inr hType2 =>
    -- x is Type 2: ∃ a b ∈ S with x + x = a + b
    -- But x ∉ blockedType2, so this is impossible
    exfalso
    obtain ⟨a, b, ha, hb, heq⟩ := hType2
    apply hxNotType2
    unfold isType2
    exact ⟨a, ha, b, hb, by omega⟩

/-- Type 1 only elements are bounded by |S|³. -/
lemma type1Only_card_le_cube (A S : Finset ℕ) (hMax : S.IsMaximalSidon A) :
    (type1Only A S).card ≤ S.card ^ 3 := by
  calc (type1Only A S).card
      ≤ (potentialBlocked S).card := Finset.card_le_card (type1Only_subset_potentialBlocked A S hMax)
    _ ≤ S.card ^ 3 := potentialBlocked_card_le S

/-- **Axiom-Free Blocking Bound**: |A \ S| ≤ |S|² + |S|³.
    
    This uses NO custom axioms — only standard Lean foundations.
    Combined with |Type 2| ≤ |S|² and |Type 1 only| ≤ |S|³.
-/
theorem blocking_bound_cubic (A S : Finset ℕ) (hMax : S.IsMaximalSidon A) :
    (A \ S).card ≤ S.card ^ 2 + S.card ^ 3 := by
  rw [card_blocked_partition A S]
  have h1 : (blockedType2 A S).card ≤ S.card ^ 2 := blockedType2_card_le A S
  have h2 : (type1Only A S).card ≤ S.card ^ 3 := type1Only_card_le_cube A S hMax
  omega

/-- **Axiom-Free Cube Root Bound**: |S| ≥ (|A|/3)^{1/3}.

    From |A| ≤ |S| + |S|² + |S|³ ≤ 3|S|³,  
    we get |S|³ ≥ |A|/3, hence |S| ≥ ∛(|A|/3).
    
    In Nat form: 3 * |S|³ ≥ |A|.
-/
theorem axiom_free_cube_bound (A S : Finset ℕ) (hMax : S.IsMaximalSidon A)
    (hSge1 : S.card ≥ 1) :
    A.card ≤ 3 * S.card ^ 3 := by
  have h1 : A.card = S.card + (A \ S).card := by
    have := Finset.card_sdiff_add_card_eq_card hMax.1
    omega
  have h2 : (A \ S).card ≤ S.card ^ 2 + S.card ^ 3 := blocking_bound_cubic A S hMax
  -- Need: |S| + |S|² + |S|³ ≤ 3|S|³ for |S| ≥ 1
  have h3 : S.card ≤ S.card ^ 3 := by nlinarith [hSge1]
  have h4 : S.card ^ 2 ≤ S.card ^ 3 := by nlinarith [hSge1]
  omega

/-- **Erdős Cube Root Bound**: For any finite A ⊆ ℕ with |A| ≥ 1,
    there exists a Sidon B ⊆ A with |A| ≤ 3|B|³.

    This is the main formalized partial result toward Erdős 530: an
    Ω(N^{1/3}) lower bound for finite natural-number sets.
-/
theorem erdos_cube_root_bound (A : Finset ℕ) (hA : A.card ≥ 1) :
    ∃ B : Finset ℕ, B ⊆ A ∧ B.IsSidon ∧ A.card ≤ 3 * B.card ^ 3 := by
  have hAne : A.Nonempty := Finset.card_pos.mp (by omega)
  obtain ⟨S, hMax⟩ := exists_maximal_sidon A hAne
  have hSne : S.Nonempty := maximal_sidon_nonempty A S hAne hMax
  have hSge1 : S.card ≥ 1 := Finset.card_pos.mpr hSne
  exact ⟨S, hMax.1, hMax.2.1, axiom_free_cube_bound A S hMax hSge1⟩

end KSSProven

/-! ## Axiom Verification

The following commands show exactly which axioms each theorem depends on.
-/

#print axioms KSSProven.blocking_bound_cubic
#print axioms KSSProven.axiom_free_cube_bound
#print axioms KSSProven.erdos_cube_root_bound

/-!
## Verified Output (February 2026)

### blocking_bound_cubic (Main blocking bound — AXIOM-FREE)
```
'KSSProven.blocking_bound_cubic' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
```
No custom axioms! This is a fully verified result.

### axiom_free_cube_bound (Cube root bound — AXIOM-FREE)
```
'KSSProven.axiom_free_cube_bound' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
```

### erdos_cube_root_bound (Main theorem — AXIOM-FREE)
```
'KSSProven.erdos_cube_root_bound' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
```

### Axiom Classification:
- `propext` — Propositional extensionality (standard Lean)
- `Classical.choice` — Classical choice (standard Lean)
- `Quot.sound` — Quotient soundness (standard Lean)

All three are standard Lean foundational axioms. **No custom mathematical axioms.**

### Result Summary

| Theorem | Bound | Axiom-Free? | Status |
|---------|-------|-------------|--------|
| `blocking_bound_cubic` | |A\S| ≤ |S|² + |S|³ | ✅ Yes | Fully proven |
| `axiom_free_cube_bound` | |A| ≤ 3|S|³ | ✅ Yes | Fully proven |
| `erdos_cube_root_bound` | ∃ Sidon B ⊆ A, |A| ≤ 3|B|³ | ✅ Yes | Fully proven |

### What This File Proves

✅ **Fully proven (axiom-free):** |A\S| ≤ |S|² + |S|³ for finite A ⊆ ℕ,
which gives a Sidon subset of size Ω(|A|^{1/3}) in that setting.

This is a partial natural-number result toward **Erdős Problem 530**. It is not
the full official statement, which quantifies over arbitrary finite subsets of ℝ.

The stronger bound ℓ(N) ≥ c√N (KSS 1975) is known classically but is not
formalized here. An earlier attempt to axiomatize an intermediate "2-to-1 map
into S×S for arbitrary maximal Sidon S ⊆ A" was an overstrong statement
and is false for general finite A ⊆ ℕ (spread-out examples give
|A\S| = Θ(|S|³)). Formalizing KSS requires encoding their actual extraction
argument, which uses additional structure beyond this naive blocking count.
-/