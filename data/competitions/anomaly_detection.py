# -*- coding: utf-8 -*-

import os
import pandas as pd
import numpy as np

from os import listdir

from tools.csv_helper import *

def find_csv_filenames( path_to_dir, suffix=".csv" ):
    filenames = listdir(path_to_dir)
    return [ filename for filename in filenames if filename.endswith( suffix ) ]

def find_filenames( path_to_dir, prefix="" ):
    filenames = listdir(path_to_dir)
    return [ filename for filename in filenames if filename.startswith( prefix ) ]


def normalize (M, min, max):
    M = (M-min)/(max-min)
    '''for i in range(M.shape[1]):
        for j in range(M.shape[0]):
            M[j,i] = (M[j,i] - min) / (max - min)'''
    return M
#################

file_names = find_csv_filenames ("data")
src_data_path = "data/"



#### eliminating outliers
'''for file in file_names:
    
    print (file)
    folder = os.path.join(src_data_path, file)
    df = pd.read_csv(os.path.join(folder), sep=';')
    df_ = df.drop (df.columns[[0,1]], axis=1)
    df_stacked = df_.stack ()
    mean = df_stacked.mean()
    Q1 = df_stacked.quantile (q=0.25)
    Q3 = df_stacked.quantile (q=0.75)
    
    if file == "plant-temperature.csv":
        k = 2.5
    else:
        if file == "weather-windspeed.csv":
            k = 10
        else:
            k = 3.5
    LB = Q1 - k * (Q3 - Q1)
    UB = Q3 + k * (Q3 - Q1)

    values = df.values
    count  = 0
    for i in range(0, values.shape[0]):
       for j in range(2, values.shape[1]):
           if float(values[i,j]) > UB or float(values[i,j]) < LB:
               print (values[i,j])
               count = count + 1
               if i > 1:
                   values[i,j] = values[i-1,j]
               else:
                   values[i,j] = values[i,j+1]


    df_whithout_outliers = pd.DataFrame (values)
    df_whithout_outliers.meta_header = {}
    write_csv_with_metadata(df_whithout_outliers, os.path.join(src_data_path, file), header = df.columns)'''

### Normalisation
file_names = find_csv_filenames ("data")
src_data_path = "data/"

min = {
    "plant-power.csv" : 0.0,
    "plant-irradiance.csv" : 0.0,
    "plant-temperature.csv" : -3.0,
    "weather-cloudcover.csv" : 0.00,
    "weather-dewpoint.csv" : -7.18,
    "weather-humidity.csv" : 0.21,
    "weather-pressure.csv" : 983.50,
    "weather-temperature.csv" : -2.00,
    "weather-windbearing.csv" : 0.00,
    "weather-windspeed.csv" : 0.00
}

max = {
    "plant-power.csv" : 777.00,
    "plant-irradiance.csv" : 1337.00,
    "plant-temperature.csv" : 52.00,
    "weather-cloudcover.csv" : 1.00,
    "weather-dewpoint.csv" : 22.19,
    "weather-humidity.csv" : 1.00,
    "weather-pressure.csv" : 1032.42,
    "weather-temperature.csv" : 36.00,
    "weather-windbearing.csv" : 359.00,
    "weather-windspeed.csv" : 21.60
}

for file in file_names:
    min_ = min[file]
    max_ = max[file]
    print (min_, max_)
    folder = os.path.join(src_data_path, file)
    df = pd.read_csv(os.path.join(folder), sep=';')
    df_values = df.drop (df.columns[[0,1]], axis=1)

    values = normalize (df_values.values, float(min_), float(max_))
    
    df_normalized = pd.DataFrame (values)
    index = df[df.columns[0:2]]
    df_normalized = pd.concat ((index,df_normalized), axis = 1)
    df_normalized.meta_header = {}
    write_csv_with_metadata(df_normalized, os.path.join(src_data_path, file), header = df.columns)



















