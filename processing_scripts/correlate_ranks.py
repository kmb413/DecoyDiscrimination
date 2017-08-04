#!/usr/bin/env python

import os
import sys
from customIO import resscoresparse 
from plot import conv
from plot import scatterplot
import argparse


def main(rosetta_native, rosetta_decoy, false_scoretype, pdb):
    #read in and rename arguments
    #title1 = os.path.basename(input_scores[0][0])

    r_n = resscoresparse.read_vals(rosetta_native, "rosetta", list_energies=["all"])
    r_d = resscoresparse.read_vals(rosetta_decoy, "rosetta", list_energies=["all"])

    e_r_n = resscoresparse.get_energies(r_n, "total", sort_by=None)
    e_r_d = resscoresparse.get_energies(r_d, "total", sort_by=None)

    r_r_n = resscoresparse.gen_ranks(resscoresparse.get_energies(r_n, "total", sort_by=None), reverse=False)
    r_r_d = resscoresparse.gen_ranks(resscoresparse.get_energies(r_d, "total", sort_by=None), reverse=False)

    true_r_n = r_r_n
    true_r_d = r_r_d
    true_n = r_n
    true_d = r_d

    counter = 0

    pymol_string = ""

    interval = len(e_r_n)//4

    output = ""

    energies = e_r_d + e_r_n

    if all( (e - energies[0]) == 0 for e in energies ):
            continue

        #st_ranks = scorefileparse.gen_ranks(scorefileparse.get_energies_dict(decoy, st) + scorefileparse.get_energies_dict(native, st))

    ranks = scipy.stats.mstats.zscore(energies)

    for i in xrange(0, len(e_r_n)):
        if true_r_n[i] - true_r_d[i] > interval:
	    #output += "{0}\n".format(i+1)
            if true_r_n: #just don't feel like indenting
		for st in true_n[i+1].keys():
		    if st == "tot" or st == "total":
 		        continue
		    st_r_d = resscoresparse.gen_ranks(resscoresparse.get_energies(true_d, st))
                    st_r_n = resscoresparse.gen_ranks(resscoresparse.get_energies(true_n, st))

		    if st_r_d[i] - st_r_n[i] > interval:
			output += "{5},{4},{3},{0},{1},{2}\n".format(st, true_d[i+1][st], true_n[i+1][st], i+1, os.path.splitext(os.path.basename(rosetta_decoy))[0][0:-5], pdb)
	    pymol_string += "{0}+".format(i+1)
	    counter += 1
            #print ranks_1[i]
	    #print ranks_2[i]

    output += "{0}\n".format(counter)   
    output += "{0}\n".format(pymol_string)

    return output
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument ('--rosetta_native', help="input score file and its scoretype")
    parser.add_argument ('--rosetta_decoy', help="input score file and its scoretype")
    parser.add_argument ('--false_scoretype', help="which scoretype has the false minimum")
    parser.add_argument ('--pdb', help="output prefix for files")

    args = parser.parse_args()

    main(args.rosetta_native, args.rosetta_decoy, args.false_scoretype, args.pdb)
