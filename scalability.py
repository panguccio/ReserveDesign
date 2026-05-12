from grsc_cb.model import GRSC_CB_Model
from grsc_cb.instance import GRSC_CB_Instance
import numpy as np
import networkx as nx
from grsc_cb.reserve_graph import Graph
import matplotlib.pyplot as plt
from tqdm import tqdm

# number of species
m = 30
# number of max connected areas
k = 3
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

size_axis = []
time_axis = []

def generate_instance(n):
    
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
    
    return instance
    
def run_model(n):
    instance = generate_instance(n)
    model = GRSC_CB_Model(instance, B=False, C=False)
    model.solve(cp_heuristic=True, lb_heuristic=True)
    return model.get_time()


if __name__ == "__main__":
    for n in tqdm(range(50, 5000, 50), desc="Solving models", unit="model"):
        times = []
        for _ in range(2):
            time = run_model(n)
            times.append(time)
        avg_time = sum(times) / len(times)
        size_axis.append(n)
        time_axis.append(avg_time)
        
        
        
    print("Number of land parcels (n):", size_axis)
    print("Times (s):", time_axis)
    
    plt.plot(size_axis, time_axis, color='mediumseagreen', marker='o', markeredgewidth=1, linewidth=3)
    
    
    y_min, y_max = min(time_axis), max(time_axis)
    margin = (y_max - y_min) * 0.1
    plt.ylim(y_min - margin, y_max + margin)
    plt.yticks(np.linspace(y_min, y_max, 6))
    plt.xticks(size_axis, rotation=45)

    plt.xlabel("Number of land parcels (n)")
    plt.ylabel("Times (s)")
    plt.title("Average GRSC-CB Solving Time")
    plt.show()