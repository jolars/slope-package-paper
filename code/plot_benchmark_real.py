import re

import matplotlib.pyplot as plt
import numpy as np

from slopeutils import (
    FULL_WIDTH,
    extract_reg_param,
    legend_labels,
    merge_parquet_files,
    reg_labels,
    set_plot_defaults,
)

set_plot_defaults()


results_dir = "results/single_0612"
df = merge_parquet_files(results_dir)
df = extract_reg_param(df)

df_subset = df[
    [
        "reg",
        "data_name",
        "solver_name",
        "idx_rep",
        "stop_val",
        "time",
        "objective_value",
        "objective_duality_gap",
    ]
]

real_df = df_subset[df_subset["data_name"].str.contains("breheny|libsvm")]


# Extract dataset specifics from data_name to create shorter labels
def extract_dataset_name(data_name):
    match = re.search(r"dataset=([^,\]]+)", data_name)
    x = match.group(1) if match else "unknown"

    if x == "brca1":
        return "BRCA1"
    elif x == "rcv1.binary":
        return "RCV1"
    elif x == "real-sim":
        return "Real-Sim"
    else:
        return x


# Apply the function to create a shorter dataset identifier
real_df["dataset"] = real_df["data_name"].apply(extract_dataset_name)

# Get unique values for facets
reg_values = np.asarray(np.flip(sorted(real_df["reg"].unique())), dtype="float64")
dataset_values = sorted(real_df["dataset"].unique())
solver_values = sorted(real_df["solver_name"].unique())

# Create a color palette for solvers
# colors = sns.color_palette("tab10", len(solver_values))
colors = plt.cm.tab10(np.linspace(0, 1, len(solver_values)))
solver_colors = dict(zip(solver_values, colors))

ymax_def = 15
ymin_def = 1e-7

custom_limits = {
    (0.5, "Koussounadis2014"): (-0.1, 2.6, ymin_def, ymax_def),
    (0.1, "Koussounadis2014"): (-0.1, 6, ymin_def, ymax_def),
    (0.02, "Koussounadis2014"): (-0.5, 23, ymin_def, ymax_def),
    (0.5, "Scheetz2006"): (-0.01, 0.6, ymin_def, ymax_def),
    (0.1, "Scheetz2006"): (-0.1, 3.2, ymin_def, ymax_def),
    (0.02, "Scheetz2006"): (-0.1, 3.2, ymin_def, ymax_def),
    (0.5, "BRCA1"): (-0.1, 2.9, ymin_def, ymax_def),
    (0.1, "BRCA1"): (-0.2, 9.1, ymin_def, ymax_def),
    (0.02, "BRCA1"): (-1, 16, ymin_def, ymax_def),
    (0.5, "RCV1"): (-0.1, 2.1, ymin_def, ymax_def),
    (0.1, "RCV1"): (-0.5, 11, ymin_def, ymax_def),
    (0.02, "RCV1"): (-2, 31, ymin_def, ymax_def),
    (0.5, "Real-Sim"): (-0.02, 0.3, ymin_def, ymax_def),
    (0.1, "Real-Sim"): (-0.1, 2.6, ymin_def, ymax_def),
    (0.02, "Real-Sim"): (-1, 11, ymin_def, ymax_def),
}

# Create markers for solvers
markers = ["o", "s", "^", "D", "*", "x", "+", "v", "<", ">", "p", "h", "H", "d"]
solver_markers = dict(zip(solver_values, markers[: len(solver_values)]))

# Set up the matplotlib figure and axes grid
fig, axes = plt.subplots(
    len(dataset_values),
    len(reg_values),
    figsize=(FULL_WIDTH, 8),
    sharex=False,
    sharey=True,
    constrained_layout=True,
)

for i, dataset in enumerate(dataset_values):
    for j, reg in enumerate(reg_values):
        ax = axes[i, j]

        subplot_data = real_df[
            (real_df["reg"] == reg) & (real_df["dataset"] == dataset)
        ]

        y_min = subplot_data["objective_value"].min()

        # Plot each solver
        for solver in solver_values:
            solver_data = subplot_data[subplot_data["solver_name"] == solver]

            if not solver_data.empty:
                solver_data = solver_data.sort_values("time")

                dual_gap = solver_data["objective_duality_gap"]
                primal = solver_data["objective_value"]
                rel_gap = dual_gap / primal

                subopt = primal - y_min

                ax.semilogy(
                    solver_data["time"],
                    rel_gap,
                    marker=solver_markers[solver],
                    linestyle="-",
                    color=solver_colors[solver],
                    label=solver,
                    markerfacecolor="white",
                    markeredgecolor=solver_colors[solver],
                )

        ax.set_yscale("log")

        if j == len(reg_values) - 1:
            ax.yaxis.set_label_position("right")
            ax.set_ylabel(dataset, rotation=270, va="bottom")

        if i == 0:
            ax.set_title(reg_labels(reg))

        # Apply custom limits if defined for this facet
        facet_key = (reg, dataset)
        if facet_key in custom_limits:
            x_min, x_max, y_min, y_max = custom_limits[facet_key]
            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)


fig.supxlabel("Time (s)")
fig.supylabel("Relative Duality Gap")

handles, labels = [], []
for solver in solver_values:
    line = plt.Line2D(
        [0],
        [0],
        color=solver_colors[solver],
        marker=solver_markers[solver],
        linestyle="-",
        markerfacecolor="white",
        markeredgecolor=solver_colors[solver],
        markersize=5,
    )
    handles.append(line)

    short_label = legend_labels(solver)

    labels.append(short_label)

fig.legend(
    handles,
    labels,
    loc="outside upper center",
    ncol=min(3, len(solver_values)),
)

save_fig = True

if save_fig:
    figpath = "images/benchmark_single_real.pdf"

    fig.savefig(figpath, bbox_inches="tight", pad_inches=0.05)
else:
    plt.show(block=False)
