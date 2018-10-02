# This a sample test of the process  on ebob-l.csv dataset.

# Put data to hdfs
sh jobs/local_to_distributed.sh data/ebob-l.csv

# Compute the Granger causality graph
sh jobs/causality_mat.sh data/ebob-l

# Execute the Pehar algorithm (feature selection)
sh jobs/pehar_dist.py ebob-l_gc

# Compute prediction
sh jobs/prediction.sh ebob-l_gc