# GRSC-CB

[toc]

## Introduzione

* the paper wants to define a nature reserve design problem using a mathematical model
* such model needs to provide optimal reserves that respect ecological, economical and eventually other requirements

### RSC model

* Reserve Set Covering Problem
* it's the base problem on which the actual article problem is defined

#### Definitions

* $V$ → **land sites** set
* $S$ → **species** set
* $G = (V,E)$ → graph where:
  * each **node** is a land site
  * each **arch** is given by the relationship: $\{i,j\} \in E \iff i, j$  share a border
* $\forall s \in S$, $V_s$ $\subseteq V $ →  set of all land sites that are suitable for specie $s$

##### Variables

* $x_i$, $1 \leq i \leq |V|$ → binary variables defined as:

  $$
  \begin{align*}
  x_i =
  \begin{cases}
  1, & \text{if the land site $i \in V$ is selected}\\
  0, & \text{otherwise}
  \end{cases}
  \end{align*}
  $$

##### Constraints

* $\sum_{i \in V_s} x_i\geq 1, \quad \forall s \in S $: assures that each specie is covered by a suitable land site 

##### Objective Function

* **minimize** the number of land sites

$$
\begin{align*}
\min \pi(x) = \sum_{i\in V} x_i\\
\end{align*}
$$

#### Observation

* this formulation of the problem is simple in the sense that it <u>doesn't</u> impose any spatial requirements, such as:
  * size/compactness of the reserve
  * number of reserves
  * proximity
  * connectivity
  * shape
  * presence of core or buffer areas

## The complete problem: GRSC-CB

* Generalized Reserve Set Covering Problem with Connectivity and Buffer Requirements

* it's an RSC where other constraints are imposed regarding:

  * connectivity
  * buffer area
  * minimum quotas of ecological suitability

* it's introduced in a modular way:

  * **GRSC**

  * GRSC-**B**

  * GRSC-**C**

  * GRSC-**CB**

### Introduction

#### Common definitions

* $S_1$ $\subseteq S$ → set of species that need to stay in the core area
* $S_2$ $\subseteq S, S_1 \cup S_2 = S, S_1 \cap S_2 = \varnothing $ → the other species
* $w: V\times S \rightarrow \mathbb{R} ^+$ → **habitat suitability function** measures how advisable is a site $i \in V$ for a specie $s \in S$

> [!WARNING]
>
> I changed the notation of the habitat suitability function, to make it more intuitive: $w(i, s)$ instead of $w_i^s$

* therefore we can define $V_s = \{i\in V| w(s,i) > 0\}$ 
* $\lambda_s$ $\geq 0$ → **minimum quota of ecological suitability** for $s$
* $s \in S$ is considered **protected** if $\sum_i w(i,s) \geq \lambda_s$
* $0\leq$ $P_1$ $\leq |S_1|$, $0\leq$ $P_2$ $\leq |S_2|$, minimum number of species respectively in $S_1$ and $S_2$ that the reserve needs to protect
* $c:V \rightarrow \mathbb{R} ^+$ → **cost function** of choosing the site $i \in V$ to be in the reserve

##### Criteria

1. at least $P_1$ species of $S_1$ in the core area
2. at least $P_2$ species of $S_2$ in the reserve
3. $\lambda_s$ is satisfied for all species
4. at maximum $k$ connected areas
5. every land site has a core and a buffer area

###### Observation

* the problem defined without the connectivity is a compact model
* the criteria 4 determines an exponential number of constraints, separated with branch and cut

### GRSC model

$$
\begin{align*}
& GRSC : \min \{\gamma(u,x,z) | \\ & (S1\text{-}SQ), (S2\text{-}SQ), (S1\text{-}PROTECT), (S2\text{-}PROTECT), (LINK)\}
\end{align*}
$$

#### Variables

* $x_i$ defined as before

* $z_i$, $1 \leq i \leq |V|$ → binary variables defined as:

  $$
  \begin{align*}
  z_i =
  \begin{cases}
  1, & \text{if the land site $i \in V$ is part of the core area}\\
  0, & \text{otherwise}
  \end{cases}
  \end{align*}
  $$

* $u_s$, $1 \leq s \leq |S|$ → binary variables defined as:

  $$
  \begin{align*}
  u_s =
  \begin{cases}
  1, & \text{if the specie $s \in S$ is protected by the reserve}\\
  0, & \text{otherwise}
  \end{cases}
  \end{align*}
  $$

The solution will be a tuple $(u,x,z)$

#### Constraints

##### S1-SQ

