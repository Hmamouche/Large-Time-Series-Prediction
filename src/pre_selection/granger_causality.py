import numpy as np
import pandas as pd
import argparse, sys
from statsmodels.tsa.stattools import grangercausalitytests
from sklearn import preprocessing

sys.path.append ("src")
from tools.csv_helper import *

# Function that generates a transfer entropy matrix using the JDIT library
# The input data is the file name
def causality_matrix (dataRaw, lag):

    min_max_scaler = preprocessing. MinMaxScaler()
    data = min_max_scaler.fit_transform(dataRaw)

    n_Features = data. shape [1]
    gc_matrix = np.ndarray(shape=(n_Features,n_Features))

    for i in range (0,n_Features):
        for j in range (0,n_Features):
            if (i == j):
                gc_matrix[i,j] = 0
            else:
                X = data[:, [j,i]]
                #gc_matrix[i,j] = grangercausalitytests (X, maxlag = 4)
                try:
                    pvalue = grangercausalitytests (X, maxlag = [lag],  verbose = 0)[lag][0]["ssr_ftest"][1]
                    gc_matrix[i,j] = pvalue
                except:
                    print ("Granger test failed from %d to %d"%(i,j))
                    gc_matrix[i,j] = 0
    return gc_matrix

if __name__ == "__main__":
    parser = argparse. ArgumentParser ()
    parser. add_argument ("data", help = "Input data")
    parser. add_argument ("out_dir", help = "Output directory")
    parser. add_argument ("--all",action="store_true", help = "Weither to consider all observations or just the training set")
    args = parser. parse_args ()

    fname, output_directory = args.data, args.out_dir
    out_fname = output_directory + "/gc.csv"
    dataRaw = read_csv_and_metadata(fname)
    dataRaw = dataRaw.dropna(axis=1, how='all')

    lag = int(dataRaw.meta_header ["lag_parameter"][0])
    nb_predictions = int(dataRaw.meta_header ["number_predictions"][0])

    if not args.all:
        dataRaw = dataRaw.iloc [-nb_predictions:]

    gc_mat = causality_matrix (dataRaw. values, lag)
    out = pd.DataFrame(gc_mat, index=dataRaw.columns, columns=dataRaw.columns)
    out.meta_header = dataRaw.meta_header
    print (out)

    #df_in = read_csv_and_metadata(fname)
    write_csv_with_metadata(out, out_fname, index=True)
