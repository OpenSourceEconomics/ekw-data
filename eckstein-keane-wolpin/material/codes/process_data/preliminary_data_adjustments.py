"""This script performs basic data requirements established in KW97 and directly adjusts special
cases which cannot be implemented automatically. """

import os
from pathlib import Path

import numpy as np
import pandas as pd
from functions_prelim_adjust import adjust_hgc_12_for_ged
from functions_prelim_adjust import extend_sample_id
from functions_prelim_adjust import extend_survey_year
from functions_prelim_adjust import extend_table_13_covariates
from functions_prelim_adjust import months_attended_school
from functions_prelim_adjust import simple_two_grade_jump

PROJECT_DIR = Path(os.environ["PROJECT_ROOT"])

# read in data
df = pd.read_pickle(
    PROJECT_DIR / "eckstein-keane-wolpin/material/output/data/raw/original_extended.pkl"
)

# Restrict sample to white males from the core random sample, i. e. SAMPLE_ID equals 1 or 2
cond = df["SAMPLE_ID"].isin([1, 2])
df = df.loc[cond]

# Construct variable 'AGE' that specifies the age of an individual on OCT, 1 of each survey year
df["AGE"] = df["SURVEY_YEAR"] - df["YEAR_OF_BIRTH"]

cond = df.MONTH_OF_BIRTH > 9
df.loc[cond, "AGE"] = df.loc[cond, "AGE"] - 1

# Restrict sample to individuals who were age 16 or less on October 1, 1977
# (<=> 'SURVEY_YEAR' - 'AGE' >= 1961)
cond = df["SURVEY_YEAR"] - df["AGE"] >= 1961
df = df.loc[cond]
len(df["IDENTIFIER"].unique())

#
id_list = df["IDENTIFIER"].unique()

age_df = pd.DataFrame(np.repeat(id_list, 36))
age_df.rename(columns={0: "IDENTIFIER"}, inplace=True)

age_df["AGE"] = np.tile(np.array(range(15, 51)), len(id_list))

df = pd.merge(
    df, age_df, how="outer", left_on=["IDENTIFIER", "AGE"], right_on=["IDENTIFIER", "AGE"]
)


df = df.groupby(df["IDENTIFIER"]).apply(lambda x: extend_survey_year(x))
df = df.groupby(df["IDENTIFIER"]).apply(lambda x: extend_table_13_covariates(x))

df["SURVEY_YEAR"] = df["SURVEY_YEAR"].astype("Int64")
df["Survey Year"] = df["SURVEY_YEAR"]
df["Identifier"] = df["IDENTIFIER"]
df.set_index(["Identifier", "Survey Year"], inplace=True)
df.sort_values(by=["IDENTIFIER", "SURVEY_YEAR"], inplace=True)

df = df.groupby(df["IDENTIFIER"]).apply(lambda x: extend_sample_id(x))

# Gaps in the HGC variables and the 'highest grade attended' cannot decrease and gaps
# in these variables can thus be potentially interpolated.
# We interpolate these variables if the values before and after the gaps are the same (i.e. simply
# fill gaps with this value) or if the values before and after the gaps suggest that
# one grade level was completed in each of the years with missing values (i. e. fill gaps linearly,
# increasing by one each year)
for prefix in ["REVISED_", "UNREVISED_"]:
    df[prefix + "AUX_HGC"] = df[prefix + "HIGHEST_GRADE_COMPLETED_MAY"].copy()

    df[prefix + "HIGHEST_GRADE_COMPLETED_MAY"] = (
        df[prefix + "HIGHEST_GRADE_COMPLETED_MAY"]
        .groupby(df["IDENTIFIER"])
        .apply(lambda x: x.interpolate(method="linear", limit_area="inside"))
    )

    cond_1 = ~(df[prefix + "HIGHEST_GRADE_COMPLETED_MAY"].diff().shift(-1).isin([0.0, 1.0]))
    cond_2 = df[prefix + "AUX_HGC"].isna()
    df.loc[cond_1 & cond_2, prefix + "HIGHEST_GRADE_COMPLETED_MAY"] = np.nan

    df.drop(columns=[prefix + "AUX_HGC"], inplace=True)

df["AUX_HGA"] = df["HIGHEST_GRADE_ATTENDED"].copy()

df["HIGHEST_GRADE_ATTENDED"] = (
    df["HIGHEST_GRADE_ATTENDED"]
    .groupby(df["IDENTIFIER"])
    .apply(lambda x: x.interpolate(method="linear", limit_area="inside"))
)

cond_1 = ~(df["HIGHEST_GRADE_ATTENDED"].diff().shift(-1).isin([0.0, 1.0]))
cond_2 = df["AUX_HGA"].isna()
df.loc[cond_1 & cond_2, "HIGHEST_GRADE_ATTENDED"] = np.nan

df.drop(columns=["AUX_HGA"], inplace=True)

# As the HGC variables indicate the highest grade completed in May of each year,
# the HGC variable and the enrollment status variable have to be shifted by one given
# the definition of a year in KW97

df["REAL_HIGHEST_GRADE_COMPLETED"] = (
    df["REVISED_HIGHEST_GRADE_COMPLETED_MAY"].groupby(df["IDENTIFIER"]).shift(-1)
)

df["REAL_ENROLLMENT_STATUS"] = (
    df["REVISED_ENROLLMENT_STATUS_MAY"].groupby(df["IDENTIFIER"]).shift(-1)
)

