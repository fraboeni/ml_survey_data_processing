# This repository contains code to process and analyze data from a LimeSurvey 

It contains three main packages:

## 1. data_processing
Contains code to
- download data from a LimeSurvey instance
- process the data into a usable CSV-file
- given an example in what order they are to call

The final CSV file has the following columns according to the types of the LimeSurvey questions:

*Single Choice questions:* For each such question, 
a column in created with question code (QC) as header. 
Under this header, there are 3-4 subcolumns:
- a: contains the answer code as an integer
- a_text: contains the answer as a plain text
- a_code: contains the answer code, such as A1
- optional: QC[other]: comments inserted to the questions

*Multiple choice questions:* For each subquery with numbering XXX (SQXXX, possible answer solution), a column is created 
with column header QCs[SQXXX]. 
Under this header there are 2 subcolumns:
- a: 0/1 binary code showing if the answer was ticked or not
- a_text: if answer was 1: text corresponting to the subquery

*Long or short free text:* The text is inserted to the table.
As all texts it is cleaned from LimeSurvey's internal HTML/CSS coding

*Ranking:* For a ranking question, for each possible answer with numbering X, a column is created with 
column header QCs[X].
Under this header there are 2 subcolumns:
- a: rank (starting with 1: highest, to N: lowest) that the user has given to this question
- a_text: text that belongs to this option in the ranking


All text in the final CSV is cleaned from LimeSurvey's HTML and CSV formatting.



## 2. data_analysis
Contains code to:
- perform statistical tests on the data
- obtain and reorder labels in questions

The latter one is only needed when during survey design, one was not careful and the order of 
the answer possibilities is not correct (to perform one of the statistical tests).
The ' get_data_labels' function needs an answer mapping, this is a dataframe having also a 2
line-header [QC,AC] with AC the answer code. And entries: the corresponding integer.

## 3. data_visualization
Contains code for several visualization techniques useful to perform exploitative analyses or to plot results from the analyses.