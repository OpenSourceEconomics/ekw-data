file handle pcdat/name='afqt.dat' /lrecl=85.
data list file pcdat free /
  A0002600 (F3)
  R0000100 (F5)
  R0000300 (F2)
  R0000500 (F2)
  R0173600 (F2)
  R0214700 (F2)
  R0214800 (F2)
  R0216700 (F2)
  R0216701 (F2)
  R0406400 (F2)
  R0406401 (F2)
  R0410100 (F2)
  R0410300 (F2)
  R0614800 (F2)
  R0615100 (F2)
  R0615200 (F2)
  R0615300 (F2)
  R0615400 (F2)
  R0618200 (F2)
  R0618300 (F2)
  R0618301 (F6)
  R0618900 (F2)
  R0618901 (F2)
  R4397702 (F2)
  R5057802 (F2)
.
* The following code works with current versions of SPSS.
missing values all (-5 thru -1).
* older versions of SPSS may require this:
* recode all (-5,-3,-2,-1=-4).
* missing values all (-4).
variable labels
  A0002600  "VERSION_R26_1 2014"
  R0000100  "ID# (1-12686) 79"
  R0000300  "DATE OF BIRTH - MONTH 79"
  R0000500  "DATE OF BIRTH - YR 79"
  R0173600  "SAMPLE ID  79 INT"
  R0214700  "RACL/ETHNIC COHORT /SCRNR 79"
  R0214800  "SEX OF R 79"
  R0216700  "HGC AS OF 05/01/79 SRVY YR"
  R0216701  "HIGHEST GRADE COMPLTD (REV) 79"
  R0406400  "HGC AS OF 05/01/80 SRVY YR"
  R0406401  "HIGHEST GRADE COMPLTD (REV) 80"
  R0410100  "DATE OF BIRTH - MONTH 81"
  R0410300  "DATE OF BIRTH - YR 81"
  R0614800  "PROFILES ASVAB NORMAL/ALTERED TEST 81"
  R0615100  "PROFILES ASVAB SEC 2-ARITHMETIC 81"
  R0615200  "PROFILES ASVAB SEC 3-WORD KNLDG 81"
  R0615300  "PROFILES ASVAB SEC 4-PARAGRAPH COMP 81"
  R0615400  "PROFILES ASVAB SEC 5-NUMERIC OPERS 81"
  R0618200  "PROFILES AFQT PRCTILE SCORE-80 81"
  R0618300  "PROFILES AFQT PRCTILE 89 (REV) 81"
  R0618301  "PROFILES AFQT PRCTILE 2006 (REV) 81"
  R0618900  "HGC AS OF 05/01/81 SRVY YR"
  R0618901  "HIGHEST GRADE COMPLTD (REV) 81"
  R4397702  "SPECL CHAR THAT COULD AFFECT ANS: MNT HC"
  R5057802  "SPECL CHAR THAT COULD AFFECT ANS: MNT HC"
.