for num in range(1, 6):
    cond = (df["IDENTIFIER"] == 5585) & (df["JOB_" + repr(num)] == 26)
    df.loc[cond, "JOB_" + repr(num)] = 385

# Changes to 'JOB_1' if the values in 'JOB_1' are not valid 1970 occupation codes and are equal
# to CPSOCC70. The values are corrected with help of the CPSOCC80 variable in which the CPS job
# of the year is coded in 1980 occupation codes

# CPSOCC70 and CPSOCC80 are the wrong way around given the next two realizations
cond = (df["IDENTIFIER"] == 1975) & (df["JOB_1"] == 547)
df.loc[cond, "JOB_1"] = 495

# Typo in CPSOCC70 given that CPSOCC80 is very similar for 208 and 280
cond = (df["IDENTIFIER"] == 2185) & (df["JOB_1"] == 208)
df.loc[cond, "JOB_1"] = 280

# Typo in CPSOCC70 given that CPSOCC80 is the same for 706 and 709
cond = (df["IDENTIFIER"] == 5306) & (df["JOB_1"] == 709)
df.loc[cond, "JOB_1"] = 706

# Identifier: 376
# HIGHEST_GRADE_ATTENDED: 10, last month/year enrolled in school: 06/1977
# => 'REAL_HIGHEST_GRADE_COMPLETED' at age 16 (1977): 10, consistent with KW data
cond = (df["IDENTIFIER"] == 376) & (df["AGE"] == 16)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 10

# Identifier: 735
cond = (df["IDENTIFIER"] == 735) & (df["AGE"] == 16)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 9

cond = (df["IDENTIFIER"] == 735) & (df["AGE"] == 17)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 10

# Identifier: 1679
# HIGHEST_GRADE_ATTENDED: 10, last month/year enrolled in school: 02/1978
# => 'REAL_HIGHEST_GRADE_COMPLETED' at age 16 (1978): 10, consistent with KW data
cond = (df["IDENTIFIER"] == 1679) & (df["AGE"] == 16)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 10

# Identifier: 1743
cond = (df["IDENTIFIER"] == 1743) & (df["AGE"] == 16)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 9

# Identifier: 2182
cond = (df["IDENTIFIER"] == 2182) & (df["AGE"] == 16)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 10

cond = (df["IDENTIFIER"] == 2182) & (df["AGE"] == 17)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 11

# Identifier: 2326
# HIGHEST_GRADE_ATTENDED: 10, last month/year enrolled in school: 03/1977
# => 'REAL_HIGHEST_GRADE_COMPLETED' at age 16 (1977): 10
cond = (df["IDENTIFIER"] == 2326) & (df["AGE"] == 16)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 10

# Identifier: 2371 HIGHEST_GRADE_ATTENDED: 12, last month/year enrolled in school: 12/1978 =>
# 'REAL_HIGHEST_GRADE_COMPLETED' as of 10/1978(AGE 17): 11
# BUT: received GED in 02/1979 and therefore seems to have not completed grade 12
# as 'REAL_HIGHEST_GRADE_COMPLETED' at age 17 equals 11, REAL_HIGHEST_GRADE_COMPLETED' at age
# 16 is set to 10
cond = (df["IDENTIFIER"] == 2371) & (df["AGE"] == 16)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 10

cond = (df["IDENTIFIER"] == 2371) & (df["AGE"] == 17)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 11

# Identifier: 2381
cond = (df["IDENTIFIER"] == 2381) & (df["AGE"] == 16)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 10

cond = (df["IDENTIFIER"] == 2381) & (df["AGE"] == 17)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 11

# Identifier: 4491
# as there is no receiving date for the GED, I follow KW with the baseline schooling at age 16
cond = (df["IDENTIFIER"] == 4491) & (df["AGE"] == 16)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 11

# Identifier: 5704
# HIGHEST_GRADE_ATTENDED: 11, last month/year enrolled in school: 03/1978
# => highest grade completed in 10/1977: 10
# => 'REAL_HIGHEST_GRADE_COMPLETED' at age 16 (1977): 10, consistent with KW data
cond = (df["IDENTIFIER"] == 5704) & (df["AGE"] == 16)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 10

# For a small number of individuals, there are decreases in the HGC variable from
# one year to the next, e. g. from 16 to 15 in the following year.
# As those decreases are not actually possible, they are corrected on the basis of
# the other values of the HGC variable ID 600
cond = (df["IDENTIFIER"] == 600) & (df["AGE"] == 32)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 16

# ID 725
cond = (df["IDENTIFIER"] == 725) & (df["AGE"] == 40)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 20

# ID 1046
cond = (df["IDENTIFIER"] == 1046) & df["AGE"].ge(30) & (df["REAL_HIGHEST_GRADE_COMPLETED"] == 18)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 19

# ID 1109
cond = (df["IDENTIFIER"] == 1109) & df["AGE"].ge(28) & (df["REAL_HIGHEST_GRADE_COMPLETED"] == 13)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 14

# ID 1309
cond = (df["IDENTIFIER"] == 1309) & df["AGE"].ge(32) & (df["REAL_HIGHEST_GRADE_COMPLETED"] == 12)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 13

# ID 1508
cond = (df["IDENTIFIER"] == 1508) & (df["AGE"].isin([38, 39, 40]))
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 14

# ID 2642
cond = (df["IDENTIFIER"] == 2642) & (df["AGE"].isin([40, 41, 42]))
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 18

