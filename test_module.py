import datapost as dp
import pandas as pd
import sys
#import csv

filename = "test_file.txt"
fileheaders = ["col_1","col_2","col_3","col_1","col_2","col_3","col_7"]

df = pd.read_table(filename, sep = '\t', names = fileheaders)
print df["col_1"].loc[:]

#dp.add_header_names(filename,fileheaders)
