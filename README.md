# cuivesta
Convert from vasp POSCAR format file to vesta format file.  
cuivesta can control some of options in VESTA gui.  

**Note: Unexceted input may break running VESTA process which you already have.

Installation instructions
---------------------------------------------------------
```
% git clone https://github.com/***
% cd cuivesta
% ls
cuivesta  README.md  requirements.txt  setup.py
% pip install -e .
```

---------------------------------------------------------

# How to use

## 1. Change preference
- create POSCAR.vesta at current directory.
```
% ls
POSCAR
% cat POSCAR
Ba1 Ti1 O3
   1.00000000000000
     3.9928776341656214    0.0000000000000000    0.0000000000000000
     0.0000000000000000    3.9928776341656214    0.0000000000000000
     0.0000000000000000    0.0000000000000000    3.9928776341656214
   Ba   Ti   O
     1     1     3
Direct
  0.5000000000000000  0.5000000000000000  0.5000000000000000
  0.0000000000000000  0.0000000000000000  0.0000000000000000
  0.5000000000000000  0.0000000000000000  0.0000000000000000
  0.0000000000000000  0.0000000000000000  0.5000000000000000
  0.0000000000000000  0.5000000000000000  0.0000000000000000
% cuivesta -p POSCAR 
<vesta_io>: generated POSCAR.vesta.
% ls
POSCAR       POSCAR.vesta
% head POSCAR.vesta
#VESTA_FORMAT_VERSION 3.3.0
TITLE
Ba1 Ti1 O3

CELLP
3.992878 3.992878 3.992878 90.000000 90.000000 90.000000

STRUC
1 Ba Ba1  1.0  0.500000 0.500000 0.500000
 0.0 0.0 0.0
```
- filter bonds to be visible (e.g., show only Ti-O bond in BaTiO3's POSCAR)
```
% cuivesta -p POSCAR -b Ti-O  
<vesta_io>: generated POSCAR.vesta.
```
- change type of element size (e.g., from atom to ionic)
```
% cuivesta -p POSCAR --atoms ionic
<vesta_io>: generated POSCAR.vesta.
```
- control plot range (e.g., extend to neighboring cells)
```
% cuivesta -p POSCAR --boundary "0 2 0 2 0 2"
<vesta_io>: generated POSCAR.vesta.
```
- To expand/reduce isotropically, single integer/fraction is also OK
```
% cuivesta -p POSCAR --boundary "2"
<vesta_io>: generated POSCAR.vesta.
```
- centering specified atom (e.g., set index 1 atom to the center of sight and reduce plot range to be half)
```
% cuivesta -p POSCAR --boundary "1/2" --centering 1
<vesta_io>: generated POSCAR.vesta.
```
## 2. Add 3d arrows
##### from *.txt file (all atoms version)
```
% cuivesta -p POSCAR -v vector.txt --boundary "-0.5 0.5 -0.5 0.5 -0.5 0.5" -b Ti-O
<vesta_io>: generated POSCAR.vesta.
% cat vector.txt
0 0 0
0 0 0.2
0 0 0
0 0 0
0 0 0
```
##### This is same as below manner. If field length is not 3 but 4, first number is interpreted as atom index.
```
% cuivesta -p POSCAR -v vector.txt --boundary "-0.5 0.5 -0.5 0.5 -0.5 0.5" -b Ti-O
<vesta_io>: generated POSCAR.vesta.
% cat vector.txt
2 0 0 0.2
```
##### Generate displacement vectors from difference from second POSCAR file (e.g., diff from POSCAR2 to POSCAR1)
```
% cuivesta -p POSCAR1 --diff POSCAR2
<vesta_io>: generated POSCAR1.vesta.
```

## 3. Add lattice planes
##### Manual add (e.g., show hkl=100 plane)
```
% cuivesta -p POSCAR --planes 100 -b Ti-O
<vesta_io>: generated POSCAR.vesta.
```
##### Manual add (show hkl=001 and 011 plane with distance d=4.0 A from origin)
```
% cuivesta -p POSCAR --planes 001-4.0 011-4.0 -b Ti-O
<vesta_io>: generated POSCAR.vesta.
```
##### These are same if use *txt file
```
% cat planes.txt
001-4.0
011-4.0
% cuivesta -p POSCAR --planes planes.txt -b Ti-O
<vesta_io>: generated POSCAR.vesta.
```

## 4. Use extensions for pydefect
##### Generate defect induced displacement vectors by reading defect.json for Va_O1_2 in 64-atom MgO. (-m: amplitude of norm of vectors)
```
% cuivesta -p CONTCAR --defect --boundary "-0.5 0.5 -0.5 0.5 -0.5 0.5" -m 1.2
<vesta_io>: defect.json found.
<vesta_io>: generated CONTCAR.vesta.
```
##### Add vacancy site as dummy element "XX".
```
% cuivesta -p CONTCAR --defect --vacancy -m 1.2
<vesta_io>: defect.json found.
<vesta_io>: generated CONTCAR.vesta.
```
##### Set vacancy site to center of sight (vacancy's dummy index is 64, so index 0 (internally -1) and/or 64 means the last of array)
```
% cuivesta -p CONTCAR --defect --vacancy --centering 0 
<vesta_io>: defect.json found.
<vesta_io>: generated CONTCAR.vesta.
```
Files and directories included in vise distribution
--------------------------------------------------------
~~~
  README                    : introduction
  setup.py                  : installation script
  requirements.txt          : list of required packages

  /cuivesta/main                : cli interface controlling option and flags
  /cuivesta/blocks              : constructers for blocks written in VESTA format files
  /cuivesta/template            : VESTA's default parameters for plot bonds of atoms
  /cuivesta/options             : hidden parameters which are not user friendry
  /cuivesta/utils               : module functions and extensions for defect 
  /cuivesta/test                : test files used for unitests
~~~~

