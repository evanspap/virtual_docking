#!/bin/bash
#SBATCH -J vina_durations
#SBATCH -p short-28core
#SBATCH -n 1
#SBATCH -c 28
#SBATCH -t 01:00:00
#SBATCH -o vina_durations_%j.log

# ----------------------------------------------------------
# Script: vina_parse_durations.sh
# Author: Evangelos Papadopoulos
# Date: 2025-09-09
# Version: 1.1
#
# Function:
#   Parse όλα τα AutoDock Vina .out αρχεία σε έναν φάκελο
#   και εξάγει CSV με CID, χρόνο εκτέλεσης (sec), και status.
#   Δείχνει ETA μέσω GNU parallel.
#
# Usage:
#   sbatch vina_parse_durations.sh <out_folder> [output_csv]
#
# Example:
#   sbatch vina_parse_durations.sh ./p1_300k_nci_r1 results.csv
# ----------------------------------------------------------

if [ $# -lt 1 ]; then
    echo "Usage: $0 <out_folder> [output_csv]"
    echo "Example: sbatch $0 ./p1_300k_nci_r1 vina_durations.csv"
    exit 1
fi

OUTDIR="$1"
RESULT="${2:-vina_durations.csv}"   # default αν δεν δοθεί 2ο arg

echo "CID,Duration_seconds,Status" > "$RESULT"

find "$OUTDIR" -type f -name "*.out" \
| parallel --eta -j $SLURM_CPUS_PER_TASK '
    CID=$(basename {} | sed "s/_.*//");
    START=$(grep "^Start:" {} | sed "s/Start: //");
    END=$(grep "^End:" {} | sed "s/End: //");
    if [ -n "$START" ] && [ -n "$END" ]; then
        TS1=$(date -d "$START" +%s);
        TS2=$(date -d "$END" +%s);
        echo "$CID,$((TS2-TS1)),FINISHED";
    else
        echo "$CID,NA,NOT_FINISHED";
    fi
' >> "$RESULT"

echo "Done. Results saved in $RESULT"

