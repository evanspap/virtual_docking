#!/bin/bash
# ----------------------------------------------------------
# Script: prepare_receptors.sh
# Author: Evangelos Papadopoulos
# Date: 2025-09-13
# Version: 1.2
#
# Function:
#   For each *_b_filter.pdb file in the given directory:
#     1. Run reduce to add hydrogens and generate *_b_filter_reduce.pdb
#     2. Run mk_prepare_receptor.py to prepare PDBQT receptor
#
# Usage:
#   ./prepare_receptors.sh [-n] <input_directory>
#
# Options:
#   -n   Dry run mode (print commands without executing)
#
# Example:
#   ./prepare_receptors.sh ./pdb
#   ./prepare_receptors.sh -n ./pdb
#
# Output:
#   - *_b_filter_reduce.pdb files in input_directory
#   - PDBQT receptor files in ../pdbqt relative to input_directory
# ----------------------------------------------------------

dry_run=0

# Parse options
if [ "$1" = "-n" ]; then
    dry_run=1
    shift
fi

if [ $# -lt 1 ]; then
    echo "Usage: $0 [-n] <input_directory>"
    echo "Example: $0 ./pdb"
    exit 1
fi

indir="$1"
outdir="../pdbqt"

mkdir -p "$outdir"

for pdb in "$indir"/*_b_filter.pdb; do
    [ -e "$pdb" ] || continue
    base=$(basename "$pdb" .pdb)              # e.g. ADSS2_b_filter
    reduce_out="${indir}/${base}_reduce.pdb"  # e.g. ADSS2_b_filter_reduce.pdb
    pdbqt_out="${outdir}/${base}_reduce"      # e.g. ../pdbqt/ADSS2_b_filter_reduce

    echo "Running: reduce -BUILD $pdb > $reduce_out"
    if [ $dry_run -eq 0 ]; then
        reduce -BUILD "$pdb" > "$reduce_out"
    fi

    echo "Running: mk_prepare_receptor.py --read_pdb $reduce_out --allow_bad_res -o $pdbqt_out -p"
    if [ $dry_run -eq 0 ]; then
        mk_prepare_receptor.py --read_pdb "$reduce_out" --allow_bad_res -o "$pdbqt_out" -p
    fi
done

