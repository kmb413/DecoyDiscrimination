#!/bin/bash

dir=$1

for subdir in $(ls -l | grep '^d' | awk '{print $9}')
do

	cd $subdir

	for scorefile in $(ls *.sc)
	do
		cp $scorefile '../'$subdir'_'$scorefile
	done
	
	cd ../

done
