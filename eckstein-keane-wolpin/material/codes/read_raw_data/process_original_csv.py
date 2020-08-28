"""This module creates original_extended.csv from original.csv and several other csv-files with
additional covariates.
"""

import os
import shutil
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(os.environ["PROJECT_ROOT"])

original_ext_df = pd.read_csv(
    f"{PROJECT_DIR}/eckstein-keane-wolpin/material/sources/original.csv", index_col="R0000100"
)

# create short description file (sdf) which are is later to create variables
shutil.copyfile(
    f"{PROJECT_DIR}/eckstein-keane-wolpin/material/sources/original.sdf",
    f"{PROJECT_DIR}/eckstein-keane-wolpin/material/sources/original_extended.sdf",
)
file_dict = {}

with open(
    f"{PROJECT_DIR}/eckstein-keane-wolpin/material/sources/unrevised_educ_vars.sdf", "r"
) as file:
    filedata = file.read()
    filedata = filedata.replace("SURVEY YEAR  ", "SURVEY YEAR (UNREVISED) ")
with open(
    f"{PROJECT_DIR}/eckstein-keane-wolpin/material/sources/unrevised_educ_vars.sdf", "w"
) as file:
    file.write(filedata)

# create original_extended.csv by merging other csv-files
for filename in [
    "unrevised_educ_vars",
    "additional_educ_vars",
    "labor_force_status_all_weeks",
    "health_vars",
    "marital_status",
    "illegal_activity",
    "Table_13_covariates",
]:
    file_dict[filename] = pd.read_csv(
        f"{PROJECT_DIR}/eckstein-keane-wolpin/material/sources/{filename}.csv",
        index_col="R0000100",
    )
    cols_to_use = file_dict[filename].columns.difference(original_ext_df.columns)
    original_ext_df = original_ext_df.merge(
        file_dict[filename][cols_to_use], on="R0000100", how="left"
    )
    original_ext_df = original_ext_df.loc[:, ~original_ext_df.columns.duplicated()]

    with open(
        f"{PROJECT_DIR}/eckstein-keane-wolpin/material/sources/original_extended.sdf", "r"
    ) as original_ext_description:
        lineset = set(original_ext_description)
    with open(
        f"{PROJECT_DIR}/eckstein-keane-wolpin/material/sources/original_extended.sdf", "a"
    ) as original_ext_description:
        with open(f"{PROJECT_DIR}/eckstein-keane-wolpin/material/sources/{filename}.sdf") as infile:

            for line in infile:
                if line not in lineset:
                    original_ext_description.write(line)

original_ext_df.to_csv(
    f"{PROJECT_DIR}/eckstein-keane-wolpin/material/sources/original_extended.csv"
)
