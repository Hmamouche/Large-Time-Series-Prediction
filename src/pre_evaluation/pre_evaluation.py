#!/usr/bin/python

import os
import sys
import glob
import re
from collections import defaultdict, OrderedDict
import pickle
import hashlib

import pandas as pd
import numpy as np

sys.path.append ('src')
import tools.csv_helper as tools
from tools.global_measures import GLOBAL_MEASURES, MASE2


def transform_into_output_tables(results_collection, methods_to_hotizon_dict):

    univariate_models = ['Auto_Arima', 'naive_benchmark', 'Arima', 'Ar']
    tables = defaultdict(lambda: defaultdict(dict))
    results_collection = dict(results_collection)

    for predict_model in results_collection:
        # Univariate models will be added to all multivatiate tables for easy comparison
        if predict_model in univariate_models:
            continue

        for target in results_collection[predict_model]:
            # diffrent timehorizons
            for horizon in range(methods_to_hotizon_dict[predict_model]):

                # Add results multivariate prediction
                new_row = [
                    OrderedDict({'predict': predict_model, 'group': group, 'method': mtype}.items() | measures.items())
                    for group in results_collection[predict_model][target][horizon]
                    for mtype, measures in results_collection[predict_model][target][horizon][group].items()
                ]
                for u_model in univariate_models:
                    try:
                        new_row.extend([
                            OrderedDict({'predict': u_model, 'group': u_model, 'method': mtype}.items() | measures.items())
                            for group in results_collection[u_model][target][horizon]
                            for mtype, measures in results_collection[u_model][target][horizon][group].items()
                        ])
                    except Exception as e:
                        print(e)
                        pass

                df = pd.DataFrame.from_dict(new_row)
                df.set_index(["predict", "group", "method"])
                tables[target][horizon][predict_model] = df

    return tables


def get_slice_with_horizon(df, nbre_preds, target, horizon, max_horizon):
    return df[[target]].tail(nbre_preds + max_horizon - 1 - horizon).head(nbre_preds).values


def evaluate_prediction(original_data, target, predictions, horizon_range):
    """Evaluate prediction results

    :real_values: a transformed data frame with real values
    :predicted_file): a data frame with predicted values
    :returns: evaluation measurments

    """

    results = defaultdict(dict)

    for horizon in range(horizon_range):
        testing_data_index = len(original_data) - (len(predictions) + horizon_range - 1 - horizon)
        testing_data = original_data[[target]].head(testing_data_index).values.T[0]
        GLOBAL_MEASURES['MASE'] = lambda x,y: MASE2(testing_data, x, y)

        for mkey, measure in GLOBAL_MEASURES.items():
            data_slice = get_slice_with_horizon(
                original_data, len(predictions), target, horizon, horizon_range)
            results[horizon][mkey] = measure(
                data_slice, predictions.values[:, horizon])

    return results


def check_fields_in_metaheader(predictions, dict_to_check, fields, fname, error_list):
    if len(predictions.columns) == 0:
        error_list.append("Error: File %s, has no columns." % (fname))
        return False

    for field in fields:
        if field not in predictions.meta_header:
            error_list.append(
                "Error: File %s, field %s\n not found in meta header." % (fname, field))
            return False
        if len(predictions.meta_header[field]) != 1:
            error_list.append(
                "Error: File %s, field %s\n has more then one value in meta_header." % (fname, field))
            return False
        if len(predictions.meta_header[field][0].strip()) == 0:
            error_list.append(
                "Error: File %s, field %s\n value is empty in meta_header." % (fname, field))
            return False
    return True


