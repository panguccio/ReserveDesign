from grsc_cb_instance import GRSC_CB_Instance

class PartialSolution:
    def __init__(self, instance: GRSC_CB_Instance):
        self.instance = instance
        
        self.Sx = set() # set of reserve (buffer + core) nodes currently selected
        self.Sz = set() # set of core nodes currently selected
        self.W_s = {s: 0 for s in self.instance.S} # suitability score of the current solution for each specie s

    def add_to_core(self, nodes):
        for i in nodes:
            self.Sz.add(i)
            self.Sx.add(i)
            for s in self.instance.S_1:
                self.W_s[s] += self.instance.w[(i, s)]
            for j in self.instance.delta_d(i):
                self.Sx.add(j)
                for s in self.instance.S_2:
                    self.W_s[s] += self.instance.w[(j, s)]
    
    # if suitability quota of a specie is met, returns true, false otherwise
    def us(self, s):
        return self.W_s[s] >= self.instance.lambda_s[s]
    
    def protected_S1(self):
        return sum(1 for s in self.instance.S_1 if self.us(s)) >= self.instance.P_1
    
    def protected_S2(self):
        return sum(1 for s in self.instance.S_2 if self.us(s)) >= self.instance.P_2
    
    def feasible(self):
        return self.protected_S1() and self.protected_S2()
    
    def helpful(self, i):
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
    
                
        