#!/bin/bash
# ======================================================================
# Docking Result Aggregator for Seawulf
# ======================================================================
#
# Purpose:
#   Automate the parsing, sorting, and merging of AutoDock Vina outputs
#   across one or more docking folders on Seawulf.
#
# Author: Evangelos Papadopoulos
# Version: 1.9
# Date: 2025-09-04
# ======================================================================

set -euo pipefail

# ---- Hardwired paths
RUN_SCRIPT="/gpfs/scratch/epapadopoulo/mmsegs_pockets/docking/setup/scripts/run_python_inputfolder_ext_arguments.sh"
PARSE_SCRIPT="/gpfs/scratch/epapadopoulo/mmsegs_pockets/docking/setup/scripts/parse_vina_out.py"
MERGE_SCRIPT="/gpfs/scratch/epapadopoulo/mmsegs_pockets/docking/setup/scripts/merge_cid_smiles.py"
CID_SMILES="/gpfs/scratch/epapadopoulo/mmsegs_pockets/docking/compounds/nci_sdf/cid_smiles.tsv"

# ---- Check args
if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <folder> <topN>"
  echo "Example: $0 /gpfs/scratch/.../EP300 2"
  exit 1
fi

INPUT_FOLDER="$1"
TOPN="$2"

if [[ ! -d "$INPUT_FOLDER" ]]; then
  echo "Error: folder not found: $INPUT_FOLDER"
  exit 2
fi

# ---- Derive names
BASENAME=$(basename "$INPUT_FOLDER")
PARENTDIR=$(dirname "$INPUT_FOLDER")
PARENTNAME=$(basename "$PARENTDIR")
OUTFILE="${PARENTDIR}/${PARENTNAME}_${BASENAME}.out"

TMP_CSV="${PARENTDIR}/tmp_${BASENAME}.csv"
SORTED_CSV="${PARENTDIR}/sorted_${BASENAME}.csv"
HEADER_FILE="${PARENTDIR}/header_${BASENAME}.csv"

TOTAL_FILES=$(grep -c "^Running:" "$PARENTDIR/../logs/syvn1_docking_hbm_1260803.out" 2>/dev/null || find "$INPUT_FOLDER" -maxdepth 1 -name '*.out' -size +0c | wc -l)
START_TIME=$(date +%s)

echo "=== Running parsing for folder: $INPUT_FOLDER (top=$TOPN) ==="
echo "[INFO] Total expected .out files: $TOTAL_FILES"

# Step 1a: Header from first non-empty .out
FIRST_FILE=$(find "$INPUT_FOLDER" -maxdepth 1 -name '*.out' -size +0c | head -n 1 || true)
if [[ -n "${FIRST_FILE:-}" ]]; then
  echo "[INFO] Using first .out for header: $FIRST_FILE"
  python "$PARSE_SCRIPT" "$FIRST_FILE" --header --top "$TOPN" > "$HEADER_FILE"
else
  echo "[ERROR] No non-empty .out files found in $INPUT_FOLDER"
  exit 3
fi

# Step 1b: Parse all files
echo "[INFO] Parsing all .out files..."
bash "$RUN_SCRIPT" "$PARSE_SCRIPT" "$INPUT_FOLDER" out --top "$TOPN" > "$TMP_CSV" &
PARSER_PID=$!

# Progress monitor
(
  while kill -0 $PARSER_PID 2>/dev/null; do
    LINES=$(wc -l < "$TMP_CSV" || echo 0)
    NOW=$(date +%s); ELAPSED=$((NOW - START_TIME))
    if [[ $LINES -gt 0 ]]; then
      PCT=$((LINES * 100 / TOTAL_FILES))
      RATE=$((LINES / ELAPSED))
      ETA=$(( (TOTAL_FILES - LINES) / RATE ))
      echo "[PROGRESS] $LINES/$TOTAL_FILES ($PCT%) ETA≈${ETA}s"
    else
      echo "[PROGRESS] waiting for lines..."
    fi
    sleep 30
  done
) &

wait $PARSER_PID

if [[ ! -s "$TMP_CSV" ]]; then
  echo "[ERROR] No data written to $TMP_CSV."
  exit 5
fi

echo "[INFO] Combining header + data"
cat "$HEADER_FILE" "$TMP_CSV" > "${TMP_CSV}.with_header"
mv "${TMP_CSV}.with_header" "$TMP_CSV"

# Step 2: Sort (skip header)
echo "[INFO] Sorting results by affinity"
{ head -n 1 "$TMP_CSV" && tail -n +2 "$TMP_CSV" | sort -t, -k3,3n; } > "$SORTED_CSV"

# Step 3: Merge with CID–SMILES
echo "[INFO] Merging with CID–SMILES mapping"
python "$MERGE_SCRIPT" "$CID_SMILES" "$SORTED_CSV" "$OUTFILE"

echo "=== Done. Final file: $OUTFILE ==="