If a specie in $S_1$ is protected, the habitat suitability score for the land sites part of the core area must be at least the minimum quota of ecological suitability of that specie.
$$
\sum_{i\in V_s} w(i, s)z_i \geq \lambda_s u_s \quad \forall s \in S_1
$$



##### S2-SQ

Similarly for a specie in $S_2$, considering land sites in the whole reserve.
$$
\sum_{i\in V_s} w(i, s)x_i \geq \lambda_s u_s \quad \forall s \in S_2
$$



##### S1-PROTECT

At least $P_1$ species of $S_1$ must be protected. 
$$
\sum_{s\in S_1} u_s \geq P_1
$$



##### S2-PROTECT

At least $P_2$ species of $S_2$ must be protected. 
$$
\sum_{s\in S_2} u_s \geq P_2
$$



##### LINK

If a site is in the core, then it must also be in the reserve.
$$
z_i \leq x_i \quad \forall i \in V
$$



#### Objective function

##### COST

Function that indicates the cost that needs to be **minimized**.
$$
\gamma(u,x,z) = \sum_{i\in V} c_i x_i
$$

### GRSC-B model

$$
\begin{align*}
& GRSC\text{-}B : \min \{\gamma(u,x,z) | \\ & (S1\text{-}SQ), (S2\text{-}SQ), (S1\text{-}PROTECT), (S2\text{-}PROTECT), (LINK)\\& (d\text{-}BUFF.1), (d\text{-}BUFF.2) \}
\end{align*}
$$

#### Distance

##### d-neighborhood

For $d \geq 0, d \in \mathbb{N}, i \in V$ the $d$-neighborhood is defined as the set of sites at distance $d$ from $i$.
$$
\begin{align*}

\delta_d (i) = \{j \in V_{i  \neq j} | \text{the number of jumps from $i$ and $j$ is max $d$} \}

\end{align*}
$$
$\delta_d^+(i)$ it the d-neighborhood that contains also $i$.

> [!NOTE]
>
> $j \in \delta_d(i) \iff i \in \delta_d (j)$

#### Constraints

##### d-BUFF.1

Every core site is surrounded by a buffer area of normal sites in its $d$-neighborhood
$$
z_i \leq x_j, \quad \forall j \in \delta_d(i), \quad \forall i \in V
$$

##### d-BUFF.2

Every normal site must have at least one core site in the $d$-neighborhood
$$
x_i \leq \sum_{j \in \delta_d(i)} z_j \quad \forall i \in V
$$

### GRSC-C model

For more info about this:

* original article → https://link.springer.com/chapter/10.1007/978-3-642-38189-8_11
* slides that explain the original article → https://www.el-kebir.net/teaching/CS598MEB/Spring_2019/MWCS.pdf

> [!WARNING]
>
> Non ho capito se qui c'è link o meno

$$
\begin{align*}
& GRSC\text{-}C : \min \{\gamma(u,x,z) | \\ & (S1\text{-}SQ), (S2\text{-}SQ), (S1\text{-}PROTECT), (S2\text{-}PROTECT), (LINK) \\ &  (ALLCON), (YX), (NCOMP) \}
\end{align*}
$$

#### Connectivity

##### r-arc-node-separator

* A root $r$ is added to the graph: we can consider $G_r=(V_r, E_r)$ where $V_r= V \cup \{r\}$ and $E_r = E \cup \{(r,i)|i\in V\}$ (so all the nodes from the original graph are connected to $r$)
* The arcs that connect the nodes to the root $r$ are called **$r$-arcs** and the set of $r$-arcs is called $A_r$
* Given $l \in V$, an **$r$-arc-node-separator** is a tuple $W=(W_V, W_A)$, where $W_V \subseteq V$ and $W_A \subseteq A_r$, such that  if $W$ is removed from $G_r$ then the site $l$ can't be reached by $r$
* $W_l$ is the set of all possible $r$-arc-node-separators w.r.t $l$
* to have connectivity, we want in the solution to have a path from $r$ to all nodes present in the solution

#### Variables

* Let $y_i, 1 \leq i \leq |V|$ be an auxiliary variable 
  $$
  \begin{align*}
  y_i =
  \begin{cases}
  1, & \text{if the land site $i \in V$ is connected to $r$ via an arc $(r,i)$}\\
  0, & \text{otherwise}
  \end{cases}
  \end{align*}
  $$

#### Constraints

Let $k$ be the max number of connected components in the reserve.

##### NCOMP

There's a max of $k$ connected components in the reserve.
$$
\sum_{j\in V} y_j \leq k
$$

