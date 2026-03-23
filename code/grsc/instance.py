class GRSCInstance:
    def __init__(self):
        self.V = list(range(5))
        self.S = list(range(12))
        self.S_1 = list(range(6))
        self.S_2 = list(range(6, 12))
        self.P_1 = 6
        self.P_2 = 6

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
        V_S = []
        for v in self.V:
            if self.w(v, s) > 0:
                V_S.append(v)
        return V_S
        
    
    def l(self, s):
        return 3 if s < 6 else 5