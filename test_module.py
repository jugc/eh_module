import datapost as dp
import pandas as pd
import sys
#import csv

summary_table =  "../../data/170404_hybrid/170404-133841.txt"
voltage_buzzer = "../../data/170404_hybrid/170404-133841_voltage_buzzer_ts.txt"
voltage_vem =    "../../data/170404_hybrid/170404-133841_voltage_VEM_ts.txt"
voltage_mfc =    "../../data/170404_hybrid/170404-133841_voltage_MFC_ts.txt"
voltage_dem =    "../../data/170404_hybrid/170404-133841_voltage_DEH_ts.txt"

filenames = [summary_table,voltage_buzzer,voltage_vem,voltage_mfc,voltage_dem]
fileheaders = ["col_1","col_2","col_3","col_1","col_2","vdc","col_7"]
Fs = 1000 # sampling rate in Hz
rl_eh = 288
rl_pzt = 36e3
summary_df = dp.read_files_into_data_frames(filenames,fileheaders,Fs)
#,eh_ts_df,pzt_ts_df


print summary_df.head()
