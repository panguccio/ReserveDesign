import igraph as ig
import networkx as nx
from scipy.spatial import Delaunay, ConvexHull
import numpy as np

INF = 1e9  # large constant

class Graph:
    def __init__(self, nodes, edges, points):
        self.nodes = nodes
        self.edges = edges
        self.n_nodes = len(nodes)
        self.points = points
        G = nx.Graph()
        G.add_nodes_from(self.nodes)
        G.add_edges_from(self.edges)
        self.G = G
    
    @classmethod
    def random_delaunay(cls, n):
        """
        Generates a random graph using Delaunay triangulation.
        """

        points = np.random.rand(n, 2)
        tri = Delaunay(points)
        nodes = list(range(len(points)))
        edges = set()

        # for each node, it connects it to its neighbors using Delaunay triangulation 
        for simplex in tri.simplices:
            i, j, h = simplex

            edges.add((i, j))
            edges.add((j, h))
            edges.add((i, h))

        return cls(
            nodes=nodes,
            edges=list(edges),
            points=points,
        )
    
    
    def external_nodes(self):
        nodes = list(set(ConvexHull(self.points).vertices)) 
        return [int(node) for node in nodes]
    
    def neighbors(self, i, radius=1):
        return set(nx.ego_graph(self.G, i, radius).nodes())
    
    def subgraph(self, nodes):
        return self.G.subgraph(nodes)
    
    def draw_graph(self, x=None, z=None, with_buffer=False, with_labels=False):
        """
        Draws the graph with nodes colored according to selection and buffer status.
        """
        color_map = []
        if x is None or z is None:
            # Default color for all nodes
            color_map = ['grey' for _ in self.nodes]
        else:
            for i in self.nodes:
                if z[i].X > 0.5: # Core nodes
                    color_map.append('green')  
                elif x[i].X > 0.5: # Buffer nodes
                    if with_buffer:
                        color_map.append('yellow')  
                    else:
                        color_map.append('green')
                else:
                    color_map.append('grey')  # Non-selected nodes
        
        # ig.plot(self.G, vertex_color=color_map)
        nx.draw(self.G, self.points, node_color=color_map, with_labels=with_labels)
        
    def get_shortest_paths(self, source_nodes, weight):
        distances, paths = nx.multi_source_dijkstra(self.G, source_nodes, weight=weight)
        return distances, paths

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