# ID 2870
cond = (df["IDENTIFIER"] == 2870) & (df["AGE"].isin([41, 42, 43]))
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 18

# ID 2904
cond = (df["IDENTIFIER"] == 2904) & (df["AGE"] == 32)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 19

# ID 3401
cond = (df["IDENTIFIER"] == 3401) & df["AGE"].ge(32) & (df["REAL_HIGHEST_GRADE_COMPLETED"] == 12)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 13

# ID 3521
cond = (df["IDENTIFIER"] == 3521) & (df["AGE"] == 20)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 13

cond = (df["IDENTIFIER"] == 3521) & df["AGE"].ge(36) & (df["REAL_HIGHEST_GRADE_COMPLETED"] == 13)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 14

# ID 3680
cond = (df["IDENTIFIER"] == 3680) & (df["AGE"] == 26)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 4010
cond = (df["IDENTIFIER"] == 4010) & (df["AGE"].isin([38, 39, 40]))
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 19

# ID 5095
cond = (df["IDENTIFIER"] == 5095) & (df["AGE"].isin([30, 31]))
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 19

# ID 5185
cond = (df["IDENTIFIER"] == 5185) & (df["AGE"].isin([38, 39, 40]))
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 20

# ID 5329
cond = (df["IDENTIFIER"] == 5329) & (df["AGE"].isin([40, 41, 41]))
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 13

# ID 5364
cond = (df["IDENTIFIER"] == 5364) & (df["AGE"].isin([39, 40, 41]))
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 14

# ID 5394
cond = (df["IDENTIFIER"] == 5394) & (df["AGE"].isin([40, 41, 42]))
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 18

# ID 5534
cond = (df["IDENTIFIER"] == 5534) & (df["AGE"] == 16)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 10

# ID 11758
cond = (df["IDENTIFIER"] == 11758) & (df["AGE"].isin([38, 39, 40, 41, 42]))
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 20

# ID 11820
cond = (df["IDENTIFIER"] == 11820) & (df["AGE"] == 32)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 16

# ID 12106
cond = (df["IDENTIFIER"] == 12106) & (df["AGE"] == 22)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 14


# There are cases in which more than one grade was completed within one year.
# Most of these cases are corrected/smoothed in the following.

# ID 70
cond = (df["IDENTIFIER"] == 70) & df["AGE"].isin([19, 20, 21])
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] + 1

# ID 81
cond = (df["IDENTIFIER"] == 81) & (df["AGE"] == 25)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

cond = (df["IDENTIFIER"] == 81) & (df["AGE"] == 27)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 17

cond = (df["IDENTIFIER"] == 81) & (df["AGE"] == 28)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 18

# ID 113
cond = (df["IDENTIFIER"] == 113) & (df["AGE"] == 18)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 11

# ID 135
cond = (df["IDENTIFIER"] == 135) & (df["AGE"].isin(range(21, 28)))
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 14

# ID 207 (jump)
cond = (df["IDENTIFIER"] == 207) & (df["AGE"] == 33)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 9

# ID 230
cond = (df["IDENTIFIER"] == 230) & (df["AGE"] == 22)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 13

cond = (df["IDENTIFIER"] == 230) & (df["AGE"] == 23)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 14

# ID 251
cond = (df["IDENTIFIER"] == 251) & (df["AGE"] == 16)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 10

cond = (df["IDENTIFIER"] == 251) & (df["AGE"] == 17)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 11

# ID 372
cond = (df["IDENTIFIER"] == 372) & (df["AGE"] == 44)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 17

# ID 430
cond = (df["IDENTIFIER"] == 430) & (df["AGE"] == 18)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 11

# ID 562
cond = (df["IDENTIFIER"] == 562) & (df["AGE"] == 24)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 18

# ID 570
cond = (df["IDENTIFIER"] == 570) & (df["AGE"] == 16)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 11

# ID 587 fine as is

# ID 638
cond = (df["IDENTIFIER"] == 638) & (df["AGE"] == 41)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 14

cond = (df["IDENTIFIER"] == 638) & (df["AGE"] == 42)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 725
cond = (df["IDENTIFIER"] == 725) & (df["AGE"] == 28)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 18

cond = (df["IDENTIFIER"] == 725) & (df["AGE"] == 29)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 19

# ID 795
cond = (df["IDENTIFIER"] == 795) & (df["AGE"] == 35)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 14

cond = (df["IDENTIFIER"] == 795) & (df["AGE"] == 36)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

cond = (df["IDENTIFIER"] == 795) & (df["AGE"] == 37)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 16

# ID 864
cond = (df["IDENTIFIER"] == 864) & df["AGE"].isin([19, 31, 32])
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] + 1

# ID 873
cond = (df["IDENTIFIER"] == 873) & df["AGE"].isin([19, 20])
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] - 1

# ID 902
cond = (df["IDENTIFIER"] == 902) & (df["AGE"] == 23)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 16

# ID 903
cond = (df["IDENTIFIER"] == 903) & (df["AGE"] == 16)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 11

# ID 1145
cond = (df["IDENTIFIER"] == 1145) & (df["AGE"] == 18)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 12

# ID 1171
cond = (df["IDENTIFIER"] == 1171) & (df["AGE"] == 17)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 11

# ID 1503
cond = (df["IDENTIFIER"] == 1503) & df["AGE"].isin([23, 24])
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] - 1

# ID 1508 PROBLEM!!!!!!!!

# ID 1611
cond = (df["IDENTIFIER"] == 1611) & (df["AGE"] == 16)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 10

