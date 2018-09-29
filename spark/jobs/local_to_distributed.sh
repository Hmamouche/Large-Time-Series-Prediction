spark-submit --class testspark --master yarn\
 			--deploy-mode client\
    		 src/local_to_hdfs/local_to_distributed.py "$1"
