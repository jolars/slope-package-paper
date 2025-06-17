import glob
import os
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from slopeutils import FULL_WIDTH, legend_labels, merge_parquet_files, set_plot_defaults

set_plot_defaults()


def extract_reg_param(df):
    # Use regex to extract the reg parameter value
    import re

    # Extract the reg value from strings like "SLOPE[fit_intercept=True,q=0.2,reg=0.1]"
    df["reg"] = df["objective_name"].str.extract(r"reg=([0-9.]+)")

    # Convert to numeric type
    df["reg"] = pd.to_numeric(df["reg"])

    return df


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
    return match.group(1) if match else "unknown"


# Apply the function to create a shorter dataset identifier
real_df["dataset"] = real_df["data_name"].apply(extract_dataset_name)

# Get unique values for facets
reg_values = np.flip(sorted(real_df["reg"].unique()))
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
    (0.5, "brca1"): (-0.1, 2.9, ymin_def, ymax_def),
    (0.1, "brca1"): (-0.2, 9.1, ymin_def, ymax_def),
    (0.02, "brca1"): (-1, 16, ymin_def, ymax_def),
    (0.5, "rcv1.binary"): (-0.1, 2.1, ymin_def, ymax_def),
    (0.1, "rcv1.binary"): (-0.5, 11, ymin_def, ymax_def),
    (0.02, "rcv1.binary"): (-2, 31, ymin_def, ymax_def),
    (0.5, "real-sim"): (-0.02, 0.3, ymin_def, ymax_def),
    (0.1, "real-sim"): (-0.1, 2.6, ymin_def, ymax_def),
    (0.02, "real-sim"): (-1, 11, ymin_def, ymax_def),
}

# Create markers for solvers
markers = ["o", "s", "^", "D", "*", "x", "+", "v", "<", ">", "p", "h", "H", "d"]
solver_markers = dict(zip(solver_values, markers[: len(solver_values)]))

# Set up the matplotlib figure and axes grid
fig, axes = plt.subplots(
    len(dataset_values),
    len(reg_values),
    figsize=(FULL_WIDTH, 8.5),
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
fig.supylabel("Relative Duality Gap")

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
        markersize=5,
    )
    handles.append(line)

    short_label = legend_labels(solver)

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
    figpath = "images/benchmark_single_real.pdf"

    fig.savefig(figpath, bbox_inches="tight", pad_inches=0.05)
else:
    plt.show(block=False)
