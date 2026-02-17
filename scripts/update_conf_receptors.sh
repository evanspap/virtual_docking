#!/bin/bash
# ----------------------------------------------------------
# Script: update_conf_receptors.sh
# Author: Evangelos Papadopoulos
# Version: 1.0
# Date: 2025-09-15
# Control: Bulk update receptor paths in .conf files
#
# Function:
#   Replace all "receptor = ./pdbqt/<file>" lines
#   with the absolute path:
#   "/gpfs/scratch/epapadopoulo/mmsegs_pockets/docking/targets/pdbqt/<file>"
#
# Usage:
#   ./update_conf_receptors.sh <conf_dir>
#
# Example:
#   ./update_conf_receptors.sh ./conf
# ----------------------------------------------------------

if [ $# -lt 1 ]; then
    echo "Usage: $0 <conf_dir>"
    echo "Example: $0 ./conf"
    exit 1
fi

CONF_DIR=$1
ABS_PATH="/gpfs/scratch/epapadopoulo/mmsegs_pockets/docking/targets/pdbqt"

echo "Running: updating receptor paths in $CONF_DIR"

for file in "$CONF_DIR"/*.conf; do
    echo "  -> Updating $file"
    sed -i "s|^receptor = ./pdbqt/|receptor = ${ABS_PATH}/|" "$file"
done

echo "Done!"

