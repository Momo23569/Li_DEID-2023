# de-id
Perl and Python code for de-identifying electronic medical records
# Prerequisites
## Python
* Python 3.5.2
## Perl
* Perl 5, Version 28, Subversion 0 (v5.28.0)
# Running insturctions
## Python Code
### De-identification
1- Change to the python directory

2- run ```python Li_deid_date.py id.text date.phi```

In which:

* ```id.text``` contains Patient Notes.
* ```date.phi``` is the output file that will be created.
### Stats
1- change to the python directory

2- run ```python stats.py id.deid id-phi.phrase date.phi ```

In which:

* ```id.deid``` is the gold standard that is category-blind.
* ```id-phi.phrase``` is the gold standard with the categories included.
* ```date.phi``` is the test file that the stats is run on.
