#!/usr/local/bin/python
# -*- coding: utf-8 -*-

# Author: Youssef Hmamouche


from __future__ import print_function
import sys

from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler

from sklearn import linear_model

from math import sqrt

from joblib import Parallel, delayed

import numpy as np
import pandas as pd
import pprint

import os

sys.path.append ('src')
from tools.csv_helper import *
from tqdm import tqdm

sh_models = {
    "BayeRidge" :linear_model.BayesianRidge(),
    "Lasso1" :linear_model.Lasso(alpha = 0.1),
    #"Lasso2" :linear_model.Lasso(alpha = 0.2),
    #"Lasso3" :linear_model.Lasso(alpha = 0.3),
    "Ridge1" :linear_model.Ridge(alpha = 0.1),
    #"Ridge2" :linear_model.Ridge(alpha = 0.2),
    #"Ridge3" :linear_model.Ridge(alpha = 0.3),
}


##########################
class toSuppervisedData:
    targets = np.empty([0,0],dtype=float)
    data = np.empty([0,0],dtype=float)

    ## constructor
    def __init__(self, X, p):
        self.targets = self.targets_decomposition (X,p)
        self.data = self.matrix_decomposition (X,p)

    ## p-decomposition of a vector
    def vector_decomposition (self,x,p):
        n = len(x)
        output = np.empty([n-p,p],dtype=float)
        for i in range (n-p):
            for j in range (p):
                output[i,j] = x[i+j]
        return output
    #########
    # p-decomposition of a target
    def target_decomposition (self,x,p):
        n = len(x)
        output = np.empty([n-p,1],dtype=float)
        for i in range (n-p):
            output[i] = x[i+p]
        return output
    ########
    # p-decomposition of a matrix
    def matrix_decomposition (self,x,p):
        output = np.empty([0,0],dtype=float)
        out = np.empty([0,0],dtype=float)
        for i in range(x.shape[1]):
            out = self.vector_decomposition(x[:,i],p)
            if output.size == 0:
                output = out
            else:
                output = np.concatenate ((output,out),axis=1)

        return output
    # extract all the targets decomposed
    def targets_decomposition (self,x,p):
        output = np.empty([0,0],dtype=float)
        out = np.empty([0,0],dtype=float)
        for i in range(x.shape[1]):
            out = self.target_decomposition(x[:,i],p)
            if output.size == 0:
                output = out
            else:
                output = np.concatenate ((output,out),axis=1)
        
        return output
######################################################
def regularized_VAR (X, targets, nbre_preds, model_):

    targets = np.array (targets)
    
    predictions = np.empty ([nbre_preds, 1])
    #print (targets.shape[0])
    #
    #exit (1)
   # reals = targets[targets.shape[0] - nbre_preds:targets.shape[0],:]
    #exit (1)
    limit = X.shape[0] - nbre_preds
    X_train, test = X[0:limit], X[limit:X.shape[0]]
    Y_train = targets [0:limit]
    
    model = model_.fit (X_train, Y_train)

    for j in range(0, nbre_preds):
        limit = X.shape[0] - nbre_preds + j
        train, X_test = X[limit-1:limit], X[j:limit+1]
        target, Y_test = targets[limit-1:limit], targets[j:limit+1]

        # prediction
        yhat = model.predict (train)
        predictions [j] = yhat
            
        # update the model: rolling window learning
        model = model.fit (X_test, Y_test)
    
    return pd.DataFrame (predictions)

#########################################################

def predictbase (fname, output_directory, reset = 0):
    fname_ = fname.split('/')[-1].split ('.')[0]
    print ("Processing: %s \n" % fname_)
    data = read_csv_and_metadata(fname)
    data = data.dropna(axis=1, how='all')
    #print (data.head (2))
    #exit (1)
    meta_header = data.meta_header
    nbre_preds = int (meta_header['number_predictions'][0])
    targets = meta_header['predict']
    

    p = int (meta_header['lag_parameter'][0])
    model = toSuppervisedData (data.values, p)
    X = model.data
    targets_ = model.targets
    
    for model in sh_models:
        for target in targets:
            out_fname = output_directory + "/" + model + "_" + target + "_" + model + "_t_K=All.csv"
            print ("Processing the column: " + target)
            try:
                predictions = regularized_VAR (X, data.ix[p:,target].values, nbre_preds, sh_models[model])
                predictions.meta_header = data.meta_header
                predictions.meta_header['predict_model'] = ["VAR"+ model]
                predictions.meta_header['method'] = [model + "(n_components=all)"]
                predictions.meta_header['predict'] = [target,]
                write_csv_with_metadata(predictions, out_fname)

            except Exception as e:
                print (e)


###########################################################
def main ():

    fnames, output_directory = sys.argv[1:-1], sys.argv[-1]
    predictbase (fnames[0], output_directory)

if __name__ == "__main__":
    main()





