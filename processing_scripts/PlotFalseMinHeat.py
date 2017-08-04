#!/usr/bin/env python

"""Create edges and nodes from a list of sequences that are a given hamming distance apart"""
import numpy as np
import argparse
from plot import conv as conv
from plot import heat
import matplotlib.pyplot as plt
import math

def read_data_plot(fig, ax, ax2, csv_vals, colormap):
    with open(csv_vals) as f:
        data = f.readlines()

    lines = [ d.strip().split(',') for d  in data ]

    xticklabels = lines[0][1:]

    data = [ map(float,l[1:]) for l in lines[1:] ]

    yticklabels = [ l[0] for l in lines[1:] ]

    xticks = [ i + 0.5 for i in np.arange(len(lines[0])-1) ]
    yticks = [ i + 0.5 for i in np.arange(len(lines)-1) ]

    heat.plot_heatmap(ax, data, colormap, xticks, yticks, xticklabels, yticklabels, "", "", "", colorbar_fig=ax2, set_under_color=None, sep_colorbar=True)
    ax.set_aspect('equal')


def main(csv_vals_rosetta, csv_vals_amber, output_prefix):

    fig, axarr = conv.create_ax(1, 1, shx=False, shy=False)
    fig_c, axarr_c = conv.create_ax(1, 1, shx=False, shy=False)

    read_data_plot(fig, axarr[0,0], axarr_c[0,0], csv_vals_rosetta, plt.cm.Reds)

    conv.save_fig(fig, output_prefix, "rosetta_heatmap", 4.6*0.8, 12*0.8, tight=True, size=8)
    conv.save_fig(fig_c, output_prefix, "rosetta_heatmap_bar", 0.8, 12, tight=True, size=8)

    fig, axarr = conv.create_ax(1, 1, shx=False, shy=False)
    fig_c, axarr_c = conv.create_ax(1, 1, shx=False, shy=False)

    read_data_plot(fig, axarr[0,0], axarr_c[0,0], csv_vals_amber, plt.cm.Blues)

    conv.save_fig(fig, output_prefix, "amber_heatmap", 2.2, 7.35, tight=True, size=8)
    conv.save_fig(fig_c, output_prefix, "amber_heatmap_bar", 0.8*0.8, 12*0.8, tight=True, size=8)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument ('--csv_vals_rosetta', '-d') 
    parser.add_argument ('--csv_vals_amber')
    parser.add_argument ('--output_prefix')

    args = parser.parse_args()

    main(args.csv_vals_rosetta, args.csv_vals_amber, args.output_prefix)
