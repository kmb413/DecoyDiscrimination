#!/bin/bash

if [ "$1" == "-h" ]; then
  echo "Usage: <inputpath> <filepattern> <outpath> <abs_outpath> <script> <n_servers> <this_server> <n_cores_per_script>"
  echo "Sample: /home/arubenstein/CADRES/DecoyDiscrimination/decoys.set1.init/1vkk/ *.pdb /home/arubenstein/CADRES/DecoyDiscrimination/Rosetta/relax/decoys.set1/1vkk/ 1 relax.sh 1 1 1"
  exit 0
fi

inputpath=$1
filepattern=$2
outpath=$3
abs_outpath=$4
script=$5
n_servers=$6
this_server=$7
scorefxn=$8
n_cores_per_script=$9

cd $inputpath

#search for appropriate files based on filepattern
#if filepattern is none searches for directories instead

if [ "none" = "$filepattern" ];
then
	second_loop=1
	ls -l | grep '^d' | awk '{print $9}' > files_list.txt
else
	second_loop=0
	ls ''$filepattern'' > files_list.txt
fi

#determines begin and end indices based on how many files there are and how many servers there are
n_files=$( wc -l files_list.txt | awk '{print $1}')

n_files_in_group=$(( $n_files / $n_servers + 1 ))
end_index=$(( $n_files_in_group * $this_server ))
this_server=$(( $this_server - 1 ))
begin_index=$(( $n_files_in_group * $this_server))

#sets counters
counter=0

filecounter=0

n_cores=50

#n_cores_per_script must be a factor of n_cores TODO: output warning if not
if [ -z ${n_cores_per_script} ];
then
	n_cores=$(( $n_cores / $n_cores_per_script ))
fi	

#loops thru file of filenames or dir names
while read item
do
	
        filecounter=$(( $filecounter + 1 ))

	#if filecounter is between beginning and end indices
        if [ $filecounter -gt $begin_index ] && [ $filecounter -le $end_index ];
        then

		#set pdb_id
                pdb_id="${item%%.*}"

 		if [[ $abs_outpath -eq "1" ]]
		then
			final_outpath=$outpath'/'$scorefxn
		else
			final_outpath=$outpath'/'$scorefxn'/'$pdb_id
		fi
			
		#if looping thru dirs then loop thru files inside
		if [[ $second_loop -eq "1" ]]
		then
			cd $inputpath'/'$item
			for pdb in $(ls *.pdb)
			do
			     counter=$((counter+1))
			     eval nohup "/home/arubenstein/CADRES/DecoyDiscrimination/Rosetta/scripts/$script" $inputpath'/'$item $pdb $final_outpath $pdb_id $scorefxn &
			     if (( $counter % $n_cores == 0 ));
				then
				wait
			     fi
			done
                	cd $inputpath
		else
	
		     counter=$((counter+1))
		     eval nohup "/home/arubenstein/CADRES/DecoyDiscrimination/Rosetta/scripts/$script" $inputpath $item $final_outpath $pdb_id $scorefxn &
		     if (( $counter % $n_cores == 0 )); 
			then
			wait
		     fi
		fi
	fi
done < files_list.txt

rm files_list.txt
