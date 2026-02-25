# GRSC-CB

## Introduzione

* the paper wants to define a nature reserve design problem using a mathematical model
* such model needs to provide optimal reserves that respect ecological, economical and eventually other requirements

### RSC

* Reserve Set Covering Problem
* it's the base problem on which the actual article problem is defined

#### Definitions

* $$V$$ → **land sites** set
* $$S$$ → **species** set
* $$G = (V,E)$$ → graph where:
  * each **node** is a land site
  * each **arch** is given by the relationship: $$\{i,j\} \in E \iff i, j$$  share a border
* $$\forall s \in S$$, $$V_S$$ $$\subseteq V $$ →  set of all land sites that are suitable for specie $$s$$

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

#### Observations

* this formulation of the problem is simple in the sense that it <u>doesn't</u> impose any spatial requirements, such as:
  * size/compactness of the reserve
  * number of reserves
  * proximity
  * connectivity
  * shape
  * presence of core or buffer areas

## GSRC-CB

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

#### Definitions

* $$S_1$$ $$\subseteq S$$ → set of species that need to stay in the core area
* $$S_2$$ $$\subseteq S, S_1 \cup S_2 = S, S_1 \cap S_2 = \varnothing $$ → the other species
* $$w: V\times S \rightarrow \mathbb{R} ^+$$ → **habitat suitability function** measures how advisable is a site $$i \in V$$ for a specie $$s \in S$$
* therefore we can define $$V_s = \{i\in V| w(s,i) > 0\}$$ 
* $$\lambda_s$$ $$\geq 0$$ → **minimum quota of ecological suitability** for $$s$$
* $$s \in S$$ is considered **protected** if $$\sum_i w(s,i) \geq \lambda_s$$
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
