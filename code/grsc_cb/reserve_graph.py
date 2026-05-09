import igraph as ig

INF = 1e9  # large constant

class FlowGraph:
    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges
        self.n_nodes = len(nodes)
        self.build_flow_graph()
        
    def build_flow_graph(self):
        graph = ig.Graph()
        graph.add_vertices(range(2 * self.n_nodes))
        graph.add_vertices(['root', 'sink'])
        
        self.root_id = 2 * self.n_nodes
        self.sink_id = 2 * self.n_nodes + 1
        
        # dicts for edges ids for faster lookup
        self.es_inout = {}
        self.es_root = {}
        self.es_sink = {}
        

        for i in self.nodes:
            # i_in -- i_out
            self.es_inout[i] = graph.ecount()
            graph.add_edges([(i, self.n_nodes + i)], {"capacity": 0})
            
            # root -- i_in
            self.es_root[i] = graph.ecount()
            graph.add_edges([(self.root_id, i)], {"capacity": 0}) 
            
            # i_out -- sink
            self.es_sink[i] = graph.ecount()
            graph.add_edges([(self.n_nodes + i, self.sink_id)], {"capacity": 0}) 
            
        for (u, v) in self.edges:
            # u_out -- v_in
            graph.add_edges([(self.n_nodes + u, v)], {"capacity": INF})
            # v_out -- u_in
            graph.add_edges([(self.n_nodes + v, u)], {"capacity": INF})
        
        self.graph = graph
        
    def build_flow_network(self, z_val, y_val, add_sink=False, Cs=None):
        graph = self.graph
        
        capacities = self.graph.es["capacity"]
        
        for i in self.nodes:
            capacities[self.es_inout[i]] = max(0, z_val[i])
            capacities[self.es_root[i]] = max(0, y_val[i])
            capacities[self.es_sink[i]] = 0
       
        if add_sink:
            for i in Cs:
                capacities[self.es_sink[i]] = INF

        self.graph.es["capacity"] = capacities
        
        return graph
    
    def root_mincut(self, node):
        return self.graph.mincut(self.root_id, self.n_nodes + node, capacity="capacity")

    def root_sink_mincut(self):
        return self.graph.mincut(self.root_id, self.sink_id, capacity="capacity")