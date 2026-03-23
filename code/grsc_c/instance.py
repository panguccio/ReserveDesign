import networkx as nx

class GRSC_BInstance:
    def __init__(self):
        self.V = list(range(5))
        self.S = list(range(12))
        self.S_1 = list(range(6))
        self.S_2 = list(range(6, 12))
        self.P_1 = 6
        self.P_2 = 6
        self.k = 3

        # Grafo dei land sites
        self.G = nx.Graph()
        self.G.add_nodes_from(self.V)
        self.G.add_edges_from([(0,1), (1,3), (0,2), (2,3), (2,4)])  # definisci tu i confini

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
    
instance = GRSC_BInstance()
print(instance.neighborhood(0))