* Recode continuous values. 
* recode 
 A0002600 
    (1 thru 999 eq 1)
    (1000 thru 1999 eq 1000)
    (2000 thru 2999 eq 2000)
    (3000 thru 3999 eq 3000)
    (4000 thru 4999 eq 4000)
    (5000 thru 5999 eq 5000)
    (6000 thru 6999 eq 6000)
    (7000 thru 7999 eq 7000)
    (8000 thru 8999 eq 8000)
    (9000 thru 9999 eq 9000)
    (10000 thru 10999 eq 10000)
    (11000 thru 11999 eq 11000)
    (12000 thru 12999 eq 12000)
    / 
 R0000300 
    (0 thru 0 eq 0)
    (1 thru 1 eq 1)
    (2 thru 2 eq 2)
    (3 thru 3 eq 3)
    (4 thru 4 eq 4)
    (5 thru 5 eq 5)
    (6 thru 6 eq 6)
    (7 thru 7 eq 7)
    (8 thru 8 eq 8)
    (9 thru 9 eq 9)
    (10 thru 10 eq 10)
    (11 thru 11 eq 11)
    (12 thru 12 eq 12)
    (13 thru 13 eq 13)
    (14 thru 14 eq 14)
    (15 thru 15 eq 15)
    (16 thru 16 eq 16)
    (17 thru 99999 eq 17)
    / 
 R0000500 
    (0 thru 56 eq 0)
    (57 thru 57 eq 57)
    (58 thru 58 eq 58)
    (59 thru 59 eq 59)
    (60 thru 60 eq 60)
    (61 thru 61 eq 61)
    (62 thru 62 eq 62)
    (63 thru 63 eq 63)
    (64 thru 64 eq 64)
    (65 thru 65 eq 65)
    (66 thru 66 eq 66)
    (67 thru 67 eq 67)
    (68 thru 68 eq 68)
    (69 thru 69 eq 69)
    (70 thru 70 eq 70)
    (71 thru 71 eq 71)
    (72 thru 72 eq 72)
    (73 thru 99999 eq 73)
    / 
 R0410100 
    (0 thru 0 eq 0)
    (1 thru 1 eq 1)
    (2 thru 2 eq 2)
    (3 thru 3 eq 3)
    (4 thru 4 eq 4)
    (5 thru 5 eq 5)
    (6 thru 6 eq 6)
    (7 thru 7 eq 7)
    (8 thru 8 eq 8)
    (9 thru 9 eq 9)
    (10 thru 10 eq 10)
    (11 thru 11 eq 11)
    (12 thru 12 eq 12)
    (13 thru 13 eq 13)
    (14 thru 14 eq 14)
    (15 thru 15 eq 15)
    (16 thru 16 eq 16)
    (17 thru 99999 eq 17)
    / 
 R0410300 
    (0 thru 54 eq 0)
    (55 thru 55 eq 55)
    (56 thru 56 eq 56)
    (57 thru 57 eq 57)
    (58 thru 58 eq 58)
    (59 thru 59 eq 59)
    (60 thru 60 eq 60)
    (61 thru 61 eq 61)
    (62 thru 62 eq 62)
    (63 thru 63 eq 63)
    (64 thru 64 eq 64)
    (65 thru 65 eq 65)
    (66 thru 66 eq 66)
    (67 thru 67 eq 67)
    (68 thru 68 eq 68)
    (69 thru 69 eq 69)
    (70 thru 70 eq 70)
    (71 thru 99999 eq 71)
    / 
 R5057802 
    (1 thru 3 eq 1)
    (0 thru 0 eq 0)
.

