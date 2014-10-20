from __future__ import print_function, division
from inspect import currentframe, getfile, getsourcefile
import pandas as pd
import numpy as np
from pandas import *
from copy import deepcopy
from os.path import *
from os import listdir, getcwd
from sys import *
from nilmtk.datastore import Key
from nilmtk.timeframe import TimeFrame
from nilmtk.measurement import LEVEL_NAMES
from nilm_metadata import *
from nilmtk.dataset import DataSet
from nilmtk.building import Building

# Column name mapping

columnNameMapping = {'V': ('voltage', ''),
                     'I': ('current', ''),
                     'f': ('frequency', ''),
                     'DPF': ('pf', 'd'),
                     'APF': ('power factor', 'apparent'),
                     'P': ('power', 'active'),
                     'Pt': ('energy', 'active'),
                     'Q': ('power', 'reactive'),
                     'Qt': ('energy', 'reactive'),
                     'S': ('power', 'apparent'),
                     'St': ('energy', 'apparent')}


def _get_module_directory():
    # Taken from http://stackoverflow.com/a/6098238/732596
    path_to_this_file = dirname(getfile(currentframe()))
    if not isdir(path_to_this_file):
        encoding = getfilesystemencoding()
        path_to_this_file = dirname(unicode(__file__, encoding))
    if not isdir(path_to_this_file):
        abspath(getsourcefile(lambda _: None))
    if not isdir(path_to_this_file):
        path_to_this_file = getcwd()
    assert isdir(path_to_this_file), path_to_this_file + ' is not a directory'
    return path_to_this_file


def convert(inputPath, hdfFilename):  # , metadataPath='/'):
    '''
    Parameters: 
    -----------
    inputPath: str
            The path of the directory where all the csv files are supposed to be stored
    hdfFilename: str
            The path of the h5 file where all the standardized data is supposed to go. The path should refer to a particular file and not just a random directory in order for this to work.

    '''
    files = [f for f in listdir(inputPath) if isfile(join(inputPath, f)) and '.csv' in f and '.swp' not in f]
    files.sort()
    assert isdir(inputPath)
    store = HDFStore(hdfFilename)
    for i, csv_file in enumerate(files):  # range(len(files)):
        # sent=files[i]
        key = Key(building=1, meter=(i + 2))
        print('Loading file #', (i + 1), ' : ', csv_file, '. Please wait...')
        fp = pd.read_csv(join(inputPath, csv_file))
        fp.TS = fp.TS.astype('int')
        fp.index = pd.to_datetime((fp.TS.values * 1e9).astype(int), utc=True)
	fp=fp.tz_convert('Asia/Kolkata')
        fp = fp.drop('TS', 1)
        fp.rename(columns=lambda x: columnNameMapping[x], inplace=True)
        fp.columns.set_names(LEVEL_NAMES, inplace=True)
        fp = fp.convert_objects(convert_numeric=True)
        fp = fp.dropna()
        fp = fp.astype(np.float32)
        store.put(str(key), fp, format='Table')
        store.flush()
        print("Done with file #", (i + 1))
    store.close()
    metadataPath = join(_get_module_directory(), 'metadata')
    print('Processing metadata...')
    convert_yaml_to_hdf5(metadataPath, hdfFilename)
convert('/Users/rishi/Documents/Master_folder/IIITD/5th_semester/Independent_Project/AMPds/electricity', '/Users/rishi/Documents/Master_folder/IIITD/5th_semester/Independent_Project/AMPds/electricity/store.h5')
