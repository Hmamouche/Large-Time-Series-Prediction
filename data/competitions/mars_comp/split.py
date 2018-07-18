# -*- coding: utf-8 -*-

import os
import pandas as pd
from tqdm import tqdm
import numpy as np

from os import listdir

from utils.read_csv import *

###########################################
def find_csv_filenames( path_to_dir, suffix=".csv" ):
    filenames = listdir(path_to_dir)
    return [ filename for filename in filenames if filename.endswith( suffix ) ]

###########################################
def find_filenames( path_to_dir, prefix="" ):
    filenames = listdir(path_to_dir)
    return [ filename for filename in filenames if filename.startswith( prefix ) ]

##################################
def normalize (M):
    minMax = np.empty ([M.shape[1], 2])
    for i in range(M.shape[1]):
        #print (M[:,i])
        max = np.max(M[:,i])
        min = np.min(M[:,i])
        minMax[i,0] = min
        minMax[i,1] = max
        
        for j in range(M.shape[0]):
            M[j,i] = (M[j,i] - min) / (max - min)

    return minMax

###########################################
def separate_data_hourly(src_data_path, dst_data_path):

    print ("Starting splitting data")
    df = read_csv_and_metadata(src_data_path)
    df = df.set_index('ut_ms')
        
    targets = df.columns[0:33]
    predictors = df.columns[33:]
    print (targets)
    print (predictors)
    
    for target in targets:
        header_ = []
        header_.append (target)
        header_.extend (predictors)
        df_v = pd.concat ((df[target], df[predictors]), axis = 1)
        #df_v = df_v.set_index('ut_ms')
    

        folder = dst_data_path + target + ".csv"
        df_v.meta_header = {}
        df_v.meta_header['predict'] = [target]
 
        df_v.meta_header['name_prefix'] = ['mars_competition_measure_'+target]
        df_v.meta_header['description'] = ['Mars Express Forecasting Challenge']
        df_v.meta_header['lag_parameter'] = ['0']
        df_v.meta_header['number_predictions'] = ['176173']
        df_v.meta_header['horizon'] = ['1']
        df_v.meta_header['prediction_type'] = ['rolling']
        write_csv_with_metadata (df_v, folder, header = header_ , index=False, sep = ';')
    
    print("Done...")


###########################################
if not os.path.exists("data_per_variable"):
   os.makedirs("data_per_variable")

separate_data_hourly ("data/train.csv", "data_per_variable/")

