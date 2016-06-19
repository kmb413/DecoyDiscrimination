#!/usr/bin/env python

import os
import sys
from customIO import scorefileparse
from customIO import discparse
from plot import conv
from plot import scatterplot
from plot import line
from plot import hist
import argparse
from matplotlib import colors

def dominates(row, rowCandidate):
    return all(r <= rc for r, rc in zip(row, rowCandidate))

def cull(pts, dominates):
    dominated = []
    cleared = []
    remaining = pts
    while remaining:
        candidate = remaining[0]
        new_remaining = []
        for other in remaining[1:]:
            [new_remaining, dominated][dominates(candidate, other)].append(other)
        if not any(dominates(other, candidate) for other in new_remaining):
            cleared.append(candidate)
        else:
            dominated.append(candidate)
        remaining = new_remaining
    return cleared, dominated

def gen_ranks(list_energies):
    indices = list(range(len(list_energies)))
    indices.sort(key=lambda x: list_energies[x])
    output = [0] * len(indices)
    for i, x in enumerate(indices):
        output[x] = i
    return output

def find_pareto(dec_inter1, dec_inter2, ax, pdb):

    d1e = scorefileparse.get_energies(dec_inter1[pdb])
    d2e = scorefileparse.get_energies(dec_inter2[pdb])

    r1 = scorefileparse.get_rmsd(dec_inter1[pdb])

    d1e_ranks = gen_ranks(d1e)
    d2e_ranks = gen_ranks(d2e)

    pts = map(list, zip(d1e_ranks, d2e_ranks))

    cleared, dominated = cull(pts, dominates)

    cleared_d = dict(cleared)
    

    pts_r = zip(d1e_ranks,d2e_ranks,r1,sorted(dec_inter1[pdb].keys()))

    pareto_equal_min = min([ e1+e2 for e1,e2 in cleared_d.items() ])
    list_pts =  [ (rosetta,amber,r,key) for rosetta,amber,r,key in pts_r if amber+rosetta == pareto_equal_min ]
    min_filename = find_lowest_point( list_pts )

    return min_filename

def find_lowest_point( list_pts ):
    first_rank_list = [ p[0] for p in list_pts ]
    second_rank_list = [ p[1] for p in list_pts ]
    min_rank = min(first_rank_list + second_rank_list)
    min_point = [ key for e1, e2, r, key in list_pts if min_rank == e1 or min_rank == e2 ][0]
    return min_point

def main(input_dir_1, scoretype1, input_dir_2, scoretype2, output_pre ):
    #read in and rename arguments
    title1 = os.path.basename(input_dir_1)
    title2 = os.path.basename(input_dir_2)

    d1 = scorefileparse.read_dir(input_dir_1, scoretype1, repl_orig=False)
    d2 = scorefileparse.read_dir(input_dir_2, scoretype2, repl_orig=False)

    dec_norm1 = scorefileparse.norm_pdbs(d1)
    dec_norm2 = scorefileparse.norm_pdbs(d2)

    [dec_inter1, dec_inter2] = scorefileparse.pdbs_scores_intersect([dec_norm1, dec_norm2])       

    line_plot_data = {}

    min_naive_by_pdb = {}

    for x_ind,pdb in enumerate(sorted(dec_inter1.keys())):

        min_naive_by_pdb[key] = find_pareto(dec_inter1, dec_inter2, ax, pdb)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument ('--input_dir_rosetta_sf', help="directory for rosetta input score files")
    parser.add_argument ('--input_dir_amber_sf', help="directory for amber input score files")
    parser.add_argument ('--input_dir_rosetta_sf', help="directory for rosetta input score files")
    parser.add_argument ('--input_dir_amber_sf', help="directory for amber input score files")

    parser.add_argument('--output_pre', help='prefix for output figure')
    
    parser.add_argument('--output_pre', help='prefix for output figure')

    args = parser.parse_args()

    main(args.input_dir[0][0], args.input_dir[0][1], args.input_dir[1][0], args.input_dir[1][1], args.output_pre)