* value labels
 A0002600
    1 "1 TO 999"
    1000 "1000 TO 1999"
    2000 "2000 TO 2999"
    3000 "3000 TO 3999"
    4000 "4000 TO 4999"
    5000 "5000 TO 5999"
    6000 "6000 TO 6999"
    7000 "7000 TO 7999"
    8000 "8000 TO 8999"
    9000 "9000 TO 9999"
    10000 "10000 TO 10999"
    11000 "11000 TO 11999"
    12000 "12000 TO 12999"
    /
 R0000300
    0 "0: < 1"
    1 "1"
    2 "2"
    3 "3"
    4 "4"
    5 "5"
    6 "6"
    7 "7"
    8 "8"
    9 "9"
    10 "10"
    11 "11"
    12 "12"
    13 "13"
    14 "14"
    15 "15"
    16 "16"
    17 "17 TO 99999: 17+"
    /
 R0000500
    0 "0 TO 56: < 57"
    57 "57"
    58 "58"
    59 "59"
    60 "60"
    61 "61"
    62 "62"
    63 "63"
    64 "64"
    65 "65"
    66 "66"
    67 "67"
    68 "68"
    69 "69"
    70 "70"
    71 "71"
    72 "72"
    73 "73 TO 99999: 73+"
    /
 R0173600
    1 "CROSS MALE WHITE"
    2 "CROSS MALE WH. POOR"
    3 "CROSS MALE BLACK"
    4 "CROSS MALE HISPANIC"
    5 "CROSS FEMALE WHITE"
    6 "CROSS FEMALE WH POOR"
    7 "CROSS FEMALE BLACK"
    8 "CROSS FEMALE HISPANIC"
    9 "SUP MALE WH POOR"
    10 "SUP MALE BLACK"
    11 "SUP MALE HISPANIC"
    12 "SUP FEM WH POOR"
    13 "SUP FEMALE BLACK"
    14 "SUP FEMALE HISPANIC"
    15 "MIL MALE WHITE"
    16 "MIL MALE BLACK"
    17 "MIL MALE HISPANIC"
    18 "MIL FEMALE WHITE"
    19 "MIL FEMALE BLACK"
    20 "MIL FEMALE HISPANIC"
    /
 R0214700
    1 "HISPANIC"
    2 "BLACK"
    3 "NON-BLACK, NON-HISPANIC"
    /
 R0214800
    1 "MALE"
    2 "FEMALE"
    /
 R0216700
    0 "NONE"
    1 "1ST GRADE"
    2 "2ND GRADE"
    3 "3RD GRADE"
    4 "4TH GRADE"
    5 "5TH GRADE"
    6 "6TH GRADE"
    7 "7TH GRADE"
    8 "8TH GRADE"
    9 "9TH GRADE"
    10 "10TH GRADE"
    11 "11TH GRADE"
    12 "12TH GRADE"
    13 "1ST YR COL"
    14 "2ND YR COL"
    15 "3RD YR COL"
    16 "4TH YR COL"
    17 "5TH YR COL"
    18 "6TH YR COL"
    19 "7TH YR COL"
    20 "8TH YR COL OR MORE"
    95 "UNGRADED"
    /
 R0216701
    0 "NONE"
    1 "1ST GRADE"
    2 "2ND GRADE"
    3 "3RD GRADE"
    4 "4TH GRADE"
    5 "5TH GRADE"
    6 "6TH GRADE"
    7 "7TH GRADE"
    8 "8TH GRADE"
    9 "9TH GRADE"
    10 "10TH GRADE"
    11 "11TH GRADE"
    12 "12TH GRADE"
    13 "1ST YR COL"
    14 "2ND YR COL"
    15 "3RD YR COL"
    16 "4TH YR COL"
    17 "5TH YR COL"
    18 "6TH YR COL"
    19 "7TH YR COL"
    20 "8TH YR COL OR MORE"
    95 "UNGRADED"
    /
 R0406400
    0 "NONE"
    1 "1ST GRADE"
    2 "2ND GRADE"
    3 "3RD GRADE"
    4 "4TH GRADE"
    5 "5TH GRADE"
    6 "6TH GRADE"
    7 "7TH GRADE"
    8 "8TH GRADE"
    9 "9TH GRADE"
    10 "10TH GRADE"
    11 "11TH GRADE"
    12 "12TH GRADE"
    13 "1ST YR COL"
    14 "2ND YR COL"
    15 "3RD YR COL"
    16 "4TH YR COL"
    17 "5TH YR COL"
    18 "6TH YR COL"
    19 "7TH YR COL"
    20 "8TH YR COL OR MORE"
    95 "UNGRADED"
    /
 R0406401
    0 "NONE"
    1 "1ST GRADE"
    2 "2ND GRADE"
    3 "3RD GRADE"
    4 "4TH GRADE"
    5 "5TH GRADE"
    6 "6TH GRADE"
    7 "7TH GRADE"
    8 "8TH GRADE"
    9 "9TH GRADE"
    10 "10TH GRADE"
    11 "11TH GRADE"
    12 "12TH GRADE"
    13 "1ST YR COL"
    14 "2ND YR COL"
    15 "3RD YR COL"
    16 "4TH YR COL"
    17 "5TH YR COL"
    18 "6TH YR COL"
    19 "7TH YR COL"
    20 "8TH YR COL OR MORE"
    95 "UNGRADED"
    /
 R0410100
    0 "0: < 1"
    1 "1"
    2 "2"
    3 "3"
    4 "4"
    5 "5"
    6 "6"
    7 "7"
    8 "8"
    9 "9"
    10 "10"
    11 "11"
    12 "12"
    13 "13"
    14 "14"
    15 "15"
    16 "16"
    17 "17 TO 99999: 17+"
    /
 R0410300
    0 "0 TO 54: < 55"
    55 "55"
    56 "56"
    57 "57"
    58 "58"
    59 "59"
    60 "60"
    61 "61"
    62 "62"
    63 "63"
    64 "64"
    65 "65"
    66 "66"
    67 "67"
    68 "68"
    69 "69"
    70 "70"
    71 "71 TO 99999: 71+"
    /
 R0614800
    51 "COMPLETED"
    52 "COMP-CONVERTED REFUSAL"
    53 "COMP-PROBLEM REPORTED"
    54 "COMP-SPANISH INSTR. CARDS"
    67 "COMP-PRODECURES ALTERED"
    /
 R0618900
    0 "NONE"
    1 "1ST GRADE"
    2 "2ND GRADE"
    3 "3RD GRADE"
    4 "4TH GRADE"
    5 "5TH GRADE"
    6 "6TH GRADE"
    7 "7TH GRADE"
    8 "8TH GRADE"
    9 "9TH GRADE"
    10 "10TH GRADE"
    11 "11TH GRADE"
    12 "12TH GRADE"
    13 "1ST YR COL"
    14 "2ND YR COL"
    15 "3RD YR COL"
    16 "4TH YR COL"
    17 "5TH YR COL"
    18 "6TH YR COL"
    19 "7TH YR COL"
    20 "8TH YR COL OR MORE"
    95 "UNGRADED"
    /
 R0618901
    0 "NONE"
    1 "1ST GRADE"
    2 "2ND GRADE"
    3 "3RD GRADE"
    4 "4TH GRADE"
    5 "5TH GRADE"
    6 "6TH GRADE"
    7 "7TH GRADE"
    8 "8TH GRADE"
    9 "9TH GRADE"
    10 "10TH GRADE"
    11 "11TH GRADE"
    12 "12TH GRADE"
    13 "1ST YR COL"
    14 "2ND YR COL"
    15 "3RD YR COL"
    16 "4TH YR COL"
    17 "5TH YR COL"
    18 "6TH YR COL"
    19 "7TH YR COL"
    20 "8TH YR COL OR MORE"
    95 "UNGRADED"
    /
 R4397702
    0 "DOES NOT APPLY"
    1 "RESPONDENT DEAF"
    2 "RESPONDENT BLIND"
    3 "RESPONDENT MENTALLY HANDICAPPED OR RETARDED"
    4 "RESPONDENT'S ENGLISH IS VERY POOR"
    5 "RESPONDENT CANNOT READ"
    6 "RESPONDENT PHYSICALLY HANDICAPPED"
    7 "OTHER"
    /
 R5057802
    1 "Respondent mentally handicapped or retarded"
    0 "NOT SELECTED"
    /
