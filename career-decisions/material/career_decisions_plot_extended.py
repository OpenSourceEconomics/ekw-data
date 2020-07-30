"""Figures for career decisions data."""
import os

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import numpy as np
import pandas as pd
from itertools import compress
import colorsys
import matplotlib.colors as mc
from scipy.signal import savgol_filter

savepath = os.environ["PROJECT_ROOT"] + "/career-decisions/material"


def make_grayscale_cmap(cmap):
    """Return a grayscale version of given colormap.

    Parameters:
    -----------
    cmap: matplotlib.colors.LinearSegmentedColormap
        Matplotlib color map (see
        https://matplotlib.org/tutorials/colors/colormaps.html for available
        color maps).

    Returns:
    --------
    cmap: 'matplotlib.colors.LinearSegmentedColormap
        Grayscale version color map of the given non-grayscale color map.

    """

    cmap = plt.cm.get_cmap(cmap)
    colors = cmap(np.arange(cmap.N))

    # Conversion of RGBA to grayscale lum by RGB_weight
    # RGB_weight given by http://alienryderflex.com/hsp.html
    RGB_weight = [0.299, 0.587, 0.114]
    lum = np.sqrt(np.dot(colors[:, :3] ** 2, RGB_weight))
    colors[:, :3] = lum[:, np.newaxis]

    return cmap.from_list(cmap.name + "_grayscale", colors, cmap.N)


def make_color_lighter(color, amount=0.5):
    """Returns a brightened (darkened) color.

    Parameters:
    -----------
    color: matplotlib color string, hex string, RGB tuple
        Name of color that will be brightened.

    amount: positive float
        Amount the color should be brightened (<1) or darkened (>1).

    Returns:
    --------
    _color: matplotlib color string, hex string, RGB tuple
        Brightened-up color (same format).

    """

    try:
        _color = mc.cnames[color]
    except Exception:
        _color = color
    _color = colorsys.rgb_to_hls(*mc.to_rgb(_color))

    return colorsys.hls_to_rgb(_color[0], 1 - amount * (1 - _color[1]), _color[2])


def plot_sample_size(df, color="color"):
    """Plot sample size.

    Parameters:
    -----------
    df: pd.DataFrame
        Dataframe consisting of sample data.

    color: str
        Switch for colored (color = "color")
            or black-white (color = "bw") version.

    Returns:
    --------
    savefig: pdf
        Figure saved as pdf file.

    """

    y = df.groupby("Period")["Age"].count().values
    x = df["Age"].unique()

    fig, ax = plt.subplots()
    ax.bar(x, y, 0.9, color=color_scheme[color]["blue_collar"])

    plt.xticks(list(df.Age[:].unique()))
    ax.set_xlabel("Age")

    ax.yaxis.get_major_ticks()[0].set_visible(False)
    ax.yaxis.set_major_formatter(mtick.StrMethodFormatter("{x:,.0f}"))
    ax.set_ylabel("Individuals")

    fig.savefig(f"{savepath}/fig_sample_size{color_scheme[color]['extension']}.pdf")


def plot_decisions_by_age(df, color="color"):
    """Plot decisions by age.

    Parameters:
    -----------
    df: pd.DataFrame
        Dataframe consisting of decision data.

    color: str
        Switch for colored (color = "color")
            or black-white (color = "bw") version.

    Returns:
    --------
    savefig: pdf
        Figure saved as pdf file.

    """

    # labels = ["blue_collar", "white_collar", "military", "schooling", "home"]

    fig, ax = plt.subplots()

    shares = df.groupby("Age").Choice.value_counts(normalize=True).unstack()[labels] * 100
    # Choices should be ordered: blue_collar, white_collar, military, school, home
    # Black white will be determined via colors here.
    shares.plot.bar(stacked=True, ax=ax, width=0.8, color=list(color_scheme[color].values())[:-1])

    ax.set_xticklabels(np.arange(16, 27, 1), rotation="horizontal")
    ax.yaxis.get_major_ticks()[0].set_visible(False)

    ax.set_ylabel("Share (in %)")
    ax.set_ylim(0, 100)

    ax.legend(
        labels=[label.split("_")[0].capitalize() for label in labels],
        loc="lower center",
        bbox_to_anchor=(0.5, 1.04),
        ncol=5,
    )

    fig.savefig(f"{savepath}/fig_observed_data_choices{color_scheme[color]['extension']}.pdf")


