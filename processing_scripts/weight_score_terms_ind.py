#!/usr/bin/env python

'''weight each score term individually. contour plots, true parameter sweep'''

import os
import sys
from customIO import scorefileparse
from customIO import discparse
from plot import conv
from plot import scatterplot
import disc
import argparse
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
import json
import plot_disc_v_disc as pdvd

def loop_weights(energies, weights, scales, offsets, dec1, inp_dir2, scoretype2, curr_weights, list_weight_discs):
    if len(curr_weights) == len(energies):
        dec2 = scorefileparse.read_dir(inp_dir2, scoretype2, list_energies=energies, weights=curr_weights, scales=scales, offsets=offsets)
        [dec_inter1, dec_inter2] = scorefileparse.pdbs_intersect([dec1, dec2])
        merged = scorefileparse.merge_pdbs_dicts([dec_inter1, dec_inter2])

        list_discs = discparse.pdbs_dict_to_metrics(merged)
        for ind, weight in enumerate(curr_weights):
            list_weight_discs[ind].append(weight)
        list_weight_discs[-1].append(list_discs)
        return 

    energies_ind = len(curr_weights)

    list_weights = weights[energies_ind]
    for w in list_weights:
        temp_weights = curr_weights[:]
        temp_weights.append(w)
        loop_weights(energies, weights, scales, offsets, dec1, inp_dir2, scoretype2, temp_weights, list_weight_discs)

def get_weights(energies, w_means, w_binsizes, w_nbins):
    weights = {}
    for e in energies:
        mean = w_means.get(e, 0)
        bsize = w_binsizes.get(e, 25)
        nbin = w_nbins.get(e, 6)
        dist = bsize*((nbin-1.0)/2.0)
        weights[e] = np.linspace(mean-dist, mean+dist, num=nbin) 
    return weights

def deltaS_pdbs_disc_dict(pdbs_disc_dict, ref_disc):
    pdbs_deltaS = { pdb : metrics["Disc"] - ref_disc[pdb]["Disc"] for pdb,metrics in pdbs_disc_dict.items() }
    return pdbs_deltaS

def avg_pdbs_deltaS(pdbs_deltaS):
    return sum(pdbs_deltaS.values())/len(pdbs_deltaS)

def convert_list_dict(list_energies_names, split=True, conv_float=False):
    
    if list_energies_names:
        new_d = dict(list_energies_names)
        if conv_float and split:
            new_d = { k :  (float(item) for item in v.split(',')) for k,v in new_d.items() }
        elif conv_float:
            new_d = { k :  float(v) for k,v in new_d.items() }
        elif split:
            new_d = { k :  v.split(',') for k,v in new_d.items() }
    else:
        new_d = {}
    return new_d

def plot_weights_dS(w_dS_sorted, col_dS, unique_z_vals, title1, title2, x_axis_name, y_axis_name, z_axis_name):
    n_unique_z_vals = unique_z_vals.shape[0]

    fig, axarr = conv.create_ax(n_unique_z_vals, 1, True,True)

    #find values in row of total_min
    min_vals = w_dS_sorted[w_dS_sorted[:,col_dS]==np.amin(w_dS_sorted[:,col_dS]),:]
    min_dS = min_vals[0,col_dS]
    max_dS = np.amax(w_dS_sorted[:,col_dS])
    dS_list = sorted(w_dS_sorted[:,col_dS].tolist())
    nlev = len(dS_list)/10 if len(dS_list)>10 else len(dS_list)/2
    levels = dS_list[0::nlev]

    subtitle_prefix = z_axis_name + ": "
    xlabel = x_axis_name + " Weights"
    ylabel = y_axis_name + " Weights"

    for ax_ind,z_val in enumerate(sorted(unique_z_vals.tolist())):
        ax = axarr[0,ax_ind]
        x = w_dS_sorted[w_dS_sorted[:,2]==z_val,0]
        y = w_dS_sorted[w_dS_sorted[:,2]==z_val,1]
        dS = w_dS_sorted[w_dS_sorted[:,2]==z_val,col_dS]
        X = x.reshape(-1, n_unique_z_vals)
        Y = y.reshape(-1, n_unique_z_vals)
        DS = dS.reshape(-1, n_unique_z_vals)

        curr_min_ind = np.argmin(dS)

        CS = ax.contourf(X, Y, DS,
                   extend='both', levels=levels)

        CSlines = ax.contour(X, Y, DS, linestyles='solid',
                  colors=('w',), levels=levels)
        if z_val == min_vals[0,2]:
            min_x = [min_vals[0,0]]
            min_y = [min_vals[0,1]]
            min_ds = [min_vals[0,col_dS]]
            ann_txt = "Global Minimum: {2:.2f} at ({0:.2f}, {1:.2f})".format(min_x[0], min_y[0], min_ds[0])
            ax.scatter(min_x, min_y, c='r', zorder=1)
        else:
            min_x = [x[curr_min_ind]]
            min_y = [y[curr_min_ind]]
            min_ds = [dS[curr_min_ind]]
            ann_txt = "Minimum: {2:.2f} at ({0:.2f}, {1:.2f})".format(min_x[0], min_y[0], min_ds[0])
            ax.scatter(min_x, min_y, c='k', zorder=1)

        ax.annotate(ann_txt, xy=(min_x[0], min_y[0]), xytext=(-20,20),
            textcoords='offset points', ha='center', va='bottom',
            bbox=dict(boxstyle='round,pad=0.2', fc='yellow', alpha=0.3),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.5',
                            color='red'),size=10)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title("{0} : {1:.2f}".format(subtitle_prefix,z_val))

    cbar = plt.colorbar(CS)
    if col_dS == 3:
    	cbar.ax.set_ylabel('combined_S - Rosetta_S')
    else:
	cbar.ax.set_ylabel('combined_S - Amber_S')
    # Add the contour line levels to the colorbar
    cbar.add_lines(CSlines)

    filename = args.output_pre + "/" + title1 + "_" + title2 + "_" + str(col_dS) + ".txt"

    conv.save_fig(fig, filename, "_weights_vs_deltaS", 4*n_unique_z_vals, 4)


