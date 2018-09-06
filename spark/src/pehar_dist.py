import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

from pyspark import SparkContext
from pyspark import SparkConf
from pyspark import SQLContext
from pyspark.sql.functions import *

import numpy as np
import sys


conf = (SparkConf().set("num-executors", "1"))
sc = SparkContext(conf = conf)
sqlcontext =  SQLContext(sc)
sc.setLogLevel('WARN')

def absolute (x):
    if x >= 0:
        return x
    else:
        return -x
def get_item (M, i, j):
    if i == j:
        return 0
    mij = M. where ((M. id1 == i) & (M. id2 == j))
    return mij

def update_hubs (a, causalities):
    caus = causalities. map (lambda x: (x[1][0], (x[0], x[1][1])))
    h = a.join (caus)
    h = h. map (lambda x: (x[1][1][0], x[1][0] * x[1][1][1])).\
    reduceByKey (lambda x, y: x + y)
    return h

def update_auths (h, causalities):     
    a = h.join (causalities). map (lambda x: (x[1][1][0], x[1][0] * x[1][1][1])).\
    reduceByKey (lambda x, y: x + y)
    return a

# l1 norm
def normalize_rdd (r):
    sum = float (r. map (lambda x : x[1]). reduce (lambda x, y: x + y))
    r = r.map (lambda x: (x[0], x[1] / sum))
    return r

def pehar_distributed (Mat, target_index, iters, error = 1.0e-3):

    # Extart Matrix of predictors and the Vector of causalities to the target
    df_predictors = df. where ( (df.id1 != target_index)  & (df.id2 != target_index)). select (["id1", "id2", "Caus"])
    df_target = df. where ((df. id1 != target_index) & (df.id2 == target_index)). select (["id1", "Caus"])

    causalities = df_predictors. join (df_target, on='id1'). rdd. map (lambda x: (x[0], x[1], x[2] * x[3])). toDF (["id1", "id2", "Caus"])

    colnames = df.select ("P1", "id1"). distinct ()#. sort ("id1") 
    n_nodes = colnames.count ()

    hubs = colnames.select ("id1"). rdd. map (lambda x: (x[0], 1.0 / float (n_nodes) ))
    direct_values = causalities. rdd. map (lambda x: (x[0], (x[1], x[2])) )

    print (19* '-')
    
    iter = 0 
   
    err = 1 
    while iter < iters and err > error:
        hlast = hubs
        hubs = hubs. map (lambda x: (x[0], 0))
        auths = hubs
    
        # update authorities and hubs 
        auths = update_auths (hlast, direct_values)
        hubs = update_hubs (auths, direct_values)
    
        # Normalization
        hubs = normalize_rdd (hubs)
        auths = normalize_rdd (auths)
        iter += 1
        err = hubs. join (hlast). map (lambda x: (x[1][0] - x[1][1])). reduce (lambda x, y: absolute (x + y))
    return (auths, hubs)

if __name__ == "__main__":
	
    '''iters = 10
    target_index = 0
    input_mat = sys.argv[1]
    data_name = input_mat. split ('/')[-1]. split ('.')[0]
 
    df = sqlcontext.read. parquet (input_mat)
    auths, hubs = pehar_distributed (df, target_index, iters)
    print (hubs. map (lambda x: x[1]). reduce (lambda x, y: x + y))'''




