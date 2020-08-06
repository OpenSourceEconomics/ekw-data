from pathlib import Path
import os

import bulwark.checks as ck
import numpy as np
import pandas as pd

from functions_extended_clean import clean_missing_wages
from functions_extended_clean import create_wages
from functions_extended_clean import get_occ_hours
from functions_extended_clean import weeks_hours_worked
from functions_prelim_adjust import adjust_hgc_12_for_ged
from functions_prelim_adjust import data_shift
from functions_prelim_adjust import months_attended_school
from functions_prelim_adjust import simple_two_grade_jump

PROJECT_DIR = Path(os.environ["PROJECT_ROOT"])


test_df = pd.DataFrame(
    {
        "HGC": [9, 9, 12, 13, 14],
        "ENROLLED_SCHOOL_OCTOBER": [1, 1, 1, 1, 1],
        "ENROLLED_SCHOOL_JANUARY": [1, 1, 1, 1, 1],
        "ENROLLED_SCHOOL_APRIL": [0, 0, 0, 0, 0],
    }
)
mock_df = adjust_hgc_12_for_ged(test_df)

np.testing.assert_array_equal(mock_df["HGC"], [9, 9, 9, 10, 11])

test_df = pd.DataFrame(
    {
        "HGC": [9, 9, 12, 13, 14],
        "ENROLLED_SCHOOL_OCTOBER": [0, 0, 0, 0, 0],
        "ENROLLED_SCHOOL_JANUARY": [0, 0, 0, 0, 0],
        "ENROLLED_SCHOOL_APRIL": [0, 0, 0, 0, 0],
    }
)
mock_df = adjust_hgc_12_for_ged(test_df)

np.testing.assert_array_equal(mock_df["HGC"], [9, 9, 9, 10, 11])


col = [
    "ENROLLED_SCHOOL_" + month
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
        "OCTOBER",
        "NOVEMBER",
        "DECEMBER",
    ]
]


row = [[0] * 12, [1] * 12, [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1]]

test_df = pd.DataFrame(row, columns=col)
mock_df = months_attended_school(test_df)

np.testing.assert_array_equal(mock_df["MONTHS_ATTENDED_SCHOOL"], [9, 8, 3])

# Test get_occ_hours()
test_df = pd.DataFrame(
    {
        "OCC_JC_WK_1": [np.nan, "blue_collar"],
        "OCC_JC_WK_7": [np.nan, "blue_collar"],
        "OCC_JC_WK_13": [np.nan, "white_collar"],
        "OCC_JC_WK_14": [np.nan, "military"],
        "OCC_JC_WK_20": [np.nan, "blue_collar"],
        "OCC_JC_WK_26": [np.nan, "white_collar"],
        "OCC_JC_WK_40": ["blue_collar", "white_collar"],
        "OCC_JC_WK_46": ["white_collar", "white_collar"],
        "OCC_JC_WK_52": ["white_collar", "white_collar"],
        "EMP_HOURS_WK_1": [np.nan, np.nan],
        "EMP_HOURS_WK_7": [np.nan, 13.5],
        "EMP_HOURS_WK_13": [np.nan, 70],
        "EMP_HOURS_WK_14": [np.nan, 0],
        "EMP_HOURS_WK_20": [np.nan, 50],
        "EMP_HOURS_WK_26": [np.nan, 17.3],
        "EMP_HOURS_WK_40": [50, 0],
        "EMP_HOURS_WK_46": [40, 15.5],
        "EMP_HOURS_WK_52": [np.nan, 109],
    }
)

mock_df = get_occ_hours(test_df)

np.testing.assert_array_equal(mock_df["WHITE_COLLAR_HOURS"], [127.3, 124.5])
np.testing.assert_array_equal(mock_df["BLUE_COLLAR_HOURS"], [113.5, 0])

test_df = pd.DataFrame(
    {
        "EMP_STATUS_WK_1": [0, 103],
        "EMP_STATUS_WK_7": [0, 0],
        "EMP_STATUS_WK_13": [0, 102],
        "EMP_STATUS_WK_14": [0, 101],
        "EMP_STATUS_WK_20": [0, 5],
        "EMP_STATUS_WK_26": [0, 101],
        "EMP_STATUS_WK_40": [104, 7],
        "EMP_STATUS_WK_46": [7, 202],
        "EMP_STATUS_WK_52": [7, 201],
        "EMP_HOURS_WK_1": [np.nan, 40],
        "EMP_HOURS_WK_7": [np.nan, 13.5],
        "EMP_HOURS_WK_13": [np.nan, 70],
        "EMP_HOURS_WK_14": [np.nan, 30],
        "EMP_HOURS_WK_20": [np.nan, 50],
        "EMP_HOURS_WK_26": [np.nan, 17.3],
        "EMP_HOURS_WK_40": [50, 0],
        "EMP_HOURS_WK_46": [40, 15.5],
        "EMP_HOURS_WK_52": [np.nan, 109],
    }
)

