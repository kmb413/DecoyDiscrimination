#!/bin/bash

path=$1
pdb=$2
outpath=$3
pdb_id=$4

strip_pdb="${pdb%.*}"


mkdir -p $outpath
cd $outpath
	
grep -sq "reported success" $strip_pdb'_rmsd.log'
if [ $? -gt 0 ]; then
	~/Rosetta/main/source/bin/score.static.linuxgccrelease -database ~/Rosetta/main/database -ex1 -ex2 -extrachi_cutoff 1 -use_input_sc -s $path'/'$pdb -score:weights talaris2014 > $strip_pdb'_score.log'
	rm $strip_pdb'_0001.pdb'
fi
