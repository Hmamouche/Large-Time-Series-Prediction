# -*- coding: utf-8 -*-

import os
import pandas as pd
from tqdm import tqdm
import numpy as np

from os import listdir

from ../../src.tools.csv_helper import *

def find_csv_filenames( path_to_dir, suffix=".csv" ):
    filenames = listdir(path_to_dir)
    return [ filename for filename in filenames if filename.endswith( suffix ) ]

def find_filenames( path_to_dir, prefix="" ):
    filenames = listdir(path_to_dir)
    return [ filename for filename in filenames if filename.startswith( prefix ) ]

## reconstruct each time series
def separate_data(src_data_path, dst_data_path):
    print ("Separate and structure files")
    file_names = find_csv_filenames (src_data_path)
    for file in tqdm(file_names):
        #print (file)
        folder = os.path.join(src_data_path, file)
        df = pd.read_csv(os.path.join(folder), sep = ';')
        
        array = df.values
        
        df1 = np.empty([0,0],dtype=float)
        df2 = np.empty([0,0],dtype=float)
        df3 = np.empty([0,0],dtype=float)
        
        for i in range(0,len(df)):
            if array[i,0] == 1:
                if df1.size == 0:
                    df1 = array[i,2:]
                else:
                    df1 = np.concatenate ((df1,array[i,2:]),axis=0)

            if array[i,0] == 2:
                if df2.size == 0:
                    df2 = array[i,2:]
                else:
                    df2 = np.concatenate ((df1,array[i,2:]),axis=0)
    
            if array[i,0] == 2:
                if df3.size == 0:
                    df3 = array[i,2:]
                else:
                    df3 = np.concatenate ((df1,array[i,2:]),axis=0)

        pd.DataFrame(df1).to_csv(os.path.join(dst_data_path, 'plant_1%s' % file), header = [file.split(".")[0]], index=False, sep = ';')
        pd.DataFrame(df2).to_csv(os.path.join(dst_data_path, 'plant_2%s' % file),  header = [file.split(".")[0]], index=False, sep = ';')
        pd.DataFrame(df3).to_csv(os.path.join(dst_data_path, 'plant_3%s' % file),  header = [file.split(".")[0]], index=False, sep = ';')

    print("Done...")

## Merger target and predictors time series in one file
def merge_all(src_data_path, dst_data_path):
    print ("Merging files for each idplant")
    idplant = ["plant_1","plant_2","plant_3"]
    
    
    for id in tqdm(idplant):
        all = pd.DataFrame
        if os.path.exists(id):
            os.remove(id)
        
        file_names = find_filenames (src_data_path, id)
        #print (file_names)
    
        for file in file_names:
            folder = os.path.join(src_data_path, file)
            df = pd.read_csv(os.path.join(folder), sep = ';')
            if all.empty:
                all = df
            else:
                all = pd.concat([all, df], axis = 1)
        all.meta_header = {}
        all.meta_header['predict'] = ["plant-power"]
        write_csv_with_metadata(all, os.path. join(dst_data_path,'%s.csv' % id))
        print("Done...")

###########################################
if not os.path.exists("multi_plants_hourly"):
    os.makedirs("multi_plants_hourly")

if not os.path.exists("id_plants_data"):
    os.makedirs("id_plants_data")

separate_data ("data", "multi_plants_hourly")

merge_all ("multi_plants_hourly", "id_plants_hourly")



