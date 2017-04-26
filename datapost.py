'''Module definition for data analysis of the energy harvesting project '''
import csv as csv
import pandas as pd
import numpy as np
from os import listdir
from os.path import isfile, join
#------------------------------- Functions ------------------------------------
#******************************************************************************
def read_files_into_data_frames(filename,headers,Fs):
# Input: filename - list of strings with the names each file
#        headers - a list of strings where each element is string and corresponds
#                  to the column header of the summary file
# Return: - the three dataframes with the modifications such as time column for the time-series
#           and the headers for the summary

    # for the summary file, only the setting for the speed in v_dc will be included in the dataframe
    summary_df = pd.read_table(filename[0], sep = '\t', names = headers, usecols = ['vdc'])
    buzzer_ts_df = pd.read_table(filename[1], sep = '\t', header = None)
    vem_ts_df = pd.read_table(filename[2], sep = '\t', header = None)
    mfc_ts_df = pd.read_table(filename[3], sep = '\t', header = None)
    dem_ts_df = pd.read_table(filename[4], sep = '\t', header = None)

    # Adding the time column to the time-series dataframes
    NoSamples = len(buzzer_ts_df.index)
    buzzer_ts_df["time(s)"] = np.linspace(0,NoSamples/Fs,num=NoSamples)

    NoSamples = len(vem_ts_df.index)
    vem_ts_df["time(s)"] = np.linspace(0,NoSamples/Fs,num=NoSamples)

    NoSamples = len(mfc_ts_df.index)
    mfc_ts_df["time(s)"] = np.linspace(0,NoSamples/Fs,num=NoSamples)

    NoSamples = len(dem_ts_df.index)
    dem_ts_df["time(s)"] = np.linspace(0,NoSamples/Fs,num=NoSamples)

    # Adding additional columns for units of speed in the summary dataframe
    summary_df["rpm"] = summary_df["vdc"]*125.0
    summary_df["rad/s"] = summary_df["rpm"]*(0.104719755)
    summary_df["hz"] = summary_df["rpm"]*(1/60.0)

    return summary_df,buzzer_ts_df,vem_ts_df,mfc_ts_df,dem_ts_df
    #,
#******************************************************************************
def get_rms_power(dataframe,rl):
    num_cols = len(dataframe.columns) - 1   # -1 because the time column is present
    new_col_index = num_cols - 1    # because the index starts in 0

    for col in dataframe:
        dataframe[new_col_index] = (dataframe[col]**2)/rl
        new_col_index = new_col_index + 1

    return dataframe
#******************************************************************************
def collect_stats(dataframes):
    return True
#******************************************************************************
def fft_shaker(Ts,y):
    ''' A customized FFT using known algorithms but tailored to the data needs of
    the project.
    Inputs:
        - Ts: sampling time
        - y: time-series data
    Outputs:
        - frq_Y: frequency range vetor of amplitude fft
        - Y: amplitude of single-side fft. The units are the same of the input y
        - frq_Pxx: frequency range vetor of power spectrum
        - Pxx: power spectrum in units of y per Hz
        '''
    N = len(y)
    Fs = 1/Ts
    k = np.arange(N)
    T = N/Fs
    frq = k/T # two sides frequency range
    frq = frq[range(N/2)] # one side frequency range
    Y = np.fft.fft(y)/N # fft computing and normalization
    Y = Y[range(N/2)]
    frq_Pxx, Pxx = signal.periodogram(y, Fs, 'flattop', scaling='spectrum')
    return frq_Y,Y,frq_Pxx,Pxx
#******************************************************************************
def check_filename(filename,word):

    for i in word:
        if i in filename:
            return True
        else:
            return False
#******************************************************************************
def load_ts_files(filename):
    text_file = open(filename, "r")
    data = text_file.read().split('\t')
    return data
#******************************************************************************
def rpm2hz(X):
    # Convertion of rpm to hz in a list
    V = X/60
    return ["%.1f" % z for z in V]
#******************************************************************************

