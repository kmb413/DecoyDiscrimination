#!/usr/bin/env python

import os
import sys
from customIO import scorefileparse
from customIO import discparse
from plot import conv
from plot import scatterplot
import argparse
import disc

def plot(ax, title, dec_inter, nat_inter, disc, xtitle):

    de = scorefileparse.get_energies(dec_inter)
    ne = scorefileparse.get_energies(nat_inter)

    dr = scorefileparse.get_rmsd(dec_inter)
    nr = scorefileparse.get_rmsd(nat_inter)

    scatterplot.draw_actual_plot(ax, dr, de, 'blue', title, xtitle, "Energy")

    scatterplot.draw_actual_plot(ax, nr, ne, 'red', title, xtitle, "Energy")

    conv.add_text_dict(ax, disc)

def get_disc(scores_dict):
    ddata1 = scorefileparse.convert_disc(scores_dict)

    disc_divs = [1.0,1.5,2.0,2.5,3.0,4.0,6.0]

    disc1, d, counts = disc.given_data_run_disc(ddata1, True, disc_divs)

    return disc1

def get_pdbs_dict(input_dir, scoretype, rmsd_cutoff, rmsd, list_energies):
    dec_orig, nat_orig = scorefileparse.read_dec_nat(input_dir, scoretype, repl_orig=False, rmsd=rmsd, list_energies=list_energies)
	
    [dec,nat] = scorefileparse.pdbs_intersect([dec_orig,nat_orig])

    dec_norm = scorefileparse.norm_pdbs(dec)
    nat_norm = scorefileparse.norm_pdbs(nat,dec)

    dec_norm = scorefileparse.filter_norm_pdbs(dec_norm, True)
    nat_norm = scorefileparse.filter_norm_pdbs(nat_norm, True)

    dec_filt = scorefileparse.filter_pdbs_by_rmsd(dec_norm, rmsd_cutoff)
    nat_filt = scorefileparse.filter_pdbs_by_rmsd(nat_norm, rmsd_cutoff)

    return dec_filt, nat_filt, dec

def plot_pdbs_dict(axarr, x_ind, dec_inter, nat_inter, dec_unnorm, title,xtitle):

    for ind, pdb in enumerate(sorted(dec_inter.keys())):

        ax = axarr[ind,x_ind]

        plot(ax, title + " " + pdb, dec_inter[pdb], nat_inter[pdb], discparse.scores_dict_to_metrics(dec_unnorm[pdb]), xtitle)


def main(list_dirs, rmsd_cutoff, output_prefix, rmsd, list_energies):

    dec_list = []
    nat_list = []
    dec_u_list = []

    for d in list_dirs:
        scoretype = d[1]
        dec, nat, dec_unnorm = get_pdbs_dict(d[0], scoretype, rmsd_cutoff, rmsd.get(scoretype), list_energies.get(scoretype)) #returns None if those values aren't present in dicts
        dec_list.append(dec)
        nat_list.append(nat)
        dec_u_list.append(dec_unnorm)

    dec_list_inter = scorefileparse.pdbs_scores_intersect(dec_list)
    nat_list_inter = scorefileparse.pdbs_scores_intersect(nat_list)
        
    fig, axarr = conv.create_ax(len(list_dirs), len(dec_list_inter[0].keys()), True, True)

    for ind,d in enumerate(dec_list_inter):
        title_pre = os.path.basename(list_dirs[ind][0])
	if ind % 2 == 1:
	    xtitle="RMSD"
	else:
	#    xtitle="RMSD SUPLOOP"
            xtitle="RMSD"
	plot_pdbs_dict(axarr, ind, d, nat_list_inter[ind], dec_u_list[ind], title_pre, xtitle)

    filename = output_prefix +  ".txt"

    suffix="energy_v_rmsd_{0}".format(rmsd_cutoff)

    dicts_list = [ (dec_dict, nat_dict) for dec_pdbs_dict,nat_pdbs_dict in zip(dec_list_inter,nat_list_inter) for dec_dict, nat_dict in zip(dec_pdbs_dict.values(), nat_pdbs_dict.values())]
    y_vals = [ scorefileparse.get_energies(dec_scores) + scorefileparse.get_energies(nat_scores) for (dec_scores, nat_scores) in dicts_list ]
    x_vals = [ scorefileparse.get_rmsd(dec_scores) + scorefileparse.get_rmsd(nat_scores) for (dec_scores, nat_scores) in dicts_list ]

    max_e = max([ max(vals) for vals in y_vals ])
    min_e = min([ min(vals) for vals in y_vals ])
    max_r = max([ max(vals) for vals in x_vals ])

    axarr[0][0].set_xlim(-0.2,max_r+0.2)
    axarr[0][0].set_ylim(min_e-0.1,max_e+0.5)

    conv.save_fig(fig, filename, suffix, len(dec_list_inter)*3, len(dec_list_inter[0].keys())*3)
 
if __name__ == "__main__":


    parser = argparse.ArgumentParser(description=__doc__)
    
    parser.add_argument ('--input_dir', '-d', nargs=2, action='append', help="directory for input score files and its scoretype")

    parser.add_argument ('--rmsd_name', type=dict, default={}, help='name of rmsd column. sample: {"rosetta" : "rmsd"}')

    parser.add_argument('--energies_names', type=dict, default={}, help='gives column names to sum over for total score. sample: { "rosetta" : "total_score" }')

    parser.add_argument('--rmsd_cutoff', default=50, type=float,
                   help='RMSD cutoff to consider energies')

    parser.add_argument('--output_prefix', help="Prefix for output file")

    args = parser.parse_args()

    main(args.input_dir, args.rmsd_cutoff, args.output_prefix, args.rmsd_name, args.energies_names )
