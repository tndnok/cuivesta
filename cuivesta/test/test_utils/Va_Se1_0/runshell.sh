#!/bin/zsh
#$ -S /bin/zsh
#$ -cwd
#$ -V
#$ -j y
#$ -N test
#$ -o std.log
#$ -q ato.q
#$ -pe all_pe* 36
#============ Shell Script ============
# source /storage/imai/venv/bin/activate
/storage/imai/venv/bin/python /storage/imai/scripts/vasp_custodian.py
