# GRSC-CB

[toc]

## Introduzione

* the paper wants to define a nature reserve design problem using a mathematical model
* such model needs to provide optimal reserves that respect ecological, economical and eventually other requirements

### RSC model

* Reserve Set Covering Problem
* it's the base problem on which the actual article problem is defined

#### Definitions

* $$V$$ → **land sites** set
* $$S$$ → **species** set
* $$G = (V,E)$$ → graph where:
  * each **node** is a land site
  * each **arch** is given by the relationship: $$\{i,j\} \in E \iff i, j$$  share a border
* $$\forall s \in S$$, $$V_s$$ $$\subseteq V $$ →  set of all land sites that are suitable for specie $$s$$

##### Variables

* $$x_i$$, $$1 \leq i \leq |V|$$ → binary variables defined as:

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

* $$\sum_{i \in V_s} x_i\geq 1, \quad \forall s \in S $$: assures that each specie is covered by a suitable land site 

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

* $$S_1$$ $$\subseteq S$$ → set of species that need to stay in the core area
* $$S_2$$ $$\subseteq S, S_1 \cup S_2 = S, S_1 \cap S_2 = \varnothing $$ → the other species
* $$w: V\times S \rightarrow \mathbb{R} ^+$$ → **habitat suitability function** measures how advisable is a site $$i \in V$$ for a specie $$s \in S$$

> [!WARNING]
>
> I changed the notation of the habitat suitability function, to make it more intuitive: $w(i, s)$ instead of $w_i^s$

* therefore we can define $$V_s = \{i\in V| w(s,i) > 0\}$$ 
* $$\lambda_s$$ $$\geq 0$$ → **minimum quota of ecological suitability** for $$s$$
* $$s \in S$$ is considered **protected** if $$\sum_i w(i,s) \geq \lambda_s$$
* $$0\leq$$ $$P_1$$ $$\leq |S_1|$$, $$0\leq$$ $$P_2$$ $$\leq |S_2|$$, minimum number of species respectively in $$S_1$$ and $$S_2$$ that the reserve needs to protect
* $$c:V \rightarrow \mathbb{R} ^+$$ → **cost function** of choosing the site $$i \in V$$ to be in the reserve

##### Criteria

1. at least $$P_1$$ species of $$S_1$$ in the core area
2. at least $$P_2$$ species of $$S_2$$ in the reserve
3. $$\lambda_s$$ is satisfied for all species
4. at maximum $$k$$ connected areas
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

* $$z_i$$, $$1 \leq i \leq |V|$$ → binary variables defined as:

  $$
  \begin{align*}
  z_i =
  \begin{cases}
  1, & \text{if the land site $i \in V$ is part of the core area}\\
  0, & \text{otherwise}
  \end{cases}
  \end{align*}
  $$

* $$u_s$$, $$1 \leq s \leq |S|$$ → binary variables defined as:

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
