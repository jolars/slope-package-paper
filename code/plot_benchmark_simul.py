import argparse
import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.append(str(Path(__file__).resolve().parents[1]))

from slopeutils import (
    FULL_WIDTH,
    extract_reg_param,
    legend_labels,
    load_benchmark_results,
    reg_labels,
    set_plot_defaults,
    solver_styles,
)
from slopeutils.plot_utils import save_paper_figure

set_plot_defaults()


def extract_dataset_name(data_name):
    n_features = re.search(r"n_features=(\d+)", data_name).group(1)
    n_samples = re.search(r"n_samples=(\d+)", data_name).group(1)
    density = re.search(r"X_density=([\d.]+)", data_name).group(1)

    n_features = int(n_features)
    n_samples = int(n_samples)
    density = float(density)

    if n_features > n_samples:
        return "High Dim, Sparse" if density < 1 else "High Dim"
    elif n_samples > n_features:
        return "Low Dim"

    return "Square"


parser = argparse.ArgumentParser(description="Plot single-penalty convergence curves")
parser.add_argument(
    "--results",
    default="results/single_1007",
    help="Benchopt table directory or Metewand JSON export",
)
parser.add_argument("--output", help="Destination PDF")
args = parser.parse_args()
df = load_benchmark_results(args.results)
df = df[df["time"] <= 30].copy()
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
        "implementation_rep",
        "trajectory_id",
        "partial",
    ]
]

simulated_df = df_subset[df_subset["data_name"].str.contains("Simulated")].copy()

simulated_df.loc[:, "dataset"] = simulated_df["data_name"].apply(extract_dataset_name)

reg_values = np.asarray(np.flip(sorted(simulated_df["reg"].unique())), dtype="float64")
dataset_values = sorted(simulated_df["dataset"].unique())
solver_values = sorted(simulated_df["solver_name"].unique())

solver_colors, solver_markers = solver_styles(solver_values)

ymax_def = 2
ymin_def = 1e-7

custom_limits = {
    (0.5, "High Dim"): (-0.05, 0.7, ymin_def, ymax_def),
    (0.1, "High Dim"): (-0.5, 5.5, ymin_def, ymax_def),
    (0.02, "High Dim"): (-1, 21, ymin_def, ymax_def),
    (0.5, "High Dim, Sparse"): (-0.1, 4, ymin_def, ymax_def),
    (0.1, "High Dim, Sparse"): (-0.5, 11, ymin_def, ymax_def),
    (0.02, "High Dim, Sparse"): (-2, 30, ymin_def, ymax_def),
    (0.5, "Low Dim"): (-0.05, 0.5, ymin_def, ymax_def),
    (0.1, "Low Dim"): (-0.05, 1.2, ymin_def, ymax_def),
    (0.02, "Low Dim"): (-0.05, 2.1, ymin_def, ymax_def),
}

fig, axes = plt.subplots(
    len(dataset_values),
    len(reg_values),
    figsize=(FULL_WIDTH, 5.5),
    squeeze=False,
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
            solver_groups = subplot_data[subplot_data["solver_name"] == solver].groupby(
                ["data_name", "implementation_rep", "idx_rep", "trajectory_id"],
                dropna=False,
            )

            for _, solver_data in solver_groups:
                solver_data = solver_data.sort_values("time")

                dual_gap = solver_data["objective_duality_gap"]
                primal = solver_data["objective_value"]
                rel_gap = dual_gap / primal

                # Plot line with markers
                ax.semilogy(
                    solver_data["time"],
                    rel_gap,
                    marker=solver_markers[solver],
                    linestyle="--" if solver_data["partial"].any() else "-",
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
    ncol=min(4, len(solver_values)),
)

save_fig = True

if save_fig:
    figpath = args.output or "images/benchmark_single_simulated.pdf"
    Path(figpath).parent.mkdir(parents=True, exist_ok=True)
    save_paper_figure(fig, figpath, bbox_inches="tight", pad_inches=0.05)
else:
    plt.show(block=False)
