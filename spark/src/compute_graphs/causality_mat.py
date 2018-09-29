
import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

from pyspark import SparkContext
from pyspark import SparkConf
from pyspark import SQLContext
from pyspark.sql.functions import *

import numpy as np
import pandas as pd

from tools.transfer_entropy_jidt import *
from tools.causality import *

from pyspark.sql.functions import isnan, when, count, col

import sys
import os

conf = (SparkConf().set("num-executors", "2"))

sc = SparkContext(conf = conf)
sc.setLogLevel('WARN')
sqlcontext =  SQLContext(sc)

# compute the causality from x to y
def causality (x, y):
    cor = 1
    #return cor 
    cor -= granger_causality (y, x, 1)
    #cor = jdit_transfer_entropy (x, y) 
    if cor == np.nan or cor == np.inf or np.isfinite(cor) == False:
        cor = 0

    if cor > 1 or cor < 0:
        cor = 0

    #print (cor) 
    return float (cor)

def distributed_pairwise_caus (input_data):

    # create repository where to put the matrix of dependencies
    os.system ('hadoop fs -mkdir -p matrix_of_depend')
    
    data_name = input_data. split ('/')[-1]. split ('.')[0]   
        
    df = sqlcontext.read. parquet ('hdfs://master:9000/user/hduser/'+ input_data)                             
    #df. show (13689)
    rdd = df. rdd 
            
    pairs = rdd.cartesian(rdd). map (lambda x: [x[0][0], x[1][0], x[0][1], x[1][1],  causality (x[0][2], x[1][2])])
    pairs = pairs. toDF (["id1", "id2", "P1", "P2", "Caus"]).  repartition ("id1") #. dropDuplicates(['id1','id2']). repartition ("id1")
    #pairs. na.fill(0). show (13687)
    #print (pairs. count ())
    pairs. write. parquet ("/user/hduser/matrix_of_depend/" + data_name + "_gc", mode = 'overwrite')
    #mat = pairs. select ("id1", "id2", "Caus")
    #mat = CoordinateMatrix(mat.rdd) 
    #print (mat.entries. collect ())

if __name__ == "__main__":

    print ("Compute the distributed matrix of causalities")    
    input_data = sys.argv[1]
    distributed_pairwise_caus (input_data)




