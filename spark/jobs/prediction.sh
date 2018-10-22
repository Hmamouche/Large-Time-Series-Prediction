#!/bin/bash
# Making prediction using LSTM model
spark-submit --class testspark --master yarn\
            --deploy-mode client\
            --py-files tools.zip \
            src/prediction/lstm.py $1
~                                                 
