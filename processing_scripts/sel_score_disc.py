#!/usr/bin/env python

import os
import sys
from customIO import scorefileparse
from customIO import discparse
from plot import conv
from plot import scatterplot
import disc
import argparse

def main(list_input_dirs, outlier, metric_name):
    #read in and rename arguments
    inp_dir1=list_input_dirs[0][0]
    scoretype1=list_input_dirs[0][1]
    inp_dir2=list_input_dirs[1][0]
    scoretype2=list_input_dirs[1][1]

    title1 = os.path.basename(inp_dir1)
    title2 = os.path.basename(inp_dir2)

    dec1, nat1 = scorefileparse.read_dec_nat(inp_dir1, [], scoretype1)
    dec2, nat2 = scorefileparse.read_dec_nat(inp_dir2, [], scoretype2)

    [dec_inter1, nat_inter1, dec_inter2, nat_inter2] = scorefileparse.pdbs_intersect([dec1, nat1, dec2, nat2]) 

    for x_ind,pdb in enumerate(sorted(dec_inter1.keys())):

        ddata1 = discparse.scores_dict_to_metrics(dec_inter1[pdb])
        ddata2 = discparse.scores_dict_to_metrics(dec_inter2[pdb])
        merged_dict = scorefileparse.merge_dicts([dec_inter1[pdb],dec_inter2[pdb]])
        ddata3 = discparse.scores_dict_to_metrics(merged_dict)

        disc1 = ddata1[metric_name]
        disc2 = ddata2[metric_name]
        disc3 = ddata3[metric_name]

        d_dict = { title1 : disc1, title2 : disc2, "Combined" : disc3}

        sorted_disc = sorted(d_dict.values())
        max_title = [ t for t,v in d_dict.items() if v == sorted_disc[0] ]
        second_max_title = [ t for t,v in d_dict.items() if v == sorted_disc[1] ]

        diff = sorted_disc[0] - sorted_disc[1]

        fulldiff = abs(sorted_disc[0] - sorted_disc[2])

        if fulldiff > outlier:
            print "{6} -- {0}: {1:.2f}, {2}: {3:.2f}, {4}: {5:.2f} -- {7} better than {8} by {9:.2f}".format(title1, disc1, title2, disc2, "Combined", disc3, pdb, max_title, second_max_title, diff)
        
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument ('--input_dir', '-d', nargs=2, action='append', help="directory for input score files and its scoretype")

    parser.add_argument('--outlier_diff', default=0, type=float,
                   help='defines an outlier.  best_disc - worst_disc must be higher than this number to qualify as an outlier')

    parser.add_argument('--metric_name', default="Disc", help="metric name to define discrimination")

    args = parser.parse_args()

    main(args.input_dir, args.outlier_diff, args.metric_name)    
