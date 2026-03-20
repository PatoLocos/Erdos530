"""
Analyze the 2-to-1 map structure for maximal Sidon sets.

Goal: For small N, find maximal Sidon sets S in {1,...,N}, identify all blocked
elements, construct ALL possible 2-to-1 maps f: A\S -> S×S, and analyze which
constructions work and why.

This will guide the Lean formalization of the KSS axiom.
"""

from itertools import combinations, product
from collections import defaultdict
import sys


def is_sidon(S):
    """Check if S is a Sidon set (all pairwise sums distinct)."""
    S = sorted(S)
    sums = set()
    for i, a in enumerate(S):
        for j, b in enumerate(S):
            if i <= j:
                s = a + b
                if s in sums:
                    return False
                sums.add(s)
    return True


def find_maximal_sidon_sets(N):
    """Find all maximal Sidon subsets of {1,...,N}."""
    A = set(range(1, N + 1))
    results = []
    
    # Try all subsets (feasible for small N)
    for size in range(N, 0, -1):
        for S_tuple in combinations(range(1, N + 1), size):
            S = set(S_tuple)
            if not is_sidon(S):
                continue
            # Check maximality: no element of A\S can be added
            is_maximal = True
            for x in A - S:
                if is_sidon(S | {x}):
                    is_maximal = False
                    break
            if is_maximal:
                results.append(frozenset(S))
        if results:
            break  # Only find the largest maximal sets first
    
    # Also find ALL maximal (not just largest)
    all_maximal = []
    for size in range(1, N + 1):
        for S_tuple in combinations(range(1, N + 1), size):
            S = set(S_tuple)
            if not is_sidon(S):
                continue
            is_maximal = True
            for x in A - S:
                if is_sidon(S | {x}):
                    is_maximal = False
                    break
            if is_maximal:
                all_maximal.append(frozenset(S))
    
    return all_maximal


def get_sumset(S):
    """Return the sumset S+S = {a+b : a,b in S}."""
    return {a + b for a in S for b in S}


def get_witness_pairs(x, S):
    """
    Find all witness pairs (a,b) in S×S that block element x.
    
    Type 1: x + c = a + b for some c in S  =>  pair (a,b) witnesses via c
    Type 2: 2x = a + b  =>  pair (a,b) witnesses via doubling
    
    Returns: list of (a, b) pairs (ordered, a <= b) with their type
    """
    S_list = sorted(S)
    sumset = get_sumset(S)
    witnesses = []
    seen = set()
    
    # Type 1: x + c = a + b for some c in S, a,b in S
    for c in S_list:
        sigma = x + c
        # Find all (a,b) with a+b = sigma, a,b in S
        for a in S_list:
            b = sigma - a
            if b in S and b >= a:
                pair = (a, b)
                key = ('T1', pair, c)
                if key not in seen:
                    seen.add(key)
                    witnesses.append(('T1', pair, c))
    
    # Type 2: 2x = a + b for a,b in S
    double_x = 2 * x
    for a in S_list:
        b = double_x - a
        if b in S and b >= a:
            pair = (a, b)
            key = ('T2', pair)
            if key not in seen:
                seen.add(key)
                witnesses.append(('T2', pair, None))
    
    return witnesses


def get_valid_target_pairs(x, S):
    """Get all (a,b) pairs in S×S (ordered) that can serve as f(x)."""
    witnesses = get_witness_pairs(x, S)
    pairs = set()
    for wtype, pair, c in witnesses:
        # We need ORDERED pairs for the product S×S
        a, b = pair
        pairs.add((a, b))
        if a != b:
            pairs.add((b, a))
    return pairs


def find_2to1_map_backtrack(blocked, S, pair_options):
    """
    Find a 2-to-1 map using backtracking.
    
    blocked: list of blocked elements
    S: the Sidon set
    pair_options: dict mapping each blocked element to its valid target pairs
    
    Returns: dict mapping each blocked element to a pair, or None
    """
    assignment = {}
    pair_count = defaultdict(int)
    
    def backtrack(idx):
        if idx == len(blocked):
            return True
        x = blocked[idx]
        for pair in pair_options[x]:
            if pair_count[pair] < 2:
                assignment[x] = pair
                pair_count[pair] += 1
                if backtrack(idx + 1):
                    return True
                del assignment[x]
                pair_count[pair] -= 1
        return False
    
    if backtrack(0):
        return assignment
    return None


