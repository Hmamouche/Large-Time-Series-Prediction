#!/bin/bash
# Making prediction using LSTM model
spark-submit --class testspark --master yarn\
            --num-executors, 1 \ 
            #--executor-cores 5 \
            --master yarn\
            --deploy-mode client\
            --py-files tools.zip \
            src/prediction/lstm.py $1
~                                                 
