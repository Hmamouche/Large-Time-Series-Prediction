import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

from pyspark import SparkContext
from pyspark import SparkConf
from pyspark import SQLContext
from pyspark.sql.functions import *

import numpy as np
import sys
import os

conf = (SparkConf("Hits"))
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
    mij = M. where ((M. P1 == i) & (M. P2 == j))
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

def normalize_rdd (r):
    sum = float (r. map (lambda x : x[1]). reduce (lambda x, y: x + y))
    r = r.map (lambda x: (x[0], x[1] / sum))
    return r

def pehar_distributed (Mat, target, iters, error = 1.0e-3):

    # Extart Matrix of predictors and the Vector of causalities to the target
    df_predictors = df. where ( (df.P1 != target)  & (df.P2 != target)). select (["P1", "P2", "Caus"])
    df_target = df. where ((df. P1 != target) & (df.P2 == target)). select (["P1", "Caus"])
    
    causalities = df_predictors. join (df_target, on='P1'). rdd. map (lambda x: (x[0], x[1], float (x[2]) * float (x[3]))).toDF(["P1", "P2", "Caus"])
    #causalities. show (13645)
    #exit (1)
    colnames = df.select ("P1"). distinct ()#. sort ("id1") 
    n_nodes = colnames.count ()

    hubs = colnames.select ("P1"). rdd. map (lambda x: (x[0], 1.0 / float (n_nodes) ))
    hubs = hubs. repartition (10)
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
        #hubs = hubs. repartition (10) 
    hubs = hubs. sortBy (lambda x: x[1], ascending= False)
    #hubs = hubs. repartition (10)
    return (auths, hubs)

def select_k_variables (Mat, target, iters, k, error = 1.0e-3):
    hubs = pehar_distributed (Mat, target, iters, error = 1.0e-3)[1].\
    map (lambda x: (target + "_" + str (k), x[0], x[1])).\
    toDF (["Target", "Hubs", "Scores"]). select(["Target", "Hubs"])
    #hubs. show ()
    return hubs. limit (k). rdd. map (lambda x: x)

def select_k (Mat, target, iters, k, error = 1.0e-3):
      hubs = pehar_distributed (Mat, target, iters, error = 1.0e-3)[1].\
      map (lambda x: (target + "_" + str (k), x[0], x[1])).\
      toDF (["Target", "Hubs", "Scores"]). select(["Target", "Hubs"])
      #hubs. show ()
      return hubs. limit (k). rdd. map (lambda x: x). collect ()
 
# Applying the pehar algorithm on all variables of a input dataset
def exec_pehar (input_mat):
    df = sqlcontext.read. parquet ('hdfs://master:9000/user/hduser/matrix_of_depend/' + input_mat)
    targets = df. select (['P1']). distinct (). rdd. map (lambda x: (x, []))
    #targets = sc.parallelize (df. columns). map (lambda x: (x, []))
    print (targets. collect ())
    
def list_to_str (x):
    res = ""
    for y in x:
        res = res + y + " "
    return res 
if __name__ == "__main__":
    
    os.system ("hadoop fs -mkdir -p /user/hduser/features_selection")
    os.system ("hadoop fs -mkdir -p /user/hduser/features_selection/input_mat")
    
    iters = 20
    target_index = 'CAC40'
    input_mat = sys.argv[1]
    #exec_pehar (input_mat)
    #data_name = input_mat. split ('/')[-1]. split ('.')[0]
 
    df = sqlcontext.read. parquet ('hdfs://master:9000/user/hduser/matrix_of_depend/' + input_mat)
    #df. show ()
    #exit (1) 
    targets = df. select ("P1"). distinct ().  rdd. map (lambda x: x[0]). collect ()
    #df. repartition (10)
    #print (targets)
    #targets = [targets[0]]
    #features = targets. map (lambda x: (x, select_k_variables (df, x, iters = iters, k=3). rdd. map (lambda x: x))
    features = sc.emptyRDD () 
    for target in targets:
        hubs = select_k_variables (df, target, iters = iters, k=3)
        #print (hubs. collect ())
        #row = sc. rdd (hubs)
        features = features.union (hubs. map (lambda x:(x[0], [x[1]])))

    #features_ = sc. parallelize (targets). map (lambda x: select_k (df, x, iters = iters, k=3))     
    features = features. reduceByKey (lambda x,y: x + y ).\
    map (lambda x: (x[0].split ('_')[0], x[0].split ('_')[1], x[1])).\
    map (lambda x: (x[0], x[1], list_to_str (x[2]))).\
    toDF (["Col", "NbV", "Hubs"])
    
    features. show ()
    #print (features. rdd. collect ())
    features.write.format("com.databricks.spark.csv").\
    mode("overwrite").\
    option("header", "true").\
    save("/user/hduser/features_selection/" + input_mat + "/features.csv") 
    #features. rdd. saveAsTextFile ("/user/hduser/features_selection/" + input_mat + "/features.txt", mode='overwrite')
    #print (auths. collect ())
    #print (hubs. map (lambda x: x[1]). reduce (lambda x, y: x + y))




