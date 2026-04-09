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

## The complete problem: GSRC-CB

* Generalized Reserve Set Covering Problem with Connectivity and Buffer Requirements

* it's an RSC where other constraints are imposed regarding:

  * connectivity
  * buffer area
  * minimum quotas of ecological suitability

* it's introducted in a modular way:

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
& GSRC : \min \{\gamma(u,x,z) | \\ & (S1-SQ), (S2-SQ), (S1-PROTECT), (S2-PROTECT), (LINK)\}
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
  u_i =
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
\sum_{s\in S_2} u_2 \geq P_2
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

### GSRC-B model

$$
\begin{align*}
& GSRC-B : \min \{\gamma(u,x,z) | \\ & (S1-SQ), (S2-SQ), (S1-PROTECT), (S2-PROTECT), (LINK)\\& (d-BUFF.1), (d-BUFF.2) \}
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

### GSRC-C model

For more info about this:

* original article → https://link.springer.com/chapter/10.1007/978-3-642-38189-8_11
* slides that explain the original article → https://www.el-kebir.net/teaching/CS598MEB/Spring_2019/MWCS.pdf

> [!WARNING]
>
> Non ho capito se qui c'è link o meno

$$
\begin{align*}
& GSRC-C : \min \{\gamma(u,x,z) | \\ & (S1-SQ), (S2-SQ), (S1-PROTECT), (S2-PROTECT), (LINK) \\ &  (ALLCON), (YX), (NCOMP) \}
\end{align*}
$$

#### Connectivity

##### r-arc-node-separator

* A root $r$ is added to the graph: we can consider $G_r=(V_r. E_r)$ where $V_r= V \cup \{r\}$ and $E_r = E \cup \{(r,i)|i\in V\}$ (so all the nodes from the original graph are connected to $r$)
* The arcs that connect the nodes to the root $r$ are called **$r$-arcs** and the set of $r$-arcs is called $A_r$
* Given $l \in V$, an **$r$-arc-node-separator** is a tuple $W=(W_V, W_A)$, where $W_V \subseteq V$ and $W_A \subseteq A_r$, such that  if $W$ is removed from $G_r$ then the site $l$ can't be reached by $r$
* $W_l$ is the set of all possible $r$-arc-node-separators w.r.t $l$
* to have connectivity, we want in the solution to have a path from $r$ to all nodes present in the solution

#### Variables

* Let $y_i, 1 \leq i \leq |V|$ be an auxilary variable 
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

If the buffer areas are not considered, this constrain replaces (CORECON).
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
& GSRC-C : \min \{\gamma(u,x,z) | \\ & (S1-SQ), (S2-SQ), (S1-PROTECT), (S2-PROTECT), (LINK) \\ & (d-BUFF.1), (d-BUFF.2) \\ &  (CORECON), (YZ), (NCOMP) \\ & (u, x, z, y) \in \{0,1\}^{|S|+3|V|} \}
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
* such that $V_s / C_s$ is not enough to satisfy the sustainability quota for that specie

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

* $\rho = (\tilde{u},\tilde{x},\tilde{x}, \tilde{y})$ is a solution of the LP relaxation at the current node of the branch-and-bound tree

#### Separation of CORECON

##### Fractionary solution

* we transform the graph in to a digraph: the nodes of the graphs are separated in to $i_1$ and $i_2$ with capacities defined as:
  $$
  \begin{align*}
  \text{cap}_{tv} = \cases{\tilde{z_i} & \text{if $t=i$, $v=i_2$, $i\in V$,}\\\tilde{y_i} & \text{if $t=r$, $v=i_1$, $i\in V$,} \\ \infty & \text{otherwise}}
  \end{align*}
  $$

