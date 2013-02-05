lawdiff
=================

This project came out of the Bicoastal Datafest with the goal of identifying bills from different states that used the same language in order to identify outside influence since it's unlikely that two states would come up with bills that use the same language. More information can be found here: http://www.bdatafest.computationalreporting.com/projects/similar-laws-across-states

Approach:

1. Use OpenStates API to download bills
2. Convert each downloaded bill to text (from PDF and HTML)
3. Extract phrases from the bill text (right now we use 8 word phrases and exclude stop words)
4. Compare these phrases across multiple states and identify overlap

Scripts:

1. get_bills.py: Use this to download and convert the bills to text
2. generate_bill_phrase_file.py: Generate a massive text file that contains the file name, the state, and the phrase for each bill
3. analyze_bill_phrase_file.py: Parse the file from the previous step to find overlap and write the overlap to a new file