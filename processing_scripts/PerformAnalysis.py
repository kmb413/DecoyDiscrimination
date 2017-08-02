#!/usr/bin/env python

import os
import sys
from customIO import scorefileparse
import argparse
from shutil import copyfile
import correlate_ranks
import glob
import CorrRanksDecoy
import CopyLowestEnergy
import CorrRanksFalse

def trim_rosetta(name):
    return os.path.basename(name)[0:-9]

def main(input_pdb, decoy_names_rosetta, decoy_names_amber):
    try:
	os.mkdir("../pdb/{0}".format(input_pdb))
    except:
        pass
    #copy rosetta and amber decoys from gaann server
    for decoy_name in decoy_names_rosetta + decoy_names_amber:
        os.system('cp ../Rosetta/min/decoys.all0/{0}/{1}_0001.pdb ../pdb/{0}/'.format(
		input_pdb, decoy_name )) 

    pdb_dir = "../pdb/{0}".format(input_pdb)
    output_prefix = "false_minima"
    output_r = open(output_prefix+"_rosetta_true_perres.csv","a")
    output_r_full = open(output_prefix+"_rosetta_true.csv", "a")
    output_a_full = open(output_prefix+"_amber_true.csv", "a")
    output_r_false = open(output_prefix+"_rosetta_false.csv", "a")
    output_a_false = open(output_prefix+"_amber_false.csv", "a")

    #if decoy_names_rosetta:
        #output_r.write(input_pdb)
        #output_r_full.write(input_pdb)
    #if decoy_names_amber:
        #output_a_full.write(input_pdb)

    if os.path.isfile("../score_files/natives.set1_Rosetta_min/{0}.sc".format(input_pdb)):
        decoy_set = 1
    else:
	decoy_set = 2

    if decoy_names_rosetta:
        CopyLowestEnergy.main("../Rosetta/min/natives.all0/", "rosetta", input_pdb, "../pdb/")

    #run correlation_ranks for all rosetta decoys
    for decoy_name in decoy_names_rosetta:
        rosetta_native = glob.glob("../pdb/{0}/*relaxed*.pdb".format(input_pdb))[0]
        rosetta_decoy = "../pdb/{0}/{1}_0001.pdb".format(input_pdb, decoy_name)               
 
        native_sf = "../score_files/natives.set{0}_Amber_min/{1}_norestraints.sc".format(decoy_set, input_pdb)
        score_dict = scorefileparse.read_vals(native_sf, "amber", repl_orig=False, trim=True)
        native_name = [ name for name, energy in sorted(score_dict.items(), key=lambda x: x[1][0]) ][0]
	if decoy_name not in decoy_names_amber:
            output_a_full.write(CorrRanksDecoy.main(("../score_files/natives.set{0}_Amber_min/{1}_norestraints.sc".format(decoy_set, input_pdb), "amber"),
                ("../score_files/decoys.set{0}_Amber_min/{1}_norestraints.sc".format(decoy_set, input_pdb), "amber"), decoy_name=decoy_name, native_name=native_name, pdb=input_pdb)    )
        

        output_r_false.write(CorrRanksFalse.main(("../score_files/natives.set{0}_Rosetta_min/{1}.sc".format(decoy_set, input_pdb), "rosetta"),
                ("../score_files/decoys.set{0}_Rosetta_min/{1}.sc".format(decoy_set, input_pdb), "rosetta"), decoy_name=trim_rosetta(rosetta_decoy), 
                native_name=trim_rosetta(rosetta_native), pdb=input_pdb)   )
    #run correlation_ranks_decoy for all amber decoys
    for decoy_name in decoy_names_amber:
        #first pdb will start with numeric string
        rosetta_native = glob.glob("../pdb/{0}/*relaxed*.pdb".format(input_pdb))[0]
        rosetta_decoy = "../pdb/{0}/{1}_0001.pdb".format(input_pdb, decoy_name)

        native_sf = "../score_files/natives.set{0}_Amber_min/{1}_norestraints.sc".format(decoy_set, input_pdb)
        score_dict = scorefileparse.read_vals(native_sf, "amber", repl_orig=False, trim=True)
        native_name = [ name for name, energy in sorted(score_dict.items(), key=lambda x: x[1][0]) ][0]

	if decoy_name not in decoy_names_rosetta:
            output_r.write(correlate_ranks.main(rosetta_native, rosetta_decoy, "amber", ""))
	    output_r_full.write(CorrRanksDecoy.main(("../score_files/natives.set{0}_Rosetta_min/{1}.sc".format(decoy_set, input_pdb), "rosetta"),
                ("../score_files/decoys.set{0}_Rosetta_min/{1}.sc".format(decoy_set, input_pdb), "rosetta"), decoy_name=trim_rosetta(rosetta_decoy),
                native_name=trim_rosetta(rosetta_native), pdb=input_pdb)   )

        output_a_false.write(CorrRanksFalse.main(("../score_files/natives.set{0}_Amber_min/{1}_norestraints.sc".format(decoy_set, input_pdb), "amber"),
                ("../score_files/decoys.set{0}_Amber_min/{1}_norestraints.sc".format(decoy_set, input_pdb), "amber"), decoy_name=decoy_name, native_name=native_name, pdb=input_pdb)    )

    output_r.close()
    output_r_full.close()
    output_a_full.close()
    output_r_false.close()
    output_a_false.close()
    #output all results into output file

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument ('--input_pdb', '-d', help="directory for input score files and its scoretype")

    parser.add_argument('--decoy_names_rosetta', default=[], action='append', help='pdb name')

    parser.add_argument('--decoy_names_amber', default=[], action='append', help='pdb name')

    args = parser.parse_args()

    main(args.input_pdb, args.decoy_names_rosetta, args.decoy_names_amber)
