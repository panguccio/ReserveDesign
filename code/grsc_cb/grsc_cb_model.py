import gurobipy as gb
import numpy as np
import networkx as nx

INF = 1e9
EPS = 1e-6

class GRSC_CB_Model:
    
    def __init__(self, instance, B=False, C=False):
        
        self.instance = instance
        self.model = gb.Model("GRSC-CB")
        self.model.Params.LazyConstraints = 1
        self.model.setParam('OutputFlag', 0)
        
        # VARIABLES
        self.x = self.model.addVars(instance.V, vtype=gb.GRB.BINARY, name="x")
        self.z = self.model.addVars(instance.V, vtype=gb.GRB.BINARY, name="z")
        self.u = self.model.addVars(instance.S, vtype=gb.GRB.BINARY, name="u")
        self.y = self.model.addVars(instance.V, vtype=gb.GRB.BINARY, name="y")
        
        # OBJECTIVE FUNCTION
        self.model.setObjective(gb.quicksum(instance.c[i] * self.x[i] for i in instance.V), gb.GRB.MINIMIZE)
        
        # CONSTRAINTS

        for s in instance.S_1:
            self.model.addConstr(gb.quicksum(instance.w[(i, s)] * self.z[i] for i in instance.v_s(s)) >= instance.lambda_s[s] * self.u[s], name=f"S1-SQ-{s}")

        for s in instance.S_2:
            self.model.addConstr(gb.quicksum(instance.w[(i, s)] * self.x[i] for i in instance.v_s(s)) >= instance.lambda_s[s] * self.u[s], name=f"S2-SQ-{s}")

        self.model.addConstr(gb.quicksum(self.u[s] for s in instance.S_1) >= instance.P_1, name="S1-PROTECT")

        self.model.addConstr(gb.quicksum(self.u[s] for s in instance.S_2) >= instance.P_2, name="S2-PROTECT")

        for i in instance.V:
            self.model.addConstr(self.z[i] <= self.x[i], name=f"LINK-{i}")   

        if B:
            
            for i in instance.V:
                for j in instance.delta_d(i):
                    self.model.addConstr(self.z[i] <= self.x[j], name=f"d-BUFF.1-{i}-{j}")

            for i in instance.V:  
                self.model.addConstr(self.x[i] <= gb.quicksum(self.z[j] for j in instance.delta_d(i)), name=f"d-BUFF.2-{i}")
            
        if C and B:
            
            self.model.addConstr(gb.quicksum(self.y[j] for j in instance.V) <= instance.k, name=f"NCOMP")

            for i in instance.V:
                self.model.addConstr(self.y[i] <= self.z[i], name=f"YZ-{i}")
                
        
        
    def separate_CORECON_fractional(self, z_val, y_val, tau=0.5):
        
        # build flow network
        DG = self.build_flow_network(z_val, y_val)
            
        # separation of fractional solutions
        cuts = []
        
        for l in self.instance.V:
            if z_val[l] < tau:
                continue 
            
            try:
                cut_val, (root_side, l_side) = nx.minimum_cut(
                    DG, 'root', (l, 'out'), capacity='capacity')
            except Exception:
                continue
            
            if cut_val >= z_val[l] - EPS:
                continue
            
            WV = [] # nodes separated by the cut
            WA = [] # arcs with capacity y that are in the cut
            
            for i in self.instance.V:
                i_in = (i, 'in')
                i_out = (i, 'out')
                
                if i_in in root_side and i_out in l_side:
                    if i <= l: # down-lifting, preventing symmetrical solutions
                        WV.append(i)
                
                if i_in not in root_side:
                    if i <= l: # down-lifting
                        WA.append(i)
                        
            if WV or WA:
                cuts.append((WV, WA, l))
                
        return cuts 
    
    def separate_CORECON_integer(self, z_val, y_val):
        G = self.instance.G
        
        cuts = []
        
        core_nodes = [i for i in self.instance.V if z_val[i] > 0.5]
        if not core_nodes:
            return cuts
        
        core_subgraph = G.subgraph(core_nodes)
        
        for component in nx.connected_components(core_subgraph):
            if any(y_val[i] > 0.5 for i in component): # if at least one node is connected to the root
                continue
            
            WA = list(component)
            WV = list({j for i in component for j in G.neighbors(i) if j not in component})
            
            l = min(component) # down-lifting
            cuts.append((WV, WA, l))
        
        return cuts
    
    def separate_COVER(self, z_val, x_val, u_val):
        
        cuts = []
        
        for s in self.instance.S:
            var_val = z_val if s in self.instance.S_1 else x_val
            
            Vs = self.instance.v_s(s)
            if not Vs:
                continue
            
            Ws = sum(self.instance.w[(i, s)] for i in Vs)
            threshold = Ws - self.instance.lambda_s[s]
            
            if threshold <= 0:
                continue
            
            # sorts nodes in non decreasing way by z/w (S_1) or x/w (S_2)
            sorted_Vs = sorted(Vs, key = lambda i: var_val[i] / (self.instance.w[(i, s)] + EPS), reverse=True)
            
            Cs = []
            partial_sum = 0
            for i in sorted_Vs:
                Cs.append(i)
                partial_sum += self.instance.w[(i, s)]
                if partial_sum >= threshold:
                    break
                
            if not Cs:
                continue
            
            if sum(var_val[i] for i in Cs) < u_val[s] - EPS:
                cuts.append((Cs, s))
        
        return cuts
                
    def separate_SCC(self, z_val, y_val, u_val, cover_cuts):
        
        cuts = []
        
        # build a flow network for each specie in S_1 in a cover cut
        for (Cs, s) in cover_cuts:
            if s in self.instance.S_2:
                continue
        
            DG = self.build_flow_network(z_val, y_val, add_sink=True, Cs=Cs)
            
            try:
                cut_val, (root_side, sink_side) = nx.minimum_cut(
                    DG, 'root', 'sink', capacity='capacity')
            except Exception:
                continue
            
            if cut_val >= u_val[s] - EPS:
                continue
            
            WV = [] # nodes separated by the cut
            WA = [] # arcs with capacity y that are in the cut
            
            for i in self.instance.V:
                i_in = (i, 'in')
                i_out = (i, 'out')
                
                if i_in in root_side and i_out in sink_side:
                    WV.append(i)
                
                if i_in not in root_side:
                    WA.append(i)
                        
            if WV or WA:
                cuts.append((WV, WA, s))
            
        return cuts
    
    def build_flow_network(self, z_val, y_val, add_sink = False, Cs = None):    
        DG = nx.DiGraph()
            
        DG.add_node('root')
        if add_sink:
            DG.add_node('sink')
        
        for i in self.instance.V:
            DG.add_edge((i, 'in'), (i, 'out'), capacity=max(0, z_val[i]))
            DG.add_edge('root', (i, 'in'), capacity=max(0, y_val[i]))
            
        for (u, v) in self.instance.E:
            DG.add_edge((u, 'out'), (v, 'in'), capacity=INF)
            DG.add_edge((v, 'out'), (u, 'in'), capacity=INF)
        
        if add_sink:
            for i in Cs:
                DG.add_edge((i, 'out'), 'sink', capacity=INF)
            
        return DG
            
    def solve(self, basic=False, verbose=False):
        
        if not basic:
            self.model.optimize()
            return
        
        def callback(model, where):
            
            # integer solution
            if where == gb.GRB.Callback.MIPSOL:
                z_val = {i: model.cbGetSolution(self.z[i]) for i in self.instance.V}
                y_val = {i: model.cbGetSolution(self.y[i]) for i in self.instance.V}
                
                # separation of CORECON constraints
                for (WV, WA, l) in self.separate_CORECON_integer(z_val, y_val):
                    model.cbLazy(gb.quicksum(self.z[i] for i in WV) + gb.quicksum(self.y[i] for i in WA) >= self.z[l])     
                    if verbose:
                        print(f"Add constraint CORECON (integer): sum(z[i] for i in {WV}) + sum(y[i] for i in {WA}) >= z[{l}]") 
                    
            # fractional solution (LP relaxation)
            if where == gb.GRB.Callback.MIPNODE:
                if self.model.cbGet(gb.GRB.Callback.MIPNODE_STATUS) != gb.GRB.OPTIMAL:
                    return
                
                z_val = {i: model.cbGetNodeRel(self.z[i]) for i in self.instance.V}
                x_val = {i: model.cbGetNodeRel(self.x[i]) for i in self.instance.V}
                y_val = {i: model.cbGetNodeRel(self.y[i]) for i in self.instance.V}
                u_val = {s: model.cbGetNodeRel(self.u[s]) for s in self.instance.S}
                
                violated_inequality_found = False
                
                # separation of COVER constraints
                cover_cuts = self.separate_COVER(z_val, x_val, u_val)
                for (Cs, s) in cover_cuts:
                    if s in self.instance.S_1:
                        model.cbLazy(gb.quicksum(self.z[i] for i in Cs) >= self.u[s])
                        if verbose:
                            print(f"Add constraint COVER (S1): sum(z[i] for i in {Cs}) >= u[{s}]")
                    else:
                        model.cbLazy(gb.quicksum(self.x[i] for i in Cs) >= self.u[s])
                        if verbose:
                            print(f"Add constraint COVER (S2): sum(x[i] for i in {Cs}) >= u[{s}]")
                    violated_inequality_found = True
                
                # separation of SCC constraints
                for (WV, WA, s) in self.separate_SCC(z_val, y_val, u_val, cover_cuts):
                    model.cbLazy(gb.quicksum(self.z[i] for i in WV) + gb.quicksum(self.y[i] for i in WA) >= self.u[s])    
                    if verbose:
                        print(f"Add constraint SCC: sum(z[i] for i in {WV}) + sum(y[i] for i in {WA}) >= u[{s}]")
                    violated_inequality_found = True
                
                # separation of CORECON constraints
                if not violated_inequality_found:
                    for (WV, WA, l) in self.separate_CORECON_fractional(z_val, y_val):
                        model.cbLazy(gb.quicksum(self.z[i] for i in WV) + gb.quicksum(self.y[i] for i in WA) >= self.z[l])    
                        if verbose:
                            print(f"Add constraint CORECON (fractional): sum(z[i] for i in {WV}) + sum(y[i] for i in {WA}) >= z[{l}]")   
        
        self.model.optimize(callback)
    
    def print_graph(self):
        self.instance.draw_graph(self.x, self.z, self.u)
        
    def print_solution(self):
        print("Status:", self.model.Status)
        print("Objective:", self.model.ObjVal)
        if self.model.Status == gb.GRB.OPTIMAL:
            print("Nodes in the reserve (x):", [i for i in self.instance.V if self.x[i].X > 0.5])
            print("Nodes in the core (z):", [i for i in self.instance.V if self.z[i].X > 0.5])
            print("Species protected (u):", [s for s in self.instance.S if self.u[s].X > 0.5])
