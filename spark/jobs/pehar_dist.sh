#!/bin/bash
# feature selection with pehar algorithm

spark-submit --class testspark \
            --num-executors, 1 \
            #--executor-cores 5 \
            --master yarn\
 			--deploy-mode client\
    		--py-files tools.zip \
    		src/feature_selection/pehar_dist.py $1