def read_and_evaluate_results():
    if len(sys.argv) != 3:
        print("Error: wrong arguments. Use %s org_data_file globing_expression" % (
            sys.argv[0]))
        exit(0)

    # Read the orginal data file
    try:
        original_data = tools.read_csv_and_metadata(sys.argv[1])
    except:
        print("Error: Could not read the file %s, exiting." % (sys.argv[1]))
        exit(0)

    prediction_method_horizon = {}
    results_collection = defaultdict(lambda: defaultdict(
        lambda: defaultdict(lambda: defaultdict(dict))))
    error_list = []

    n_components_match = re.compile("n_components\s*=\s*([0-9]+)\s*[,)]")

    out_dir = sys.argv[2]
    in_dir = out_dir.replace("pre_evaluation","prediction")

    for fname in glob.glob(in_dir + "/*.csv"):
        # Read the predictions
        try:
            predictions = tools.read_csv_and_metadata(fname)
        except Exception as e:
            # print(e)
            error_list.append(
                "Error: Could not read file %s, moving to next file" % (fname))
            continue

        meta_header = predictions.meta_header
        # Complain and continue if fields are messed up in input file
        # meta_header
        fields = ['predict', 'predict_model', 'method']
        if not check_fields_in_metaheader(predictions, meta_header, fields, fname, error_list):
            continue

        # Extract fields from meta_header and data
        predict_model = predictions.meta_header['predict_model'][0]
        selection_method = predictions.meta_header['method'][0]
        target = predictions.meta_header['predict'][0]
        if 'experiment_type' in predictions. meta_header. keys ():
            original_data = original_data.copy()
            original_data[:] = 0
        horizon = len(predictions.columns)

        # For each prediction method only one prediction horizon is available
        if predict_model in prediction_method_horizon \
                and prediction_method_horizon[predict_model] != horizon:
                    # TODO: maybe just use the max ?
            prediction_method_horizon[predict_model] = max(horizon, prediction_method_horizon[predict_model])
            # error_list.append("Error: more then one horizon detected for method %s skipping file %s" % (
            #     predict_model, fname))
            continue

        # If the prediction horizon match the previously set one or when this
        # the first time we see horizon
        prediction_method_horizon[predict_model] = horizon

        # The number of predicted vectors (vector may be one dimensional or may include some additional time horizon prediction)
        # nbre_preds = len(predictions.index)

        try:
            ret = evaluate_prediction(
                original_data, target, predictions, horizon)
        except Exception as e:
            print(e)
            error_list.append(
                "Error: Evaluation of predictions failed, skipping file %s" % (fname))
            continue

        # This will fail if name does not match, but then the
        # prediction/selection methods must be fixed
        try:
            selection_method_group_name, id_name = \
                predictions.meta_header['method'][0].split('(')[:2]
        except Exception as exception:
            print("Error: couldn't parse the selection method name,\
                    please use 'method_group_name(other_params, n_components=k, other_params)'.\
                    If no n_components param is found group is treated as one element group.")
            selection_method_group_name, id_name = "None", "None"

        r_match = n_components_match.search(id_name)
        m_id = hashlib.sha1(id_name.encode('UTF-8')).hexdigest()[:10]
        if r_match is not None:
            id_name = str(int(r_match.group(1))) + ":" + m_id
        else:
            id_name = str(0) + ":" + m_id


        for k, evaluation_result in ret.items():
            results_collection[predict_model][target][k][
                selection_method_group_name][id_name] = evaluation_result

    return results_collection, prediction_method_horizon, error_list

def default_to_regular(d):
    if isinstance(d, defaultdict):
        d = {k: default_to_regular(v) for k, v in d.items()}
    return d


def main():
    results_collection, prediction_method_horizon, error_list = read_and_evaluate_results()
    # This was already checked in read_and_evaluate_results
    out_dir = sys.argv[2]
    # Set the output prefix
    timeseries_prefix = sys.argv[1].split("/")[-1].split(".")[0]

    if os.path.exists ("%s/%s.pickle"%(out_dir, timeseries_prefix)):
        os.system ("rm %s/%s.pickle"%(out_dir, timeseries_prefix))


    # Get the output touple
    tables_real = transform_into_output_tables(
        results_collection, prediction_method_horizon)

    tables_real = default_to_regular(tables_real)

    with open("%s/%s.pickle"%(out_dir, timeseries_prefix),"wb") as out_file:
        pickle.dump(tables_real, out_file)
        pickle.dump(error_list, out_file)

    # transform_into_excel(tables_real, error_list).write(timeseries_prefix)
    # transform_into_figure(tables_real, error_list).write(timeseries_prefix)
    # transform_into_html(tables_real, error_list).write(timeseries_prefix)

if __name__ == "__main__":
    main()
