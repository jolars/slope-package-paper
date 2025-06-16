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
