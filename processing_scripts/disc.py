#!/usr/bin/python 

'''copy of disc.py script which allows you to transfer data easily. not currently used anywhere'''

import sys
import os,copy
import string
import re
import gzip
import bz2


def main( argv, disc_divs):
  non_numerical_cols = [
  "aln_id",
  "user_tag",
  "description",
  "usid",
  "husid",
  "pdb",
  "__file__"
  ];

  if len(argv) < 2:
    sys.stderr.write("CODE ERROR") 
    sys.exit(1)

  ## Analyse options 

  showfilename = False
  multifilemode = False
  summode = False
  normalize_sums = False
  normalize_all = False
  normalize_all_but_key  = False
  offset_sums = False
  offset_all = False
  discriminate = False

  for arg in argv[1:]:
    if arg == "-": 
      multifilemode = True
      continue


  columnbreak = False

  columns = []
  files = []
  sums = []


  next_sum_type = ""

  # arguments made by Mike, not using...
  for arg in argv[1:]:
    if arg == "-o": 
      offset_all= True
      continue
    if arg == "-os": 
      offset_sums = True
      continue
    if arg == "-d": 
      discriminate = True
      normalize_all = True
      normalize_all_but_key = True
      continue
    if arg == "-n": 
      normalize_all = True
      continue
    if arg == "-nk": 
      normalize_all = True
      normalize_all_but_key = True
      continue
    if arg == "-ns": 
      normalize_sums = True
      continue
    if arg == "-f": 
      showfilename = True
      continue
    if arg == "-": 
      columnbreak = True
      continue
    
    if not columnbreak:
      files.append( arg )
      if not multifilemode:
        columnbreak = True
      continue

    if arg[0] == '-' or arg[0] == '+' or arg[0] == '.' or (arg[0] >= '0' and arg[0] <= '9'):
      next_sum_type = arg
      summode = True
      continue

    column_name = arg
    sum_type = next_sum_type
    columns.append( ( column_name, sum_type ) )
    
    next_sum_type = ""

  if len(columns) == 0: columns = [(RMSD_KEY,''), (SCORE_KEY,'') ] 

  final_data = []


  ## now iterate through files and print columns etc..
  for filename in files:

    ## gzip/bzip support
    lines = []
    if( filename[-3:] == ".gz" ): ## gzipped
      file = gzip.open(filename,"r")
      lines = string.split(file.read(),"\n")
    elif( filename[-4:] == ".bz2" ): ## gzipped
      lines = bz2.BZ2File( filename,"r").readlines()  
    else: ## plain text
      file = open(filename,"r")
      lines = string.split(file.read(),"\n")
    
    
    donetitles = False
    names = []
    for arg,sumtype in columns:
      names.append((arg,-1))

    for (i,(n,j)) in enumerate(names):
      names[i] = (string.lower(n), j)
     
    if len(names)<=0:  
      sys.stderr.write("Warning: no columns names supplied: defaulting to rms vs score\n")
      names.append( (SCORE_KEY, -1) ) 
      names.append( (RMSD_KEY, -1) ) 


    for number,l in enumerate(lines):
      token = string.split(l)

      if len(token) <= 0: continue
      ## SCORE LINE HEADERS
      if not donetitles and ( token[0] == "SCORE:" or token[0] == "pdb" or token[0] == "description") :
        ## look for names
        
        for ti,t in enumerate(token):
          for (i,(n,j)) in enumerate(names):
            if string.lower(t) == n:  ## if names match
              (existing_n, existing_ti) = names[i];
              if( existing_ti < 0):
                names[i] = (n,ti)  ## remember index
                
        Error = False
        for i,(n,j) in enumerate(names):
          if n == "__file__": ## special column
            names[i] = (n, -1 )  
          elif j < 0:
            sys.stderr.write("Error: Cannot find column named '%s' in '%s' \n"%(n,filename) )
            Error = True
        
	if Error: sys.exit(1)
        donetitles = True
        continue
      
      ## SCORE LINE
      if token[0] == "SCORE:" or token[0][0:3] == "min" :
        token = string.split(l)
        brokenline = False
        for (n,i) in names: 
          if i >= len( token ):
            brokenline = True
            continue  
        if brokenline : continue
        
	## Check columns for correctness. Allow only special columns to have 
        # non-numerical values ( see array at the top of this code file)  
        for (n,i) in names:
          ## Figure out if the tag is an official non-numeric one
          is_nonnumtag = False
          for nonnumtags in non_numerical_cols:
            if n == nonnumtags:
              is_nonnumtag = True
              break
          if is_nonnumtag: break

          ## if we're here, the tag is considered a numeric one and thus must pass the float conversion test
          try:
            t = float( token[i] )
          except:
            ## if it does not then ignore this line - we assume it's corrupted
            brokenline = True;    
	
	## Ignore broken lines!
        if brokenline : continue
        
	## Ok, if we're here, the line is clean and we can go ahead to extract the data
        newdataline = dict();

        # now actuall extract the data into an array
        for (n,i) in names:
          if n == "__file__":   
            ## record the filename as "data"
            newdataline[ n ] = filename
          else:
            ## extract the data itself
            newdataline[ n ] = token[i]
          #sys.stdout.write("%10s "%token[i]) 
        #sys.stdout.write("\n")
        
        
        ## and append that array to the overall data stack
        final_data.append( newdataline )  

  ################################################

  # Now print combined data - weighted?
 # this assumes that columns list is rmsd, score*
 # Input: (rmsd,""), (score1,0.5), (score2,0.5) Output: (rmsd,0.5), ("",0.3)
 # Input: (rmsd,""), (score1,0.5) Output: (rmsd,0.5), (score1,0.4)
 # Input: (rmsd,""), (score1,1.0), (score2,1.0) Output: (rmsd,0.5), ("",0.6)
  combined_data = []

  for l in final_data:
    sum = 0
    sumactive = False

    new_combined_data_line = [] 

    for (n,i) in columns:
      
      if i == '':
        if sumactive:
          #sys.stdout.write("%10s "%sum )
          new_combined_data_line.append( ("", sum  ) )
          sum = 0
          sumactive = False

        #sys.stdout.write("%10s "%l[ n ])
        new_combined_data_line.append( ( n, l[ n ] ) )
      else:
        sum += float(l[ n ]) * float(i)
        sumactive = True

    if sumactive:
        #sys.stdout.write("%10s "%sum )
        new_combined_data_line.append( ("", sum ) )
        sum = 0
        sumactive = False

    combined_data.append( new_combined_data_line )
    given_data_run_disc(combined_data, discriminate, disc_divs)
 
