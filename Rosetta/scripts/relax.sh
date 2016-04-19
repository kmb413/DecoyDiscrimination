#!/bin/bash

path=$1
pdb=$2
outpath=$3
pdb_id=$4


strip_pdb="${pdb%.*}"

mkdir -p $outpath'/'$strip_pdb
cd $outpath'/'$strip_pdb

grep -sq "reported success" $strip_pdb'_relax.log' 
if [ $? -gt 0 ]; then
	~/Rosetta/main/source/bin/rosetta_scripts.static.linuxgccrelease -database ~/Rosetta/main/database -nstruct 5 -ex1 -ex2 -extrachi_cutoff 1 -use_input_sc -s $path'/'$pdb -parser:protocol ~/CADRES/DecoyDiscrimination/Rosetta/xml/relax.xml -score:weights talaris2014_cst -overwrite > $strip_pdb'_relax.log' 
fi