def plot_wage_moments(df, savgol=False, color="color"):
    """Plot mean and std of observed wages in blue, white, and military.

    Parameters:
    -----------
    df: pd.DataFrame
        Dataframe consisting of sample data.

    color: str
        Switch for colored (color = "color")
            or black-white (color = "bw") version.

    savgol: Boolean
        Switch for application of Savitzky-Golay Filtering.

    Returns:
    --------
    savefig: pdf
        Figure saved as pdf file.

    References:
    -----------
    .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
       Data by Simplified Least Squares Procedures. Analytical
       Chemistry, 1964, 36 (8), pp 1627-1639.
    .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
       W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
       Cambridge University Press ISBN-13: 9780521880688

    """

    minimum_observations = 10
    wage_categories = ["blue_collar", "white_collar", "military"]
    # wage_colors = {"blue_collar": "tab:blue", "white_collar": "tab:red", "military": "tab:purple"}

    # moment_settings = {
    #     "mean": {"color_scale": 1,
    #              "label_moment": "Average"},
    #     "std": {"color_scale": 0.6,
    #             "label_moments": "Standard deviation"},
    #     }

    wage_moments = df.groupby(["Age", "Choice"])["Wage"].describe()[["mean", "std"]].unstack()

    for moment in ["mean", "std"]:
        fig, ax = plt.subplots()

        if moment == "mean":
            color_scale = 1
            moment_label = "Average"
        if moment == "std":
            color_scale = 0.6
            moment_label = "Standard deviation"

        for wc in wage_categories:

            # Exlude wage categories with less than `minimum_observations` observations
            sufficient_boolean = list(
                *[df.groupby(["Age"]).Choice.value_counts().unstack()[wc] >= minimum_observations]
            )
            non_sufficient_index = [i for i, bool in enumerate(sufficient_boolean) if bool is False]
            _wage_moments = list(wage_moments[moment][wc])
            sufficient_wage_moments = list(compress(_wage_moments, sufficient_boolean))

            # Application of savgol_filter
            if savgol:
                y = list(savgol_filter(sufficient_wage_moments, 7, 3))
                ext_sg = "_savgol"
            else:
                y = sufficient_wage_moments
                ext_sg = ""

            for i, insertion in enumerate(non_sufficient_index):
                y.insert(insertion + i, np.nan)

            y_plot = pd.DataFrame(y, columns=[moment])
            y_plot.index = list(wage_moments[moment].index)

            ax.plot(
                y_plot, color=make_color_lighter(color_scheme[color][wc], color_scale), label=wc,
            )

        ax.legend(
            labels=[label.split("_")[0].capitalize() for label in wage_categories],
            loc="upper left",
            bbox_to_anchor=(0.2, 1.04),
            ncol=3,
        )

        ax.set_xticks(df["Age"].unique())
        ax.set_xlabel("Age")

        ax.set_ylabel(f"{moment_label} wage (in $ 1,000)", labelpad=20)
        ax.get_yaxis().set_major_formatter(
            plt.FuncFormatter(lambda x, loc: "{0:0,}".format(int(x / 1000)))
        )

        fig.tight_layout()

        fig.savefig(
            f"{savepath}/fig_observed_wage_{moment}{ext_sg}{color_scheme[color]['extension']}.pdf"
        )


def plot_initial_schooling(initial_schooling, color="color"):
    """Illustration of initial schooling frequency.

    Parameters:
    -----------
    initial_schooling: dict
        Dictionary that contains key: value pairs of schooling information
        years, number, and frequency.

    Returns:
    --------
    savefig: pdf
        Figure saved as pdf file.

    """

    fig, ax = plt.subplots()
    ax.bar(
        initial_schooling["years"],
        initial_schooling["frequency"],
        0.8,
        color=color_scheme[color]["blue_collar"],
    )

    ax.set_xlabel("Initial Schooling Level")

    ax.set_ylim([0, 1])
    ax.set_ylabel("Share of Individuals")
    ax.yaxis.get_major_ticks()[0].set_visible(False)

    fig.savefig(f"{savepath}/fig_initial_schooling{color_scheme[color]['extension']}.pdf")


def plot_transition_heatmap(tm, transition_direction="origin_to_destination", color="color"):
    """Illustration of transition probability (od and do) in a heatmap.

    Parameters:
    -----------
    tm: dictionary
        Dictionary of transition matrices for both directions.

    transition_direction: str
        Direction for which the heatmap should be plotted (for subsetting purpose).


    Returns:
    -------
    savefig: pdf
        Figure saved as pdf file.

    """
    label_order = ["blue_collar", "white_collar", "military", "schooling", "home"]
    # Refactor the transition_matrix
    tm = tm[transition_direction]
    tm = tm.reindex(label_order[::-1])

    fig, ax = plt.subplots()

    if color == "color":
        _cmap = "Blues"
        ext = ""
    if color == "bw":
        _cmap = make_grayscale_cmap("Blues")
        ext = "_bw"

    sns.heatmap(
        tm,
        cmap=_cmap,
        annot=True,
        vmin=0,
        vmax=0.75,
        xticklabels=["Blue", "White", "Military", "Schooling", "Home"],
        yticklabels=["Home", "Schooling", "Military", "White", "Blue"],
        ax=ax,
    )

    plt.yticks(rotation=0)
    plt.ylabel("Choice $t$", labelpad=10)
    plt.xlabel("Choice $t+1$", labelpad=10)

    fig.savefig(f"{savepath}/fig_heatmap_transitionprobs{ext}.pdf")


_cmap = make_grayscale_cmap("copper")
color_scheme = {
    "bw": {
        "blue_collar": _cmap(0.29),
        "white_collar": _cmap(0.16),
        "military": _cmap(0.51),
        "school": _cmap(0.93),
        "home": _cmap(0.76),
        "extension": "_bw",
    },
    "color": {
        "blue_collar": "tab:blue",
        "white_collar": "tab:red",
        "military": "tab:purple",
        "school": "tab:orange",
        "home": "tab:green",
        "extension": "",
    },
}

labels = ["blue_collar", "white_collar", "military", "schooling", "home"]

# if __name__ == "__main__":
