#!/bin/bash
in=$1
out=$2
# $(find $in -name "*.json"); do

for i in $in/*.json; do   
    path=$i
    python3 main.py -o $out $path  
done
