spark-submit --class testspark \
            --executor-cores 5 \
            --master yarn\
 			--deploy-mode client\
    		--py-files tools.zip \
    		src/feature_selection/algo_hits.py $1
