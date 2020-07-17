import numpy as np
import pandas as pd

import sys
sys.path.insert(0, '../replication_codes')
from replication_kw_data import get_working_experience
from replication_kw_data import replicate_tables_1_to_4

# We read the original KW data file and calculate the work experience for the different occupations
columns = ['Identifier', 'Age', 'schooling_experience', 'Choice', 'Wage']
dtype = {'Identifier': np.int, 'Age': np.int64, 'schooling_experience': np.int, 'Choice': 'category'}

kw_df = pd.DataFrame(np.genfromtxt('../../sources/raw_kw97_data/KW_97.raw'), columns=columns).astype(dtype)
kw_df['Choice'] = kw_df['Choice'].map({1.0: 'schooling', 2.0: 'home',
                                       3.0: 'white_collar', 4.0: 'blue_collar', 5.0: 'military'})
kw_df = kw_df.groupby(kw_df['Identifier']).apply(lambda x: get_working_experience(x))

# We read in our self-constructed data set
sd_df = pd.read_pickle('../../output/data/final/original_extended_final.pkl')
sd_df['Survey Year'] = sd_df['SURVEY_YEAR']

# We merge the two data sets and save them for later usage
merged_df = sd_df.merge(kw_df, left_on=['IDENTIFIER', 'AGE'],
                        right_on=['Identifier', 'Age']).set_index(['IDENTIFIER', 'Survey Year'])
merged_df.to_pickle('../../output/data/final/merge_kw_structData.pkl')

# They are several IDs in the merged data for which an observation in the year 1988 exists. As the last year in the
# original data is 1987, these observations hint at a wrong age assignment in the original data. We construct a list
# with the concerned IDs.
cond = merged_df['SURVEY_YEAR'].eq(1988) & (~merged_df['Choice'].isna())
list_1988 = merged_df.loc[cond, 'Identifier'].unique()

# We count the number of wrongly assigned IDs per birth month and save the results
wrong_year_decomp = pd.DataFrame(merged_df.loc[cond, 'MONTH_OF_BIRTH'].value_counts()
                                 ).rename(columns={'MONTH_OF_BIRTH': 'Number of IDs with wrongly assigned age'})
wrong_year_decomp.to_html('../../output/data_problems/wrong_age_decomposition.html')
wrong_year_decomp.to_csv('../../output/data_problems/wrong_age_decomposition.csv')

# We adjust the original KW data set so that the observations for the wrongly assigned IDs are corrected by shifting
# them and save the resulting data frame
cond = kw_df['Identifier'].isin(list_1988)
kw_df_adjusted = kw_df.copy()
kw_df_adjusted[cond] = kw_df[cond].groupby([kw_df['Identifier']]).apply(lambda x: x.shift(-1))
kw_df_adjusted.to_pickle('../../output/data/final/adjusted_kw_97.pkl')

# We merge the adjusted KW data with our self-constructed data set and save it
adjusted_merged_df = sd_df.merge(kw_df_adjusted, left_on=['IDENTIFIER', 'AGE'],
                                 right_on=['Identifier', 'Age']).set_index(['IDENTIFIER', 'SURVEY_YEAR'])
adjusted_merged_df.to_pickle('../../output/data/final/adjusted_merge_kw_structData.pkl')

# We replicate the Tables 1 - 4 in KW97 with the adjusted KW data and save the results
all_tables_dict = replicate_tables_1_to_4(kw_df_adjusted)

for table_ in all_tables_dict.values():
    table_.to_html('../../output/kw_data_replication_tables/adjusted_data_replication/kw_adjusted_' + table_.name + '.html')
    table_.to_csv('../../output/kw_data_replication_tables/adjusted_data_replication/kw_adjusted_' + table_.name + '.csv')

# A large number of wages are missing in the original data set despite the individual working in the year. We check
# how many of these missing values can be replicated by our decision rules in extended_kw97_dataclean.py. (Note that
# without these decision rules, there would be no missing wage values for working individuals in our self-constructed
# data set.)
missing_wages_dict = dict()

# Number of observations for which the work choice in the original data set (variable 'Choice) and our
# self-constructed data set (variable 'CHOICE') is the same
cond = (merged_df['CHOICE'].eq('white_collar') & merged_df['Choice'].eq('white_collar')) | \
       (merged_df['CHOICE'].eq('blue_collar') & merged_df['Choice'].eq('blue_collar'))
missing_wages_dict['Occupation the same in KW and now'] = sum(cond)

