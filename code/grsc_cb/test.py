from grsc_cb_model import GRSC_CB_Model
from grsc_cb_instance import GRSC_CB_Instance
import numpy as np
from scipy.spatial import Delaunay
import networkx as nx

points = np.random.rand(8, 2)
tri = Delaunay(points)

G = nx.Graph()
G.add_nodes_from(range(len(points)))

for simplex in tri.simplices:
    i, j, k = simplex
    G.add_edge(i, j)
    G.add_edge(j, k)
    G.add_edge(i, k)

instance = GRSC_CB_Instance(V=G.nodes, 
                            E=G.edges, 
                            S_1=list(range(6)), 
                            S_2=list(range(6, 12)), 
                            P_1=6, 
                            P_2=6, 
                            k=3, 
                            w={(i, s): 1.5 if s < 6 and i < 2 else 0.5 if s < 6 and i >= 2 else 2 if s >= 6 and i < 2 else 1.8 for i in G.nodes for s in range(12)}, 
                            lambda_s={s: 3 if s < 6 else 5 for s in range(12)}, 
                            c={i: 1 if i < 3 else 2 for i in G.nodes})

model = GRSC_CB_Model(instance)
model.solve()
model.print_solution()
model.print_graph()
        
  

