#!/bin/bash

path=$1
filename=$2
outpath=$3
pdb_id=$4

mkdir -p $outpath
cd $outpath
	
echo "SEQUENCE" > $outpath'/'$pdb_id'.sc' && grep "^SCORE" $path'/'$filename | grep -v "OLD SCORE" | grep -v "_0002$" >> $outpath'/'$pdb_id'.sc'

sed -i 's/ score / total_score /g' $outpath'/'$pdb_id'.sc'
