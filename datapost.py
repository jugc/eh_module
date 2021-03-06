'''Module definition for data analysis of the energy harvesting project '''
import csv as csv
import pandas as pd
import numpy as np
from os import listdir
import fnmatch
from os.path import isfile, join
from scipy import signal
#------------------------------- Functions ------------------------------------
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
    return frq,Y,frq_Pxx,Pxx
#******************************************************************************
def check_filename(filename,word):
    if fnmatch.fnmatch(filename, '*_'+word+'*.txt'):
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
    def __init__(self,NAME,FOLDER,rl_mfc,rl_vem,rl_buzzer,rl_dem,fs):
        self.data    = []
        self.name    = NAME
        self.folder  = FOLDER
        self.filelist = []
        self.dataframes = []
        self.df_dummy_buzzer = []
        self.df_dummy_mfc = []
        self.df_dummy_vem = []
        self.df_dummy_dem = []
        self.df_buzzer = pd.DataFrame()
        self.df_mfc = pd.DataFrame()
        self.df_vem = pd.DataFrame()
        self.df_dem = pd.DataFrame()
        self.exp_speeds_rpm  = []
        self.exp_speeds_vdc  = []
        self.exp_speeds_hz   = []
        self.exp_speeds_radsec  = []
        self.max_power_eh    = []
        self.max_voltage_eh  = []
        self.min_power_eh    = []
        self.min_voltage_eh  = []
        self.max_power_mfc   = []
        self.max_voltage_mfc = []
        self.min_power_mfc   = []
        self.min_voltage_mfc = []
        self.rl_mfc          = rl_mfc
        self.rl_vem          = rl_vem
        self.rl_buzzer        = rl_buzzer
        self.rl_dem          = rl_dem
        self.fs              = fs
        self.testlist        = []
        self.power_col_labels= []
        self.dummy_summary_headers = ["col_1","col_2","col_3","col_1","col_2","vdc","col_7"]
        self.num_of_reps     = 0
        self.category_labels = []
        self.time            = []
        self.num_of_samples  = 0

    def get_num_repetitions(self):
        # Calculates the number of repetitions for a given experiment (read dataset).
        # Since each repetition contains 5 files (summary and four time series),
        # the length of the file list is divided by 5
        self.num_of_reps = len(self.filelist)/5
        self.category_labels = ['rep_' + str(num+1) for num in range(0,self.num_of_reps) ]


    def save_in_list(self):
        # creates a list with all the file names in the dataset folder
        self.filelist = [f for f in listdir(self.folder) if isfile(join(self.folder, f))]

    def read_into_dataframes(self):
        # This method reads each file into a data frame. Then, concatenates each dataframe type (buzzer,mfc,vem,dem)
        # into one big dataframe.
        self.save_in_list()
        self.get_num_repetitions()
        print self.category_labels
        # Dummy for loop that finds a summary file from the dataset in order to create the list of tests carried out during the experiment
        # These correspond to the speeds of the motor in VDC
        for item in range(0,len(self.filelist)):
        # if the file name contains the word s, then it corresponds to a voltage time series
            tmp_filename = self.folder+self.filelist[item]

            if check_filename(tmp_filename,'summary'):
                df_summary_dummy = pd.read_table(tmp_filename, sep = '\t', names = self.dummy_summary_headers, usecols = ['vdc'])
                self.exp_speeds_vdc = df_summary_dummy["vdc"].values
                self.exp_speeds_rpm = self.exp_speeds_vdc*125.0
                self.exp_speeds_radsec = self.exp_speeds_rpm*(0.104719755)
                self.exp_speeds_hz = self.exp_speeds_rpm*(1/60.0)
                num_of_exp = len(df_summary_dummy['vdc'])
                a = range(1,num_of_exp+1)
                self.testlist = ['v_' + str(s) for s in a]
                self.power_col_labels = ['p_' + str(s) for s in a]
                del df_summary_dummy
                break

        # This loop opens each time-series file and saves it into a dataframe with the headers in slef.testlist
        # It also savs the summary files into dataframes and converst the speeds from vdc to hz, rpm and rad/s
        self.df_dummy_mfc = self.append_df_to_list('MFC')
        self.df_mfc = pd.concat(self.df_dummy_mfc)
        self.get_rms_power(self.df_mfc,self.rl_mfc)

        self.df_dummy_buzzer = self.append_df_to_list('buzzer')
        self.df_buzzer = pd.concat(self.df_dummy_buzzer)
        self.get_rms_power(self.df_buzzer,self.rl_buzzer)

        self.df_dummy_dem = self.append_df_to_list('DEM')
        self.df_dem = pd.concat(self.df_dummy_dem)
        self.get_rms_power(self.df_dem,self.rl_dem)

        self.df_dummy_vem = self.append_df_to_list('VEM')
        self.df_vem = pd.concat(self.df_dummy_vem)
        self.get_rms_power(self.df_vem,self.rl_vem)

        # Defining the time vector. This is in case it is needed for time-series plotting


    def append_df_to_list(self,NAME_EH):
        dummy_list = []
        time_vec_flag = True
        for item in range(0,len(self.filelist)):
        # if the file name contains the word voltage, then it corresponds to a voltage time series
            tmp_filename = self.filelist[item]
            if check_filename(tmp_filename,NAME_EH):
                # loads the time-series data
                df = pd.read_table(self.folder+tmp_filename, sep = '\t', names = self.testlist)
                dummy_list.append(df)      #

                # defining a time vector that correspnds to a time series length. This is the reason why it is inside a loop
                # of one of the energy harvesters time-series files
                if time_vec_flag == True:
                    self.time_vector(tmp_filename)
                    time_vec_flag = False
        return dummy_list

    def get_rms_power(self,dataframe,rl):
        num_cols = len(dataframe.columns)
        new_col_index = num_cols - 1    # because the index starts in 0
        power_col_index = 0
        for col in dataframe:
            dataframe[new_col_index] = (1/np.sqrt(2))*(dataframe[col]**2)/rl
            # Renaming the default column name given
            dataframe.rename(columns={new_col_index: self.power_col_labels[power_col_index]}, inplace=True)
            new_col_index = new_col_index + 1
            power_col_index = power_col_index + 1

    def time_vector(self,tmp_filename):
        df = pd.read_table(self.folder+tmp_filename, sep = '\t', names = self.testlist)
        self.num_of_samples = df[self.testlist[0]].count()
        self.time = np.linspace(0,self.num_of_samples/self.fs,num=self.num_of_samples)
