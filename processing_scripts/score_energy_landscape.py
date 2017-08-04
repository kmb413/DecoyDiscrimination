#!/usr/bin/env python2.7
# Tom Linsky (tlinsky@uw.edu)
# based on plot_energy_landscape.py by Javier Castellanos

import string
import random
from argparse import ArgumentParser
import sys
import os
import math
#import numpy
import glob
from subprocess import Popen, PIPE
boinc_scripts_dir = os.path.dirname( __file__ )
utils_scripts_dir = os.path.join( boinc_scripts_dir, '..', 'utils' )
sys.path.append( boinc_scripts_dir )
sys.path.append( utils_scripts_dir )
from boinc_data import read_boinc_dat, write_boinc_dat
import Jabot
from ScoreFile import ScoreData
import tempfile
#from SilentDataWrapper import SilentDataReader, SilentDataWriter

description = '''Given a scorefile, score the energy landscape according the metrics defined below:

*SampledRMS* - RMS at which 2% of points are lower, and 98% of points are higher

*PNear* - Vikram's boltzmann-sum-based probability of being in the folded state. Defined as: sum( e^( -( rms^2/lambda^2 ) )*e^( -score/temp ) )/sum( e^( -score/temp ) )

*WeightedRMS* - Given the energies and the temperature, tells the expected RMS. Defined as: sum( rms*e^( -score/temp ) )/sum( e^( -score/temp ) )

*calcbinnedboltz.pl* - The DiMaio method.  Divide the landscape into bins, and compute boltzmann sum for all points before the bin and all points. Average these sums for all bin boundaries.  See calcbinnedboltz.pl for more defails.

*tyka.py* - The method described in figure 2 of Conway, Tyka et al, Protein Sci. 2014 ("Relaxation of backbone bond geometry improves protein energy landscape modeling.")
'''

parser = ArgumentParser( description=description )
parser.add_argument('-terms', metavar='ETERM', type=str, default=['rms','score'], nargs=2,  help='RMS and score terms to pick (in that order), by default will pick the lowest values unless a \'+\' sign is put infront of the term')
parser.add_argument('-compression', default = None, help='compression type (gz, bz2 or None)')
parser.add_argument('-one_relaxed', action='store_true', help='Use only one representative structure from relax run and add to abinitio results (default add best several times with a 1:1000 ratio)' )
parser.add_argument('-use_best_relaxed', action='store_true', help='Use the best relaxed structure instead of the mean')
parser.add_argument('-no_relaxed', action='store_true', help='Skip using relaxed structures')
parser.add_argument('-rms', default=2.0, type=float, help='RMS which is the center of the gaussian for penalizing bad rms points. e^( -(rms^2/lambda^2) )*e^( -score/temp )' )
parser.add_argument('-temp', default=0.5, type=float, help='Temperature for boltzmann sum' )
parser.add_argument('-abinitio_scorefile', default='fold_abinitio_*.sc', type=str, help='Scorefile to use for ab initio decoys.' )
parser.add_argument('-relax_scorefile', default='fold_relax_*.sc', type=str, help='Scorefile to use for relaxed structures.' )
parser.add_argument('-tyka_flags', metavar='TYKA', default=[], nargs='+', type=str, help='String of flags to pass to tyka_discrimination script (without dashes).' )
args = parser.parse_args()

def get_scorefile_name( path ):
    abinitio_scorefiles = glob.glob( path )
    if len(abinitio_scorefiles) == 0:
        print "Error: The abinitio scorefile could not be found in the given directory:", args.dir
        sys.exit(1)
    elif len(abinitio_scorefiles) > 1:
        print "Error: More than one abinitio scorefile was found in the given directory and this script is unsure of which file to use.  Files=", abinitio_scorefiles
        sys.exit(1)
    assert( len(abinitio_scorefiles) == 1 )
    return abinitio_scorefiles[0]

