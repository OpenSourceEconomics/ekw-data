#!/usr/bin/env python
# coding: utf-8

# This notebook creates an extended version of 'occ1990_xwalk.xls' where job categories
# (white-collar or blue-collar) are assigned to every occupation code regardless of coding system.


import pandas as pd
import numpy as np

crosswalk = pd.read_excel("../../sources/occ_crosswalks/occ1990_xwalk.xls")
crosswalk = crosswalk.iloc[:, [0, 1, 4, 7, 8]]
crosswalk.columns = ["OCC1990", "DESCRIPTION", "CPS_1970", "CPS_2000_1", "CPS_2000_5"]
# Delete headings in file
crosswalk = crosswalk.loc[~(crosswalk.OCC1990 == "#")]


# Transfer categorizations from CPS1970 codes to their corresponding OCC1990 codes

crosswalk["category_aux"] = np.nan
crosswalk["category_service"] = np.nan

white_occ_codes = [i for i in range(1, 400)] + [801, 802]
blue_occ_codes = [i for i in range(400, 800)] + [i for i in range(821, 985)]
unemployed_codes = [0, 991, 995]

cond = crosswalk["CPS_1970"].isin(white_occ_codes)
crosswalk.loc[cond, "category_aux"] = "white_collar"

cond = crosswalk["CPS_1970"].isin(blue_occ_codes)
crosswalk.loc[cond, "category_aux"] = "blue_collar"

cond = crosswalk["CPS_1970"].isin(unemployed_codes)
crosswalk.loc[cond, "category_aux"] = "unemployed"


service_codes = [i for i in range(900, 985)]
cond = crosswalk["CPS_1970"].isin(service_codes)
crosswalk.loc[cond, "category_service"] = "service"


# For OCC1990 codes which correspond to multiple codes in some coding system
# (i. e. more than 1 row with the same OCC1990 code) assign the category of the first CPS1970 code
# that corresponds to a given OCC1990 code

crosswalk_aux = crosswalk["category_aux"].groupby(crosswalk["OCC1990"]).first()
crosswalk_aux = pd.DataFrame(crosswalk_aux).rename(columns={"category_aux": "CATEGORY"})


crosswalk = crosswalk.merge(crosswalk_aux, on="OCC1990")


# add the extra 1970 occupation code '590' and assign it to the choice 'military'
# (see https://www.nlsinfo.org/sites/nlsinfo.org/files/attachments/121217/
# Attachment%203-1970%20Industry%20and%20Occupational%20Codes.pdf, p. 22)

row = [np.nan, "Current member of armed forces", 590, np.nan, np.nan, "military", "military"]


# As OCC1990 codes sometimes incorporate > 1 CPS1970 codes, it is necessary to check
# whether some OCC1990 codes include both a white-collar and a blue-collar CPS1970 code.
# In this case, the practice of assigning the categorization from the first CPS1970 code
# to the whole corresponding OCC1990 code would need to be revised for such codes.
# As "aux_list" shows, there are indeed 5 such OCC1990 codes which are fixed in the cell below.

aux_dict = dict()

for num in crosswalk["OCC1990"].unique():
    aux_dict[num] = list(crosswalk["category_aux"][crosswalk["OCC1990"] == num])

aux_list = []

for key, value in aux_dict.items():
    if ("white_collar" in aux_dict[key]) and ("blue_collar" in aux_dict[key]):
        aux_list += [key]
    else:
        continue


# OCC1990 = 89
crosswalk.loc[(crosswalk["CPS_1970"] == 924), "CATEGORY"] = "blue_collar"

# OCC1990 = 95
crosswalk.loc[(crosswalk["CPS_1970"] == 923), "CATEGORY"] = "blue_collar"

# OCC1990 = 185
crosswalk.loc[(crosswalk["CPS_1970"] == 425), "CATEGORY"] = "blue_collar"

# OCC1990 = 475
crosswalk.loc[(crosswalk["CPS_1970"] == 802), "CATEGORY"] = "white_collar"

# OCC1990 = 829
crosswalk.loc[(crosswalk["CPS_1970"] == 221), "CATEGORY"] = "white_collar"


# This cell categorizes OCC1990 codes that do not have a corresponding CPS1970 code

extended_white_col = {
    "Legislators": 3,
    "Chief executives and public administrators": 4,
    "Human resources and labor relations managers": 8,
    "Managers of service organizations, n.e.c.": 21,
    "Insurance underwriters": 24,
    "Other financial specialists": 25,
    "Management analysts": 26,
    "Personnel, HR, training, and labor relations specialists": 27,
    "Business and promotion agents": 34,
    "Management support occupations": 37,
    "Medical scientists": 83,
    "Respiratory therapists": 98,
    "Occupational therapists": 99,
    "Physical therapists": 103,
    "Speech therapists": 104,
    "Humanities profs/instructors, college, nec": 150,
    "Special education teachers": 158,
    "Technical writers": 184,
    "Professionals, n.e.c.": 200,
    "Legal assistants, paralegals, legal support, etc": 234,
    "Supervisors and proprietors of sales jobs": 243,
    "Sales workers--allocated (1990 internal census)": 290,
    "Hotel clerks": 317,
    "Information clerks, nec": 323,
    "Correspondence and order clerks": 326,
    "Records clerks": 336,
    "Cost and rate clerks (financial records processing)": 343,
    "Mail clerks, outside of post office": 356,
    "Inspectors, n.e.c.": 361,
    "Eligibility clerks for government programs; social welfare": 377,
    "Supervisors of guards": 415,
    "Supervisors of cleaning and building service": 448,
    "Supervisors of personal service jobs, n.e.c.": 456,
    "Horticultural specialty farmers": 474,
    "Managers of horticultural specialty farms": 476,
    "Supervisors of agricultural occupations": 485,
    "Supervisors of mechanics and repairers": 503,
    "Supervisors of construction work": 558,
    "Supervisors of motor vehicle transportation": 803,
}

