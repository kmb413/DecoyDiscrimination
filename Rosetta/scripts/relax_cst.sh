#!/bin/bash

path=$1
pdb=$2
outpath=$3
pdb_id=$4

python /home/arubenstein/CADRES/DecoyDiscrimination/Rosetta/scripts/sidechain_cst_3.py $path'/'$pdb 0.1 0.5

strip_pdb="${pdb%.*}"

const=$path'/'$strip_pdb"_sc.cst"


mkdir -p $outpath
cd $outpath

#loop so that relax occurs 100 times
grep -sq "reported success" $strip_pdb'_relax.log' 
if [ $? -gt 0 ]; then
	
	~/Rosetta/main/source/bin/rosetta_scripts.static.linuxgccrelease -database ~/Rosetta/main/database -nstruct 5 -ex1 -ex2 -extrachi_cutoff 1 -use_input_sc -s $path'/'$pdb -parser:protocol ~/CADRES/DecoyDiscrimination/Rosetta/xml/relax_cst.xml -score:weights talaris2014_cst -overwrite -constraints:cst_fa_file $const  > $strip_pdb'_relax.log' 
fi
