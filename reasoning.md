Erdős Problem 530 (OPEN)

Let 
ℓ
(
N
)
ℓ(N) be maximal such that in any finite set 
A
⊂
R
A⊂R of size 
N
N there exists a Sidon subset 
S
S of size 
ℓ
(
N
)
ℓ(N). Determine the order of 
ℓ
(
N
)
ℓ(N).

In particular, is it true that 
ℓ
(
N
)
∼
N
1
/
2
ℓ(N)∼N 
1/2
 ?

Key facts from the page:

Originally asked by Riddell (1969).
Erdős noted: 
N
1
/
3
≪
ℓ
(
N
)
≤
(
1
+
o
(
1
)
)
N
1
/
2
N 
1/3
 ≪ℓ(N)≤(1+o(1))N 
1/2
 , with the upper bound from 
A
=
{
1
,
…
,
N
}
A={1,…,N}.
KSS (1975) improved the lower bound to 
N
1
/
2
≪
ℓ
(
N
)
N 
1/2
 ≪ℓ(N) — this is exactly what your formalization proves.
The correct constant is unknown, but it is likely 
ℓ
(
N
)
∼
N
1
/
2
ℓ(N)∼N 
1/2
 .
Alon–Erdős (1985) made the stronger conjecture that 
A
A can always be partitioned into at most 
(
1
+
o
(
1
)
)
N
1
/
2
(1+o(1))N 
1/2
  Sidon sets.
Related: Problem 1088 (higher-dimensional generalization).
Status: OPEN. No formalization exists yet (per the page: "Formalised statement? No").
Related OEIS: A143824.
Your KSS_Proven.lean formalizes exactly the KSS lower bound 
ℓ
(
N
)
≥
1
2
N
ℓ(N)≥ 
2
1
​
  
N
​
 , which is the best-known order result (
N
1
/
2
≪
ℓ
(
N
)
N 
1/2
 ≪ℓ(N)). The open question — whether 
ℓ
(
N
)
∼
N
ℓ(N)∼ 
N
​
  (i.e., the constant approaches 1) — remains unresolved in the literature.


What's known:

Upper bound: $\ell(N) \leq (1+o(1))\sqrt{N}$ (from $A = {1,\ldots,N}$)

Lower bound: $\sqrt{N} \ll \ell(N)$ (KSS 1975), though the exact constant remains unknown and the conjecture is $\ell(N) \sim \sqrt{N}$

A Lean formalization of the KSS lower bound exists with one axiom remaining

This is an open problem in combinatorial number theory that's resisted solution for roughly fifty years, so I can't prove new mathematics that doesn't exist in the literature—I need to be honest about that limitation.

What I can realistically accomplish is removing the remaining axiom to complete the formal proof of the KSS bound, formalizing the upper bound direction, providing computational evidence through available tools, and offering a thorough analysis of the problem. Looking back at the problem statement though, it asks to determine the order of $\ell(N)$, which is actually known: $\ell(N) = \Theta(\sqrt{N})$ follows from the KSS lower bound and the trivial upper bound.

The open question is whether $\ell(N) \sim \sqrt{N}$ exactly—that is, whether the ratio approaches 1. So the order itself is settled; what remains is pinning down the asymptotic constant. My focus should be on eliminating that axiom from the formal proof, adding the upper bound formalization, and exploring the constant computationally.

For the blocking argument, I need to show that for each element outside a maximal Sidon set, I can assign it to a pair in the set that witnesses why it's blocked—either through a Type 1 sum relation or a Type 2 doubling relation—and that the fibers of this assignment stay bounded.

