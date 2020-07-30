import os
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(os.environ["PROJECT_ROOT"])

df = pd.read_csv(PROJECT_DIR / "eckstein-keane-wolpin/material/sources/original-0.csv",
                 index_col="R0000100")

for num in range(1, 9):
    aux_df = pd.read_csv(
        PROJECT_DIR / "eckstein-keane-wolpin/material/sources/original-" + repr(num) + ".csv",
        index_col="R0000100")
    df = df.append(aux_df)

df.to_csv(PROJECT_DIR / "eckstein-keane-wolpin/material/sources/original.csv", index=True)

df = pd.read_csv(
    PROJECT_DIR / "eckstein-keane-wolpin/material/sources/labor_force_status_all_weeks-0.csv",
    index_col="R0000100")

for num in range(1, 17):
    aux_df = pd.read_csv(
        PROJECT_DIR / "eckstein-keane-wolpin/material/sources/labor_force_status_all_weeks-" + repr(
            num) + ".csv", index_col="R0000100"
    )
    df = df.append(aux_df)

df.to_csv(PROJECT_DIR / "eckstein-keane-wolpin/material/sources/labor_force_status_all_weeks.csv",
          index=True)
