# -*- coding: utf-8 -*-

import os
import pandas as pd
from tqdm import tqdm
import numpy as np

from os import listdir

from tools.csv_helper import *

###########################################
def find_csv_filenames( path_to_dir, suffix=".csv" ):
    filenames = listdir(path_to_dir)
    return [ filename for filename in filenames if filename.endswith( suffix ) ]

###########################################
def find_filenames( path_to_dir, prefix="" ):
    filenames = listdir(path_to_dir)
    return [ filename for filename in filenames if filename.startswith( prefix ) ]

###########################################
def separate_data_hourly(src_data_path, dst_data_path):
    print ("Separate and structure files")
    file_names = find_csv_filenames (src_data_path)
    for file in tqdm(file_names):
        #print (file)
        folder = os.path.join(src_data_path, file)
        df = pd.read_csv(os.path.join(folder), sep = ';')
        
        array = df.values
        
        for id in range(1,4):
            dfi = []
            header_ = []

            for i in range(0,len(df)):
                if array[i,0] == id:
                    dfi.append(array[i,2:])

            for h in range(2,21):
                    header_.append ("hour%s" % h)


            folder = "id_" + str(id) + "_" + file
            
            output = pd.DataFrame(dfi)
            output.meta_header = {}
            output.header = []
            
            output.meta_header['description'] = ["daliy observations of %s for plant %d" % (file.split(".")[0] ,id)]

            target_name = [("id_" + str(id) + "_" + file.split(".")[0])]
            output.header = np.concatenate ((target_name, header_), axis = 0)
            
            #print (output.header)
            write_csv_with_metadata (output, os.path.join(dst_data_path, folder), header = header_ , index=False, sep = ';')
    
    print("Done...")



###########################################
if not os.path.exists("multi_plants_daily"):
   os.makedirs("multi_plants_daily")

separate_data_hourly ("data/", "multi_plants_daily")

