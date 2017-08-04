#!/usr/bin/env python

import os
import sys
from customIO import scorefileparse
from customIO import discparse
from plot import conv
from plot import scatterplot
import argparse
import disc

def plot(ax, title, dec_inter, color, y_axis, highlight_outlier=False):

    de = scorefileparse.get_energies(dec_inter)

    dr = scorefileparse.get_rmsd(dec_inter)

    scatterplot.draw_actual_plot(ax, dr, de, color, title, "RMSD", y_axis, alpha=0.6, size=15)

    ranks = scorefileparse.gen_ranks(de) 

    false_minima_r = [ r for r, e, rank in zip(dr, de, ranks) if rank <= 10 and r >= 5.0 ]
    false_minima_e = [ e for r, e, rank in zip(dr, de, ranks) if rank <= 10 and r >= 5.0 ]

    if false_minima_r:
        scatterplot.draw_actual_plot(ax, false_minima_r, false_minima_e, 'k', title, "RMSD", y_axis, alpha=0.6, size=15) 

    if highlight_outlier:
        min_e = [ (e, r) for e, r, rank in zip(de, dr,ranks) if rank == 0 ]
        max_e = [ (e, r) for e, r, rank in zip(de, dr,ranks) if rank == len(ranks)-1 ]
        scatterplot.draw_actual_plot(ax, min_e[0][1], min_e[0][0], 'forestgreen', title, "RMSD", y_axis, alpha=0.6, size=25, edgecolors='k', linewidth=0.5)
        scatterplot.draw_actual_plot(ax, max_e[0][1], max_e[0][0], 'red', title, "RMSD", y_axis, alpha=0.6, size=25, edgecolors='k', linewidth=0.5)

    conv.add_text(ax, "B", discparse.scores_dict_to_metrics(dec_inter)["BinBoltz"])

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

    return ros_norm, amb_norm

def main(rosetta_score_file, amber_score_file, output_prefix, rmsd, list_energies):

    rosetta_scores_dict = scorefileparse.read_vals(rosetta_score_file, "rosetta", rmsd=rmsd, list_energies=list_energies)
    amber_scores_dict = scorefileparse.read_vals(amber_score_file, "amber", rmsd=rmsd, list_energies=list_energies)                                          

    rosetta_scores_dict, amber_scores_dict = inter_norm(rosetta_scores_dict, amber_scores_dict) 

    fig, axarr = conv.create_ax(2, 1, True, True)

    pdb = os.path.splitext(os.path.basename(rosetta_score_file))[0]

    plot(axarr[0,0], "", rosetta_scores_dict, color='darksalmon', y_axis="Normalized Energy")

    plot(axarr[0,1], "", amber_scores_dict, color='darkturquoise', y_axis="")

    filename = output_prefix +  ".txt"

    suffix="{0}_energy_v_rmsd".format(pdb)

    conv.save_fig(fig, filename, suffix, 4.4, 2.2)
 
if __name__ == "__main__":


    parser = argparse.ArgumentParser(description=__doc__)
    
    parser.add_argument ('--rosetta_score_file', help="rosetta score file")
    parser.add_argument ('--amber_score_file', help="amber score file")

    parser.add_argument ('--rmsd_name', type=dict, default={}, help='name of rmsd column. sample: {"rosetta" : "rmsd"}')

    parser.add_argument('--energies_names', type=dict, default={}, help='gives column names to sum over for total score. sample: { "rosetta" : "total_score" }')

    parser.add_argument('--output_prefix', help="Prefix for output file")

    args = parser.parse_args()

    main(args.rosetta_score_file, args.amber_score_file, args.output_prefix, args.rmsd_name, args.energies_names )