# Number of observations for which the work choices are the same and the wage is non-missing in both the original
# data set (variable 'Wage') and our self-constructed data (variable 'INCOME')
cond = (~merged_df['Wage'].isna() & ~merged_df['INCOME'].isna()) & \
       ((merged_df['CHOICE'].eq('white_collar') & merged_df['Choice'].eq('white_collar')) |
        (merged_df['CHOICE'].eq('blue_collar') & merged_df['Choice'].eq('blue_collar')))
missing_wages_dict['Non-missing wages in KW that are non-missing now'] = sum(cond)

# Number of observations for which the work choices are the same and the wage is missing in the original data but
# non-missing in our data
cond = (merged_df['Wage'].isna() & ~merged_df['INCOME'].isna()) & \
       ((merged_df['CHOICE'].eq('white_collar') & merged_df['Choice'].eq('white_collar')) |
        (merged_df['CHOICE'].eq('blue_collar') & merged_df['Choice'].eq('blue_collar')))
missing_wages_dict['Missing wages in KW that are non-missing now'] = sum(cond)

# Number of observations for which the work choices are the same and the wage is missing in our data but
# non-missing in the original data
cond = (~merged_df['Wage'].isna() & merged_df['INCOME'].isna()) & \
       ((merged_df['CHOICE'].eq('white_collar') & merged_df['Choice'].eq('white_collar')) |
        (merged_df['CHOICE'].eq('blue_collar') & merged_df['Choice'].eq('blue_collar')))
missing_wages_dict['Non-missing wages in KW that are missing now'] = sum(cond)

# Number of observations for which the work choices are the same and the wage is missing in both data sets
cond = (merged_df['Wage'].isna() & merged_df['INCOME'].isna()) & \
       ((merged_df['CHOICE'].eq('white_collar') & merged_df['Choice'].eq('white_collar')) |
        (merged_df['CHOICE'].eq('blue_collar') & merged_df['Choice'].eq('blue_collar')))
missing_wages_dict['Missing wages in KW that are missing now'] = sum(cond)

missing_wages_df = pd.DataFrame.from_dict(missing_wages_dict, orient='index', columns=['Number of occurrences'])
missing_wages_df.to_html('../../output/data_problems/missing_wages_comparison.html')
missing_wages_df.to_csv('../../output/data_problems/missing_wages_comparison.csv')


# A large number of wages are missing in the original data set despite the individual working in the year. We check
# how many of these missing values can be replicated by our decision rules in extended_kw97_dataclean.py. (Note that
# without these decision rules, there would be no missing wage values for working individuals in our self-constructed
# data set.)
missing_wages_dict = dict()

# Number of observations for which the work choice in the original data set (variable 'Choice) and our
# self-constructed data set (variable 'CHOICE') is the same
cond = (merged_df['CHOICE'].eq('military') & merged_df['Choice'].eq('military'))
missing_wages_dict['Occupation the same in KW and now'] = sum(cond)

# Number of observations for which the work choices are the same and the wage is non-missing in both the original
# data set (variable 'Wage') and our self-constructed data (variable 'INCOME')
cond = (~merged_df['Wage'].isna() & ~merged_df['INCOME'].isna()) & \
       (merged_df['CHOICE'].eq('military') & merged_df['Choice'].eq('military'))
missing_wages_dict['Non-missing wages in KW that are non-missing now'] = sum(cond)

# Number of observations for which the work choices are the same and the wage is missing in the original data but
# non-missing in our data
cond = (merged_df['Wage'].isna() & ~merged_df['INCOME'].isna()) & \
       (merged_df['CHOICE'].eq('military') & merged_df['Choice'].eq('military'))
missing_wages_dict['Missing wages in KW that are non-missing now'] = sum(cond)

# Number of observations for which the work choices are the same and the wage is missing in our data but
# non-missing in the original data
cond = (~merged_df['Wage'].isna() & merged_df['INCOME'].isna()) & \
       (merged_df['CHOICE'].eq('military') & merged_df['Choice'].eq('military'))
missing_wages_dict['Non-missing wages in KW that are missing now'] = sum(cond)

# Number of observations for which the work choices are the same and the wage is missing in both data sets
cond = (merged_df['Wage'].isna() & merged_df['INCOME'].isna()) & \
       (merged_df['CHOICE'].eq('military') & merged_df['Choice'].eq('military'))
missing_wages_dict['Missing wages in KW that are missing now'] = sum(cond)

missing_wages_df = pd.DataFrame.from_dict(missing_wages_dict, orient='index', columns=['Number of occurrences'])
missing_wages_df.to_html('../../output/data_problems/military_missing_wages_comparison.html')
missing_wages_df.to_csv('../../output/data_problems/military_missing_wages_comparison.csv')
