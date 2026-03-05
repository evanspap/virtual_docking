#!/bin/bash
# MIT License
# -------------------------------------------------------
# Script : estimate_size.sh
# Author : Evangelos Papadopoulos
# Date   : 2025-09-15
# Version: 1.0
#
# Function:
#   Estimate total size of files under a directory by sampling.
#   Prints average file size, total file count, and estimated total.
#
# Usage:
#   ./estimate_size.sh <directory> [sample_size]
# Example:
#   ./estimate_size.sh /gpfs/scratch/epapadopoulo/mmsegs_pockets/docking 2000
# -------------------------------------------------------

DIR=${1:-.}
SAMPLE=${2:-1000}

# Count total files
TOTAL=$(find "$DIR" -type f | wc -l)

if [ "$TOTAL" -eq 0 ]; then
    echo "No files found in $DIR"
    exit 1
fi

echo "Directory   : $DIR"
echo "Total files : $TOTAL"
echo "Sample size : $SAMPLE"
echo

# Sample files and show progress bar
TMP=$(mktemp)
find "$DIR" -type f | shuf -n "$SAMPLE" > "$TMP"

COUNT=0
SUM=0
while read -r FILE; do
    SIZE=$(stat -c %s "$FILE" 2>/dev/null || echo 0)
    SUM=$((SUM + SIZE))
    COUNT=$((COUNT + 1))

    # Progress bar
    PCT=$((COUNT * 100 / SAMPLE))
    BAR=$(printf "%-${PCT}s" "#" | tr ' ' '#')
    echo -ne "\r[${BAR:0:50}] $PCT% ($COUNT/$SAMPLE)"
done < "$TMP"
echo

AVG=$((SUM / COUNT))
EST=$((AVG * TOTAL))

echo "Average file size : $AVG bytes"
echo "Estimated total   : $(echo "$EST/1024/1024/1024" | bc) GB"

rm -f "$TMP"

