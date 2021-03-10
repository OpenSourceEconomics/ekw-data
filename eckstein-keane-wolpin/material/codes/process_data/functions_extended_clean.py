"""This script contains the functions used in extended_kw97_dataclean.py
"""

from heapq import nlargest
import math
import numpy as np
import pandas as pd


def get_occ_hours(agent):
    """This function calculates the amount of hours worked in each occupation in a given year."""
    for occ in ["white_collar", "blue_collar"]:

        agent[occ.upper() + "_HOURS"] = 0

        for week_num in [1, 7, 13, 14, 20, 26]:
            cond = (agent["OCC_JC_WK_" + repr(week_num)].shift(-1) == occ).astype(int).fillna(0)
            agent[occ.upper() + "_HOURS"] += (
                agent["EMP_HOURS_WK_" + repr(week_num)].shift(-1).fillna(0).mul(cond)
            )

        for week_num in [40, 46, 52]:
            cond = (agent["OCC_JC_WK_" + repr(week_num)] == occ).astype(int).fillna(0)
            agent[occ.upper() + "_HOURS"] += (
                agent["EMP_HOURS_WK_" + repr(week_num)].fillna(0).mul(cond)
            )

    return agent


def weeks_hours_worked(agent):
    """This function creates the variables that are necessary to check the requirements for
    the work choices, i. e. it creates a variable for the number of weeks in a year
    (of the 9 representative weeks) that an individual worked, the number of weeks for which
    the EMP_STATUS variable was not missing, i.e. not equal to 0, and a variable for the
    number of hours that an individual worked in a given year.
    """

    # Weeks worked in civilian or military occupation (labor force status == 7 or >= 100)
    agent["WORKED_WEEKS"] = 0

    # Weeks worked in the military
    agent["WORKED_WEEKS_MILITARY"] = 0

    # Weeks in which labor force status is non-missing (!= 0)
    agent["EMP_NONMISSING_WEEKS"] = 0

    # Amount of hours worked in a given year
    agent["WORKED_HOURS"] = 0

    # List to store all weekly hour information (of the relevant 9 weeks) in a given year
    agent["HOURS_LIST"] = agent.apply(lambda x: [], axis=1)

    for week_num in [40, 46, 52]:
        # Condition that individual worked in a non-military occupation (labor-force status >= 100)
        cond_1 = agent["EMP_STATUS_WK_" + repr(week_num)].ge(100).astype(int)

        # Condition that individual worked in the military  (labor-force status == 7)
        cond_2 = agent["EMP_STATUS_WK_" + repr(week_num)].eq(7.0).astype(int)

        agent["WORKED_WEEKS"] += (cond_1 | cond_2).astype(float)

        agent["WORKED_WEEKS_MILITARY"] += cond_2.astype(float)

        cond_3 = (
            agent["EMP_STATUS_WK_" + repr(week_num)].ne(0)
            & ~agent["EMP_STATUS_WK_" + repr(week_num)].isna()
        )
        agent["EMP_NONMISSING_WEEKS"] += cond_3.astype(int)

        agent["HOURS_LIST"] = agent["HOURS_LIST"] + agent["EMP_HOURS_WK_" + repr(week_num)].fillna(
            0
        ).mul(cond_1).apply(lambda x: [x])

    for week_num in [1, 7, 13, 14, 20, 26]:
        cond_1 = agent["EMP_STATUS_WK_" + repr(week_num)].shift(-1).ge(100).astype(int)
        cond_2 = agent["EMP_STATUS_WK_" + repr(week_num)].shift(-1).eq(7.0).astype(int)

        agent["WORKED_WEEKS"] += (cond_1 | cond_2).astype(float)

        agent["WORKED_WEEKS_MILITARY"] += cond_2.astype(float)

        cond_3 = (
            agent["EMP_STATUS_WK_" + repr(week_num)].shift(-1).ne(0)
            & ~agent["EMP_STATUS_WK_" + repr(week_num)].shift(-1).isna()
        )
        agent["EMP_NONMISSING_WEEKS"] += cond_3.astype(int)

        agent["HOURS_LIST"] = agent["HOURS_LIST"] + agent["EMP_HOURS_WK_" + repr(week_num)].shift(
            -1
        ).fillna(0).mul(cond_1).apply(lambda x: [x])

    agent["WORKED_HOURS"] = agent["HOURS_LIST"].apply(lambda x: sum(x))

    # number of weekly hours worked which are necessary to determine the
    # 'average hours worked' criterion (subtract weeks in military as no information
    # on weekly hours worked is available for them)
    agent["NECESSARY_WEEKS_WORKED"] = (agent["EMP_NONMISSING_WEEKS"] * (2 / 3)).apply(
        lambda x: math.ceil(x)
    ) - agent["WORKED_WEEKS_MILITARY"]

    # initialize a list of the n highest values of "hours worked per week" in a given year
    # where n is equal to the value of 'NECESSARY_WEEKS_WORKED'
    agent["MAX_HOURS"] = np.nan

    for num in [1, 2, 3, 4, 5, 6]:
        cond = agent["NECESSARY_WEEKS_WORKED"].eq(num)
        agent.loc[cond, "MAX_HOURS"] = agent.loc[cond, "HOURS_LIST"].apply(
            lambda x: nlargest(num, x)
        )

    cond = agent["MAX_HOURS"].isna()
    agent.loc[cond, "MAX_HOURS"] = agent.loc[cond, "MAX_HOURS"].apply(lambda x: [])

    # sum the values included in 'MAX_HOURS'
    agent["SUM_MAX_HOURS"] = agent["MAX_HOURS"].apply(lambda x: sum(x))

    return pd.DataFrame(agent)


