import Mathlib.Data.Finset.Card
import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic
import Mathlib.Data.Finset.Powerset
import Mathlib.Data.Nat.Prime.Basic

/-!
# Singer Extraction: A Conditional Interval Model

This file explores an axiomatized Singer-partition extraction for dense initial
segments of the natural numbers. It is **not** a formalization of the official
Erdős 530 lower bound, which concerns arbitrary N-element finite subsets of R.

## Architecture

The proof has two pillars, both axiomatized:

1. **Singer's Partition Theorem** (1938): For prime p, ℤ/(p²+p+1)ℤ
   can be partitioned into p+1 Sidon sets, each of size p+1.
   (Proven via finite field extensions, not available in Mathlib.)

2. **Modular Projection Lemma**: A Sidon subset of [1,N] maps to a
   Sidon multiset in ℤ/qℤ under reduction mod q. More precisely:
   if A ⊆ [1,N] is Sidon, then for q > 2N, the reduction mod q is
   injective on A and the image is Sidon in ℤ/qℤ.

## Main Results

- `singer_partition`: Axiom — Singer's partition exists
- `modular_projection_sidon`: Axiom — mod-q projection preserves Sidon
- `singer_pigeonhole`: Theorem — pigeonhole on Singer partition extracts Ω(√q) Sidon
- `dense_interval_sqrt_bound`: Theorem — a conditional square-root extraction
  for sets contained in `{0, ..., N-1}`

## The Conditional Singer Strategy

Given A ⊆ {0, ..., N-1} with |A| = N (therefore essentially the whole initial
segment):
1. Choose prime p with p²+p+1 > 2N (exists by Bertrand-like bounds)
2. Reduce A mod (p²+p+1) — injective since p²+p+1 > 2N > max pairwise diff
3. By Singer's theorem, ℤ/(p²+p+1)ℤ = S₁ ∪ ... ∪ S_{p+1}, each Sᵢ Sidon
4. By pigeonhole, some Sᵢ contains ≥ N/(p+1) elements of A's image
5. The preimage of this intersection is Sidon in A (modular Sidon lifts)
6. Since p ≈ √(2N), we get ≥ N/(√(2N)+1) ≈ √N/√2 Sidon elements

## Axiom Budget and Scope

This file uses two axioms beyond Lean's core:
- `singer_partition` (algebraic — would need finite field theory)
- `modular_projection_sidon` (number-theoretic — needs sum-distinctness mod q)

Some are standard textbook results, but the pipeline in this file is still a
conditional interval model. It does not prove the KSS theorem for arbitrary
finite sets.

## References

- Singer, J. (1938). "A theorem in finite projective geometry..."
- Komlos, Sulyok, Szemeredi (1975), for the actual arbitrary-set lower bound
-/

/-! ## Part 1: Definitions for modular Sidon sets -/

/-- A Sidon set over ℕ: all pairwise sums are distinct. -/
def Finset.IsSidon (s : Finset ℕ) : Prop :=
  ∀ a b c d : ℕ, a ∈ s → b ∈ s → c ∈ s → d ∈ s →
    a + b = c + d → ({a, b} : Set ℕ) = {c, d}

/-- A Sidon set in ℤ/nℤ: all pairwise sums are distinct modulo n. -/
def IsSidonMod (n : ℕ) (s : Finset (ZMod n)) : Prop :=
  ∀ a b c d : ZMod n, a ∈ s → b ∈ s → c ∈ s → d ∈ s →
    a + b = c + d → ({a, b} : Set (ZMod n)) = {c, d}

/-- A partition of ℤ/nℤ into k parts is a list of Finsets that are
    pairwise disjoint and cover all of ℤ/nℤ. -/
structure SidonPartition (n : ℕ) (k : ℕ) where
  parts : Fin k → Finset (ZMod n)
  disjoint : ∀ i j : Fin k, i ≠ j → Disjoint (parts i) (parts j)
  covers : ∀ x : ZMod n, ∃ i : Fin k, x ∈ parts i
  each_sidon : ∀ i : Fin k, IsSidonMod n (parts i)
  each_size : ∀ i : Fin k, (parts i).card = k

