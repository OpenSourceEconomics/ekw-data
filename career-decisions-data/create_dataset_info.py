#!/usr/bin/env python
"""This module prepares the original data for the respy package."""
"""This module contains the auxiliary function for the data transformation."""
import pandas as pd
import numpy as np

DATA_LABELS_EST = []
DATA_LABELS_EST += ['Ident', 'Period', 'Choice', 'Wage', 'Experience_A', 'Experience_B', "Military"]
DATA_LABELS_EST += ['Years_Schooling', 'Lagged_Activity']

DATA_FORMATS_EST = dict()
for key_ in DATA_LABELS_EST:
    DATA_FORMATS_EST[key_] = np.int
    if key_ in ['Wage']:
        DATA_FORMATS_EST[key_] = np.float


def minor_refactoring(df):
    """This function performs some basic refactoring directly from existing variables."""

    df['Period'] = df['Age'] - 16
    df['Choice'].cat.categories = [3, 4, 1, 2, 5]

    return df

# new: change identifier to ident in the columns to remove ambiguity of columns labels and indexes
def prepare_dataset():
    """This function just prepares the original submission in a data frame."""
    columns = ['Ident', 'Age', 'Schooling', 'Choice', 'Wage']
    dtype = {'Ident': np.int, 'Age': np.int, 'Schooling': np.int, 'Choice': 'category'}
    df = pd.DataFrame(np.genfromtxt('./KW_97.raw'), columns=columns).astype(dtype) # new

    df.set_index(['Ident', 'Age'], inplace=True, drop=False)

    # I drop the information on the NLSY identifier and set the identifier to the count.
    for count, idx in enumerate(df.index.levels[0]):
        df.loc[(slice(idx, idx), slice(None)), 'Ident'] = count
    df.set_index(['Ident', 'Age'], inplace=True, drop=False)

    # This mapping is based on direct communication with Kenneth Wolpin.
    df['Period'] = df['Age'] - 16
    df['Choice'].cat.categories = ['Schooling', 'Home', 'White', 'Blue', 'Military'] # new

    return df


# def truncate_military_history(df):
#     """This function truncates in individual's history once assigned to the military."""
#     def _delete_military_service(agent):
#         """This function deletes all observations going forward if an individual enrolls in the
#         military."""
#         for index, row in agent.iterrows():
#             identifier, period = index
#             if row['Choice'] == -99:
#                 return agent.loc[(slice(None, None), slice(None, period - 1)), :]
#         return agent
#
#     df = df.groupby(level='Identifier').apply(_delete_military_service)
#     df.set_index(['Identifier', 'Age'], inplace=True, drop=False)
#
#     return df


def add_state_variables(df):
    """This function adds all additional state variables."""
    def _add_state_variables(agent):
        """This function iterates through an agent record and constructs the state variables for
        each point in tim.
        """
        exp_a, exp_b, military = 0, 0, 0  # new

        # We simply assume that individuals who do not have the expected number of years of
        # education did spend the last year at home.
        if agent.loc[(slice(None), slice(16, 16)), 'Years_Schooling'].values < 10:
            lagged_activity = 0
        else:
            lagged_activity = 1

        for index, row in agent.iterrows():
            identifier, period = index

            agent['Lagged_Activity'].loc[:, period] = lagged_activity
            agent['Experience_A'].loc[:, period] = exp_a
            agent['Experience_B'].loc[:, period] = exp_b
            agent['Military'].loc[:, period] = military

            # Update labor market experience
            # Attention: This is really confusing indexing
            if row['Choice'] == 1:
                exp_a += 1
            elif row['Choice'] == 2:
                exp_b += 1
            elif row["Choice"] == 5:
                military += 1
            else:
                pass

            # Update lagged activity:
            #   (0) Home, (1) Education, (2) Occupation A, and (3) Occupation B (4) Military # new
            lagged_activity = 0

            if row['Choice'] == 1:
                lagged_activity = 2
            elif row['Choice'] == 2:
                lagged_activity = 3
            elif row['Choice'] == 3:
                lagged_activity = 1
            elif row["Choice"] == 5:
                lagged_activity = 5
            else:
                pass

        return agent

    df['Lagged_Activity'] = np.nan
    df['Experience_A'] = np.nan
    df['Experience_B'] = np.nan
    df['Military'] = np.nan

    df = df.groupby(level='Ident').apply(_add_state_variables)

    return df


def write_out(df):
    """This function writes out the relevant information to a simple text file."""
    df = df[DATA_LABELS_EST].astype(DATA_FORMATS_EST)
    with open('career_decisions_data.respy.dat', 'w') as file_:
        df.to_string(file_, index=False, header=True, na_rep='.')

    df.set_index(['Ident', 'Period'], drop=False, inplace=True)
    df.to_pickle('career_decisions_data.respy.pkl')


