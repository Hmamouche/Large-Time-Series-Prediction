
import warnings
warnings.filterwarnings ("ignore", message="numpy.dtype size changed")
warnings.filterwarnings ("ignore", message="numpy.ufunc size changed")

from pyspark import SparkContext
from pyspark import SQLContext
from pyspark import SparkConf
from pyspark.sql.functions import *

import sys
import os

conf = (SparkConf () .set ("num-executors", "2")
                    .setAppName("Create the dataFrame"))
sc = SparkContext (conf = conf)
sqlcontext =  SQLContext(sc)

def local_to_hdfs (data_path):
    print (data_path. split ('/')[-1])
    #data_path = data_path. split ('/')[-1]
    
    put_file_to_hdfs_command = "hdfs dfs -put -f " + data_path
    print (put_file_to_hdfs_command)
    try:
        os.system (put_file_to_hdfs_command)
    except ValueError:
        print (ValueError)    
    data_name = data_path. split ('/')[-1]. split ('.')[0]
    print (data_name)
    df = sqlcontext.read.load (data_path. split ('/')[-1],
                        format='csv',  
                        header='true',
                        inferSchema='true',
                        inferschema='true',
                        comment = '#',
                        sep = ';')
                           
    cols = df.columns[1:]
      
    rdd = sc.parallelize ((cols. index (cols[i]), cols[i], df.select (cols[i]). toPandas() [cols[i]]. tolist ()) for i in range (len (cols)))
    rdd. toDF (["id", "colname", "time_series"]). show ()
    rdd. toDF (["id", "colname", "time_series"]). write. parquet ("/user/hduser/data/" + data_name, mode='overwrite')

if __name__ == "__main__":

    print ("Put a local file to HDFS")
    input_data = sys.argv[1]
    local_to_hdfs (input_data)
