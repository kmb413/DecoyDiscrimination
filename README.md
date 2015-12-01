# DecoyDiscrimination
Rosetta Community-Wide Benchmark -- Decoy Discrimination 

================
Dataset contents
================

Each dataset contains:

    1000 structures representing the lowest-energy structures binned in RMS space. 
    The structures were generated using Mike Tyka's loophash protocol, are stored as silent files, and have been relaxed with score12.


==================
Evaluation metrics
==================

Evaluation uses a measure from Mike Tyka, where energies are normalized such that 0 = 5%ile energy and 1 = 95%ile energy. 
Then the energy gap between the lowest-energy native and lowest-energy non-native model is calculated (lower value = deeper energy well for native). 
This is averaged over 6 different "threshold" values at which we call a structure native: 1, 1.5, 2, 3, 4, and 6Å RMSD from the crystal structure. 
A script for computing this score is attached. To run the discrimination script:

./disc [file containing list of scorefiles]


===========
Description
===========

Benchmark name: Decoy discrimination (landscape energy evaluation)

Benchmark subsets: Two sets as described above

Overview: 
    Set 1 (assembled by Mike Tyka) was specifically chosen where score12 has a poor energy landscape. 
    Set 2 (assembled by Patrick Conway) was chosen as an independent validation set; consequently, Rosetta's discrimination is better on set2 than on set1 using score12 and talaris2014.


=================
Submission format
=================

Teams must provide the following information when submitting their results. File and folder names below should be relative to the location assigned to the team for upload. README files may be submitted in plain text (README.txt) or reStructuredText (README.rst).

Method description

    A README file in the root directory containing these data e.g.:

    Team name: The Mighty Docks
    Contact person 1: Shane O'Connor, Kortemme Lab, shane.oconnor@ucsf.edu
    ...more lines for any other contacts...
    Git branch name: master
    Git SHA1 hash: 2062f13a4477b9c4533398f61da06a8dd6eb71aa
    Method: A description of the method
    Methods must be checked into GitHub by the submission date but can live on a branch.

Method executables

    A /method folder containing

    A README file describing how the method is run
    Command lines, shell scripts, or RosettaScripts used in the method
    An example simulation script which... TBA