extended_blue_col = {
    "Physicians assistants": 106,
    "Protective services, n.e.c.": 427,
    "Misc food prep workers": 444,
    "Pest control occupations": 455,
    "Guides": 461,
    "Marine life cultivation workers": 483,
    "Nursery farming workers": 484,
    "Graders and sorters of agricultural products": 488,
    "Inspectors of agricultural products": 489,
    "Bus, truck, and stationary engine mechanics": 507,
    "Small engine repairers": 509,
    "Industrial machinery repairers": 518,
    "Repairers of electrical equipment, n.e.c.": 533,
    "Locksmiths and safe repairers": 536,
    "Repairers of mechanical controls and valves": 539,
    "Elevator installers and repairers": 543,
    "Sheet metal duct installers": 596,
    "Drillers of oil wells": 614,
    "Other mining occupations": 617,
    "Precision grinders and filers": 644,
    "Other precision woodworkers": 659,
    "Other precision and craft workers": 684,
    "Batch food makers": 688,
    "Adjusters and calibrators": 693,
    "Water and sewage treatment plant operators": 694,
    "Other plant and system operators": 699,
    "Wood lathe, routing, and planing machine operators": 726,
    "Shaping and joining machine operator (woodworking)": 728,
    "Nail and tacking machine operators (woodworking)": 729,
    "Other woodworking machine operators": 733,
    "Textile cutting machine operators": 743,
    "Pressing machine operators (clothing)": 747,
    "Cementing and gluing maching operators": 753,
    "Extruding and forming machine operators": 755,
    "Separating, filtering, and clarifying machine operators": 757,
    "Roasting and baking machine operators (food)": 763,
    "Washing, cleaning, and pickling machine operators": 764,
    "Paper folding machine operators": 765,
    "Water transport infrastructure tenders and crossing guards": 834,
    "Excavating and loading machine operators": 853,
    "Helpers, constructions": 865,
    "Production helpers": 874,
    "Machine feeders and offbearers": 878,
}

extended_military = {"Military": 905}

occ_not_needed = [390, 391, 408, 480, 815, 890, 999]

crosswalk["CATEGORY"][crosswalk["OCC1990"].isin(extended_white_col.values())] = "white_collar"
crosswalk["CATEGORY"][crosswalk["OCC1990"].isin(extended_blue_col.values())] = "blue_collar"
crosswalk["CATEGORY"][crosswalk["OCC1990"].isin(extended_military.values())] = "military"


# check that all occupation codes that are supposed to be categorized, are indeed categorized

print(
    crosswalk[["OCC1990", "DESCRIPTION"]][
        crosswalk["CATEGORY"].isna() & ~crosswalk["OCC1990"].isin(occ_not_needed)
    ]
)


# Check of assigned categories with description manual for CPS_2000_1
# (available here: https://usa.ipums.org/usa/volii/occ2000.shtml)

# Professional divers CPS_2000_1 = 752, currently white collar
crosswalk["CATEGORY"].loc[crosswalk["CPS_2000_1"] == 752] = "blue_collar"
# Fire inspectors CPS_2000_1 = 375, currently blue collar
# First-Line Supervisors/Managers of Food Preparation and Serving Workers CPS_2000_1 = 401,
# currently blue collar => white collar
crosswalk["CATEGORY"].loc[crosswalk["CPS_2000_1"] == 401] = "white_collar"
# First-Line Supervisors/Managers of Personal Service Workers CPS_2000_1 = 432,
# currently blue collar => white collar
crosswalk["CATEGORY"].loc[crosswalk["CPS_2000_1"] == 432] = "white_collar"
# Medical, Dental, and Ophthalmic Laboratory Technicians CPS_2000_1 = 876,
# currently blue collar => white collar (compare e. g. CPS1970 = 080)
crosswalk["CATEGORY"].loc[crosswalk["CPS_2000_1"] == 876] = "white_collar"
# Ship Engineers CPS_2000_1 = 933, currently blue collar => white collar
crosswalk["CATEGORY"].loc[crosswalk["CPS_2000_1"] == 933] = "white_collar"


# => Few changes necessary which strengthens confidence in the initial assignment method

# Create the 2002 and 2003 codes
# (see structDataset\doc\documents\occupation_codes\2000_2002 Industry and Occupational Codes.pdf)
# by adding a trailing 0 to the 2000 codes
crosswalk["CPS_2002"] = crosswalk["CPS_2000_1"].copy() * 10


crosswalk.drop(columns=["category_aux"]).to_pickle(
    "../../output/data/interim/categorized_xwalk.pkl"
)