mock_df = weeks_hours_worked(test_df)

np.testing.assert_array_equal(mock_df["WORKED_WEEKS"], [7, 3])
np.testing.assert_array_equal(mock_df["WORKED_WEEKS_MILITARY"], [2, 1])
np.testing.assert_array_equal(mock_df["EMP_NONMISSING_WEEKS"], [8, 3])
# np.testing.assert_equal(mock_df['HOURS_LIST'], [[50, 0, 0, 40, 0, 70, 30, 0, 17.3],
#                                                [0, 15.5, 109, 0, 0, 0, 0, 0, 0]])
np.testing.assert_array_equal(mock_df["WORKED_HOURS"], [207.3, 124.5])
np.testing.assert_array_equal(mock_df["NECESSARY_WEEKS_WORKED"], [4, 1])
np.testing.assert_array_equal(mock_df["MAX_HOURS"], [[70, 50, 40, 30], [109]])
np.testing.assert_array_equal(mock_df["SUM_MAX_HOURS"], [190, 109])


test_df = pd.DataFrame(
    {
        "EMP_STATUS_WK_1": [0, 103],
        "EMP_STATUS_WK_7": [0, 0],
        "EMP_STATUS_WK_13": [0, 102],
        "EMP_STATUS_WK_14": [0, 101],
        "EMP_STATUS_WK_20": [0, 204],
        "EMP_STATUS_WK_26": [0, 101],
        "EMP_STATUS_WK_40": [104, 305],
        "EMP_STATUS_WK_46": [102, 202],
        "EMP_STATUS_WK_52": [103, 201],
        "WAGE_WK_1": [np.nan, np.nan],
        "WAGE_WK_7": [np.nan, 1350],
        "WAGE_WK_13": [np.nan, 7000],
        "WAGE_WK_14": [np.nan, 3000],
        "WAGE_WK_20": [np.nan, np.nan],
        "WAGE_WK_26": [np.nan, 1730],
        "WAGE_WK_40": [5000, np.nan],
        "WAGE_WK_46": [1061, 155],
        "WAGE_WK_52": [np.nan, 1090],
    }
)

mock_df = clean_missing_wages(test_df)

np.testing.assert_array_equal(mock_df["MISSPECIFIED_EMP_STATUS"], [3, 1])

test_df = pd.DataFrame(
    {
        "CHOICE": ["blue_collar", "white_collar", "white_collar"],
        "GNP_DEFL_BASE_1987": [0.75, 1, 1.25],
        "OCC_JC_WK_1": [np.nan, "white_collar", "white_collar"],
        "OCC_JC_WK_7": [np.nan, "blue_collar", "white_collar"],
        "OCC_JC_WK_13": [np.nan, "blue_collar", "white_collar"],
        "OCC_JC_WK_14": [np.nan, np.nan, "white_collar"],
        "OCC_JC_WK_20": [np.nan, "blue_collar", "white_collar"],
        "OCC_JC_WK_26": [np.nan, "blue_collar", "white_collar"],
        "OCC_JC_WK_40": ["blue_collar", "white_collar", "white_collar"],
        "OCC_JC_WK_46": ["blue_collar", "white_collar", "white_collar"],
        "OCC_JC_WK_52": ["white_collar", "white_collar", "white_collar"],
        "EMP_STATUS_WK_1": [0, 202, 301],
        "EMP_STATUS_WK_7": [0, 202, 301],
        "EMP_STATUS_WK_13": [0, 103, 301],
        "EMP_STATUS_WK_14": [0, 5, 301],
        "EMP_STATUS_WK_20": [0, 201, 301],
        "EMP_STATUS_WK_26": [0, 201, 301],
        "EMP_STATUS_WK_40": [203, 303, 401],
        "EMP_STATUS_WK_46": [203, 301, 401],
        "EMP_STATUS_WK_52": [202, 301, 401],
        "EMP_HOURS_WK_1": [np.nan, 80, 50],
        "EMP_HOURS_WK_7": [np.nan, 80, 50],
        "EMP_HOURS_WK_13": [np.nan, 80, 50],
        "EMP_HOURS_WK_14": [np.nan, np.nan, 50],
        "EMP_HOURS_WK_20": [np.nan, 80, 50],
        "EMP_HOURS_WK_26": [np.nan, 80, 50],
        "EMP_HOURS_WK_40": [30, 40, 50],
        "EMP_HOURS_WK_46": [30, 40, 50],
        "EMP_HOURS_WK_52": [30, 109, 50],
        "WAGE_WK_1": [np.nan, 1000, 2000],
        "WAGE_WK_7": [np.nan, 1000, 2000],
        "WAGE_WK_13": [np.nan, 1000, 2000],
        "WAGE_WK_14": [np.nan, 0, 2000],
        "WAGE_WK_20": [np.nan, 1000, 2000],
        "WAGE_WK_26": [np.nan, 1000, 2000],
        "WAGE_WK_40": [2000, np.nan, 1000],
        "WAGE_WK_46": [2000, 15.5, 1000],
        "WAGE_WK_52": [2000, 109, 1000],
    }
)