.
/* Crosswalk for Reference number & Question name
 * Uncomment and edit this RENAME VARIABLES statement to rename variables for ease of use.
 * This command does not guarantee uniqueness
 */  /* *start* */

* RENAME VARIABLES
  (A0002600 = VERSION_R26_2014) 
  (R0000100 = CASEID_1979) 
  (R0000300 = Q1_3_A_M_1979)   /* Q1-3_A~M */
  (R0000500 = Q1_3_A_Y_1979)   /* Q1-3_A~Y */
  (R0173600 = SAMPLE_ID_1979) 
  (R0214700 = SAMPLE_RACE_78SCRN) 
  (R0214800 = SAMPLE_SEX_1979) 
  (R0216700 = HGC_1979) 
  (R0216701 = HGCREV79_1979) 
  (R0406400 = HGC_1980) 
  (R0406401 = HGCREV80_1980) 
  (R0410100 = Q1_3_A_M_1981)   /* Q1-3_A~M */
  (R0410300 = Q1_3_A_Y_1981)   /* Q1-3_A~Y */
  (R0614800 = ASVAB_1_1981)   /* ASVAB-1 */
  (R0615100 = ASVAB_4_1981)   /* ASVAB-4 */
  (R0615200 = ASVAB_5_1981)   /* ASVAB-5 */
  (R0615300 = ASVAB_6_1981)   /* ASVAB-6 */
  (R0615400 = ASVAB_7_1981)   /* ASVAB-7 */
  (R0618200 = AFQT_1_1981)   /* AFQT-1 */
  (R0618300 = AFQT_2_1981)   /* AFQT-2 */
  (R0618301 = AFQT_3_1981)   /* AFQT-3 */
  (R0618900 = HGC_1981) 
  (R0618901 = HGCREV81_1981) 
  (R4397702 = Q15_9A_000003_1993)   /* Q15-9A~000003 */
  (R5057802 = Q15_9A_000003_1994)   /* Q15-9A~000003 */
.
  /* *end* */

descriptives all.

*--- Tabulations using reference number variables.
*freq var=A0002600, 
  R0000100, 
  R0000300, 
  R0000500, 
  R0173600, 
  R0214700, 
  R0214800, 
  R0216700, 
  R0216701, 
  R0406400, 
  R0406401, 
  R0410100, 
  R0410300, 
  R0614800, 
  R0615100, 
  R0615200, 
  R0615300, 
  R0615400, 
  R0618200, 
  R0618300, 
  R0618301, 
  R0618900, 
  R0618901, 
  R4397702, 
  R5057802.

*--- Tabulations using qname variables.
*freq var=VERSION_R26_2014, 
  CASEID_1979, 
  Q1_3_A_M_1979, 
  Q1_3_A_Y_1979, 
  SAMPLE_ID_1979, 
  SAMPLE_RACE_78SCRN, 
  SAMPLE_SEX_1979, 
  HGC_1979, 
  HGCREV79_1979, 
  HGC_1980, 
  HGCREV80_1980, 
  Q1_3_A_M_1981, 
  Q1_3_A_Y_1981, 
  ASVAB_1_1981, 
  ASVAB_4_1981, 
  ASVAB_5_1981, 
  ASVAB_6_1981, 
  ASVAB_7_1981, 
  AFQT_1_1981, 
  AFQT_2_1981, 
  AFQT_3_1981, 
  HGC_1981, 
  HGCREV81_1981, 
  Q15_9A_000003_1993, 
  Q15_9A_000003_1994.