def clean_missing_wages(agent):
    agent["MISSPECIFIED_EMP_STATUS"] = 0

    for week_num in [1, 7, 13, 14, 20, 26]:
        cond = (
            agent["EMP_STATUS_WK_" + repr(week_num)].shift(-1).ge(100)
            & agent["WAGE_WK_" + repr(week_num)].shift(-1).isna()
        )
        agent["MISSPECIFIED_EMP_STATUS"] += cond.astype(int)

    for week_num in [40, 46, 52]:
        cond = (
            agent["EMP_STATUS_WK_" + repr(week_num)].ge(100)
            & agent["WAGE_WK_" + repr(week_num)].isna()
        )
        agent["MISSPECIFIED_EMP_STATUS"] += cond.astype(int)

    return agent


def create_wages(agent):
    """This function creates real incomes for a given individual working in either
    a blue-collar or white-collar occupation following the instructions on page 484 of KW97.
    Additionally, we also compute the corresponding average hourly wage
    """

    agent = clean_missing_wages(agent)

    agent["SUM_WEEKLY_WAGES"] = 0
    agent["AVG_WEEKLY_WAGE"] = np.nan
    agent["WEEKS_IN_MAJOR_OCC"] = 0
    agent["SUM_HOURLY_WAGES"] = 0

    for week_num in [1, 7, 13, 14, 20, 26]:
        cond = (agent["OCC_JC_WK_" + repr(week_num)].shift(-1) == agent["CHOICE"]).astype(int)
        nominal_weekly_wage = agent["WAGE_WK_" + repr(week_num)].shift(-1) * agent[
            "EMP_HOURS_WK_" + repr(week_num)
        ].shift(-1)
        agent["SUM_WEEKLY_WAGES"] += (
            nominal_weekly_wage / agent["GNP_DEFL_BASE_1987"].shift(-1) * cond
        ).fillna(0)
        agent["WEEKS_IN_MAJOR_OCC"] += cond
        agent["SUM_HOURLY_WAGES"] += agent["WAGE_WK_" + repr(week_num)].shift(-1) / agent[
            "GNP_DEFL_BASE_1987"
        ].shift(-1)

    for week_num in [40, 46, 52]:
        cond = (agent["OCC_JC_WK_" + repr(week_num)] == agent["CHOICE"]).astype(int)
        nominal_weekly_wage = (
            agent["WAGE_WK_" + repr(week_num)] * agent["EMP_HOURS_WK_" + repr(week_num)]
        )
        agent["SUM_WEEKLY_WAGES"] += (
            nominal_weekly_wage / agent["GNP_DEFL_BASE_1987"] * cond
        ).fillna(0)
        agent["WEEKS_IN_MAJOR_OCC"] += cond
        agent["SUM_HOURLY_WAGES"] += (
            agent["WAGE_WK_" + repr(week_num)] / agent["GNP_DEFL_BASE_1987"]
        )

    agent["AVG_WEEKLY_WAGE"] = agent["SUM_WEEKLY_WAGES"] / (agent["WEEKS_IN_MAJOR_OCC"] * 100)

    agent["AVERAGE_HOURLY_WAGES"] = agent["SUM_HOURLY_WAGES"] / (agent["WEEKS_IN_MAJOR_OCC"] * 100)

    agent["AVERAGE_HOURLY_WAGES"].replace(np.inf, np.nan, inplace=True)

    agent["INCOME"] = np.nan

    cond = agent["CHOICE"].isin(["blue_collar", "white_collar"])
    agent.loc[cond, "INCOME"] = agent.loc[cond, "AVG_WEEKLY_WAGE"] * 50

    cond = agent["MISSPECIFIED_EMP_STATUS"].ge(1)
    agent.loc[cond, "INCOME"] = np.nan

    agent.drop(
        columns=["SUM_WEEKLY_WAGES", "AVG_WEEKLY_WAGE", "WEEKS_IN_MAJOR_OCC", "SUM_HOURLY_WAGES"],
        inplace=True,
    )

    return pd.DataFrame(agent)