#---------------------------- Class definition ---------------------------------
class HEH_dataset:
    def __init__(self,NAME,FOLDER,rl_mfc,rl_eh):
        self.data    = []
        self.name    = NAME
        self.folder  = FOLDER
        self.filelist = []
        self.dataframes = []
        self.exp_speeds_rpm  = []
        self.exp_speeds_vdc  = []
        self.max_power_eh    = []
        self.max_voltage_eh  = []
        self.min_power_eh    = []
        self.min_voltage_eh  = []
        self.max_power_mfc   = []
        self.max_voltage_mfc = []
        self.min_power_mfc   = []
        self.min_voltage_mfc = []
        self.rl_mfc          = rl_mfc
        self.rl_eh           = rl_eh

    def save_in_list(self):
        self.filelist = [f for f in listdir(self.folder) if isfile(join(self.folder, f))]

    def read_into_dataframes(self):
        self.save_in_list()
        for item in range(0,len(self.filelist)):
        # if the file name contains the word voltage, then it corresponds to a voltage time series
            tmp_filename = self.filelist[item]
            if check_filename(tmp_filename,'voltage'):
                # loads the time-series data
                tmp_list = load_ts_files(self.folder+self.filelist[item])
                df = pd.DataFrame(tmp_list)     # create a data frame with the time-series data
                df.columns = ['voltage(v)']     # add the name voltage to the dataframe.
                self.dataframes.append(df)           #
                self.dataframes[item]['voltage(v)'] = pd.to_numeric(self.dataframes[item]['voltage(v)'], errors='coerce')
                # I noticed some of the data points are missing, so an interpolation is performed to fill in the gaps
                self.dataframes[item]['voltage(v)'] = self.dataframes[item]['voltage(v)'].interpolate()
            else:
                self.dataframes.append(pd.read_table(self.folder+self.filelist[item], sep='\t',
                          names = ["time(s)", "voltage_eh(v)", "power(mw)", "position(mm)","velocity(RPM)","velocity(VDC)",
                                   "voltage_mfc(v)"]))

    def add_time_column(self):
        #  Add a time column into the data frames that contain de time-series of the voltage from the EH
        for item in range(0,len(self.filelist)):
            if not check_filename(self.filelist[item],'voltage'):
                tmp_time = self.dataframes[item]["time(s)"].max()
            else:
                self.dataframes[item].describe()
                self.dataframes[item]["time(s)"] = np.linspace(0, tmp_time, num=len(self.dataframes[item]["voltage(v)"]))

    def eh_stats(self):
        no_files = len(self.filelist)
        self.exp_speeds_rpm  = np.empty(no_files/3)
        self.exp_speeds_vdc  = np.empty(no_files/3)
        self.max_power_eh    = np.empty(no_files/3)
        self.max_voltage_eh  = np.empty(no_files/3)
        self.min_power_eh    = np.empty(no_files/3)
        self.min_voltage_eh  = np.empty(no_files/3)
        self.max_power_mfc   = np.empty(no_files/3)
        self.max_voltage_mfc = np.empty(no_files/3)
        self.min_power_mfc   = np.empty(no_files/3)
        self.min_voltage_mfc = np.empty(no_files/3)
        v_idx_1 = 0
        v_idx_2 = 0
        v_idx_3 = 0

        for item in range(0,no_files):
            if check_filename(self.filelist[item],'MFC'):
                #print v_idx_1
                # Get the maximum and minimum values for the last half of the data for the MFC
                Count                   = self.dataframes[item]['voltage(v)'].count()
                self.max_voltage_mfc[v_idx_1] = (self.dataframes[item].loc[0.9*Count:Count]['voltage(v)'].max())/np.sqrt(2)
                self.max_power_mfc[v_idx_1]   = ((self.dataframes[item].loc[0.9*Count:Count]['voltage(v)'].max()/np.sqrt(2))**2)/self.rl_mfc
                self.min_power_mfc[v_idx_1]   = ((self.dataframes[item].loc[0.9*Count:Count]['voltage(v)'].min()/np.sqrt(2))**2)/self.rl_mfc
                self.min_voltage_mfc[v_idx_1] = (self.dataframes[item].loc[0.9*Count:Count]['voltage(v)'].min())/np.sqrt(2)
                v_idx_1 = v_idx_1 + 1
            elif check_filename(self.filelist[item],'EH'):
                #print v_idx_2
                Count     = self.dataframes[item]['voltage(v)'].count()
                self.max_voltage_eh[v_idx_2] = (self.dataframes[item].loc[0.9*Count:Count]['voltage(v)'].max())/np.sqrt(2)
                self.max_power_eh[v_idx_2]   = ((self.dataframes[item].loc[0.9*Count:Count]['voltage(v)'].max()/np.sqrt(2))**2)/self.rl_eh
                self.min_power_eh[v_idx_2]   = ((self.dataframes[item].loc[0.9*Count:Count]['voltage(v)'].min()/np.sqrt(2))**2)/self.rl_eh
                self.min_voltage_eh[v_idx_2] = (self.dataframes[item].loc[0.9*Count:Count]['voltage(v)'].min())/np.sqrt(2)
                v_idx_2 = v_idx_2 + 1
            else:
                Count                  = self.dataframes[item]['velocity(VDC)'].count()
                self.exp_speeds_rpm[v_idx_3] = 125*self.dataframes[item].loc[0.9*Count:Count]['velocity(VDC)'].mean()
                self.exp_speeds_vdc[v_idx_3] = self.dataframes[item].loc[0.9*Count:Count]['velocity(VDC)'].mean()
                v_idx_3 = v_idx_3 + 1
            if v_idx_1 == no_files and v_idx_2 == no_files and v_idx_3 == no_files:
                break
