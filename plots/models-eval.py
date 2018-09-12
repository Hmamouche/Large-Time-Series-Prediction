# Author: Youssef Hmamouche
# This file compute Prediction Models Applicability

import pandas as pd
import numpy as np
import seaborn as sns; sns.set()
import matplotlib.pyplot as plt
import os
import sys

sys.path.insert(0, 'src/tools')

from csv_helper import *

#------------------------------#
#-------- COLORS CLASS --------#
#------------------------------#
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

#------------------------------#
#------  REDUCED NAMES  -------#
#------------------------------#
def reduce_methods_names (methods):
    reduced_cols = []
    for method in methods:
        if 'Kernel' in method:
            reduced_cols.append ('KPCA')
        elif 'BayeRidge' in method:
            reduced_cols.append ('BayesianRidge')
        elif 'PCA' in method and 'Kernel' not in method:
            reduced_cols.append ('PCA')
        elif 'Hits_te' in method or 'Hits_TE' in method:
            reduced_cols.append ('PEHAR-te')
        elif 'Hits_g' in method:
            reduced_cols.append ('PEHAR-gg')
        elif 'Auto' in method:
            reduced_cols.append ('Arima')
        elif 'Factor' in method:
            reduced_cols.append ('FactA')
        elif 'GFS_te' in method:
            reduced_cols.append ('GFSM-te')
        elif 'GFS_gr' in method:
            reduced_cols.append ('GFSM-gg')
        elif 'Ridge1' in method and 'Ridge' not in reduced_cols:
            reduced_cols.append ('Ridge')
        elif 'Lasso1' in method and 'Lasso' not in reduced_cols:
            reduced_cols.append ('Lasso')
        else:
            reduced_cols.append (method)
    return reduced_cols


#-------------------------------------------------#
#-------------    MAIN FUNCTION    ---------------#
#-------------------------------------------------#
def main (xls, cols, target_names, reduced_cols, data_name):
    
    
    measures = ["rmse", "MASE"]
    
    for measure in measures:
        file = data_name + "_" + measure + "_Models.csv"
        matrix_pf = pd.DataFrame (np.zeros ((len (reduced_cols), len (reduced_cols))))
        df = pd.DataFrame ()
        
        matrix = {}
        for method in cols:
            matrix [method] = [0 for i in range (len (cols))]
    
        number_of_variables = {}
        for method in cols:
            number_of_variables [method] = [0 for i in range (len (cols))]
        
        
        for target_name in target_names:
            df = pd.DataFrame ()
            for name in sheet_names:
                t_name = name.split('_')[0]
                if target_name != t_name:
                    continue
                df = pd.concat ([df, pd.read_excel(xls, name)], axis = 0)
         
            if df.empty == True:
                continue

            rmse_values = df[['predict',measure]]
            rmse_values = rmse_values.groupby(['predict']).min()
            rmse_values = rmse_values.sort_values(by=[measure])
            INDEX = rmse_values.index
            
            for i in range (len (INDEX)):
                matrix [INDEX[i]][i] = int (matrix [INDEX[i]][i]) + 1


        # Dict to DaraFrame
        for i in range (len (reduced_cols)):
            for j in range (len (reduced_cols)):
                matrix_pf.iloc [i,j] = matrix [cols[i]][j]

        matrix_pf.index = reduced_cols
        matrix_pf.to_csv ("plots/csv/" + file)
        #print (matrix_pf)

#-------------------------------------------------#
#                    MAIN                         #
#-------------------------------------------------#
if __name__ == "__main__":
    
    if len (sys.argv) < 2:
        print ( bcolors.FAIL + "Unsufficient arguments!" + bcolors.ENDC)
        exit (1)

    #------ READ DATA ---------#
    file_name = sys.argv[1]
    data_name = file_name.split('/')[-1].split('.')[0]


    #------ READ TARGET NAMES ---------#
    target_names = read_csv_and_metadata (file_name).meta_header['predict']

    #------ READ SHEET NAMES ---------#
    if os.path.exists ("results/evaluation/" + data_name + "/" + data_name + ".xlsx"):
        xls = pd.ExcelFile("results/evaluation/" + data_name + "/" + data_name + ".xlsx")
    elif os.path.exists ("results/evaluation/" + data_name + "/" + data_name + ".xls"):
        xls = pd.ExcelFile("results/evaluation/" + data_name + "/" + data_name + ".xls")
    else:
    	print ("Error in reading the file: " + data_name)
    sheet_names = xls.sheet_names
    
    df = pd.read_excel(xls, sheet_names[0])
    cols, counts = np.unique(df['predict'], return_counts=True)
    
    for i in range(len (sheet_names)):
        df = pd.read_excel(xls, sheet_names[i])
        cols_ = np.unique(df['predict'])
        cols = np.concatenate ((cols, cols_), axis = 0)

    cols = np.unique(cols)

    #------ CONSTRUCT REDUCED NAMES ---------#
    reduced_cols = reduce_methods_names (cols)
    #print (reduced_cols)

    #------------- MAIN ---------------#
    main (xls, cols, target_names, reduced_cols, data_name)



