def analyze_assignment(assignment, S):
    """Analyze the structure of a valid 2-to-1 assignment."""
    pair_to_elements = defaultdict(list)
    for x, pair in assignment.items():
        pair_to_elements[pair].append(x)
    
    fiber_sizes = defaultdict(int)
    for pair, elements in pair_to_elements.items():
        fiber_sizes[len(elements)] += 1
    
    return pair_to_elements, fiber_sizes


def classify_element(x, S):
    """Classify blocked element as Type 1, Type 2, or Both."""
    sumset = get_sumset(S)
    is_type2 = (2 * x) in sumset
    is_type1 = any((x + c) in sumset for c in S)
    
    if is_type2 and is_type1:
        return "Both"
    elif is_type2:
        return "Type2"
    elif is_type1:
        return "Type1"
    else:
        return "None"  # Should not happen for blocked elements


def main():
    print("=" * 70)
    print("ANALYSIS OF 2-TO-1 MAPS FOR MAXIMAL SIDON SETS")
    print("=" * 70)
    
    for N in range(5, 21):
        print(f"\n{'='*70}")
        print(f"N = {N}")
        print(f"{'='*70}")
        
        A = set(range(1, N + 1))
        all_maximal = find_maximal_sidon_sets(N)
        
        if not all_maximal:
            print("  No maximal Sidon sets found (shouldn't happen)")
            continue
        
        print(f"  Found {len(all_maximal)} maximal Sidon set(s)")
        
        # Analyze each maximal Sidon set (limit to a few for large N)
        for S_frozen in all_maximal[:3]:
            S = set(S_frozen)
            blocked = sorted(A - S)
            k = len(S)
            
            print(f"\n  S = {sorted(S)} (k={k})")
            print(f"  Blocked: {blocked} (count={len(blocked)})")
            print(f"  Bound 2k² = {2*k**2}")
            print(f"  Ratio |blocked|/k² = {len(blocked)/k**2:.3f}")
            
            # Classify blocked elements
            type_counts = defaultdict(int)
            for x in blocked:
                typ = classify_element(x, S)
                type_counts[typ] += 1
            print(f"  Types: {dict(type_counts)}")
            
            # Get witness pairs for each blocked element
            pair_options = {}
            print(f"\n  Witness analysis:")
            for x in blocked:
                valid_pairs = get_valid_target_pairs(x, S)
                pair_options[x] = sorted(valid_pairs)
                witnesses = get_witness_pairs(x, S)
                typ = classify_element(x, S)
                print(f"    x={x:3d} [{typ:5s}]: {len(valid_pairs)} target pairs, "
                      f"witnesses: {[(w[0], w[1]) for w in witnesses[:4]]}"
                      f"{'...' if len(witnesses) > 4 else ''}")
            
            # Find a valid 2-to-1 assignment
            assignment = find_2to1_map_backtrack(blocked, S, pair_options)
            
            if assignment:
                pair_to_elements, fiber_sizes = analyze_assignment(assignment, S)
                print(f"\n  ✓ Valid 2-to-1 assignment found!")
                print(f"    Fiber size distribution: {dict(fiber_sizes)}")
                print(f"    Assignment:")
                for x in blocked:
                    pair = assignment[x]
                    typ = classify_element(x, S)
                    print(f"      f({x}) = {pair}  [{typ}]")
                
                # Analyze the pattern
                print(f"\n    Pairs used (with fibers):")
                for pair, elements in sorted(pair_to_elements.items()):
                    types = [classify_element(x, S) for x in elements]
                    print(f"      {pair} <- {elements} types={types}")
            else:
                print(f"\n  ✗ NO valid 2-to-1 assignment exists!")
                print(f"    THIS WOULD DISPROVE THE KSS AXIOM!")
            
            # Check: does the lex-min canonical assignment work?
            lex_assignment = {}
            for x in blocked:
                if pair_options[x]:
                    lex_assignment[x] = min(pair_options[x])  # lex-min pair
            
            lex_pair_to_elements, lex_fiber_sizes = analyze_assignment(lex_assignment, S)
            max_fiber = max(len(v) for v in lex_pair_to_elements.values()) if lex_pair_to_elements else 0
            print(f"\n  Lex-min canonical map: max fiber = {max_fiber}")
            if max_fiber > 2:
                print(f"    ✗ Lex-min FAILS (fiber > 2)")
                for pair, elements in sorted(lex_pair_to_elements.items()):
                    if len(elements) > 2:
                        print(f"      {pair} <- {elements} (fiber={len(elements)})")
            else:
                print(f"    ✓ Lex-min works!")

        # Stop at N=15 for reasonable runtime
        if N >= 15:
            break


if __name__ == "__main__":
    main()
