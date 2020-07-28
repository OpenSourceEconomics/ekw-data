options nocenter validvarname=any;

*---Read in space-delimited ascii file;

data new_data;


infile 'afqt.dat' lrecl=85 missover DSD DLM=' ' print;
input
  A0002600
  R0000100
  R0000300
  R0000500
  R0173600
  R0214700
  R0214800
  R0216700
  R0216701
  R0406400
  R0406401
  R0410100
  R0410300
  R0614800
  R0615100
  R0615200
  R0615300
  R0615400
  R0618200
  R0618300
  R0618301
  R0618900
  R0618901
  R4397702
  R5057802
;
array nvarlist _numeric_;


*---Recode missing values to SAS custom system missing. See SAS
      documentation for use of MISSING option in procedures, e.g. PROC FREQ;

do over nvarlist;
  if nvarlist = -1 then nvarlist = .R;  /* Refused */
  if nvarlist = -2 then nvarlist = .D;  /* Dont know */
  if nvarlist = -3 then nvarlist = .I;  /* Invalid missing */
  if nvarlist = -4 then nvarlist = .V;  /* Valid missing */
  if nvarlist = -5 then nvarlist = .N;  /* Non-interview */
end;

  label A0002600 = "VERSION_R26_1 2014";
  label R0000100 = "ID# (1-12686) 79";
  label R0000300 = "DATE OF BIRTH - MONTH 79";
  label R0000500 = "DATE OF BIRTH - YR 79";
  label R0173600 = "SAMPLE ID  79 INT";
  label R0214700 = "RACL/ETHNIC COHORT /SCRNR 79";
  label R0214800 = "SEX OF R 79";
  label R0216700 = "HGC AS OF 05/01/79 SRVY YR";
  label R0216701 = "HIGHEST GRADE COMPLTD (REV) 79";
  label R0406400 = "HGC AS OF 05/01/80 SRVY YR";
  label R0406401 = "HIGHEST GRADE COMPLTD (REV) 80";
  label R0410100 = "DATE OF BIRTH - MONTH 81";
  label R0410300 = "DATE OF BIRTH - YR 81";
  label R0614800 = "PROFILES ASVAB NORMAL/ALTERED TEST 81";
  label R0615100 = "PROFILES ASVAB SEC 2-ARITHMETIC 81";
  label R0615200 = "PROFILES ASVAB SEC 3-WORD KNLDG 81";
  label R0615300 = "PROFILES ASVAB SEC 4-PARAGRAPH COMP 81";
  label R0615400 = "PROFILES ASVAB SEC 5-NUMERIC OPERS 81";
  label R0618200 = "PROFILES AFQT PRCTILE SCORE-80 81";
  label R0618300 = "PROFILES AFQT PRCTILE 89 (REV) 81";
  label R0618301 = "PROFILES AFQT PRCTILE 2006 (REV) 81";
  label R0618900 = "HGC AS OF 05/01/81 SRVY YR";
  label R0618901 = "HIGHEST GRADE COMPLTD (REV) 81";
  label R4397702 = "SPECL CHAR THAT COULD AFFECT ANS: MNT HC";
  label R5057802 = "SPECL CHAR THAT COULD AFFECT ANS: MNT HC";

/*---------------------------------------------------------------------*
 *  Crosswalk for Reference number & Question name                     *
 *---------------------------------------------------------------------*
 * Uncomment and edit this RENAME statement to rename variables
 * for ease of use.  You may need to use  name literal strings
 * e.g.  'variable-name'n   to create valid SAS variable names, or 
 * alter variables similarly named across years.
 * This command does not guarantee uniqueness

 * See SAS documentation for use of name literals and use of the
 * VALIDVARNAME=ANY option.     
 *---------------------------------------------------------------------*/
  /* *start* */

