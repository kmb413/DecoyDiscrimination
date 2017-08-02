#!/usr/bin/env python

import os
import sys
from customIO import resscoresparse 
from plot import conv
from plot import scatterplot
import argparse


def main(rosetta_native, rosetta_decoy, amber_native, amber_decoy, false_scoretype, output_prefix):
    #read in and rename arguments
    #title1 = os.path.basename(input_scores[0][0])

    r_n = resscoresparse.read_vals(rosetta_native, "rosetta", list_energies=["all"])
    r_d = resscoresparse.read_vals(rosetta_decoy, "rosetta", list_energies=["all"])
    a_n = resscoresparse.read_vals(amber_native, "amber", list_energies=["all"])
    a_d = resscoresparse.read_vals(amber_decoy, "amber", list_energies=["all"])

    e_r_n = resscoresparse.get_energies(r_n, "total", sort_by=None)
    e_r_d = resscoresparse.get_energies(r_d, "total", sort_by=None)
    e_a_n = resscoresparse.get_energies(a_n, "tot", sort_by=None)
    e_a_d = resscoresparse.get_energies(a_d, "tot", sort_by=None)

    r_r_n = resscoresparse.gen_ranks(resscoresparse.get_energies(r_n, "total", sort_by=None), reverse=False)
    r_r_d = resscoresparse.gen_ranks(resscoresparse.get_energies(r_d, "total", sort_by=None), reverse=False)
    r_a_n = resscoresparse.gen_ranks(resscoresparse.get_energies(a_n, "tot", sort_by=None), reverse=False)
    r_a_d = resscoresparse.gen_ranks(resscoresparse.get_energies(a_d, "tot", sort_by=None), reverse=False)

    if false_scoretype == "amber":
        false_r_n = r_a_n
        false_r_d = r_a_d
        true_r_n = r_r_n
        true_r_d = r_r_d
        false_n = a_n
        false_d = a_d
	true_n = r_n
        true_d = r_d
    else:
        false_r_n = r_r_n
        false_r_d = r_r_d
        true_r_n = r_a_n
        true_r_d = r_a_d
        false_n = r_n
        false_d = r_d
        true_n = a_n
        true_d = a_d

    counter = 0

    pymol_string = ""

    interval = len(e_r_n)//4

    for i in xrange(0, len(e_r_n)):
        if true_r_n[i] - true_r_d[i] > interval:
	    print i+1
	    if false_r_d[i] - false_r_n[i] < interval:
                print "false minima is similar"
		for st in true_n[i+1].keys():
		    if st == "tot" or st == "total":
 		        continue
		    st_r_d = resscoresparse.gen_ranks(resscoresparse.get_energies(true_d, st))
                    st_r_n = resscoresparse.gen_ranks(resscoresparse.get_energies(true_n, st))

		    if st_r_d[i] - st_r_n[i] > interval:
			print "{0},{1},{2}".format(st, true_d[i+1][st], true_n[i+1][st])
	    pymol_string += "{0}+".format(i+1)
	    counter += 1
            #print ranks_1[i]
	    #print ranks_2[i]

    print counter    
    print pymol_string

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument ('--rosetta_native', help="input score file and its scoretype")
    parser.add_argument ('--rosetta_decoy', help="input score file and its scoretype")
    parser.add_argument ('--amber_native', help="input score file and its scoretype")
    parser.add_argument ('--amber_decoy', help="input score file and its scoretype")
    parser.add_argument ('--false_scoretype', help="which scoretype has the false minimum")
    parser.add_argument ('--output_prefix', help="output prefix for files")

    args = parser.parse_args()

    main(args.rosetta_native, args.rosetta_decoy, args.amber_native, args.amber_decoy, args.false_scoretype, args.output_prefix)
