#!/bin/bash

# ----------------------------------------------------------
# Script: setupRun.sh
# Author: Evangelos Papadopoulos
# Date: 2025-09-22
# Version: 2.1
#
# Summary:
#   Sets up a single docking run for a given protein and pocket.
#   It substitutes placeholders in template files (param_file and run_template)
#   with the provided arguments. Always starts from p1 template.
#
# Usage:
#   ./setupRun.sh <protein> <pocket> <docktype> <root_folder> <partition> <nodes> <tasks_per_node> <time> [--dry-run]
#
# Example:
#   ./setupRun.sh NUP37 p2 300k_nci_r1 /gpfs/scratch/... large-28core 72 28 08:00:00 --dry-run
#
# Expected folder structure under <root_folder>:
#   param_files/
#   runs/
#   output/
# Expected templates & scripts:
#   scripts/run_template_p1_mpirun_<docktype>.sbatch
#   param_files/param_file_template_p1_<docktype>
#   scripts/vina_commands_v1.3.py
# Generated folders:
#   runs/<protein>/<suffix>_<docktype>/
#   output/<protein>/<suffix>_<docktype>/
# Generated vina commands input file:
#   runs/<protein>/<suffix>_<docktype>/input.txt
# ----------------------------------------------------------

if [ $# -lt 8 ]; then
    echo "Usage: $0 <protein> <pocket> <docktype> <root_folder> <partition> <nodes> <tasks_per_node> <time> [--dry-run]"
    echo "Example: $0 NUP37 p2 300k_nci_r1 /gpfs/scratch/... large-28core 72 28 08:00:00 --dry-run"
    exit 1
fi

PROT=$1
SUFFIX=$2
DOCKTYPE=$3
ROOT=$4
PARTITION=$5
NODES=$6
TPN=$7
TIME=$8
DRYRUN=false

if [ "$9" == "--dry-run" ]; then
    DRYRUN=true
fi

RUN_DIR=$ROOT/runs/${PROT,,}/${SUFFIX}_${DOCKTYPE}
OUT_DIR=$ROOT/output/${PROT,,}/${SUFFIX}_${DOCKTYPE}

CMD1="mkdir -p $RUN_DIR/logs"
CMD2="mkdir -p $OUT_DIR"

# Always start from p1 template
BASE_SUFFIX="p1"

# Copy and substitute param file
SRC_PARAM=$ROOT/param_files/param_file_template_${BASE_SUFFIX}_${DOCKTYPE}
DST_PARAM=$ROOT/param_files/param_file_${PROT,,}_${SUFFIX}_${DOCKTYPE}
CMD3a="cp $SRC_PARAM $DST_PARAM"
CMD3b="sed -i 's/template/${PROT,,}/g; s/${BASE_SUFFIX}/${SUFFIX}/g; s/PARTITION_PLACEHOLDER/${PARTITION}/g; s/NNODES_PLACEHOLDER/${NODES}/g; s/TPN_PLACEHOLDER/${TPN}/g; s/TIME_PLACEHOLDER/${TIME}/g' $DST_PARAM"

CMD4="python $ROOT/scripts/vina_commands_v1.3.py \
    $DST_PARAM \
    > $RUN_DIR/input.txt"

# Copy and substitute run script
SRC_RUN=$ROOT/scripts/run_template_${BASE_SUFFIX}_mpirun_${DOCKTYPE}.sbatch
DST_RUN=$RUN_DIR/run_${PROT,,}_${SUFFIX}_mpirun_${DOCKTYPE}.sbatch
CMD5a="cp $SRC_RUN $DST_RUN"
CMD5b="sed -i 's/template/${PROT,,}/g; s/${BASE_SUFFIX}/${SUFFIX}/g; s/docktype/${DOCKTYPE}/g; s/PARTITION_PLACEHOLDER/${PARTITION}/g; s/NNODES_PLACEHOLDER/${NODES}/g; s/TPN_PLACEHOLDER/${TPN}/g; s/TIME_PLACEHOLDER/${TIME}/g' $DST_RUN"

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

