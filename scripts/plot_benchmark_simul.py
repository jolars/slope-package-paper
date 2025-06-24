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


def extract_dataset_name(data_name):
    n_features = re.search(r"n_features=(\d+)", data_name).group(1)
    n_samples = re.search(r"n_samples=(\d+)", data_name).group(1)

    n_features = int(n_features)
    n_samples = int(n_samples)

    if n_samples == 200 and n_features == 20000:
        return "High Dim"
    elif n_samples == 200 and n_features == 200000:
        return "High Dim, Sparse"
    elif n_samples == 200000 and n_features == 200:
        return "Low Dim"

    return "Unknown Scenario"


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

simulated_df = df_subset[df_subset["data_name"].str.contains("Simulated")]

simulated_df.loc[:, "dataset"] = simulated_df["data_name"].apply(extract_dataset_name)

reg_values = np.asarray(np.flip(sorted(simulated_df["reg"].unique())), dtype="float64")
dataset_values = sorted(simulated_df["dataset"].unique())
solver_values = sorted(simulated_df["solver_name"].unique())

colors = plt.cm.tab10(np.linspace(0, 1, len(solver_values)))
solver_colors = dict(zip(solver_values, colors))

ymax_def = 2
ymin_def = 1e-7

custom_limits = {
    (0.5, "High Dim"): (-0.05, 0.7, ymin_def, ymax_def),
    (0.1, "High Dim"): (-0.5, 5.5, ymin_def, ymax_def),
    (0.02, "High Dim"): (-1, 21, ymin_def, ymax_def),
    (0.5, "High Dim, Sparse"): (-0.1, 4, ymin_def, ymax_def),
    (0.1, "High Dim, Sparse"): (-0.5, 11, ymin_def, ymax_def),
    (0.02, "High Dim, Sparse"): (-2, 81, ymin_def, ymax_def),
    (0.5, "Low Dim"): (-0.05, 1.6, ymin_def, ymax_def),
    (0.1, "Low Dim"): (-0.05, 3.1, ymin_def, ymax_def),
    (0.02, "Low Dim"): (-0.05, 5.1, ymin_def, ymax_def),
}

markers = ["o", "s", "^", "D", "*", "x", "+", "v", "<", ">", "p", "h", "H", "d"]
solver_markers = dict(zip(solver_values, markers[: len(solver_values)]))

fig, axes = plt.subplots(
    len(dataset_values),
    len(reg_values),
    figsize=(FULL_WIDTH, 5.5),
    sharex=False,
    sharey=True,
    constrained_layout=True,
)

for i, dataset in enumerate(dataset_values):
    for j, reg in enumerate(reg_values):
        ax = axes[i, j]

        # Filter data for this subplot
        subplot_data = simulated_df[
            (simulated_df["reg"] == reg) & (simulated_df["dataset"] == dataset)
        ]

        # Plot each solver
        for solver in solver_values:
            solver_data = subplot_data[subplot_data["solver_name"] == solver]

            if not solver_data.empty:
                # Sort by time to ensure proper line order
                solver_data = solver_data.sort_values("time")

                dual_gap = solver_data["objective_duality_gap"]
                primal = solver_data["objective_value"]
                rel_gap = dual_gap / primal

                # Plot line with markers
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
    figpath = "images/benchmark_single_simulated.pdf"

    fig.savefig(figpath, bbox_inches="tight", pad_inches=0.05)
else:
    plt.show(block=False)
