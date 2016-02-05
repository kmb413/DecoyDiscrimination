#!/bin/bash

path=$1
outpath=$2

cd $path
counter=1

pdb_id=$(basename $path)

for pdb in $(ls *.pdb)
do
     counter=$((counter+1))
     nohup ~/CADRES/scripts/sc_relax_sc.sh $path $pdb $outpath'/'$pdb_id &
     if (( $counter % 60 == 0 )); then wait; fi
done
