# Erdős Problem 530: Sidon Set Blocking Bounds (Formalization)

A Lean 4 formalization for [Erdős Problem 530](https://www.erdosproblems.com/530).

## ✅ Fully Proven (No Custom Axioms)

All theorems in this repository are **axiom-free** — they depend only on the standard Lean foundations (`propext`, `Classical.choice`, `Quot.sound`).

## What This Repository Contains

- `KSS_Proven.lean` - Main formalization (compiles with Mathlib, **0 custom axioms**)
- `530.lean` - Formatted for potential submission to [formal-conjectures](https://github.com/google-deepmind/formal-conjectures)

## What Is Proven

```
∀ finite A ⊆ ℕ, |A| ≥ 1 → ∃ Sidon B ⊆ A with |A| ≤ 3|B|³
```

This establishes the **lower bound** direction: ℓ(N) ≥ Ω(N^{1/3}).

### Main Results

| Theorem | Statement | Status |
|---------|-----------|--------|
| `blocking_bound_cubic` | \|A \ S\| ≤ \|S\|² + \|S\|³ | ✅ Proven |
| `axiom_free_cube_bound` | \|A\| ≤ 3\|S\|³ | ✅ Proven |
| `erdos_cube_root_bound` | ∃ Sidon B ⊆ A, \|A\| ≤ 3\|B\|³ | ✅ Proven |

### Key Lemmas

- `singleton_isSidon` — Singleton sets are Sidon
- `exists_maximal_sidon` — Maximal Sidon subsets exist (finite maximality)
- `collision_involves_x` — Any collision in insert x S involves x
- `blocked_element_form` — Blocked elements have specific algebraic form (16 cases)
- `blockedType2_card_le` — |Type 2 blocked| ≤ |S|² (injection into sumset)
- `type1Only_card_le_cube` — |Type 1 only blocked| ≤ |S|³ (subset of S³ image)

## Axiom Verification

```
'KSSProven.erdos_cube_root_bound' depends on axioms: 
  [propext, Classical.choice, Quot.sound]
```

All three are standard Lean foundational axioms. **No custom mathematical axioms.**

## What This Doesn't Prove

The stronger bound ℓ(N) ≥ Ω(√N) from KSS (1975) requires a 2-to-1 charging argument. An earlier version of this formalization axiomatized that claim, but computational verification showed the axiom is **false** under universal quantification over all finite A ⊆ ℕ (counterexample: spread-out Sidon sets where |A\S| grows as Θ(|S|³) > 2|S|²). The false axiom was removed.

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
