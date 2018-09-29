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


def get_line (df, col):
    line = df. where (df.Col == col).rdd. flatMap (lambda x: x). collect ()
    #print (line)
    line = [line[0]] + line[2]. split (" ")
    return sc. parallelize ([line])

if __name__ == "__main__":

    input_data = sys.argv[1]

    # data
    data = sqlcontext.read. parquet ('hdfs://master:9000/user/hduser/'+ input_data) 
    
    # features
    df = sqlcontext.read. format ("com.databricks.spark.csv").\
    option("header", "true").\
    option("sep",",").\
    load("hdfs://master:9000/user/hduser/features_selection/ausmacro_gc/features.csv/")
    cols = df. where (df.Col == "BusInv").rdd. flatMap (lambda x: x). collect ()
    
    # colnames
    colnames = data. select ("colname"). distinct ().  rdd. map (lambda x: x[0]). collect ()
    #print (colnames)
    models = sc.emptyRDD ()

    for col in colnames:
        models = models.union (get_line (df, col));

    
    df. show ()
    models. toDF (). show ()
    exit (1)
    
    small_data  = pd.DataFrame (data. where (col("colname").isin (cols)).\
    select (["time_seres"]).rdd. flatMap (lambda x: x). collect ()). transpose ()
    small_data.columns = cols
    
    data. where (col("colname").isin (cols)). show ()
    print (small_data)

    predictions, reals = imp_LSTM (small_data. values, 10, 4, 20, 5, batchSize = 1)
    print (predictions)




