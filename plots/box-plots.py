from grsc_cb.model import GRSC_CB_Model
from grsc_cb.instance import GRSC_CB_Instance
import numpy as np
from grsc_cb.reserve_graph import Graph
import matplotlib.pyplot as plt
from tqdm import tqdm

# number of land parcels
min_n, max_n, step = 2000, 2000, 1
m = 30
k = 3
w_min, w_max = 20, 100
c_min, c_max = 1, 100
lambda_threshold = 0.05
d = 1
tau = 0.8
N_RUNS = 10

configs = [
    ('Basic',                         dict(cp_heuristic=False, lb_heuristic=False, verbose=True), 'yellowgreen'),
    ('+ Primal & Construction',        dict(cp_heuristic=True,  lb_heuristic=False, verbose=True), 'deepskyblue'),
    ('+ Local Branching',              dict(cp_heuristic=True,  lb_heuristic=True, verbose=True),  'navy'),
]


def generate_instance(n):
    G = Graph.random_delaunay(n)
    external_nodes = G.external_nodes()
    c = {i: np.random.randint(c_min, c_max + 1) for i in G.nodes}
    S_1 = list(range(m // 3))
    S_2 = list(range(m // 3, m))
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
    return GRSC_CB_Instance(G, S_1, S_2, len(S_1), len(S_2), k, w, lambda_s, c, tau, d)


if __name__ == "__main__":
    size_axis = list(range(min_n, max_n + 1, step))

    # data[cfg_label][n_idx] = lista di tempi per i N_RUNS run
    data = {label: [[] for _ in size_axis] for label, _, _ in configs}

    for n_idx, n in enumerate(tqdm(size_axis, desc="Solving models")):
        for _ in range(N_RUNS):
            instance = generate_instance(n)
            for label, solve_kwargs, _ in configs:
                model = GRSC_CB_Model(instance, B=False, C=False)
                model.solve(**solve_kwargs)
                model.print_solution()
                t = model.get_time()
                if t is not None:
                    data[label][n_idx].append(t)

    # --- box plot ---
    # --- box plot raggruppato per n ---
    fig, ax = plt.subplots(figsize=(16, 6))

    n_groups = len(size_axis)
    n_configs = len(configs)
    group_width = 0.8
    box_width = group_width / n_configs

    for cfg_idx, (label, _, color) in enumerate(configs):
        # posizioni dei box per questa configurazione
        positions = [
            n_idx * (n_configs + 1) + cfg_idx * box_width * n_configs / group_width
            for n_idx in range(n_groups)
        ]
        box_data = [data[label][n_idx] for n_idx in range(n_groups)]

        bp = ax.boxplot(
            box_data,
            positions=positions,
            widths=box_width * n_configs / (n_configs + 1),
            patch_artist=True,
            manage_ticks=False,
            medianprops=dict(color='black', linewidth=2),
        )
        for patch in bp['boxes']:
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        for whisker in bp['whiskers']:
            whisker.set(color=color, linewidth=1.5, linestyle='--')
        for cap in bp['caps']:
            cap.set(color=color, linewidth=1.5)
        for flier in bp['fliers']:
            flier.set(marker='o', color=color, alpha=0.5, markersize=4)

        # segnaposto per la legenda
        ax.plot([], [], color=color, linewidth=6, alpha=0.7, label=label)

    # tick centrati su ogni gruppo
    group_centers = [
        n_idx * (n_configs + 1) + (n_configs - 1) * box_width * n_configs / (2 * group_width)
        for n_idx in range(n_groups)
    ]
    ax.set_xticks(group_centers)
    ax.set_xticklabels(size_axis, rotation=45)
    ax.set_xlabel("n")
    ax.set_ylabel("Time (s)")
    ax.set_title(f"GRSC-CB Solving Time — {N_RUNS} runs per instance")
    ax.legend()
    plt.tight_layout()
    plt.show()