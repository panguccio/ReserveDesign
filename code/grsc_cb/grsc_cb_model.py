import gurobipy as gb
import numpy as np

class GRSC_CB_Model:
    def __init__(self, instance):
        
        self.instance = instance
        self.model = gb.Model("GRSC-CB")
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
            self.model.addConstr(gb.quicksum(instance.w[(i, s)] * self.z[i] for i in instance.v_s(s)) >= instance.lambda_s[s] * self.u[s], name="S1-SQ")

        for s in instance.S_2:
            self.model.addConstr(gb.quicksum(instance.w[(i, s)] * self.x[i] for i in instance.v_s(s)) >= instance.lambda_s[s] * self.u[s], name="S2-SQ")

        self.model.addConstr(gb.quicksum(self.u[s] for s in instance.S_1) >= instance.P_1, name="S1-PROTECT")

        self.model.addConstr(gb.quicksum(self.u[s] for s in instance.S_2) >= instance.P_2, name="S2-PROTECT")

        for i in instance.V:
            self.model.addConstr(self.z[i] <= self.x[i], name=f"LINK")   

        for i in instance.V:
            for j in instance.delta_d(i):
                self.model.addConstr(self.z[i] <= self.x[j], name=f"d-BUFF.1")

        for i in instance.V:  
            self.model.addConstr(self.x[i] <= gb.quicksum(self.z[j] for j in instance.delta_d(i)), name=f"d-BUFF.2")

        self.model.addConstr(gb.quicksum(self.y[j] for j in instance.V) <= instance.k, name=f"NCOMP")

        for i in instance.V:
            self.model.addConstr(self.y[i] <= self.z[i], name=f"YZ")
            
    def solve(self, callback=None):
        self.model.optimize(callback)
        
    def print_solution(self):
        print("Status:", self.model.Status)
        print("Objective:", self.model.ObjVal)

        print("\n--- Variabili x ---")
        for v in self.instance.V:
            print(f"  x[{v}] = {self.x[v].X}")

        print("\n--- Variabili z ---")
        for v in self.instance.V:
            print(f"  z[{v}] = {self.z[v].X}")

        print("\n--- Variabili u ---")
        for s in self.instance.S:
            print(f"  u[{s}] = {self.u[s].X}")
