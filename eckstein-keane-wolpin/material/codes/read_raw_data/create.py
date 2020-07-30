#!/usr/bin/env python
""" This script constructs the panel dataset based on the NLSY sources from the website which are in
the wide format.
"""
import os
from pathlib import Path

import create_large_files  # noqa: F401
import process_original_csv  # noqa: F401
from clsSource import SourceCls

PROJECT_DIR = Path(os.environ["PROJECT_ROOT"])

if __name__ == "__main__":
    fname = PROJECT_DIR/"eckstein-keane-wolpin/material/output/data/raw/original_extended.pkl"

    source_obj = SourceCls()

    source_obj.read_source()
    source_obj.transform_wide_to_panel()
    source_obj.add_basic_variables()
    source_obj.store(fname)

    source_obj.load(fname)
    source_obj.testing()