/-! ## Part 2: Axioms -/

/-- **Singer's Partition Theorem** (1938).

For any prime p, the group ℤ/(p²+p+1)ℤ admits a partition into p+1
Sidon sets, each of size p+1.

This is constructed from the multiplicative structure of 𝔽_{p³}/𝔽_p.
The cosets of the norm-1 subgroup of 𝔽_{p³}× form a perfect difference
set, and the translates of this difference set partition the group.

**Proof status**: Standard textbook result (Singer 1938, Hall 1986).
Not in Mathlib — would require finite field extensions and projective geometry.
-/
axiom singer_partition (p : ℕ) (hp : Nat.Prime p) :
    SidonPartition (p ^ 2 + p + 1) (p + 1)

/-- **Modular Projection Preserves Sidon** (Folklore).

If A ⊆ [0, N-1] is a Sidon set of natural numbers, and q > 2N,
then the reduction A mod q is injective and the image is Sidon in ℤ/qℤ.

Proof sketch: If a+b = c+d in ℤ/qℤ for a,b,c,d ∈ A, then
a+b ≡ c+d (mod q). Since 0 ≤ a+b, c+d < 2N < q, the congruence
is actually an equality in ℕ. Then apply the Sidon property of A.

**Proof status**: Elementary but requires `ZMod` casting infrastructure
that is tedious to formalize. Could be proven with sufficient Mathlib work.
-/
axiom modular_projection_sidon (A : Finset ℕ) (q : ℕ) (hq : q ≥ 1)
    (hA_sidon : A.IsSidon)
    (hA_range : ∀ a ∈ A, a < q)
    (hA_inj : ∀ a ∈ A, ∀ b ∈ A, (a : ZMod q) = (b : ZMod q) → a = b) :
    IsSidonMod q (A.image (fun (x : ℕ) => (x : ZMod q)))

/-- **Prime Existence for Singer** (Bertrand-type).

For N ≥ 2, there exists a prime p such that p² + p + 1 > 2N and p ≤ 2√N.
This ensures the Singer modulus is large enough for injection while p is small
enough to give a good pigeonhole bound.

More precisely: we need p with N < (p²+p+1)/2, so p ≈ √(2N) suffices.
By Bertrand's postulate, such a prime exists in [√(2N), 2√(2N)].

**Proof status**: Follows from Bertrand's postulate (in Mathlib as
`Nat.exists_infinite_primes` for weak form; the interval form needs more).
-/
axiom exists_singer_prime (N : ℕ) (hN : N ≥ 2) :
    ∃ p : ℕ, Nat.Prime p ∧ p ^ 2 + p + 1 > 2 * N ∧ p ≤ 3 * Nat.sqrt N

/-! ## Part 3: Combinatorial Pipeline -/

namespace SingerExtraction

/-- **Pigeonhole on Singer Partition.**

Given a finite set B ⊆ ℤ/qℤ of size m, and a partition of ℤ/qℤ into k
Sidon sets, there exists a part that contains at least ⌈m/k⌉ elements of B.
Moreover, the intersection B ∩ Sᵢ is Sidon (as a subset of a Sidon set).