* RENAME
  A0002600 = 'VERSION_R26_2014'n
  R0000100 = 'CASEID_1979'n
  R0000300 = 'Q1-3_A~M_1979'n
  R0000500 = 'Q1-3_A~Y_1979'n
  R0173600 = 'SAMPLE_ID_1979'n
  R0214700 = 'SAMPLE_RACE_78SCRN'n
  R0214800 = 'SAMPLE_SEX_1979'n
  R0216700 = 'HGC_1979'n
  R0216701 = 'HGCREV79_1979'n
  R0406400 = 'HGC_1980'n
  R0406401 = 'HGCREV80_1980'n
  R0410100 = 'Q1-3_A~M_1981'n
  R0410300 = 'Q1-3_A~Y_1981'n
  R0614800 = 'ASVAB-1_1981'n
  R0615100 = 'ASVAB-4_1981'n
  R0615200 = 'ASVAB-5_1981'n
  R0615300 = 'ASVAB-6_1981'n
  R0615400 = 'ASVAB-7_1981'n
  R0618200 = 'AFQT-1_1981'n
  R0618300 = 'AFQT-2_1981'n
  R0618301 = 'AFQT-3_1981'n
  R0618900 = 'HGC_1981'n
  R0618901 = 'HGCREV81_1981'n
  R4397702 = 'Q15-9A~000003_1993'n
  R5057802 = 'Q15-9A~000003_1994'n
;
  /* *finish* */

run;

proc means data=new_data n mean min max;
run;


/*---------------------------------------------------------------------*
 *  FORMATTED TABULATIONS                                              *
 *---------------------------------------------------------------------*
 * You can uncomment and edit the PROC FORMAT and PROC FREQ statements 
 * provided below to obtain formatted tabulations. The tabulations 
 * should reflect codebook values.
 * 
 * Please edit the formats below reflect any renaming of the variables
 * you may have done in the first data step. 
 *---------------------------------------------------------------------*/

