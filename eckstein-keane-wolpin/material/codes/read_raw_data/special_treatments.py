""" This module contains some functionality for some special treatment that is required for a
selected few variables.
"""
import numpy as np
from numpy.testing import assert_equal


def aggregate_highest_degree_received(df):
    """ This function merges the information about the highest degree ever received. It is
    sometimes collected under two variable names. However, there is no conflicting information.
    At least one of the two is always a missing value.
    """
    label = "HIGHEST_DEGREE_RECEIVED"

    # This assignment rule simply takes the first assignment and then tries to replace it with
    # the second if the first is a missing value.
    df[label] = df["HIGHEST_DEGREE_RECEIVED_1"]

    cond = df[label].isnull()
    df.loc[cond, label] = df["HIGHEST_DEGREE_RECEIVED_2"]

    return df


def cleaning_highest_grade_attended(df):
    """ The variable contains a value 95 which corresponds to UNGRADED.
    """
    cond = df["HIGHEST_GRADE_ATTENDED"] == 95
    df.loc[cond, "HIGHEST_GRADE_ATTENDED"] = np.nan

    return df


def aggregate_school_enrollment_monthly(df):
    """ This function merges the information about monthly school enrollment. It is sometimes
    collected twice due the differing time an individual is interviewed that year.
    """
    months = []
    months += ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY", "AUGUST"]
    months += ["SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"]

    for month in months:
        label = "ENROLLED_SCHOOL_" + month
        df[label] = np.nan

        # TODO: There is an open ASANA issue that tries to better understand how to deal with the
        # fact that sometimes valid values are provided twice that do not align. Tobias is on
        # the case.

        # This assignment rule simply takes the first assignment and only uses the second if
        # that results in a missing value.
        df[label] = df["ENROLLED_SCHOOL_" + month + "_1"]

        cond = df[label].isnull()
        df.loc[cond, label] = df["ENROLLED_SCHOOL_" + month + "_2"]

        # It also appears that sometimes the indicator that an individual was attending school that
        # month takes values different from one. However, SELECTED is always positive and NOT
        # SELECTED is always zero.
        cond = df[label] == 0
        df.loc[cond, label] = 0

        cond = df[label] > 0
        df.loc[cond, label] = 1

    return df


def create_is_interviewed(df):
    """ This function creates an indicator that evaluates to TRUE if an individual was
    interviewed that year based on the information about the reasons for non-interviews.
    """
    df["IS_INTERVIEWED"] = df["REASON_NONINTERVIEW"].fillna(0) == 0

    return df


def standarize_employer_information(df):
    """ This function merges the employer-specific information on an individual's occupation
    using the 70 CPS codes into a new variable. See additional information at:

        https://www.nlsinfo.org/content/cohorts/nlsy79/topical-guide/employment/jobs-employers

    """
    # We create a set of new variables to signal to users that a modification took place.
    for i in range(1, 6):
        df["OCCALL70_MOD_JOB_" + str(i)] = df["OCCALL70_JOB_" + str(i)]

    # The information on #1 is missing in 1979 and 1993 as it is identical with CPSOCC70.
    for year in [1979, 1993]:
        cond = df["SURVEY_YEAR"] == year
        df.loc[cond, "OCCALL70_MOD_JOB_1"] = df.loc[cond, "CPSOCC70"]

    # For the years 1980 - 1992 there is an indicator variable that maps the CPSOCC70 information
    # to the OCCALL70 variable.
    #
    # TODO: There are two open questions that are ignored here: (1) There exist two variables in
    # 1990 that read ``INT CHECK - IS JOB #01 SAME AS CURRENT JOB?'' (R3340000, R3342400). The
    # realizations of both variables are not identical.
    # ANSWER: Use R3340000 (see correspondence)
    # (2) There exist a few individuals where
    # the CPSOCC indicator takes value one for more than one of the 5 OCCALL70 variables. The
    # issue is set up on ASANA and assigned to Tobias.
    for i in range(1, 6):
        cond = df["CPS_JOB_INDICATOR_JOB_" + str(i)] == 1
        df.loc[cond, "OCCALL70_MOD_JOB_" + str(i)] = df.loc[cond, "CPSOCC70"]

    return df


