#!/usr/bin/env python
""" This script construct the panel dataset based on the NLSY sources from the website which are in
the wide format.
"""

import os

for dir_ in ['read_raw_data', 'process_data']:
    os.chdir('codes/' + dir_)
    os.system('python create.py')
    print(dir_ + 'complete')
    os.chdir('../../')
