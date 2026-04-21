from grsc_cb_instance import GRSC_CB_Instance

'''Creates a partial solution for the heuristic'''
class PartialSolution:
    def __init__(self, instance: GRSC_CB_Instance):
        self.instance = instance
        
        self.Sx = set() # set of reserve (buffer + core) nodes currently selected
        self.Sz = set() # set of core nodes currently selected
        self.W_s = {s: 0 for s in self.instance.S} # suitability score of the current solution for each specie s

    def add_to_core(self, nodes):
        '''adds a node to the core and all its neighbor to the buffer'''
        for i in nodes:
            self.Sz.add(i)
            self.Sx.add(i)
            for s in self.instance.S_1:
                self.W_s[s] += self.instance.w[(i, s)]
            for j in self.instance.delta_d(i):
                self.Sx.add(j)
                for s in self.instance.S_2:
                    self.W_s[s] += self.instance.w[(j, s)]
    
    def us(self, s):
        '''if suitability quota of a specie is met, returns true, false otherwise'''
        return self.W_s[s] >= self.instance.lambda_s[s]
    
    def protected_S1(self):
        '''returns true if at least P_1 species from S_1 are protected'''
        return sum(1 for s in self.instance.S_1 if self.us(s)) >= self.instance.P_1
    
    def protected_S2(self):
        '''returns true if at least P_2 species from S_2 are protected'''
        return sum(1 for s in self.instance.S_2 if self.us(s)) >= self.instance.P_2
    
    def feasible(self):
        '''returns true if current solution is feasible'''
        return self.protected_S1() and self.protected_S2()
    
    def helpful(self, i):
        '''node i is helpful if adding it to the core increases suitability score'''
        if not self.protected_S1():
            for s in self.instance.S_1:
                if self.instance.w[(i, s)] > 0 and not self.us(s):
                    return True
                
        if not self.protected_S2():
            for s in self.instance.S_2:
                if not self.us(s):
                    if any(self.instance.w[(j, s)] > 0 for j in self.instance.delta_d_plus(i)):
                        return True
        return False

    def terminal_nodes(self):
        terminal_nodes = set()
        
        for i in self.instance.V:
            if i not in self.Sz:
                if self.helpful(i):
                    terminal_nodes.add(i)
                    
        return terminal_nodes
    
    def node_cost_function(self, cost):
        '''this node cost function will be use for the shortest-path calculations'''
        
        def cost_function(i):
            
            Ci = sum(cost[j] for j in (self.instance.delta_d_plus(i) - self.Sx))
            
            prot_S1 = int(self.protected_S1())
            prot_S2 = int(self.protected_S2())
            
            sum_W1 = 0
            for s in self.instance.S_1:
                helpfulness1 = (self.instance.w[(i, s)] + self.W_s[s] - self.instance.lambda_s[s]) * (1 - int(self.us(s)))
                sum_W1 += helpfulness1
            sum_W2 = 0
            for s in self.instance.S_2:
                sum_w = sum(self.instance.w[(j, s)] for j in (self.instance.delta_d_plus(i) - self.Sx))
                helpfulness2 = (sum_w + self.W_s[s] - self.instance.lambda_s[s]) * (1 - int(self.us(s)))
                sum_W2 += helpfulness2
                
            return (Ci + 0.001) / ((sum_W1 * (1 - prot_S1)) + (sum_W2 * (1 - prot_S2)) + 0.0001)
        
        return cost_function
    
    def post_process(self):
        '''once we found a solution we try to improve it by removing unneccessary nodes'''
        improved = True
        while improved:
            improved = False
            for i in self.Sz:
                # find the buffer nodes to remove
                other_cores = self.Sz - {i} #remove i from the core
                other_buffers = set()
                for j in other_cores:
                    other_buffers |= self.instance.delta_d_plus(j)
                removable_buffers = self.instance.delta_d_plus(i) - other_buffers #remove buffer nodes associated to only i
                
                new_Sz = other_cores
                new_Sx = self.Sx - removable_buffers
                new_Ws = {s: 0.0 for s in self.instance.S}
                for j in new_Sz:
                    for s in self.instance.S_1:
                        new_Ws[s] += self.instance.w[(j, s)]
                for j in new_Sx:
                    for s in self.instance.S_2:
                        new_Ws[s] += self.instance.w[(j, s)]
                        
                still_ok = (
                    sum(1 for s in self.instance.S_1 if new_Ws[s] >= self.instance.lambda_s[s]) >= self.instance.P_1
                    and
                    sum(1 for s in self.instance.S_2 if new_Ws[s] >= self.instance.lambda_s[s]) >= self.instance.P_2
                ) #check if the new solution is still feasible
                if still_ok:
                    self.Sz = new_Sz
                    self.Sx = new_Sx
                    self.W_s = new_Ws
                    improved = True
                    break
                
    def objective(self):
        '''returns objective function of the partial solution'''
        return sum(self.instance.c[i] for i in self.Sx)
                        
                
                
            
            
