from grsc_cb_instance import GRSC_CB_Instance

class PartialSolution:
    def __init__(self, instance: GRSC_CB_Instance):
        self.instance = instance
        
        self.Sx = set() # set of reserve (buffer + core) nodes currently selected
        self.Sz = set() # set of core nodes currently selected
        self.W_s = {s: 0 for s in self.instance.S} # suitability score of the current solution for each specie s
