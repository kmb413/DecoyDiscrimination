#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
from adjustText import adjust_text

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

def plot_pareto(dec_inter1, dec_inter2, d_orig, ax, pdb, title1, title2, plot=False):
    d1e = scorefileparse.get_energies(dec_inter1[pdb])
    d2e = scorefileparse.get_energies(dec_inter2[pdb])

    r1 = scorefileparse.get_rmsd(dec_inter1[pdb])
    r2 = scorefileparse.get_rmsd(dec_inter2[pdb])
    rorig = scorefileparse.get_rmsd(d_orig[pdb])

    d1e_ranks = gen_ranks(d1e)
    d2e_ranks = gen_ranks(d2e)

    pts = map(list, zip(d1e_ranks, d2e_ranks))

    #cleared is a list of pareto dominant pts
    #dominated is a list of all points that are not dominated
    #cleared_d is a dictionary with keys of d1e_ranks and values of d2e_ranks 
    cleared, dominated = cull(pts, dominates)
    cleared_d = dict(cleared)
    min_tuple = { "All" : (1000,1000,1000000), "ParetoRA" : (1000,1000,60), "Rosetta" : (1000,1000,60), "Amber" : (1000,1000,60) }
    min_naive = { "All" : [], "Rosetta" : [], "Amber" : []  }

    for (e1, e2), r in zip(pts,rorig):
        #assign points to min_tuple
        if r < min_tuple["All"][2]:
            min_tuple["All"] = (e1, e2, r)

    pts_r_r = zip(d1e_ranks,d2e_ranks,r1)
    pts_r_a = zip(d1e_ranks,d2e_ranks,r2)
    pts_r_orig = zip(d1e_ranks, d2e_ranks, rorig)

    #used original rmsd for all datasets - trends remain the same  
    pareto_equal_min = min([ e1+e2 for e1,e2 in cleared_d.items() ])
    list_pts =  [ (rosetta,amber,r) for rosetta,amber, r in pts_r_orig if amber+rosetta == pareto_equal_min ]
    min_naive["Pareto"] = find_lowest_point( list_pts )

    #assign min_naive
    rosetta_min_e1 = min([  e1 for e1,e2 in pts ])
    amber_min_e2 = min([  e2 for e1,e2 in pts ])

    min_naive["All"] = min_tuple["All"]
    min_naive["Rosetta"] = [ (rosetta,amber,r) for rosetta,amber,r in pts_r_orig if 0 == rosetta ][0]
    min_naive["Amber"] = [ (rosetta,amber,r) for rosetta,amber,r in pts_r_orig if 0 == amber ][0]
    
    if plot:
        plot_rank_v_rank(pts, rorig, "Rosetta", "Amber", cleared_d, ax, min_naive["Pareto"])     
    
    return min_naive