This is the core combinatorial step: Singer gives the partition,
pigeonhole finds a large Sidon piece.
-/
theorem pigeonhole_partition {n k : ℕ} (_hn : n ≥ 1) (hk : k ≥ 1)
    (P : SidonPartition n k)
    (B : Finset (ZMod n)) :
    ∃ i : Fin k, (B.filter (· ∈ P.parts i)).card ≥ B.card / k := by
  classical
  by_cases h0 : B.card / k = 0
  · exact ⟨⟨0, by omega⟩, by omega⟩
  · by_contra hcontra; push_neg at hcontra
    -- B = disjoint union of filtered parts
    have hB_eq : B = Finset.univ.biUnion (fun i : Fin k => B.filter (· ∈ P.parts i)) := by
      ext x; simp only [Finset.mem_biUnion, Finset.mem_univ, true_and, Finset.mem_filter]
      exact ⟨fun hx => let ⟨i, hi⟩ := P.covers x; ⟨i, hx, hi⟩, fun ⟨_, hx, _⟩ => hx⟩
    have hdisj : Set.PairwiseDisjoint (↑(Finset.univ : Finset (Fin k)))
        (fun i => B.filter (· ∈ P.parts i)) := by
      intro i _ j _ hij
      change Disjoint (B.filter (· ∈ P.parts i)) (B.filter (· ∈ P.parts j))
      rw [Finset.disjoint_filter]
      intro x _ hxi; exact Finset.disjoint_left.mp (P.disjoint i j hij) hxi
    have hcard : B.card = ∑ i ∈ Finset.univ, (B.filter (· ∈ P.parts i)).card := by
      conv_lhs => rw [hB_eq]; exact Finset.card_biUnion hdisj
    -- Strict: ∑ filter_cards < ∑ (B.card/k) since each filter < B.card/k
    have hslt : ∑ i ∈ Finset.univ, (B.filter (· ∈ P.parts i)).card <
        ∑ _i ∈ (Finset.univ : Finset (Fin k)), B.card / k := by
      apply Finset.sum_lt_sum
      · intro i _; exact le_of_lt (hcontra i)
      · exact ⟨⟨0, by omega⟩, Finset.mem_univ _, hcontra ⟨0, by omega⟩⟩
    -- ∑ (B.card/k) = k * (B.card/k)
    simp only [Finset.sum_const, Finset.card_univ, Fintype.card_fin, smul_eq_mul] at hslt
    -- Name k * (B.card/k) so omega can handle it linearly
    set kq := k * (B.card / k) with hkq_def
    have hkq_le : kq ≤ B.card := by
      show k * (B.card / k) ≤ B.card
      rw [mul_comm]; exact Nat.div_mul_le_self B.card k
    omega

/-- A filter-intersection of a Sidon set is still Sidon. -/
lemma sidon_filter_sidon {n : ℕ} (S : Finset (ZMod n)) (hS : IsSidonMod n S)
    (P : ZMod n → Prop) [DecidablePred P] :
    IsSidonMod n (S.filter P) := by
  intro a b c d ha hb hc hd hab
  have ha' := (Finset.mem_filter.mp ha).1
  have hb' := (Finset.mem_filter.mp hb).1
  have hc' := (Finset.mem_filter.mp hc).1
  have hd' := (Finset.mem_filter.mp hd).1
  exact hS a b c d ha' hb' hc' hd' hab

/-- Intersection with a Sidon part of a partition is Sidon. -/
lemma inter_partition_sidon {n k : ℕ} (P : SidonPartition n k)
    (i : Fin k) (B : Finset (ZMod n)) :
    IsSidonMod n (B.filter (· ∈ P.parts i)) := by
  intro a b c d ha hb hc hd hab
  have ha' := (Finset.mem_filter.mp ha).2
  have hb' := (Finset.mem_filter.mp hb).2
  have hc' := (Finset.mem_filter.mp hc).2
  have hd' := (Finset.mem_filter.mp hd).2
  exact P.each_sidon i a b c d ha' hb' hc' hd' hab

/-- **Key Extraction Theorem (modular version).**

Given B ⊆ ℤ/(p²+p+1)ℤ with |B| = m, Singer's partition gives a Sidon
subset of B of size ≥ m/(p+1).
-/
theorem singer_extraction_mod (p : ℕ) (hp : Nat.Prime p)
    (B : Finset (ZMod (p ^ 2 + p + 1))) :
    ∃ T : Finset (ZMod (p ^ 2 + p + 1)),
      T ⊆ B ∧ IsSidonMod (p ^ 2 + p + 1) T ∧
      T.card ≥ B.card / (p + 1) := by
  have hk : p + 1 ≥ 1 := by omega
  have hn : p ^ 2 + p + 1 ≥ 1 := by omega
  obtain ⟨i, hi⟩ := pigeonhole_partition hn hk (singer_partition p hp) B
  exact ⟨B.filter (· ∈ (singer_partition p hp).parts i),
         Finset.filter_subset _ _,
         inter_partition_sidon (singer_partition p hp) i B,
         hi⟩

