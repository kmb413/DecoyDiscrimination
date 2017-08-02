#!/usr/bin/env python

import os
import sys
from customIO import resscoresparse 
from plot import conv
from plot import scatterplot
import argparse
import scipy.stats.mstats


def main(rosetta_native, rosetta_decoy, false_scoretype):
    #read in and rename arguments
    #title1 = os.path.basename(input_scores[0][0])

    r_n = resscoresparse.read_vals(rosetta_native, "rosetta", list_energies=["all"])
    r_d = resscoresparse.read_vals(rosetta_decoy, "rosetta", list_energies=["all"])

    e_r_n = resscoresparse.get_energies(r_n, "total", sort_by=None)
    e_r_d = resscoresparse.get_energies(r_d, "total", sort_by=None)

    counter = 0

    pymol_string = ""


    for i in xrange(0, len(e_r_n)):
	dec_ranks = scipy.stats.mstats.zscore(e_r_d)
	nat_ranks = scipy.stats.mstats.zscore(e_r_n)
        ranks = scipy.stats.mstats.zscore(e_r_d+e_r_n)       
	if (false_scoretype == "decoy" and ranks[i] - ranks[i+len(e_r_n)] >= 1.0) or (false_scoretype == "native" and ranks[i+len(e_r_n)] - ranks[i] >= 1.0):
	        pymol_string += "{0}+".format(i+1)
	        counter += 1

    print counter
    print pymol_string

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument ('--rosetta_native', help="input score file and its scoretype")
    parser.add_argument ('--rosetta_decoy', help="input score file and its scoretype")
    parser.add_argument ('--false_scoretype', help="which scoretype has the false minimum")

    args = parser.parse_args()

    main(args.rosetta_native, args.rosetta_decoy, args.false_scoretype)
