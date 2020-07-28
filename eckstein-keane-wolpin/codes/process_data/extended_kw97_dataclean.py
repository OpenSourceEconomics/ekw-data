#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd

from functions_extended_clean import get_occ_hours
from functions_extended_clean import weeks_hours_worked
from functions_extended_clean import clean_missing_wages
from functions_extended_clean import clean_military_wages
from functions_extended_clean import create_wages
from functions_extended_clean import create_military_wages
from functions_extended_clean import get_schooling_experience

df = pd.read_pickle("../../output/data/interim/original_extended_interim.pkl")

# Construct variable that indicates whether or not an individual completed a grade in a given year,
# i. e. if the HGC variable is increased by one in the following year
df["GRADE_COMPLETED"] = (
    df["REAL_HIGHEST_GRADE_COMPLETED"].groupby(df["IDENTIFIER"]).diff().shift(-1)
)

# Set observation with (necessarily false) negative values for grade completed to 0.
cond = df["GRADE_COMPLETED"] < 0
df.loc[cond, "GRADE_COMPLETED"] = 0

# Merge the dataframe with the disentangled information on weekly jobs (occupation codes)
# and wages from get_occ_codes_kw97.py
job_choice_df = pd.read_pickle("../../output/data/interim/jobs_with_occ_codes.pkl")
job_choice_df.index.rename(["Identifier", "Survey Year"], inplace=True)

df = df.join(job_choice_df, rsuffix="_y")

# Initialize the choice variable
df["CHOICE"] = np.nan

# check whether the requirements for the choice "schooling" (see p. 483 and footnote 15
# on p. 484 in KW97) are fulfilled and code the responding observations accordingly

# Condition 1: "An individual ist considered to have attended school
# during the year if the individual attended in any of the three weeks..."
school_cond_1 = (
    df["ENROLLED_SCHOOL_APRIL"].shift(-1).eq(1.0)
    | df["ENROLLED_SCHOOL_JANUARY"].shift(-1).eq(1.0)
    | df["ENROLLED_SCHOOL_OCTOBER"].eq(1.0)
)

# Condition 2: "... and the individual reported completing one grade level by October 1
# of the next year."
school_cond_2 = df["GRADE_COMPLETED"].ge(1.0)  # 'GRADE_COMPLETED' might be larger than 1

# Create variable which counts the number of attendance data points [October 1, January 1, April 1]
# non-missing in a given year
df["SCHOOL_NONMISSING_MONTHS"] = (
    (~(df["ENROLLED_SCHOOL_OCTOBER"].isna())).astype(int)
    + (~(df["ENROLLED_SCHOOL_JANUARY"].shift(-1).isna())).astype(int)
    + (~(df["ENROLLED_SCHOOL_APRIL"].shift(-1).isna())).astype(int)
)

# Condition 3: All 3 attendance data points are non-missing
school_cond_3 = df["SCHOOL_NONMISSING_MONTHS"].eq(3)

# Condition 4: 1 or 2 attendance data points are non-missing
school_cond_4 = df["SCHOOL_NONMISSING_MONTHS"].isin([1, 2])

# If all of the 3 monthly attendance data points are non-missing,
# assign 'schooling' if Condition 1 AND Condition 2 are satisfied.
df.loc[(school_cond_1 & school_cond_2 & school_cond_3), "CHOICE"] = "schooling"

# If 1 or 2 of the monthly attendance data points are non-missing,
# assign 'Schooling' if only Condition 2 (grade completed) is satisfied
df.loc[(school_cond_2 & school_cond_4), "CHOICE"] = "schooling"

# As information on monthly school attendance is available only from January 1980 onwards,
# individuals are assigned to have chosen 'schooling' in 1978 if they completed a grade in this year
df.loc[(df["SURVEY_YEAR"].eq(1978)) & school_cond_2, "CHOICE"] = "schooling"


