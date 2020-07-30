#!/usr/bin/env python
"""
"""
import os

for file in [
    "xwalk_with_categories",
    "preliminary_data_adjustments",
    "extended_kw97_dataclean",
    "testing",
]:
    os.system("python " + file + ".py")