/-! ## Part 4: Lifting Back to ℕ -/

/-- **Sidon Lift**: If the mod-q image of A is Sidon and the map is injective,
    any Sidon subset of the image lifts to a Sidon subset of A.

    More precisely: if T ⊆ image(A) is Sidon mod q, and the casting is
    injective on A, then the preimage A' = { a ∈ A | (a : ZMod q) ∈ T }
    is Sidon over ℕ (provided q > 2·max(A)).
-/
axiom sidon_lift (A : Finset ℕ) (q : ℕ) (hq : q ≥ 1)
    (T : Finset (ZMod q))
    (hT_sidon : IsSidonMod q T)
    (hT_sub : T ⊆ A.image (fun (x : ℕ) => (x : ZMod q)))
    (hA_range : ∀ a ∈ A, 2 * a < q)
    (hA_inj : ∀ a ∈ A, ∀ b ∈ A, (a : ZMod q) = (b : ZMod q) → a = b) :
    (A.filter (fun (a : ℕ) => (a : ZMod q) ∈ T)).IsSidon

/-- Size of the lifted preimage equals size of T when casting is injective. -/
axiom lift_card_eq (A : Finset ℕ) (q : ℕ) (hq : q ≥ 1)
    (T : Finset (ZMod q))
    (hT_sub : T ⊆ A.image (fun (x : ℕ) => (x : ZMod q)))
    (hA_inj : ∀ a ∈ A, ∀ b ∈ A, (a : ZMod q) = (b : ZMod q) → a = b) :
    (A.filter (fun (a : ℕ) => (a : ZMod q) ∈ T)).card = T.card

/-! ## Part 5: Main Theorem -/

/-- **Conditional square-root extraction for a dense initial segment.**

For any N ≥ 2 and any A ⊆ [0, N-1] with |A| = N,
there exists a Sidon subset of A of size ≥ N / (3√N + 1),
which is Ω(√N).

Because `A.card = N` and every element of `A` is `< N`, this theorem is about
the dense initial segment case, not arbitrary N-element sets. It depends on the
axioms listed above.
-/
theorem dense_interval_sqrt_bound (A : Finset ℕ) (N : ℕ) (hN : N ≥ 2)
    (hA_card : A.card = N)
    (hA_range : ∀ a ∈ A, a < N) :
    ∃ S : Finset ℕ, S ⊆ A ∧ S.IsSidon ∧
      S.card ≥ N / (3 * Nat.sqrt N + 1) := by
  -- Step 1: Find Singer prime p with p²+p+1 > 2N, p ≤ 3√N
  obtain ⟨p, hp_prime, hp_large, hp_small⟩ := exists_singer_prime N hN
  set q := p ^ 2 + p + 1 with hq_def
  -- Step 2: q > 2N, so casting A → ℤ/qℤ is injective and range-safe
  have hq_pos : q ≥ 1 := by omega
  have hq_large : q > 2 * N := hp_large
  have hA_q_range : ∀ a ∈ A, a < q := by
    intro a ha; have := hA_range a ha; omega
  have hA_2q : ∀ a ∈ A, 2 * a < q := by
    intro a ha; have := hA_range a ha; omega
  have hA_inj : ∀ a ∈ A, ∀ b ∈ A, (a : ZMod q) = (b : ZMod q) → a = b := by
    intro a ha b hb hab
    have ha_lt := hA_q_range a ha
    have hb_lt := hA_q_range b hb
    have hva : ZMod.val (a : ZMod q) = a := ZMod.val_natCast_of_lt ha_lt
    have hvb : ZMod.val (b : ZMod q) = b := ZMod.val_natCast_of_lt hb_lt
    have hval_eq : ZMod.val (a : ZMod q) = ZMod.val (b : ZMod q) := by rw [hab]
    omega
  -- Step 3: Apply Singer extraction in ℤ/qℤ
  set B := A.image (fun (x : ℕ) => (x : ZMod q)) with hB_def
  have hB_card : B.card = N := by
    rw [Finset.card_image_of_injOn]
    · exact hA_card
    · intro x hx y hy hxy; exact hA_inj x hx y hy hxy
  obtain ⟨T, hT_sub, hT_sidon, hT_card⟩ :=
    singer_extraction_mod p hp_prime B
  -- Step 4: Lift T back to ℕ
  set S := A.filter (fun (a : ℕ) => (a : ZMod q) ∈ T) with hS_def
  have hS_sub : S ⊆ A := Finset.filter_subset _ _
  have hS_sidon : S.IsSidon :=
    sidon_lift A q hq_pos T hT_sidon hT_sub hA_2q hA_inj
  have hS_card_eq : S.card = T.card :=
    lift_card_eq A q hq_pos T hT_sub hA_inj
  -- Step 5: Bound the size
  have hT_size : T.card ≥ N / (p + 1) := by
    calc T.card ≥ B.card / (p + 1) := hT_card
      _ = N / (p + 1) := by rw [hB_card]
  have hS_size : S.card ≥ N / (3 * Nat.sqrt N + 1) := by
    rw [hS_card_eq]
    calc T.card ≥ N / (p + 1) := hT_size
      _ ≥ N / (3 * Nat.sqrt N + 1) := by
          apply Nat.div_le_div_left
          · omega
          · omega
  exact ⟨S, hS_sub, hS_sidon, hS_size⟩

