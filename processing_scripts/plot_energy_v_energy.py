#!/usr/bin/env python

import os
import sys
from customIO import scorefileparse
from customIO import discparse
from plot import conv
from plot import scatterplot
import argparse

def plot(dec_inter1, dec_inter2, nat_inter1, nat_inter2, ax, pdb, title1, title2):

    d1e = scorefileparse.get_energies(dec_inter1[pdb])
    d2e = scorefileparse.get_energies(dec_inter2[pdb])
    n1e = scorefileparse.get_energies(nat_inter1[pdb])
    n2e = scorefileparse.get_energies(nat_inter2[pdb])

    r = scorefileparse.get_rmsd(dec_inter1[pdb])

    scatterplot.draw_actual_plot(ax, d1e, d2e, r, pdb, title1,title2)

    #scatterplot.draw_actual_plot(ax, n1e, n2e, [], pdb, title1,title2)

    scatterplot.plot_regression(ax, scorefileparse.get_energies(dec_inter1[pdb])+scorefileparse.get_energies(nat_inter1[pdb])
                                ,scorefileparse.get_energies(dec_inter2[pdb])+scorefileparse.get_energies(nat_inter2[pdb]),False)


def main(args):
    #read in and rename arguments
    title1 = os.path.basename(args.input_dir_1)
    title2 = os.path.basename(args.input_dir_2)

    d1, n1 = scorefileparse.read_dec_nat(args.input_dir_1, [], args.scoretype1, True)
    d2, n2 = scorefileparse.read_dec_nat(args.input_dir_2, [], args.scoretype2, True)

    dec1 = scorefileparse.filter_pdbs_by_rmsd(d1, args.rmsd_cutoff)
    nat1 = scorefileparse.filter_pdbs_by_rmsd(n1, args.rmsd_cutoff)
    dec2 = scorefileparse.filter_pdbs_by_rmsd(d2, args.rmsd_cutoff)
    nat2 = scorefileparse.filter_pdbs_by_rmsd(n2, args.rmsd_cutoff)

    dec_norm1 = scorefileparse.norm_pdbs(dec1)
    nat_norm1 = scorefileparse.norm_pdbs(nat1,dec1)
    dec_norm2 = scorefileparse.norm_pdbs(dec2)
    nat_norm2 = scorefileparse.norm_pdbs(nat2,dec2)

    [dec_inter1, nat_inter1, dec_inter2, nat_inter2] = scorefileparse.pdbs_intersect([dec_norm1, nat_norm1, dec_norm2, nat_norm2]) 
    [dec_inter1, dec_inter2] = scorefileparse.pdbs_scores_intersect([dec_inter1, dec_inter2])       
    [nat_inter1, nat_inter2] = scorefileparse.pdbs_scores_intersect([nat_inter1, nat_inter2])       

    dec_filt1 = scorefileparse.filter_norm_pdbs(dec_norm1)
    nat_filt1 = scorefileparse.filter_norm_pdbs(nat_norm1)
    dec_filt2 = scorefileparse.filter_norm_pdbs(dec_norm2)
    nat_filt2 = scorefileparse.filter_norm_pdbs(nat_norm2)

    [dec_finter1, dec_finter2] = scorefileparse.pdbs_scores_intersect([dec_filt1, dec_filt2])
    [nat_finter1, nat_finter2] = scorefileparse.pdbs_scores_intersect([nat_filt1, nat_filt2])

    fig, axarr = conv.create_ax(2, len(dec_inter1))

    for x_ind,pdb in enumerate(sorted(dec_inter1.keys())):

        ax = axarr[x_ind, 0] 

	    plot(dec_inter1, dec_inter2, nat_inter1, nat_inter2, ax, pdb, title1, title2)

	    ax = axarr[x_ind, 1]

	    plot(dec_finter1, dec_finter2, nat_finter1, nat_finter2, ax, pdb, title1, title2)

    filename = args.input_dir_1 + "/" + title1 + "_" + title2 + ".txt"   

    suffix="energy_v_energy_{0}".format(args.rmsd_cutoff)
 
    conv.save_fig(fig, filename, suffix, 7, len(dec_inter1)*3)
 
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input_dir_1',
		   help='first directory for input score files')
    parser.add_argument('scoretype1',
                   help='score type of first dir of score files')
    parser.add_argument('input_dir_2', 
                   help='second directory for input score files')
    parser.add_argument('scoretype2',
                   help='score type of second dir of score files')
    parser.add_argument('--rmsd_cutoff', default=50, type=float,
		   help='RMSD cutoff to consider energies')

    args = parser.parse_args()

    main(args)