def standarize_job_information(df):
    for i in range(1, 6):
        df["JOB_" + str(i)] = 0
        df["JOB_" + str(i)] = df[
            ["OCCALL70_MOD_JOB_" + str(i), "OCCALL00_JOB_" + str(i), "OCCALL02_JOB_" + str(i)]
        ].sum(axis=1, min_count=1)

    return df


def calculate_afqt_scores(df):
    """ This function calculates the AFQT scores. See information at

        https://www.nlsinfo.org/content/cohorts/nlsy79/topical-guide/education/aptitude-achievement-intelligence-scores

    for more details. In addition, we adjust the Numerical Operations score along the lines
    described in NLS Attachment 106.
    """
    df["NUMERICAL_ADJ"] = df["ASVAB_NUMERICAL_OPERATIONS"]

    adjust_no = {
        0: 0,
        1: 0,
        2: 1,
        3: 2,
        7: 8,
        8: 9,
        9: 10,
        10: 11,
        11: 12,
        12: 14,
        13: 15,
        14: 16,
        15: 17,
        16: 18,
        17: 19,
        18: 21,
        19: 22,
        20: 23,
        21: 24,
        22: 25,
        23: 26,
        24: 27,
        25: 28,
        26: 29,
        27: 30,
        28: 31,
        29: 33,
        30: 34,
        31: 35,
        32: 36,
        33: 37,
        34: 38,
        35: 39,
        36: 39,
        37: 40,
        38: 41,
        39: 42,
        40: 43,
        41: 44,
        42: 45,
        43: 46,
        44: 47,
        45: 48,
        46: 49,
        47: 49,
        48: 50,
        49: 50,
        50: 50,
    }

    df["NUMERICAL_ADJ"].replace(adjust_no, inplace=True)

    df["AFQT_RAW"] = 0.00
    df["AFQT_RAW"] += df["ASVAB_ARITHMETIC_REASONING"]
    df["AFQT_RAW"] += df["ASVAB_WORD_KNOWLEDGE"]
    df["AFQT_RAW"] += df["ASVAB_PARAGRAPH_COMPREHENSION"]
    df["AFQT_RAW"] += 0.5 * df["NUMERICAL_ADJ"]

    del df["NUMERICAL_ADJ"]

    # There are a couple of variables for which we can compute AFQT_RAW while there is no AFQT_1
    # available. The variable AFQT_1 is set to NAN by the NLSY team if the test procedure was
    # altered, i.e. variable R06148 (ASVAB_ALTERED_TESTING) takes value 67. However, we noticed
    # that there are other indicators of problems as well.
    #
    #   PROFILES, ASVAB VOCATIONAL TEST - NORMAL/ALTERED TESTING
    #
    #       11625   51      COMPLETED
    #          41   52      COMP-CONVERTED REFUSAL
    #         127   53      COMP-PROBLEM REPORTED
    #          85   54      COMP-SPANISH INSTR. CARDS
    #          36   67      COMP-PRODECURES ALTERED
    #
    # We followed up with the NLSY staff to get some guidance on how to deal with 51, 52, 53,
    # 54. The correspondence is available in ``correspondence-altered-testing.pdf'' in the sources
    # subdirectory. In a nutshell, not detailed information is available anymore on the meaning
    # of the different realizations. We decided to follow the original decision of the NLSY staff
    # to only set 67 to NAN.
    cond = df["ASVAB_ALTERED_TESTING"].isin([67])
    df.loc[cond, "AFQT_RAW"] = np.nan

    # We have a little unit test, where we reconstruct the AFQT_1 variable from the inputs.
    assert_equal(_test_afqt(df), True)

    return df


