import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay
import networkx as nx

class GRSC_BInstance:
    def __init__(self):
        
        self.S = list(range(12))
        self.S_1 = list(range(6))
        self.S_2 = list(range(6, 12))
        self.P_1 = 6
        self.P_2 = 6
        self.k = 3
        
        self.points = np.random.rand(8, 2)
        # plt.scatter(self.points[:, 0], self.points[:, 1])
        tri = Delaunay(self.points)
        self.G = nx.Graph()
        self.G.add_nodes_from(range(8))
        for i in range(8):
            self.G.add_edge(tri.simplices[i][0], tri.simplices[i][1])
            self.G.add_edge(tri.simplices[i][1], tri.simplices[i][2])
            self.G.add_edge(tri.simplices[i][0], tri.simplices[i][2])
        
        self.V = self.G.nodes

    def c(self, v):
        return 1 if v < 3 else 2

    def w(self, v, s):
        if s < 6 and v < 2:
            return 1.5
        elif s < 6 and v >= 2:
            return 0.5
        elif s >= 6 and v < 2:
            return 2
        else:
            return 1.8

    def v_s(self, s):
        return [v for v in self.V if self.w(v, s) > 0]
        
    def l(self, s):
        return 3 if s < 6 else 5
    
    def all_neighborhood(self, v, d=1):
        return list(nx.ego_graph(self.G, v, radius=d).nodes())
    
    def neighborhood(self, v, d=1):
        neighborhood = self.all_neighborhood(v, d)
        neighborhood.remove(v)  # rimuovi il nodo stesso
        return neighborhood
    
    def plot(self):
        nx.draw(instance.G, pos=instance.points)
    
instance = GRSC_BInstance()
print(instance.V)
instance.plot()