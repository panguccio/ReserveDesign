import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import igraph as ig

from scipy.spatial import Delaunay, ConvexHull
from shapely.geometry import LineString, box

INF = 1e9  # large constant

def square_intersection(A, B):
    dx, dy = B[0] - A[0], B[1] - A[1]
    line = LineString([
        (A[0] - dx*1000, A[1] - dy*1000),
        (A[0] + dx*1000, A[1] + dy*1000)
    ])
    square = box(-0.1, -0.1, 1.1, 1.1)
    C = min(
        line.intersection(square.boundary).geoms,
        key=lambda p: (p.x - A[0])*dx + (p.y - A[1])*dy
    )
    return np.array([C.x, C.y])


class Graph:
    def __init__(self, nodes, edges=None, points=None):
        self.nodes = nodes
        if edges is not None: self.edges = edges
        self.n_nodes = len(nodes)
        if points is not None: self.points = points
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

        return cls(nodes=nodes, edges=list(edges), points=points)
    
    
    def external_nodes(self):
        nodes = list(set(ConvexHull(self.points).vertices)) 
        return [int(node) for node in nodes]
    
    def external_edges(self):
        return set(map(tuple, ConvexHull(self.points).simplices))
    
    def neighbors(self, i, radius=1):
        return set(nx.ego_graph(self.G, i, radius).nodes())
    
    def subgraph(self, nodes):
        return self.G.subgraph(nodes)
    
    def get_shortest_paths(self, source_nodes, weight):
        distances, paths = nx.multi_source_dijkstra(self.G, source_nodes, weight=weight)
        return distances, paths
    
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
    
    def map(self):
        point_to_idx = {}
        segment_to_centroids = {}
        border_nodes = [[], [], [], []]  # left, right, bottom, top
        cb_edges = []
        points = self.points
        tri = Delaunay(points)
        external_edges = self.external_edges()
        edges = set()
        nodes = []
        centroid_indices = []

        def add_point(p):
            key = (round(p[0], 10), round(p[1], 10))
            if key not in point_to_idx:
                point_to_idx[key] = len(nodes)
                nodes.append(p)
            return point_to_idx[key]

        for simplex in tri.simplices:
            i, j, h = sorted(simplex)
            centroid = points[[i, j, h]].mean(axis=0)
            
            c_idx = add_point(centroid)
            centroid_indices.append(c_idx)  # tieni traccia dei centroidi

            for a, b in [(i, j), (j, h), (i, h)]:
                mean_point = points[[a, b]].mean(axis=0)
                
                # update dictionary and add edge between centroids
                key = (a, b) 
                if key not in segment_to_centroids:
                    segment_to_centroids[key] = []
                else:
                    for centroid_idx in segment_to_centroids[key]:
                        edges.add((c_idx, add_point(mean_point)))
                        edges.add((centroid_idx, add_point(mean_point)))
                segment_to_centroids[key].append(c_idx)
                
                if (a, b) in external_edges or (b, a) in external_edges:
                    border_node = square_intersection(mean_point, centroid)
                    bn_idx = add_point(border_node)
                    for i, coord in enumerate(border_node):
                        for j, value in enumerate([-0.1, 1.1]):
                            # 0, 1, 2, 3 are the indices for the border nodes in the order: left, right, bottom, top
                            if abs(coord - value) < 1e-10:
                                index = (i + 1) * 2 + (j + 1) - 3
                                border_nodes[index].append(bn_idx)
                    edges.add((c_idx, bn_idx))
                    cb_edges.append((c_idx, bn_idx))

        # Aggiungi i 4 vertici agli angoli
        corners = [[-0.1, -0.1], [-0.1, 1.1], [1.1, -0.1], [1.1, 1.1]]
        cns_idxs = []
        for corner in corners:
            cns_idxs.append(add_point(np.array(corner)))
        for dir, points in enumerate(border_nodes):
            
            c0, c1, c2, c3 = cns_idxs
            cns_id = [[c0, c1], [c2, c3], [c0, c2], [c1, c3]][dir]
            if len(points) == 0:
                edges.add((cns_id[0], cns_id[1]))
                continue
            sorted_p = sorted(points, key=lambda idx: (nodes[idx][0], nodes[idx][1]))
            edges.add((sorted_p[0], cns_id[0]))
            edges.add((sorted_p[-1], cns_id[1]))
            for i in range(len(sorted_p) - 1):
                edges.add((sorted_p[i], sorted_p[i + 1]))
        
        
        for (u, v) in cb_edges:
            for (p, q) in cb_edges:
                if u==p and v==q:
                    continue
                # inter = segment_intersection(
                #     points[u], points[v],
                #     points[a], points[b]
                # )

           
        map_graph = Graph(nodes=list(range(len(nodes))), edges=list(edges), points=np.array(nodes))
        map_graph.draw_graph()
        return map_graph
    
    
    def draw_map(self, with_edges=False, with_labels=False):
        map = self.map()
        is_planar, embedding = nx.check_planarity(map)
        if not is_planar:
            print("Il grafo non è planare!")
            return

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
    
    
