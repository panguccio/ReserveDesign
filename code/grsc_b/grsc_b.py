import gurobipy as gb
import numpy as np
from instance_2 import GRSC_BInstance

instance = GRSC_BInstance()
grsc = gb.Model("grsc")
grsc.setParam('OutputFlag', 0)

x = grsc.addVars(instance.V, vtype=gb.GRB.BINARY, name="x")
z = grsc.addVars(instance.V, vtype=gb.GRB.BINARY, name="z")
u = grsc.addVars(instance.S, vtype=gb.GRB.BINARY, name="u")

grsc.setObjective(gb.quicksum(instance.c(v) * x[v] for v in instance.V), gb.GRB.MINIMIZE)

for s in instance.S_1:
    grsc.addConstr(gb.quicksum(instance.w(v, s) * z[v] for v in instance.v_s(s)) >= instance.l(s) * u[s], name="S1-SQ")

for s in instance.S_2:
    grsc.addConstr(gb.quicksum(instance.w(v, s) * x[v] for v in instance.v_s(s)) >= instance.l(s) * u[s], name="S2-SQ")
    
grsc.addConstr(gb.quicksum(u[s] for s in instance.S_1) >= instance.P_1, name="S1-PROTECT")
grsc.addConstr(gb.quicksum(u[s] for s in instance.S_2) >= instance.P_2, name="S2-PROTECT")

for v in instance.V:
    grsc.addConstr(z[v] <= x[v], name=f"LINK")
   


for v in instance.V:
    delta = instance.neighborhood(v, d=3)
    for j in delta:
        grsc.addConstr(z[v] <= x[j], name=f"d-BUFF.1")
    grsc.addConstr(x[v] <= gb.quicksum(z[j] for j in delta), name=f"d-BUFF.2")
grsc.optimize()


print("Status:", grsc.Status)
print("Objective:", grsc.ObjVal)

print("\n--- Variabili x ---")
for v in instance.V:
    print(f"  x[{v}] = {x[v].X}")

print("\n--- Variabili z ---")
for v in instance.V:
    print(f"  z[{v}] = {z[v].X}")

print("\n--- Variabili u ---")
for s in instance.S:
    print(f"  u[{s}] = {u[s].X}")