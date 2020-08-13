"""This script contains the functions used in preliminary_data_adjustments.py
"""

import numpy as np
import pandas as pd


def extend_survey_year(agent):
    agent.sort_values(by=["AGE"], inplace=True)
    cond = agent["AGE"] == 25
    agent["aux_extend_survey_year"] = agent.loc[cond, "SURVEY_YEAR"] - 25
    agent["aux_extend_survey_year"].ffill(inplace=True)
    agent["aux_extend_survey_year"].bfill(inplace=True)

    cond = agent["SURVEY_YEAR"].isna()
    agent.loc[cond, "SURVEY_YEAR"] = (agent["aux_extend_survey_year"] + agent["AGE"]).astype(
        "Int64"
    )

    agent.drop(columns=["aux_extend_survey_year"], inplace=True)

    return agent


def extend_sample_id(agent):
    agent["SAMPLE_ID"].bfill(inplace=True)
    agent["SAMPLE_ID"].ffill(inplace=True)

    return agent


def extend_table_13_covariates(agent):
    for var in ["NUMBER_OF_SIBLINGS", "FAMILY_INCOME", "MOTHER_HGC", "HH_STRUCTURE_AGE_14"]:
        agent[var].bfill(inplace=True)
        agent[var].ffill(inplace=True)

    return agent


def adjust_hgc_12_for_ged(agent):
    """This function reduces the HGC variable if an increase in the HGC variable
    is caused by the completion of a GED"""
    agent["AUX_HGC_GED"] = agent["REAL_HIGHEST_GRADE_COMPLETED"].copy()

    agent["AUX_HGC_GED"].ffill(inplace=True)

    agent["grade_before_GED"] = np.nan

    cond = (agent["AUX_HGC_GED"].shift(-1) == 12) & (~(agent["AUX_HGC_GED"] == 12))
    agent.loc[cond, "grade_before_GED"] = agent.loc[cond, "AUX_HGC_GED"]
    agent["grade_before_GED"].ffill(inplace=True)
    agent["grade_before_GED"].bfill(inplace=True)

    agent["less_years_bc_GED"] = (12 - agent["grade_before_GED"]).fillna(0)

    cond = agent["REAL_HIGHEST_GRADE_COMPLETED"] >= 12
    agent.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = (
        agent.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] - agent.loc[cond, "less_years_bc_GED"]
    )

    return agent


def simple_two_grade_jump(agent):
    """This function smoothes the HGC variable in cases in which two grades are completed
    in one year and none in the next year so that one grade is completed in each of the two years.
    E. g. an HGC variable progression of 12 -> 14 -> 14 is changed to 12 -> 13 -> 14.
    """
    cond_1 = agent["REAL_HIGHEST_GRADE_COMPLETED"].diff() == 2
    cond_2 = agent["REAL_HIGHEST_GRADE_COMPLETED"].eq(
        agent["REAL_HIGHEST_GRADE_COMPLETED"].shift(-1)
    )
    cond_3 = agent["MONTHS_ATTENDED_SCHOOL"].shift(1).gt(0) & agent["MONTHS_ATTENDED_SCHOOL"].gt(0)

    agent.loc[cond_1 & cond_2 & cond_3, "REAL_HIGHEST_GRADE_COMPLETED"] = (
        agent.loc[cond_1 & cond_2 & cond_3, "REAL_HIGHEST_GRADE_COMPLETED"] - 1
    )

    return agent


def months_attended_school(agent):
    """This function calculates the amount of months in which an individual attended school
    in a given year.
    """
    agent["MONTHS_ATTENDED_SCHOOL"] = 0

    for month in [
        "JANUARY",
        "FEBRUARY",
        "MARCH",
        "APRIL",
        "MAY",
        "JUNE",
        "JULY",
        "AUGUST",
        "SEPTEMBER",
    ]:
        cond = (agent["ENROLLED_SCHOOL_" + month].shift(-1).eq(1)).astype(int)
        agent["MONTHS_ATTENDED_SCHOOL"] += cond

    for month in ["OCTOBER", "NOVEMBER", "DECEMBER"]:
        cond = (agent["ENROLLED_SCHOOL_" + month].eq(1)).astype(int)
        agent["MONTHS_ATTENDED_SCHOOL"] += cond

    return agent


