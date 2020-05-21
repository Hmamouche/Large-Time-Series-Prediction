#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# Author: Youssef Hmamouche

import sys, os, glob
import numpy as np
import pandas as pd
from pmdarima.arima import auto_arima
from joblib import Parallel, delayed
sys.path.append ('src')
from tools.csv_helper import *

import argparse

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

######################################################
def arima_one_target (X, nbre_preds, p):

    """
    Predict an array X with vecm model
    X: np array where the first column repesent the target variable
    nbre_preds: number of predictions
    p: lag parameter
    """

    predictions = []

    for j in range(0, nbre_preds):

        X_train = X [0 : (X. shape[0] - nbre_preds + j)]
        model = auto_arima (X_train, start_p = p,  max_p = p)
        yhat = model. fit_predict (X_train, n_periods = 1)
        predictions. append (yhat[0])

    return pd.DataFrame (predictions)

#########################################################
def predictbase (fname, output_directory, reset = 0):
    """
    Predict targets variables with arima model of a given dataset
    """

    fname_ = fname.split('/')[-1].split ('.')[0]
    print ("Processing: %s \n" % fname_)
    data = read_csv_and_metadata(fname)
    data = data.dropna(axis=1, how='all')

    meta_header = data.meta_header
    nbre_preds = int (meta_header['number_predictions'][0])
    targets = meta_header['predict']
    p = int (meta_header['lag_parameter'][0])

    for target in targets:
        print ("Processing the column: " + target)
        out_fname = output_directory + "/ARIMA_" + target + "_t_K=All.csv"

        # check if file already processed
        if not os.path.exists(out_fname):
            n_predictions = 0

        else:
            predictions = read_csv_and_metadata(out_fname)
            n_predictions = predictions.shape [0]

        if n_predictions < nbre_preds or reset == 1:
            try:
                predictions = arima_one_target (data.loc[:,target].values, nbre_preds, p)
            except Exception as e:
                print (e)
            predictions.meta_header = data.meta_header
            predictions.meta_header['predict_model'] = ["Auto_Arima"]
            predictions.meta_header['method'] = ["univariate_mode"]
            predictions.meta_header['predict'] = [target]
            write_csv_with_metadata(predictions, out_fname)


        else:
            print ( bcolors.OKGREEN + "File %s already exist" % out_fname + bcolors.ENDC)
        print ("Done...")


###########################################################
if __name__ == "__main__":

    parser = argparse. ArgumentParser ()
    parser. add_argument ("in_files", help = "sv file of the folder that contains the csv files to predict")
    parser. add_argument ("out_dir", help = "output output_directory")
    args = parser.parse_args()

    fnames_path, output_directory = sys.argv[1], sys.argv[-1]
    if (args.in_files.split ('.')[-1] == 'csv'):
        fnames = [args.in_files]
    else:
        if args.in_files[-1] != '/':
            args.in_files += "/"
        fnames = glob.glob (args.in_files+"*.csv")

    Parallel(5)(delayed(predictbase)(fname, output_directory, reset = 0) for fname in fnames)
