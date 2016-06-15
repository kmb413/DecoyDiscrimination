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

def plot_r_v_r(dec_inter1, dec_inter2, nat_inter1, nat_inter2, ax, pdb, title1, title2):

    r1 = scorefileparse.get_rmsd(dec_inter1[pdb], sort_by="energy")
    r2 = scorefileparse.get_rmsd(dec_inter2[pdb], sort_by="energy")
    
    scatterplot.draw_actual_plot(ax, r1, r2, 'k', pdb, title1,title2)

def gen_ranks(list_energies):
    indices = list(range(len(list_energies)))
    indices.sort(key=lambda x: list_energies[x])
    output = [0] * len(indices)
    for i, x in enumerate(indices):
        output[x] = i
    return output

def plot_pareto(dec_inter1, dec_inter2, nat_inter1, nat_inter2, ax, pdb, title1, title2):

    d1e = scorefileparse.get_energies(dec_inter1[pdb])
    d2e = scorefileparse.get_energies(dec_inter2[pdb])

    r1 = scorefileparse.get_rmsd(dec_inter1[pdb])

    d1e_ranks = gen_ranks(d1e)
    d2e_ranks = gen_ranks(d2e)

    pts = map(list, zip(d1e_ranks, d2e_ranks))

    cleared, dominated = cull(pts, dominates)

    cleared_d = dict(cleared)
    
    min_tuple = { "All" : (1000,1000,60), "ParetoRA" : (1000,1000,60), "Rosetta" : (1000,1000,60), "Amber" : (1000,60,60) }
    min_naive = { "All" : [], "Rosetta" : [], "Amber" : []  }

    for i in range(1, 11):
        w = i * 0.1
        

    color = []
    for (e1, e2), r in zip(pts,r1):
        #assign points to min_tuple
        if r < min_tuple["All"][2]:
            min_tuple["All"] = (e1, e2, r)
        if cleared_d.get(e1) == e2 and e1 <=10 and e2 <= 10 and r < min_tuple["ParetoRA"][2]:
            min_tuple["ParetoRA"] = (e1, e2, r)
        if e1 <= 10 and r < min_tuple["Rosetta"][2]:
            min_tuple["Rosetta"] = (e1, e2, r)
        if e2 <= 10 and r < min_tuple["Amber"][2]:
            min_tuple["Amber"] = (e1, e2, r)
        #assign colors to points
        if cleared_d.get(e1) == e2 and e1 <=10 and e2 <= 10:
            color.append((0, 0, 0)) #black
        elif cleared_d.get(e1) == e2 and e1 <= 10:
            color.append((161, 8, 8)) #dark red
        elif cleared_d.get(e1) == e2  and e2 <= 10:
            color.append((0, 153, 153)) #dark cyan
        elif e1 <= 10:
            color.append((255, 51, 51)) #red
        elif e2 <= 10:
            color.append((51, 255, 255)) #cyan
        elif cleared_d.get(e1) == e2:
            color.append((128, 128, 128)) #gray
        else:
            color.append((255,255,51)) #yellow

    #assign min_naive
    rosetta_min_e1 = min([  e1 for e1,e2 in pts if e1 <= 10 ])
    amber_min_e2 = min([  e2 for e1,e2 in pts if e2 <= 10 ])

    pts_r = zip(d1e_ranks,d2e_ranks,r1)

    min_naive["All"] = min_tuple["All"]
    min_naive["Rosetta"] = [ (rosetta,amber,r) for rosetta,amber,r in pts_r if rosetta_min_e1 == rosetta ][0]
    min_naive["Amber"] = [ (rosetta,amber,r) for rosetta,amber,r in pts_r if amber_min_e2 == amber ][0]
    for i in range(1, 11):
        w = i * 0.1
	key = "Pareto{0}".format(i)
	pareto_equal_min = min([ e1+e2*w for e1,e2 in cleared_d.items() ])
        list_pts =  [ (rosetta,amber,r) for rosetta,amber, r in pts_r if amber*w+rosetta == pareto_equal_min ]
        min_naive[key] = find_lowest_point( list_pts )

    color_converted = [ (c[0]/255.0, c[1]/255.0, c[2]/255.0) if hasattr(c, "__iter__") else '' for c in color ] 

    scatterplot.draw_actual_plot(ax, d1e_ranks, d2e_ranks, color_converted, pdb, title1, title2, cm="summer", size=20)

    s = "{0}\t1".format(pdb)
    for k, (e1, e2, r) in min_tuple.items():
        s += ("\t{3} {0:.0f},{1:.0f},{2:.1f}".format(e1, e2, r, k))

    #print s

    s = "{0}\t2".format(pdb)
    for k, (e1, e2, r) in min_naive.items():
        s += "\t{0}".format(k)
        s += " {0:.0f},{1:.0f},{2:.1f}".format(e1, e2, r)
    #print s

    return min_naive