# ID 1619
cond = (df["IDENTIFIER"] == 1619) & (df["AGE"] == 23)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 17

# ID 1632 fine as is

# ID 1772 fine as is

# ID 1869
cond = (df["IDENTIFIER"] == 1869) & (df["AGE"] == 16)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 11

# ID 1984
cond = (df["IDENTIFIER"] == 1984) & (df["AGE"] == 29)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 11

# ID 2015
cond = (df["IDENTIFIER"] == 2015) & (df["AGE"] == 16)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 11

# ID 2067
cond = (df["IDENTIFIER"] == 2067) & df["AGE"].isin([16, 17])
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] + 1

# ID 2135 fine as is

# ID 2261
cond = (df["IDENTIFIER"] == 2261) & (df["AGE"] == 23)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 8

cond = (df["IDENTIFIER"] == 2261) & (df["AGE"] == 24)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 9

# ID 2277
cond = (df["IDENTIFIER"] == 2277) & df["AGE"].isin([19, 20, 21])
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] - 1

# ID 2306 (jump)
cond = (df["IDENTIFIER"] == 2306) & (df["AGE"] == 40)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 9

# ID 2415
cond = (df["IDENTIFIER"] == 2415) & (df["AGE"] == 21)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 13

# ID 2520
cond = (df["IDENTIFIER"] == 2520) & (df["AGE"] == 16)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 10

# ID 2545
cond = (df["IDENTIFIER"] == 2545) & (df["AGE"] == 30)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 14

cond = (df["IDENTIFIER"] == 2545) & (df["AGE"] == 32)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 2589
cond = (df["IDENTIFIER"] == 2589) & (df["AGE"] == 24)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 19

# ID 2593
cond = (df["IDENTIFIER"] == 2593) & df["AGE"].isin([20, 23])
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] - 1

cond = (df["IDENTIFIER"] == 2593) & (df["AGE"] == 22)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 13

# ID 2597
cond = (df["IDENTIFIER"] == 2597) & (df["AGE"] == 31)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

cond = (df["IDENTIFIER"] == 2597) & (df["AGE"] == 32)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 16

# ID 2754
cond = (df["IDENTIFIER"] == 2754) & df["AGE"].isin([18, 19])
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] - 1

# ID 2755 fine as is

# ID 2759
cond = (df["IDENTIFIER"] == 2759) & (df["AGE"] >= 17)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 8

# ID 2851 fine as is

# ID 2845
cond = (df["IDENTIFIER"] == 2845) & df["AGE"].isin([25, 26])
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] - 1

# ID 2941
cond = (df["IDENTIFIER"] == 2941) & (df["AGE"] == 21)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 16

# ID 3171
cond = (df["IDENTIFIER"] == 3171) & (df["AGE"] == 21)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 16

# ID 3290
cond = (df["IDENTIFIER"] == 3290) & df["AGE"].isin([24, 25])
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] + 1

# ID 3398
cond = (df["IDENTIFIER"] == 3398) & (df["AGE"] == 16)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 11

# ID 3449
cond = (df["IDENTIFIER"] == 3449) & (df["AGE"] == 18)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 11

cond = (df["IDENTIFIER"] == 3449) & (df["AGE"] == 19)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 12

# ID 3450
cond = (df["IDENTIFIER"] == 3450) & df["AGE"].isin([19, 20, 21])
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] - 1

# ID 3484 fine as is

# ID 3588
cond = (df["IDENTIFIER"] == 3588) & (df["AGE"] == 24)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 3642
cond = (df["IDENTIFIER"] == 3642) & (df["AGE"].isin([23, 24, 25]))
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 17

# ID 3644
cond = (df["IDENTIFIER"] == 3644) & (df["AGE"] == 16)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 10

# ID 3788
cond = (df["IDENTIFIER"] == 3788) & df["AGE"].isin([16, 17])
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] + 1

# ID 3854
cond = (df["IDENTIFIER"] == 3854) & (df["AGE"] == 16)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 10

# ID 3863
cond = (df["IDENTIFIER"] == 3863) & df["AGE"].isin([19, 20, 21])
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] - 1

# ID 3865
cond = (df["IDENTIFIER"] == 3865) & (df["AGE"] == 23)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 17

cond = (df["IDENTIFIER"] == 3865) & (df["AGE"] == 24)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 18

# ID 3880
cond = (df["IDENTIFIER"] == 3880) & (df["AGE"] == 18)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 12

# ID 3905
cond = (df["IDENTIFIER"] == 3905) & df["AGE"].isin([16, 17])
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] + 1

# ID 4009
cond = (df["IDENTIFIER"] == 4009) & df["AGE"].isin([15, 16])
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] + 1

# ID 4042 fine as is

# ID 4059
cond = (df["IDENTIFIER"] == 4059) & df["AGE"].isin([22, 23, 24])
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] - 1

# ID 4067
cond = (df["IDENTIFIER"] == 4067) & (df["AGE"] == 16)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 11

# ID 4137
cond = (df["IDENTIFIER"] == 4137) & (df["AGE"] == 18)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 12

# ID 4191
cond = (df["IDENTIFIER"] == 4191) & df["AGE"].isin([18, 19])
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] - 1

# ID 4289
cond = (df["IDENTIFIER"] == 4289) & df["AGE"].isin([17, 20, 21, 23, 24])
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] - 1

cond = (df["IDENTIFIER"] == 4289) & df["AGE"].isin([18, 19])
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] - 2

