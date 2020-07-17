
Correspondence with NLSY Support
================================

We had to contact the NLSY support several times to gain more insights into the
structure of NLSY79. The original files are contained in the `repository`_.

.. _repository: https://github.com/structDataset/documentation/tree/master/documents/correspondence_nlsy

`Question about erroneous county code entries in the Higher Education General Information Survey <https://github.com/OpenSourceEconomics/structDataset/blob/master/doc/documents/correspondence_nlsy/cer_about_erroneous_county_code_entries.pdf>`_
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

* Question: There are instances where two different county names are assigned to the same county code. How should we deal with this?

|

* Answer: These instances might be due to data entry errors. You may need to use other location information (zip code and city name) to determine the correct county.

`Replication of AFQT scores <https://github.com/OpenSourceEconomics/structDataset/blob/master/doc/documents/correspondence_nlsy/nlsy_afqt_score_replication.pdf>`_
-------------------------------------------------------------------------------------------------------------------------------------------------------------------

* Problems:

  1. The percentiles for the AFQT_1 score cannot be properly calculated from the ASVAB scores.

  2. Three testing conditions are unspecified.

* Answers:

  1. The original values for "Numerical Operations" have to be adjusted according `Table A on page 38 <https://github.com/OpenSourceEconomics/structDataset/blob/master/sources/NLSY79%20Attachment%20106%2C%20Profiles%20of%20American%20Youth.pdf>`_.

  2. 

  * Comp-Converted Refusal: Participant was hesitant to take ASVAB but was later convinced by instructor

  * Comp-Spanish Instr. Cards: The test was taken with Spanish instructions

  * Comp-Problem Reported: No explanation

`Questions about coherency of occupational categories <https://github.com/OpenSourceEconomics/structDataset/blob/master/doc/documents/correspondence_nlsy/nlsy_coherent_occupational_categories.pdf>`_
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

* Questions:
  
  1. Over the years, the occupation codes in the NLSY79 have varied. Is there a coherent occupation classification available in the NLSY79 or do you know of classifications from other sources

  2. There are some undocumented codes. Is there any more information about these values?

* Answers:

  1. The different codes have to be mapped into each other (i. e. 1970 codes to 1980 codes, 1980 codes to 1990 codes, etc.). The 4-digit 2002 codes are most likely the 3-digit 2000 codes with an added trailing zero.

     NB: We currently use `this crosswalk <https://github.com/OpenSourceEconomics/structDataset/blob/master/doc/data/external/occ_crosswalks/occ1990_xwalk.xls>`_ to map the codes into each other.
 
  2. No, as the information was collected on pen and paper questionnaires and not saved. However, some verbatim responses could maybe be brought back. Some of the undocumented codes will be/have been corrected in the next/latest public data release.

`Questions regarding occupational and educational data <https://github.com/OpenSourceEconomics/structDataset/blob/master/doc/documents/correspondence_nlsy/nlsy_cps_job_occ_1978_monthly_enrollment.pdf>`_
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

* Questions:

  1. Why are there two sets of employer identifiers (QES_52 and QES_84) for the years 1990-1992?

  2. Why is sometimes more than one CPS job per period and ID specified?

  3. Are the occupational category codes available for 1978?

  4. Often there exist two variables that indicate the enrollment data for a particular month. Which variables do we have to pick?

|

* Answers:

  1. For the years 1990-1992, a second set of questions (e. g. about job promotions and responsibilities) were included in the employer supplement which were also included in the CPS section and QES_84 is used to properly route to these questions. Thus, use QES_52 to identify the employer that matches to the CPS job.
  
  2. This is likely an error.

  3. There are no occupational category codes available for 1978.

  4. No clear answer


`Weekly information on school attendance <https://github.com/OpenSourceEconomics/structDataset/blob/master/doc/documents/correspondence_nlsy/nlsy_weekly_school_attendance.pdf>`_
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

* Question: Is there weekly information on school attendance in the NLSY79 structDataset?

|

* Answer: No, information on school attendance is only available on a monthly basis. In particular, any part of a month attended is counted as an entire month.


