#!/bin/bash
path_dst=../../
path_src=data_per_variable
for f in $path_src/*.csv
do
    echo $(basename $f)
    file_dst=$(basename $f)
    echo ${path_dst}${file_dst}
#rm -f ${path_dst}${file_dst}
    cp  $f ${path_dst}
#scp  -P 9244  $f yussef@s0.mydevil.net:causality-features-selection/data/
done



