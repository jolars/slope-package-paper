import matplotlib.pyplot as plt
import pandas as pd

# The CSDA elsarticle preprint text block is 390 pt (about 5.4 inches).
# Leave room for the PDF crop and place figures at their exported size.
FULL_WIDTH = 6.2

# Keep solver identities consistent when a figure includes only a subset.
SOLVER_STYLES = {
    "ADMM": ("#1f77b4", "o"),
    "Newt-ALM": ("#ff7f0e", "s"),
    "Anderson PGD": ("#2ca02c", "^"),
    "BB PGD": ("#d62728", "D"),
    "FISTA": ("#9467bd", "*"),
    "Safe PGD": ("#8c564b", "x"),
    "SolutionPath": ("#e377c2", "+"),
    "skglm": ("#7f7f7f", "v"),
    "sortedl1 (ours)": ("#000000", "<"),
    "tick": ("#17becf", ">"),
}


def solver_styles(solvers):
    """Return fixed colors and markers for each solver's legend label."""
    styles = {solver: SOLVER_STYLES[legend_labels(solver)] for solver in solvers}
    colors = {solver: style[0] for solver, style in styles.items()}
    markers = {solver: style[1] for solver, style in styles.items()}
    return colors, markers


def reg_labels(reg):
    """Create a label for the regularization parameter."""
    reg_frac = int(1 / reg)
    return r"$\alpha_\text{max}" + " / " + str(reg_frac) + r"$"


def extract_reg_param(df):
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
        return "sortedl1 (ours)"
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