# check whether the requirements for the choice "work" (see p. 484 in KW97; will below be
# separated in blue, white, military)
id_sorted_data = df.groupby(df["IDENTIFIER"])
df = id_sorted_data.apply(lambda x: weeks_hours_worked(x))

# Condition 1: individual was employed in at least two-thirds of the (non-missing) weeks
work_cond_1 = (df["WORKED_WEEKS"] / df["EMP_NONMISSING_WEEKS"]).ge(2 / 3)

# Condition 2: individual for at least 20 hours on average,
# excluding weeks worked in military as there is no information on hours worked in the military
work_cond_2 = df["SUM_MAX_HOURS"] >= (20 * df["NECESSARY_WEEKS_WORKED"])
# work_cond_2 = (df['WORKED_HOURS'] / df['WORKED_WEEKS']).ge(20)

# Condition 3: Less than 2/3 of the 9 relevant weeks have a missing labor force status,
# i. e. at least 4 weeks have a non-missing labor force status
work_cond_3 = df["EMP_NONMISSING_WEEKS"].ge(4)

# Condition 4: individual did not attend school according to the criteria above
work_cond_4 = df["CHOICE"].ne("schooling")

# If all 4 conditions are fulfilled, the choice in this year is work.
# Assigning work occupations will be done later
df.loc[work_cond_1 & work_cond_2 & work_cond_3 & work_cond_4, "CHOICE"] = "Work"

# If all conditions except the hours condition (cond 2)  are fulfilled, an individual did not work
# in white- or blue-collar that year but might have worked in the military due to the
# missing 'hours worked' data in the military
df.loc[work_cond_1 & ~work_cond_2 & work_cond_3 & work_cond_4, "CHOICE"] = "Potentially military"


# Next, we read in the GNP deflation data, adjust the data to base year 1987 (from 2012) and
# merge it with our previous data
gnp_deflation = pd.read_csv(
    "../../sources/gnp_deflator_data/st_louis_fed_deflator.csv", index_col="SURVEY_YEAR"
)

gnp_deflation["GNP_DEFL_BASE_1987"] = (
    gnp_deflation["IMPLICIT_GNP"] / gnp_deflation.loc[1987, "IMPLICIT_GNP"]
)

df = df.merge(gnp_deflation, left_on="SURVEY_YEAR", right_index=True, how="outer")

df.sort_values(by=["IDENTIFIER", "SURVEY_YEAR"], inplace=True)


# Translate the occupation codes in the "CHOICE_WK" variables to white/blue collar taking
# into account the change of occupation coding in 2002 and 2004

# Read in csv-file
categories_df = pd.read_pickle("../../output/data/interim/categorized_xwalk.pkl")

categories_df.columns = [
    "OCC1990",
    "DESCRIPTION",
    "CPS_1970",
    "CPS_2000_1",
    "CPS_2000_5",
    "category_service",
    "CATEGORY",
    "CPS_2002",
]

# Construct dictionaries that assigns blue- or white-collar to each occupation for each set of
# occupation codes (1970, 2000, 2002)
cond_1 = categories_df.CPS_1970.isin(range(1, 1000))
category_dict_1970 = dict(
    zip(categories_df.CPS_1970[cond_1].astype("Int64"), categories_df.CATEGORY[cond_1])
)

cond_2 = categories_df.CPS_2000_1.isin(range(1, 1000))
category_dict_2000 = dict(
    zip(categories_df.CPS_2000_1[cond_2].astype("Int64"), categories_df.CATEGORY[cond_2])
)

cond_3 = categories_df.CPS_2002.isin(range(1, 10000))
category_dict_2002 = dict(
    zip(categories_df.CPS_2002[cond_3].astype("Int64"), categories_df.CATEGORY[cond_3])
)

