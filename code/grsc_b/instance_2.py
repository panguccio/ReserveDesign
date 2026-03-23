import networkx as nx

class GRSC_BInstance:
    def __init__(self):
        self.V = list(range(15))
        self.S = list(range(20))
        self.S_1 = list(range(10))
        self.S_2 = list(range(10, 20))
        self.P_1 = 4
        self.P_2 = 5

        # Grafo dei land sites (griglia 3x5 con qualche arco in più)
        self.G = nx.Graph()
        self.G.add_nodes_from(self.V)
        self.G.add_edges_from([
            # riga 0: nodi 0-4
            (0,1), (1,2), (2,3), (3,4),
            # riga 1: nodi 5-9
            (5,6), (6,7), (7,8), (8,9),
            # riga 2: nodi 10-14
            (10,11), (11,12), (12,13), (13,14),
            # colonne
            (0,5), (1,6), (2,7), (3,8), (4,9),
            (5,10), (6,11), (7,12), (8,13), (9,14),
            # qualche diagonale per renderlo più interessante
            (0,6), (2,8), (5,11), (7,13)
        ])

    def c(self, v):
        if v < 5:
            return 1
        elif v < 10:
            return 2
        else:
            return 3

    def w(self, v, s):
        if s < 10 and v < 5:
            return 1.5
        elif s < 10 and v < 10:
            return 0.8
        elif s < 10:
            return 0.3
        elif s >= 10 and v < 5:
            return 2.0
        elif s >= 10 and v < 10:
            return 1.2
        else:
            return 0.6

    def v_s(self, s):
        return [v for v in self.V if self.w(v, s) > 0]

    def l(self, s):
        return 4 if s < 10 else 6

    def all_neighborhood(self, v, d=1):
        return list(nx.ego_graph(self.G, v, radius=d).nodes())

    def neighborhood(self, v, d=1):
        neighborhood = self.all_neighborhood(v, d)
        neighborhood.remove(v)
        return neighborhood

instance = GRSC_BInstance()
print(instance.neighborhood(0))