
from __future__ import print_function, division
import numpy as np
import pandas as pd
from os import *
from os.path import *


from pylab import rcParams
import matplotlib.pyplot as plt

rcParams['figure.figsize'] = (16, 8)


import nilmtk
from nilmtk import DataSet, TimeFrame, MeterGroup, HDFDataStore
from nilmtk.disaggregate import CombinatorialOptimisation
from nilmtk.utils import print_dict
from nilmtk.metrics import f1_score


import pandas as pd
import numpy as np
from pandas import *
from os.path import *
from os import *
from nilmtk.datastore import Key
from nilmtk.measurement import LEVEL_NAMES
from nilmtk.utils import check_directory_exists
from nilm_metadata import *
from inspect import currentframe, getfile, getsourcefile
from sys import getfilesystemencoding


import warnings
warnings.filterwarnings("ignore")




def test_all(path_to_directory):
    '''
    path_to_directory: Contains the h5 files on which the tests are supposed to be run
    '''

    check_directory_exists(path_to_directory)

#files=[f for f in listdir(path_to_directory) and '.h5' in f and '.swp' not in f]
    files = [f for f in listdir(path_to_directory) if isfile(join(path_to_directory, f)) and
         '.h5' in f and '.swp' not in f]
    files.sort()

    print ("Datasets collected and sorted. Processing...")


    try:
        for i, file in enumerate(files):
            current_file=DataSet(join(path_to_directory, file))
            print ("Printing metadata for current file...done.")
            print_dict(current_file.metadata)
            print (" Loading file # ", i, " : ", file, ". Please wait.")
            for building_number in range(1, len(current_file.buildings)+1):
    #Examine metadata for a single house
                print ("Metadata for current file: ")
                print_dict(current_file.buildings[building_number].metadata)


                print ("Examining sub-metered appliances...")
                elec=current_file.buildings[building_number].elec
                print ("MeterGroup object of current file...")
                print (elec)
                print (elec.appliances)

                print ("Plotting wiring hierarchy of meters....")
                elec.draw_wiring_graph()

                appliance_type="fridge"
    #TODO : appliance_type should cycle through all appliances and check for each of them. For this, use a list.
                selected_appliance=nilmtk.global_meter_group.select_using_appliances(type=appliance_type)
                appliance_restricted = MeterGroup(selected_appliance.meters[:5])
                if ((appliance_restricted.proportion_of_upstream_total_per_meter()) is not None):
                    proportion_per_appliance = appliance_restricted.proportion_of_upstream_total_per_meter()


                    proportion_per_appliance.plot(kind='bar');
                    plt.title('Appliance energy as proportion of total building energy');
                    plt.ylabel('Proportion');
                    plt.xlabel('Appliance (<appliance instance>, <building instance>, <dataset name>)');
                    selected_appliance.select(building=building_number).total_energy()
                    selected_appliance.select(building=61).plot();


                    appliance_restricted = MeterGroup(fridges.meters[5])
                    daily_energy = pd.DataFrame([meter.average_energy_per_period(offset_alias='D')
                                     for meter in appliance_restricted.meters])

                    daily_energy.plot(kind='hist');
                    plt.title('Histogram of daily ', selected_appliance, ' energy');
                    plt.xlabel('energy (kWh)');
                    plt.ylabel('Occurences');
                    plt.legend().set_visible(False)

                    current_file.store.window=TimeFrame(start='2012-04-01 00:00:00-05:00', end='2012-04-02 00:00:00-05:00')
                    elec.plot();

                    fraction = elec.submeters().fraction_per_meter().dropna()

                    labels = elec.get_appliance_labels(fraction.index)
                    plt.figure(figsize=(8,8))
                    fraction.plot(kind='pie', labels=labels);

                    elec.select_using_appliances(category='heating')
                    elec.select_using_appliances(category='single-phase induction motor')


                    co = CombinatorialOptimisation()
                    co.train(elec)

                    for model in co.model:
                        print_dict(model)


                    disag_filename = join(data_dir, 'ampds-disag.h5')
                    output = HDFDataStore(disag_filename, 'w')
                    co.disaggregate(elec.mains(), output)
                    output.close()



                    disag = DataSet(disag_filename)








                    disag_elec = disag.buildings[building_number].elec

                    f1 = f1_score(disag_elec, elec)
                    f1.index = disag_elec.get_appliance_labels(f1.index)
                    f1.plot(kind='bar')
                    plt.xlabel('appliance');
                    plt.ylabel('f-score');
                    disag_elec.plot()

                    disag.store.close()
    except AttributeError:
        print ("AttributeError occured while executing. This means that the value returned by  proportion_per_appliance = appliance_restricted.proportion_of_upstream_total_per_meter() is None")





test_all('/Users/rishi/Documents/Master_folder/IIITD/5th_semester/Independent_Project/nilmtk/data/Location_of_h5')