# ID 4330 fine as is

# ID 4348
cond = (df["IDENTIFIER"] == 4348) & (df["AGE"] == 22)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 12

# ID 4435 fine as is

# ID 4461
cond = (df["IDENTIFIER"] == 4461) & (df["AGE"] == 16)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 10

# ID 4471
cond = (df["IDENTIFIER"] == 4471) & (df["AGE"] == 22)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 4529
cond = (df["IDENTIFIER"] == 4529) & (df["AGE"] == 21)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 11

cond = (df["IDENTIFIER"] == 4529) & (df["AGE"] == 24)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 13

cond = (df["IDENTIFIER"] == 4529) & (df["AGE"] == 25)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 14

# ID 4830
cond = (df["IDENTIFIER"] == 4830) & (df["AGE"] == 20)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 13

# ID 4831
cond = (df["IDENTIFIER"] == 4831) & df["AGE"].isin([23, 24])
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] - 1

# ID 4834
cond = (df["IDENTIFIER"] == 4834) & df["AGE"].isin([38, 39])
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] + 1

cond = (df["IDENTIFIER"] == 4834) & (df["AGE"] == 40)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 4843
cond = (df["IDENTIFIER"] == 4843) & (df["AGE"] == 31)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 5012
cond = (df["IDENTIFIER"] == 5012) & df["AGE"].isin([21, 22, 23])
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] - 1

# ID 5036
cond = (df["IDENTIFIER"] == 5036) & df["AGE"].isin([19, 20, 22])
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] - 1

# ID 5102
cond = (df["IDENTIFIER"] == 5102) & (df["AGE"] == 19)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 13

# ID 5168
cond = (df["IDENTIFIER"] == 5168) & (df["AGE"] == 28)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 16

# ID 5177 fine as is

# ID 5184
cond = (df["IDENTIFIER"] == 5184) & (df["AGE"] == 16)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 9

# ID 5185
cond = (df["IDENTIFIER"] == 5185) & (df["AGE"] == 25)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 17

# ID 5215
cond = (df["IDENTIFIER"] == 5215) & (df["AGE"].isin(range(16, 25)))
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 9

# ID 5252
cond = (df["IDENTIFIER"] == 5252) & (df["AGE"] == 17)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 11

# ID 5281
cond = (df["IDENTIFIER"] == 5281) & (df["AGE"] == 42)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 11

# ID 5343
cond = (df["IDENTIFIER"] == 5343) & df["AGE"].isin([19, 20, 21])
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] - 1

# ID 5358
cond = (df["IDENTIFIER"] == 5358) & (df["AGE"] == 19)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 13

# ID 5394
cond = (df["IDENTIFIER"] == 5394) & (df["AGE"] == 19)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 13

cond = (df["IDENTIFIER"] == 5394) & (df["AGE"] == 23)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 17

# ID 5491
cond = (df["IDENTIFIER"] == 5491) & (df["AGE"] == 16)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 10

cond = (df["IDENTIFIER"] == 5491) & (df["AGE"] == 17)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 11

# ID 5512
cond = (df["IDENTIFIER"] == 5512) & (df["AGE"] == 43)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 14

cond = (df["IDENTIFIER"] == 5512) & (df["AGE"] == 44)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

cond = (df["IDENTIFIER"] == 5512) & (df["AGE"] == 45)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 16

# ID 5567
cond = (df["IDENTIFIER"] == 5567) & df["AGE"].isin([19, 20, 23])
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] - 1

# ID 11823
cond = (df["IDENTIFIER"] == 11823) & df["AGE"].isin([24, 25])
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] - 1

# ID 11888
cond = (df["IDENTIFIER"] == 11888) & (df["AGE"] == 17)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 11

# ID 11954
cond = (df["IDENTIFIER"] == 11954) & (df["AGE"] == 16)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 10

# ID 11964
cond = (df["IDENTIFIER"] == 11964) & df["AGE"].isin([19, 20])
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] - 1

# ID 12043 censored at age 32 due to conflicting information from data
cond = (df["IDENTIFIER"] == 12043) & df["AGE"].ge(33)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = np.nan

# ID 12069
cond = (df["IDENTIFIER"] == 12069) & (df["AGE"] == 38)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 17

cond = (df["IDENTIFIER"] == 12069) & (df["AGE"] == 39)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 18

cond = (df["IDENTIFIER"] == 12069) & (df["AGE"] == 40)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 19

# ID 12106
cond = (df["IDENTIFIER"] == 12106) & df["AGE"].isin([25, 26, 27])
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] - 1

cond = df["WHICH_OF_HS_OR_GED"].isin([2.0])
list_ged = list(df["IDENTIFIER"].loc[cond])
cond = df["IDENTIFIER"].isin(list_ged)

df[cond] = df[cond].groupby(df["IDENTIFIER"]).apply(lambda x: adjust_hgc_12_for_ged(x))

df = df.groupby(df["IDENTIFIER"]).apply(lambda x: months_attended_school(x))
df = df.groupby(df["IDENTIFIER"]).apply(lambda x: simple_two_grade_jump(x))