The constraint comes from the structure of these relations: a Type 2 element can only correspond to one pair (since $2x = a + b$ determines $x$ uniquely), while Type 1 elements corresponding to the same pair $(a,b)$ must satisfy $x = a + b - c$ for different choices of $c \in S$, which limits how many can exist before violating the Sidon property. For Type 1 elements, each $x \in A \setminus S$ satisfies $x = a + b - c$ for some $a, b, c \in S$, and I can bound the number of such representations by considering how many distinct values this map produces from $S^3$. I need to reconsider the charging argument more carefully. The key is that the specific map $f$ assigns each element $x$ to some pair $(a,b)$, and I can show that at most two elements map to any given pair by noting that for a fixed pair, at most one element can satisfy the Type 2 condition (where $2x = a + b$), leaving room for at most one Type 1 element as well. For a third element, if it's Type 2 then $x_3 = (a+b)/2$, but if it's Type 1 with $x_3 + c_3 = a + b$, then $c_3$ must equal either $c_1$ or $c_2$ (otherwise we'd have three distinct elements of $S$ summing to $a+b$, which leads to a contradiction). I need to verify that $x_2$ isn't in the modified set, since $x_2 \notin S$ and inserting $x_1$ doesn't add $x_2$, which means these four elements can't all belong to the same set—contradicting the assumption that they produce equal sums.

Rather than continuing down this path, I should reconsider the approach entirely. The KSS argument is more subtle than a direct application of the Sidon property, so I need to examine their actual strategy more carefully, particularly the concrete plan outlined in the workspace about defining a canonical witness selector and proving the fiber bound. and $x_2 + c_2 = a + b$ with $c_1, c_2 \in S$. From $x_1 + c_1 = x_2 + c_2$ and $x_1 \neq x_2$, I get $c_1 \neq c_2$. For the third element, if $x_3$ is Type 2 then $2x_3 = a + b = x_1 + c_1$, which means ${x_3, x_3}$ and ${x_1, c_1}$ both sum to the same value, creating a contradiction with the injectivity requirement. The Sidon property requires ${a,b} = {c,d}$ as sets when $a + b = c + d$, so $x_3 + x_3 = x_1 + c_1$ would violate this only if all four elements were in $S$, but they're not since $x_3 \notin S$. For Type 1 collisions, I need to consider when $x_3 + c_3 = a + b$ where $c_3 \in S$ and $c_3 \neq c_1$.

The key insight is that if all three collisions are Type 1, then $x_1 + c_1 = x_2 + c_2 = x_3 + c_3$, which gives me the difference equations $x_1 - x_2 = c_2 - c_1$ and $x_1 - x_3 = c_3 - c_1$.

For the canonical map, I assign each $x$ to the lexicographically smallest pair $(a,b)$ that blocks it, and this lex-smallest condition should prevent certain collision patterns from occurring simultaneously.

But I'm realizing this approach ties the argument too tightly to the specific canonical choice. Instead, I can use a much more direct counting argument: every element in $A \setminus S$ can be expressed as $a + b - c$ for some $a, b, c \in S$, which immediately gives a bound on how many such elements exist based on the size of $S$. For each element outside $S$, maximality of the Sidon set forces a collision involving that element, which must take one of two forms: either it's the sum of two elements in $S$, or it appears in a sum equation with elements from $S$.

Type 2 elements (those equal to half a sum from $S$) map injectively to $S + S$, giving at most $|S|^2$ such elements. For Type 1 elements, I need to bound those satisfying $x + c = a + b$ for some $a, b, c \in S$ by analyzing how many elements can map to each fixed $c$. The map $x \mapsto (\sigma, c)$ where $\sigma = a+b$ is injective into $(S+S) \times S$, giving a cubic bound, but I need to leverage the Sidon property more effectively. Let me reconsider the approach used in the KSS paper. For each element $x$ in $A \setminus S$, I can find at least one $c \in S$ such that $x + c$ lies in $S + S$, giving me a set of evidence pairs $(x, c)$ with size at least $|A \setminus S|$. Counting these pairs differently by fixing $c$ and using the injectivity of translation, I can bound how many elements of $A \setminus S$ map into $S + S$ under the shift by $c$.

Since $|S + S| \leq |S|^2$, the total number of evidence pairs is at most $|S|^3$, which yields the bound $|A \setminus S| \leq |S|^3$ for Type 1 elements. This cubic bound combined with the Type 2 analysis gives $|S| \geq |A|^{1/3}$, which is Erdős's original result. The stronger $|A|^{1/2}$ bound that KSS achieved requires a more refined charging argument that exploits the structure more carefully.

The key innovation is establishing that each pair $(a, b) \in S \times S$ can be the canonical collision witness for at most 2 elements from $A \setminus S$. To prove this, suppose three elements $x_1 < x_2 < x_3$ all map to the same pair $(a, b)$, and analyze what constraints this places on their types and the structure of the sum-free set. I have $x_1 + c_1 = x_2 + c_2$ where $c_1, c_2$ are in the Sidon set $S$ but $x_1, x_2$ aren't, so I can't directly apply the Sidon property to conclude anything about these four elements.

Let me think about what happens if there's a third Type 1 element $x_3$ with $x_3 + c_3 = a + b$ where $c_3 \in S$ and $c_3$ is distinct from both $c_1$ and $c_2$—then I'd have three equations all equal to $a + b$, which might give me a contradiction or constraint. I'm deriving relationships between the differences of the x values and c values, then recognizing that if three distinct elements all map to the same pair, I need to find a contradiction by examining what constraints this places on their structure. The pairwise sums of the $c$ values are all distinct by the Sidon property, and I can express each sum $x_i + x_j$ in terms of $\sigma$ and the corresponding pair sum from $S$, which gives me a system of constraints to work with. The pairwise sums being distinct doesn't actually help us here since we're not trying to show the $x_i$ form a Sidon set. I need to step back and think about this differently—maybe I can avoid the 2-to-1 charging argument altogether and find a weaker bound that still works, or use a direct approach based on the Sidon structure to bound the blocked elements. I'm trying different injection strategies to bound the Type 1 elements, but mapping to $c_x$ alone or to pairs still yields cubic bounds. Let me explore whether directly mapping to $(a_x, b_x)$ gives a better result. can't directly apply Sidon. But if $c_1 \neq c_2$, then $c_1 + x_1 = c_2 + x_2$ with $c_1, c_2 \in S$ distinct means the Sidon property forces $x_1 = x_2$, so different blocked elements for the same sum must come from the same $c \in S$. Each sum $\sigma$ in $S + S$ corresponds to at most $|S|$ Type 1 elements, giving an upper bound of $|S|^3$ through direct counting, but this cubic bound suggests the 2-to-1 mapping argument is crucial for improvement. I need to carefully construct this map and establish the fiber size bound to break through the cubic barrier.

The key insight is charging each blocked element to its canonical collision pair $(a, b)$ and proving each pair receives at most 2 charges. The challenge is that a single sum $\sigma = a + b$ can arise from multiple witness triples with different $c$ values, potentially creating more than 2 blocked elements per pair. However, with careful analysis of Type 1 and Type 2 elements for a fixed ordered pair, this might still be manageable. I need to show that at most two elements can charge to the same canonical pair $(a,b)$ by proving that a third element $x_3$ would necessarily have a lexicographically smaller witness pair, contradicting the assumption that $(a,b)$ is canonical for it. Since $x_3 = \sigma - c_3$, I can substitute to get $x_3 + c_1 = \sigma - c_3 + c_1$ and $x_3 + c_2 = \sigma - c_3 + c_2$, and I need to check whether these values themselves decompose as sums from $S + S$, which would give additional collision witnesses for $x_3$. Since $x_3 \notin S$, we have a collision in $S \cup {x_3}$ where $x_3 + c_1 = a' + b'$ with $a', b' \in S$, but the pair $(a', b')$ isn't necessarily lex-smaller than $(a, b)$, so this approach is getting unwieldy. I should step back and focus on what I can actually verify with the tools at hand rather than trying to reconstruct the full argument from scratch. I'm reconsidering the proof strategy by splitting the bound into Type 1 and Type 2 elements separately, where Type 2 is already handled but Type 1 requires a different approach. The challenge is bounding the Type 1 only elements by |S|², so I'm exploring whether the collision graph structure itself might provide the key insight. Let me try a direct counting argument instead: for each blocked element $x \in A \setminus S$, I'll fix a specific collision witnessing why it can't be added, then count how many elements can share the same collision to bound $|A \setminus S|$. Each sum in $S + S$ can be formed by at most one Type 2 element and at most $|S|$ Type 1 elements, giving an upper bound of $|S|^2(1 + |S|)$ total pairs, which yields only the weaker bound $|S| \geq |A|^{1/3}$—so I need the 2-to-1 argument to achieve the $|A|^{1/2}$ bound.

Now I'm formalizing the key lemma: for a Sidon set $S$ and a disjoint set $B$, every element of $B$ is either a Type 1 element (satisfying $x + c = a + b$ for some $a, b, c \in S$ with $x \neq (a+b)/2$) or Type 2 (satisfying $2x = a + b$ for some $a, b \in S$), and I'll assign each element a canonical pair from $S \times S$ to establish the 2-to-1 map.

To prove the core claim that each pair in $S \times S$ has at most 2 preimages in $B$, I'm assuming three distinct elements $x_1, x_2, x_3$ all map to the same pair $(a,b)$ and deriving a contradiction by analyzing their types.

Since at most one element can satisfy $2x = a + b$, at least two must satisfy $x + c = a + b$ for some $c \in S$, and if $x_1, x_2$ are both Type 1 with different $c$ values, then $x_1 \neq x_2$ follows from the distinctness of their complements.

For the third element $x_3$, I need to check whether it's Type 2 (the midpoint case) or Type 1, which will lead to a contradiction in either scenario. I'm realizing the Sidon property only constrains pairs within $S$ itself, so this collision between $x_1$, $c_1$, and $x_3$ doesn't directly violate it. But if $(a,b)$ has three preimages—two Type 1 elements and one Type 2—that contradicts the claim that each fiber has size at most 2. For this to work, I need $a + b$ to be even so that $x_3 = (a+b)/2$ is an integer, and I need $x_3$ to be distinct from both $x_1$ and $x_2$ and not already in $S$. Let me test with $S = {0, 1, 3}$, which is Sidon, and $a = 1, b = 3$ giving $\sigma = 4$—this gives $x_3 = 2$, which isn't in $S$.

For Type 1 with $c_1 = 0$, I get $x_1 = 4$, which works since it's not in $S$. But with $c_2 = 1$ or $c_2 = 3$, I get $x_2 = 3$ or $x_2 = 1$ respectively, both of which are already in $S$, so neither can be added to $A \setminus S$.

With $(a,b) = (1,3)$ and $\sigma = 4$, the constraint that elements must avoid $S$ means I can only construct $x_1 = 4$ from Type 1 and $x_3 = 2$ from Type 2, giving a fiber of size 2 instead of 3.

Let me test this with a larger Sidon set like $S = {0, 1, 5, 11}$ where $a = 5$, $b = 11$, and $\sigma = 16$, checking what Type 2 elements I can generate.

For Type 1 with different values of $c$, I get valid elements at $x = 16$ and $x = 15$, but $c = 5$ and $c = 11$ produce values already in $S$, so they're excluded. Combined with the Type 2 element $x = 8$, this gives me three valid preimages mapping to the pair. I need to check what pairs in $S \times S$ sum to 16 to find witnesses for $x_1 = 16$, and verify whether Type 2 blocking (where $2 \cdot 16 = 32$) is possible—but 32 isn't in $S + S$, so that rules it out.

For $x_2 = 15$, I'm checking if 30 can be expressed as a sum of elements from $S$, and examining all possible values of $c$ to see if $15 + c$ yields any valid pairs. For $x_3 = 8$, I need to check if $8 + c = a + b$ for various values of $c$ in $S$. Since $16 = 5 + 11$ is in $S+S$, a Type 2 mapping is possible, but checking $c = 0, 1, 5, 11$ shows none of these produce sums in $S+S$, so 8 can only map to $(5, 11)$.

All three blocked elements map to the same pair $(5, 11)$, which would give a fiber of 3—this seems to violate the axiom. Let me verify whether $S = {0, 1, 5, 11}$ is actually maximal Sidon in $A = {0, 1, 5, 8, 11, 15, 16}$ by checking if adding any element from $A \setminus S$ would break the Sidon property. I need to check whether the three elements outside $S$ can be distributed across the fiber constraint by mapping some to $(5, 11)$ and others to $(11, 5)$, since these are distinct ordered pairs in $S \times S$ even though they contain the same elements. I'm realizing the axiom is essentially just asserting that |A \ S| ≤ 2|S|² by requiring the existence of some function with bounded fibers, which is equivalent by pigeonhole principle—though this feels somewhat circular since that's exactly what we're trying to prove. The axiom essentially encodes the cardinality bound $|A \setminus S| \leq 2|S|^2$, so I need to derive this bound directly from the Sidon property using a charging argument grounded in the mathematical structure rather than an arbitrary function. My counterexample shows the bound holds with room to spare, but the challenge is constructing the right map from the Sidon property itself.

Let me try a different approach using double-counting: I'll define a collision set pairing elements of $A \setminus S$ with elements of $S$ based on which sums they obstruct, then count these pairs to bound how many blocked elements can exist. The bound becomes $|A \setminus S| \leq |S+S| \cdot (1 + |S|)$, which for Sidon sets gives a cubic upper bound, but the key insight is that different sums $\sigma_1$ and $\sigma_2$ can produce the same blocked element $x$ through Type 1, so I'm overcounting.

For a fixed $x \in A \setminus S$, the number of pairs $(\sigma, c)$ where $x + c = \sigma$ is bounded by how many $c \in S$ satisfy $x + c \in S + S$, which determines the actual multiplicity of each element in the count. Subtracting these equations gives a constraint involving six elements of $S$, but the Sidon property only controls pairwise sums, so I can't bound the overcounting to a constant. I think the KSS argument is too intricate to reconstruct rigorously here, so I should shift approaches and try to work around the axiom rather than eliminate it entirely.

My plan is to verify the current proof compiles, compute $\ell(N)$ for small values using constraint solvers, analyze the structure with graph tools, and attempt to formalize the construction in Lean—maybe leveraging proof search tactics to handle the case analysis.

Looking more carefully at the axiom, I see it's asserting that for any maximal Sidon set $S$ within $A$, there exists a two-to-one map from $A \setminus S$ into $S \times S$, which fundamentally bounds $|A \setminus S| \leq 2|S|^2$, so I should explore a different proof strategy that avoids the intricate formalization.

Instead, I'll leverage the Sidon sumset structure directly: elements in $A \setminus S$ either satisfy $2x = a_x + b_x$ for some pair in $S \times S$ (Type 2), or $x + c_x = a_x + b_x$ for some $c_x \in S$ (Type 1 exclusive). Type 2 elements are bounded by $|S|^2$ since they correspond to sumset pairs, and for Type 1, each element $x$ maps to a residue class $(S + S) - c_x$ for some fixed $c \in S$, which I can use to establish the remaining bound. If $x$ belongs to both $T_{c_1}$ and $T_{c_2}$ for distinct $c_1, c_2$, then $x$ has representations in $S+S$ for both shifts, which by the Sidon property gives us $(a_1 + b_1) - (a_2 + b_2) = c_1 - c_2$. For Type 1 elements specifically, the constraint that $x \neq (a+b)/2$ means $x \neq c$, which might limit how much overlap can occur across different $T_c$ sets.

Rather than continuing this algebraic path, I should try a more direct computational approach: use the Lean proof assistant to check the current state and attempt to construct the map explicitly, while simultaneously running a computational verification on small cases with OR-Tools to build intuition about whether the bound holds and where the key constraints matter. For my specific counterexample, I can construct a mapping where each fiber has size at most 2, confirming the statement holds—it just requires choosing the right function. So instead of relying on a canonical map, I should directly prove that $|A \setminus S| \leq 2|S|$ without assuming any particular mapping structure.

I'm thinking about this combinatorially: each blocked element in $A \setminus S$ creates at least one collision sum in $S + S$, and by the Sidon property, each sum corresponds to exactly one unordered pair from $S$, which constrains how many elements can be blocked. For a Sidon set, the $\binom{|S|}{2}$ off-diagonal sums each appear exactly twice, the $|S|$ diagonal sums each appear once, and crucially, diagonal sums never equal off-diagonal sums since $2a = b + c$ would require $b = c = a$ by the Sidon property.

This gives $|S + S| = \binom{|S|+1}{2}$. For blocked elements, Type 2 elements correspond to realized sums $2x$ in $S + S$, so there are at most $\binom{|S|+1}{2}$ of them. Type 1 elements have the form $x = \sigma - c$ where $\sigma$ is a realized sum and $c \in S$, and each Type 1 element can be associated with at least one such pair.

Since there are roughly $|S|^3/2$ total pairs $(\sigma, c)$ from $(S+S) \times S$, I need to show that each Type 1 element accounts for many pairs to reduce the count from $|S|^3$ down to $|S|^2$. For a fixed Type 1 element $x$, I'm counting how many pairs $(\sigma, c)$ satisfy $x + c = \sigma$ by checking, for each $c \in S$, whether the resulting $\sigma$ lies in $S + S$.

The problem is that some Type 1 elements might only have this property for a single $c$, giving multiplicity 1 and leaving me stuck with a cubic bound. I keep running into the same obstacle—the KSS 2-to-1 argument seems unavoidable and I can't find a way around it.

Let me take a more practical approach: verify the existing proof in Lean, attempt progress on the axiom using Lean tactics, compute $\ell(N)$ values with constraint solving, and get a clearer sense of what's actually provable versus what remains open.

Actually, there might be another angle entirely. Instead of the map-based argument, what if I bound $|A \setminus S|$ through a graph coloring approach? I'd construct a blocking graph on the elements outside $S$ where two elements connect if they share a witnessing sum, then analyze the structure of this graph to constrain the size of $A \setminus S$.

The probabilistic method doesn't seem to work here—choosing a random map and bounding expected fiber sizes just circles back to the inequality I'm trying to prove. Let me instead explore whether each blocked element determines a specific triple structure that relates to Sidon sets, which might give a tighter combinatorial constraint. Since $x = (a_x + b_x)/2$ is uniquely determined by the pair, $\psi$ is injective and Type 2 elements are bounded by $|S|^2$. For Type 1, while the map to pairs might not be injective (since different values of $c$ give different $x$ for the same pair), including the witness $c$ itself makes the map to triples injective, so I need to verify that distinct elements can't share the same canonical triple.

The real insight is that the KSS bound of $2|S|^2$ is tight compared to the naive $|S|^3$ bound—achieving the quadratic improvement requires the clever 2-to-1 charging argument that deeply exploits Sidon set structure, and I don't see a way around using that key technique.

Now I need to formalize the KSS construction by defining a canonical pair selector for each element in $A \setminus S$ that picks the lexicographically minimal witnessing pair, then verify this map is well-defined and has the required 2-to-1 property.

For the fiber size argument, I'll assume three distinct elements map to the same pair and derive a contradiction by noting that at most one can satisfy the doubling condition, forcing the others into a configuration that violates the structure of $S$. I'm checking whether the collisions from $x_1$ and $x_2$ give me an alternative witness pair for $x_3$, but computing $x_3 + c_1$ doesn't land in $S + S$, so I need to search for a different pair $(a', b')$ that works.

In Case 2, I'm exploring what happens if $x_3$ itself satisfies the blocking condition with a third element $c_3 \in S$ distinct from $c_1$ and $c_2$.

This gives me three equations all equaling $a + b$, which means $x_2 + c_2 = x_3 + c_3$ forms a collision in the relevant set—and I need to determine whether this collision forces either $x_2$ or $x_3$ to have a lexicographically smaller witness pair than $(a, b)$. The issue is that these blocked elements don't interact with each other in ways that create collisions within the expanded sets. Let me try a completely different approach—instead of the lexicographically minimal map, I'll construct an injection by mapping each element directly to one of its witnesses in the sum representation.

For each $x$ outside $S$, I assign it to the smallest $c \in S$ such that $x + c$ lies in $S + S$. The preimage of any fixed $c$ is bounded by $|S + S|$, which gives at most $|S|^2$ elements mapping to each witness. This yields a total bound of $|S|^3$, which is still cubic, but there's something important I'm missing about how these collisions actually work.

Rather than continuing to hunt for shortcuts, I should just work through the KSS argument directly. Let me examine what happens when multiple elements map to the same sum: for a fixed $\sigma \in S + S$, at most one element can be the midpoint $\sigma/2$, while the remaining elements come from pairs $(a,b)$ with $a + b = \sigma$ where $a,b \in S$.

The key constraint is that for Type 1 elements $x = \sigma - c$ to actually lie in $A \setminus S$, we need $\sigma - c \notin S$. But when $\sigma = a + b$ with $a,b \in S$, the values $\sigma - a = b$ and $\sigma - b = a$ are both in $S$, so these two choices of $c$ are automatically excluded.

For any other $c \in S$ with $c \neq a, b$, if $a + b - c$ were in $S$, say equal to some $d \in S$, then we'd have $a + b = c + d$. By the Sidon property, this forces ${a,b} = {c,d}$, which contradicts $c \neq a$ and $c \neq b$. Therefore $\sigma - c \notin S$ for all $c \in S \setminus {a,b}$. So for any $c \in S \setminus {a, b}$, we have $a + b - c \notin S$, while the cases $c = a$ and $c = b$ give us elements already in $S$ that are excluded from Type 1 by definition. This means Type 1 elements are exactly those of the form $\sigma - c$ where $c$ ranges over $S \setminus {a, b}$, and there are $|S| - 2$ such elements. The number of possible sums is roughly $|S|^2/2$, and with at most $|S|-1$ blocked elements per sum, the total count reaches cubic complexity. I've established that $a + b - c \notin S$ for distinct elements, which prevents collisions within $S$ itself, but this doesn't reduce the overall count. The key constraints are that Type 2 elements (midpoints of sums) contribute at most $|S|^2$ blocked values, while Type 1 elements (differences from sums) are bounded by the structure of $S$. For each blocked element $x$, I need to count how many pairs $(\sigma, c)$ map to it—that is, how many $c \in S$ satisfy $x + c \in S+S$. This is equivalent to asking how many translates of $S+S$ contain $x$, which bounds the overcounting factor. When $x + c_1 = a_1 + b_1$ and $x + c_2 = a_2 + b_2$ for different elements $c_1, c_2 \in S$, subtracting these equations gives $c_1 - c_2 = (a_1 + b_1) - (a_2 + b_2)$, meaning the sums $x + c$ for different $c \in S$ are all distinct and each corresponds to a unique difference in $S + S$.

The key insight is that the intersection of the shifted set $x + S$ with $S + S$ determines how many representations exist, but for random $x$ this intersection is typically small (around $|S| \cdot |S+S| / M$), while adversarial choices of $x$ could make it as large as $|S|$. Since this approach doesn't seem to lead anywhere without a fundamentally different strategy, I'll move forward by checking the Lean proof status and attempting to remove the axiom dependency.

My concrete plan is to construct the charging map in Lean, compute $\ell(N)$ for small values using constraint satisfaction optimization, analyze the collision structure with graph algorithms, and present the results. The main computational challenge is determining exact values of $\ell(N)$ for $N$ up to around 50, which requires either enumerating all sets of that size or using optimization techniques—though computing this exactly is quite difficult since it involves minimizing over all possible sets.

For a given set $A$, finding the maximum Sidon subset is computationally tractable via constraint satisfaction, and I can use the known bounds: the upper bound comes from $F_2(N)$, the maximum Sidon subset size in ${1, \ldots, N}$, while the lower bound follows from the KSS result giving $\ell(N) \geq c\sqrt{N}$.

Since this is an open problem in combinatorics, I can't fully resolve it, but I can complete the formalization by removing the axiom if possible, provide computational evidence for specific values of $N$, and establish the foundational framework for future work. Let me start by verifying the Lean proof compiles, then attempt to eliminate the axiom, and finally compute concrete bounds on $\ell(N)$.

For the axiom removal, I'm exploring whether I can prove the bound $|A \setminus S| \leq 2|S|^2$ directly using a map-based argument. The key idea is to define a function that assigns each element in $A \setminus S$ a canonical pair from $S$, then show each pair has at most 2 preimages. I'll follow the approach outlined in the file: construct the map using lexicographically smallest pairs, then verify the fiber size bound. For each element in $A \setminus S$, I can classify it as either Type 1 (satisfying $x + c = a + b$) or Type 2 (satisfying $2x = a + b$), then construct an injection by mapping Type 2 elements to pairs with a marker and Type 1 elements to triples from $S \times S \times S$, giving a total codomain size of at most $2|S|^2$. The codomain becomes $S \times (S+S)$ with size at most $|S|^3$, which is still cubic and doesn't help. The real issue is that Type 1 triples can't be reduced to pairs without either breaking injectivity or inflating the count—the KSS approach of bounding fibers by 2 is the key insight that makes this work. I need to formalize this by fixing a sum $\sigma = a + b$ and defining the set of all $x \in A \setminus S$ where $x + c = \sigma$ for some $c \in S$. The counterexample shows that $|T_{16}| + [u_{16} \text{ exists}] = 3$, which violates the bound of 2, so the canonical sum assignment alone won't establish the desired inequality. I need to find a more sophisticated assignment strategy where each element in $A \setminus S$ maps to multiple pairs rather than just one. I need to reconsider the axiom more carefully—the function $f$ simply needs to map blocked elements into $S \times S$ with fibers of size at most 2, with no constraint relating $f(x)$ to any blocking structure of $x$. This means any such function satisfying these cardinality conditions will work.

The axiom is therefore equivalent to the simple cardinality bound $|A \setminus S| \leq 2|S|^2$: I can construct the required function by pairing up elements of $A \setminus S$ and mapping them to elements of $S \times S$, and conversely the axiom forces this bound to hold.

Rather than proving the existence of a two-to-one map, I should directly establish the cardinality bound as a lemma and derive the rest from there, which might sidestep some of the axiom-related complications.

To prove this bound, I'll partition the elements outside S into those that can be expressed as half-sums of S elements (Type 2) and those that can't (Type 1), then bound each part separately—the Type 2 bound follows from the sumset size, but bounding Type 1 elements is where the real difficulty lies.

For Type 1 elements, I'm constructing a map from these elements into S + S by sending each element to the sum it witnesses, but since this map isn't injective, I need to carefully count the preimages to establish that there can't be too many Type 1 elements. If the witnesses are identical, then $g$ is injective on that fiber, but different witnesses create collisions. For any element $\sigma$ in the image, the fiber $g^{-1}(\sigma)$ consists of elements $x = \sigma - c_x$ where each $c_x$ is uniquely determined by $x$, so different elements in the fiber must have different witnesses. I need to clarify what $c_x$ actually represents: it's the smallest element in $S$ such that adding it to $x$ produces a sum in $S + S$, and I'm trying to understand whether this $c_x$ must equal $\sigma - x$ for a given $\sigma$.

Now I'm defining a function $g$ that maps each $x$ to $x + c_x$, and I want to show this function is injective by considering what happens when two inputs produce the same output—if $c_{x_1} = c_{x_2}$ then clearly $x_1 = x_2$, but the harder case is when the witnesses differ, which would force a contradiction. Since $c_{x_1}$ is smaller than $c_{x_2}$ but $x_2 + c_{x_1} \notin S + S$, it's not a valid witness for $x_2$, which is consistent with $c_{x_2}$ being minimal—but this doesn't lead to a contradiction, so the injectivity claim fails in general.

For a fixed sum $\sigma$, the fiber $g^{-1}(\sigma)$ consists of pairs $(x, c_x)$ where $x = \sigma - c_x$ and $c_x$ is the smallest valid witness for $x$, meaning different elements in the fiber correspond to different witness values. I keep arriving at cubic bounds no matter the approach. Let me try a completely different angle using graph theory instead—I'll construct a bipartite graph where blocked elements connect to Sidon set elements that witness their membership in $S + S$, and analyze the edge structure to get a better bound on Type 1 elements. If each Type 1 element has degree at least 2, then $|T_1'| \leq |E|/2 \leq |S|^3/2$, but I need to verify whether every such element actually has a second witness $c_2 \neq c_1$ with $x + c_2 \in S + S$.

A counterexample shows this isn't guaranteed: taking $S = {0, 1, 5, 11}$ and $x = 16$, we get $16 + 0 = 16 \in S + S$ as a witness, but $16 + 1, 16 + 5, 16 + 11$ all fall outside $S + S$, so $x$ has exactly one witness.

Since the graph-theoretic degree approach can't guarantee degree at least 2, I can't improve beyond the cubic bound. The KSS charging argument with the canonical pair selector appears to be the most direct path: defining a map from $A \setminus S$ into $S \times S$ by selecting the lexicographically minimal witnessing pair for each element, then showing each pair has at most 2 preimages by deriving a contradiction if three elements share the same pair.

Rather than fully formalizing this intricate case analysis in Lean, I'll focus on verifying the existing proof, computing $\ell(N)$ values computationally, and documenting what progress can be made on the axiom itself.

For the computational experiments, I'll use constraint satisfaction tools to find maximal Sidon subsets for various set sizes, compute $\ell(N)$ for small values by exhaustively minimizing over all possible sets, validate the bound $|A\S| \leq 2|S|^2$ empirically, and analyze the structure of collision graphs across different configurations.

I should prioritize what's actually feasible: checking the Lean proof with MCP tools, running CP-SAT computations to explore $\ell(N)$, and attempting to eliminate the axiom using Lean's tactic suggestions on the proof structure.


Now I have the complete picture. Let me plan the fix.

The key issue: The axiom kss_two_to_one_map_exists at line 488 is mathematically false. It claims that for ANY finite A and any maximal Sidon S ⊆ A, there exists a 2-to-1 map from A\S to S×S. This is equivalent to |A\S| ≤ 2|S|², which fails for spread-out Sidon sets where |A\S| can be Θ(|S|³).

The fix strategy:

Option A: Remove everything that depends on the false axiom, keep only axiom-free results.

This would mean stripping out the AdmitsTwoToOneMap definition, the false axiom itself, and all downstream lemmas and theorems that rely on it—leaving only the axiom-free results like blocking_bound_cubic and axiom_free_cube_bound. The downside is losing the √N bound entirely, which is the main result we're after.

Option B: Restrict the axiom to interval sets A =

I'm verifying computationally that for A = {1,...,N}, the counting condition |A\S| ≤ 2|S|² holds up through N=25+. This is relevant because ℓ(N) is defined as the minimum over all N-element sets of the maximum Sidon subset size, so to prove ℓ(N) ≥ (1/2)√N, I need to show that every N-element set contains a Sidon subset of that size—but actually, I only need to show it for one specific set to get a lower bound on ℓ(N).

Wait, I'm confusing myself. Let me reconsider the definition: ℓ(N) is the largest value such that any finite set of size N contains a Sidon subset of size ℓ(N). So to establish a lower bound, I need to prove that for all sets A with |A| = N, there exists a Sidon subset of size at least (1/2)√N. Restricting to intervals won't work for the main theorem because I need the result to hold universally.

Looking back at the KSS paper, Lemma 2 actually does establish that |A\S| ≤ 2|S|² for any finite set A and maximal Sidon subset S. The issue isn't that the lemma is false—it's that my formalization of what the "2-to-1 map" condition means doesn't quite capture what the proof actually shows. The mathematical content is sound, but the specific way I've encoded the condition needs adjustment. So our counterexample actually does work—S is maximal Sidon in A with |A\S| exceeding 2|S|²—which means either the KSS paper's Lemma 2 proves something more restrictive than we thought, or there's an error in our analysis of what they're claiming. I suspect their result applies under different assumptions or definitions than what we're working with.

Let me trace through the blocking condition more carefully: for x to be blocked, adding it to S must create a sum collision where a + b = c + x for some elements in S.

This breaks into two cases—either x combines with an existing element to match a sum of two existing elements, or x appears in a sum that equals twice another element. For the first case, x can be expressed as the difference of two sums from S, giving at most 343 possible values, though many would be negative or duplicates.

The second case is simpler: x would be the average of two elements from S, yielding at most 49 candidates. Combined, we're looking at roughly 392 potential blocked values, but the real question is how many distinct ones actually fall outside S itself. The Python script testing this found a concrete counterexample with S as powers of 10 up to 10^6, where the blocked set exceeds the theoretical bound of 98.

This suggests either the KSS paper is claiming something different than what we've formalized, or there's a gap in the proof. The paper might be working over integers rather than naturals, or applying additional constraints we haven't accounted for. But the core issue remains: the axiom as currently stated in the Lean file doesn't hold.

The real question is what fix makes the most sense. Since we've shown the false axiom doesn't generalize, but we can prove a weaker bound of |A\S| ≤ |S|² + |S|³ without any axioms, the cleanest path forward is removing the false axiom entirely and keeping only the axiom-free results—we'd lose the √N bound but retain the proven ∛N bound with complete mathematical integrity.

Now I'm wondering if we can actually tighten the Type 1 bound below |S|³ by leveraging the Sidon property more carefully. For Type 1 elements, we have x + c = a + b where a, b, c are all in S and x isn't Type 2, meaning x = a + b - c for some choice of these elements. Let me explore whether this structure gives us something stronger. = a'+b'+c₁. This doesn't directly help.

I'm trying a different approach: mapping each Type 1 element x to the pair (a+b, c) where a+b is the sum and c is the witness. Since x = (a+b) - c, this mapping is injective, but the domain size is still bounded by |S+S| · |S|, which gives the same cubic bound. For each sum σ = a+b, I showed there are |S|-2 Type 1 elements, not just one, so that doesn't tighten things. But here's an interesting observation: for each c ∈ S, the shift map x ↦ x+c sends all Type 1 elements with witness c into S+S, and this map is injective.

So the Type 1 elements with witness c are bounded by |S+S| ≤ |S|², and summing over all possible witnesses gives |Type 1| ≤ |S|³. The problem is that elements can have multiple witnesses, causing overcounting. My counterexample shows the true count can exceed 2|S|², so no quadratic bound is achievable with this approach. This suggests the cubic bound is the best I can prove for general sets, and the √N bound from the KSS paper must rely on something deeper than just the blocking argument. I'm realizing there's a gap between what I can prove here and what the paper actually establishes.

Looking more carefully, the KSS paper likely uses an iterative or greedy strategy rather than a single application of the maximal Sidon subset plus blocking argument. The key claim that |A\S| ≤ 2|S|² for any maximal Sidon S in A appears to be false based on my counterexample, so either the paper uses a different technique or there's a subtlety I'm missing about how the argument actually works.

Wait, I should double-check whether my proposed set S is actually maximal Sidon in A. Maximal means no element from A\S can be added while preserving the Sidon property—it doesn't mean S is the largest Sidon subset of A. Let me verify that S is truly maximal in this sense.

Since S = {1, 10, 100, ..., 10^6} is Sidon and every element in A\S was specifically constructed to break the Sidon property when added, S is indeed maximal Sidon in A. And I've confirmed that |A\S| = 106 exceeds 2|S|² = 98, which contradicts the axiom.

So the axiom is false. Now I need to figure out whether the actual KSS paper claims something different or if there's an error in my reasoning. The next step is to remove the false axiom and reconsider what the paper actually proves.

Maybe the KSS paper doesn't use the maximal Sidon approach at all—they could be using a probabilistic argument, greedy construction, or some other technique entirely to establish the √N bound.

Looking at the summary though, it does seem to describe exactly the maximal Sidon approach: find a maximal Sidon subset S, then use a blocking bound to show |A| ≤ O(|S|²), which gives |S| ≥ Ω(√|A|). But we've shown this blocking bound fails for general sets, so either the KSS paper proves something different, there's a subtlety we're missing, or our counterexample is actually flawed. Let me trace through the counterexample one more time with S = {1, 10, 100, 1000, 10000, 100000, 1000000}.

For Type 1 blocked elements where x = a + b - c with a,b,c ∈ S, I can verify that inserting x actually does break the Sidon property. Take x = 109 = 10 + 100 - 1: adding 109 creates the collision 109 + 1 = 110 = 10 + 100, so {109, 1} and {10, 100} both sum to 110, violating the Sidon condition.

Now I'm counting how many distinct values of the form a + b - c exist for S = {1, 10, 100, 1000, 10000, 100000, 1000000}. With 343 possible triples and exponentially spread values, there are very few collisions among the resulting sums, giving roughly 106 distinct non-negative non-S values. This convinces me the axiom is false.

I need to remove the false axiom and everything built on it—the two-to-one map definition, the related lemmas, and the sqrt bound theorem—then promote the axiom-free cubic bound as the main result and add documentation explaining the changes.

I'm also wondering if we can tighten the cubic bound further, particularly for interval sets where experiments suggest |A\S| ≤ 2|S|² might hold, which would give us the sqrt bound for the specific case of {1,...,N}. That's worth exploring separately though.

For now, the immediate task is straightforward: remove the false axiom and its dependents, keep the cubic bound as the main result, and update the documentation. I should also add a cube-root theorem statement to match the structure of the sqrt bound result. The file structure stays mostly intact through the blocked element form and sumset sections, but I need to carefully handle the KSS charging argument section where the axiom lives.

Let me trace through the exact line ranges to identify what stays and what goes, checking dependencies as I work through the file. I'm identifying which sections to remove from the formalization and what to replace them with. The key is replacing the removed axiom-dependent proofs with a clean statement of the main theorem using the cubic bound that's already proven: for any finite set A, there exists a Sidon set B where 3|B|³ ≥ |A|. I'll need to update the documentation and axiom verification section accordingly. Finishing the theorem proof...

Now I'm going through the file structure to identify what needs to stay and what to remove. The sidon_sumset_card_le_sq lemma stays, but I need to strip out the entire 4.3 section covering the KSS charging argument—that includes the AdmitsTwoToOneMap definition, the two_to_one_map_exists axiom, the bound_from_two_to_one lemma, the blocking count bound, and the maximal_sidon_blocking_bound lemma along with its historical note. I'll keep Part 5 and make these edits carefully. I'm trying to pinpoint the exact boundaries of what needs to be replaced. Looking at the file structure, I can see that sidon_sumset_card_le_sq ends somewhere around line 451, and then section 4.3 begins with the KSS Charging Argument header. I need to find where kss_sqrt_bound ends so I know the full extent of the content to remove and replace.

The plan is to remove everything from the 4.3 header through the end of that section, then update Part 6 and the final documentation. I should also update the file header comments to reflect the new structure. I need to replace a large section of the file—everything from the KSS Charging Argument through the end of the sqrt_bound proof—with a single comment. Let me identify the exact line boundaries and execute these edits as a series of string replacements to keep things clean and precise. Now I'm planning the edits I need to make. First, I'll update the header to reflect the new main result—the cubic blocking bound that's axiom-free—replacing the old √N bound that depended on the false axiom. Then I'll remove the entire section about the KSS charging argument since that axiom no longer holds. After that, I'll promote Part 6 to become Part 5 and establish it as the main theorem. Finally, I'll update the documentation to reflect that we've eliminated the axiom dependency.

Let me start by identifying the exact boundaries for each edit so I can do the string replacements carefully. and continues through the exact sqrt bound from the quadratic formula using the cardinality constraints. Then Part 6 shifts to the axiom-free cubic bound matching the Erdős N^{1/3} result.

Now I'm looking at the KSS charging argument from 1975, which establishes that blocked elements can be mapped to pairs in S with bounded fiber size. I'm defining what it means for a set to admit a 2-to-1 map—essentially a function from elements outside S into pairs within S, which is the minimal structure needed for the counting argument. I'm now working through the main blocking bound lemmas that derive the cardinality constraint from the 2-to-1 map existence, establishing that any maximal Sidon set S in A satisfies |A| ≤ |S| + 2|S|². Then I'm moving toward the final theorem that ties everything together to prove the square root bound.

For the remaining work, I need to handle several key transformations: consolidating the axiom-dependent sections into a cleaner structure, promoting Part 6 to Part 5 as the main result, and setting up the final theorem statement that captures the complete bound without relying on unproven axioms. I'm identifying the exact text boundaries for the replacements by locating unique strings like sidon_sumset_card_le_sq and the Part 6 header, then I'll execute a multi-replace strategy to remove the large section, condense it to a note, rename Part 6 to Part 5, integrate the main theorem, and refresh the verification section. I'm looking at the exact line numbers where the replacement needs to happen—the section after sidon_sumset_card_le_sq through the old Part 6 header. I need to identify the precise boundaries: section 4.3 starts around line 455 and I need to find where Part 6 begins so I can replace both the axiom-free cubic bound section and update the header. Let me work through this systematically by reading the exact text at those line numbers, then I'll construct the multi-string replacement to swap out the old content with the new note and updated Part 5 header. the boundaries more carefully by looking at the actual line numbers and content. The section I need to remove starts right after the sidon_sumset_card_le_sq lemma definition and goes through the end of kss_sqrt_bound, stopping just before the Part 6 header. I can identify the exact start and end points by matching the unique text around sumset_card_le_sq S and the closing exact sqrt_bound_from_quadratic statement. I'm looking at the file structure now—the header doc comment spans lines 1-57, followed by imports. Rather than replacing the entire header at once, I should make targeted edits to the title, status section, and axiom listing, though this is getting complicated enough that I might need to reconsider my approach.

Let me map out the specific edits I need to make: updating the main result description, revising the status section, removing the axiom section entirely (which is substantial), renumbering the remaining parts, and updating the axiom verification at the end. I'll need to be precise about identifying the exact boundaries for deletion, particularly for the axiom section—I need to find the exact lines before and after it to remove cleanly. I'm working through the Lean proof structure, identifying sections that need to be refactored. The current thinking shows I'm at a transition point where I need to remove the old axiom-dependent KSS charging argument section and replace it with the new axiom-free cubic bound approach based on Erdős's N^{1/3} result.

Rather than trying to do this in one massive replacement, I'm breaking it into smaller, more manageable chunks—removing the charging argument definition, the axiom declaration itself, and the dependent lemmas one by one. This way each edit is focused and less likely to cause compilation issues. I'm defining the core axiom that formalizes the KSS lemma: for any maximal Sidon set S within a finite set A, there must exist a function from the remaining elements A \ S into pairs from S × S, where each pair in the image has at most 2 preimages. The intuition is that elements outside S are "blocked" by existing sum relationships within S, and this blocking structure can be captured by the 2-to-1 map.

Now I'm moving toward the main result: deriving the cardinality bound from this 2-to-1 map existence...

Proving the blocking bound... Completing the proof by showing the sum of fiber cardinalities is bounded by twice the image cardinality through a calculation, then establishing that the image itself is contained in the Cartesian product of S with itself to bound its size. Now I'm wrapping up the proof by applying the two-to-one map result to establish the blocking bound, casting the cardinality to reals to complete the inequality. Finishing the proof by decomposing the cardinality of A into S and its complement, then applying the blocking bound to show the complement is bounded by 2|S|², which gives us the desired inequality.

Now I'm stating the main KSS theorem: for any finite set A of natural numbers with at least one element, there exists a Sidon subset B contained in A where B's cardinality is at least (1/2)√|A|.

Completing the proof...

Now I'm establishing that the card of S is at least 1, then using the blocking bound to show that the cardinality of A is bounded by 3 times the square of S's cardinality, which gives me the final sqrt bound I need.

Moving into the axiom-free cubic bound section, I'm proving a weaker version that avoids any axioms beyond standard Lean foundations—showing that the number of blocked elements is at most the square plus cube of S's cardinality, which yields the Ω(N^{1/3}) lower bound on the line complexity.

Now I'm planning the refactoring strategy: I'll replace the entire axiom-dependent section (from the KSS charging argument through the end of that part) with a note explaining the removal, then update the section numbering and add the main theorem after the axiom-free bound.

For the multi_replace tool, I need to be precise with the string matching—I'll use the KSS section header as my starting point and include enough surrounding context to make the match unique, ending just before the Part 6 header.

Rather than trying to match the exact boundaries, it might be cleaner to just rewrite the whole file since I'm making substantial changes across multiple sections. But the create_file tool won't let me overwrite an existing file, so I'm stuck with multi_replace for these edits.

The core changes are removing about 150 lines from the axiom section, renumbering Part 6 to Part 5, adding a main theorem statement, and updating the documentation—this is a significant refactor that would be easier to handle all at once.

Let me break the deletion into smaller chunks: first the definition and axiom, then the downstream lemmas, then the historical note and remaining parts. Each chunk should be manageable at 30-50 lines, so I'll use multiple replace_string_in_file calls to handle this systematically. I'm breaking down the axiom section removal into four separate edits to ensure accuracy. Each split will target a specific chunk—starting with AdmitsTwoToOneMap and its related definitions, then moving through bound_from_two_to_one, the blocking bound theorems, and finally the historical note with Part 5. I'll sandwich each target section with three lines of context before and after to keep the edits precise and avoid accidentally removing the wrong content.

But I'm realizing the replacements will cascade—once I remove the first section, the line positions shift, which means the context lines for the second split won't match anymore. I need to think about this more carefully. Let me reconsider using a single multi-replace call with all the non-overlapping chunks at once, processed sequentially so each replacement accounts for the file state after the previous one.

My plan: replace the header with updated content, then swap out the entire axiom section and Part 5 with a brief note, update the Part 6 header to Part 5, and finally insert the main theorem after the end of the KSSProven block.

I'm realizing the replace_string_in_file tool only handles one occurrence at a time, so I need to construct each old string to span the full region I want to replace—including surrounding context lines to ensure uniqueness. The challenge is that some of these regions are quite long, like the axiom section which runs about 150 lines. Let me think through how to break this down into manageable chunks.

I'll start with the header update first, then work through the axiom removal and the section renumbering. For each replacement, I need to be precise about what I'm matching and what I'm replacing it with, preserving the context lines on either side.

Writing the replacement strings... I'm clarifying what this formalization actually establishes: it proves the lower bound direction of Erdős Problem 530, showing that any finite set has a Sidon subset of size at least (1/2)√|A|, but the upper bound and exact asymptotics remain open questions in the literature. √N → 1?)

Note on the constant: We prove c = 1/2, weaker than best-known values. This suffices to establish ℓ(N) = Ω(√N), i.e., the correct order of growth.

Status: ✅ COMPLETE (modulo 1 axiom)
✅ PROVEN: - singleton_isSidon: Singleton sets are Sidon - exists_maximal_sidon: Maximal Sidon subsets exist (finite maximality) - maximal_sidon_nonempty: Maximal Sidon subsets are nonempty - sqrt_bound_from_quadratic: From N ≤ 3k², derive k ≥ (1/2)√N - collision_involves_x: Any collision in insert x S involves x - blocked_element_form: Blocked elements have specific algebraic form - bound_from_two_to_one: Double-counting gives |A \ S| ≤ 2|S|² from 2-to-1 map - kss_blocked_count_bound: Fully derived from axiom (complete proof!) - maximal_sidon_blocking_bound: |A| ≤ |S| + 2|S|² - kss_sqrt_bound: Main theorem - ∃ Sidon B ⊆ A with |B| ≥ (1/2)√|A|

⚠️ AXIOM (1 only): - kss_two_to_one_map_exists: Existence of 2-to-1 charging map This corresponds to the "three implies Type 2" argument from KSS Lemma 2.

Verified Axiom Dependencies
Running the axiom checker shows the main theorem depends on three standard Lean axioms plus one mathematical axiom: the existence of the 2-to-1 charging map, which encodes the combinatorial argument from KSS Lemma 2.

Now I'm verifying the axiom dependencies by checking what the main theorem actually relies on—it turns out the only non-standard mathematical axiom needed is the 2-to-1 map existence, which captures the key combinatorial step from the original KSS paper. I'm laying out the main theorems about Sidon set blocking bounds—showing that any maximal Sidon subset S of a finite set A satisfies |A \ S| ≤ |S|² + |S|³, which leads to the cubic root bound |S| ≥ (|A|/3)^{1/3}. This connects to Erdős's classical Problem 530 about determining the maximum size of Sidon sets in intervals. such that every N-element set contains a Sidon subset of size k. The known bound is ℓ(N) = Θ(√N), with the KSS lower bound giving ℓ(N) ≥ c√N, but my formalization only achieves the weaker Ω(N^{1/3}) via a direct blocking argument—the stronger √N bound would need a more delicate charging argument that I haven't been able to formalize.

I've now completed the axiom-free proof with all the key lemmas established: singleton sets are Sidon, maximal Sidon subsets exist and are nonempty, the quadratic constraint gives the √N bound, collisions in insertions involve the new element, blocked elements have a specific algebraic structure across 16 cases, and the cardinality bounds for sumsets and blocked element types all follow from the set size constraints.

The main theorem states that for any finite set A, there exists a Sidon subset B where |A| ≤ 3|B|³, which gives the cubic root bound. I also removed an earlier axiom about 2-to-1 maps that was unnecessary for the final result. I've removed the dependent lemmas along with the false axiom, so the entire formalization is now axiom-free. Let me document the key references that motivated this work and note when it was completed.

Now I'm planning out all the edits systematically—I'll map out the exact boundaries for each change, then execute them efficiently. I need to identify where section 4.3 starts after the sidon_sumset_card_le_sq lemma and trace through to find where the removable sections end, so I can replace them with a concise note and renumber the remaining parts accordingly. I'm documenting the removal of a flawed axiom about two-to-one maps that was supposed to prove the √N bound for Sidon sets. The axiom claimed blocking elements were bounded by 2|S|², but counterexamples like spread-out Sidon sets actually produce Θ(|S|³) blocked elements, so I'm removing the axiom and all dependent lemmas. The correct bound is |A \ S| ≤ |S|² + |S|³, which I'll prove instead, and I'm reorganizing the section structure to focus on the Erdős cube root bound as the main result.

Defining the main theorem that establishes the Ω(N^{1/3}) lower bound... I'm thinking through how to apply these changes sequentially with the multi_replace tool, making sure each replacement matches the exact text after previous ones have been applied. Since the changes are in different sections, I'll break down the header updates into smaller, more targeted replacements to avoid matching issues with the full 55-line comment block. axiom dependencies section. Now I'm clarifying what this formalization actually establishes—it proves the lower bound direction of Erdős Problem 530, showing that the maximum Sidon subset size grows at least as √N, though the exact asymptotics and matching upper bound remain open questions in the literature. √N, completing the derivation of the lower bound on Sidon set size. I've now verified all the key lemmas—collision properties, blocking element structure, and the double-counting argument that yields the quadratic bound on excluded elements. The main theorem follows: any finite set contains a Sidon subset of size at least (1/2)√N, establishing the correct order of growth. Everything hinges on a single axiom about the structure of blocked elements. I've identified the key axiom dependency—kss_two_to_one_map_exists is the only mathematical assumption needed, with the rest being standard Lean axioms. Now I'm looking at the main theorems in the formalization: the blocking bound showing that any maximal Sidon subset leaves at most a cubic number of elements uncovered, which leads to the cube root bound for Sidon set sizes. A ⊆ ℕ with |A| ≥ 1, there exists a Sidon B ⊆ A with |A| ≤ 3|B|³, giving |B| ≥ Ω(|A|^{1/3}).

This connects to Erdős Problem 530, which asks for the order of ℓ(N)—the maximum size of a Sidon subset in any N-element set. The known result is ℓ(N) = Θ(√N) from the KSS lower bound, but what I'm formalizing here is the weaker Ω(N^{1/3}) bound using a direct blocking argument. I've completed the proof without custom axioms, establishing that singletons are Sidon, maximal Sidon subsets exist and are nonempty, collisions in insertions involve the new element, and blocked elements have a specific algebraic structure. I discovered that a previously included axiom claiming |A \ S| ≤ 2|S|² was actually false—counterexamples with spread-out Sidon sets produce far more blocked elements than the bound allows. I've removed that axiom and all dependent lemmas, and verified that the main theorem only relies on standard logical axioms with no custom mathematical assumptions. I'm continuing to define the theorem statement, showing that it establishes a lower bound for the Sidon subset problem—specifically that any finite set has a Sidon subset of size at least half the square root of the original set. I'm also clarifying what this formalization covers versus what remains open, noting that while the lower bound is proven here, the matching upper bound and the full resolution of Erdős's problem are established through classical results but not in this file. witnesses this.

Still OPEN in the literature:

Exact asymptotics: Is ℓ(N) ~ √N? (i.e., does ℓ(N)/√N → 1?)
Note on the constant: We prove c = 1/2, weaker than best-known values. This suffices to establish ℓ(N) = Ω(√N), i.e., the correct order of growth.

Status: ✅ COMPLETE (modulo 1 axiom)
I've now verified the full chain of results: from the quadratic bound on k through collision analysis and the blocking structure, all the way to the double-counting argument that gives us |A \ S| ≤ 2|S|², and finally the main theorem establishing that any finite set A contains a Sidon subset of size at least (1/2)√|A|.

The main theorem depends on just one mathematical axiom—the existence of a 2-to-1 charging map—which corresponds to the key combinatorial argument in the original KSS paper.

Now I'm laying out the core results: the blocking bound theorem that constrains how many elements can be outside a maximal Sidon set, which then yields the cubic bound on the original set size, and finally the Erdős-style cube root guarantee for finding large Sidon subsets.

This connects to Erdős Problem 530, which asks for the maximum size of a Sidon subset in any N-element set. The classical result is Θ(√N), but this formalization establishes the weaker Ω(N^{1/3}) bound through a direct blocking argument instead. ≤ |S|² + |S|³, which gives us the main result: there exists a Sidon subset B of A with |A| ≤ 3|B|³. I should note that an earlier approach tried to claim |A \ S| ≤ 2|S|² universally, but that turned out to be false—counterexamples like spread-out Sidon sets show this bound doesn't hold.

The good news is that the main theorem only depends on the standard Lean axioms (propext, Classical.choice, Quot.sound), so the proof is fully axiom-free from a mathematical perspective.

Now I'm moving on to remove the axiom section itself—I need to strip out the 4.3 header and everything related to the KSS charging argument definition, including the kss_two_to_one_map_exists and the supporting lemmas, all the way through kss_sqrt_bound. I'm working through a strategy to refactor this file by making targeted replacements rather than trying to match large blocks all at once. Each step removes or updates a specific section—the axiom, various bounds, historical notes, and parts of the verification—then I'll renumber the remaining sections and add the new cube root bound. I need to apply these replacements sequentially so each one operates on the updated file state. the entire block from the section 4.3 header all the way through the kss_sqrt_bound definition, using the section header as the starting anchor and the end of that bound as the stopping point. This way I avoid the line-number shifting problem and can do it in one clean replacement operation. I'm realizing the string matching approach is getting unwieldy with such long text blocks. Let me step back and do this incrementally—start with a small replacement like the section header, verify it works, then move through the file piece by piece rather than trying to construct massive old-text strings upfront. map_exists text will be gone, so step 3's match for "section 4.4 + bound_from_two_to_one" should still find its text. This should work fine with multi_replace since I'm matching on content, not positions.

Let me use grep_search to pull the exact text I need to match for each replacement, so I can be precise with the content matching.

Actually, I already have the full file content from my earlier read, so I can just carefully construct each old string to match. I'm organizing this into seven replacements: updating the header, then removing sections 4.3 and 4.4 along with their associated definitions and axioms, followed by cleaning up the remaining lemmas and the historical note, and finally removing Part 5 entirely.

Now I need to refine my replacement strategy. Instead of keeping all seven separate, I can combine the middle ones—merging the removal of section 4.3 through the axiom into one replacement, then handling section 4.4 through the end of kss_sqrt_bound as another. After that, I'll update Part 6 to Part 5, add the erdos_cube_root_bound definition, and update the verification section.

Let me start writing out the exact old and new strings for each replacement, being very precise about the boundaries. Defining the charging map structure... I'm realizing I can streamline this by combining the two replacements into one larger block, pulling together the section from 4.3 through the quadratic bound proof to reduce the total number of edits needed. I'm noting that a previous version of this proof contained axiom-dependent sections that have been removed because the underlying axiom was proven false—specifically, the claim that certain two-to-one maps exist for spread-out Sidon sets turned out not to hold.

The counterexample is a geometric progression like {1, 10, 100, ..., 10⁶} where the set of blocked elements far exceeds the claimed bound, since the sumset difference S+S-S actually contains Θ(|S|³) elements rather than the assumed O(|S|²).

Now I'm moving forward with the correct, axiom-free blocking bound that establishes |A\S| ≤ |S|² + |S|³ through direct proof. I'm breaking this down into manageable chunks so I can target specific sections of the file without risking mismatches on the massive axiom block. I'll start with the header comment, then tackle the axiom section by matching its boundaries carefully, rename Part 6 to Part 5, add the main theorem, and finally update the verification section. Defining the two-to-one map structure... I'm formalizing the KSS charging argument: for a maximal Sidon set S in A, I need to establish that there's a map from A \ S to S × S where each element of S × S has at most 2 preimages. The intuition is that any element x outside S must be "blocked" by some pair (a,b) in S satisfying either x + c = a + b or 2x = a + b for some c in S, and mapping x to the lexicographically smallest such pair ensures the map is at most 2-to-1 because the Sidon property prevents three elements from mapping to the same pair. I'm axiomatizing this existence claim to move forward with the main blocking bound argument.

However, this axiom turned out to be false—counterexamples with spread-out Sidon sets show that the number of blocked elements can grow as Θ(|S|³), far exceeding the claimed 2|S|² bound. I've removed the axiom and all dependent lemmas, and the correct blocking bound will be derived axiom-free in the next section.

Now I'm working through what needs to be removed from the old section 4.4 and the kss_sqrt_bound lemma, which depended on the false axiom. The tricky part is figuring out where exactly the old text ends after my previous replacement, since removing the section header shifts everything downstream.