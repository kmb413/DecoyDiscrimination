#!/bin/sh

# energy decomposition for each restart file.

source ~/amber_git/amber/amber.sh
MMPBSA.py -i mmgbsa.in -cp tz2.parm7 -y tz2.nc
