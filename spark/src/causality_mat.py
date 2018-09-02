#spark-submit --class testspark --master yarn --deploy-mode cluster --files ebob-l.csv --py-files tools.zip causality_mat.py

import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")
from pyspark.mllib.linalg.distributed import IndexedRow, IndexedRowMatrix
from pyspark.mllib.linalg.distributed import CoordinateMatrix, MatrixEntry

import pyspark.sql.functions as func
from pyspark import SparkContext
from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark import SQLContext
from pyspark.ml.stat import Correlation
from pyspark.ml.linalg import Vectors
from pyspark.sql.functions import *

import numpy as np
import pandas as pd
from scipy.stats.stats import pearsonr

from tools.transfer_entropy_jidt import *
from tools.causality import *

import sys


conf = (SparkConf().set("num-executors", "2"))

sc = SparkContext(conf = conf)
sc.setLogLevel('WARN')


def corr (x, y):
    
    try:
        #cor = jdit_transfer_entropy (x[1], y[1])
        cor = granger_causality (y, x, 1)
    
    except (ValueError):
        print (ValueError)
        cor = 0
    return float (cor)

if __name__ == "__main__":
    
    sqlcontext =  SQLContext(sc)
    
    input_data = sys.argv[1]
    data_name = input_data. split ('/')[-1]. split ('.')[0]   
    
    df = sqlcontext.read. parquet (input_data)                         
    rdd = df. rdd
    
    pairs = rdd.cartesian(rdd). map (lambda x: [x[0][0], x[1][0], x[0][1], x[1][1],  corr (x[0][2], x[1][2])])
    pairs = pairs. toDF (["id1", "id2", "P1", "P2", "Caus"]). dropDuplicates(['id1','id2'])
    pairs. write. parquet (data_name + "_gc", mode = 'overwrite')    

