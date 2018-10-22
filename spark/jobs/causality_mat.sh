#!/bin/bash
# Compute the causality graph of a data in the HDFS given as argument
spark-submit --class testspark --master yarn\
 			--deploy-mode client\
    		--py-files tools.zip \
    		src/compute_graphs/causality_mat.py $1 