def create_military_wages(agent):
    """This function creates real and nominal incomes in the military for a given individual
    following the instructions on page 484 of KW97. As there is no information on hours worked
    when an individual is in the military, average hours worked per week are assumed to be
    constant across weeks.
    """

    agent["SUM_MILITARY_INCOME"] = 0
    agent["WEEKS_IN_MILITARY"] = 0
    agent["WEEKS_MILITARY_PER_CALENDAR_YEAR"] = 0

    agent["WEEKS_MILITARY_PER_CALENDAR_YEAR"] = (
        agent.loc[:, agent.columns.str.startswith("EMP_STATUS_WK_")].eq(7.0).sum(axis=1)
    )

    agent["WEEKLY_MILITARY_INCOME"] = (
        agent["INCOME_MILITARY"] / agent["WEEKS_MILITARY_PER_CALENDAR_YEAR"]
    )

    for week_num in range(1, 40):
        cond = agent["EMP_STATUS_WK_" + repr(week_num)].shift(-1).eq(7.0)
        agent["SUM_MILITARY_INCOME"] += (
            agent["WEEKLY_MILITARY_INCOME"].shift(-1) / agent["GNP_DEFL_BASE_1987"].shift(-1)
        ).fillna(0) * cond
        agent["WEEKS_IN_MILITARY"] += cond

    for week_num in range(40, 53):
        cond = agent["EMP_STATUS_WK_" + repr(week_num)].eq(7.0)
        agent["SUM_MILITARY_INCOME"] += (
            agent["WEEKLY_MILITARY_INCOME"] / agent["GNP_DEFL_BASE_1987"]
        ).fillna(0) * cond
        agent["WEEKS_IN_MILITARY"] += cond

    agent["CALCULATED_MILITARY_INCOME"] = (
        agent["SUM_MILITARY_INCOME"] / agent["WEEKS_IN_MILITARY"]
    ) * 50

    cond_1 = agent["CHOICE"].eq("military")
    agent.loc[cond_1, "INCOME"] = agent.loc[cond_1, "CALCULATED_MILITARY_INCOME"]

    cond_2 = (
        agent["INCOME_MILITARY"].isna()
        & agent.loc[
            :,
            agent.columns.str.startswith("EMP_STATUS_WK_")
            & agent.columns.str.endswith(tuple([str(num) for num in range(40, 53)])),
        ]
        .eq(7.0)
        .sum(axis=1)
        .gt(0)
    ) | (
        agent["INCOME_MILITARY"].shift(-1).isna()
        & agent.loc[
            :,
            agent.columns.str.startswith("EMP_STATUS_WK_")
            & agent.columns.str.endswith(tuple([str(num) for num in range(1, 40)])),
        ]
        .shift(-1)
        .eq(7.0)
        .sum(axis=1)
        .gt(0)
    )

    agent.loc[cond_1 & cond_2, "INCOME"] = np.nan

    agent.drop(
        columns=[
            "SUM_MILITARY_INCOME",
            "WEEKLY_MILITARY_INCOME",
            "WEEKS_IN_MILITARY",
            "WEEKS_MILITARY_PER_CALENDAR_YEAR",
        ],
        inplace=True,
    )

    return pd.DataFrame(agent)


def get_schooling_experience(agent):
    """This function creates the variable that indicates the level of schooling an individual has
    obtained at a given age"""
    base_schooling = agent.loc[agent["AGE"] == 15, "HGC"].item()
    agent["SCHOOLING"] = base_schooling + (agent["CHOICE"] == "schooling").astype(
        int
    ).cumsum().shift(1).fillna(0)

    return agent