df["AUX_HGC"] = df["REAL_HIGHEST_GRADE_COMPLETED"].ffill()
cond_1 = (df["MONTHS_ATTENDED_SCHOOL"].diff().shift(-1) <= 0) & (
    df["REAL_ENROLLMENT_STATUS"].shift(1).isin([2.0, 3.0])
)
cond_2 = (
    ~(df["REAL_HIGHEST_GRADE_COMPLETED"].shift(1).isna())
    & (df["REAL_HIGHEST_GRADE_COMPLETED"].isna())
    & ~(df["REAL_HIGHEST_GRADE_COMPLETED"].shift(-1).isna())
)
cond_3 = (df["REAL_HIGHEST_GRADE_COMPLETED"].shift(1) + 1) == df[
    "REAL_HIGHEST_GRADE_COMPLETED"
].shift(-1)

df.loc[cond_1 & cond_2 & cond_3, "REAL_HIGHEST_GRADE_COMPLETED"] = (
    df.loc[cond_1 & cond_2, "AUX_HGC"] + 1
)
df.loc[~cond_1 & cond_2 & cond_3, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[
    ~cond_1 & cond_2, "AUX_HGC"
]

df.drop(columns=["AUX_HGC"], inplace=True)

df["AUX_HGC"] = df["REAL_HIGHEST_GRADE_COMPLETED"].copy()

df["REAL_HIGHEST_GRADE_COMPLETED"] = (
    df["REAL_HIGHEST_GRADE_COMPLETED"]
    .groupby(df["IDENTIFIER"])
    .apply(lambda x: x.interpolate(method="linear", limit_area="inside"))
)

cond_1 = ~(df["REAL_HIGHEST_GRADE_COMPLETED"].diff().shift(-1).isin([0.0, 1.0]))
cond_2 = df["AUX_HGC"].isna()
df.loc[cond_1 & cond_2, "REAL_HIGHEST_GRADE_COMPLETED"] = np.nan

df.drop(columns=["AUX_HGC"], inplace=True)

# correct 'REAL_HIGHEST_GRADE_COMPLETED' if degree was obtained between October and May

# ID 9: Community college degree 11/87
cond = df["IDENTIFIER"].eq(9) & df["SURVEY_YEAR"].eq(1988)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 14

# ID 26: Bachelor degree 12/87
cond = df["IDENTIFIER"].eq(26) & df["SURVEY_YEAR"].eq(1987)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 106: Bachelor degree 12/83
cond = df["IDENTIFIER"].eq(106) & df["SURVEY_YEAR"].eq(1983)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 191: Bachelor degree 12/85
cond = df["IDENTIFIER"].eq(191) & df["SURVEY_YEAR"].eq(1985)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 318: HS degree 11/81
cond = df["IDENTIFIER"].eq(318) & df["SURVEY_YEAR"].eq(1981)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 11

# ID 372: Bachelor degree 05/2003
cond = df["IDENTIFIER"].eq(372) & df["SURVEY_YEAR"].eq(2003)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 16

# ID 406: Community college degree 05/97
cond = df["IDENTIFIER"].eq(406) & df["SURVEY_YEAR"].eq(1996)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 13

# ID 445: Bachelor degree 12/86
cond = df["IDENTIFIER"].eq(445) & df["SURVEY_YEAR"].eq(1986)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 570: Bachelor degree 04/99
cond = df["IDENTIFIER"].eq(570) & df["SURVEY_YEAR"].eq(1998)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 573: HS degree 09/79
cond = df["IDENTIFIER"].eq(573) & df["SURVEY_YEAR"].eq(1978)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 11

# ID 667: Community college degree 12/85
cond = df["IDENTIFIER"].eq(667) & df["SURVEY_YEAR"].eq(1985)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 13

# ID 750: HS degree 01/81
cond = df["IDENTIFIER"].eq(750) & df["SURVEY_YEAR"].eq(1980)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 11

# ID 817: Bachelor degree 12/89
cond = df["IDENTIFIER"].eq(817) & df["SURVEY_YEAR"].eq(1989)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 882: Bachelor degree 12/84
cond = df["IDENTIFIER"].eq(882) & df["SURVEY_YEAR"].eq(1984)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 913: Bachelor degree 11/87
cond = df["IDENTIFIER"].eq(913) & df["SURVEY_YEAR"].eq(1987)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 946: Bachelor degree 12/84
cond = df["IDENTIFIER"].eq(946) & df["SURVEY_YEAR"].eq(1984)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 960: Bachelor degree 05/83
cond = df["IDENTIFIER"].eq(960) & df["SURVEY_YEAR"].ge(1983)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 16

# ID 961: Bachelor degree 10/85
cond = df["IDENTIFIER"].eq(961) & df["SURVEY_YEAR"].isin([1984, 1985])
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 1003: Bachelor degree 12/86
cond = df["IDENTIFIER"].eq(1003) & df["SURVEY_YEAR"].eq(1986)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 1021: Bachelor degree 05/90
cond = df["IDENTIFIER"].eq(1021) & df["SURVEY_YEAR"].eq(1989)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 1046: Bachelor degree 12/86
cond = df["IDENTIFIER"].eq(1046) & df["SURVEY_YEAR"].eq(1986)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 1146: Bachelor degree 12/84
cond = df["IDENTIFIER"].eq(1146) & df["SURVEY_YEAR"].eq(1984)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 1197: Bachelor degree 12/87
cond = df["IDENTIFIER"].eq(1197) & df["SURVEY_YEAR"].eq(1987)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 1198: Community college degree 12/95
cond = df["IDENTIFIER"].eq(1198) & df["SURVEY_YEAR"].eq(1995)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 13

# ID 1303: Bachelor degree 12/85
cond = df["IDENTIFIER"].eq(1303) & df["SURVEY_YEAR"].eq(1985)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 1503: PhD 12/93
cond = df["IDENTIFIER"].eq(1503) & df["SURVEY_YEAR"].eq(1993)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 19

# ID 1565: Bachelor degree 12/85
cond = df["IDENTIFIER"].eq(1565) & df["SURVEY_YEAR"].eq(1985)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 1588: Bachelor degree 12/89
cond = df["IDENTIFIER"].eq(1588) & df["SURVEY_YEAR"].eq(1989)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 1631: Bachelor degree 12/99
cond = df["IDENTIFIER"].eq(1631) & df["SURVEY_YEAR"].eq(1999)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 1875: Master degree 05/95
cond = df["IDENTIFIER"].eq(1875) & df["SURVEY_YEAR"].eq(1994)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 17

# ID 1916: Other degree 12/94
cond = df["IDENTIFIER"].eq(1916) & df["SURVEY_YEAR"].eq(1994)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 18

# ID 1924: Bachelor degree 05/99
cond = df["IDENTIFIER"].eq(1924) & df["SURVEY_YEAR"].eq(1998)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 1950: Bachelor degree 01/97
cond = df["IDENTIFIER"].eq(1950) & df["SURVEY_YEAR"].eq(1996)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 2006: Bachelor degree 12/84
cond = df["IDENTIFIER"].eq(2006) & df["SURVEY_YEAR"].eq(1984)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 2032: HS degree 01/84
cond = df["IDENTIFIER"].eq(2032) & df["SURVEY_YEAR"].eq(1983)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 11

# ID 2141: Bachelor degree 12/87
cond = df["IDENTIFIER"].eq(2141) & df["SURVEY_YEAR"].eq(1987)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 2291: Bachelor degree 12/86
cond = df["IDENTIFIER"].eq(2291) & df["SURVEY_YEAR"].eq(1986)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 2341: Community college degree 02/88
cond = df["IDENTIFIER"].eq(2341) & df["SURVEY_YEAR"].eq(1987)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 13

# ID 2372: Bachelor degree 05/93
cond = df["IDENTIFIER"].eq(2372) & df["SURVEY_YEAR"].eq(1992)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 2557: Bachelor degree 12/86
cond = df["IDENTIFIER"].eq(2557) & df["SURVEY_YEAR"].eq(1986)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 2611: Bachelor degree 12/84
cond = df["IDENTIFIER"].eq(2611) & df["SURVEY_YEAR"].eq(1984)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 2633: Bachelor degree 02/86
cond = df["IDENTIFIER"].eq(2633) & df["SURVEY_YEAR"].eq(1985)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 2714: Bachelor degree 12/83
cond = df["IDENTIFIER"].eq(2714) & df["SURVEY_YEAR"].eq(1983)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 2767: Community college degree 03/89
cond = df["IDENTIFIER"].eq(2767) & df["SURVEY_YEAR"].eq(1988)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 13

# ID 2800: Master degree 05/95
cond = df["IDENTIFIER"].eq(2800) & df["SURVEY_YEAR"].eq(1994)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 17

# ID 2904: Master degree 12/88
cond = df["IDENTIFIER"].eq(2904) & df["SURVEY_YEAR"].eq(1988)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 17

# ID 2956: Bachelor degree 12/86
cond = df["IDENTIFIER"].eq(2956) & df["SURVEY_YEAR"].eq(1986)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 2963: Bachelor degree 05/95
cond = df["IDENTIFIER"].eq(2963) & df["SURVEY_YEAR"].eq(1994)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 2962: Bachelor degree 12/83
cond = df["IDENTIFIER"].eq(2962) & df["SURVEY_YEAR"].eq(1983)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 3018: Bachelor degree 12/86
cond = df["IDENTIFIER"].eq(3018) & df["SURVEY_YEAR"].eq(1986)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 3019: Bachelor degree 01/84
cond = df["IDENTIFIER"].eq(3019) & df["SURVEY_YEAR"].eq(1983)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 3361: Master degree 01/92
cond = df["IDENTIFIER"].eq(3361) & df["SURVEY_YEAR"].eq(1991)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 17

# ID 3379: Bachelor degree 11/85
cond = df["IDENTIFIER"].eq(3379) & df["SURVEY_YEAR"].eq(1985)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 3464: Bachelor degree 12/83
cond = df["IDENTIFIER"].eq(3464) & df["SURVEY_YEAR"].eq(1983)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 3520: Bachelor degree 12/84
cond = df["IDENTIFIER"].eq(3520) & df["SURVEY_YEAR"].eq(1984)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 3582: Master degree 12/88
cond = df["IDENTIFIER"].eq(3582) & df["SURVEY_YEAR"].eq(1988)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 17

# ID 3583: Bachelor degree 12/85
cond = df["IDENTIFIER"].eq(3583) & df["SURVEY_YEAR"].eq(1985)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 3585: Bachelor degree 12/83
cond = df["IDENTIFIER"].eq(3585) & df["SURVEY_YEAR"].eq(1983)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 3680: Bachelor degree 04/95
cond = df["IDENTIFIER"].eq(3680) & df["SURVEY_YEAR"].eq(1994)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 3724: HS degree 01/82
cond = df["IDENTIFIER"].eq(3724) & df["SURVEY_YEAR"].eq(1981)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 11

# ID 3857: Bachelor degree 12/85
cond = df["IDENTIFIER"].eq(3857) & df["SURVEY_YEAR"].eq(1985)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 3861: Bachelor degree 12/86
cond = df["IDENTIFIER"].eq(3861) & df["SURVEY_YEAR"].eq(1986)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 3875: Bachelor degree 05/86
cond = df["IDENTIFIER"].eq(3875) & df["SURVEY_YEAR"].eq(1985)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 3892: Bachelor degree 12/85
cond = df["IDENTIFIER"].eq(3892) & df["SURVEY_YEAR"].eq(1985)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 4010: Bachelor degree 12/86
cond = df["IDENTIFIER"].eq(4010) & df["SURVEY_YEAR"].eq(1986)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 4056: Bachelor degree 12/83
cond = df["IDENTIFIER"].eq(4056) & df["SURVEY_YEAR"].eq(1983)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 4087: Bachelor degree 12/84
cond = df["IDENTIFIER"].eq(4087) & df["SURVEY_YEAR"].eq(1984)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 4106: Bachelor degree 12/87
cond = df["IDENTIFIER"].eq(4106) & df["SURVEY_YEAR"].eq(1987)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 4191: Master degree 05/89
cond = df["IDENTIFIER"].eq(4191) & df["SURVEY_YEAR"].eq(1988)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 17

# ID 4244: Bachelor degree 12/83
cond = df["IDENTIFIER"].eq(4244) & df["SURVEY_YEAR"].eq(1983)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 4245: Community college degree 01/83
cond = df["IDENTIFIER"].eq(4245) & df["SURVEY_YEAR"].eq(1982)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 13

# ID 4418: Bachelor degree 12/87
cond = df["IDENTIFIER"].eq(4418) & df["SURVEY_YEAR"].eq(1987)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 4466: Bachelor degree 03/2005
cond = df["IDENTIFIER"].eq(4466) & df["SURVEY_YEAR"].eq(2004)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 4470: Bachelor degree 01/95
cond = df["IDENTIFIER"].eq(4470) & df["SURVEY_YEAR"].eq(1994)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] - 1

