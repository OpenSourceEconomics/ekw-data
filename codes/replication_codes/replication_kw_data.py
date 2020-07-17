"""This script replicates (or at least tries to replicate) the values in Tables 1-4 with the
original dataset of KW97
"""

import numpy as np
import pandas as pd

columns = ['Identifier', 'Age', 'schooling_experience', 'Choice', 'Wage']
dtype = {'Identifier': np.int, 'Age': np.int64, 'schooling_experience': np.int, 'Choice': 'category'}

# We read the original data file.
kw_df = pd.DataFrame(np.genfromtxt('../../sources/raw_kw97_data/KW_97.raw'), columns=columns).astype(dtype)
kw_df['Choice'] = kw_df['Choice'].map({1.0: 'schooling', 2.0: 'home',
                                       3.0: 'white_collar', 4.0: 'blue_collar', 5.0: 'military'})

new_row = {'Identifier': np.nan, 'Age': 15, 'schooling_experience': np.nan,
           'Choice': np.nan, 'Wage': np.nan}
kw_df = kw_df.groupby(kw_df['Identifier']).apply(lambda x: x.append(new_row, ignore_index=True))
kw_df['Identifier'] = kw_df['Identifier'].ffill()
kw_df = kw_df.groupby(kw_df['Identifier']).apply(lambda x: x.sort_values(by=['Age']))


cond_1 = kw_df['Age'].eq(15)
cond_2 = kw_df['schooling_experience'].shift(-1).ge(9)
kw_df.loc[cond_1 & cond_2, 'Choice'] = 'schooling'

cond_2 = kw_df['schooling_experience'].shift(-1).le(8)
kw_df.loc[cond_1 & cond_2, 'Choice'] = 'home'


def get_working_experience(agent):
    """This function generates the work experience in the three occupations that an individual prior to a given year"""

    for occ in ['white_collar', 'blue_collar', 'military']:
        agent[occ + '_experience'] = (agent['Choice'] == occ).astype(int).cumsum().shift(1)
    return agent


kw_df = kw_df.groupby(kw_df['Identifier']).apply(lambda x: get_working_experience(x))


# Replication of Table 1
def replicate_tables_1_to_4(df):
    """This function implements the operations necessary to replicate the values in tables 1-4 from KW97 from the input
    dataframe
    """
    # Table 1, upper part of each row, i. e. total values
    table_1_dict = dict()
    table_1_dict['Total'] = pd.crosstab(index=df['Age'], columns=df['Choice'],
                                        margins=True, margins_name='Total')
    col_order = ['schooling', 'home', 'white_collar', 'blue_collar', 'military', 'Total']
    table_1_dict['Total'] = table_1_dict['Total'][col_order]
    table_1_dict['Total'].name = 'Table_1_total'

    # Table 1, lower part of each row, i. e. proportional values
    table_1_dict['Normalized'] = pd.crosstab(index=df['Age'], columns=df['Choice'],
                                             margins=True, normalize='index').round(3)
    col_order = ['schooling', 'home', 'white_collar', 'blue_collar', 'military']
    table_1_dict['Normalized'] = table_1_dict['Normalized'][col_order] * 100
    table_1_dict['Normalized'].name = 'Table_1_normalized'

    # Replication of Table 2
    df['Choice_t_plus_1'] = df['Choice'].groupby(df['Identifier']).apply(lambda x: x.shift(-1))
    df['Choice_t_minus_1'] = df['Choice'].groupby(df['Identifier']).apply(lambda x: x.shift(1))
    table_2_dict = dict()

    # Table 2, upper part of each row (t-1 -> t)
    table_2_dict['Upper'] = pd.crosstab(index=df['Choice_t_minus_1'], columns=df['Choice'], normalize='index').round(3)
    col_order = ['schooling', 'home', 'white_collar', 'blue_collar', 'military']
    table_2_dict['Upper'] = table_2_dict['Upper'].loc[col_order, col_order] * 100
    table_2_dict['Upper'].name = 'Table_2_upper_rows'

    # Table 2, lower part of each row (t -> t-1)
    table_2_dict['Lower'] = pd.crosstab(index=df['Choice'], columns=df['Choice_t_minus_1'], normalize='index').round(3)
    col_order = ['schooling', 'home', 'white_collar', 'blue_collar', 'military']
    table_2_dict['Lower'] = table_2_dict['Lower'].loc[col_order, col_order] * 100
    table_2_dict['Lower'].name = 'Table_2_lower_rows'

    # Replication of Table 3
    table_3_dict = dict()
    table_3_aux_df_dict = dict()

    for occ in ['schooling', 'blue_collar', 'white_collar', 'military']:
        # upper part of each row
        table_3_dict[occ + '_upper'] = pd.crosstab(index=kw_df[occ + '_experience'], columns=kw_df['Choice'],
                                                   normalize='index').round(3)
        table_3_dict[occ + '_upper'] = pd.DataFrame(table_3_dict[occ + '_upper'][occ] * 100)
        table_3_dict[occ + '_upper'].name = 'Table_3_' + occ + '_upper_row'

        # lower part of each row
        cond = df['Choice_t_minus_1'].eq(occ)
        table_3_aux_df_dict[occ] = df[cond]
        table_3_dict[occ + '_lower'] = pd.crosstab(index=table_3_aux_df_dict[occ][occ + '_experience'],
                                                   columns=table_3_aux_df_dict[occ]['Choice'], normalize='index').round(
                                                   3)
        table_3_dict[occ + '_lower'] = pd.DataFrame(table_3_dict[occ + '_lower'][occ] * 100)
        table_3_dict[occ + '_lower'].name = 'Table_3_' + occ + '_lower_row'

    # Replication of Table 4
    table_4_dict = dict()

    # upper part of each row (mean income)
    table_4_dict['Wages'] = pd.crosstab(df['Age'], df['Choice'], values=df['Wage'], aggfunc=['mean'],
                                        margins=True, margins_name='All Occupations').round(0)
    col_order = [('mean', 'All Occupations'), ('mean', 'white_collar'), ('mean', 'blue_collar'),
                 ('mean', 'military')]
    table_4_dict['Wages'] = table_4_dict['Wages'][col_order]
    table_4_dict['Wages'].name = 'Table_4_mean_income'

    # lower part of each row (number of wage observations)
    # we get first get rid of observations in which the individual chose a working option but the wage is missing
    wage_df = df[~df['Wage'].isna()]

    table_4_dict['Num_of_obs'] = pd.crosstab(wage_df['Age'], wage_df['Choice'], values=wage_df['Wage'],
                                             aggfunc=[len],
                                             margins=True, margins_name='All Occupations')
    col_order = [('len', 'All Occupations'), ('len', 'white_collar'), ('len', 'blue_collar'),
                 ('len', 'military')]
    table_4_dict['Num_of_obs'] = table_4_dict['Num_of_obs'][col_order]
    table_4_dict['Num_of_obs'].name = 'Table_4_number_of_observations'

    all_tables_dict = {**table_1_dict, **table_2_dict, **table_3_dict, **table_4_dict}

    return all_tables_dict


all_tables = replicate_tables_1_to_4(kw_df)

for table_ in all_tables.values():
    table_.to_html('../../output/kw_data_replication_tables/kw_' + table_.name + '.html')
    table_.to_csv('../../output/kw_data_replication_tables/kw_' + table_.name + '.csv')