for week_num in [1, 7, 13, 14, 20, 26, 40, 46, 52]:
    # Initialize variable that contains the chosen occupation (blue-/white-collar, military)
    # in a given week
    df["OCC_JC_WK_" + repr(week_num)] = np.nan

    # Before survey round 20 (year 2002), use 1970 occupation codes to convert occupation code
    # to blue-/white-collar
    cond_1 = df["ROUND_JOBS_WK_" + repr(week_num)] < 20
    df.loc[cond_1, "OCC_JC_WK_" + repr(week_num)] = (
        df.loc[cond_1, "JOB_CHOICE_WK_" + repr(week_num)].astype("Int64").map(category_dict_1970)
    )

    # For survey round 20 (year 2002), use 2000 occupation codes to convert occupation code
    # to blue-/white-collar
    cond_2 = df["ROUND_JOBS_WK_" + repr(week_num)] == 20
    df.loc[cond_2, "OCC_JC_WK_" + repr(week_num)] = (
        df.loc[cond_2, "JOB_CHOICE_WK_" + repr(week_num)].astype("Int64").map(category_dict_2000)
    )

    # From survey round 21 (year 2004) onwards, use 2002 occupation codes to convert
    # occupation code to blue-/white-collar
    cond_3 = df["ROUND_JOBS_WK_" + repr(week_num)] > 20
    df.loc[cond_3, "OCC_JC_WK_" + repr(week_num)] = (
        df.loc[cond_3, "JOB_CHOICE_WK_" + repr(week_num)].astype("Int64").map(category_dict_2002)
    )


# Assign occupation choice 'military' for the week if 'EMP_STATUS' of the week == 7
for week_num in [1, 7, 13, 14, 20, 26, 40, 46, 52]:
    cond = df["EMP_STATUS_WK_" + repr(week_num)].eq(7.0)
    df.loc[cond, "OCC_JC_WK_" + repr(week_num)] = "military"

# Shift military income by 1 given the definition of the variable
# (TOTAL INCOME FROM MILITARY SERVICE IN PAST CALENDAR YEAR)
df["INCOME_MILITARY"] = df["INCOME_MILITARY"].groupby(df["IDENTIFIER"]).apply(lambda x: x.shift(-1))


# We now aggregate several metrics related to occupational choice

# Weeks spend in white-collar jobs in a given year
df["WHITE_COLLAR"] = 0

# Weeks spend in blue-collar jobs in a given year
df["BLUE_COLLAR"] = 0

# Weeks spend in the military in a given year
df["MILITARY"] = 0

# Weeks spend in unemployment (i. e. labor force status == 4) in a given year
df["UNEMPLOYED"] = 0

# Weeks spend out of the labor force (i. e. labor force status == 5) in a given year
df["OUT_OF_LABOR_FORCE"] = 0

# Weeks spend unspecified not working (i. e. labor force status == 2) in a given year
df["NOT_WORKING"] = 0

for week_num in [1, 7, 13, 14, 20, 26]:
    df["WHITE_COLLAR"] += (
        (df["OCC_JC_WK_" + repr(week_num)] == "white_collar").astype(int).fillna(0)
    )
    df["BLUE_COLLAR"] += (df["OCC_JC_WK_" + repr(week_num)] == "blue_collar").astype(int).fillna(0)
    df["MILITARY"] += (df["OCC_JC_WK_" + repr(week_num)] == "military").astype(int).fillna(0)
    df["UNEMPLOYED"] += (df["EMP_STATUS_WK_" + repr(week_num)].eq(4.0)).astype(int).fillna(0)
    df["OUT_OF_LABOR_FORCE"] += (
        (df["EMP_STATUS_WK_" + repr(week_num)].eq(5.0)).astype(int).fillna(0)
    )
    df["NOT_WORKING"] += (df["EMP_STATUS_WK_" + repr(week_num)].eq(2.0)).astype(int).fillna(0)

for choice in [
    "WHITE_COLLAR",
    "BLUE_COLLAR",
    "MILITARY",
    "UNEMPLOYED",
    "OUT_OF_LABOR_FORCE",
    "NOT_WORKING",
]:
    df[choice] = df[choice].shift(-1)