/*
proc format; 
value vx0f
  1-999='1 TO 999'
  1000-1999='1000 TO 1999'
  2000-2999='2000 TO 2999'
  3000-3999='3000 TO 3999'
  4000-4999='4000 TO 4999'
  5000-5999='5000 TO 5999'
  6000-6999='6000 TO 6999'
  7000-7999='7000 TO 7999'
  8000-8999='8000 TO 8999'
  9000-9999='9000 TO 9999'
  10000-10999='10000 TO 10999'
  11000-11999='11000 TO 11999'
  12000-12999='12000 TO 12999'
;
value vx2f
  0='0: < 1'
  1='1'
  2='2'
  3='3'
  4='4'
  5='5'
  6='6'
  7='7'
  8='8'
  9='9'
  10='10'
  11='11'
  12='12'
  13='13'
  14='14'
  15='15'
  16='16'
  17-99999='17 TO 99999: 17+'
;
value vx3f
  0-56='0 TO 56: < 57'
  57='57'
  58='58'
  59='59'
  60='60'
  61='61'
  62='62'
  63='63'
  64='64'
  65='65'
  66='66'
  67='67'
  68='68'
  69='69'
  70='70'
  71='71'
  72='72'
  73-99999='73 TO 99999: 73+'
;
value vx4f
  1='CROSS MALE WHITE'
  2='CROSS MALE WH. POOR'
  3='CROSS MALE BLACK'
  4='CROSS MALE HISPANIC'
  5='CROSS FEMALE WHITE'
  6='CROSS FEMALE WH POOR'
  7='CROSS FEMALE BLACK'
  8='CROSS FEMALE HISPANIC'
  9='SUP MALE WH POOR'
  10='SUP MALE BLACK'
  11='SUP MALE HISPANIC'
  12='SUP FEM WH POOR'
  13='SUP FEMALE BLACK'
  14='SUP FEMALE HISPANIC'
  15='MIL MALE WHITE'
  16='MIL MALE BLACK'
  17='MIL MALE HISPANIC'
  18='MIL FEMALE WHITE'
  19='MIL FEMALE BLACK'
  20='MIL FEMALE HISPANIC'
;
value vx5f
  1='HISPANIC'
  2='BLACK'
  3='NON-BLACK, NON-HISPANIC'
;
value vx6f
  1='MALE'
  2='FEMALE'
;
value vx7f
  0='NONE'
  1='1ST GRADE'
  2='2ND GRADE'
  3='3RD GRADE'
  4='4TH GRADE'
  5='5TH GRADE'
  6='6TH GRADE'
  7='7TH GRADE'
  8='8TH GRADE'
  9='9TH GRADE'
  10='10TH GRADE'
  11='11TH GRADE'
  12='12TH GRADE'
  13='1ST YR COL'
  14='2ND YR COL'
  15='3RD YR COL'
  16='4TH YR COL'
  17='5TH YR COL'
  18='6TH YR COL'
  19='7TH YR COL'
  20='8TH YR COL OR MORE'
  95='UNGRADED'
;
value vx8f
  0='NONE'
  1='1ST GRADE'
  2='2ND GRADE'
  3='3RD GRADE'
  4='4TH GRADE'
  5='5TH GRADE'
  6='6TH GRADE'
  7='7TH GRADE'
  8='8TH GRADE'
  9='9TH GRADE'
  10='10TH GRADE'
  11='11TH GRADE'
  12='12TH GRADE'
  13='1ST YR COL'
  14='2ND YR COL'
  15='3RD YR COL'
  16='4TH YR COL'
  17='5TH YR COL'
  18='6TH YR COL'
  19='7TH YR COL'
  20='8TH YR COL OR MORE'
  95='UNGRADED'
;
value vx9f
  0='NONE'
  1='1ST GRADE'
  2='2ND GRADE'
  3='3RD GRADE'
  4='4TH GRADE'
  5='5TH GRADE'
  6='6TH GRADE'
  7='7TH GRADE'
  8='8TH GRADE'
  9='9TH GRADE'
  10='10TH GRADE'
  11='11TH GRADE'
  12='12TH GRADE'
  13='1ST YR COL'
  14='2ND YR COL'
  15='3RD YR COL'
  16='4TH YR COL'
  17='5TH YR COL'
  18='6TH YR COL'
  19='7TH YR COL'
  20='8TH YR COL OR MORE'
  95='UNGRADED'
;
value vx10f
  0='NONE'
  1='1ST GRADE'
  2='2ND GRADE'
  3='3RD GRADE'
  4='4TH GRADE'
  5='5TH GRADE'
  6='6TH GRADE'
  7='7TH GRADE'
  8='8TH GRADE'
  9='9TH GRADE'
  10='10TH GRADE'
  11='11TH GRADE'
  12='12TH GRADE'
  13='1ST YR COL'
  14='2ND YR COL'
  15='3RD YR COL'
  16='4TH YR COL'
  17='5TH YR COL'
  18='6TH YR COL'
  19='7TH YR COL'
  20='8TH YR COL OR MORE'
  95='UNGRADED'
;
value vx11f
  0='0: < 1'
  1='1'
  2='2'
  3='3'
  4='4'
  5='5'
  6='6'
  7='7'
  8='8'
  9='9'
  10='10'
  11='11'
  12='12'
  13='13'
  14='14'
  15='15'
  16='16'
  17-99999='17 TO 99999: 17+'
;
value vx12f
  0-54='0 TO 54: < 55'
  55='55'
  56='56'
  57='57'
  58='58'
  59='59'
  60='60'
  61='61'
  62='62'
  63='63'
  64='64'
  65='65'
  66='66'
  67='67'
  68='68'
  69='69'
  70='70'
  71-99999='71 TO 99999: 71+'
;
value vx13f
  51='COMPLETED'
  52='COMP-CONVERTED REFUSAL'
  53='COMP-PROBLEM REPORTED'
  54='COMP-SPANISH INSTR. CARDS'
  67='COMP-PRODECURES ALTERED'
;
value vx21f
  0='NONE'
  1='1ST GRADE'
  2='2ND GRADE'
  3='3RD GRADE'
  4='4TH GRADE'
  5='5TH GRADE'
  6='6TH GRADE'
  7='7TH GRADE'
  8='8TH GRADE'
  9='9TH GRADE'
  10='10TH GRADE'
  11='11TH GRADE'
  12='12TH GRADE'
  13='1ST YR COL'
  14='2ND YR COL'
  15='3RD YR COL'
  16='4TH YR COL'
  17='5TH YR COL'
  18='6TH YR COL'
  19='7TH YR COL'
  20='8TH YR COL OR MORE'
  95='UNGRADED'
;
value vx22f
  0='NONE'
  1='1ST GRADE'
  2='2ND GRADE'
  3='3RD GRADE'
  4='4TH GRADE'
  5='5TH GRADE'
  6='6TH GRADE'
  7='7TH GRADE'
  8='8TH GRADE'
  9='9TH GRADE'
  10='10TH GRADE'
  11='11TH GRADE'
  12='12TH GRADE'
  13='1ST YR COL'
  14='2ND YR COL'
  15='3RD YR COL'
  16='4TH YR COL'
  17='5TH YR COL'
  18='6TH YR COL'
  19='7TH YR COL'
  20='8TH YR COL OR MORE'
  95='UNGRADED'
;
value vx23f
  0='DOES NOT APPLY'
  1='RESPONDENT DEAF'
  2='RESPONDENT BLIND'
  3='RESPONDENT MENTALLY HANDICAPPED OR RETARDED'
  4='RESPONDENT''S ENGLISH IS VERY POOR'
  5='RESPONDENT CANNOT READ'
  6='RESPONDENT PHYSICALLY HANDICAPPED'
  7='OTHER'
;
value vx24f
  1-3='Respondent mentally handicapped or retarded'
  0='NOT SELECTED'
;
*/