def find_lowest_point( list_pts ):
    first_rank_list = [ p[0] for p in list_pts ]
    second_rank_list = [ p[1] for p in list_pts ]
    min_rank = min(first_rank_list + second_rank_list)
    min_point = [ (e1, e2, r) for e1, e2, r in list_pts if min_rank == e1 or min_rank == e2 ][0]
    return min_point

def main(input_dir_1, scoretype1, input_dir_2, scoretype2, rmsd_cutoff, output_pre ):
    #read in and rename arguments
    title1 = os.path.basename(input_dir_1)
    title2 = os.path.basename(input_dir_2)

    d1, n1 = scorefileparse.read_dec_nat(input_dir_1, scoretype1, repl_orig=False)
    d2, n2 = scorefileparse.read_dec_nat(input_dir_2, scoretype2, repl_orig=False)

    dec1 = scorefileparse.filter_pdbs_by_rmsd(d1, rmsd_cutoff)
    nat1 = scorefileparse.filter_pdbs_by_rmsd(n1, rmsd_cutoff)
    dec2 = scorefileparse.filter_pdbs_by_rmsd(d2, rmsd_cutoff)
    nat2 = scorefileparse.filter_pdbs_by_rmsd(n2, rmsd_cutoff)

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

    line_plot_data = {}

    min_naive_by_pdb = {}

    for x_ind,pdb in enumerate(sorted(dec_inter1.keys())):

        ax = axarr[x_ind, 0] 

        plot_r_v_r(dec_inter1, dec_inter2, nat_inter1, nat_inter2, ax, pdb, title1, title2)

        ax = axarr[x_ind, 1]

        min_naive = plot_pareto(dec_inter1, dec_inter2, nat_inter1, nat_inter2, ax, pdb, title1, title2)
	keys_to_include = ["Amber", "Rosetta","All","Pareto10"]
        for key, (rank1, rank2, rmsd) in min_naive.items():
	     #if key not in keys_to_include:
	     #    continue
	     if line_plot_data.get(key) is None:
	         line_plot_data[key] = ([],[])
       	     line_plot_data[key][0].append(pdb)
	     line_plot_data[key][1].append(rmsd)
	     if min_naive_by_pdb.get(pdb) is None:
                 min_naive_by_pdb[pdb] = {}
             min_naive_by_pdb[pdb][key] = rmsd

    indices = list(range(len(line_plot_data["All"][1])))
    indices.sort(key=lambda x: line_plot_data["All"][1][x])
    
    ranked_pdbs_by_rmsd_all = {}

    for i, x in enumerate(indices):
        ranked_pdbs_by_rmsd_all[line_plot_data["All"][0][x]] = i

    for label, (pdbs, rmsds) in line_plot_data.items():
	line_plot_data[label] = tuple(zip(*sorted(zip(pdbs,rmsds), key=lambda x: ranked_pdbs_by_rmsd_all[x[0]] )))    

    filename = output_pre + "/" + title1 + "_" + title2 + ".txt"   
    
    #suffix="rmsd_v_rmsd_{0}".format(rmsd_cutoff)
 
    #conv.save_fig(fig, filename, suffix, 7, len(dec_inter1)*3)


    ordered_labels = ["All", "Amber", "Rosetta", "Pareto1", "Pareto2", "Pareto3", "Pareto4", "Pareto5", "Pareto6", "Pareto7", "Pareto8", "Pareto9", "Pareto10"]
    lines = [ (line_plot_data[label][0], line_plot_data[label][1], label) for label in ordered_labels ]

    fig2, axarr2 = conv.create_ax(1, len(ordered_labels), shx=True, shy=True)

    for i, label in enumerate(ordered_labels):

        line.draw_actual_plot(axarr2[i,0], lines[0:i+1], "RMSD vs. pdb", "PDB", "RMSD")
    
    conv.save_fig(fig2, filename, "_line", 10, len(ordered_labels)*5)


    hist_comp = [ ("Amber","All"), ("Rosetta", "All"), ("Pareto10", "All"), ("Pareto1", "Rosetta"), ("Pareto2", "Rosetta"),
                  ("Pareto3","Rosetta"), ("Pareto4","Rosetta"), ("Pareto5","Rosetta"), ("Pareto6","Rosetta"), ("Pareto7","Rosetta"),
                  ("Pareto8","Rosetta"), ("Pareto9","Rosetta"), ("Pareto10","Rosetta"), ("Pareto1", "Amber"), ("Pareto2", "Amber"),
                  ("Pareto3","Amber"), ("Pareto4","Amber"), ("Pareto5","Amber"), ("Pareto6","Amber"), ("Pareto7","Amber"),
                  ("Pareto8","Amber"), ("Pareto9","Amber"), ("Pareto10","Amber")]

    fig3, axarr3 = conv.create_ax(2, len(hist_comp), shx=False, shy=False)

    for ind, (top, bottom) in enumerate(hist_comp):
        gen_dist_plot(axarr3[ind,0], axarr3[ind,1], top, bottom, min_naive_by_pdb)

    conv.save_fig(fig3, filename, "_distdeltas", 7, len(hist_comp)*5)

