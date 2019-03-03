# This a sample test of the process  on australian macro-economic dataset.

# Put data to hdfs
sh jobs/local_to_distributed.sh data/ausmacro.csv

# Compute the Granger causality graph
sh jobs/causality_mat.sh data/ausmacro

# Execute the Pehar algorithm (feature selection)
sh jobs/pehar_dist.py ausmacro_gc

# Compute prediction
sh jobs/prediction.sh ausmacro
