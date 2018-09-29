from __future__ import print_function

import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

import sys
import os
from scipy import *

import numpy as np
from numpy import inf
import pandas as pd


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

def get_value (data, i, j):
    if i == j:
        return 0.0
    tuple = data. loc [ (data['id1'] == i) & (data['id2'] == j)]
    value = tuple
    if tuple.shape[0] == 0:
        return 0
    else:
        #print (tuple.values[0][2])
        return tuple.values[0][2] * tuple.values[0][3]
#-------------------------------------------------#
#                    Hits                         #
#-------------------------------------------------#
def hits (matrix, index_target, iters, min_error =1.0e-3):
   
    normalized = True
    nodes = np.unique (matrix.iloc[:,0]). tolist ()
    nodes. remove(index_target) 
    n_nodes = len (nodes)
    
    h = np.empty ([n_nodes + 1, 1],dtype=float)
    hlast = np.empty ([n_nodes + 1, 1],dtype=float)
    a = np.empty ([n_nodes + 1, 1], dtype=float)


    h[index_target] = 0
    a[index_target] = 0
    M = matrix. loc [ (matrix['id1'] != index_target) & (matrix['id2'] != index_target)]
    V = matrix. loc [ (matrix['id1'] != index_target) & (matrix['id2'] == index_target)] [["id1", "Caus"]]
    V.columns = ["id1", "Caus_T"]
    
    M = M. set_index ('id1'). join (V. set_index ('id1'))
    M.reset_index(level=0, inplace=True)

    for node in nodes:
        h[node] = 1.0 / (float) (n_nodes)

    i = 0
    err = 1

    while i < iters and err > min_error :
        for node in nodes:
            hlast[node] = h[node]
        
        for node in nodes:
            h[node] = 0.0
            a[node] = 0.0

        # compute a
        for node in  nodes:
            for pt in  nodes:
                a[pt] += hlast[node] *  get_value (M, node, pt) #* get_value (matrix, node, index_target) # matrix[node, pt]
                
        #a[where(isinf(a))]=0.0
        #a[where(isnan(a))]=0.0

        # compute h
        for node in  nodes:
            for pt in  nodes:
                h[node] += a[pt] *  get_value (M, node, pt) #* get_value (matrix, node, index_target) 

        #h[where(isinf(h))]=0.0
        #h[where(isnan(h))]=0.0

        # normalize vector
        s = 1.0 / sum (h)
        for n in nodes:
            h[n]*=s

        # normalize vector
        s = 1.0 / sum (a)
        for n in nodes:
            a[n]*=s

        # check convergence, l1 norm
        err = sum ([abs(h[n]-hlast[n]) for n in nodes])

        i += 1
        
    return a, h

#                    MAIN                         #
def main():
    data = pd.read_csv ("data/mat.csv", header = 0, sep=';')  [[ "id1", "id2", "Caus"]]
    a, h = hits (data, 0, iters = 10, min_error =1.0e-3)
    print (h. tolist ())
    print (a. tolist ())
if __name__ == '__main__':
    main()

