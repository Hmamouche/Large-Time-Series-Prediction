import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

from pyspark import SparkContext
from pyspark import SparkConf
from pyspark import SQLContext
from pyspark.sql.functions import *

from tools.lstm import *

import numpy as np
import pandas as pd
import sys 
import os

conf = (SparkConf(). set ("--executor-cores", "3"))
sc = SparkContext(conf = conf)
sqlcontext =  SQLContext(sc)
sc.setLogLevel('WARN')


def get_line (df,data, col):

    # extract target + predictors
    line = df. where (df.Col == col).rdd. flatMap (lambda x: x). collect ()
    line = [line[0]] + line[2]. split (" ")

    # construct input data of the model
    line = [str (x) for x in line]
    print (line)
    small_data = data. filter (data["colname"].isin (line)).\
    select (["time_series"]).rdd. flatMap (lambda x: x).toDF ().toPandas(). transpose ()
    small_data.columns = line
    #print (small_data)
    return sc. parallelize ([small_data])

def predict_one_col (x):
    return 0    


if __name__ == "__main__":

    print (19 * '-')
    input_data = sys.argv[1]

    if (len (input_data.split ('/')) > 1):
        data_name = input_data.split ('/')[1] .split ('.')[0]
    else:
        data_name = input_data. split ('.')[0]

    graph_name= data_name + '_gc'
    # data
    data = sqlcontext.read. parquet ('data/'+data_name) 
    os.system ('hdfs dfs  -mkdir -p prediction/')    
    # features
    df = sqlcontext.read. format ("com.databricks.spark.csv").\
    option("header", "true").\
    option("sep",",").\
    load("features_selection/"+ graph_name)
    
    # colnames
    colnames = data. select ("colname"). distinct ().  rdd. map (lambda x: x[0]). collect ()
    #print (colnames)
    models = sc.emptyRDD ()

    for col in colnames:
        #get_line (df, col)
        models = models.union (get_line (df, data, col));



    lag_parameter = 4
    number_of_predictions = 10
    number_of_neurons = 5
    number_of_iteration = 20
    predictions = models.map (lambda x: imp_LSTM (x. values, 
                                                  number_of_predictions,
                                                  lag_parameter, 
                                                  number_of_iteration, 
                                                  number_of_neurons, 
                                                  batchSize = 1)[0]).\
                            toDF (). write. parquet ("prediction/" + data_name, mode='overwrite')
    
    