for week_num in [40, 46, 52]:
    df["WHITE_COLLAR"] += (
        (df["OCC_JC_WK_" + repr(week_num)] == "white_collar").astype(int).fillna(0)
    )
    df["BLUE_COLLAR"] += (df["OCC_JC_WK_" + repr(week_num)] == "blue_collar").astype(int).fillna(0)
    df["MILITARY"] += (df["OCC_JC_WK_" + repr(week_num)] == "military").astype(int).fillna(0)
    df["UNEMPLOYED"] += (df["EMP_STATUS_WK_" + repr(week_num)].eq(4.0)).astype(int).fillna(0)
    df["OUT_OF_LABOR_FORCE"] += (
        (df["EMP_STATUS_WK_" + repr(week_num)].eq(5.0)).astype(int).fillna(0)
    )
    df["NOT_WORKING"] += (df["EMP_STATUS_WK_" + repr(week_num)].eq(2.0)).astype(int).fillna(0)


df = df.groupby(df["IDENTIFIER"]).apply(lambda x: get_occ_hours(x))

# Assign the occupation in which the most weeks were worked in a given year as the work choice
# in that year if the work criteria are satisfied, i. e. 'CHOICE' == 'Work'
cond_1 = df["CHOICE"] == "Work"
cond_2 = df[["WHITE_COLLAR", "BLUE_COLLAR", "MILITARY"]].max(axis=1) > 0
df.loc[cond_1 & cond_2, "CHOICE"] = (
    df.loc[cond_1 & cond_2, ["WHITE_COLLAR", "BLUE_COLLAR", "MILITARY"]]
    .idxmax(axis=1)
    .astype(str)
    .str.lower()
)

# In case there is a tie between two rows (same number of weeks worked in both occupations),
# the max() function in Python chooses the first row encountered (see
# https://stackoverflow.com/questions/6783000/which-maximum-does-python-pick-in-the-case-of-a-tie).
# To solve a tie between white- and blue-collar, we choose the occupation in which more hours
# were worked in a given year.
cond_1 = df["CHOICE"].isin(["WHITE_COLLAR", "BLUE_COLLAR"])
cond_2 = df["WHITE_COLLAR"].eq(df["BLUE_COLLAR"])
cond_3 = df["WHITE_COLLAR_HOURS"].gt(df["BLUE_COLLAR_HOURS"])
cond_4 = df["BLUE_COLLAR_HOURS"].gt(df["WHITE_COLLAR_HOURS"])

df.loc[cond_1 & cond_2 & cond_3, "CHOICE"] = "white_collar"
df.loc[cond_1 & cond_2 & cond_4, "CHOICE"] = "blue_collar"

# If all work conditions except for the average hour criterion are fulfilled and 'military' is
# the most often chosen occupation, an individual is assigned to the military occupation
cond_1 = df["CHOICE"] == "Potentially military"
cond_2 = df[["WHITE_COLLAR", "BLUE_COLLAR", "MILITARY"]].idxmax(axis=1) == "MILITARY"

df.loc[cond_1 & cond_2, "CHOICE"] = "military"


# We assign all observations that are not assigned to another option until now, to the option 'home'
cond = (df["CHOICE"] == "Potentially military") | (df["CHOICE"].isna()) | (df["CHOICE"] == "Work")
df.loc[cond, "CHOICE"] = "home"


# We initialize a new variable so which decomposes the home option
df["HOME_CHOICE"] = np.nan

# An individual who stays home and did not work for more than 1/3 of the non-missing weeks
# (i. e. did not satisfy work_cond_1), are assigned to 'non_working'
cond = df["CHOICE"].eq("home") & (
    (df["UNEMPLOYED"] + df["OUT_OF_LABOR_FORCE"] + df["NOT_WORKING"]) / df["EMP_NONMISSING_WEEKS"]
).gt(1 / 3)
df.loc[cond, "HOME_CHOICE"] = "not_working"

