#!/usr/bin/env bash
# extract_vina_results.sh
#
# Purpose:
#   Scan a folder of AutoDock Vina .pdbqt output files and extract scoring
#   information for every MODEL block in each file.
#
# Output:
#   CSV written to stdout with a single header line for the whole table.
#   One row is produced per MODEL.
#
# Extracted fields:
#   LIGAND,MODEL,VINA_SCORE,RMSD_LB,RMSD_UB,INTER_PLUS_INTRA,INTER,INTRA,UNBOUND
#
# Filename handling:
#   By default, LIGAND is clipped at the first underscore in the filename
#   to preserve the original behavior.
#   Use --full-name to keep the complete filename stem instead.
#
# Usage:
#   extract_vina_results.sh [--full-name] <pdbqt_folder>
#
# Examples:
#   ./extract_vina_results.sh /path/to/B1_2ZHR_aln6UJ0_out_2
#   ./extract_vina_results.sh --full-name /path/to/B1_2ZHR_aln6UJ0_out_2
#
# Author: Evangelos Papadopoulos
# Date: 2026-03-20
# Version: 1.2

set -euo pipefail

keep_full_name=0

usage() {
  echo "Usage: $0 [--full-name] <pdbqt_folder>"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --full-name)
      keep_full_name=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      break
      ;;
    -*)
      echo "Error: unknown option '$1'"
      usage
      exit 1
      ;;
    *)
      break
      ;;
  esac
done

if [ $# -ne 1 ]; then
  usage
  exit 1
fi

folder="$1"

if [ ! -d "$folder" ]; then
  echo "Error: '$folder' is not a directory."
  exit 1
fi

printf "LIGAND,MODEL,VINA_SCORE,RMSD_LB,RMSD_UB,INTER_PLUS_INTRA,INTER,INTRA,UNBOUND\n"

for file in "$folder"/*.pdbqt; do
  [ -e "$file" ] || continue

  base=$(basename "$file")
  stem=${base%.pdbqt}

  if [ "$keep_full_name" -eq 1 ]; then
    ligand="$stem"
  else
    ligand=${stem%%_*}
  fi

  awk -v ligand="$ligand" '
    function reset_fields() {
      vina_score = ""
      rmsd_lb = ""
      rmsd_ub = ""
      inter_plus_intra = ""
      inter = ""
      intra = ""
      unbound = ""
    }

    function emit_model() {
      if (vina_score == "") {
        return
      }

      model_to_print = (current_model == "" ? 1 : current_model)
      printf "%s,%s,%s,%s,%s,%s,%s,%s,%s\n",
             ligand,
             model_to_print,
             vina_score,
             rmsd_lb,
             rmsd_ub,
             inter_plus_intra,
             inter,
             intra,
             unbound
    }

    BEGIN {
      current_model = ""
      saw_model = 0
      reset_fields()
    }

    /^MODEL[[:space:]]+/ {
      if (saw_model) {
        emit_model()
        reset_fields()
      }
      current_model = $2
      saw_model = 1
      next
    }

    /^REMARK VINA RESULT:/ {
      vina_score = $4
      rmsd_lb = $5
      rmsd_ub = $6
      next
    }

    /^REMARK INTER \+ INTRA:/ {
      inter_plus_intra = $5
      next
    }

    /^REMARK INTER:/ {
      inter = $3
      next
    }

    /^REMARK INTRA:/ {
      intra = $3
      next
    }

    /^REMARK UNBOUND:/ {
      unbound = $3
      next
    }

    /^ENDMDL$/ {
      emit_model()
      reset_fields()
      next
    }

    END {
      if (!saw_model) {
        emit_model()
      }
    }
  ' "$file"
done