def plot_rank_v_rank(pts, rorig, x_axis, y_axis, pareto_dict, ax, pareto_min):
    x1 = []
    y1 = []
    color1 = []

    x2 = []
    y2 = []
    color2 = []

    labels = []

    for (e1, e2), r in zip(pts,rorig):
        #assign colors to points
        if (e1, e2, r) == pareto_min:
            color2.append('black')
            x2.append(e1)
            y2.append(e2)
        elif pareto_dict.get(e1) == e2:
            color2.append('purple') #black
	    x2.append(e1)
            y2.append(e2)
        elif e1 <= 10:
            color2.append('salmon')
	    x2.append(e1)
	    y2.append(e2)
        elif e2 <= 10:
            color2.append('turquoise')
	    x2.append(e1)
            y2.append(e2)
        else:
            color1.append('lightgray')
	    x1.append(e1)
	    y1.append(e2)
        if (e1, e2, r) == pareto_min: 
	    labels.append((e1, e2, r, 'black'))
        if e1 == 0:
            labels.append((e1, e2, r, 'salmon'))
	if e2 == 0:
            labels.append((e1, e2, r, 'turquoise'))


    scatterplot.draw_actual_plot(ax, x1, y1, color1, "", x_axis, y_axis, size=20, alpha=0.4)
    scatterplot.draw_actual_plot(ax, x2[::-1], y2[::-1], color2[::-1], "", x_axis, y_axis, size=30, alpha=0.6)

    max_x = max([ e1 for e1, e2 in pts ]) 

    min_y = min([ y for x, y, text, col in labels ])
    max_y = max([ y for x, y, text, col in labels ]) + 350
    interval = (max_y - min_y)/3

    sort_labels = sorted(labels,key=lambda x: x[1]) 

    [ conv.annotate_point_arrow(ax, x, y, "{0:.1f}".format(text), color=col, fontweight='bold', xytext=(max_x, min_y + interval*ind), textcoords='data') for ind, (x, y, text, col) in enumerate(sort_labels) ]

    #texts = [ conv.add_text_adjust(ax, x, y, "{0:.1f}".format(text), size=8, color=col, fontweight='bold', bbox=True) for x, y, text, col in labels ]

    #adjust_text(texts, arrowprops=dict(arrowstyle="->", color='k', lw=1.0, connectionstyle='arc3,rad=0.3'), expand_points=(2.7, 2.7),
    #        force_points=3.2, lim=300)
def find_lowest_point( list_pts ):
    first_rank_list = [ p[0] for p in list_pts ]
    second_rank_list = [ p[1] for p in list_pts ]
    #TODO check that this arithmetic is sound
    min_rank = min(first_rank_list + second_rank_list)
    if len([ (e1, e2, r) for e1, e2, r in list_pts if min_rank == e1 or min_rank == e2 ]) > 1:
        print [ (e1, e2, r) for e1, e2, r in list_pts if min_rank == e1 or min_rank == e2 ]
    min_point = [ (e1, e2, r) for e1, e2, r in list_pts if min_rank == e1 or min_rank == e2 ][0]
    return min_point