# An individual was 'out_of_labor_force' if he was 'not_working' in the previous step and
# spend more time out of the labor force than unemployed
cond = df["HOME_CHOICE"].eq("not_working") & df["OUT_OF_LABOR_FORCE"].gt(df["UNEMPLOYED"])
df.loc[cond, "HOME_CHOICE"] = "out_of_labor_force"

# An individual was 'unemployed' if he was 'not_working' and spend more time unemployed than
# out of the labor force
cond = df["HOME_CHOICE"].eq("not_working") & df["UNEMPLOYED"].gt(df["OUT_OF_LABOR_FORCE"])
df.loc[cond, "HOME_CHOICE"] = "unemployed"

# An individual who stayed home and fulfills all work conditions except the average hours
# criterion, is assigned to 'part_time_work'
cond = df["CHOICE"].eq("home")
df.loc[
    cond & work_cond_1 & ~work_cond_2 & work_cond_3 & work_cond_4, "HOME_CHOICE"
] = "part_time_work"

# An individual has 'failed_schooling' if he did attend school according to the attendance
# criterion but did not complete a grade
cond = df["CHOICE"].eq("home")
df.loc[cond & school_cond_1 & ~school_cond_2, "HOME_CHOICE"] = "failed_schooling"

# For 'CHOICE'=='home' and not being assigned to a 'HOME_CHOICE' yet, an individual is assigned to
# 'HOME_CHOICE'=='residual'
cond = df["CHOICE"].eq("home") & df["HOME_CHOICE"].isna()
df.loc[cond, "HOME_CHOICE"] = "residual"


# We clean and create the yearly income data
df = df.groupby(df["IDENTIFIER"]).apply(lambda x: clean_missing_wages(x))

df = df.groupby(df["IDENTIFIER"]).apply(lambda x: clean_military_wages(x))

df = df.groupby(df["IDENTIFIER"]).apply(lambda x: create_wages(x))

df = df.groupby(df["IDENTIFIER"]).apply(lambda x: create_military_wages(x))


# We remove the most extreme income outliers, i. e. values that are not within 3 standard
# deviations of the mean of all income values
df["INCOME_RAW"] = df["INCOME"].copy()

cond = df["INCOME"] > (df["INCOME"].mean() + 3 * df["INCOME"].std())
df.loc[cond, "INCOME"] = np.nan

# Table 13
cond = df["NUMBER_OF_SIBLINGS"].gt(4)
df.loc[cond, "NUMBER_OF_SIBLINGS"] = 4

df["MOTHER_NON_HS"] = 0
cond = df["MOTHER_HGC"].le(11)
df.loc[cond, "MOTHER_NON_HS"] = 1

df["MOTHER_HS"] = 0
cond = df["MOTHER_HGC"].eq(12)
df.loc[cond, "MOTHER_HS"] = 1

df["MOTHER_SOME_COLLEGE"] = 0
cond = df["MOTHER_HGC"].isin([13, 14, 15])
df.loc[cond, "MOTHER_SOME_COLLEGE"] = 1

df["MOTHER_COLLEGE_GRAD"] = 0
cond = df["MOTHER_HGC"].ge(16)
df.loc[cond, "MOTHER_COLLEGE_GRAD"] = 1

df["AGE_14_MOTHER_FATHER"] = 0
cond = df["HH_STRUCTURE_AGE_14"].eq(11)
df.loc[cond, "AGE_14_MOTHER_FATHER"] = 1

df["AGE_14_ONLY_FATHER"] = 0
father_list = [12, 13, 14, 15, 19]
cond = df["HH_STRUCTURE_AGE_14"].isin(father_list)
df.loc[cond, "AGE_14_ONLY_FATHER"] = 1