##### YZ

If a site $i$ is connected to the root, then it must be considered in the core area.
$$
y_i \leq z_i \quad \forall i \in V
$$

##### CORECON

If the land site $l$ is in the core area of the solution, then for all the $W \in W_l$, I must have at least one node from $W_V$ or one arc from $W_A$. 
$$
\sum_{i\in W_V} z_i + \sum_{j \in W_A } y_j \geq z_l, \quad \forall W \in W_l, \quad \forall l \in V
$$

##### ALLCON

If the buffer areas are not considered, this constraint replaces (CORECON).
$$
\sum_{i \in W_V} x_i + \sum_{j \in W_A} y_j \geq x_l, \quad \forall W \in W_l, \quad \forall l \in V
$$

##### YX

This constraint replaces (LINK)
$$
y_i \leq x_i \quad \forall i \in V
$$

### GRSC-CB

$$
\begin{align*}
& GRSC\text{-}CB : \min \{\gamma(u,x,z) | \\ & (S1\text{-}SQ), (S2\text{-}SQ), (S1\text{-}PROTECT), (S2\text{-}PROTECT), (LINK) \\ & (d\text{-}BUFF.1), (d\text{-}BUFF.2) \\ &  (CORECON), (YZ), (NCOMP) \\ & (u, x, z, y) \in \{0,1\}^{|S|+3|V|} \}
\end{align*}
$$

## Branch and Cut

* based on the separation of the connectivity cuts (CORECON)
* additional valid inequalities are defined and also separated
  * species cuts (SC)
  * cover inequalities (COVER)
  * species-cover cuts (SCC)
* finally, heuristics are designed to find feasible solutions within the framework

implement branch and cut with gurobi: https://support.gurobi.com/hc/en-us/community/posts/25514581728401-Best-practice-for-implementing-branch-and-cut-algorithm-with-gurobi

### Valid inequalities

#### Species cuts

* a sink node $s$ is defined
* for a certain specie, every node in $V_s$ is connected with a new arc to the sink node
* $r$-arc nodes separators are considered with respect to $s$

$$
\sum_{i\in W_V} z_i + \sum_{j \in W_A } y_j \geq u_s, \quad \forall W \in W_s, s\in S_1
$$

#### Cover inequalities

* let $W_s = \sum_{i\in V}w_i^s$
* **cover** = a set $C_s \subset V_s$ such that $\sum_{i \in C_s} w_i^s \geq W_s - \lambda_s$ 
* such that $V_s \setminus C_s$ is not enough to satisfy the sustainability quota for that specie

$$
\sum_{i\in C_s} z_i \geq u_s, \text{if } s \in S_1
$$

$$
\sum_{i \in C_s} x_i \geq u_s, \text{if } s\in S_2
$$

#### Species cover cuts

* like species cuts, but it's $C_s$ that is connected to the sink node

$$
\sum_{i\in W_V} z_i + \sum_{j \in W_A } y_j \geq u_s, \quad \forall W \in W_s, s\in S_1
$$

### Constraint separation

* $\rho = (\tilde{u},\tilde{x},\tilde{z}, \tilde{y})$ is a solution of the LP relaxation at the current node of the branch-and-bound tree

#### Separation of CORECON

##### Fractionary solution — Digraph Construction

To find a violated CORECON cut from a fractional LP solution, the undirected graph $G$ is transformed into a directed graph (digraph) via **node splitting**:

* Each node $i \in V$ is split into two copies:
  * $i_1$ (entry copy)
  * $i_2$ (exit copy)

* The arcs of the digraph and their capacities are defined as follows:

$$
\text{cap}(t, v) =
\begin{cases}
\tilde{z}_i & \text{if } t = i_1,\ v = i_2,\ i \in V \quad \text{(internal node arc)}\\
\tilde{y}_i & \text{if } t = r,\ v = i_1,\ i \in V \quad \text{(root arc)}\\
\infty & \text{if } t = i_2,\ v = j_1 \text{ for } \{i,j\} \in E \quad \text{(original graph edges, both directions)}
\end{cases}
$$

> [!NOTE]
>
> Each undirected edge $\{i,j\} \in E$ generates **two** directed arcs: $(i_2, j_1)$ and $(j_2, i_1)$, both with capacity $\infty$. This forces all flow to pass through the internal node arcs (with capacity $\tilde{z}_i$), which implements **node separation** via max-flow: the minimum $r$-$l$ node-cut has value equal to the max-flow from $r$ to $l_2$ in this digraph.

