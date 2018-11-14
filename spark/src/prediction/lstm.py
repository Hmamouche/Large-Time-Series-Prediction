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

conf = (SparkConf())
sc = SparkContext(conf = conf)
sqlcontext =  SQLContext(sc)
sc.setLogLevel('WARN')


def extract_data (df,data, col):

    # extract target + predictors
    line = df. where (df.Col == col).rdd. flatMap (lambda x: x). collect ()
    line = [line[0]] + line[2]. split (" ")

    # construct input data of the model
    line = [str (x) for x in line]
    print (line)
  
    # First columns 
    small_data = data. where (data["colname"] == line[0]).\
        select (["time_series"]).rdd. flatMap (lambda x: x).toDF ().toPandas(). transpose () 

    # Add the other columns to the dataframe by concatenation
    for name in line[1:]:
        attribute = data. where (data["colname"] == name).\
                                select (["time_series"]).rdd. flatMap (lambda x: x).toDF ().toPandas(). transpose ()
        
        small_data = pd.concat ([small_data, attribute], axis = 1)
    
    return sc. parallelize ([[col, small_data. values]])

    

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
    

    # Construct an Rdd that contains the predictiosn of each target time series
    models = sc.emptyRDD ()

    for col in colnames:
        models = models.union (extract_data (df, data, col))

    #models = models.partitionByKey ()


    # TODO : read these information from metadata automatically
    if data_name == 'ausmacro' or data_name == 'us_dif':
        lag_parameter = 4
        number_of_predictions = 10
        number_of_neurons = 5
        number_of_iteration = 20


    # Run lstm in parallel on all selection file
    predictions = models.map (lambda x: [x[0], imp_LSTM (x[1],\
                                                  number_of_predictions,\
                                                  lag_parameter,\
                                                  number_of_iteration,\
                                                  number_of_neurons,\
                                                  batchSize = 1). tolist ()]). toDF (['Variables', 'Predictions'])
    predictions. show ()
    predictions. write. parquet ("prediction/" + data_name, mode='overwrite')
    
    





