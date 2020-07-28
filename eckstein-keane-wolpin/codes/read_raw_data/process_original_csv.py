import pandas as pd
import shutil

original_ext_df = pd.read_csv('../../sources/original.csv', index_col='R0000100')

shutil.copyfile('../../sources/original.sdf', '../../sources/original_extended.sdf')
file_dict = {}

with open('../../sources/unrevised_educ_vars.sdf', 'r') as file:
    filedata = file.read()
    filedata = filedata.replace('SURVEY YEAR  ', 'SURVEY YEAR (UNREVISED) ')
with open('../../sources/unrevised_educ_vars.sdf', 'w') as file:
    file.write(filedata)

for filename in ['unrevised_educ_vars', 'additional_educ_vars',
                 'labor_force_status_all_weeks', 'health_vars', 'marital_status',
                 'illegal_activity', 'Table_13_covariates']:
    file_dict[filename] = pd.read_csv('../../sources/' + filename + '.csv', index_col='R0000100')
    cols_to_use = file_dict[filename].columns.difference(original_ext_df.columns)
    original_ext_df = original_ext_df.merge(file_dict[filename][cols_to_use],
                                            on='R0000100', how='left')
    original_ext_df = original_ext_df.loc[:, ~original_ext_df.columns.duplicated()]

    with open('../../sources/original_extended.sdf', 'r') as original_ext_description:
        lineset = set(original_ext_description)
    with open('../../sources/original_extended.sdf', 'a') as original_ext_description:
        with open('../../sources/' + filename + '.sdf') as infile:

            for line in infile:
                if line not in lineset:
                    original_ext_description.write(line)

original_ext_df.to_csv('../../sources/original_extended.csv')