# ID 4548: Bachelor degree 12/86
cond = df["IDENTIFIER"].eq(4548) & df["SURVEY_YEAR"].eq(1986)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 4669: Community college degree 12/84
cond = df["IDENTIFIER"].eq(4669) & df["SURVEY_YEAR"].eq(1984)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 13

# ID 4693: Bachelor degree 12/85
cond = df["IDENTIFIER"].eq(4693) & df["SURVEY_YEAR"].eq(1985)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 4698: Bachelor degree 12/87
cond = df["IDENTIFIER"].eq(4698) & df["SURVEY_YEAR"].eq(1987)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 4699: Community college degree 12/81
cond = df["IDENTIFIER"].eq(4699) & df["SURVEY_YEAR"].eq(1981)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 13

# ID 4829: Bachelor degree 12/86
cond = df["IDENTIFIER"].eq(4829) & df["SURVEY_YEAR"].eq(1986)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 4831: Master degree 12/93
cond = df["IDENTIFIER"].eq(4831) & df["SURVEY_YEAR"].eq(1993)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 17

# ID 4861: HS degree 05/80
cond = df["IDENTIFIER"].eq(4861) & df["SURVEY_YEAR"].eq(1980)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 12

# ID 4894: Bachelor degree 12/85
cond = df["IDENTIFIER"].eq(4894) & df["SURVEY_YEAR"].eq(1985)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 4897: Bachelor degree 11/83
cond = df["IDENTIFIER"].eq(4897) & df["SURVEY_YEAR"].eq(1983)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 4963: HS degree 05/80
cond = df["IDENTIFIER"].eq(4693) & df["SURVEY_YEAR"].eq(1980)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 12

