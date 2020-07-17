#!/usr/bin/env python
# coding: utf-8

"""This script translates the weekly labor force status into occupation codes
"""

import numpy as np
import pandas as pd

from functions_prelim_adjust import data_shift


df = pd.read_pickle('../../output/data/raw/original_extended.pkl')

# Construct variable 'AGE_OCT' that specifies the age of an individual on OCT, 1 of each survey year
df['AGE_OCT'] = df['SURVEY_YEAR'] - df['YEAR_OF_BIRTH']
cond = df.MONTH_OF_BIRTH > 9
df.loc[cond, 'AGE_OCT'] = df['AGE_OCT'] - 1


# Restrict sample to white males from the core random sample, i. e. SAMPLE_ID equals 1 or 2
cond = df['SAMPLE_ID'].isin([1, 2])
df = df.loc[cond]


# Restrict sample to individuals who were age 16 or less on October 1, 1977 (<=> 'SURVEY_YEAR' - 'AGE_OCT' >= 1961)
cond = df['SURVEY_YEAR'] - df['AGE_OCT'] >= 1961
df = df.loc[cond]


# construct a variable that displays which survey round took place in a given year if there was any (, e. g. 1979 =
# survey round #1)

df['SURVEY_ROUND'] = np.nan

# For all years until 1994, interviews are conducted annually
cond = df['SURVEY_YEAR'] <= 1994
df.loc[cond, 'SURVEY_ROUND'] = (df['SURVEY_YEAR'] - 1978).astype(int)

# After 1994, interviews are conducted biannually in even numbered years
cond = (df['SURVEY_YEAR'] > 1994) & ~((df['SURVEY_YEAR'] % 2).astype(bool))
df.loc[cond, 'SURVEY_ROUND'] = ((df['SURVEY_YEAR'] - 1994) / 2 + 16).astype(int)

# For all odd numbered years after 1994, 'SURVEY_ROUND' takes the same value as in the next even numbered year

cond = (df['SURVEY_YEAR'] > 1994) & (df['SURVEY_YEAR'] % 2).astype(bool)
df.loc[cond, 'SURVEY_ROUND'] = (((df['SURVEY_YEAR'] + 1) - 1994) / 2 + 16).astype(int)

df['SURVEY_ROUND'] = pd.Series(df['SURVEY_ROUND'], dtype='Int64')


# split the values in "EMP_STATUS_WK" into the relevant survey round (first digit/two digits)
# and the relevant job number (last two digits)
# based on the relevant survey round, determine the shift of the occjob_mod variables
# that is necessary so that the job choice in a given year uses the jobs
# from the survey year that correspond to the relevant survey round

for week_num in [1, 7, 13, 14, 20, 26, 40, 46, 52]:
    df['JOB_CHOICE_WK_' + repr(week_num)] = np.nan
    df['WAGE_WK_' + repr(week_num)] = np.nan

    cond = df['EMP_STATUS_WK_' + repr(week_num)] >= 100
    df.loc[cond, 'ROUND_JOBS_WK_' + repr(week_num)] = (df.loc[cond, 'EMP_STATUS_WK_' + repr(week_num)] / 100).astype(
        int)
    df.loc[cond, 'JOB_NUMBER_WK_' + repr(week_num)] = (df.loc[cond, 'EMP_STATUS_WK_' + repr(week_num)] % 10)

    df['REQUIRED_SHIFT_WK_' + repr(week_num)] = np.nan

    cond = (df['SURVEY_ROUND'] <= 16) & (df['ROUND_JOBS_WK_' + repr(week_num)] <= 16)
    df.loc[cond, 'REQUIRED_SHIFT_WK_' + repr(week_num)] = df['ROUND_JOBS_WK_' + repr(week_num)] - df['SURVEY_ROUND']

    cond = (df['SURVEY_ROUND'] <= 16) & (df['ROUND_JOBS_WK_' + repr(week_num)] > 16)
    df.loc[cond, 'REQUIRED_SHIFT_WK_' + repr(week_num)] = (df['ROUND_JOBS_WK_' + repr(week_num)] - 16) * 2 + (
                16 - df['SURVEY_ROUND'])

    cond = (df['SURVEY_ROUND'] > 16) & (df['SURVEY_YEAR'] % 2).astype(bool)
    df.loc[cond, 'REQUIRED_SHIFT_WK_' + repr(week_num)] = (df['ROUND_JOBS_WK_' + repr(week_num)] - df[
        'SURVEY_ROUND']) * 2 + 1

    cond = (df['SURVEY_ROUND'] > 16) & ~(df['SURVEY_YEAR'] % 2).astype(bool)
    df.loc[cond, 'REQUIRED_SHIFT_WK_' + repr(week_num)] = (df['ROUND_JOBS_WK_' + repr(week_num)] - df[
        'SURVEY_ROUND']) * 2

    df['JOB_YEAR_WK_' + repr(week_num)] = df['SURVEY_YEAR'] + df['REQUIRED_SHIFT_WK_' + repr(week_num)]

df_ext = pd.DataFrame(df.groupby(df['IDENTIFIER']).apply(lambda x: data_shift(x)))

df_ext.to_pickle('../../output/data/interim/jobs_with_occ_codes.pkl')