def given_data_run_disc(combined_data, discriminate, disc_divs):

  if not 'FRACMAX' in locals() and not 'FRACMAX' in globals():
    FRAC_MAX = 0.95
  if not 'FRACMIN' in locals() and not 'FRACMIN' in globals():
    FRAC_MIN = 0.05
  if not 'discmin' in locals() and not 'discmin' in globals():
    discmin = -1.0
  if not 'discmax' in locals() and not 'discmax' in globals():
    discmax =  1.0
  if not 'NORMALIZE' in locals() and not 'NORMALIZE' in globals():
    NORMALIZE =  True

  range_data = dict()

  for l in combined_data:
    for (n,i) in l:
      if range_data.get( n ): range_data[n].append( float(i) )
      else: range_data[n] = [ i ];

  perc_high = dict()
  perc_low  = dict()

  disc_lowest = [ dict(), dict(), dict() ] 

  for key in range_data.keys():
    range_data[key].sort()
    perc_high[key] = float(range_data[key][ int( len( range_data[key] ) * FRAC_MAX)  ])
    perc_low[key]  = float(range_data[key][ int( len( range_data[key] ) * FRAC_MIN)  ])

  for l in combined_data:
    '''
    for keyindex,(n,i) in enumerate(l):
      try: 
        value =  float(i) 

        if normalize_all or ( normalize_sums and n == '' ):
          #sys.stdout.write("Here: %f %f \n"%( perc_low[ n ], perc_high[ n ] ) )
          if normalize_all_but_key and keyindex == 0:
            value = float(i) 
          else:
            value = ( float(i) - perc_low[ n ] ) / ( perc_high[ n ] - perc_low[ n ] )    

          #safe guide for strangely low scores (necessary for docking interaction energy)
        
        elif offset_all or ( offset_sums and n == '' ):
          value = ( float(i) - perc_low[ n ] ) 
        if not discriminate:
          sys.stdout.write("%10.3f "%value )
      except:
        if not discriminate:
          sys.stdout.write("%10s "%i )
    '''
    #print l
    if discriminate:
      rms = float(l[0][1])

      #safe guide for unrealistic cases
      #if float(l[1][1]) < MINSCORE:
       # continue

      if NORMALIZE:
        score = (float(l[1][1]) - perc_low[ n ] ) / ( perc_high[ n ] - perc_low[ n ] )
      else:
        score = (float(l[1][1]) - perc_low[ n ] ) / dE
      
      for dd in disc_divs:
        if rms < dd:
          bucket_index = 0
        else:
          bucket_index = 1
        if dd not in disc_lowest[bucket_index] or score < disc_lowest[bucket_index][dd]: 
          disc_lowest[bucket_index][dd] = score
    
    if not discriminate:
      sys.stdout.write("\n")


  missing_count = 0
  discs = []
  for i in disc_divs:
    if i not in disc_lowest[0] and  i not in disc_lowest[1]: 
      discs.append(0.0)
      continue
    if i not in disc_lowest[0]: 
      disc_lowest[0][i] = disc_lowest[1][i]
      missing_count += 1
    if i not in disc_lowest[1]: 
      disc_lowest[1][i] = disc_lowest[0][i]
      missing_count += 1
    #print i, disc_lowest[0][i], disc_lowest[1][i]
    disc_loc = disc_lowest[0][i] - disc_lowest[1][i]

    discs.append( min(discmax,max(disc_loc,discmin)) )

  return sum(discs)/float(len(discs)), discs, missing_count

