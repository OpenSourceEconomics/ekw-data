import matplotlib.ticker as mtick
import matplotlib.pyplot as plt
import matplotlib.colors as mc
import colorsys
import pandas as pd
import numpy as np


fname = "../KW_97.raw"


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
        Brightened-up color (same format)

    """

    try:
        _color = mc.cnames[color]
    except:
        _color = color
    _color = colorsys.rgb_to_hls(*mc.to_rgb(_color))

    return colorsys.hls_to_rgb(_color[0], 1 - amount * (1 - _color[1]), _color[2])


def plot_decision_by_age(df, color="color"):
    """Plot decisions by age.

    Parameters:
    -----------
    df: pd.DataFrame
        Dataframe consisting of decision data.

    color: str
        Set colored or bw version.

    Returns:
    --------
    savefig: pdf
        Figure saved as pdf file.

    """

    age_colors = ["tab:green", "tab:orange", "tab:blue", "tab:red", "tab:purple"]
    labels = ["Home", "Schooling", "Blue", "White", "Military"]

    fig, ax = plt.subplots()

    shares = (
        df.groupby("Age").Choice.value_counts(normalize=True).unstack()[labels] * 100
    )

    if color == "color":
        shares.plot.bar(stacked=True, ax=ax, width=0.8, color=age_colors)
        savename = "fig-observed-data-choices"
    elif color == "bw":
        shares.plot.bar(
            stacked=True, ax=ax, width=0.8, colormap=make_grayscale_cmap("copper")
        )
        savename = "fig-observed-data-choices-bw"

    ax.set_xticklabels(np.arange(16, 27, 1), rotation="horizontal")
    ax.yaxis.get_major_ticks()[0].set_visible(False)

    ax.set_ylabel("Share (in %)")
    ax.set_ylim(0, 100)

    ax.legend(labels=labels, loc="lower center", bbox_to_anchor=(0.5, 1.04), ncol=5)

    fig.savefig(f"{savename}")


def plot_sample_size(df, color="color"):
    """Plot sample size.

    Parameters:
    -----------
    df: pd.DataFrame
        Dataframe consisting of sample data.

    color: str
        Set colored or bw version.

    Returns:
    --------
    savefig: pdf
        Figure saved as pdf file.

    """

    y = df.groupby("Period")["Age"].count().values
    x = df["Age"].unique()

    fig, ax = plt.subplots()

    if color == "color":
        ax.bar(x, y, 0.9)
        savename = "fig-observed-data-sample"
    elif color == "bw":
        _cmap = make_grayscale_cmap("copper")
        ax.bar(x, y, 0.9, color=_cmap(0.25))
        savename = "fig-observed-data-sample-bw"

    plt.xticks(np.arange(16, 27, 1))
    ax.set_xlabel("Age")

    ax.yaxis.get_major_ticks()[0].set_visible(False)
    ax.yaxis.set_major_formatter(mtick.StrMethodFormatter("{x:,.0f}"))
    ax.set_ylabel("Individuals")

    fig.savefig(f"{savename}")


def plot_wage_moments(df, color="color"):
    """Plot mean and std of observed wages in blue, white, and military.

    Parameters:
    -----------
    df: pd.DataFrame
        Dataframe consisting of sample data.

    color: str
        Set colored or bw version.

    Returns:
    --------
    savefig: pdf
        Figure saved as pdf file.

    """

    # Set coloring
    _cmap = make_grayscale_cmap("copper")
    wage_categories = ["Blue", "White", "Military"]
    wage_colors = {"Blue": "tab:blue", "White": "tab:red", "Military": "tab:purple"}
    wage_colors_bw = {"Blue": _cmap(0.5), "White": _cmap(0.7), "Military": _cmap(0.9)}

    # Set bar width
    width = 0.25
    widths = [-width, 0, width]

    wage_moments = (
        df.groupby(["Age", "Choice"])["Wage"].describe()[["mean", "std"]].unstack()
    )

    for moment in ["mean", "std"]:
        fig, ax = plt.subplots()

        if moment == "mean":
            color_scale = 1
        if moment == "std":
            color_scale = 0.8

        for wc, w in zip(wage_categories, widths):

            if color == "color":
                ax.plot(
                    # df["Age"].unique() + w,
                    wage_moments[moment][wc],
                    # width=width,
                    color=make_color_lighter(wage_colors[wc], color_scale),
                    label=wc,
                )
                savename = f"fig-observed-wage-{moment}"

            elif color == "bw":
                ax.plot(
                    # df["Age"].unique() + w,
                    wage_moments[moment][wc],
                    # width=width,
                    color=make_color_lighter(wage_colors_bw[wc], color_scale),
                    label=wc,
                )
                savename = f"fig-observed-wage-{moment}-bw"

        ax.legend(loc="upper left", bbox_to_anchor=(0.2, 1.04), ncol=3)

        ax.set_xticks(df["Age"].unique())
        ax.set_xlabel("Age")

        ax.set_ylabel("Real Wage")
        ax.yaxis.set_major_formatter(mtick.StrMethodFormatter("{x:,.0f}"))

        fig.tight_layout()
        plt.savefig(f"{savename}", dpi=300)


if __name__ == "__main__":

    columns = ["Identifier", "Age", "Schooling", "Choice", "Wage"]
    dtype = {
        "Identifier": np.int,
        "Age": np.int,
        "Schooling": np.int,
        "Choice": "category",
    }

    # Read original data file
    df = pd.DataFrame(np.genfromtxt(fname), columns=columns).astype(dtype)

    # Labeling of chocie categories
    df["Choice"].cat.categories = ["Schooling", "Home", "White", "Blue", "Military"]

    # Start with Period = 0
    df["Period"] = df["Age"] - 16
    df.set_index(["Identifier", "Period"], inplace=True, drop=True)

    # Plot of decisions by age
    plot_decision_by_age(df)
    plot_decision_by_age(df, "bw")

    # Plot of sample size
    plot_sample_size(df)
    plot_sample_size(df, "bw")

    # Plots for mean and std of observed wages
    plot_wage_moments(df)
    plot_wage_moments(df, "bw")