df["AGE_14_ONLY_MOTHER"] = 0
mother_list = [21, 31, 41, 51, 91]
cond = df["HH_STRUCTURE_AGE_14"].isin(mother_list)
df.loc[cond, "AGE_14_ONLY_MOTHER"] = 1

df["AGE_14_NO_PARENTS"] = 0
cond = ~df["HH_STRUCTURE_AGE_14"].isin([11, father_list, mother_list])
df.loc[cond, "AGE_14_NO_PARENTS"] = 1

df["PARENTAL_INCOME_VERY_LOW"] = 0
cond = df["FAMILY_INCOME"].le((0.5 * df["FAMILY_INCOME"].median())) & ~df["FAMILY_INCOME"].isna()
df.loc[cond, "PARENTAL_INCOME_VERY_LOW"] = 1

df["PARENTAL_INCOME_LOW"] = 0
cond = df["FAMILY_INCOME"].gt((0.5 * df["FAMILY_INCOME"].median())) & df["FAMILY_INCOME"].le(
    df["FAMILY_INCOME"].median()
)
df.loc[cond, "PARENTAL_INCOME_LOW"] = 1

df["PARENTAL_INCOME_HIGH"] = 0
cond = df["FAMILY_INCOME"].ge(df["FAMILY_INCOME"].median()) & df["FAMILY_INCOME"].le(
    (2 * df["FAMILY_INCOME"].median())
)
df.loc[cond, "PARENTAL_INCOME_HIGH"] = 1

df["PARENTAL_INCOME_VERY_HIGH"] = 0
cond = df["FAMILY_INCOME"].ge((2 * df["FAMILY_INCOME"].median())) & ~df["FAMILY_INCOME"].isna()
df.loc[cond, "PARENTAL_INCOME_VERY_HIGH"] = 1

# We restrict sample to years in which individuals were at least 16
cond = df["AGE"] >= 15
df = df.loc[cond]

df["aux_schooling"] = df["REAL_HIGHEST_GRADE_COMPLETED"].copy().shift(-1)

cond = (
    df["AGE"].eq(16)
    & df["REAL_HIGHEST_GRADE_COMPLETED"].shift(-1).ge(10)
    & df["SURVEY_YEAR"].eq(1977)
)
df.loc[cond, "CHOICE"] = df.loc[cond, "SPECIFIC_CHOICE"] = "schooling"
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[cond, "aux_schooling"] - 1

cond = (
    df["AGE"].eq(16)
    & df["REAL_HIGHEST_GRADE_COMPLETED"].shift(-1).eq(9)
    & df["SURVEY_YEAR"].eq(1977)
    & df["CHOICE"].shift(-1).eq("schooling")
)
df.loc[cond, "CHOICE"] = df.loc[cond, "SPECIFIC_CHOICE"] = "schooling"
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[cond, "aux_schooling"] - 1

cond = df["AGE"].eq(16) & df["SURVEY_YEAR"].eq(1977) & df["CHOICE"].ne("schooling")
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[cond, "aux_schooling"]

cond = df["CHOICE"].eq("schooling") & ~df["INCOME"].isna()
df.loc[cond, "INCOME"] = np.nan


df["aux_schooling"] = df["REAL_HIGHEST_GRADE_COMPLETED"].copy().shift(-1)
cond_1 = df["AGE"].eq(15) & df["SURVEY_YEAR"].isin([1976, 1977])
cond_2 = df["REAL_HIGHEST_GRADE_COMPLETED"].shift(-1).ge(9)
df.loc[cond_1 & cond_2, "CHOICE"] = "schooling"
df.loc[cond_1 & cond_2, "REAL_HIGHEST_GRADE_COMPLETED"] = (
    df.loc[cond_1 & cond_2, "aux_schooling"] - 1
)

