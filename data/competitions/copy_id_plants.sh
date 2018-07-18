#!/bin/bash
declare -a arr=("id_1.csv" "id_2.csv" "id_3.csv")

for d in "${arr[@]}"
do
    cp -f $d ../
    scp  -P 9244  $d yussef@s0.mydevil.net:causality-features-selection/data/
done
#




