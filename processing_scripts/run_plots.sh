#!/bin/bash

scorefilepath="/Users/arubenstein/Dropbox/Research/Khare/CADRES/DecoyDiscrimination/score_files/"
output_path="/Users/arubenstein/Dropbox/Research/Khare/CADRES/DecoyDiscrimination/plots/"
decoydiscpath="/Users/arubenstein/git_repos/cadres_submissions/2016/decoy_discrimination/team_2/results"
loopmodpath="/Users/arubenstein/git_repos/cadres_submissions/2016/loop_modeling/team_2/results"

python ./plot_disc_v_disc.py --input_dir $decoydiscpath/rosetta_desc rosetta --input_dir $decoydiscpath/amber_desc amber --output_pre /Users/arubenstein/Dropbox/Research/Khare/CADRES/DecoyDiscrimination/plots/decoydisc &
python ./plot_disc_v_disc.py --input_dir $loopmodpath/rosetta/scores rosetta --input_dir $loopmodpath/amber/scores amber --output_pre /Users/arubenstein/Dropbox/Research/Khare/CADRES/DecoyDiscrimination/plots/loopmod &
python ./find_best_solution.py --input_dir $decoydiscpath/rosetta_desc rosetta --input_dir $decoydiscpath/amber_desc amber --output_pre /Users/arubenstein/Dropbox/Research/Khare/CADRES/DecoyDiscrimination/plots/decoydisc/pareto
python ./find_best_solution.py --input_dir $loopmodpath/rosetta/scores rosetta --input_dir $loopmodpath/amber/scores amber --output_pre /Users/arubenstein/Dropbox/Research/Khare/CADRES/DecoyDiscrimination/plots/loopmod/pareto
python ./find_best_solution.py --input_dir $scorefilepath/decoys.set1_Rosetta_min rosetta --input_dir $scorefilepath/decoys.set1_Amber_min amber --output_pre /Users/arubenstein/Dropbox/Research/Khare/CADRES/DecoyDiscrimination/plots/decoydisc/pareto_from_oldsf
python ./plot_disc_v_disc.py --input_dir $scorefilepath/decoys.set1_Rosetta_min rosetta --input_dir $scorefilepath/decoys.set1_Amber_min amber --output_pre /Users/arubenstein/Dropbox/Research/Khare/CADRES/DecoyDiscrimination/plots/decoydisc &
