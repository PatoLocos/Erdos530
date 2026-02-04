# Erdős Problem 530: Partial Formalization

A Lean 4 formalization attempt for [Erdős Problem 530](https://www.erdosproblems.com/530).

## ⚠️ Important Disclaimer

**This is NOT a complete proof.** 

The formalization contains **one mathematical axiom** that encapsulates the combinatorial core of the Komlós-Sulyok-Szemerédi (1975) charging argument. The axiom has not been eliminated.

## What This Repository Contains

- `KSS_Proven.lean` - Main formalization (compiles with Mathlib, 1 axiom)
- `530.lean` - Formatted for potential submission to [formal-conjectures](https://github.com/google-deepmind/formal-conjectures)

## What Is Proven (Modulo 1 Axiom)

```
∀ finite A ⊆ ℕ, ∃ Sidon B ⊆ A with |B| ≥ (1/2)√|A|
```

This establishes the **lower bound** direction: ℓ(N) ≥ Ω(√N).

## The Remaining Axiom

```lean
axiom kss_two_to_one_map_exists (A S : Finset ℕ) (hMax : S.IsMaximalSidon A) :
    ∃ (f : ℕ → ℕ × ℕ), 
      (∀ x ∈ A \ S, f x ∈ S ×ˢ S) ∧
      (∀ p ∈ (A \ S).image f, ((A \ S).filter fun x => f x = p).card ≤ 2)
```

This states that blocked elements can be "charged" to pairs in S×S with each pair receiving at most 2 charges. Eliminating this axiom requires formalizing the canonical witness selector and detailed case analysis from KSS Lemma 2.

## Axiom Verification

```
$ lake env lean KSS_Proven.lean
'KSSProven.kss_sqrt_bound' depends on axioms: 
  [propext, Classical.choice, KSSProven.kss_two_to_one_map_exists, Quot.sound]
```

Only `kss_two_to_one_map_exists` is non-standard.

## Building

Requires Lean 4 with Mathlib. From a Mathlib workspace:

```bash
lake env lean KSS_Proven.lean
```

## References

- [Erdős Problem 530](https://www.erdosproblems.com/530)
- Komlós, Sulyok, Szemerédi. "Linear problems in combinatorial number theory." Acta Math. Acad. Sci. Hung. 26 (1975), 113-121.

## License

MIT
