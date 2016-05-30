#!/usr/bin/env python

import os
import sys
from customIO import scorefileparse
from customIO import discparse
from plot import conv
from plot import scatterplot

def main(args):
    #read in and rename arguments
    inp_dir=args[1]
    scoretype=args[2]

    dec, nat = scorefileparse.read_dec_nat(inp_dir, [], scoretype)

    disc = discparse.read_dir(inp_dir)

    dec_norm = scorefileparse.norm_pdbs(dec)
    nat_norm = scorefileparse.norm_pdbs(nat,dec)

    [dec_inter, nat_inter, disc_inter] = scorefileparse.pdbs_intersect([dec_norm, nat_norm, disc]) 

    #labels = ["Average","1.0","1.5","2.0","2.5","3.0","4.0","6.0"]
    labels = ["Average"]
    energy_gap = [[] for l in labels]
    avg_disc = [[] for l in labels]

    for pdb in dec_inter.keys():

        for ind in xrange(0,len(labels)):
            lowest_dec = min([ e[0] for e in dec_inter[pdb].values() ])
            lowest_nat = min([ n[0] for n in nat_inter[pdb].values() if n[1] < 2.0 ])
            energy_gap[ind].append(lowest_nat - lowest_dec)
            avg_disc[ind].append(disc_inter[pdb][0])

    fig, axarr = conv.create_ax(len(labels), 1)

    for x_ind,l in enumerate(labels):
        ax = axarr[0,x_ind] 

        scatterplot.draw_actual_plot(ax, avg_disc[x_ind], energy_gap[x_ind], [], l,"Disc","Energy Gap")

        scatterplot.plot_regression(ax, avg_disc[x_ind], energy_gap[x_ind], False, False)

    title = os.path.basename(inp_dir)

    filename=inp_dir + "/test.txt"

    conv.save_fig(fig, filename, "disc_v_egap", len(labels)*3, 4)
 
if __name__ == "__main__":

    main(sys.argv)