/* 
 *--- Tabulations using reference number variables;
proc freq data=new_data;
tables _ALL_ /MISSING;
  format A0002600 vx0f.;
  format R0000300 vx2f.;
  format R0000500 vx3f.;
  format R0173600 vx4f.;
  format R0214700 vx5f.;
  format R0214800 vx6f.;
  format R0216700 vx7f.;
  format R0216701 vx8f.;
  format R0406400 vx9f.;
  format R0406401 vx10f.;
  format R0410100 vx11f.;
  format R0410300 vx12f.;
  format R0614800 vx13f.;
  format R0618900 vx21f.;
  format R0618901 vx22f.;
  format R4397702 vx23f.;
  format R5057802 vx24f.;
run;
*/

/*
*--- Tabulations using default named variables;
proc freq data=new_data;
tables _ALL_ /MISSING;
  format 'VERSION_R26_2014'n vx0f.;
  format 'Q1-3_A~M_1979'n vx2f.;
  format 'Q1-3_A~Y_1979'n vx3f.;
  format 'SAMPLE_ID_1979'n vx4f.;
  format 'SAMPLE_RACE_78SCRN'n vx5f.;
  format 'SAMPLE_SEX_1979'n vx6f.;
  format 'HGC_1979'n vx7f.;
  format 'HGCREV79_1979'n vx8f.;
  format 'HGC_1980'n vx9f.;
  format 'HGCREV80_1980'n vx10f.;
  format 'Q1-3_A~M_1981'n vx11f.;
  format 'Q1-3_A~Y_1981'n vx12f.;
  format 'ASVAB-1_1981'n vx13f.;
  format 'HGC_1981'n vx21f.;
  format 'HGCREV81_1981'n vx22f.;
  format 'Q15-9A~000003_1993'n vx23f.;
  format 'Q15-9A~000003_1994'n vx24f.;
run;
*/