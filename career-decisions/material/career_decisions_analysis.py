"""Analysis functions for career decisions data."""
import os

import pandas as pd
import numpy as np

SAVEPATH = os.environ["PROJECT_ROOT"] + "/career-decisions/material"
RAW_DATA = os.environ["PROJECT_ROOT"] + "/career-decisions/career-decisions.raw"


def get_prepare_career_decisions_data(file):
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
    columns = ["Identifier", "Age", "schooling_experience", "Choice", "Wage"]
    dtype = {
        "Identifier": np.int,
        "Age": np.int64,
        "schooling_experience": np.int,
        "Choice": "category",
    }

    # Read the original data file
    df = pd.DataFrame(np.genfromtxt(file), columns=columns).astype(dtype)
    # Labeling different choice categories, introduction period, setting index
    df["Choice"] = df["Choice"].map(
        {1.0: "schooling", 2.0: "home", 3.0: "white_collar", 4.0: "blue_collar", 5.0: "military"}
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
    for occupation in ["blue_collar", "white_collar", "military"]:
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
        "blue_collar",
        "white_collar",
        "military",
        "schooling",
        "home",
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

    table_choices["total"].to_csv(f"{SAVEPATH}/total_choices_by_age.csv")
    table_choices["share"].to_csv(f"{SAVEPATH}/share_choices_by_age.csv")

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

    average_wages.to_csv(f"{SAVEPATH}/average_wages.csv")

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
            DataFrame with "number" of inidividuals with "years" of education and its "frequency".

    """

    initial_schooling = {}

    num_obs = df.groupby("Identifier").schooling_experience.min().count()
    schooling_counts = df.groupby("Identifier").schooling_experience.min().value_counts().to_dict()
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

    df_initial_schooling.to_csv(f"{SAVEPATH}/initial_schooling.csv")

    return [df_initial_schooling, initial_schooling]


def construct_activity_count(agent):
    """Construction of an agent-specific activity count.

    Parameters:
    -----------
        agent: pd.DataFrame
            pd.DataFrame with information on work experience.

    """

    agent["Count White"] = (agent["Choice"] == "white_collar").sum()
    agent["Count Blue"] = (agent["Choice"] == "blue_collar").sum()
    agent["Count School"] = (agent["Choice"] == "schooling").sum()
    agent["Count Home"] = (agent["Choice"] == "home").sum()
    agent["Count Military"] = (agent["Choice"] == "military").sum()
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
        cond = df["schooling_experience"].loc[:] == year

        stats = []
        for label in ["Blue", "White", "Military", "School", "Home", "Total"]:
            stats += [counted_activities["Count " + label][cond].mean()]

        initial_schooling_activity[f"{year}"] = stats

    df_initial_schooling_activity = pd.DataFrame.from_dict(initial_schooling_activity)
    df_initial_schooling_activity.index = [["Blue", "White", "Military", "School", "Home", "Total"]]

    df_initial_schooling_activity.to_csv(f"{SAVEPATH}/initial_schooling_activity.csv")

    return df_initial_schooling_activity


def make_transition_matrix(df, include_fifteen=False):
    """Calculation of transition matrix.

    Parameters:
    -----------
        df: pd.DataFrame
            DataFrame with unique Identifier (agent) containing the choice for each model period.

        include_fifteen: bool
            If True, then schooling of individuals at age 15 will be inferred from age 16 choices.
            Transition probabilities get closer to those reported in KW97, Table 2, p.487.

    Returns:
    --------
        transition_matrix: dict
            Dictionary of transition matrices for both directions.

    """

    _df = df.copy(deep="True")

    if include_fifteen:

        new_row = {
            "Identifier": np.nan,
            "Age": 15,
            "schooling_experience": np.nan,
            "Choice": np.nan,
            "Wage": np.nan,
        }
        _df["Identifier"] = _df.index.get_level_values(0)

        _df = _df.groupby(_df["Identifier"]).apply(lambda x: x.append(new_row, ignore_index=True))
        _df["Identifier"] = _df["Identifier"].ffill()
        _df = _df.groupby(_df["Identifier"]).apply(lambda x: x.sort_values(by=["Age"]))

        cond_1 = _df["Age"].eq(15)
        cond_2 = _df["schooling_experience"].shift(-1).ge(9)
        _df.loc[cond_1 & cond_2, "Choice"] = "schooling"

        cond_2 = _df["schooling_experience"].shift(-1).le(8)
        _df.loc[cond_1 & cond_2, "Choice"] = "home"

    label_order = ["blue_collar", "white_collar", "military", "schooling", "home"]
    _df["Choice_t_minus_one"] = _df["Choice"].groupby("Identifier").apply(lambda x: x.shift(1))
    _df["Choice_t_plus_one"] = _df["Choice"].groupby("Identifier").apply(lambda x: x.shift(-1))

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
            index=_df[_relevant_choice[f"{transition_direction}"]],
            columns=_df["Choice"],
            normalize="index",
        ).round(4)

        transition_matrix[f"{transition_direction}"] = (
            transition_matrix[f"{transition_direction}"].loc[row_order, col_order].round(2)
        )

    return transition_matrix


def get_df_transition_probabilities(tm, direction, save_include_fifteen=False):
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

    if not save_include_fifteen:
        df_trans_probs.to_csv(f"{SAVEPATH}/transition_probabilties_{direction}.csv")
    elif save_include_fifteen:
        df_trans_probs.to_csv(f"{SAVEPATH}/transition_probabilties_{direction}_fifteen.csv")

    return df_trans_probs


# Stand-alone export of tables
if __name__ == "__main__":

    df = get_prepare_career_decisions_data(RAW_DATA)
    df = df.groupby("Identifier").apply(lambda x: get_working_experience(x))

    get_choices(df)

    get_average_wages(df)

    get_initial_schooling(df)
    get_initial_schooling_activity(df)

    get_df_transition_probabilities(make_transition_matrix(df), "origin_to_destination")
    get_df_transition_probabilities(make_transition_matrix(df), "destination_from_origin")
    get_df_transition_probabilities(
        make_transition_matrix(df, include_fifteen=True), "origin_to_destination", True
    )
