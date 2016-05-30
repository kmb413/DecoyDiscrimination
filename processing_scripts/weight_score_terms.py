#!/usr/bin/env python

'''First iteration of weighting scheme - weight amber or rosetta scoreterms as one, graph in a colored plot kind of way'''

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

def main(list_input_dirs, energies_names, output_pre):
    #read in and rename arguments
    inp_dir1=list_input_dirs[0][0]
    scoretype1=list_input_dirs[0][1]
    inp_dir2=list_input_dirs[1][0]
    scoretype2=list_input_dirs[1][1]

    title1 = os.path.basename(inp_dir1)
    title2 = os.path.basename(inp_dir2)

    column_dict = {}

    for c in energies_names:
        column_dict[c[0]] = c[1:]

    dec1, nat1 = scorefileparse.read_dec_nat(inp_dir1, energies_names[scoretype1], scoretype1)
    dec2, nat2 = scorefileparse.read_dec_nat(inp_dir2, energies_names[scoretype2], scoretype2)

    [dec_inter1, nat_inter1, dec_inter2, nat_inter2] = scorefileparse.pdbs_intersect([dec1, nat1, dec2, nat2]) 

    sum_discs = Counter()

    fig, axarr = conv.create_ax(1, len(dec_inter1)+1, True,True)

    for x_ind, pdb in enumerate(sorted(dec_inter1.keys())):

        discs_per_pdb = {}

        for w_1 in xrange(-10,10,2):
            for w_2 in xrange(-10,10,2): 
                weight_1 = 2 ** w_1
                weight_2 = 2 ** w_2
                weighted_1 = scorefileparse.weight_dict(dec_inter1[pdb], weight_1)
                weighted_2 = scorefileparse.weight_dict(dec_inter2[pdb], weight_2)
                merged = scorefileparse.merge_dicts([weighted_1, weighted_2])
                ddata1 = scorefileparse.convert_disc(merged)

                disc_divs = [1.0,1.5,2.0,2.5,3.0,4.0,6.0]

                disc1, d, counts = disc.given_data_run_disc(ddata1, True, disc_divs)
                discs_per_pdb[(weight_1,weight_2)] = disc1

        sorted_disc = sorted(discs_per_pdb.values())
        max_title = [ t for t,v in discs_per_pdb.items() if v == sorted_disc[0] ]
        
        #header_string = "\t".join("{0:.3f}-{1:.3f}".format(x,y) for x,y in sorted(discs_per_pdb.keys())) + "\tMax_Weight"
        #values_string = "\t".join(format(x, "10.3f") for (w1,w2),x in sorted(discs_per_pdb.items())) + "\t{0:.3f}".format(max_title[0])
        
        #print header_string
        #print values_string

        ax = axarr[x_ind, 0]

        #ax.set_xlim(-10, 600)
        #ax.set_ylim(-10, 600)

        ax.set_xscale('log', basex=2)
        ax.set_yscale('log', basey=2)

        x = [ w1 for (w1,w2) in sorted(discs_per_pdb.keys()) ]
        y = [ w2 for (w1,w2) in sorted(discs_per_pdb.keys()) ]
        d = [ v for k,v in sorted(discs_per_pdb.items()) ]
  
        min_y = min(discs_per_pdb.values())
        max_y = max(discs_per_pdb.values())
        #print min_y, max_y
        s = scatterplot.draw_actual_plot(ax, x, y, d, pdb, scoretype1, scoretype2, 'bwr')
        fig.colorbar(s,ax=ax)
        #ax.axhline(y=min_y)
        #ax.set_ylim(min_y-0.05,max_y+0.05)
        scatterplot.add_x_y_line(ax, 0,600)

        sum_discs.update(discs_per_pdb)

    #print "All PDBs {0}".format(len(dec_inter1))

    #sorted_disc = sorted(sum_discs.values())
    #max_title = [ t for t,v in sum_discs.items() if v == sorted_disc[0] ]

    #header_string = "\t".join(format(x, "10.3f") for x in sorted(sum_discs.keys())) + "\tMax_Weight"
    #values_string = "\t".join(format(x/len(dec_inter1), "10.3f") for key,x in sorted(sum_discs.items())) + "\t{0:.3f}".format(max_title[0])
  
    #print header_string
    #print values_string 

    ax = axarr[len(dec_inter1), 0]

    min_y = min(x/len(dec_inter1) for x in sum_discs.values())   
    max_y = max(x/len(dec_inter1) for x in sum_discs.values())

    x = [ w1 for w1,w2 in sorted(sum_discs.keys()) ]
    y = [ w2 for w1,w2 in sorted(sum_discs.keys()) ]
    d = [ v/len(dec_inter1) for k,v in sorted(sum_discs.items()) ]
    #fix titles of axes

    ax.set_xscale('log', basex=2)
    ax.set_yscale('log', basey=2)

    s = scatterplot.draw_actual_plot(ax, x,y,d, "All", scoretype1, scoretype2, cm='bwr')
    fig.colorbar(s,ax=ax)
    scatterplot.add_x_y_line(ax, 0,600)
    #ax.axhline(y=min_y)

    conv.save_fig(fig, output_pre, "_weights_v_disc", 3, len(dec_inter1)*3)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument ('--input_dir', '-d', nargs=2, action='append', help="directory for input score files and its scoretype")

    parser.add_argument('--energies_names', type=dict, help='gives column names to sum over for total score. sample: { "rosetta" : "total_score" }') 

    parser.add_argument('--output_pre', help='prefix for output figure')

    args = parser.parse_args()

    main(args.input_dir, args.energies_names, args.output_pre)    
