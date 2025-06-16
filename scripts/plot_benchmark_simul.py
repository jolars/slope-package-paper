import glob
import os
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from slopeutils import FULL_WIDTH, merge_parquet_files, set_plot_defaults

set_plot_defaults()


def extract_reg_param(df):
    # Use regex to extract the reg parameter value
    import re

    # Extract the reg value from strings like "SLOPE[fit_intercept=True,q=0.2,reg=0.1]"
    df["reg"] = df["objective_name"].str.extract(r"reg=([0-9.]+)")

    # Convert to numeric type
    df["reg"] = pd.to_numeric(df["reg"])

    return df


# Extract dataset specifics from data_name to create shorter labels
def extract_dataset_name(data_name):
    # Extract n_features and n_samples
    n_features = re.search(r"n_features=(\d+)", data_name).group(1)
    n_samples = re.search(r"n_samples=(\d+)", data_name).group(1)
    return rf"$n={n_samples}$, $p={n_features}$"


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

# Apply the function to create a shorter dataset identifier
simulated_df.loc[:, "dataset"] = simulated_df["data_name"].apply(extract_dataset_name)

# Get unique values for facets
reg_values = np.flip(sorted(simulated_df["reg"].unique()))
dataset_values = sorted(simulated_df["dataset"].unique())
solver_values = sorted(simulated_df["solver_name"].unique())

# Create a color palette for solvers
# colors = sns.color_palette("tab10", len(solver_values))
colors = plt.cm.tab10(np.linspace(0, 1, len(solver_values)))
solver_colors = dict(zip(solver_values, colors))

ymax_def = 2
ymin_def = 1e-7

custom_limits = {
    (0.5, "$n=200$, $p=20000$"): (-0.05, 0.7, ymin_def, ymax_def),
    (0.1, "$n=200$, $p=20000$"): (-0.5, 5.5, ymin_def, ymax_def),
    (0.02, "$n=200$, $p=20000$"): (-1, 21, ymin_def, ymax_def),
    (0.5, "$n=200$, $p=200000$"): (-0.1, 4, ymin_def, ymax_def),
    (0.1, "$n=200$, $p=200000$"): (-0.5, 11, ymin_def, ymax_def),
    (0.02, "$n=200$, $p=200000$"): (-2, 81, ymin_def, ymax_def),
    (0.5, "$n=20000$, $p=200$"): (-0.05, 0.41, ymin_def, ymax_def),
    (0.1, "$n=20000$, $p=200$"): (-0.05, 0.61, ymin_def, ymax_def),
    (0.02, "$n=20000$, $p=200$"): (-0.05, 0.71, ymin_def, ymax_def),
}

# Create markers for solvers
markers = ["o", "s", "^", "D", "*", "x", "+", "v", "<", ">", "p", "h", "H", "d"]
solver_markers = dict(zip(solver_values, markers[: len(solver_values)]))

# Set up the matplotlib figure and axes grid
fig, axes = plt.subplots(
    len(dataset_values),
    len(reg_values),
    figsize=(FULL_WIDTH, 5.5),
    sharex=False,
    sharey=True,
    constrained_layout=True,
)

# Adjust to handle single row or column case
if len(reg_values) == 1 and len(dataset_values) == 1:
    axes = np.array([[axes]])
elif len(reg_values) == 1:
    axes = axes.reshape(-1, 1)
elif len(dataset_values) == 1:
    axes = axes.reshape(1, -1)

# Plot data on each subplot
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

        # Set y-axis to log scale
        ax.set_yscale("log")

        if j == len(reg_values) - 1:
            ax.yaxis.set_label_position("right")
            ax.set_ylabel(dataset, rotation=270, va="bottom")

        # Set titles and labels
        if i == 0:
            ax.set_title(f"Reg: {reg_values[j]}")

        # Apply custom limits if defined for this facet
        facet_key = (reg, dataset)
        if facet_key in custom_limits:
            x_min, x_max, y_min, y_max = custom_limits[facet_key]
            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)

        # ax.grid(True, linestyle="--", alpha=0.7)


fig.supxlabel("Time (s)")
fig.supylabel("Duality Gap")

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

save_fig = True

if save_fig:
    figpath = "images/benchmark_single_simulated.pdf"

    fig.savefig(figpath, bbox_inches="tight", pad_inches=0.05)
else:
    plt.show(block=False)
