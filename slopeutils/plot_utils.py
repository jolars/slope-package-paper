import matplotlib.pyplot as plt

FULL_WIDTH = 6


def set_plot_defaults():
    plt.rcParams["text.usetex"] = True
    plt.rcParams["font.size"] = 9
    plt.rcParams["axes.labelsize"] = 10
    plt.rcParams["axes.titlesize"] = 10
    plt.rcParams["lines.markersize"] = 3
    plt.rcParams["lines.linewidth"] = 1
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
