from grsc_cb.model import GRSC_CB_Model
from grsc_cb.instance import GRSC_CB_Instance
import numpy as np
from grsc_cb.reserve_graph import Graph

# number of land parcels
n = 10
# number of species
m = 3
# number of max connected areas
k = 2
# range of habitat suitability function
w_min, w_max = 20, 100
# range of costs
c_min, c_max = 1, 100
# lambda percentage threshold
lambda_threshold = 0.05
# buffer size
d = 1
# tau threshold
tau = 0.8

# generate a random instance Delunay graph
G = Graph.random_delaunay(n)
external_nodes = G.external_nodes()

# costs of land parcels
c = {i: np.random.randint(c_min, c_max + 1) for i in G.nodes}

# specie definition
S_1 = list(range(m//3))
S_2 = list(range(m//3, m))
P_1 = len(S_1)
P_2 = len(S_2)

# habitat suitability score function
w = {}
for s in S_1 + S_2:
    prob_zero = 0.2 if s in S_1 else 0.1
    for i in G.nodes:
        if i in external_nodes and s in S_1:
            w[(i, s)] = 0
        elif np.random.rand() < prob_zero:
            w[(i, s)] = 0
        else:
            w[(i, s)] = np.random.randint(w_min, w_max + 1)
            
# suitability quota
lambda_s = {s: lambda_threshold * sum(w[(i, s)] for i in G.nodes) for s in S_1 + S_2}

# toy instance
instance = GRSC_CB_Instance(G, 
                            S_1, S_2, P_1, P_2, 
                            k, w, lambda_s, c, tau, d)

if __name__ == "__main__":
    
    print(instance)
    for s in S_1 + S_2:
        print(f"Species {s}: \n\tSuitability scores in the nodes: {[w[(i, s)] for i in G.nodes]} \n\t=> suitability quota = {lambda_s[s]:.2f}")
    print(f"Land parcels costs: {c}")

    # Reserve Set Covering Problem
    print(f"\nReserve Set Covering Problem\n{'-'*30}")
    model = GRSC_CB_Model(instance, simple=True, B=False, C=False)
    model.solve()
    model.print_solution()

    # Generalized Reserve Set Covering Problem
    print(f"\nGeneralized Reserve Set Covering Problem\n{'-'*30}")
    model = GRSC_CB_Model(instance, B=False, C=False)
    model.solve()
    model.print_solution()

    # Generalized Reserve Set Covering Problem with Buffer requirements
    print(f"\nGeneralized Reserve Set Covering Problem with Buffer requirements\n{'-'*30}")
    model = GRSC_CB_Model(instance, C=False)
    model.solve()
    model.print_solution()

    # Generalized Reserve Set Covering Problem with Connectivity requirements
    print(f"\nGeneralized Reserve Set Covering Problem with Connectivity requirements\n{'-'*30}")
    model = GRSC_CB_Model(instance, B=False)
    model.solve()
    model.print_solution()

    # Generalized Reserve Set Covering Problem with Buffer and Connectivity requirements
    print(f"\nGeneralized Reserve Set Covering Problem with Buffer and Connectivity requirements\n{'-'*30}")
    model = GRSC_CB_Model(instance)
    result = model.solve()
    model.print_solution()

    # GRSC-CB + Primal heuristic
    print(f"\nGRSC-CB + Primal heuristic\n{'-'*30}")
    model = GRSC_CB_Model(instance)
    result = model.solve(cp_heuristic=True)
    model.print_solution()

    # GRSC-CB + Primal heuristic + Local Branching heuristic
    print(f"\nGRSC-CB + Primal heuristic + Local Branching heuristic\n{'-'*30}")
    model = GRSC_CB_Model(instance)
    result = model.solve(cp_heuristic=True, lb_heuristic=True)
    model.print_solution()