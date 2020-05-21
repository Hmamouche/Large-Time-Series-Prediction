# Author: Youssef Hmamouche

import os, glob, re, sys, argparse
import numpy as np
from numpy import inf
import pandas as pd
from joblib import Parallel, delayed

sys.path.append ("src")
import tools.csv_helper as csvh

#=====================================================================================
def pehar_feature_selection (causality_matrix, ind_target,  iters = 100, min_error =1.0e-3):
    """ The PEHAR feature selection method

    Parameters
    ----------
    causality_matrix : np array
        The causality matrix of all variables
    ind_target : int
        The index of the target variable
    iters : int, optional
        Number of iterations (default is 500)
    min_error : float, optional
        Minimum error to stop in iterations (default is 1.0e-3)

    Returns
    -------
    list
        The variable ranked according to their causal importance on the target variable
    """

    for i in range (causality_matrix.shape[0]):
        for j in range (causality_matrix.shape[1]):
            if causality_matrix [i,j] < 0:
                causality_matrix [i,j] = 0


    matrix = causality_matrix.copy ()

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
                a[pt] += hlast[node] * matrix[node, pt] * matrix[node, ind_target]

        a[np.where(np.isinf(a))]=0.0
        a[np.where(np.isnan(a))]=0.0

        # compute h
        for node in range (n_nodes):
            for pt in range (n_nodes):
                h[node] += a[pt] * matrix[node, pt] * matrix[node, ind_target]

        h[np.where(np.isinf(h))]=0.0
        h[np.where(np.isnan(h))]=0.0

        if sum (h) == 0 or sum (a) == 0:
            return "None"

        # normalize vector
        s = 1.0 / np. sum (h)
        for n in range (n_nodes): h[n]*=s
        # normalize vector
        s = 1.0 / np. sum (a)
        for n in range (n_nodes): a[n]*=s
        # check convergence, l1 norm
        err = sum ([abs(h[n]-hlast[n]) for n in range (n_nodes)])

        i += 1

    pd_h = pd.concat([pd.DataFrame (range (n_nodes)), pd.DataFrame(h)], axis = 1)


    pd_h.columns = ["Index", "Scores"]
    pd_h = pd_h.drop (pd_h.index[ind_target], axis = 0)
    pd_h = pd_h.sort_values (["Scores"], ascending=False)

    rank = pd_h. Index. values. tolist ()

    return rank

#=============================================================================================================#
# Apply feature selection with multiple reduction sizes from an input file and store the results as csv files #
#=============================================================================================================#
def predictFile (data, target, output_directory, fname, fname_graph, graph_type, max_features):
    #print ('\t' + "... Processing: %s" %(target))

    # Check if selection files already exist
    test = 0
    for output_dimension in range (1, max_features + 1):
        out_fname = output_directory + fname.split("/")[len(fname.split("/"))-1].split(".")[0] +  "_" + target + "_" + "PEHAR_" + graph_type + "k=" + str (output_dimension)+ ".csv"
        if not os.path.exists(out_fname):
            test = 1
            break
    if test == 0:
        print ("already processed!")
        return

    # Read causality matrix
    causality_matrix = pd.read_csv (fname_graph, index_col=0, sep = ';', comment = '#')
    all_variables = list (causality_matrix. columns)
    ind_target = all_variables.index (target)

    try:
        variables_rank = pehar_feature_selection (causality_matrix. values, ind_target)
    except Exception as e:
        print ("Error with variable: %s"%(target))
        print (e)

    if variables_rank == "None":
        return

    # Apply pehar_feature selection with multiple number of features
    for output_dimension in range (1, max_features + 1):
        out_fname = output_directory + fname.split("/")[len(fname.split("/"))-1].split(".")[0] +  "_" + target + "_" + "PEHAR_" + graph_type + "_k=" + str (output_dimension)+ ".csv"

        if os.path.exists(out_fname):
            continue

        top_k = variables_rank [0:output_dimension]

        top_k_ = np.insert (top_k, 0, ind_target)
        reduced_data = data. iloc[:, top_k_]

        reduced_data._metadata = data.meta_header. copy ()

        reduced_data._metadata['predict'] = [target]
        method_name = "PEHAR_" + graph_type + "(n_components=" + str (output_dimension) + ")"
        reduced_data._metadata['method'] = [method_name]
        csvh.write_csv_with_metadata_2 (reduced_data, out_fname)


#=================================#
if __name__ == '__main__':

    parser = argparse. ArgumentParser ()
    parser. add_argument ("data", help = "csv file of the folder that contains the csv files to predict")
    parser. add_argument ("out_dir", help = "output output_directory")
    args = parser.parse_args()

    fname, output_directory = args.data, args.out_dir

    data = csvh.read_csv_and_metadata(fname)
    data = data.dropna(axis=1, how='all')
    meta_header = data.meta_header
    targets = meta_header['predict']
    max_features = min(data.shape[1], int (data.meta_header['max_attributes'][0]))

    # Search for Adj-matrix for TS file in data folder
    fname_base = os.path.basename(fname).split(".")[0]

    output_directory_pre_selection = output_directory.replace("selection", "pre_selection")

    for fname_graph in glob.glob(output_directory_pre_selection + "/*.csv"):

        '''if fname_graph.split ('/')[-1] not in ["gc.csv", "te.csv", "nlin_gc.csv"]:
            print("Error: could not match graph_type in filename", fname_graph)
            continue'''
        graph_type = fname_graph.split ('/')[-1]. split ('.')[0]

        print ("Feature selection with", graph_type, "causality graph")
        print (17 * '-')
        Parallel(5)(delayed(predictFile) (data, target, output_directory, fname, fname_graph, graph_type, max_features) for target in targets)
        print ("... Done.")