def aggregate_birth_information(df):
    """ This function aggregates the birth information that was collected in 1979 and 1981. See
    information at

        https://www.nlsinfo.org/content/cohorts/nlsy79/topical-guide/household/age for

    more details.
    """

    def _construct_birth_info(agent):
        """ This method constructs the correct birth variable for each agent.
        """
        # We want to store the original information for now for debugging and testing purposes.
        for substring in ["YEAR_OF_BIRTH", "MONTH_OF_BIRTH"]:
            for year in [1979, 1981]:
                agent[substring + "_" + str(year)] = agent[substring][:, year].values[0]
            # We start with a clean slate and always prefer the information from 1981
            agent[substring] = np.nan
            agent[substring] = agent[substring + "_1981"]
            # However, if no information in 1981 is available we fall back to 1979.
            if agent[substring].isnull().values.any():
                agent[substring] = agent[substring + "_1979"]

        return agent

    df = df.groupby("IDENTIFIER").apply(_construct_birth_info)

    # Now we can directly apply some basic tests to ensure that the computation was correct.
    for substring in ["YEAR_OF_BIRTH", "MONTH_OF_BIRTH"]:
        # There cannot be any missing values in the birth variables.
        print(substring)
        print(df.loc[df[substring].isnull(), "IDENTIFIER"])
        assert not df[substring].isnull().any()
        # Whenever there is not a missing value in for 1981 then the columns should be identical.
        # For the others it should be identical to 1979.
        cond = df[substring + "_1981"].notnull()
        assert df.loc[cond, substring].equals(df.loc[cond, substring + "_1981"])
        assert df.loc[~cond, substring].equals(df.loc[~cond, substring + "_1979"])

    # We do not need to keep track of the intermediate variables.
    for substring in ["YEAR_OF_BIRTH", "MONTH_OF_BIRTH"]:
        for year in [1979, 1981]:
            del df[substring + "_" + str(year)]

    df["YEAR_OF_BIRTH"] += 1900

    return df


def _test_afqt(df):
    """ The NLSY does provide a percentile information but we reconstruct based on their
    instructions just to be sure.
    """
    # As we break the logic of the code a bit, we work only with copies of the object here.
    df_internal = df.copy(deep=True)

    # We need to adjust for missing values right here, even though this is done later in the code
    # for all variables.
    for label in ["AFQT_RAW", "AFQT_1"]:
        cond = df_internal[label] < 0
        df_internal.loc[cond, label] = np.nan

    # Match ``AFQT_RAW`` to percentile of distribution
    cond = df_internal["AFQT_RAW"] <= 23.5
    df_internal.loc[cond, "AFQT_PERCENTILES"] = 1

    infos = []
    infos += [(23.50, 27.00, 2), (27.00, 29.50, 3), (29.50, 32.00, 4), (32.00, 34.00, 5)]
    infos += [(34.00, 36.50, 6), (36.50, 38.00, 7), (38.00, 40.00, 8), (40.00, 41.00, 9)]

    infos += [(41.00, 42.50, 10), (42.50, 44.00, 11), (44.00, 45.50, 12), (45.50, 47.00, 13)]
    infos += [(47.00, 48.50, 14), (48.50, 49.50, 15), (49.50, 51.00, 16), (51.00, 52.50, 17)]

    for i in range(18, 29):
        infos += [(i + 34.50, i + 35.50, i)]

    infos += [(63.50, 64.00, 29), (64.00, 65.00, 30), (65.00, 65.50, 31), (65.50, 66.50, 32)]
    infos += [(66.50, 67.00, 33), (67.00, 67.50, 34), (67.50, 68.50, 35), (68.50, 69.00, 36)]
    infos += [(69.00, 69.50, 37), (69.50, 70.50, 38), (70.50, 71.00, 39), (71.00, 71.50, 40)]
    infos += [(71.50, 72.00, 41), (72.00, 73.00, 42), (73.00, 73.50, 43), (73.50, 74.00, 44)]
    infos += [(74.00, 74.50, 45), (74.50, 75.50, 46), (75.50, 76.00, 47), (76.00, 76.50, 48)]
    infos += [(76.50, 77.50, 49)]

    for i, j in enumerate(range(50, 62), 1):
        infos += [(j + 28.00 - 0.50 * i, j + 28.00 - 0.50 * (i - 1), j)]

    for i, j in enumerate(range(62, 94), 1):
        infos += [(j + 21.50 - 0.50 * i, j + 21.50 - 0.50 * (i - 1), j)]

    infos += [(99.00, 100.00, 94)]

    for i, j in enumerate(range(95, 98), 1):
        infos += [(j + 5.50 - 0.50 * i, j + 5.50 - 0.50 * (i - 1), j)]

    infos += [(101.50, 102.50, 98), (102.5, 105.00, 99)]

    for info in infos:
        lower, upper, value = info
        cond = (df_internal["AFQT_RAW"] > lower) & (df_internal["AFQT_RAW"] <= upper)
        df_internal.loc[cond, "AFQT_PERCENTILES"] = value

    return df_internal["AFQT_PERCENTILES"].equals(df_internal["AFQT_1"])
