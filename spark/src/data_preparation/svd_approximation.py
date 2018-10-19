import warnings
warnings.filterwarnings ("ignore", message="numpy.dtype size changed")
warnings.filterwarnings ("ignore", message="numpy.ufunc size changed")

from pyspark import SparkContext
from pyspark import SQLContext
from pyspark import SparkConf
from pyspark.sql.functions import *
#from pyspark.mllib.linalg.distributed import RowMatrix
from pyspark.mllib.linalg import *
#from pyspark.mllib.linalg.distributed import IndexedRow, IndexedRowMatrix
#from pyspark.mllib.linalg.distributed import CoordinateMatrix, MatrixEntry
#from pyspark.mllib.linalg import Matrices

import sys
import os

conf = (SparkConf ())
sc = SparkContext (conf = conf)
sqlcontext =  SQLContext(sc)


def vect_to_dense (V, k):
    j = 0
    SV = []
    for val in V:
        list = [0 for i in range (k)]
        list [j] = val
        SV = SV + list
        j = j + 1
        if j == k:
            break

    S = DenseMatrix(k, k, SV)

    return S
        
if __name__ == "__main__":
    
    input_data = sys.argv [1]
    
    if len (sys.argv) < 2:
        k = 0
    else:
        k = sys.argv [2]   
 
    df = sqlcontext.read. parquet (input_data)
    data_name = input_data. split ('/')[-1]

    df = df. select (["id","time_series"]).rdd. map (lambda x: IndexedRow(x[0], x[1]))
    
    mat = IndexedRowMatrix (df). toBlockMatrix()
    mat = mat.toCoordinateMatrix ()
    mat = mat. transpose (). toIndexedRowMatrix ()

    # SVD decomposition
    svd = mat.computeSVD(3, computeU=True)
    
    U = svd.U
    s = svd.s
    V = svd.V

    # Transform s  from vector to dense Matrix
    m = mat.numRows()
    n = mat.numCols()
    
    # we take top 10% of singular values as default values
    # TODO: find the best k
    if k == 0:
        k = n * 0.1 
    S = vect_to_dense (s, k)
    
    
    # Compute the transpose of the matrix V
    _list = V. toArray(). transpose (). tolist ()
    flat_list = [item for sublist in _list for item in sublist]
    
    Vt = DenseMatrix(k, n, flat_list)

    # Store the matrix U, S, and Vt
    os.system ('hadoop fs -mkdir -p svd_decomposition')
    os.system ('hadoop fs -mkdir -p svd_decomposition/' + data_name)

    # TODO: compute distributed multiplication U.S.Vt 
    M = U. multiply (S)
    #mat = M. multiply (Vt)
    
