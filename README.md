# Energy Harvesting Data Analysis Module

This is a python module created to analyze experimental data.

### Data management strategy

#### File structure

It is assumed that for each experiment, there will be a range of tests at different speeds of the motor. For example, an experiment that uses the long crank type, will be run from 50 RPM to 300 RPM in steps of 50 RPM. That results in six tests. Moreover, the data for each test comes in a set of three files: one that contains the time, position, maximum values of power and voltage, and the speed (the file name doesn't have a suffix, only the date and time of recording); the second file contains the MFC voltage per sample; and last, the EH voltage per sample. The last two files have the suffix `voltage_MFC_ts` and `voltage_EH_ts`.

The data for an experiment should be stored in a folder with the following convention: `yymmdd_description`.

#### Class for shaker data

The class `HEH_dataset` (Hybrid Energy Harvester dataset) contains properties and methods that are used for analysing the data from the experiments. Here are the short description for each method:
* `__init__`: initializes the instance of this class. The arguments it takes are the name and folder for the experiment. It also initializes the rest of properties, e.g. the empty list that will contain the max values of the MFC voltage.
* `save_in_list`: finds the files in a given folder, and saves the names in a list. This method is used in `read_into_dataframes`, so it is not necessary to call it.
* `read_into_dataframes`: uses the list of filenames, and reads the data into panda dataframes. This method takes into account the file type (whether is a time-series or not) and assigns the appropriate headings to the dataframes.
* `add_time_column`: using information about the data collection time and the sampling time, it assigns the corresponding time column to the time series data.
* `eh_stats`: finds the max and min values for voltage and power for both energy harvesters. It also defines the speed vector, where each entry is the corresponding speed of a test. This is calculated as the mean over the last half of the data, in order to avoid misleading data due to adjustment of the system. The same is true for the rest of the stats calculated in this method.

**NOTE:** there will be an instance of a class created for each experiment. One of the properties of the class is `dataframes`, and it holds all the data frames that are created for each test.

#### How to use this

Lets assume we want to compare the data among a group of experiments. The list `NAMES` contains the names for each experiment. The location where the data is stored for each experiment, should be indicated in the list `FOLDERS`. There should be as many elements in `NAMES` as in `FOLDERS`!

An easy way to manage the data for several experiments at the same time is to use an ordered dictionary. It is mandatory to use the ordered version because the association of the folders and the names of the experiments. In the dictionary, each key corresponds to an experiment and the value is an instance of the class `HEH_dataset`.

First, the dictionary is initialized with:

    datasets = OrderedDict((el, 0) for el in NAMES)

Each key will be created with the entries of `NAMES` and the value is set to zero.

To populate the dictionary datasets, it is necessary to run the following routine. The lop runs through the lists `NAMES` and `FOLDERS`, and initializes an instance of the class for each key in the dictionary. This is followed by the reading of the data and the calculation of the stats for each experiment.

    idx = 0
    for key in datasets:
        datasets[key] = HEH_dataset(NAMES[idx],FOLDERS[idx])
        datasets[key].read_into_dataframes()
        datasets[key].add_time_column()
        datasets[key].eh_stats()    
        idx += 1

To access the raw data, which is contained in the class instance, you should access the property `dataframes`. This is a list that contains 3 elements, where is element is a dataframe. The order of the elements goes like this: [0] is the dataframe that contains the summary data. Element [1] contains the time-series of the **EH**. Last, element [2] contains the time-series of the **MFC**. In summary, the order of the dataframes contain in the property list `dataframes`, is the same as the list order `filelist`. The later, is populated in alphabetic order using the file names.
