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
def merge_daily (src_data_path, dst_data_path):
    
    print ("Merging files for each idplant")
    idplant = ["id_1","id_2","id_3"]
    #F = open("minMax",”w”)
    
    for id in tqdm(idplant):
        all = pd.DataFrame
        
        predictors_fnames = find_filenames (src_data_path, id)
    
        predictors_list = dict ()
        target_fname = ""

        
        for fname in predictors_fnames:
            if "power" in fname:
                predictors_fnames.remove (fname)
                target_fname = fname
                break


        # Store all dataframes in dictionary
        for fname in predictors_fnames:
            df = read_csv_and_metadata (os.path.join(src_data_path, fname))
            predictors_list[fname.split('.')[0]] = df.values

        # traget variable
        power = read_csv_and_metadata (os.path.join(src_data_path, target_fname)).values
        #power =  pd.read_csv(os.path.join(src_data_path, target_fname), sep = ';').values

        # Construct predictores varible for each hour of power variable
        for i in range(0,19):
            header_ = ['power_hour_' + str(i+2)]
            predictors_ = power[:,i:i+1]
            
            for df_ in predictors_list:
                header_ = np.concatenate ((header_, [df_+"_hour_" + str(i+2)]), axis = 0)
                predictors_ = np.concatenate ((predictors_, predictors_list[df_][:,i:i+1]),axis=1)
            
            #normalize (predictors_)
            
            p_df = pd.DataFrame(predictors_)
            p_df.meta_header = {}
            p_df.meta_header['predict'] = ['power_hour_' + str(i+2)]
            #p_df.meta_header['method'] = ['All_variables(n_components=9)']
            p_df.meta_header['name_prefix'] = ['PV_competition' +"_" + id]
            p_df.meta_header['description'] = ['Multi-Plant Photovoltaic Energy Forecasting Challenge']
            p_df.meta_header['lag_parameter'] = ['0']
            p_df.meta_header['number_predictions'] = ['90']
            p_df.meta_header['horizon'] = ['1']
            p_df.meta_header['prediction_type'] = ['rolling']

  
            write_csv_with_metadata(p_df, os.path. join(dst_data_path, 'train_%s_houre_%d.csv' % (id, i+2)), header = header_)
                
        print (".... Ok for id: %s" % id)
    print("Done...")

###########################################

def merge_data_daily(src_data_path, dst_data_path):
    
    idplant = ["id_1","id_2","id_3"]
    id = idplant[0]
    for id in idplant:
        file_names = find_filenames (src_data_path, id)

        all_variables = pd.DataFrame()
        header_ = []
        for file in tqdm(file_names):
            folder = os.path.join(src_data_path, file)
            df = read_csv_and_metadata(os.path.join(folder), sep = ';')
            header_.extend(df.columns.values)
        
            if all_variables.empty:
                all_variables = df
            else:
                all_variables = pd.concat ([all_variables,df], axis = 1)
    
        all_variables.meta_header = {}
        targets = []
        for j in range(2,21):
            targets.append ('power_hour_' + str(j))
        
        all_variables.meta_header['predict'] = targets
        all_variables.meta_header['method'] = ['All_variables(n_components=9)']
        all_variables.meta_header['name_prefix'] = ['PV_competition' +"_" + id]
        all_variables.meta_header['description'] = ['Multi-Plant Photovoltaic Energy Forecasting Challenge']
        all_variables.meta_header['lag_parameter'] = ['0']
        all_variables.meta_header['number_predictions'] = ['90']
        all_variables.meta_header['horizon'] = ['1']
        all_variables.meta_header['prediction_type'] = ['rolling']

        write_csv_with_metadata (all_variables,os.path.join(dst_data_path, "%s.csv" % id ), header = header_, index=False, sep = ';')
    
    print("Done...")
###########################################


if not os.path.exists("id_daily_same_houre"):
   os.makedirs("id_daily_same_houre")

merge_daily ("multi_plants_daily/", "id_daily_same_houre")

merge_data_daily ("id_daily_same_houre/", "")
