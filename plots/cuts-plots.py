from grsc_cb.model import GRSC_CB_Model
from grsc_cb.instance import GRSC_CB_Instance
import numpy as np
import networkx as nx
from grsc_cb.reserve_graph import Graph
import matplotlib.pyplot as plt
from tqdm import tqdm

# number of land parcels
min_n, max_n, step = 10, 110, 10
# number of species
m = 30
# number of max connected areas
k = 3
# range of habitat suitability function
w_min, w_max = 20, 100
# range of costs
c_min, c_max = 1, 100
# lambda percentage threshold
lambda_threshold = 0.05
# buffer size
d = 1
# tau threshold
tau = 0.8

# number of instances per n to average over
N_INSTANCES = 3

cut_keys   = ['corecon-int', 'corecon-frc', 'cover-s1', 'cover-s2', 'scc']
cut_colors = ['mediumorchid', 'darkviolet', 'royalblue', 'cornflowerblue', 'mediumturquoise']
cfg_names  = ['C', 'CB', 'CB+CPH', 'CB+CPH+LBH']


def generate_instance(n):
    G = Graph.random_delaunay(n)
    external_nodes = G.external_nodes()

    c = {i: np.random.randint(c_min, c_max + 1) for i in G.nodes}

    S_1 = list(range(m // 3))
    S_2 = list(range(m // 3, m))
    P_1 = len(S_1)
    P_2 = len(S_2)

    w = {}
    for s in S_1 + S_2:
        prob_zero = 0.2 if s in S_1 else 0.1
        for i in G.nodes:
            if i in external_nodes and s in S_1:
                w[(i, s)] = 0
            elif np.random.rand() < prob_zero:
                w[(i, s)] = 0
            else:
                w[(i, s)] = np.random.randint(w_min, w_max + 1)

    lambda_s = {s: lambda_threshold * sum(w[(i, s)] for i in G.nodes) for s in S_1 + S_2}

    return GRSC_CB_Instance(G, S_1, S_2, P_1, P_2, k, w, lambda_s, c, tau, d)


def run_instance(instance):
    """Runs all 4 configurations on a single instance, returns list of cnt dicts."""
    results = []

    model = GRSC_CB_Model(instance, B=False)
    model.solve()
    results.append(model.cnt)

    model = GRSC_CB_Model(instance)
    model.solve()
    results.append(model.cnt)

    model = GRSC_CB_Model(instance)
    model.solve(cp_heuristic=True)
    results.append(model.cnt)

    model = GRSC_CB_Model(instance)
    model.solve(cp_heuristic=True, lb_heuristic=True)
    results.append(model.cnt)

    return results  # lista di 4 cnt dict, uno per configurazione


def average_cnts(cnt_lists):
    """
    cnt_lists: lista di N_INSTANCES elementi, ognuno è una lista di 4 cnt dict.
    Restituisce una lista di 4 cnt dict con i valori mediati.
    """
    n_configs = len(cnt_lists[0])
    averaged = []
    for cfg_idx in range(n_configs):
        avg = {key: np.mean([run[cfg_idx][key] for run in cnt_lists]) for key in cut_keys}
        averaged.append(avg)
    return averaged


if __name__ == "__main__":
    size_axis = []
    # avg_results[cfg_idx] = lista di cnt dict mediati, uno per ogni n
    avg_results = [[] for _ in cfg_names]

    for n in tqdm(range(min_n, max_n + 1, step), desc="Solving models", unit="n"):
        instance_results = []

        for _ in range(N_INSTANCES):
            instance = generate_instance(n)
            instance_results.append(run_instance(instance))

        averaged = average_cnts(instance_results)
        for cfg_idx, avg_cnt in enumerate(averaged):
            avg_results[cfg_idx].append(avg_cnt)

        size_axis.append(n)

    # --- plot ---
    fig, axes = plt.subplots(1, len(cfg_names), figsize=(14, 5), sharey=True)

    for ax, cfg_idx, name in zip(axes, range(len(cfg_names)), cfg_names):
        bottoms = np.zeros(len(size_axis))
        for key, color in zip(cut_keys, cut_colors):
            values = [avg_results[cfg_idx][n_idx][key] for n_idx in range(len(size_axis))]
            ax.bar(range(len(size_axis)), values, bottom=bottoms,
                   label=key, color=color, alpha=0.85)
            bottoms += np.array(values)
        ax.set_xticks(range(len(size_axis)))
        ax.set_xticklabels(size_axis, rotation=45)
        ax.set_title(name)
        ax.set_xlabel("n")

    axes[0].set_ylabel("Cuts added (avg)")
    axes[0].legend(fontsize=8)
    fig.suptitle(f"Cuts added per configuration (avg over {N_INSTANCES} instances)")
    plt.tight_layout()
    plt.show()