* A violated connectivity cut $(\overline{W}_V, \overline{W}_A)$ is then identified as the min-cut of the above digraph from $r$ to $l_2$:

$$
\begin{align*}
&\overline{W}_V = \{i \mid (i_1, i_2) \in \text{cut arcs}\}\\
&\overline{W}_A = \{(r,i) \mid (r, i_1) \in \text{cut arcs}\}\\
&\sum_{i\in \overline{W}_V} \tilde{z}_i + \sum_{j \in \overline{W}_A} \tilde{y}_j < \tilde{z}_l
\end{align*}
$$

If such a cut exists, the corresponding CORECON inequality is violated and can be added to the LP.

##### Integer solution

* $H$ = connected component of the core induced by $\tilde{z}_i = 1$ that does **not** contain any root arc (i.e., $\tilde{y}_i = 0$ for all $i \in H$) → the component is disconnected from $r$

* the connectivity cut is defined as $(W_V, W_A)$ such that:
  $$
  \begin{align*}
  &W_A = H \\
  &W_V = \{j \mid \{i,j\} \in E,\ i \in H,\ j \notin H\}
  \end{align*}
  $$

> [!NOTE]
>
> **Down-lifting (symmetry breaking):** In both the fractional and integer case, the CORECON cut for node $l$ is strengthened via down-lifting. Specifically, the constraint:
> $$
> \sum_{i\in W_V} z_i + \sum_{j \in W_A} y_j \geq z_l
> $$
> is tightened by restricting the $y_j$ sum to only those root arcs with $j \leq l$ (imposing a numeric ordering on nodes). This prevents the solver from exploring symmetric solutions — i.e., the same reserve but with different root choices — and significantly reduces the branch-and-bound tree size.

#### Separation of SCC

The same max-flow digraph construction as CORECON is used, but applied to the cover set $C_s$ (connected to a sink node) instead of a single node $l$.

#### Separation of COVER

* the feasible solutions of this separation problem (a knapsack-problem) in minimization form are the covers

$$
\begin{align*}
\min \left\{\sum_{j\in V_s} \tilde{z}_j q_j \;\middle|\; \sum_{j\in V_s} w_j^s q_j \geq W_s - \lambda_s,\ \mathbf{q} \in \{0, 1\}^{|V_s|} \right\}
\end{align*}
$$

* but this problem is not solved exactly; a heuristic is followed:
  * sort the nodes in non-decreasing order by $\tilde{z}_j / w_j^s$
  * construct a cover by iteratively picking nodes in that order (smallest ratio first), until: $\sum_{j\in C_s} w_j^s \geq W_s - \lambda_s$

#### Implementation of the cut-loop

1. Separate COVER and SCC/SC
   * At the root node, add **at most 20** cuts of type COVER/SCC per iteration to avoid overloading the LP
2. Separate CORECON
   * Done **only** for nodes $l$ where $\tilde{z}_l \geq \tau$, with $\tau = 0.5$ (or $0.1$ for a looser threshold)
   * Once a violated inequality is found for node $l$, the nodes $\{i \mid (r,i) \in W_A\}$ are excluded from further separation in the same iteration

> [!NOTE]
>
> For **integer solutions**, only connectivity cuts (CORECON) are separated; COVER and SCC are only added at fractional nodes.

### Heuristics

* **construction heuristic** → to generate a solution for initializing the branch and cut
* **primal heuristic** → incorporated in the branch and cut
* **local-branching ILP-heuristic** → to improve the solution found

> [!NOTE]
>
> In Gurobi and CPLEX, the construction and primal heuristics must be passed as **callbacks** (e.g., `cbSolution` in Gurobi), not as standalone functions. The solver calls them at appropriate nodes of the branch-and-bound tree.

#### Construction and Primal heuristic

##### Node-cost function $\eta_i(S)$

The greedy choice at each step is guided by the **node-cost function**, which balances the incremental cost of adding node $i$ against the suitability gain it brings. It is composed of two terms:

**Incremental cost $C_i(S)$:**
$$
C_i(S) = c_i + \sum_{j \in \delta_d^+(i),\ j \notin S_x} c_j
$$
This is the cost of adding $i$ to the core, plus the cost of all buffer nodes in its $d$-neighborhood that are **not yet** in the reserve $S_x$. In the **primal heuristic**, $c_i$ is replaced by $c_i(1 - \tilde{x}_i)$ to account for nodes already (partially) selected in the LP solution.

