import pandas as pd

merge_df = pd.read_pickle('../../output/data/final/merge_kw_structData.pkl')
adjusted_merge_df = pd.read_pickle('../../output/data/final/adjusted_merge_kw_structData.pkl')


def get_birthmonths_early_hs_graduates(df):
    """This function calculates the number of individuals who finished high school (i. e.
    grade 12) at age 17 sorted by month of birth
    """
    cond = df['AGE'].eq(17) & df['schooling_experience'].eq(12)
    df['EARLY_HS_GRAD'] = cond.astype(int)
    months_df = pd.DataFrame(df.groupby(['MONTH_OF_BIRTH']).EARLY_HS_GRAD.sum())

    return months_df


early_grad_months = get_birthmonths_early_hs_graduates(merge_df)
early_grad_months.to_html('../../output/miscallenous/birthmonths_of_early_hs_grads.html')
early_grad_months.to_csv('../../output/miscallenous/birthmonths_of_early_hs_grads.csv')

adj_early_grad_months = get_birthmonths_early_hs_graduates(adjusted_merge_df)
adj_early_grad_months.to_html('../../output/miscallenous/adjusted_birthmonths_of_early_hs_grads.html')
adj_early_grad_months.to_csv('../../output/miscallenous/adjusted_birthmonths_of_early_hs_grads.csv')