# script rules:
# arg1 = RMSD term
# arg2 = score term
# arg3 = abinitio scorefile
# output to stderr = single floating point score
def score_script( script, args ):
    cmd = [ script ] + args
    p = Popen( cmd, stderr=PIPE, stdout=PIPE, stdin=PIPE )
    return p.stderr.read().strip()

def read_scorefile( name ):
    rms_terms = []
    scf = ScoreData( compression=args.compression )
    scf.read_score( name )
    for key in scf.data.keys():
        val = []
        for term in args.terms:
            val.append( float(scf.data[key][term]) )
        rms_terms.append( val )
    return rms_terms

def score( rms_data ):
    num_sum = 0.0
    denom_sum = 0.0
    weighted_rms = 0.0
    max_score = None
    for (rms, score) in rms_data:
        if max_score is None or score < max_score:
            max_score = score

    ''' RMS coverage will be defined as RMS of best 2% of points '''
    rmslst = [ rms for (rms, score) in rms_data ]
    rmslst.sort()
    rms_idx = int(float(len(rmslst))*0.02)

    for (rms, score) in rms_data:
        energy = math.exp( -(score-max_score)/args.temp )
        weight_energy = math.exp( -rms*rms/(args.rms*args.rms) )*energy
        weighted_rms += rms*energy
        num_sum += weight_energy
        ''' upweight energy that has higher RMS '''
        denom_sum += energy
    return ( rmslst[rms_idx], num_sum/denom_sum, weighted_rms/denom_sum )

abinitio_scorefile = get_scorefile_name( args.abinitio_scorefile )
rms_data = read_scorefile( abinitio_scorefile )

if not args.no_relaxed:
    relax_scorefile = get_scorefile_name( args.abinitio_scorefile )
    rms_data_relax = read_scorefile( relax_scorefile )
else:
    rms_data_relax = []

score_scripts = glob.glob( os.path.join( boinc_scripts_dir, 'scoring_methods', '*' ) )

# Add a few points from relaxed structure
if not args.no_relaxed:
    best = None
    sum = [ 0.0, 0.0 ]
    for d in rms_data_relax:
        sum = [ d[0] + sum[0], d[1] + sum[1] ]
        if best is None or d[1] < best[1]:
            best = [ d[0], d[1] ]
    sum = [ x / len(rms_data_relax) for x in sum ]

    for count in range( len(rms_data)/1000 ):
        if args.use_best_relaxed:
            rms_data += [best]
        else:
            rms_data += [sum]
        if args.one_relaxed:
            break

# write rms data for use in scoring scripts
sf_out = [ '\t'.join( [ 'SCORE:', args.terms[0], args.terms[1], "description" ] ) ]
for ( rms, scoreval ) in rms_data:
    sf_out.append( 'SCORE:\t%.5f\t%.5f' % ( rms, scoreval ) )
scorefile = 'tmp_sf_%d' % os.getpid()
with open( scorefile, 'w' ) as f:
    f.write( '\n'.join( sf_out ) + '\n' )

(sampled_rms, pnear, weighted_rms) = score(rms_data)

output = '\t'.join( [ 'SampledRMS', 'PNear', 'WeightedRMS' ] + [ os.path.basename( script ) for script in score_scripts ] ) + '\n'

scores = [ str(sampled_rms), str(pnear), str(weighted_rms) ]
for script in score_scripts:
    script_args = [ args.terms[0], args.terms[1], scorefile ]
    if 'tyka' in script:
        script_args += [ '-' + x for x in args.tyka_flags ]
    if '1d' in script:
        temp_fn = "temp_" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4)) + ".txt"
	with open(temp_fn, "w") as f:
            f.write(scorefile)
        script_args = [ args.terms[1], temp_fn, "0.1" ]
    scores.append( score_script( script, script_args ).strip() )
    try:
	os.remove(temp_fn)
	pass
    except:
	pass
output += '\t'.join( scores ) + '\n'
print output,
os.remove( scorefile )