* then a violeted connectivity cut is $(\overline{W}_V, \overline{W}_A)$  such that:
  $$
  \begin{align*}
  &\overline{W}_V = \{i | (i_1, i_2) \in A_z\}\\
  &\overline{W}_A = \{(r,i)|(r, i_1) \in A_r'\}\\
  &\sum_{i\in \overline{W}_V} \overline{z}_i + \sum_{i \in \overline{W}_A} \overline{y}_j < \overline{z}_l
  \end{align*}
  $$

##### Integer solution

* $H$ connected components induced by $\overline{z}_i = 1$ 

* if for all, $\overline{y}_i=0$, the component is not connected

* the connectivity cut can then be defined as $(W_A, W_V)$ such that:
  $$
  \begin{align*}
  &W_A = H \\
  &W_V = \{j | {i,j} \in E : i \in H, j \notin H\}
  \end{align*}
  $$

> [!NOTE]
>
> in both cases, downlifting is used, by allowing only $j \leq l$ for $z_l$ on the left hand side.

#### Separation of SCC

the same as CORECON, but $\overline{C}$ is considered.

#### Separation of COVER

* the feasible solutions of this separation problem (a knapsack-problem) in minimization form are the covers

$$
\begin{align*}
\min \{\sum_{j\in V_s} \tilde{z}_jq_j| \sum_{j\in V_s} w_j^sq_j \geq W_s - \lambda \text{ and } \bold{q} \in \{0, 1\}^{|V_s|} \}
\end{align*}
$$

* but this problem is not solved exactly, a heuristic is followed
  * sord the nodes in a non-decreasing way by $\tilde{z}_j /w_j^s$
  * construct a cover by iteratively picking the nodes sorted in this way, starting with smallest ration, until: $\sum_{j\in C_s} w_j^s \geq W_s - \lambda_s$

#### Implementation of the cut-loop

1. separate COVER and SCC/SC
2. separate CORECON
   * done only for nodes with $\tilde z_l \geq \tau$ where $\tau = 0.5$ or $0.1$
   * once a violated ineq. is found, the nodes $\{i|(r,i) \in W_A \}$ are not considered for separation

> [!NOTE]
>
> for integer solutions, only connectivity cuts (CORECON) are separated

### Heuristics

* **construction heuristic** → to generate a solution for initializing the branch and cut
* **primal heuristic** → incorporated in the branch and cut
* **local-branching ILP-heuristic** → to improve the solution found

#### Construction and Primal heuristic

##### Construction heuristic - Phase 1

creates a feasible solution in  a greedy fashion:

* $k$ nodes are chosen at random
* $S_x$ is build by considering the buffer for each core node
* while the (PROTECT) constraints are **not** valid, do:
  * compute the distances (node weighted) between the nodes in the core and T(S)*****
  * considers the node $i^*$ with min distance among T(S)
  * considers the nodes on the shortest path between the core nodes and this $i^*$
  * adds all these nodes to the core and adds also the buffer for each
  * updates T(S)

> [!NOTE]
>
> **[*]** T(S) = set dynamically updated of the nodes that are deemed as "helpful" if added to $S_z$,
>
> * "helpful" = if 
>   * $protectedS_1$ is false (less than $P_1$ species protected) 
>   * and the node $\in V_s$ for at least one specie with $u_s = 0$ ⇒ that's still not protected by the reserve (meaning, its suitability quota is not fulfilled with the current solution)
>   * helpfulness is measured by the **node-cost** function $\Delta_i(S)$ (see article)

##### Primal heuristic - Phase 1

* used during the branch-and-cut
* it's basically the same as the construction heuristic, but with 2 differences:
  * in the **node-cost** function a value changes: $c_i(1-\tilde x_i)$ instead of $c_i$
  * the randomly generated starting solutions are constructed considering nodes with: $\tilde y_i \geq 0.001$

##### Post processing - Phase 2

greedy local improvement procedure to remove unnecessary nodes from $S_z$

* check for every node in the core (and the consequent buffer nodes) if they're removed, what is the improvement in the objective function?
* remove that node
* repeat until no other zone nodes can be removed (i think until constraints are still valid)

#### Local-branching ILP-heuristic

* start with basic ILP formulation and extend with additional local branching constraint which specifies the **r-neighborhood** wrt S (LOCBRA)
  $$
  \sum_{i\in S_z} z_i \geq |S_z| - r
  $$
  this ensures that at least $|S_z| - r$ of the core parcels of the initial solution, belong also to the new solution $S'$

* use of the **cutpool**: collects all violated inequalities detected during the local branching phase

  * these are used to initialize the final call of the branch and cut procedure
  * and also to initialize each subsequent local search iteration

* the formulation is solved through branch and cut + primal heuristic

* impose a time limit for each local search iteration

* solver is interrupted as soon as a feasible solution is found (first-improvement local search strategy)

* if no improving solution is found in the time limit, then the size of the neighborhood is increased by $\Delta_r$

* whenever new best solution is found, the size of the neighborhood is reset to $r$ 

* the procedure is then repeated with the new improved solution $S'$ until either:

  * max number of local search iteration is satisfied
  * max neighborhood size is reached
  * overall time limit for local branching phase is reached

* in their implementation 

  * $r = 5$, 
  * time limit is $20$ seconds, 
  * if no improved solution is found, $r$ is increased by $\Delta_r = 5$ until maximum neighborhood size of $20$
  * if improved solution is found, $r$ is reset to $5$ 

### Computational results

#### Instances

* 400 nodes in grid (760 edges)
* cost at random in [1, 100]
* score at random between [20, 100] and set to 0 with 20% prob. for $S_1$, 10% for $S_2$
* 4 sets of 10 instances, with $S_1$ = 1 and $S_2 = 3$ o il triplo
* d = 1
* scores are 0 for all boundary nodes
* k = 1 o 3
* $\lambda_s = \ceil 0.05 \sum_{i \in V_s} w$

#### Computational settings

* **basic** → only CORECON cuts
* **basic+** → also COVER and SCC cuts
* **basic+CP** → also constructon and primal heuristic 
* **basic+CPLB** → also local branching procedure (between construction and branch and cut)
