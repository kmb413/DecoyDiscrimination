#!/usr/bin/env python

import os
import sys
from customIO import scorefileparse
from customIO import discparse
from plot import conv
from plot import scatterplot
import argparse

def plot(disc_metrics_1, disc_metrics_2, title1, title2, output_pre, add_slash=True):
    pdbs = sorted(disc_metrics_1.keys())
    n_metrics = len(disc_metrics_1[pdbs[0]])

    fig, axarr = conv.create_ax(n_metrics, 1)

    for x_ind,metric_name in enumerate(disc_metrics_1[pdbs[0]].keys()):
        x = []
        y = []
        ax = axarr[0,x_ind]
        for pdb in pdbs:
            x.append(disc_metrics_1[pdb][metric_name])
            y.append(disc_metrics_2[pdb][metric_name])

        scatterplot.draw_actual_plot(ax, x, y, 'b', metric_name, title1,title2, size=20, edgecolors='k')
        scatterplot.plot_regression(ax,x,y,False)

    if add_slash:
        filename = output_pre + "/" + title1 + "_" + title2 + ".txt"
    else:
	filename = output_pre + title1 + "_" + title2 + ".txt"
    suffix="disc_v_disc"
 
    conv.save_fig(fig, filename, suffix, n_metrics*3, 3, size=9)

def main(input_dir, output_pre, repl_orig):
    #read in and rename arguments
    title1 = os.path.basename(input_dir[0][0])
    title2 = os.path.basename(input_dir[1][0])

    d1 = scorefileparse.read_dir(input_dir[0][0], input_dir[0][1], repl_orig)
    d2 = scorefileparse.read_dir(input_dir[1][0], input_dir[1][1], repl_orig)
    [dec_inter1, dec_inter2] = scorefileparse.pdbs_scores_intersect([d1, d2])       
    disc_metrics_1 = discparse.pdbs_dict_to_metrics(dec_inter1,input_dir[0][1])
    disc_metrics_2 = discparse.pdbs_dict_to_metrics(dec_inter2,input_dir[1][1])
    print len(dec_inter1)
    print len(dec_inter2)
    print disc_metrics_2
    plot(disc_metrics_1, disc_metrics_2, title1, title2, output_pre)
 
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument ('--input_dir', '-d', nargs=2, action='append', help="directory for input score files and its scoretype")

    parser.add_argument('--output_pre', help='prefix for output figure')

    parser.add_argument('--repl_orig', default=False, help='should the original rmsds be replaced')

    args = parser.parse_args()

    main(args.input_dir,args.output_pre, args.repl_orig)
