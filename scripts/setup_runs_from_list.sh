#!/bin/bash

# ----------------------------------------------------------
# Script: setup_runs_from_list.sh
# Author: Evangelos Papadopoulos
# Date: 2025-09-16
# Version: 1.7
#
# Function:
#   Reads a tab-delimited list of Protein and Pocket pairs from a file.
#   For each entry, creates the necessary directory structure,
#   copies and substitutes template files (cp + sed),
#   and prepares input files for docking runs.
#   A dry-run option is available to print commands without executing.
#
# Usage:
#   ./setup_runs_from_list.sh protein_pocket_list.tsv docking_type root_folder [--dry-run]
#
# Example:
#   ./setup_runs_from_list.sh proteins.tsv 300k_nci_r1 /gpfs/scratch/epapadopoulo/mmsegs_pockets/docking --dry-run
#
# Example input list (TSV):
#   Protein    Pocket
#   EP300      EP300_P1
#   CAD        CAD_P1
#   AK2        AK2_P1
#   DMXL1      DMXL1_P1
#   DMXL1      DMXL1_P2
#   CAD        CAD_P2
#
# Expected folder structure under <root_folder>:
#   param_files/
#   runs/
#   output/
# Expected templates & scripts:
#   scripts/run_template_<suffix>_mpirun.sbatch
#   param_files/param_file_template_<suffix>_<docktype>
#   scripts/vina_commands_v1.3.py
# Generated folders:
#   runs/<protein>/<suffix>_<docktype>/
#   output/<protein>/<suffix>_<docktype>/
# Generated vina commands input file:
#   runs/<protein>/<suffix>_<docktype>/input.txt
# ----------------------------------------------------------

if [ $# -lt 3 ]; then
    echo "Usage: $0 <protein_pocket_list.tsv> <docking_type> <root_folder> [--dry-run]"
    echo "Example: $0 proteins.tsv 300k_nci_r1 /gpfs/scratch/epapadopoulo/mmsegs_pockets/docking --dry-run"
    exit 1
fi

LIST=$1
DOCKTYPE=$2
ROOT=$3
DRYRUN=false

if [ "$4" == "--dry-run" ]; then
    DRYRUN=true
fi

while IFS=$'\t' read -r PROT POCKET _; do
    # Skip header
    if [[ "$PROT" == "Protein" ]]; then
        continue
    fi

    # Extract pocket suffix (p1, p2, ...)
    SUFFIX=$(echo "$POCKET" | awk -F'_' '{print tolower($2)}')

    echo "Processing $PROT $SUFFIX with docking type $DOCKTYPE"

    CMD1="mkdir -p $ROOT/runs/${PROT,,}/${SUFFIX}_${DOCKTYPE}/logs"
    CMD2="mkdir -p $ROOT/output/${PROT,,}/${SUFFIX}_${DOCKTYPE}/"

    # Copy template param file and substitute placeholders
    SRC_PARAM=$ROOT/param_files/param_file_template_${SUFFIX}_${DOCKTYPE}
    DST_PARAM=$ROOT/param_files/param_file_${PROT,,}_${SUFFIX}_${DOCKTYPE}
    CMD3a="cp $SRC_PARAM $DST_PARAM"
    CMD3b="sed -i 's/template/${PROT,,}/g; s/p1/${SUFFIX}/g' $DST_PARAM"

    CMD4="python $ROOT/scripts/vina_commands_v1.3.py \
        $DST_PARAM \
        > $ROOT/runs/${PROT,,}/${SUFFIX}_${DOCKTYPE}/input.txt"

    # Copy sbatch run script and substitute placeholders
    SRC_RUN=$ROOT/scripts/run_template_${SUFFIX}_mpirun.sbatch
    DST_RUN=$ROOT/runs/${PROT,,}/${SUFFIX}_${DOCKTYPE}/run_${PROT,,}_${SUFFIX}_mpirun.sbatch
    CMD5a="cp $SRC_RUN $DST_RUN"
    CMD5b="sed -i 's/template/${PROT,,}/g; s/p1/${SUFFIX}/g' $DST_RUN"

    if $DRYRUN; then
        echo "[DRY-RUN] $CMD1"
        echo "[DRY-RUN] $CMD2"
        echo "[DRY-RUN] $CMD3a"
        echo "[DRY-RUN] $CMD3b"
        echo "[DRY-RUN] $CMD4"
        echo "[DRY-RUN] $CMD5a"
        echo "[DRY-RUN] $CMD5b"
    else
        eval "$CMD1"
        eval "$CMD2"
        eval "$CMD3a"
        eval "$CMD3b"
        eval "$CMD4"
        eval "$CMD5a"
        eval "$CMD5b"
    fi

done < "$LIST"