cond_2 = df["REAL_HIGHEST_GRADE_COMPLETED"].shift(-1).le(8)
df.loc[cond_1 & cond_2, "CHOICE"] = "home"
df.loc[cond_1 & cond_2, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[cond_1 & cond_2, "aux_schooling"]

cond = df["AGE"].eq(15) & df["CHOICE"].isin(["blue_collar", "white_collar", "military"])
df.loc[cond, "CHOICE"] = "home"

print(sum(df.loc[df["AGE"].eq(15), "REAL_HIGHEST_GRADE_COMPLETED"].isna()))
# truncate observations according to footnote 15 on p. 484,

df["CONSECUTIVE_HIGHEST_GRADES_MISSING"] = 0

# Create indicator variable for years which are the first of two consecutive years with missing
# 'REAL_HIGHEST_GRADE_COMPLETED'
cond = (
    df["REAL_HIGHEST_GRADE_COMPLETED"].isna()
    & df["REAL_HIGHEST_GRADE_COMPLETED"].shift(-1).isna()
    & df["IDENTIFIER"].eq(df["IDENTIFIER"].shift(-1))
)
df.loc[cond, "CONSECUTIVE_HIGHEST_GRADES_MISSING"] = 1

df["CONSECUTIVE_HIGHEST_GRADES_MISSING"] = df.groupby(
    "IDENTIFIER"
).CONSECUTIVE_HIGHEST_GRADES_MISSING.cumsum()
df = df.loc[df["CONSECUTIVE_HIGHEST_GRADES_MISSING"] == 0]

# drop observations according to footnote 17 on p. 484
# Create indicator variable for years in which more than 5 of the 9 weekly
# labor force statuses is missing
df["CUTOFF_WORK"] = 0

cond = df["EMP_NONMISSING_WEEKS"].le(3) & df["AGE"].ge(16)
df.loc[cond, "CUTOFF_WORK"] = 1

df["CUTOFF_WORK"] = df.groupby("IDENTIFIER").CUTOFF_WORK.cumsum()
df = df[df["CUTOFF_WORK"] == 0]

df = df.groupby(df["IDENTIFIER"]).apply(lambda x: get_schooling_experience(x))


# Delete all individuals for which baseline schooling (i. e. schooling at age 16) is less than 7
cond = df["AGE"].eq(16) & df["SCHOOLING"].lt(7)
schooling_too_low = df.loc[cond, "IDENTIFIER"].unique()

df.drop(index=schooling_too_low, level=0, inplace=True)

# save data set
df.to_pickle("../../output/data/final/original_extended_final.pkl")

# create and save continuous data set
cond = df.loc[df["SURVEY_YEAR"].eq(2011), "CHOICE"].isin(
    ["schooling", "blue_collar", "white_collar", "military", "home"]
)
continuous_list = list(cond.index.get_level_values(0))

cont_df = df[df["IDENTIFIER"].isin(continuous_list)]

cont_df.to_pickle("../../output/data/final/cont_original_extended_final.pkl")

# create and save extended replication of original KW97 data set
cond = df["AGE"].ge(16)
ext_kw_df = df.loc[cond, ["IDENTIFIER", "AGE", "SCHOOLING", "CHOICE", "INCOME"]]
ext_kw_df.rename(
    columns={
        "IDENTIFIER": "Identifier",
        "AGE": "Age",
        "SCHOOLING": "Schooling",
        "CHOICE": "Choice",
        "INCOME": "Wage",
    },
    inplace=True,
)
ext_kw_df.to_csv("../../ext_kw_data.csv", index=False)

# create and save replication of original KW97 data set
cond = df["AGE"].ge(16) & df["SURVEY_YEAR"].le(1987)
kw_df = df.loc[cond, ["IDENTIFIER", "AGE", "SCHOOLING", "CHOICE", "INCOME"]]
kw_df.rename(
    columns={
        "IDENTIFIER": "Identifier",
        "AGE": "Age",
        "SCHOOLING": "Schooling",
        "CHOICE": "Choice",
        "INCOME": "Wage",
    },
    inplace=True,
)
kw_df.to_csv("../../kw_data.csv", index=False)