**Suitability gain $W^s(i, S)$:**
$$
W^s(i, S) = \sum_{j \in \delta_d^+(i)} w(j, s)
$$
This measures how much node $i$ (and its buffer $\delta_d^+(i)$) contributes toward reaching the quota $\lambda_s$ for species $s \in S_1$ not yet protected (i.e., with $u_s = 0$).

**Full node-cost function:**
$$
\eta_i(S) = C_i(S) + 0.001 \cdot (\ldots) + 0.0001
$$
where the $0.001$ and $0.0001$ terms are small tie-breaking penalties. Refer to the article (Section 3.3) for the precise weights. Without this exact weighting, the greedy heuristic will not produce high-quality solutions.

##### Construction heuristic - Phase 1

Creates a feasible solution in a greedy fashion:

* $k$ nodes are chosen at random as initial root nodes (one per component)
* $S_x$ is built by considering the buffer for each core node
* while the (PROTECT) constraints are **not** satisfied, do:
  * compute the distances (node weighted, using $\eta_i(S)$) between the nodes in the core and $T(S)$
  * consider the node $i^*$ with minimum distance among $T(S)$
  * consider the nodes on the shortest path between the core nodes and $i^*$
  * add all these nodes to the core and add also the buffer for each
  * update $T(S)$

> [!NOTE]
>
> **$T(S)$** = dynamically updated set of nodes deemed "helpful" if added to $S_z$:
>
> * "helpful" = if $protectedS_1$ is false (fewer than $P_1$ species protected)
>   and the node $\in V_s$ for at least one species with $u_s = 0$ (still unprotected)
> * helpfulness is measured by the **node-cost** function $\eta_i(S)$ described above

##### Primal heuristic - Phase 1

* Used during the branch-and-cut (passed as a callback)
* Essentially the same as the construction heuristic, with 2 differences:
  * In the **node-cost** function: $c_i$ is replaced by $c_i(1 - \tilde{x}_i)$
  * The randomly generated starting solutions use nodes with $\tilde{y}_i \geq 0.001$ as seeds

##### Post processing - Phase 2

Greedy local improvement procedure to remove unnecessary nodes from $S_z$:

* For every node in the core (and its consequent buffer nodes): check whether removing it improves the objective function
* Remove the best such node
* Repeat until no further core nodes can be removed while keeping all constraints valid

#### Local-branching ILP-heuristic

* Start with the basic ILP formulation and extend with an additional local branching constraint specifying the **r-neighborhood** w.r.t. $S$ (LOCBRA):
  $$
  \sum_{i\in S_z} z_i \geq |S_z| - r
  $$
  This ensures that at least $|S_z| - r$ of the core parcels of the initial solution also belong to the new solution $S'$

* Use of the **cutpool**: collects all violated inequalities detected during the local branching phase

  * These are used to initialize the final call of the branch and cut procedure
  * And also to initialize each subsequent local search iteration

* The formulation is solved through branch and cut + primal heuristic

* Impose a time limit for each local search iteration

* Solver is interrupted as soon as a feasible solution is found (first-improvement local search strategy)

* If no improving solution is found within the time limit, the size of the neighborhood is increased by $\Delta_r$

* Whenever a new best solution is found, the size of the neighborhood is reset to $r$ 

* The procedure is repeated with the new improved solution $S'$ until either:

  * max number of local search iterations is reached
  * max neighborhood size is reached
  * overall time limit for the local branching phase is reached

* Implementation parameters used in the article:

  * $r = 5$
  * time limit = $20$ seconds per iteration
  * if no improved solution is found, $r$ is increased by $\Delta_r = 5$ up to a maximum neighborhood size of $20$
  * if an improved solution is found, $r$ is reset to $5$

### Computational results

#### Instances

* Grid graph: $20 \times 20$ nodes (400 nodes, 760 edges)
* Cost at random in $[1, 100]$
* Score at random between $[20, 100]$ and set to $0$ with $20\%$ probability for $S_1$, $10\%$ for $S_2$
* 4 sets of 10 instances, with $|S_1| = 1$ and $|S_2| = 3$ or triple
* $d = 1$ (buffer width)
* Scores are $0$ for all boundary nodes
* $k = 1$ or $3$
* $\lambda_s = \lceil 0.05 \sum_{i \in V_s} w(i,s) \rceil$ (5% of total suitability per species)

#### Computational settings

* **basic** → only CORECON cuts
* **basic+** → also COVER and SCC cuts
* **basic+CP** → also construction and primal heuristic 
* **basic+CPLB** → also local branching procedure (between construction and branch and cut)