import matplotlib.pyplot as plt

import pandas as pd

df = pd.read_pickle('../../output/data/final/original_extended_final.pkl')
cond = df['AGE'].le(47)
df = df[cond]

cond = df['HOME_CHOICE'].eq('out_of_labor_force') & (
        df['AMOUNT_OF_WORK_LIMITED'].shift(-1).eq(1.0) | df['AMOUNT_OF_WORK_LIMITED'].eq(1.0))
df['HEALTH_OLF'] = cond.astype(int)

cond = df['CHOICE'].eq('home')
df['home'] = cond.astype(int)

cond = df['HOME_CHOICE'].eq('out_of_labor_force')
df['olf'] = cond.astype(int)


health_df = pd.DataFrame(((df['HEALTH_OLF'].groupby(df['AGE']).mean() / df['home'].groupby(df['AGE']).
                          mean())*100).round(2))
health_df.rename(columns={0: 'Share among individuals at home'}, inplace=True)
add_health_df = pd.DataFrame(((df['HEALTH_OLF'].groupby(df['AGE']).mean() / df['olf'].groupby(df['AGE']).
                               mean())*100).round(2))
add_health_df.rename(columns={0: 'Share among individuals out of the labor force'}, inplace=True)
health_df = health_df.join(add_health_df)

health_df.to_html('../../output/analysis/health_effects.html')
health_df.to_csv('../../output/analysis/health_effects.csv')