def gen_dist_plot(ax1, ax2, top, bottom, min_naive_by_pdb):

    deltas = get_dist_deltas(top, bottom, min_naive_by_pdb)

    hist.draw_actual_plot(ax1, deltas, top + " - " + bottom, "Deltas", "Frequency")

    counts_equal = sum([1 for d in deltas if d < 0.5 and d > -0.5 ])
    counts_rescued = sum([1 for d in deltas if d < -2.0 ])
    counts_worse = sum([1 for d in deltas if d > 2.0 ])

    size = len(deltas)

    text = "Total: {0}\nSimilar: {1}\nRescued: {2}\nWorse: {3}".format(size, counts_equal, counts_rescued, counts_worse)

    ax2.text(0.5, 0.5, text,
           horizontalalignment='center',
           verticalalignment='center',
           fontsize=10, color='red',
           transform=ax2.transAxes)

def get_dist_deltas(top, bottom, min_naive_by_pdb):
    dists = []
    for pdb, dict_rmsds in min_naive_by_pdb.items(): 
        dists.append( dict_rmsds[top] - dict_rmsds[bottom] )

    return dists

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument ('--input_dir', '-d', nargs=2, action='append', help="directory for input score files and its scoretype")

    parser.add_argument('--output_pre', help='prefix for output figure')
    
    parser.add_argument('--rmsd_cutoff', default=50, type=float,
		   help='RMSD cutoff to consider energies')

    args = parser.parse_args()

    main(args.input_dir[0][0], args.input_dir[0][1], args.input_dir[1][0], args.input_dir[1][1], args.rmsd_cutoff, args.output_pre)
