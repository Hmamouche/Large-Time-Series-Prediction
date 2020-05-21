import pandas as pd
import numpy as np
import argparse, os, sys

from pmdarima.arima import auto_arima
from statsmodels.tsa.vector_ar.vecm import VECM

from sklearn import preprocessing
from sklearn.exceptions import ConvergenceWarning

sys.path.append ("src")
from tools.csv_helper import *
from selection.gfsm_fselection import gfsm_feature_selection
from selection.pehar_fselection import pehar_feature_selection
from pre_selection.granger_causality import causality_matrix

'''import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=ConvergenceWarning)'''

def make_dir (dir):
    """ create dir if does not exist """
    if not os.path.exists (dir):
        os.mkdir (dir)

def predict_target (data, prediction_model, method, nb_predictors, causality_graph):
    target_index = list (data. columns). index (target)

    if "Arima" in prediction_model:
        try:
            model = auto_arima (data. loc[:, target]. values, start_p = 1, start_q = 1)
            predictions = model. fit_predict (data. loc[:, target]. values, n_periods = 5)
        except:
            print ("VECM failed for this variable")
            predictions = [float('nan') for x in range (5)]
    else:
        if "PEHAR" in method:
            predictors_index = pehar_feature_selection (causality_graph, target_index)[0:nb_predictors]

        elif "GFSM":
            predictors_index = gfsm_feature_selection (causality_graph, target_index, nb_predictors)

        # Add target variable in the first column
        predictors_index. insert (0, target_index)

        # Construct data from the colmuns
        X_train = data. iloc[:, predictors_index]. values

        # Fit the model
        try:
            model = VECM (X_train, k_ar_diff = lag, deterministic = "ci"). fit ()
            # Make 5 predictions
            predictions = model. predict (steps = 5)[:, 0]
        except:
            print ("VECM falied for this variable")
            predictions = [float('nan') for x in range (5)]

    return predictions
#=======================================================================================================================
if __name__ == '__main__':
    parser = argparse. ArgumentParser ()
    parser. add_argument ("--data", "-d", help = "file of data to process")
    parser. add_argument ("--mode", "-m", help = "prediction mode", choices = ["eval", "direct"])
    parser. add_argument ("--pred_model", "-pr", help = "prediction model", choices = ["VECM", "ARIMA"])
    parser. add_argument ("--fs_method", "-fsm", help = "feature selection method", choices = ["PEHAR_te", "PEHAR_gc"])
    parser. add_argument ("--nb_predictors", "-nbp", help = "number of variables to select")
    parser. add_argument ("--graph_type", "-g", help = "Causality graph to use, ganger causality (gc), or transfer entropy (te)", choices = ["gc", "te"])
    args = parser.parse_args()

    #print (args)

    # Read data and get information from metadata
    data = read_csv_and_metadata_2 (args.data)
    data_name = args.data. split ("/")[-1].split ('.')[0]
    lag = int (data._metadata["lag_parameter"][0])
    targets_ts = data._metadata["predict"]

    # Create output directory if does not exist
    make_dir ("Processed")
    make_dir ("Processed/%s"%data_name)
    out_dir = "Processed/%s"%data_name

    # Compute causality graphs
    gc_causality_graph = causality_matrix (data. values, lag)
    te_causality_graph = causality_matrix (data. values, lag)
    pd.DataFrame(gc_causality_graph, index=data.columns, columns=data.columns). to_csv ("%s/causality_graph_gc.csv"%(out_dir), sep = ';')


    if args.mode == "eval":
        evaluation_results = pd.read_excel ("results/evaluation/%s/%s_best.xlsx"%(data_name,data_name), index_col = 0)

    all_predictions = {}
    info_models = []

    for target in targets_ts:
        if args. mode == "eval":
            pred_model = evaluation_results.loc["predict", target]
            nb_predictors = int (evaluation_results.loc["method", target]. split (':')[0])
            method = evaluation_results.loc["group", target]
            graph_type = evaluation_results.loc["group", target]. split ('_')[-1]

        elif args. mode == "direct":
            pred_model = args.pred_model
            method = args.fs_method
            graph_type = args.graphe_type
            nb_predictors = args.nb_predictors

        info_models. append ([target, pred_model, nb_predictors, method, graph_type])
        # Compute causality graphs
        if graph_type == "te":
            causality_graph = te_causality_graph
        elif graph_type == "gc":
            causality_graph = gc_causality_graph

        predictions = predict_target (data, pred_model, method, nb_predictors, causality_graph)

        # Concatenate predictions of all target variables
        all_predictions [target]  = predictions

    pd. DataFrame (all_predictions). to_csv ("%s/predictions.csv"%out_dir, sep = ";",  index = False)
    pd. DataFrame (info_models, columns = ["Variables", "Prediction_model", "Nb_predictors", "Reduction_method", "Graph_type"]). to_csv ("%s/info_models.csv"%out_dir, sep = ";",  index = False)
