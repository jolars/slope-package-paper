import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from slopeutils import FULL_WIDTH, merge_parquet_files, set_plot_defaults

set_plot_defaults()


def extract_path_length(df):
    df["path_length"] = df["objective_name"].str.extract(r"path_length=([0-9.]+)")
    df["path_length"] = pd.to_numeric(df["path_length"])

    return df


results_dir = "results/path_0613"
df = merge_parquet_files(results_dir)
df = extract_path_length(df)


df_subset = df[
    [
        "path_length",
        "data_name",
        "solver_name",
        "idx_rep",
        "stop_val",
        "time",
        "objective_value",
        "objective_max_rel_duality_gap",
    ]
]


# Extract dataset specifics from data_name to create shorter labels
def extract_dataset_name(data_name):
    match = re.search(r"dataset=([^,\]]+)", data_name)
    return match.group(1) if match else "unknown"


# Apply the function to create a shorter dataset identifier
df_subset["dataset"] = df_subset["data_name"].apply(extract_dataset_name)

# Get unique values for facets
path_values = sorted(df_subset["path_length"].unique())
dataset_values = sorted(df_subset["dataset"].unique())
solver_values = sorted(df_subset["solver_name"].unique())

# Create a color palette for solvers
# colors = sns.color_palette("tab10", len(solver_values))
colors = plt.cm.tab10(np.linspace(0, 1, len(solver_values)))
solver_colors = dict(zip(solver_values, colors))

ymax_def = 15
ymin_def = 1e-7

custom_limits = {
    # (50, "Koussounadis2014"): (-0.1, 2.6, ymin_def, ymax_def),
    # (0.1, "Koussounadis2014"): (-0.1, 6, ymin_def, ymax_def),
    # (0.02, "Koussounadis2014"): (-0.5, 33, ymin_def, ymax_def),
    # (0.5, "Rhee2006"): (-0.001, 0.011, ymin_def, ymax_def),
    # (0.1, "Rhee2006"): (-0.001, 0.021, ymin_def, ymax_def),
    # (0.02, "Rhee2006"): (-0.001, 0.045, ymin_def, ymax_def),
    # (0.5, "brca1"): (-0.1, 2.6, ymin_def, ymax_def),
    # (0.1, "brca1"): (-0.2, 9.1, ymin_def, ymax_def),
    # (0.02, "brca1"): (-1, 31, ymin_def, ymax_def),
    # (0.5, "news20.binary"): (-2, 41, ymin_def, ymax_def),
    # (0.1, "news20.binary"): (-3, 81, ymin_def, ymax_def),
    # (0.02, "news20.binary"): (-4, 101, ymin_def, ymax_def),
    # (0.5, "rcv1.binary"): (-0.1, 2.1, ymin_def, ymax_def),
    # (0.1, "rcv1.binary"): (-0.5, 11, ymin_def, ymax_def),
    # (0.02, "rcv1.binary"): (-2, 31, ymin_def, ymax_def),
}

# Create markers for solvers
markers = ["o", "s", "^", "D", "*", "x", "+", "v", "<", ">", "p", "h", "H", "d"]
solver_markers = dict(zip(solver_values, markers[: len(solver_values)]))

# Set up the matplotlib figure and axes grid
fig, axes = plt.subplots(
    len(dataset_values),
    len(path_values),
    figsize=(FULL_WIDTH, 5),
    sharex=False,
    sharey=True,
    constrained_layout=True,
)

# Adjust to handle single row or column case
if len(path_values) == 1 and len(dataset_values) == 1:
    axes = np.array([[axes]])
elif len(path_values) == 1:
    axes = axes.reshape(-1, 1)
elif len(dataset_values) == 1:
    axes = axes.reshape(1, -1)

# Plot data on each subplot
for i, dataset in enumerate(dataset_values):
    for j, path_length in enumerate(path_values):
        ax = axes[i, j]

        # Filter data for this subplot
        subplot_data = df_subset[
            (df_subset["path_length"] == path_length)
            & (df_subset["dataset"] == dataset)
        ]

        y_min = subplot_data["objective_value"].min()

        # Plot each solver
        for solver in solver_values:
            solver_data = subplot_data[subplot_data["solver_name"] == solver]

            if not solver_data.empty:
                solver_data = solver_data.sort_values("time")

                rel_gap = solver_data["objective_max_rel_duality_gap"]

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

        # Set y-axis to log scale
        ax.set_yscale("log")

        if j == len(path_values) - 1:
            ax.yaxis.set_label_position("right")
            ax.set_ylabel(dataset, rotation=270, va="bottom")

        # Set titles and labels
        if i == 0:
            ax.set_title(f"Path length: {path_values[j]}")

        # Apply custom limits if defined for this facet
        facet_key = (path_length, dataset)
        if facet_key in custom_limits:
            x_min, x_max, y_min, y_max = custom_limits[facet_key]
            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)

        # ax.grid(True, linestyle="--", alpha=0.7)


fig.supxlabel("Time (s)")
fig.supylabel("Maximum Relative Duality Gap")

# Create a single legend for all subplots
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
        markersize=6,
    )
    handles.append(line)

    # Create shorter solver labels by extracting key info
    if "[" in solver:
        # Extract the acceleration and prox method if available
        acceleration = re.search(r"acceleration=(\w+)", solver)
        acceleration = acceleration.group(1) if acceleration else ""

        prox = re.search(r"prox=(\w+)", solver)
        prox = prox.group(1) if prox else ""

        # Get the base solver name (before the bracket)
        base_solver = solver.split("[")[0]

        if acceleration and prox:
            short_label = f"{base_solver}[{acceleration},{prox.replace('prox_', '')}]"
        elif acceleration:
            short_label = f"{base_solver}[{acceleration}]"
        elif prox:
            short_label = f"{base_solver}[{prox.replace('prox_', '')}]"
        else:
            short_label = solver
    else:
        short_label = solver

    labels.append(short_label)

# Add the legend below the subplots
fig.legend(
    handles,
    labels,
    loc="outside upper center",
    ncol=min(3, len(solver_values)),
)

# plt.subplots_adjust(top=0.85)  # Make room for the legend at the top
# plt.show()

save_fig = True

if save_fig:
    figpath = "images/benchmark_path_real.pdf"

    fig.savefig(figpath, bbox_inches="tight", pad_inches=0.05)
else:
    plt.show(block=False)
