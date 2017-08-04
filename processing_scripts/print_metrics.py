#!/usr/bin/env python

import os
import sys
from customIO import scorefileparse
from customIO import discparse
from plot import conv
from plot import scatterplot
import argparse


def main(input_dir, output_file):
    #read in and rename arguments
    title1 = os.path.basename(input_dir[0][0])

    d1 = scorefileparse.read_dir(input_dir[0][0], input_dir[0][1], repl_orig=False)
    disc_metrics = discparse.pdbs_dict_to_metrics(d1,input_dir[0][1])

    discparse.show_pdbs_dict_metrics(disc_metrics, filename=output_file) 
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument ('--input_dir', '-d', nargs=2, action='append', help="directory for input score files and its scoretype")
    parser.add_argument ('--output_file', help="output file for metrics")

    args = parser.parse_args()

    main(args.input_dir, args.output_file)
