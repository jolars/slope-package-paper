import matplotlib.pyplot as plt
import pandas as pd

FULL_WIDTH = 6


def reg_labels(reg):
    """Create a label for the regularization parameter."""
    reg_frac = int(1 / reg)
    return r"$\alpha_\text{max}" + " / " + str(reg_frac) + r"$"


def extract_reg_param(df):
    import re

    df["reg"] = df["objective_name"].str.extract(r"reg=([0-9.]+)")
    df["reg"] = pd.to_numeric(df["reg"])

    return df


def set_plot_defaults():
    plt.rcParams["text.usetex"] = True
    plt.rcParams["font.size"] = 9
    plt.rcParams["axes.labelsize"] = 10
    plt.rcParams["axes.titlesize"] = 10
    plt.rcParams["lines.markersize"] = 3
    plt.rcParams["lines.linewidth"] = 1
    plt.rcParams["legend.frameon"] = False
    plt.rcParams["text.latex.preamble"] = (
        r"\usepackage{mathtools}\usepackage{lmodern}\usepackage{bm}\usepackage{siunitx}"
    )


def legend_labels(solver):
    if "PGD[acceleration=bb" in solver:
        return "BB PGD"
    elif "PGD[acceleration=fista" in solver:
        return "FISTA"
    elif "ADMM" in solver:
        return "ADMM"
    elif "sortedl1" in solver:
        return "sortedl1"
    elif "PGD_safe_screening" in solver:
        return "Safe PGD"
    elif "SlopePath" in solver:
        return "SolutionPath"
    elif "PGD[acceleration=anderson" in solver:
        return "Anderson PGD"
    elif "Newt-ALM" in solver:
        return "Newt-ALM"
    else:
        return solver
