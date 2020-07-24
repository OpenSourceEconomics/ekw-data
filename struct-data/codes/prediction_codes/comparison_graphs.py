"""This script generates the graphs in which the predicted values from KW97 for share of
individuals choosing an option and the average yearly incomes per occupation are compared
to the actual values computed from structDataset
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# We read in our data set and restrict it to ages of at most 47
df = pd.read_pickle('../../output/data/final/original_extended_final.pkl')
continuous_df = pd.read_pickle('../../output/data/final/cont_original_extended_final.pkl')
cond = df['AGE'].le(50)
df = df[cond]
cond = continuous_df['AGE'].le(50)
continuous_df = continuous_df[cond]


def wage_comparison(df, cont_df, graph_name, cont_graph_name, table_name, cont_table_name):
    # We compare the actual average income in blue- and white-collar jobs with the predicted income at age 50 (see KW97
    # p. 504)

    wage_predictions = pd.crosstab(df['AGE'], df['CHOICE'], values=df['INCOME'], aggfunc=['mean']).round(0)
    sem_wage_predictions = pd.crosstab(df['AGE'], df['CHOICE'], values=df['INCOME'], aggfunc=['sem']).round(0)

    cont_wage_predictions = pd.crosstab(cont_df['AGE'], cont_df['CHOICE'], values=cont_df['INCOME'], aggfunc=['mean']).round(0)

    fig, ax = plt.subplots(2, 1, figsize=(8, 10))
    plt.tight_layout(pad=6.5)
    fig.subplots_adjust(hspace=0.35)

    for occ, occ_name, color_, pred_val, num_ in [('white_collar', 'White-collar', 'orange', 48497, 0),
                                        ('blue_collar', 'Blue-collar', 'orange', 42222, 1)]:
        ax[num_].set_xticks(np.arange(20, 55, 5))
        ax[num_].set_xlim([25, 51])
        ax[num_].set_ylim([0, 65000])

        ax[num_].plot(wage_predictions['mean'][occ], color=color_, label='Actual yearly income')
        ax[num_].plot(wage_predictions['mean'][occ] + 1.96 * sem_wage_predictions['sem'][occ], color=color_,
                      linestyle=':')
        ax[num_].plot(wage_predictions['mean'][occ] - 1.96 * sem_wage_predictions['sem'][occ], color=color_,
                      linestyle=':')
        ax[num_].axhline(y=pred_val, linestyle='--', label='Predicted income at age 50')

        ax[num_].spines['top'].set_visible(False)
        ax[num_].set_title(occ_name, size=14)
        ax[num_].set_ylabel('Yearly income in 1987 dollars', size=12)
        ax[num_].set_xlabel('Age', size=12)
        ax[num_].legend(loc='lower right')

    plt.savefig('../../output/prediction_graphs/' + graph_name + '.png')

    fig, ax = plt.subplots(2, 1, figsize=(8, 10))
    plt.tight_layout(pad=6.5)
    fig.subplots_adjust(hspace=0.35)

    for occ, occ_name, color_, num_ in [('white_collar', 'White-collar', 'orange', 0),
                                        ('blue_collar', 'Blue-collar', 'orange', 1)]:
        ax[num_].set_xticks(np.arange(20, 55, 5))
        ax[num_].set_xlim([25, 51])
        ax[num_].set_ylim([0, 65000])

        ax[num_].plot(wage_predictions['mean'][occ], color=color_, label='Full sample')
        ax[num_].plot(wage_predictions['mean'][occ] + 1.96 * sem_wage_predictions['sem'][occ], color=color_,
                      linestyle=':')
        ax[num_].plot(wage_predictions['mean'][occ] - 1.96 * sem_wage_predictions['sem'][occ], color=color_,
                      linestyle=':')
        ax[num_].plot(cont_wage_predictions['mean'][occ], label='Continuous sample')

        ax[num_].spines['top'].set_visible(False)
        ax[num_].set_title(occ_name, size=14)
        ax[num_].set_ylabel('Yearly income in 1987 dollars', size=12)
        ax[num_].set_xlabel('Age', size=12)
        ax[num_].legend(loc='lower right')

    plt.savefig('../../output/prediction_graphs/' + cont_graph_name + '.png')

    wage_predictions.to_html('../../output/prediction_data/' + table_name + '.html')
    wage_predictions.to_csv('../../output/prediction_data/' + table_name + '.csv')

    cont_wage_predictions.to_html('../../output/prediction_data/' + cont_table_name + '.html')
    cont_wage_predictions.to_csv('../../output/prediction_data/' + cont_table_name + '.csv')


wage_comparison(df, continuous_df, 'wages_wc_bc', 'cont_wages_wc_bc',
                'struct_data_actual_income', 'cont_struct_data_actual_income')

cond = df['AGE'].le(47)
df = df[cond]
cond = continuous_df['AGE'].le(47)
continuous_df = continuous_df[cond]


def share_comparison(df, graph_name, table_name):
    # We calculate the share of individuals choosing an option in a given year and save the results
    sd_predictions = pd.crosstab(index=df['AGE'], columns=df['CHOICE'], normalize='index').round(3)
    col_order = ['schooling', 'home', 'white_collar', 'blue_collar', 'military']
    sd_predictions = sd_predictions.loc[17:51, col_order] * 100

    sd_predictions.to_html('../../output/prediction_data/' + table_name + '.html')
    sd_predictions.to_csv('../../output/prediction_data/' + table_name + '.csv')

    total_predictions = pd.crosstab(index=df['AGE'], columns=df['CHOICE'])
    col_order = ['schooling', 'home', 'white_collar', 'blue_collar', 'military']
    total_predictions = total_predictions.loc[17:51, col_order]
    total_predictions.to_html('../../output/prediction_data/total_' + table_name + '.html')

    # We plot the share of individuals choosing an option that is predicted by KW against the actual share of
    # individuals choosing this option in our self-constructed data set
    fig, axes = plt.subplots(5, 1, figsize=(17, 39))
    plt.setp(axes, xticks=np.arange(20, 70, 5))
    plt.tight_layout(pad=6.5)
    fig.subplots_adjust(hspace=0.4)

    for choice_, label_, num_ in [('white_collar', 'white-collar', 0), ('blue_collar', 'blue-collar', 1),
                                  ('Schooling', 'in school', 2), ('home', 'at home', 3),
                                  ('military', 'in the military', 4)]:
        kw_predictions = pd.read_csv('../../sources/prediction_graphs/spreadsheets/' + choice_ + '_dp.csv')

        axes[num_].plot(kw_predictions['AGE'], kw_predictions[choice_], linewidth=4.0)
        axes[num_].plot(sd_predictions[choice_.lower()], linewidth=4.0, marker='.', markersize=12)

        axes[num_].spines['top'].set_visible(False)
        axes[num_].set_title('Percentage ' + label_ + ' by age', size=36)
        axes[num_].set_ylabel('Percent', labelpad=15, size=32)
        axes[num_].set_xlabel('Age', labelpad=15, size=32)
        axes[num_].tick_params(labelsize=25)
        axes[num_].legend(('Predicted values', 'Actual values'), prop={'size': 26})
    plt.savefig('../../output/prediction_graphs/' + graph_name + '.png')


share_comparison(df, 'shares_choices', 'choice_predictions')
share_comparison(continuous_df, 'cont_shares_choices', 'cont_choice_predictions')


def bc_wc_comparison(table_name, graph_name):
    sd_predictions = pd.read_csv('../../output/prediction_data/' + table_name + '.csv')
    # We compare the predicted and actual shares of individuals in blue-collar and white-collar jobs separately
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))
    fig.subplots_adjust(hspace=0.35)
    ax1.set_ylim([0, 65])
    ax1.set_xticks(np.arange(20, 55, 5))
    ax1.set_yticks(np.arange(20, 80, 20))

    bc_predictions = pd.read_csv('../../sources/prediction_graphs/spreadsheets/blue_collar_dp.csv')
    cond = bc_predictions['AGE'].le(47)
    bc_predictions = bc_predictions[cond]
    ax1.plot(bc_predictions['AGE'], bc_predictions['blue_collar'])

    wc_predictions = pd.read_csv('../../sources/prediction_graphs/spreadsheets/white_collar_dp.csv')
    cond = wc_predictions['AGE'].le(47)
    wc_predictions = wc_predictions[cond]
    ax1.plot(wc_predictions['AGE'], wc_predictions['white_collar'])

    ax1.spines['top'].set_visible(False)
    ax1.set_title('Predicted share in blue-collar and white-collar jobs by age', size=14)
    ax1.set_ylabel('Percent', size=12)
    ax1.set_xlabel('Age', size=12)
    ax1.legend(('Blue-collar', 'White-collar'), loc='lower right')

    ax2.set_ylim([0, 65])
    ax2.set_xticks(np.arange(20, 55, 5))
    ax2.set_yticks(np.arange(20, 80, 20))

    ax2.plot(sd_predictions['AGE'], sd_predictions['blue_collar'])
    ax2.plot(sd_predictions['AGE'], sd_predictions['white_collar'])

    ax2.spines['top'].set_visible(False)
    ax2.set_title('Actual share in blue-collar and white-collar jobs by age', size=14)
    ax2.set_ylabel('Percent', size=12)
    ax2.set_xlabel('Age', size=12)
    ax2.legend(('Blue-collar', 'White-collar'), loc='lower right')
    plt.savefig('../../output/prediction_graphs/' + graph_name + '.png')


bc_wc_comparison('choice_predictions', 'comparison_bc_wc')
bc_wc_comparison('cont_choice_predictions', 'cont_comparison_bc_wc')


def continuous_comparison(graph_name, table_name):
    # We calculate the share of individuals choosing an option in a given year and save the results
    predictions = pd.read_csv('../../output/prediction_data/' + table_name + '.csv')
    cont_predictions = pd.read_csv('../../output/prediction_data/cont_' + table_name + '.csv')

    fig, axes = plt.subplots(5, 1, figsize=(17, 39))
    plt.setp(axes, xticks=np.arange(20, 70, 5))
    plt.tight_layout(pad=6.5)
    fig.subplots_adjust(hspace=0.4)

    for choice_, label_, num_ in [('white_collar', 'white-collar', 0), ('blue_collar', 'blue-collar', 1),
                                  ('Schooling', 'in school', 2), ('home', 'at home', 3),
                                  ('military', 'in the military', 4)]:
        axes[num_].plot(predictions['AGE'], predictions[choice_.lower()], linewidth=4.0)
        axes[num_].plot(cont_predictions['AGE'], cont_predictions[choice_.lower()], linewidth=4.0, marker='.', markersize=12)

        axes[num_].spines['top'].set_visible(False)
        axes[num_].set_title('Percentage ' + label_ + ' by age', size=36)
        axes[num_].set_ylabel('Percent', labelpad=15, size=32)
        axes[num_].set_xlabel('Age', labelpad=15, size=32)
        axes[num_].tick_params(labelsize=25)
        axes[num_].legend(('Values for the full sample', 'Values for the continuous sample'), prop={'size': 26})
    plt.savefig('../../output/prediction_graphs/' + graph_name + '.png')


continuous_comparison('continuous_comparison_shares', 'choice_predictions')


def continuous_wage_comparison(df, graph_name, table_name):
    full_wages = pd.read_csv('../../output/prediction_data/' + table_name + '.csv')
    # We compare the predicted and actual shares of individuals in blue-collar and white-collar jobs separately
    cont_wages = pd.crosstab(df['AGE'], df['CHOICE'], values=df['INCOME'], aggfunc=['mean']).round(0)
    sem_wage_predictions = pd.crosstab(df['AGE'], df['CHOICE'], values=df['INCOME'], aggfunc=['sem']).round(0)

    fig, ax = plt.subplots(2, 1, figsize=(8, 10))
    plt.tight_layout(pad=6.5)
    fig.subplots_adjust(hspace=0.35)

    for occ, color_, pred_val, num_ in [('white_collar', 'orange', 48497, 0), ('blue_collar', 'orange', 42222, 1)]:
        ax[num_].set_xticks(np.arange(20, 55, 5))
        ax[num_].set_xlim([25, 51])
        ax[num_].set_ylim([0, 65000])

        ax[num_].plot(wage_predictions['mean'][occ], color=color_, label='Actual yearly income')
        ax[num_].plot(wage_predictions['mean'][occ] + 1.96 * sem_wage_predictions['sem'][occ], color=color_,
                      linestyle=':')
        ax[num_].plot(wage_predictions['mean'][occ] - 1.96 * sem_wage_predictions['sem'][occ], color=color_,
                      linestyle=':')
        ax[num_].axhline(y=pred_val, linestyle='--', label='Predicted income at age 50')

        ax[num_].spines['top'].set_visible(False)
        ax[num_].set_title('Actual incomes vs. predicted incomes at age 50', size=14)
        ax[num_].set_ylabel('Yearly income in 1987 dollars', size=12)
        ax[num_].set_xlabel('Age', size=12)
        ax[num_].legend(loc='lower right')

    plt.savefig('../../output/prediction_graphs/' + graph_name + '.png')

    wage_predictions.to_html('../../output/prediction_data/' + table_name + '.html')
    wage_predictions.to_csv('../../output/prediction_data/' + table_name + '.csv')