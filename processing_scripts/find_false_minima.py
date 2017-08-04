#!/usr/bin/env python

import os
from customIO import scorefileparse
from customIO import discparse
import argparse
from collections import defaultdict

def gen_ranks(list_energies):
    indices = list(range(len(list_energies)))
    indices.sort(key=lambda x: list_energies[x])
    output = [0] * len(indices)
    for i, x in enumerate(indices):
        output[x] = i
    return output

def find_false_minima(dec_inter1, dec_inter2, pdb, index):

    d1e = scorefileparse.get_energies(dec_inter1[pdb])
    d2e = scorefileparse.get_energies(dec_inter2[pdb])

    r1 = scorefileparse.get_rmsd(dec_inter1[pdb])
    r2 = scorefileparse.get_rmsd(dec_inter2[pdb])

    d1e_ranks = gen_ranks(d1e)
    d2e_ranks = gen_ranks(d2e)

    set1_false_minima = [ (decoy, rank+1, rmsd) for decoy, rank, rmsd in zip(sorted(dec_inter1[pdb].keys()), d1e_ranks, r1) if rank <= 10 and rmsd >= 5.0 ] 
    set2_corr = [ (decoy, rank+1, rmsd) for decoy, rank, rmsd in zip(sorted(dec_inter2[pdb].keys()), d2e_ranks, r2) if decoy in (d for d,rank,r in set1_false_minima) ]

    if index == 0:
        result = zip(set1_false_minima, set2_corr)
    elif index == 1:
        result = zip(set2_corr, set1_false_minima)

    return result

def main(input_dir):
    #read in and rename arguments
    title1 = os.path.basename(input_dir[0][0])
    title2 = os.path.basename(input_dir[1][0])

    d1 = scorefileparse.read_dir(input_dir[0][0], input_dir[0][1])
    d2 = scorefileparse.read_dir(input_dir[1][0], input_dir[1][1])
    

    print d1.keys()
    print d2.keys()
    dec_inter1 = d1
    dec_inter2 = d2

    [dec_inter1, dec_inter2] = scorefileparse.pdbs_scores_intersect([d1, d2])       

    pdb_false = {} 
    pdb_decoys = defaultdict(list)
    pdb_n_decoys_r = {}
    pdb_n_decoys_a = {}

    #loop through dict
    for pdb in sorted(dec_inter1.keys()):
        s1_false = find_false_minima(dec_inter1, dec_inter2, pdb, 0)
        s2_false = find_false_minima(dec_inter2, dec_inter1, pdb, 1)
	if not s1_false and not s2_false:
	    pdb_false[pdb] = ""
	    continue
	elif s1_false and s2_false:
            pdb_false[pdb] = "RA"
	elif s1_false:
            pdb_false[pdb] = "R" #Rosetta must be input first
        elif s2_false:
            pdb_false[pdb] = "A"
	pdb_decoys[pdb].extend([ (d1[0],input_dir[0][1]) for d1, d2 in s1_false])
        pdb_decoys[pdb].extend([ (d1[0],input_dir[1][1]) for d1, d2 in s2_false])
	if s1_false:
	    pdb_n_decoys_r[pdb] = len(s1_false)
        if s2_false:
            pdb_n_decoys_a[pdb] = len(s2_false)

        print pdb
	print input_dir[0][1]
        print "\n".join([ ",".join(map(str,d)) for d in s1_false ])
        print input_dir[1][1]
        print "\n".join([ ",".join(map(str,d)) for d in s2_false ])

    print "\n"
    print "\n".join( "{0},{1}".format(pdb, false) for pdb, false in sorted(pdb_false.items()) )

    print "\n"
    print "\n".join( [ "{0}\n{1}\n".format(pdb,"\n".join([ "{0},{1}".format(decoy, st) for decoy, st in list_vals])) for pdb, list_vals in sorted(pdb_decoys.items()) ]) 

    print "\nNumber of Decoys Rosetta\n"
    print "\n".join( [ "{0},{1}".format(pdb, n) for pdb, n in sorted(pdb_n_decoys_r.items()) ] )

    print "\nNumber of Decoys Amber\n"
    print "\n".join( [ "{0},{1}".format(pdb, n) for pdb, n in sorted(pdb_n_decoys_a.items()) ] )    

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument ('--input_dir', '-d', nargs=2, action='append', help="directory for input score files and its scoretype")

    args = parser.parse_args()

    main(args.input_dir)
