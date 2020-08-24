""" This module creates the original.csv and labor_force_status_all_weeks.csv which are too large
to directly store them in our Github repo.
"""

import os
from glob import glob
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(os.environ["PROJECT_ROOT"])

# create original.csv
original_list = sorted(
    glob(f"{PROJECT_DIR}/eckstein-keane-wolpin/material/sources/original-*"),
    key=lambda x: int(x.partition("-")[2].partition(".")[0]),
)
df = pd.concat((pd.read_csv(file) for file in original_list))
df.to_csv(f"{PROJECT_DIR}/eckstein-keane-wolpin/material/sources/original.csv", index=True)

# create labor_force_status_all_weeks.csv
labor_list = sorted(
    glob(f"{PROJECT_DIR}/eckstein-keane-wolpin/material/sources/labor_force_status_all_weeks-*"),
    key=lambda x: int(x.partition("-")[2].partition(".")[0]),
)
df = pd.concat((pd.read_csv(file) for file in labor_list))
df.to_csv(
    f"{PROJECT_DIR}/eckstein-keane-wolpin/material/sources/labor_force_status_all_weeks.csv",
    index=True,
)
