#!/bin/bash
# Put the data (in argument) from local into HDFS
            #--num-executors 1 \
            #--executor-cores 5 \
spark-submit --class testspark \
            --master yarn\
            --deploy-mode client\
            --py-files tools.zip \
    		 src/local_to_hdfs/local_to_distributed.py "$1"
