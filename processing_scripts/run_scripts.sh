python correlate_ranks.py --rosetta_decoy ../pdb/1t2i/Rosetta_1t2i_empty_tag_323_0002.pdb --rosetta_native ../pdb/1t2i/rosetta_native_22_relaxed_1t2i_0001_0001.pdb --amber_decoy ../pdb/1t2i/min_NoH_empty_tag_323_0002per_res.sc --amber_native ../pdb/1t2i/min_NoH_78_relaxed_1t2i_0001per_res.sc --output_prefix ./ --false_scoretype amber

python correlate_ranks.py --rosetta_decoy ../pdb/1enh/empty_tag_19244_0001_0001.pdb --rosetta_native ../pdb/1enh/rosetta_native_6_relaxed_1enh_0001_0001.pdb --amber_decoy ../pdb/1enh/min_NoH_empty_tag_19244_0001.sc --amber_native ../pdb/1enh/min_NoH_17_relaxed_1enh_0001per_res.sc --output_prefix ./ --false_scoretype amber

#python correlate_ranks.py --rosetta_decoy ../pdb/2zxj/empty_tag_1_794_0001.pdb --rosetta_native ../pdb/2zxj/rosetta_native_16_relaxed_2zxj_0001_0001.pdb --amber_decoy ../pdb/2zxj/min_NoH_empty_tag_1_794per_res.sc --amber_native ../pdb/2zxj/min_NoH_99_relaxed_2zxj_0001per_res.sc --output_prefix ./ --false_scoretype rosetta

#python correlate_ranks.py --rosetta_decoy ../pdb/2zxj/Rosetta_2zxj_empty_tag_1212_0001.pdb --rosetta_native ../pdb/2zxj/rosetta_native_16_relaxed_2zxj_0001_0001.pdb --amber_decoy ../pdb/2zxj/min_NoH_empty_tag_1212_0001per_res.sc --amber_native ../pdb/2zxj/min_NoH_99_relaxed_2zxj_0001per_res.sc --output_prefix ./ --false_scoretype rosetta

#python correlate_ranks.py --rosetta_decoy ../pdb/2zxj/empty_tag_1_1042_0001.pdb --rosetta_native ../pdb/2zxj/rosetta_native_16_relaxed_2zxj_0001_0001.pdb --amber_decoy ../pdb/2zxj/min_NoH_empty_tag_1_1042per_res.sc --amber_native ../pdb/2zxj/min_NoH_99_relaxed_2zxj_0001per_res.sc --output_prefix ./ --false_scoretype rosetta

#python correlate_ranks.py --rosetta_decoy ../pdb/1bkr/empty_tag_7051_0001_0001.pdb --rosetta_native ../pdb/1bkr/rosetta_native_78_relaxed_1bkr_0001_0001.pdb --amber_decoy ../pdb/1bkr/min_NoH_empty_tag_7051_0001per_res.sc --amber_native ../pdb/1bkr/min_NoH_56_relaxed_1bkr_0001per_res.sc --output_prefix ./ --false_scoretype rosetta

python correlate_ranks.py --rosetta_decoy ../pdb/1bkr/Rosetta_1bkr_empty_tag_15420_0001.pdb --rosetta_native ../pdb/1bkr/rosetta_native_78_relaxed_1bkr_0001_0001.pdb --amber_decoy ../pdb/1bkr/min_NoH_empty_tag_15420_0001per_res.sc --amber_native ../pdb/1bkr/min_NoH_56_relaxed_1bkr_0001per_res.sc --output_prefix ./ --false_scoretype amber 

python correlate_ranks.py --rosetta_decoy ../pdb/1sen/empty_tag_723_0010_0001.pdb --rosetta_native ../pdb/1sen/rosetta_native_70_relaxed_1sen_0001_0001.pdb --amber_decoy ../pdb/1sen/min_NoH_empty_tag_723_0010per_res.sc --amber_native ../pdb/1sen/min_NoH_90_relaxed_1sen_0001per_res.sc --output_prefix ./ --false_scoretype amber

python correlate_ranks.py --rosetta_decoy ../pdb/1sen/empty_tag_9156_0001_0001.pdb --rosetta_native ../pdb/1sen/rosetta_native_70_relaxed_1sen_0001_0001.pdb --amber_decoy ../pdb/1sen/min_NoH_empty_tag_9156_0001per_res.sc --amber_native ../pdb/1sen/min_NoH_90_relaxed_1sen_0001per_res.sc --output_prefix ./ --false_scoretype amber

python PerformAnalysis.py --input_pdb 3cx2 --decoy_set 1 --decoy_names_rosetta empty_tag_10857_0001 --decoy_names_rosetta empty_tag_507_0003 --decoy_names_rosetta empty_tag_5357_0001 --decoy_names_rosetta empty_tag_552_0011 --decoy_names_rosetta empty_tag_6007_0001 --decoy_names_rosetta empty_tag_9514_0001 --decoy_names_amber empty_tag_10086_0001 --decoy_names_amber empty_tag_5371_0001 

#turn adjust_text off and rotation=90, width 4, height 4
python PlotPNear.py --input_dir ../score_files/decoys.all0_Rosetta_min/ "rosetta" --input_dir ../score_files/decoys.all0_Amber_min/ "amber" --output_pre ../plots/ --x_axis "talaris2014" --y_axis "Amber"
python PlotPNear.py --input_dir ../score_files/decoys.all0_Rosetta_relax_beta/ "rosetta" --input_dir ../score_files/decoys.all0_Amber_min/ "amber" --output_pre ../plots/ --x_axis "REF2015" --y_axis "Amber"

#turn adjust_text on and rotation=0, width 2.8, height 4.4
python PlotPNear.py --input_dir ../score_files/loops_Rosetta_min/ "rosetta" --input_dir ../score_files/loops_Amber_min/ "amber" --output_pre ../plots/loops --x_axis "talaris2014" --y_axis "Amber"

#turn adjust_text on and rotation=0
python PlotPareto.py --input_dir ../score_files/decoys.all0_Rosetta_min "rosetta" --input_dir ../score_files/decoys.all0_Amber_min amber --output_pre ../plots/ --rmsd_cutoff 1000000000

python ./PlotFalseMinHeat.py --csv_vals_rosetta ../false_minima/analysis/rosetta_false_true.csv --output_prefix ../plots/rosetta_false_true --csv_vals_amber ../false_minima/analysis/amber_false_true.csv

#highlight_outlier=True
python PlotER.py --rosetta_score_file ../score_files/loops_Rosetta_min/1tca.all.sc --amber_score_file ../score_files/loops_Amber_min/1tca.sc --output_prefix ../plots/plot

#highlight_outlier=False
python PlotER.py --rosetta_score_file ../score_files/decoys.all0_Rosetta_min/1t2i.sc --amber_score_file ../score_files/decoys.all0_Amber_min/1t2i_norestraints.sc --output_prefix ../plots/plot
python PlotER.py --rosetta_score_file ../score_files/decoys.all0_Rosetta_min/2qy7.sc --amber_score_file ../score_files/decoys.all0_Amber_min/2qy7_norestraints.sc --output_prefix ../plots/plot
python PlotER.py --rosetta_score_file ../score_files/decoys.all0_Rosetta_min/1sen.sc --amber_score_file ../score_files/decoys.all0_Amber_min/1sen_norestraints.sc --output_prefix ../plots/plot