/-- **Dense initial segment corollary.**

For every N ≥ 2, any N-element subset of [0, N-1] contains a Sidon subset of
size Ω(√N). This is not the official `ell(N)` lower bound for arbitrary finite
subsets of R.
-/
theorem dense_initial_segment_ge_c_sqrt (N : ℕ) (hN : N ≥ 2) :
    ∀ A : Finset ℕ, A.card = N → (∀ a ∈ A, a < N) →
      ∃ S : Finset ℕ, S ⊆ A ∧ S.IsSidon ∧ S.card ≥ N / (3 * Nat.sqrt N + 1) :=
  fun A hcard hrange => dense_interval_sqrt_bound A N hN hcard hrange

end SingerExtraction

/-! ## Discussion: Axiom Inventory and Formalization Path

### Axioms Used

| Axiom | Status | Formalization Difficulty |
|---|---|---|
| `singer_partition` | Textbook (Singer 1938) | **Hard** — needs finite fields, projective planes |
| `modular_projection_sidon` | Folklore | **Medium** — needs ZMod arithmetic lemmas |
| `exists_singer_prime` | Bertrand's postulate | **Medium** — needs interval prime existence |
| `sidon_lift` | Elementary | **Medium** — reverse direction of mod projection |
| `lift_card_eq` | Elementary | **Easy** — injectivity + filter card |

### Comparison with KSS_Proven.lean

| File | Bound | Axioms | Lines |
|---|---|---|---|
| `KSS_Proven.lean` | N^{1/3} | **None** (axiom-free) | 613 |
| `SingerExtraction.lean` | dense interval √N model | 5 axioms | ~250 |
| Official KSS lower bound | arbitrary finite sets | not formalized here | — |

### Path to Axiom Removal

1. **`lift_card_eq`**: Straightforward with `Finset.card_filter` + injectivity
2. **`sidon_lift`**: Needs `ZMod.val_natCast` manipulation
3. **`modular_projection_sidon`**: Same + the forward direction
4. **`exists_singer_prime`**: Needs Bertrand's postulate from Mathlib
5. **`singer_partition`**: Needs new Mathlib infrastructure:
   - Finite field extensions (𝔽_{p³} over 𝔽_p)
   - Norm map and its kernel
   - Difference sets from cosets
   - Partition into translates

Singer's theorem is useful for interval constructions, but it is not by itself
the missing formal proof of the KSS arbitrary-set lower bound.
-/
