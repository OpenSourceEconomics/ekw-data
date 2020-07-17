
import pandas as pd

df = pd.read_csv('../../sources/original-0.csv', index_col='R0000100')

for num in range(1, 9):
    aux_df = pd.read_csv('../../sources/original-' + repr(num) + '.csv', index_col='R0000100')
    df = df.append(aux_df)

df.to_csv('../../sources/original.csv', index=True)

print('lol')

df = pd.read_csv('../../sources/labor_force_status_all_weeks-0.csv', index_col='R0000100')

for num in range(1, 17):
    aux_df = pd.read_csv('../../sources/labor_force_status_all_weeks-' + repr(num) + '.csv', index_col='R0000100')
    df = df.append(aux_df)

df.to_csv('../../sources/labor_force_status_all_weeks.csv', index=True)

print('lol')