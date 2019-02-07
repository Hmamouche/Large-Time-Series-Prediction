#!/bin/bash
# This script generate the SVD approximation of the data
# It has one argumebt, which is the path of the data in the HDFS.
spark-submit --class testspark \
            --master yarn\
 			--deploy-mode client\
    		--py-files tools.zip \
    		src/data_preparation/svd_approximation.py $1
