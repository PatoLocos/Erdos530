"""
Compute collision graph edges for Sidon problem experiments.
Two elements x,y collide if there exist distinct z,w with x+y = z+w and {x,y} ≠ {z,w}.
"""

def compute_collision_edges(N):
    """
    For A = {1, ..., N}, find all collision pairs.
    Returns list of edges [{"source": x-1, "target": y-1}] (0-indexed for iGraph)
    """
    A = list(range(1, N+1))
    
    # Build sum -> list of pairs mapping
    sum_to_pairs = {}
    for i, x in enumerate(A):
        for j, y in enumerate(A):
            if i < j:  # unordered pairs, x < y
                s = x + y
                if s not in sum_to_pairs:
                    sum_to_pairs[s] = []
                sum_to_pairs[s].append((x, y))
    
    # Find collisions: pairs that share a sum with another pair
    collision_edges = set()
    for s, pairs in sum_to_pairs.items():
        if len(pairs) >= 2:
            # All pairs with this sum collide with each other
            # But we need edges between ELEMENTS, not pairs
            # If (a,b) and (c,d) collide, then:
            # - {a,b} collides (edge a-b would violate Sidon if both included)
            # Wait, that's not right either...
            
            # Actually: collision graph has vertices = elements of A
            # Edge {x, y} means: including both x and y would create a collision
            # This happens if ∃ z,w ∈ A with x+y = z+w and {x,y} ≠ {z,w}
            
            for p1 in pairs:
                for p2 in pairs:
                    if p1 < p2:  # different pairs
                        # p1 = (a,b), p2 = (c,d), a+b = c+d
                        # This means {a,b} and {c,d} collide
                        # In the collision graph on elements:
                        # Actually we need edges within pairs that share sums
                        pass
    
    # Let me reconsider the collision graph definition.
    # For Sidon: S is Sidon iff for all a,b,c,d in S with a+b=c+d, we have {a,b}={c,d}
    # 
    # The standard collision graph for Sidon:
    # - Vertices: elements of A
    # - Edge {x,y}: there exist z,w in A with x+y=z+w and {x,y}≠{z,w}
    #   i.e., the pair {x,y} "collides" with some other pair
    #
    # S is Sidon iff S induces NO edges in this graph? No, that's not right either.
    #
    # Actually the correct formulation:
    # - Vertices: PAIRS {a,b} with a,b in A, a ≤ b
    # - Edge between {a,b} and {c,d}: a+b = c+d and {a,b} ≠ {c,d}
    #
    # Then S is Sidon iff the induced subgraph on pairs from S is empty (no edges).
    # That's an independent set in the PAIR graph, not element graph.
    
    # For element-based graph: 
    # A simpler model is the "incompatibility graph":
    # - Vertices: elements of A  
    # - Edge {x, y}: x and y CANNOT both be in a Sidon set
    # But two elements CAN both be in a Sidon set unless their sum collides!
    
    # The issue: it's not pairwise - it depends on what else is in the set.
    # {1,2,3} might be Sidon, {1,2,4} might not be.
    
    # Let me use a different approach: direct computation of max Sidon subset
    
    return None

def is_sidon(S):
    """Check if S is a Sidon set."""
    S = sorted(S)
    sums = {}
    for i, a in enumerate(S):
        for j, b in enumerate(S):
            if i <= j:
                s = a + b
                if s in sums:
                    # Check if same pair
                    prev_a, prev_b = sums[s]
                    if not (prev_a == a and prev_b == b):
                        return False
                else:
                    sums[s] = (a, b)
    return True

def find_max_sidon_brute(A, current=None, index=0, best=None):
    """Brute force search for maximum Sidon subset."""
    if current is None:
        current = []
    if best is None:
        best = [0, []]  # [size, set]
    
    if index == len(A):
        if len(current) > best[0] and is_sidon(current):
            best[0] = len(current)
            best[1] = list(current)
        return best
    
    # Try including A[index]
    current.append(A[index])
    if is_sidon(current):
        find_max_sidon_brute(A, current, index+1, best)
    current.pop()
    
    # Try excluding A[index]
    find_max_sidon_brute(A, current, index+1, best)
    
    return best

def find_max_sidon_greedy(A):
    """Greedy: add elements in order if they don't break Sidon property."""
    S = []
    for x in A:
        test = S + [x]
        if is_sidon(test):
            S.append(x)
    return S

# Test
if __name__ == "__main__":
    for N in [10, 15, 20, 25, 30]:
        A = list(range(1, N+1))
        greedy = find_max_sidon_greedy(A)
        print(f"N={N}: greedy Sidon size = {len(greedy)}, ratio = {len(greedy)/N**0.5:.3f}")
        print(f"  Sidon set: {greedy}")