def run_disc(argv):
    scs = [l[:-1] for l in file(argv[1])]
    runtype = 'mono'

    RMSD_KEY = 'rmsd'
    FRAC_MAX = 0.95
    FRAC_MIN = 0.05
    discmin = -1.0
    discmax =  1.0
    MINSCORE = -100000 #safecut

    if '-dock' in argv: #docking
        SCORE_KEY = 'ddg'
        default_disc_divs = [1.0,2.0,5.0]
        NORMALIZE = False
        dE = 5.0 #use uniform energy gap

    elif '-loop' in argv:
        SCORE_KEY = 'total_score'
        default_disc_divs = [1.0,1.5,2.0,2.5,3.0]
        NORMALIZE = False
        dE = 5.0 #use uniform energy gap

    else: #for monomeric structure prediction
        SCORE_KEY = 'total_score'
        #default_disc_divs = [1.0,3.0,4.0,6.0]
        default_disc_divs = [1.0,1.5,2.0,2.5,3.0,4.0,6.0]
        NORMALIZE = True

    disc_counts = [ 0.0 for i in default_disc_divs ] 
    disc_averages = [ 0.0 for i in default_disc_divs ]
    discs_at_bin = [ [] for i in default_disc_divs ]

    for sc in copy.copy(scs):
      if not os.path.exists(sc): 
        print 'removed: ', sc
        scs.remove(sc)
    total = len( scs )

    for ind,i in enumerate(scs):
      if i[0] == '#':
        continue
      #for our purposes, argv should be "filename - 1.0 energy1 2.0 energy2" 
      #todo - this doesn't work
      result = calculate_disc([i,argv[2:-1]], default_disc_divs)
      discs = result[0]  ## teh first part is the discrimination score array 
      
      for di,de in enumerate( discs ):
        if de < 0:
          disc_counts[di] += 1 
        disc_averages[di] += de
        discs_at_bin[di].append(de)

      #print i, " %5.3f"%(sum(discs)/float(len(discs))), " ".join(  "% 4.3f"%i for i in discs  )  

    median_gaps = []
    for disc in discs_at_bin:
      disc.sort()
      med = disc[int(len(disc)*0.5)]
      median_gaps.append(med)

    average_disc = sum( disc_counts  ) / float(len(default_disc_divs)) * 100.0 / float(total)
    average_gaps = sum( disc_averages ) / float(len(default_disc_divs)) / float(total)

    #print "%5.4f %3.0f %3d - "%(average_gaps, average_disc, total)
    #print " ".join(  "% 4.3f"%(i/float(total)) for i in disc_averages  ) + " - " + " ".join( "%2.0f "%( 100*i/float(total) ) for i in disc_counts )

    #print "%5.4f"%(sum(median_gaps)/len(median_gaps))+" ".join( "% 4.3f"%val for val in median_gaps)


    #output is n lines + 2 (where n is no. of score files)
    #each score file has a line. first token is average disc and rest are per division
    #second to last line is average_gaps average_disc total_scorefiles
    #last line is disc averages across scorefiles - percent negative discs across scorefiles


if __name__ == "__main__":
   main(sys.argv[0])
