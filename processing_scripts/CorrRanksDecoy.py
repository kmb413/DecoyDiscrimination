#!/usr/bin/env python

import os
import sys
from customIO import scorefileparse 
from plot import conv
from plot import scatterplot
import argparse
import scipy.stats.mstats
import numpy as np

def main(input_native, input_decoy, native_name, decoy_name, pdb):
    #read in and rename arguments
    #title1 = os.path.basename(input_scores[0][0])

    native = scorefileparse.read_vals(input_native[0], input_native[1], list_energies=["all"])
    decoy = scorefileparse.read_vals(input_decoy[0], input_decoy[1], list_energies=["all"])

    interval = (len(decoy)+len(native))//4

    ind_native = sorted(native.keys()).index(native_name)
    ind_decoy = sorted(decoy.keys()).index(decoy_name)

    output = ""

    for st in decoy[decoy_name].keys():
        if st == "tot" or st == "total" or st == "rms" or st == "rmsd" or st == "total_score":
 	    continue
        energies = scorefileparse.get_energies_dict(decoy, st) + scorefileparse.get_energies_dict(native, st)
        
        if all( (e - energies[0]) == 0 for e in energies ):
	    continue

        #st_ranks = scorefileparse.gen_ranks(scorefileparse.get_energies_dict(decoy, st) + scorefileparse.get_energies_dict(native, st))

	st_ranks = scipy.stats.mstats.zscore(energies)
        if st_ranks[ind_decoy] - st_ranks[ind_native+len(decoy)] >= 1.0: #z-score of decoy is greater than z-score of native by more than 1 standard deviation
	    output += "{4},{3},{0},{1},{2}\n".format(st, native[native_name][st], decoy[decoy_name][st], decoy_name, pdb)

    return output

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument ('--input_native', nargs=2, help="input score file and its scoretype")
    parser.add_argument ('--input_decoy', nargs=2, help="input score file and its scoretype")
    parser.add_argument ('--native_name', help="name of native to test")
    parser.add_argument ('--decoy_name', help="name of decoy to test")
    parser.add_argument ('--pdb', help="output prefix for files")

    args = parser.parse_args()

    main(args.input_native, args.input_decoy, args.native_name, args.decoy_name, args.pdb)
