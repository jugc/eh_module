import datapost as dp
import pandas as pd
import sys
#import csv

filenames = ["test_file.txt","voltage_EH_ts.txt","voltage_MFC_ts.txt"]
fileheaders = ["col_1","col_2","col_3","col_1","col_2","vdc","col_7"]
Fs = 1000 # sampling rate in Hz
rl_eh = 288
rl_pzt = 36e3
summary_df,eh_ts_df,pzt_ts_df = dp.read_files_into_data_frames(filenames,fileheaders,Fs)


eh_ts_df = dp.get_rms_power(eh_ts_df,rl_eh)
pzt_ts_df = dp.get_rms_power(pzt_ts_df,rl_pzt)

print summary_df.head()
print eh_ts_df.head()