# ID 4998: Bachelor degree 10/95
cond = df["IDENTIFIER"].eq(4998) & df["SURVEY_YEAR"].eq(1995)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 19

# ID 5010: Bachelor degree 12/84
cond = df["IDENTIFIER"].eq(5010) & df["SURVEY_YEAR"].eq(1984)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 5166: Bachelor degree 12/86
cond = df["IDENTIFIER"].eq(5166) & df["SURVEY_YEAR"].eq(1986)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 5300: Bachelor degree 05/87
cond = df["IDENTIFIER"].eq(5300) & df["SURVEY_YEAR"].ge(1987)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 16

# ID 5410: Bachelor degree 12/85
cond = df["IDENTIFIER"].eq(5410) & df["SURVEY_YEAR"].eq(1985)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 5504: Bachelor degree 12/92
cond = df["IDENTIFIER"].eq(5504) & df["SURVEY_YEAR"].eq(1992)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 11758: Bachelor degree 12/86
cond = df["IDENTIFIER"].eq(11758) & df["SURVEY_YEAR"].eq(1986)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 12002: Community college degree 01/83
cond = df["IDENTIFIER"].eq(12002) & df["SURVEY_YEAR"].eq(1982)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 13

# ID 12044: Bachelor degree 12/86
cond = df["IDENTIFIER"].eq(12044) & df["SURVEY_YEAR"].eq(1986)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# ID 12069: Bachelor degree 12/89
cond = df["IDENTIFIER"].eq(12069) & df["SURVEY_YEAR"].eq(1989)
df.loc[cond, "REAL_HIGHEST_GRADE_COMPLETED"] = 15

# save the dataframe
df.to_pickle(
    PROJECT_DIR / "eckstein-keane-wolpin/material/output/data/interim/original_extended_interim.pkl"
)
