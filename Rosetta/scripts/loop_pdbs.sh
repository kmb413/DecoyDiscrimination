#!/bin/bash

path=$1
outpath=$2
script=$3
max_cores=$4

cd $path
counter=1

#pdb_id=$(basename $path)

for pdb in $(ls *.pdb)
do
     counter=$((counter+1))
     eval nohup "/home/arubenstein/CADRES/DecoyDiscrimination/Rosetta/scripts/$script" $path $pdb $outpath &
     if (( $counter % 50 == 0 )); 
	then 
	wait
	fi
done
