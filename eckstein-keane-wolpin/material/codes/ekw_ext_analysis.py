"""Analysis functions for career decisions data."""

import pandas as pd
import numpy as np


def get_prepare_ekw_ext_data(file):
    """Read and reformat career decisions data (file).

    Parameters:
    -----------
        file: str
            Path and filename of career decisions data (data to load).

    Returns:
    --------
        df: pd.DataFrame
            Reformatted and indexed DataFrame of career decisions data.

    """

    # Label and format columns
    dtype = {
        "Identifier": np.int,
        "Age": np.int64,
        "Schooling": np.int,
        "Choice": "category",
    }

    # Read the original data file
    df = pd.read_csv(file, dtype=dtype)
    # Labeling different choice categories, introduction period, setting index
    df["Choice"] = df["Choice"].map(
        {
            "schooling": "Schooling",
            "home": "Home",
            "white_collar": "White",
            "blue_collar": "Blue",
            "military": "Military",
        }
    )
    df["Period"] = df["Age"] - 16
    df.set_index(["Identifier", "Period"], inplace=True, drop=True)

    return df


def get_working_experience(agent):
    """Generate work experience for each agent prior to a given year.

    Parameters:
    -----------
        agent: pd.DataFrame
            pd.DataFrame with information on work experience.
    """
    for occupation in ["Blue", "White", "Military"]:
        agent[f"{occupation}_experience"] = (
            (agent["Choice"] == occupation).astype(int).cumsum().shift(1)
        )
    return agent


def get_choices(df):
    """Returns number of choices for each alternative at given age.

    Parameters:
    -----------
        df: pd.DataFrame
            DataFrame with unique Identifier (agent) containing the choice for each model period.

    Returns:
    --------
        table_choices: dict
            Dictionary with "total" choices and the "share" among all individuals.

    """
    crosstab_labels = [
        "Blue",
        "White",
        "Military",
        "Schooling",
        "Home",
        "All",
    ]

    table_choices = {}

    # Get the total number of choices within each alternative
    table_choices["total"] = pd.crosstab(index=df["Age"], columns=df["Choice"], margins=True,)
    table_choices["total"] = table_choices["total"][crosstab_labels]
    table_choices["total"].columns = [label.split("_")[0].capitalize() for label in crosstab_labels]

    # Get the share of choices within each alternative
    table_choices["share"] = pd.crosstab(
        index=df["Age"], columns=df["Choice"], margins=True, normalize="index"
    ).round(4)
    table_choices["share"] = table_choices["share"][crosstab_labels[:-1]] * 100
    table_choices["share"].columns = [
        label.split("_")[0].capitalize() for label in crosstab_labels[:-1]
    ]

    return table_choices


def get_average_wages(df):
    """Get average wages for each occupation at given period (age).

    Parameters:
    -----------
        df: pd.DataFrame
            DataFrame with unique Identifier (agent) containing the choice for each model period.

    Returns:
    --------
        df: pd.DataFrame
            DataFrame with average wages for each occupation at any given period (age).

    """

    average_wages = pd.crosstab(
        index=df["Age"], columns=df["Choice"], values=df["Wage"], aggfunc="mean", margins=True,
    )

    average_wages.columns = [
        label.split("_")[0].capitalize() for label in list(average_wages.keys())
    ]

    return average_wages


def get_initial_schooling(df):
    """Returns information around the initial years of schooling.

    Parameters:
    -----------
        df: pd.DataFrame
            DataFrame with unique Identifier (agent) containing the choice for each model period.

    Returns:
    --------
        initial_schooling: pd.DataFrame
            DataFrame with "number" of individuals with "years" of education and its "frequency".

    """

    initial_schooling = {}

    num_obs = df.groupby("Identifier").Schooling.min().count()
    schooling_counts = df.groupby("Identifier").Schooling.min().value_counts().to_dict()
    years = sorted(schooling_counts.keys())
    edu_level_counts = [
        schooling_counts[edu_level] for edu_level in sorted(schooling_counts.keys())
    ]
    edu_level_freq = list(map(lambda x: x / num_obs, edu_level_counts))

    initial_schooling = {
        "years": years,
        "number": edu_level_counts,
        "frequency": edu_level_freq,
    }

    df_initial_schooling = pd.DataFrame.from_dict(initial_schooling)
    df_initial_schooling.columns = [label.capitalize() for label in list(initial_schooling.keys())]
    df_initial_schooling.set_index("Years")

    return [df_initial_schooling, initial_schooling]