def main(input_dir_1, scoretype1, input_dir_2, scoretype2, rmsd_cutoff, output_pre ):
    #read in and rename arguments
    title1 = os.path.basename(input_dir_1)
    title2 = os.path.basename(input_dir_2)
    d1 = scorefileparse.read_dir(input_dir_1, scoretype1, repl_orig=False)
    d2 = scorefileparse.read_dir(input_dir_2, scoretype2, repl_orig=False)
    dorig = scorefileparse.read_dir(input_dir_1, scoretype1, repl_orig=True)
    #dorig = scorefileparse.read_dir(input_dir_1, scoretype1, repl_orig=False)

    #[dec_inter1, dec_inter2, dorig_test] = scorefileparse.pdbs_scores_intersect([d1, d2, dorig])       

    dec_inter1 = d1
    dec_inter2 = d2

    line_plot_data = {}

    min_naive_by_pdb = {}

    filename = output_pre + "/" + title1 + "_" + title2 + ".txt"

    for x_ind,pdb in enumerate(sorted(dec_inter1.keys())):
        if pdb == "1sen" or pdb == "1t2i" or pdb == "2qy7":
            fig, axarr = conv.create_ax(1, 1)
	    plot = True
	    if pdb == "1sen":
                width = 2.1
	    else:
		width = 2.1
	    ax = axarr[0,0]
        else:
	    fig, axarr, ax = None, None, None
	    plot = False

        min_naive = plot_pareto(dec_inter1, dec_inter2, dorig, ax, pdb, title1, title2, plot=plot)

        for key, (rank1, rank2, rmsd) in min_naive.items():
	     if line_plot_data.get(key) is None:
	         line_plot_data[key] = ([],[])
       	     line_plot_data[key][0].append(pdb)
	     line_plot_data[key][1].append(rmsd)
	     if min_naive_by_pdb.get(pdb) is None:
                 min_naive_by_pdb[pdb] = {}
             min_naive_by_pdb[pdb][key] = rmsd
	if plot:
	     conv.save_fig(fig, filename, "rank_v_rank_{0}".format(pdb), width+1.0, width, size=10)
	plot = False
    #organize data
    indices = list(range(len(line_plot_data["All"][1])))
    indices.sort(key=lambda x: line_plot_data["All"][1][x])
    
    ranked_pdbs_by_rmsd_all = {}

    for i, x in enumerate(indices):
        ranked_pdbs_by_rmsd_all[line_plot_data["All"][0][x]] = i

    for label, (pdbs, rmsds) in line_plot_data.items():
	line_plot_data[label] = tuple(zip(*sorted(zip(pdbs,rmsds), key=lambda x: ranked_pdbs_by_rmsd_all[x[0]] )))    

    #plot line plot
    ordered_labels=["All","Amber","Rosetta","Pareto"]

    lines = [ (line_plot_data[label][0], line_plot_data[label][1], label) for label in ordered_labels ]
    fig2, axarr2 = conv.create_ax(1, 1, shx=True, shy=True)
    line.plot_series(axarr2[0,0], lines, "RMSD vs. pdb", "PDB", "RMSD", linestyle='-', colors=['black', 'turquoise', 'salmon', 'mediumslateblue'])
    conv.add_legend(axarr2[0,0], ncol=4)
    conv.save_fig(fig2, filename, "line", 8, 3,size=10)

    #output table of minimum rmsds for each case
    with open(filename.replace(".txt",".csv"),'w') as csv_f:
        csv_f.write(",")
	csv_f.write(",".join(sorted(line_plot_data.keys())))
        csv_f.write("\n")
        pdbs = sorted(line_plot_data["All"][0])
        csv_f.write("\n".join([ ",".join([p] + [ str(rmsds[pdbs.index(p)]) for label, (pdbs,rmsds) in sorted(line_plot_data.items())]) for p in pdbs ])) 

    #plot scatterplot
    fig4, axarr4 = conv.create_ax(1, 2)
    gen_scatterplot(axarr4[0,0], "Pareto", "Rosetta", min_naive_by_pdb, color='darksalmon')
    gen_scatterplot(axarr4[1,0], "Pareto", "Amber", min_naive_by_pdb, color='darkturquoise')

    conv.save_fig(fig4, filename, "scattdeltas", 3.0, 6.0)

def gen_scatterplot(ax, x_axis, y_axis, min_naive_by_pdb, color='k'):
    x_deltas = get_dist_deltas(x_axis, "All", min_naive_by_pdb)
    y_deltas = get_dist_deltas(y_axis, "All", min_naive_by_pdb)

    scatterplot.draw_actual_plot(ax, x_deltas, y_deltas, color, "", u'Δ {0} RMSD (Å)'.format(x_axis), u'Δ {0} RMSD (Å)'.format(y_axis), size=25, alpha=0.6, label=y_axis)

    #just for the sake of labeling outliers
    scatterplot.plot_regression(ax, x_deltas, y_deltas, fit=False, neg=False, label_corr=False, labels=sorted(min_naive_by_pdb.keys()), plot_PI=False)
    #conv.add_legend(ax)

    scatterplot.add_x_y_line(ax)

def get_dist_deltas(top, bottom, min_naive_by_pdb):
    dists = []
    for pdb, dict_rmsds in sorted(min_naive_by_pdb.items()):
        if bottom is None:
            b = 0
        else:
            b = dict_rmsds[bottom] 
        dists.append( dict_rmsds[top] - b )

    return dists

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument ('--input_dir', '-d', nargs=2, action='append', help="directory for input score files and its scoretype")

    parser.add_argument('--output_pre', help='prefix for output figure')
    
    parser.add_argument('--rmsd_cutoff', default=50, type=float,
		   help='RMSD cutoff to consider energies')

    args = parser.parse_args()

    main(args.input_dir[0][0], args.input_dir[0][1], args.input_dir[1][0], args.input_dir[1][1], args.rmsd_cutoff, args.output_pre)
