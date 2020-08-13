"""Auxiliary functions."""

from IPython.display import display_html


def display_side_by_side(*args):
    """Displays pd.DataFrames side by side in Jupyter notebooks"""

    html_str = ""
    for df in args:
        html_str += df.to_html()
    display_html(html_str.replace("table", 'table style="display:inline"'), raw=True)
