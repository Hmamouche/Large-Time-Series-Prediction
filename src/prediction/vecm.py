#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# Author: Youssef Hmamouche

import sys, os, glob
import numpy as np
import pandas as pd
from statsmodels.tsa.vector_ar.vecm import VECM
from joblib import Parallel, delayed
sys.path.append ('src')
from tools.csv_helper import *
from pmdarima.arima import auto_arima

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
def vecm_one_target (X, nbre_preds, p):

    """
    Predict an array X with vecm model
    X: np array where the first column repesent the target variable
    nbre_preds: number of predictions
    p: lag parameter
    """

    predictions = []

    for j in range(0, nbre_preds):

        X_train = X [0 : (X. shape[0] - nbre_preds + j),:]
        try:
            model = VECM (X_train, k_ar_diff = p, deterministic = "co")
            model = model. fit ()
            yhat = model.predict (steps = 1)
            predictions. append (yhat[0,0])
        except:
            #print ("VECM failed for this variable, we will try a p= 1")
            try:
                model = VECM (X_train, k_ar_diff = 1, deterministic = "co")
                model = model. fit ()
                yhat = model.predict (steps = 1)
                predictions. append (yhat[0,0])
            except:
                print ("Still does not work")
                return pd.DataFrame ()

    return pd.DataFrame (predictions)

#########################################################
def predictbase (fname, output_directory, reset = 0):
    """
    Predict a csv file where the target variable is in the first column
    """

    fname_ = fname.split('/')[-1]
    if output_directory[-1] == '/':
        output_directory = output_directory[:-1]

    out_fname = output_directory + "/VECM_" + fname_

    X_train = read_csv_and_metadata(fname)
    meta_header = X_train.meta_header
    nbre_preds = int (meta_header['number_predictions'][0])
    p = int (meta_header['lag_parameter'][0])
    horizon = int (meta_header['horizon'][0])
    target_names =  (meta_header['predict'])

    if not os.path.exists(out_fname):
        n_predictions = 0

    else:
        predictions = read_csv_and_metadata(out_fname)
        n_predictions = predictions.shape [0]

    if n_predictions < nbre_preds or reset == 1:
        #print ("Processing file %s" % out_fname)
        predictions = vecm_one_target (X_train.values, nbre_preds, p)

        if predictions. empty:
            #print ("This file was not processed")
            return

        predictions = pd.DataFrame (np.array (predictions), columns = ["Predictions"])

        # Put meta-data for the output file
        predictions.meta_header = X_train.meta_header
        predictions.meta_header['predict_model'] = ["VECM"]
        predictions.meta_header['predict'] = [target_names[0],]

        write_csv_with_metadata(predictions, out_fname)
    else:
        print ( bcolors.OKGREEN + "File %s already exist" % out_fname + bcolors.ENDC)
    #print ("Done...")


###########################################################
if __name__ == "__main__":

    parser = argparse. ArgumentParser ()
    parser. add_argument ("in_files", help = "path the folder that contains the csv files to predict")
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
