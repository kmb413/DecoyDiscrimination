#!/usr/bin/env python

import os
import sys
from customIO import scorefileparse
from customIO import discparse
from plot import conv
from plot import scatterplot
import argparse
import disc
from matplotlib.backends.backend_pdf import PdfPages

def plot(ax, title, dec_inter, color, x_axis, y_axis, highlight_outlier=False):

    de = scorefileparse.get_energies(dec_inter)

    dr = scorefileparse.get_rmsd(dec_inter)

    scatterplot.draw_actual_plot(ax, dr, de, color, title, x_axis, y_axis, alpha=0.6, size=15)
    ranks = scorefileparse.gen_ranks(de) 

    false_minima_r = [ r for r, e, rank in zip(dr, de, ranks) if rank <= 10 and r >= 5.0 ]
    false_minima_e = [ e for r, e, rank in zip(dr, de, ranks) if rank <= 10 and r >= 5.0 ]

    if false_minima_r:
        scatterplot.draw_actual_plot(ax, false_minima_r, false_minima_e, 'k', title, x_axis, y_axis, alpha=0.6, size=15) 

    if highlight_outlier:
        min_e = [ (e, r) for e, r, rank in zip(de, dr,ranks) if rank == 0 ]
        max_e = [ (e, r) for e, r, rank in zip(de, dr,ranks) if rank == len(ranks)-1 ]
        scatterplot.draw_actual_plot(ax, min_e[0][1], min_e[0][0], 'forestgreen', title, x_axis, y_axis, alpha=0.6, size=25, edgecolors='k', linewidth=0.5)
        scatterplot.draw_actual_plot(ax, max_e[0][1], max_e[0][0], 'red', title, x_axis, y_axis, alpha=0.6, size=25, edgecolors='k', linewidth=0.5)

    B = discparse.scores_dict_to_metrics(dec_inter)["BinBoltz"]

    conv.add_text(ax, "B", B)

    return B
def get_disc(scores_dict):
    ddata1 = scorefileparse.convert_disc(scores_dict)

    disc_divs = [1.0,1.5,2.0,2.5,3.0,4.0,6.0]

    disc1, d, counts = disc.given_data_run_disc(ddata1, True, disc_divs)

    return disc1

def inter_norm(rosetta_scores, amber_scores):
    [ros, amb] = scorefileparse.scores_intersect([rosetta_scores,amber_scores])

    perc_low, perc_high = scorefileparse.find_perc(ros)

    ros_norm = scorefileparse.norm_vals(ros, perc_low, perc_high)

    perc_low, perc_high = scorefileparse.find_perc(amb)

    amb_norm = scorefileparse.norm_vals(amb, perc_low, perc_high)

    ros_filt = scorefileparse.filter_norm (ros_norm, low_also=False)
    amb_filt = scorefileparse.filter_norm (amb_norm, low_also=False)

    [ ros_f, amb_f ] = scorefileparse.scores_intersect([ros_filt, amb_filt])
    return ros_f, amb_f

def main(rosetta_score_dir, amber_score_dir, output_prefix, rmsd, list_energies):

    rosetta_pdb_dict = scorefileparse.read_dir(rosetta_score_dir, "rosetta", rmsd=rmsd, list_energies=list_energies)
    amber_pdb_dict = scorefileparse.read_dir(amber_score_dir, "amber", rmsd=rmsd, list_energies=list_energies)                                          
    B_dict = {}

    with PdfPages(output_prefix + "energy_v_rmsd.pdf") as pdf:
	fig, axarr = conv.create_ax(4, 6, False, False)
        for index, key in enumerate(sorted(rosetta_pdb_dict.keys()), 2):
            rosetta_scores_dict = rosetta_pdb_dict[key]
            amber_scores_dict = amber_pdb_dict[key]

            rosetta_scores_dict, amber_scores_dict = inter_norm(rosetta_scores_dict, amber_scores_dict) 

	    curr_ind = index%12

            if curr_ind == 0:
                fig, axarr = conv.create_ax(4, 6, False, False)

            pdb = key

            x_axis=""
            y_axis=""

            if curr_ind >= 10:
                x_axis = "RMSD"
	    if curr_ind%2==0:
                y_axis = "Normalized Energy"

            ros_B = plot(axarr[curr_ind//2,curr_ind%2*2+0], key, rosetta_scores_dict, color='darksalmon', x_axis=x_axis, y_axis=y_axis)

            amb_B = plot(axarr[curr_ind//2,curr_ind%2*2+1], key, amber_scores_dict, color='darkturquoise', x_axis=x_axis, y_axis="")
	    B_dict[pdb] = (ros_B, amb_B)
	    
	    if index == 11:
	       axarr[0, 0].axis('off')
               axarr[0, 1].axis('off')
               axarr[0, 2].axis('off')
               axarr[0, 3].axis('off')

	    if curr_ind == 11: 
               conv.save_fig(fig, pdf, "", 8.5, 11.0, format="pdf", size=8)
	    if index == len(rosetta_pdb_dict)+1 and curr_ind != 11:
	       for ind in range(curr_ind+1, 12):
                   axarr[ind//2, ind%2*2+0].axis('off')
                   axarr[ind//2, ind%2*2+1].axis('off')
               conv.save_fig(fig, pdf, "", 8.5, 11.0, format="pdf", size=8, tight=True)

    with open(output_prefix + "B_vals.csv", "w") as csv:
        csv.write("\n".join("{0},{1:.2f},{2:.2f}".format(key, ros, amb) for key, (ros, amb) in B_dict.items() ))

if __name__ == "__main__":


    parser = argparse.ArgumentParser(description=__doc__)
    
    parser.add_argument ('--rosetta_score_dir', help="rosetta score file")
    parser.add_argument ('--amber_score_dir', help="amber score file")

    parser.add_argument ('--rmsd_name', type=dict, default={}, help='name of rmsd column. sample: {"rosetta" : "rmsd"}')

    parser.add_argument('--energies_names', type=dict, default={}, help='gives column names to sum over for total score. sample: { "rosetta" : "total_score" }')

    parser.add_argument('--output_prefix', help="Prefix for output file")

    args = parser.parse_args()

    main(args.rosetta_score_dir, args.amber_score_dir, args.output_prefix, args.rmsd_name, args.energies_names )