def main(list_input_dirs, energies_names, output_pre, scales, offsets):
    #read in and rename arguments
    inp_dir1=list_input_dirs[0][0]
    scoretype1=list_input_dirs[0][1]
    inp_dir2=list_input_dirs[1][0]
    scoretype2=list_input_dirs[1][1]

    title1 = os.path.basename(inp_dir1)
    title2 = os.path.basename(inp_dir2)

    #keep inp_dir1 as constant
    #loop through energies_names[scoretype2]
    #for each energies_names - make a list of weights either using random or centered around mean using sampling bins and nbins from input parameters

    #recursive method - input is list of energies, list of weights per energy, and index of energy. 
    #for that energy, loops thru list of weights, and kicks off further method per next index
    #base case - index = len(list). create weighted dec2, nat2.  merge dicts. convert_disc and get list of discs, one per pdb. return this.
    dec1_total = scorefileparse.read_dir(inp_dir1, scoretype1)
    dec1_total_disc = discparse.pdbs_dict_to_metrics(dec1_total)
    dec2_total = scorefileparse.read_dir(inp_dir2, scoretype2)
    dec2_total_disc = discparse.pdbs_dict_to_metrics(dec2_total)

    dec1 = scorefileparse.read_dir(inp_dir1, scoretype1, list_energies=energies_names[scoretype1])

    weights = [ np.linspace(-2.0, 2.0, num=9).tolist() for _ in energies_names[scoretype2] ] 

    lwd = [ [] for _ in xrange(0, len(weights)+1) ] # need list for each weight + one for pdb_disc_dict
    loop_weights(energies_names[scoretype2], weights, scales, offsets, dec1, inp_dir2, scoretype2, [], lwd)
    list_avg_pdbs_deltaS_R = [ avg_pdbs_deltaS(deltaS_pdbs_disc_dict(pdbs_disc_dict, dec1_total_disc)) for pdbs_disc_dict in lwd[-1] ] 
    list_avg_pdbs_deltaS_A = [ avg_pdbs_deltaS(deltaS_pdbs_disc_dict(pdbs_disc_dict, dec2_total_disc)) for pdbs_disc_dict in lwd[-1] ]

    list_weights_deltaS = lwd[:-1]
    list_weights_deltaS.append(list_avg_pdbs_deltaS_R)
    list_weights_deltaS.append(list_avg_pdbs_deltaS_A)
    
    weights_deltaS_arr = np.array(list_weights_deltaS, dtype="float")
    weights_deltaS_arr = weights_deltaS_arr.T
    
    unique_z_vals = np.unique(weights_deltaS_arr[:,2])

    low_dS = sorted(weights_deltaS_arr[:,3].tolist())[0:3]
    low_dS_ind = [ i for i,dS in enumerate(weights_deltaS_arr[:,3].tolist()) if dS in low_dS ]

    for ind in low_dS_ind:
	pdvd.plot(dec1_total_disc, lwd[-1][ind], "Rosetta", "Combined", "{0}{1}_".format(output_pre,ind,"_"), add_slash=False)
        pdvd.plot(dec2_total_disc, lwd[-1][ind], "Amber", "Combined", "{0}{1}_".format(output_pre,ind,"_"), add_slash=False)

    #w_dS_sorted = weights_deltaS_arr[np.lexsort((weights_deltaS_arr[:,0],weights_deltaS_arr[:,1]))]
    w_dS_sorted = weights_deltaS_arr

    plot_weights_dS(w_dS_sorted, 3, unique_z_vals, title1, title2, energies_names[scoretype2][0], energies_names[scoretype2][1], energies_names[scoretype2][2])

    plot_weights_dS(w_dS_sorted, 4, unique_z_vals, title1, title2, energies_names[scoretype2][0], energies_names[scoretype2][1], energies_names[scoretype2][2])

    filename_txt = args.output_pre + "/" + title1 + "_" + title2 + "_weights_vs_deltaS.txt"

    np.savetxt(filename_txt, w_dS_sorted, fmt='%2.5f', delimiter=",", header="gb,elec,dihedral,deltaSR,deltaSA")
   
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument ('--input_dir', '-d', nargs=2, action='append', help="directory for input score files and its scoretype")

    parser.add_argument('--energies_names', action='append',
               type=lambda kv: kv.split("="),  help='gives column names to sum over for total score. sample: rosetta=fa_elec,fa_sol') 

    parser.add_argument('--output_pre', help='prefix for output figure')

    parser.add_argument('--scales', 
               type=lambda kv: kv.split(","), help='gives scales for weights in order of energies_names for second scoretype. sample: 0.5,0.4')
    parser.add_argument('--offsets', 
               type=lambda kv: kv.split(","), help='gives offsets for weights in order of energies_names for second scoretype. sample: 0.5,0.4')

    args = parser.parse_args()

    dict_energies_names = convert_list_dict(args.energies_names)
    scales = map(float,args.scales)
    offsets = map(float,args.offsets)

    main(args.input_dir, dict_energies_names, args.output_pre, scales, offsets)    