"""This module contains auxiliary functions to generate tables and figures that
provide information about the observed dataset.
"""

import pandas as pd
import numpy as np

def construct_transition_matrix(base_df):
    """ This method constructs the transition matrix.
    """
    df = base_df.copy(deep=True)
    df['Choice_Next'] = df.groupby(level='Ident')['Choice'].shift(-1)
    args = []
    for label in ['Choice', 'Choice_Next']:
        args += [pd.Categorical(df[label], categories=range(1, 5))]
    tm = pd.crosstab(*args, normalize='index', dropna=False)

    return tm



def get_observed_infos(FNAME):
    """This function provides a host of information on the observed dataset.
    """

    OBS_DATASET = pd.read_pickle(FNAME)

    OBS_DATASET = OBS_DATASET.set_index(['Ident', 'Period'], drop=False)

    PERIODS = OBS_DATASET['Period'].unique().tolist()
    NUM_OBS = [OBS_DATASET['Choice'].loc[:, period].count() for period in PERIODS]

    df = OBS_DATASET
    rslt = dict()
    info = []
    for i, period in enumerate(PERIODS):
        shares = []
        for decision in [1, 2, 3, 4, 5]:    # new
            count = np.sum(df['Choice'].loc[:, period] == decision)
            shares += [count / float(NUM_OBS[i])]

        info += [shares]

    rslt['Choice'] = info
    df.set_index(['Ident', 'Period'], drop=False, inplace=True)
    rslt['Transition_Matrix'] = construct_transition_matrix(df)
    for occupation in ['White', 'Blue']:
        info = []
        for period in PERIODS:
            if occupation == 'White':
                cond = df['Choice'].loc[:, period] == 1
            elif occupation == 'Blue':
                cond = df['Choice'].loc[:, period] == 2
            info += [df['Wage'].loc[:, period][cond].describe().values[
                [0, 1, 2, 4, 5, 6]].tolist()]

        rslt[occupation] = info

    # I also need some information on the distribution of initial schooling.
    rslt['Initial Schooling'] = dict()
    rslt['Initial Schooling']['counts'] = OBS_DATASET[
        'Years_Schooling'].loc[:, 0].value_counts().to_dict()

    # I also need some information on the activities by initial schooling.
    df = OBS_DATASET.groupby(
        'Ident', axis=0).apply(construct_activity_count)

    rslt['Initial Schooling']['activity'] = dict()

    for years in [7, 8, 9, 10, 11]:
        cond = df['Years_Schooling'].loc[:, 0] == years

        stats = []
        for label in ['White', 'Blue', 'School', 'Home', 'Military', 'Total']: ## new
            stats += [df['Count ' + label][:, 0][cond].mean()]

        rslt['Initial Schooling']['activity'][years] = stats

    rslt['num_obs'] = NUM_OBS
    rslt['periods'] = PERIODS

    import pickle as pkl
    pkl.dump(rslt, open('dataset.info.pkl', 'wb'))

    return rslt


def construct_activity_count(agent):
    """Construction of an agent-specific activity count.
    """
    agent['Count White'] = (agent['Choice'] == 1).sum()
    agent['Count Blue'] = (agent['Choice'] == 2).sum()
    agent['Count School'] = (agent['Choice'] == 3).sum()
    agent['Count Home'] = (agent['Choice'] == 4).sum()
    agent['Count Military'] = (agent['Choice'] == 5).sum() ## new
    agent['Count Total'] = len(agent)

    return agent


def format_float(x, digits=2):
    """Pretty formatting for floats
    """
    if pd.isnull(x):
        return '    .'
    else:
        str_ = ('{0:,.' + str(digits) + 'f}')
        return str_.format(float(x))


def format_integer(x):
    """Pretty formatting for integers.
    """
    if pd.isnull(x):
        return '    ---'
    else:
        return '{0:>14,}'.format(int(x))


# Initially a couple of preparations are required to ease further processing.
print("Prepare the dataset")
df = prepare_dataset()

# The respy package works with different integer codes for the choice alternatives and periods
# instead of age.
print("Minor refactoring")
df = minor_refactoring(df)

# The naming convention/basic information is slightly different in the package.
print("Renaming")
df.rename(columns={'Schooling': 'Years_Schooling'}, inplace=True)

# I need to construct some additional state variables.
print("Adding state variables")
df = add_state_variables(df)
print("ADDED STATE VARIABLES")

print("write_out")
write_out(df)
print("WRITTEN_OUT")

get_observed_infos('career_decisions_data.respy.pkl')
