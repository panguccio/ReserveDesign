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
    S : list
        List of all sites, concatenation of S_1 and S_2.
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
    def __init__(self, G, S_1, S_2, P_1, P_2, k, w, lambda_s, c, tau, d=1):
        self.G = G
        self.V = set(G.nodes)
        self.E = set(G.edges)
        self.S_1 = S_1
        self.S_2 = S_2
        self.S = S_1 + S_2
        self.P_1 = P_1
        self.P_2 = P_2
        self.k = k
        self.w = w
        self.lambda_s = lambda_s
        self.c = c
        self.tau = tau
        self.d = d

        self._precompute_neighborhoods()
        self._precompute_species_quantities()
       
    def v_s(self, s):
        """Returns the precomputed set of suitable land sites for species s."""
        return self.Vs[s]
    
    def _precompute_neighborhoods(self):
        """Precomputes neighborhoods once to avoid set operations in the callback."""
        self._delta_d_plus_map = {}
        self._delta_d_minus_map = {}
        for i in self.V:
            neighbors = self.G.neighbors(i, radius=self.d)
            self._delta_d_plus_map[i] = frozenset(neighbors)
            self._delta_d_minus_map[i] = frozenset(neighbors - {i})

    def _precompute_species_quantities(self):
        """Precomputes the set of suitable nodes for each species and the sum of the suitability quota in them."""
        self.Vs = {
            s: frozenset(i for i in self.V if self.w[(i, s)] > 0)
            for s in self.S
        }
        self._Ws = {
            s: sum(self.w[(i, s)] for i in self.Vs[s]) 
            for s in self.S
        }
    
    def delta_d_plus(self, i):
        """Returns the set of all nodes separated by at most d edges from i"""
        return self._delta_d_plus_map[i]
    
    def delta_d(self, i):
        return self._delta_d_minus_map[i]
    
    def get_graph(self):
        return self.G.G
    
    
    def __str__(self):
        return (
        f"GRSC_CB_Instance(|V|={len(self.V)}, |E|={len(self.E)}, "
        f"|S1|={len(self.S_1)}, |S2|={len(self.S_2)}, "
        f"P1={self.P_1}, P2={self.P_2}, k={self.k}, d={self.d})"
        )
 
        