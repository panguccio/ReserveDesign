import networkx as nx

class GRSC_CB_Instance:
    """
    Class creates an instance for GRSC-CB problem.
    
    Attributes
    ----------
    V : list
        List of land parcels (nodes in the graph).
    E : list of tuples
        List of edges in the graph, that represent if a border is shared among 2 nodes. Represented as tuples (u, v).
    S_1 : list                   
        List of sites of species 1 that need to be protected in the core areas.
    S_2 : list
        List of sites of species 2 defined as S_2 = S\S_1.
    P_1 : int
        Number of species 1 that need to be protected.
    P_2 : int
        Number of species 2 that need to be protected.
    k : int
        Maximum number of connected components allowed.
    w : dict[(s, i)]    
        Dictionary that gives the suitability score of a node i for a specie s.
    lambda_s : dict[s]
        Dictionary lambda that gives the minimum quota of ecological suitability for a specie s.
    c : dict[i]
        Dictionary that gives the cost of selecting a node i as part of the reserve.
    d : int
        Width of the protection buffer.
    """
    def __init__(self, V, E, S_1, S_2, P_1, P_2, k, w, lambda_s, c, d=1):
        self.V = V
        self.E = E
        self.S_1 = S_1
        self.S_2 = S_2
        self.S = S_1 + S_2
        self.P_1 = P_1
        self.P_2 = P_2
        self.k = k
        self.w = w
        self.lambda_s = lambda_s
        self.c = c
        self.d = d
        
        self.G = nx.Graph()
        self.G.add_nodes_from(self.V)
        self.G.add_edges_from(self.E)
        
    def v_s(self, s):
        return [i for i in self.V if self.w[(i, s)] > 0]
    
    def delta_d_plus(self, i):
        return list(nx.ego_graph(self.G, i, radius=self.d).nodes())
    
    def delta_d(self, i):
        neighborhood = self.delta_d_plus(i)
        neighborhood.remove(i)  # removes node i
        return neighborhood
    
    def __str__(self):
        return (
        f"GRSC_CB_Instance(n={len(self.V)}, m={len(self.E)}, "
        f"|S1|={len(self.S_1)}, |S2|={len(self.S_2)}, "
        f"P1={self.P_1}, P2={self.P_2}, k={self.k}, d={self.d})"
        )
 
        