def data_shift(agent):
    """The objective of this function is to translate the weekly labor force status
    to valid occupation codes. For this purpose, the labor force status in a given week
    is translated to the occupation code from the job number (last two digits of the
    labor force status) in the survey round (first one or two digits of the labor force status)
    """

    agent_ext = agent.copy()
    for week_num in [1, 7, 13, 14, 20, 26, 40, 46, 52]:
        for num in [1, 2, 3, 4, 5]:
            aux_agent = agent["SURVEY_YEAR"]

            # Create a matrix of size k x k ((k = # of survey years) in which both rows and
            # columns correspond to the survey years. This matrix, for a given week and job number,
            # indicates to which column year the labor force status in a row year corresponds
            # E. g. if the labor force status in the year 1978 is 101, it corresponds to the
            # first survey round, i. e. 1979. Therefore in the row '1978' only the element with
            # column '1979' evaluates to 'True', all row elements with other columns (i. e. years)
            # evaluate to 'False'
            cond = agent["JOB_YEAR_WK_" + repr(week_num)].apply(lambda x: x == aux_agent)

            # initialize similar matrices for job numbers and wages
            job_num = cond.copy()
            wage_num = cond.copy()

            # Fill the columns (with years as column headers) of the additionally created
            # matrices with the occupation code corresponding to the job number in the year
            # given by the column header.
            # E. g. if 'num'==1, every element of the column '1979' will be filled with the
            # occupation code given by the first job in the year 1979 (i. e. survey round 1)
            for year in agent["SURVEY_YEAR"].values:
                job_num.loc[slice(None), (slice(None), year)] = float(
                    agent["JOB_" + repr(num)].loc[agent["SURVEY_YEAR"] == year]
                )
                wage_num.loc[slice(None), (slice(None), year)] = float(
                    agent["WAGE_HOURLY_JOB_" + repr(num)].loc[agent["SURVEY_YEAR"] == year]
                )

            # use the matrix 'cond' to pick only those elements from the matrices created in the
            # previous two steps for which 'cond' evaluates to 'True', i. e. only elements for
            # which the occupation code for a week (indicated by 'week_num') in the row year
            # corresponds to the jobs reported in the column year.

            # As there is only one non-missing value in each row (the occupation code for the job
            # number and week in the row year), we can sum up each row across all columns,
            # again receiving the suitable occupation code.

            # As a result, we receive a vector of size k x 1 (k = # of survey years) in which the
            # value of each row equals the occupation code in the row year for the week number
            # given by 'week_num' and the job number given by 'num'.

            job_num = pd.DataFrame(job_num[cond].sum(axis=1, min_count=1)).rename(
                columns={0: "JOB_" + repr(num) + "_WK_" + repr(week_num)}
            )
            wage_num = pd.DataFrame(wage_num[cond].sum(axis=1, min_count=1)).rename(
                columns={0: "WAGE_" + repr(num) + "_WK_" + repr(week_num)}
            )

            # merge the column created in the previous step onto the existing data frame
            agent_ext = agent_ext.merge(job_num, on="Survey Year")
            agent_ext = agent_ext.merge(wage_num, on="Survey Year")

            cond = agent_ext["JOB_NUMBER_WK_" + repr(week_num)].eq(num)
            agent_ext.loc[cond, "JOB_CHOICE_WK_" + repr(week_num)] = agent_ext.loc[
                cond, "JOB_" + repr(num) + "_WK_" + repr(week_num)
            ]
            agent_ext.loc[cond, "WAGE_WK_" + repr(week_num)] = agent_ext.loc[
                cond, "WAGE_" + repr(num) + "_WK_" + repr(week_num)
            ]

            # drop unnecessary variables
            agent_ext.drop(
                ["JOB_" + repr(int(num)) + "_WK_" + repr(week_num)], axis=1, inplace=True
            )
            agent_ext.drop(
                ["WAGE_" + repr(int(num)) + "_WK_" + repr(week_num)], axis=1, inplace=True
            )

    cols = [col for col in agent_ext if col.startswith("JOB_CHOICE_WK_")]
    cols.extend([col for col in agent_ext if col.startswith("ROUND_JOBS_WK_")])
    cols.extend([col for col in agent_ext if col.startswith("WAGE_WK_")])
    cols.extend(["SURVEY_ROUND"])

    return agent_ext[cols]
