#!/usr/local/bin/python
# -*- coding: utf-8 -*-

# Author: Youssef Hmamouche

from __future__ import print_function
import sys
import glob
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense
from math import sqrt

from joblib import Parallel, delayed

import numpy as np
import pandas as pd
import pprint

import os

sys.path.append ('src')
from tools.csv_helper import *


#------------------------------#
#-----+     COLORS      +------#
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

#-------------------------------------------------------------#
#----+     TRANSFORM THE DATA TO SUPPERISED STRUCTURE  +------#
#-------------------------------------------------------------#
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

    ## p-decomposition of a target
    def target_decomposition (self,x,p):
        n = len(x)
        output = np.empty([n-p,1],dtype=float)
        for i in range (n-p):
            output[i] = x[i+p]
        return output

    ## p-decomposition of a matrix
    def matrix_decomposition (self,x,p):
        output = np.empty([0,0],dtype=float)
        out = np.empty([0,0],dtype=float)
        for i in range(x.shape[1]):
            out = self.vector_decomposition(x[:,i],p)
            #print (out)
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
#--------------------------------#
#----+     NORMALIZE      +------#
#--------------------------------#
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

#========================================================================
class LSTM_MODEL:
    def __init__(self, lag):
        self. look_back = lag
        self. model = None

    def fit (self, X, Y, epochs = 30):
        X = np.array (X)
        new_shape = [X.shape[0], self.look_back, int (X.shape[1] / self.look_back)]
        X_reshaped = X.reshape (new_shape)

        self.model = Sequential()
        #self. model. add (LSTM (X_reshaped. shape [2], input_shape=(self. look_back , X_reshaped. shape [2]), dropout_W = 0.2))
        self. model. add (LSTM (units = X_reshaped. shape [2],  dropout = 0.2))
        #self. model. add (Dense(1, activation='sigmoid'))
        self.model.add(Dense(1, activation='relu'))
        self.model.compile (loss = 'mean_squared_error', optimizer = 'adam', metrics = ['mae'])

        self.model.fit (X_reshaped, Y,  epochs = epochs, batch_size = 1, verbose = 0, shuffle = False)

    def predict (self, X):
        X_reshaped = X.reshape(X.shape[0], self. look_back, int (X.shape[1] / self. look_back))
        preds = self. model. predict (X_reshaped, batch_size = 1). flatten ()
        return preds

    def update (self, X, Y, epochs):
        new_shape = [X.shape[0], self.look_back, int (X.shape[1] / self.look_back)]
        X_reshaped = X.reshape (new_shape)
        self.model.fit (X_reshaped, Y,  epochs = epochs, batch_size = 1, verbose = 0, shuffle = False)
        self.model.reset_states()


#--------------------------------------#
#----+     DENORMALIZATION      +------#
#--------------------------------------#
def inverse_normalize (M,minMax):
    for i in range(M.shape[0]):
        M[i] = M[i] * (minMax[1] - minMax[0]) + minMax[0]
    return M

#==========================================================================#
def imp_LSTM (data, nbre_preds, p):

    # normalize the data
    #minMax = normalize(data)

    # transform the data to supervised learning
    model = toSuppervisedData(data,p)
    X = model.data
    y = model.targets[:,0:1]

    predictions = np.empty ([nbre_preds, 1])
    limit = X.shape[0] - nbre_preds

    X_train, y_train = X[0:limit], y[0:limit]


    lstm_model = LSTM_MODEL (p)
    lstm_model. fit  (X_train, y_train)

    prediction = []

    for j in range (0, nbre_preds):
        limit = X.shape[0] - nbre_preds + j

        Xx, yy = X [limit  :limit+1], y[limit  :limit+1]

        # make  predictions
        yhat = lstm_model.predict (Xx)
        # take the last one corresponding to the futur prediction
        prediction.append (yhat[-1])

        # update the model: online learning
        X_update, y_update = X[limit :limit+1], y[limit :limit+1]
        lstm_model. update (X_update, y_update, epochs=1)


    predictions[:,0] = prediction
    #predictions = inverse_normalize (predictions,minMax[0,:])
    #reals = inverse_normalize (reals, minMax[0,:])

    return np.array(predictions)

#-------------------------------------------#
#-------+      PREDICT A FILE      +--------#
#-------------------------------------------#
def predictbase (fname, output_directory, reset = 0):

    '''if "PEHAR" not in fname:
        return'''
    fname_ = fname.split('/')[-1]
    out_fname = output_directory + "/LSTM_" + fname_

    data = read_csv_and_metadata(fname)
    meta_header = data.meta_header
    nbre_preds = int (meta_header['number_predictions'][0])
    p = int (meta_header['lag_parameter'][0])
    horizon = int (meta_header['horizon'][0])
    target_names =  meta_header['predict']

    # Temporarly: to reduce the computation time
    if data.shape[1] not in [4, 5, 6, 7]:
        return

    if not os.path.exists(out_fname):
        n_predictions = 0

    if os.path.exists(out_fname):
        predictions = read_csv_and_metadata(out_fname)
        n_predictions = predictions.shape [0]

    if n_predictions < nbre_preds or reset == 1:
        #print ("Processing file %s" % out_fname)
        predictions = imp_LSTM (data.values, nbre_preds, p)
        predictions = pd.DataFrame (predictions[:,0])

        # Put meta-data for the output file
        predictions.meta_header = data.meta_header
        predictions.meta_header['predict_model'] = ["lstm"]
        predictions.meta_header['predict'] = [target_names[0],]


        write_csv_with_metadata(predictions, out_fname)
    '''else:
        print ( bcolors.OKGREEN + "File %s already exist" % out_fname + bcolors.ENDC)
    print ("Done...")'''


#-----------------------------------------#
#------------+      MAIN     +------------#
#-----------------------------------------#
def main ():
    fnames_path, output_directory = sys.argv[1], sys.argv[-1]
    if (sys.argv[1].split ('.')[-1] == 'csv'):
    	fnames = [sys.argv[1]]
    else:
    	fnames = glob.glob (fnames_path+"*.csv")

    Parallel(5)(delayed(predictbase)(fname, output_directory, reset = 0) for fname in fnames)


if __name__ == "__main__":
    main()
