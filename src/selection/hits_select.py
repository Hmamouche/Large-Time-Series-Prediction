# Author: Youssef Hmamouche

from __future__ import print_function
import sys
#import traceback
import glob
#from os import path
import re
import os
#from scipy import *

#import matplotlib.pyplot as plt
import numpy as np
from numpy import inf
import pandas as pd
from joblib import Parallel, delayed

sys.path.append ("src")
import tools.csv_helper as csvh

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

#-------------------------------------------------#
#                    Pehar                         #
#-------------------------------------------------#
def hits (fname, output_directory, fname_graph, graph_type, target,  iters = 500, min_error =1.0e-3):
    matrix_all = csvh.read_csv_and_metadata(fname_graph, index_col=0)
    
    for i in range (matrix_all.shape[0]):
        for j in range (matrix_all.shape[1]):
            if matrix_all.iloc[i,j] < 0:
                matrix_all.iloc[i,j] = 0

    targets = list (matrix_all)
    
    ind_target = 0
    for item in targets:
               if item == target:
                    break
               else: ind_target += 1

    matrix = matrix_all.values

    normalized = True
    n_nodes = matrix.shape[0]
    
    h = np.empty ([n_nodes, 1],dtype=float)
    hlast = np.empty ([n_nodes, 1],dtype=float)
    a = np.empty ([n_nodes, 1], dtype=float)
    
    for node in range (n_nodes):
        h[node] = 1.0 / (float) (n_nodes)

    i = 0
    err = 1

    while i < iters and err > min_error :
        for node in range (n_nodes):
            hlast[node] = h[node]
        
        for node in range (n_nodes):
            h[node] = 0.0
            a[node] = 0.0

        # compute a
        for node in range (n_nodes):
            for pt in range (n_nodes):
                a[pt] += hlast[node] * matrix[node, pt] * matrix[node, ind_target] #* matrix[pt, ind_target]
                
        #hm = [(a[pt], hlast[node] * matrix[node, pt]) for pt in nodes]. reduce (lambda x,y: x + y)

        a[np.where(np.isinf(a))]=0.0
        a[np.where(np.isnan(a))]=0.0

        # compute h
        for node in range (n_nodes):
            for pt in range (n_nodes):
                h[node] += a[pt] * matrix[node, pt] * matrix[node, ind_target] #* matrix[pt, ind_target]

        h[np.where(np.isinf(h))]=0.0
        h[np.where(np.isnan(h))]=0.0

        # normalize vector
        s = 1.0 / np. sum (h)
        for n in range (n_nodes): h[n]*=s
        # normalize vector
        s = 1.0 / np. sum (a)
        for n in range (n_nodes): a[n]*=s
        # check convergence, l1 norm
        err = sum ([abs(h[n]-hlast[n]) for n in range (n_nodes)])

        i += 1

    pd_h = pd.concat([pd.DataFrame (targets), pd.DataFrame(h)], axis = 1)

    pd_h.columns = ["Variabes", "Scores"]
    pd_h = pd_h.drop (pd_h.index[ind_target], axis = 0)
    pd_h = pd_h.sort_values (["Scores"], ascending=False)
    index = [i for i in range(n_nodes-1)]

    return pd_h,a

#-----------------------------------#
#           Predict File            #
#-----------------------------------#
def predictFile (data, target, output_directory, fname, fname_graph, graph_type, max_features):
    print ('\t' + "... Processing: %s" %(target))
    
    test = 0
    for output_dimension in range (1, max_features + 1):
        out_fname = output_directory + fname.split("/")[len(fname.split("/"))-1].split(".")[0] +  "_" + target + "_" + "Hits_" + graph_type + "k=" + str (output_dimension)+ ".csv"
        if not os.path.exists(out_fname):
            test = 1
            break
    if test == 0:
        print ("already done!")
        #return
    
    
    a, h = hits (fname, output_directory, fname_graph, graph_type, target)
    
    for output_dimension in range (1, max_features + 1):
        out_fname = output_directory + fname.split("/")[len(fname.split("/"))-1].split(".")[0] +  "_" + target + "_" + "Hits_" + graph_type + "k=" + str (output_dimension)+ ".csv"
        
        #if os.path.exists(out_fname):
        #    continue
        try:
            top_k = a.loc[:, 'Variabes'].values[0:output_dimension]
            op_k = np.insert (top_k, 0, target)
            reduced_data = data[op_k]

            reduced_data.meta_header['predict'] = [target,]
            method_name = "Hits_" + graph_type + "(n_components=" + str (output_dimension) + ")"
            reduced_data.meta_header['method'] = [method_name,]
            csvh.write_csv_with_metadata (reduced_data, out_fname)
        except Exception as e:
            print ("Error with file: %s"%(out_fname))
#-------------------------------------------------#
#                    MAIN                         #
#-------------------------------------------------#
def main():
    fname, output_directory = csvh.parse_selection_arguments(sys.argv)
    data = csvh.read_csv_and_metadata(fname)
    data = data.dropna(axis=1, how='all')
    meta_header = data.meta_header
    targets = meta_header['predict']
    max_features = min(data.shape[1], int (data.meta_header['max_attributes'][0]))

    # Search for Adj-matrix for TS file in data folder
    fname_base = os.path.basename(fname).split(".")[0]
    
    output_directory_pre_selection = output_directory.replace("selection", "pre_selection")
    
    for fname_graph in glob.glob(output_directory_pre_selection + "/*.csv"):
        m = re.match(".*(te|granger)(.*).csv", fname_graph)
        if m is None:
            print("Error: could not match graph_type in filename", fname_graph)
            continue
        graph_type = m.group (1) + "_" + m.group (2)
        
        print (graph_type)
        print (17 * '-')
        Parallel(-1)(delayed(predictFile) (data, target, output_directory, fname, fname_graph, graph_type, max_features) for target in targets)
            #for target in targets:
#  predictFile (target, output_directory, fname, fname_graph, graph_type, max_features)

if __name__ == '__main__':
    main()

