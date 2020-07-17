
import pandas as pd

df = pd.read_pickle('../../output/data/final/original_extended_final.pkl')


home_choice_table = pd.DataFrame(pd.crosstab(index=df['AGE'], columns=df['HOME_CHOICE'], normalize='index')).round(3)
home_choice_table = home_choice_table[16:47]*100
home_choice_table.rename(columns={'residual': 'Residual', 'unemployed': 'Unemployment',
                                  'part_time_work': 'Part-time work', 'out_of_labor_force': 'Out-of-labor force',
                                  'failed_schooling': 'Failed schooling'}, inplace=True)
home_choice_table.drop(columns=['not_working'], inplace=True)

columns = ['Out-of-labor force', 'Unemployment', 'Part-time work', 'Failed schooling', 'Residual']
home_choice_table = home_choice_table[columns]

home_choice_table.to_html('../../output/analysis/home_decomposition.html')
home_choice_table.to_csv('../../output/analysis/home_decomposition.csv')
