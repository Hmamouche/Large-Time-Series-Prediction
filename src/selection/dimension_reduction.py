#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys

import sklearn.decomposition as decomp
import pandas as pd

sys.path.append ("src")
from tools.csv_helper import *

from joblib import Parallel, delayed
from joblib import load, dump
import os


def dimension_reduction(fname, column, f_max, output_directory):

    df = read_csv_and_metadata(fname)
    df = df.dropna(axis=1, how='all')
    #df = df[df.columns.difference([column,])]

    methods_manual = [
                      decomp.FactorAnalysis,
                      decomp.PCA,
                      partial_with_pretty_method_name(decomp.KernelPCA, kernel="rbf")
                      ]

    methods = []
    #methods.extend([m() for m in methods_automatic])
    methods.extend([m(n_components=f_num) for m in methods_manual for f_num in range(1,f_max+1)])

    #methods.extend ([m(n_components=f_num) for m in methods_manual for f_num in [f_max+1]])

    for method in methods:
        # output for method name
        mname = "dm_" + pretty_print_method_name(method)
        out_fname = get_filename_from_method(fname, column, mname, prefix=output_directory)

        #out_fname = output_directory + fname.split("/")[len(fname.split("/"))-1].split(".")[0] +  "_" + column + "_" + method + "_" + "k=" + str (output_dimension)+ ".csv"

        # TODO: only update the files ?
        # if file exists skip selection for this method
        # if path.isfile(out_fname):
        #     print ("File for method %s exists - skipping.\n  * Remove %s file to recompute it."%(mname,out_fname))
        #     continue

        # Fit and transform using method
        if os.path.exists(out_fname):
            continue
        try:
            #print ("Warning: creation of the file %s: "%(out_fname))
            reduced_ts = method.fit_transform(df)
            #print (reduced_ts)
            #exit ()
            reduced_ts = pd.DataFrame(reduced_ts)

            reduced_ts.meta_header = df.meta_header.copy()
            reduced_ts.meta_header['method'] = [mname,]
            reduced_ts.meta_header['predict'] = [column,]

            # Output columns in corrrect order
            cols=[column,]
            cols.extend(reduced_ts.columns.values)

            # Add predicted column to output
            reduced_ts[column] = df[column]

            # Write reduced_ts with cols in correct order (reduced_ts[cols]) to filename generated from the method name with params
            write_csv_with_metadata(reduced_ts[cols], out_fname)
        except Exception as e:
            print ("Error with method %s: %s"%(method,e))
            continue

def main():
    fname, output_directory = parse_selection_arguments(sys.argv)


    df = read_csv_and_metadata(fname)
    f_max = min(min(df.shape), int (df.meta_header['max_attributes'][0]))

    for column in df.meta_header['predict']:
    	dimension_reduction (fname, column, f_max, output_directory)

    #Parallel(-1)(delayed(dimension_reduction)(fname, column, f_max, output_directory) for column in df.meta_header['predict'])


if __name__ == "__main__":
    main()