mock_df = create_wages(test_df)

np.testing.assert_array_equal(mock_df["INCOME"], [40000, np.nan, 20000])


col_list = ["JOB_NUMBER_WK_" + repr(week) for week in [1, 7, 13, 14, 20, 26, 40, 46, 52]]
col_list_2 = ["JOB_YEAR_WK_" + repr(week) for week in [1, 7, 13, 14, 20, 26, 40, 46, 52]]
col_list.extend(col_list_2)
row_list = [
    [2, 1, 6, 3, 5, 1, 4, 2, 1, 1981, 1981, 1982, 1982, 1983, 1983, 1984, 1984, 1984],
    [np.nan] * 18,
    [np.nan] * 18,
    [np.nan] * 18,
]

test_df = pd.DataFrame(row_list, columns=col_list)

test_df["JOB_1"] = pd.Series([11, 12, 13, 14]).astype(float)
test_df["WAGE_HOURLY_JOB_1"] = pd.Series([10001, 10002, 10003, 10004]).astype(float)

test_df["JOB_2"] = pd.Series([21, 22, 23, np.nan]).astype(float)
test_df["WAGE_HOURLY_JOB_2"] = pd.Series([20001, 20002, 20003, 20004]).astype(float)

test_df["JOB_3"] = pd.Series([31, 32, 33, 34]).astype(float)
test_df["WAGE_HOURLY_JOB_3"] = pd.Series([30001, 30002, 30003, 30004]).astype(float)

test_df["JOB_4"] = pd.Series([41, 42, 43, 44]).astype(float)
test_df["WAGE_HOURLY_JOB_4"] = pd.Series([40001, 40002, 40003, np.nan]).astype(float)

test_df["JOB_5"] = pd.Series([51, 52, 53, 54]).astype(float)
test_df["WAGE_HOURLY_JOB_5"] = pd.Series([50001, 50002, 50003, 50004]).astype(float)

test_df["SURVEY_YEAR"] = pd.Series([1981, 1982, 1983, 1984])
test_df["SURVEY_ROUND"] = pd.Series([1, 2, 3, 4])

test_df["Identifier"] = [0, 0, 0, 0]
test_df["Survey Year"] = [1981, 1982, 1983, 1984]
test_df.set_index(["Identifier", "Survey Year"], inplace=True)

mock_df = data_shift(test_df)


job_choice_col = [col for col in mock_df if col.startswith("JOB_CHOICE_WK_")]
np.testing.assert_array_equal(
    mock_df.loc[(1981), job_choice_col], [21, 11, np.nan, 32, 53, 13, 44, np.nan, 14]
)

wage_col = [col for col in mock_df if col.startswith("WAGE_WK_")]
np.testing.assert_array_equal(
    mock_df.loc[(1981), wage_col], [20001, 10001, np.nan, 30002, 50003, 10003, np.nan, 20004, 10004]
)


test_df = pd.DataFrame(
    {"HGC": [12, 14, 14, 15, 17, 17], "MONTHS_ATTENDED_SCHOOL": [9, 9, 7, 7, 0, 10]}
)
mock_df = simple_two_grade_jump(test_df)

np.testing.assert_array_equal(mock_df["HGC"], [12, 13, 14, 15, 17, 17])


df = pd.read_pickle(
    f"{PROJECT_DIR}/eckstein-keane-wolpin/material/output/data/final/ekw_ext_all_vars.pkl"
)

# As we will sum over them later, we have to check that there are no (necessarily wrong) negative
# values for hours worked and wages
assert (
    df.filter(regex="EMP_HOURS_*").apply(lambda column: (column[column.notnull()] >= 0).all()).all()
)
assert (
    df.filter(regex="WAGE_WK_*").apply(lambda column: (column[column.notnull()] >= 0).all()).all()
)

# We have to check that the HGC variable does not have missing values
ck.has_no_nans(df, columns=["HGC"])

# All values of the choice options have to correspond to one of the five choice options
assert df["CHOICE"].isin(["schooling", "white_collar", "blue_collar", "military", "home"]).all()

# There should be no income outliers, i. e. all income values should lie within 3 standard
# deviations of the mean of the unadjusted income variable
cond = df["INCOME"] > (df["INCOME_RAW"].mean() + 3 * df["INCOME_RAW"].std())
assert sum(cond) == 0
