# This a sample test of the process  on australian macro-economic dataset.

# To make an example, we create an RDD data from local csv file and put it to hdfs
# This not necessarely if you data is already in hdfs
sh jobs/local_to_distributed.sh data/ausmacro.csv

# Compute the Granger causality graph
sh jobs/causality_mat.sh data/ausmacro

# Execute the Pehar algorithm (feature selection)
sh jobs/pehar_dist.py ausmacro_gc

# Compute predictions
sh jobs/prediction.sh ausmacro