def construct_activity_count(agent):
    """Construction of an agent-specific activity count.

    Parameters:
    -----------
        agent: pd.DataFrame
            pd.DataFrame with information on work experience.

    """

    agent["Count White"] = (agent["Choice"] == "White").sum()
    agent["Count Blue"] = (agent["Choice"] == "Blue").sum()
    agent["Count School"] = (agent["Choice"] == "Schooling").sum()
    agent["Count Home"] = (agent["Choice"] == "Home").sum()
    agent["Count Military"] = (agent["Choice"] == "Military").sum()
    agent["Count Total"] = len(agent)

    return agent


def get_initial_schooling_activity(df):
    """Calculation of initial schooling by alternative choice.

    Parameters:
    -----------
        df: pd.DataFrame
            DataFrame with unique Identifier (agent) containing the choice for each model period.

    Returns:
    --------
        df_initial_schooling_activity: pd.DataFrame
            DataFrame with each alternative and associated initial schooling.

    """

    initial_schooling_activity = {}
    counted_activities = df.groupby("Identifier", axis=0).apply(construct_activity_count)

    for year in get_initial_schooling(df)[1]["years"]:
        cond = df["Schooling"].loc[:] == year

        stats = []
        for label in ["Blue", "White", "Military", "School", "Home", "Total"]:
            stats += [counted_activities["Count " + label][cond].mean()]

        initial_schooling_activity[f"{year}"] = stats

    df_initial_schooling_activity = pd.DataFrame.from_dict(initial_schooling_activity)
    df_initial_schooling_activity.index = [["Blue", "White", "Military", "School", "Home", "Total"]]

    return df_initial_schooling_activity


def make_transition_matrix(df):
    """Calculation of transition matrix.

    Parameters:
    -----------
        df: pd.DataFrame
            DataFrame with unique Identifier (agent) containing the choice for each model period.

    Returns:
    --------
        transition_matrix: dict
            Dictionary of transition matrices for both directions.

    """

    label_order = ["Blue", "White", "Military", "Schooling", "Home"]
    df["Choice_t_minus_one"] = df["Choice"].groupby("Identifier").apply(lambda x: x.shift(1))
    df["Choice_t_plus_one"] = df["Choice"].groupby("Identifier").apply(lambda x: x.shift(-1))

    transition_matrix = {}
    row_order = label_order
    col_order = label_order
    _relevant_choice = {
        "origin_to_destination": "Choice_t_minus_one",
        "destination_from_origin": "Choice_t_plus_one",
    }

    # Origin to destination (t -> t+1)
    # Corresponding to upper cell entry in KW97, p.487, Table 2

    # Destination from origin (t <- t-1)
    # Percentage in t who started from t-1
    # Corresponding to lower cell entry in KW97, p.487, Table 2

    for transition_direction in ["origin_to_destination", "destination_from_origin"]:
        transition_matrix[f"{transition_direction}"] = pd.crosstab(
            index=df[_relevant_choice[f"{transition_direction}"]],
            columns=df["Choice"],
            normalize="index",
        ).round(4)

        transition_matrix[f"{transition_direction}"] = (
            transition_matrix[f"{transition_direction}"].loc[row_order, col_order].round(2)
        )

    return transition_matrix


def get_df_transition_probabilities(tm, direction):
    """Create dataframe of transition probabilities for given direction.

    Parameters:
    -----------
        tm: dict
            Dictionary of transition matrices for both directions.

        direction: str
            "origin_to_destination": Column = origin (t), row = destination (t+1)
                - % column (origin) goes to row (destination).
            "destination_to_origin": Column = destination (t), Row = origin (t-1)
                - % column (origin) that came from row (origin).

    Returns:
    --------
        df_trans_probs: pd.DataFrame
            DataFrame consisting of transition probabilities according
            to specified direction.

    """

    df_trans_probs = tm[direction]
    df_trans_probs.columns, df_trans_probs.index = (
        [label.split("_")[0].capitalize() for label in list(df_trans_probs.columns)],
        [label.split("_")[0].capitalize() for label in list(df_trans_probs.index)],
    )

    return df_trans_probs
