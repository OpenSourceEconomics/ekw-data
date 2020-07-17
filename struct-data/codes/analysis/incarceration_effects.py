"""This script generates the graph which compares the shares of individuals staying at home
among those who were sent to a correctional institution until 1980 and those who were not
"""

import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_pickle('../../output/data/final/original_extended_final.pkl')

# restrict sample to age 47
cond = df['AGE'].le(47)
df = df[cond]

# create variable for individuals who stay at home and were sent to correctional institution until 1980
cond = df['CHOICE'].eq('home') & df['CORRECTIONAL INSTITUTION_1980'].eq(1)
df['JAILED'] = cond.astype(int)

# create variable for individuals who stay at home and were not sent to correctional institution until 1980
cond = df['CHOICE'].eq('home') & df['CORRECTIONAL INSTITUTION_1980'].lt(1)
df['NOT_JAILED'] = cond.astype(int)

# create plot which compares the share of jailed and unjailed individuals staying at home in a given year
fig, ax = plt.subplots()
ax.plot((df['JAILED'].groupby(df['AGE']).mean() / df['CORRECTIONAL INSTITUTION_1980'].eq(1).mean())*100)
ax.plot((df['NOT_JAILED'].groupby(df['AGE']).mean() / df['CORRECTIONAL INSTITUTION_1980'].lt(1).mean())*100)

ax.spines['top'].set_visible(False)
ax.set_ylabel('Percent staying at home', size=12)
ax.set_xlabel('Age', size=12)
ax.legend(('Sent to correctional institution until 1980', 'Not sent to correctional institution until 1980'))
plt.savefig('../../output/analysis/incarceration_effects.png')

# obtain number of individuals in our sample who were set to correctional institution until 1980
cond = df['SURVEY_YEAR'].eq(1980) & df['CORRECTIONAL INSTITUTION_1980'].eq(1)
print(sum(cond))