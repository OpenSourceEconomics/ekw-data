"""This script tries to replicate the values in Tables 1-4 from the data in structDataset
"""

import numpy as np
import pandas as pd

df = pd.read_pickle('../../output/data/final/original_extended_final.pkl')

cond = df['AGE'].ge(15) & df['SURVEY_YEAR'].le(1987)
df = df[cond]


def get_schooling_experience(agent):
    agent['BASELINE_SCHOOLING'] = agent.loc[agent['AGE'] == 15, 'REAL_HIGHEST_GRADE_COMPLETED']
    agent['BASELINE_SCHOOLING'].ffill(inplace=True)

    agent['ADDITIONAL_SCHOOLING'] = (agent['CHOICE'] == 'schooling').astype(int).cumsum().shift(1)

    agent['schooling_experience'] = agent['BASELINE_SCHOOLING'] + agent['ADDITIONAL_SCHOOLING']
    agent.loc[agent['AGE'] == 15, 'schooling_experience'] = agent.loc[agent['AGE'] == 15, 'BASELINE_SCHOOLING']
    #agent.drop(columns=['BASELINE_SCHOOLING', 'ADDITIONAL_SCHOOLING'])

    return agent


df = df.groupby(df['IDENTIFIER']).apply(lambda x: get_schooling_experience(x))
print(df.loc[df['IDENTIFIER'].eq(6), ['CHOICE', 'schooling_experience', 'BASELINE_SCHOOLING', 'ADDITIONAL_SCHOOLING']])

def get_work_experience(agent):
    for occ in ['white_collar', 'blue_collar', 'military']:
        agent[occ + '_experience'] = (agent['CHOICE'] == occ).astype(int).cumsum().shift(1)

    agent['work_experience'] = sum([agent[occ + '_experience'] for occ in ['white_collar', 'blue_collar', 'military']])

    return agent


df = df.groupby(df['IDENTIFIER']).apply(lambda x: get_schooling_experience(x))
df = df.groupby(df['IDENTIFIER']).apply(lambda x: get_work_experience(x))

table_1_dict = dict()
table_1_dict['Total'] = pd.crosstab(index=df['AGE'], columns=df['CHOICE'],
                                    margins=True, margins_name='Total')
col_order = ['schooling', 'home', 'white_collar', 'blue_collar', 'military', 'Total']
table_1_dict['Total'] = table_1_dict['Total'][col_order]
table_1_dict['Total'].name = 'Table_1_total'

table_1_dict['Normalized'] = pd.crosstab(index=df['AGE'], columns=df['CHOICE'],
                                         margins=True, normalize='index').round(3)
col_order = ['schooling', 'home', 'white_collar', 'blue_collar', 'military']
table_1_dict['Normalized'] = table_1_dict['Normalized'][col_order] * 100
table_1_dict['Normalized'].name = 'Table_1_normalized'

# Replication of Table 2
df['Choice_t_plus_1'] = df['CHOICE'].groupby(df['IDENTIFIER']).apply(lambda x: x.shift(-1))
df['Choice_t_minus_1'] = df['CHOICE'].groupby(df['IDENTIFIER']).apply(lambda x: x.shift(1))
table_2_dict = dict()

table_2_dict['Upper'] = pd.crosstab(index=df['Choice_t_minus_1'], columns=df['CHOICE'], normalize='index').round(3)
col_order = ['schooling', 'home', 'white_collar', 'blue_collar', 'military']
table_2_dict['Upper'] = table_2_dict['Upper'].loc[col_order, col_order] * 100
table_2_dict['Upper'].name = 'Table_2_upper_rows'

table_2_dict['Lower'] = pd.crosstab(index=df['CHOICE'], columns=df['Choice_t_minus_1'], normalize='index').round(3)
col_order = ['schooling', 'home', 'white_collar', 'blue_collar', 'military']
table_2_dict['Lower'] = table_2_dict['Lower'].loc[col_order, col_order] * 100
table_2_dict['Lower'].name = 'Table_2_lower_rows'
print(df.loc[df['AGE'].eq(15), 'CHOICE'].value_counts())
print(sum(df.loc[df['AGE'].eq(15), 'CHOICE'].isna()))
print(sum(df.loc[df['AGE'].eq(15), 'REAL_HIGHEST_GRADE_COMPLETED'].isna()))


df = df[df['AGE'].ge(16)]
# Replication of Table 3
table_3_dict = dict()
table_3_aux_df_dict = dict()

for occ in ['schooling', 'blue_collar', 'white_collar', 'military']:
    table_3_dict[occ + '_upper'] = pd.crosstab(index=df[occ + '_experience'], columns=df['CHOICE'],
                                               normalize='index').round(3)
    table_3_dict[occ + '_upper'] = pd.DataFrame(table_3_dict[occ + '_upper'][occ] * 100)
    table_3_dict[occ + '_upper'].name = 'Table_3_' + occ + '_upper_row'

    cond = df['Choice_t_minus_1'].eq(occ)
    table_3_aux_df_dict[occ] = df[cond]
    table_3_dict[occ + '_lower'] = pd.crosstab(index=table_3_aux_df_dict[occ][occ + '_experience'],
                                               columns=table_3_aux_df_dict[occ]['CHOICE'], normalize='index').round(3)
    table_3_dict[occ + '_lower'] = pd.DataFrame(table_3_dict[occ + '_lower'][occ] * 100)
    table_3_dict[occ + '_lower'].name = 'Table_3_' + occ + '_lower_row'

# Replication of Table 4
table_4_dict = dict()
table_4_dict['Wages'] = pd.crosstab(df['AGE'], df['CHOICE'], values=df['INCOME'], aggfunc=['mean'],
                                    margins=True, margins_name='All Occupations').round(0)
col_order = [('mean', 'All Occupations'), ('mean', 'white_collar'), ('mean', 'blue_collar'),
             ('mean', 'military')]
table_4_dict['Wages'] = table_4_dict['Wages'][col_order]
table_4_dict['Wages'].name = 'Table_4_mean_income'

wage_df = df[~df['INCOME'].isna()]
table_4_dict['Num_of_obs'] = pd.crosstab(wage_df['AGE'], wage_df['CHOICE'], values=wage_df['INCOME'],
                                         aggfunc=[len],
                                         margins=True, margins_name='All Occupations')
col_order = [('len', 'All Occupations'), ('len', 'white_collar'), ('len', 'blue_collar'),
             ('len', 'military')]
table_4_dict['Num_of_obs'] = table_4_dict['Num_of_obs'][col_order]
table_4_dict['Num_of_obs'].name = 'Table_4_number_of_observations'

all_tables_dict = {**table_1_dict, **table_2_dict, **table_3_dict, **table_4_dict}

for table_ in all_tables_dict.values():
    table_.to_html('../../output/struct_dataset_replication_tables/sd_' + table_.name + '.html')
    table_.to_csv('../../output/struct_dataset_replication_tables/sd_' + table_.name + '.csv')
