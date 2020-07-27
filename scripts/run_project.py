#!/usr/bin/env python
"""Run project.

This script simply runs all files in the repository to ensure all is working properly throughout.

"""
import subprocess as sp
import glob
import os

PROJECT_ROOT = os.environ["PROJECT_ROOT"]


def run_notebook(notebook):
    cmd = f" jupyter nbconvert --execute {notebook}  --ExecutePreprocessor.timeout=-1"
    sp.check_call(cmd, shell=True)


# We want to make sure all notebooks run.
os.chdir(PROJECT_ROOT)
for dirname in ["career-decisions"]:
    os.chdir(dirname)
    run_notebook("exploration.ipynb")
    os.chdir(PROJECT_ROOT)

# We want to make sure all modules that are used to create input into the notebooks run as well.
os.chdir(PROJECT_ROOT)
for dirname in ["career-decisions"]:
    os.chdir(dirname + "/material")
    for fname in glob.glob("*.py"):
        sp.check_call(["python", fname])
    os.chdir(PROJECT_ROOT)
