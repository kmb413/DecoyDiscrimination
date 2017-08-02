#!/usr/bin/env python

import os
import sys
from customIO import scorefileparse
import argparse
from shutil import copyfile

def main(input_dir, scoretype, pdb_name, target_dir):
    #read in and rename arguments
    scores_dict = scorefileparse.read_vals(os.path.join(input_dir,pdb_name,"score.sc"), scoretype, repl_orig=False)

    lowest_energy_name = [ k for k, e in sorted(scores_dict.items(), key=lambda x: x[1][0]) ][0]

    copyfile(os.path.join(input_dir,pdb_name,lowest_energy_name + "_0001.pdb"), os.path.join(target_dir,pdb_name, "{0}_0001.pdb".format(lowest_energy_name))) 

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument ('--input_dir', '-d', nargs=2, action='append', help="directory for input score files and its scoretype")

    parser.add_argument('--pdb_name', help='pdb name')
    
    parser.add_argument('--target_dir', help='target directory for pdb file')

    args = parser.parse_args()

    main(args.input_dir[0][0], args.input_dir[0][1], args.pdb_name, args.target_dir)
