#!/bin/bash
#
# run_smiles_to_pdbqt_single_node.sh
#
# Single-node, procedural (non-parallel) conversion of SMILES to PDBQT files.
# Designed for small datasets or local development on a single processor.
#
# Converts a plain SMILES list (one SMILES per line) into:
#   (1) 3D SDF files via RDKit (ETKDGv3 + MMFF/UFF)
#   (2) PDBQT files via Open Babel with Gasteiger partial charges
#
# Usage:
#   ./run_smiles_to_pdbqt_single_node.sh <input.smi>
#
# Example:
#   ./run_smiles_to_pdbqt_single_node.sh small_compounds.smi
#
# Input:
#   - A .smi file where each line contains a SMILES string (no header).
#   - Format options:
#       (A) Single column (SMILES only):
#           CC(C)Cc1ccc(cc1)C(C)C(=O)O
#           CN1CCC[C@H]1c2cccnc2
#           O=C(O)c1ccccc1
#       (B) Two columns (SMILES + NAME, tab-separated):
#           CC(C)Cc1ccc(cc1)C(C)C(=O)O    ibuprofen
#           CN1CCC[C@H]1c2cccnc2          compound_A123
#           O=C(O)c1ccccc1                aspirin
#   - Expected behavior:
#       * Each line is read as a SMILES string (and optional name).
#       * Columns are separated by tab or whitespace.
#       * Empty lines are skipped.
#       * No header line expected (data starts on line 1).
#       * If names are provided (column 2), they are used in output filenames.
#       * If no names are provided, sequential index numbers are used.
#
# Outputs:
#   - SDF_Structures_3D/mol_<idx>_3d.sdf
#   - PDBQT_OBABEL/mol_<idx>_3d.pdbqt
#   - logs_3d/mol_<idx>.out|err
#   - logs_pdbqt/mol_<idx>_3d.out|err
#   - 3d_success.list
#   - pdbqt_success.list
#
# Author: Evangelos Papadopoulos
# Version: 1.0 (Single-node procedural variant)
# Date: 2026-02-03
#

set -euo pipefail

# Print the leading comment header as a manual/help
print_manual() {
  awk '
    /^[[:space:]]*#/ { sub(/^[[:space:]]*#[[:space:]]?/,"", $0); print; next }
    { exit }
  ' "$0"
}

# Detect --debug anywhere in argv and remove it from args
DEBUG=0
_params=()
for _a in "$@"; do
  if [[ "$_a" == "--debug" ]]; then
    DEBUG=1
    continue
  fi
  _params+=("$_a")
done
set -- "${_params[@]:-}"

# Turn on shell tracing if requested
# shell tracing will be enabled later when the debug log is ready

# -----------------------
# Argument parsing
# -----------------------
# Support printing the embedded manual/header
if [[ ${1:-} == "-h" || ${1:-} == "--help" || ${1:-} == "--man" ]]; then
  print_manual
  exit 0
fi

if [[ $# -lt 1 ]]; then
  echo "ERROR: No SMILES file provided. Use --help for usage." >&2
  exit 1
fi

SMI="$1"

# -----------------------
# User configuration
# -----------------------
# RDKit env path (update as needed for your system)
RDKIT_ENV="/gpfs/home/epapadopoulo/my_rdkit_env"

# Open Babel conda env name (update as needed)
OBABEL_ENV="openbabel"

# Get the directory of the input SMILES file
SMI_DIR="$(cd "$(dirname "$SMI")" && pwd)"
SMI_BASENAME="$(basename "$SMI")"

OUT3D="${SMI_DIR}/SDF_Structures_3D"
OUTPDBQT="${SMI_DIR}/PDBQT_OBABEL"

# -----------------------
# Pre-flight checks
# -----------------------
if [[ ! -f "$SMI" ]]; then
  echo "ERROR: Input SMILES file not found: $SMI" >&2
  exit 10
fi

mkdir -p "$OUT3D" "$OUTPDBQT"

SMILES_COUNT=$(wc -l < "$SMI")

echo "=========================================="
echo "Single-node SMILES to PDBQT conversion"
echo "Job started : $(date)"
echo "Output dir  : $SMI_DIR"
echo "Input file  : $SMI_BASENAME"
echo "SMILES lines: $SMILES_COUNT"
echo "=========================================="

if [[ "$DEBUG" -eq 1 ]]; then
  # Debug log in the input directory with timestamp
  DEBUG_LOG="${SMI_DIR}/run_smiles_to_pdbqt.$(date +%Y%m%dT%H%M%S).debug.log"
  touch "$DEBUG_LOG"

  debug_echo() { echo "$@" >> "$DEBUG_LOG"; }

  # Send shell xtrace output to the debug log (Bash 4.1+)
  if [[ -n ${BASH_VERSION:-} ]]; then
    exec {XTRACEFD}>>"$DEBUG_LOG" || true
    export BASH_XTRACEFD=${XTRACEFD}
    PS4='+ $(date "+%Y-%m-%d %H:%M:%S")\011 '
    set -x
  fi

  debug_echo "DEBUG: RDKIT_ENV=$RDKIT_ENV"
  debug_echo "DEBUG: OBABEL_ENV=$OBABEL_ENV"
  if [[ -f /gpfs/software/Anaconda3/etc/profile.d/conda.sh ]]; then
    debug_echo "DEBUG: conda script exists: yes"
  else
    debug_echo "DEBUG: conda script exists: no"
  fi
  debug_echo "DEBUG: conda in PATH: $(command -v conda || echo not-found)"
  if command -v conda >/dev/null 2>&1; then
    debug_echo "DEBUG: conda environments:"
    conda info --envs >>"$DEBUG_LOG" 2>&1 || true

    debug_echo "DEBUG: trying to activate RDKit env and import RDKit"
    if (conda activate "$RDKIT_ENV" >/dev/null 2>&1 || conda activate -p "$RDKIT_ENV" >/dev/null 2>&1); then
      python - >>"$DEBUG_LOG" 2>&1 <<'PY'
try:
    import rdkit
    print('RDKit', rdkit.__version__)
except Exception as e:
    print('RDKit import failed:', e)
PY
    else
      debug_echo "DEBUG: could not activate RDKit env '$RDKIT_ENV'"
    fi

    debug_echo "DEBUG: trying to activate OpenBabel env and check obabel"
    if (conda activate "$OBABEL_ENV" >/dev/null 2>&1 || conda activate -p "$OBABEL_ENV" >/dev/null 2>&1); then
      if command -v obabel >/dev/null 2>&1; then
        obabel -V >>"$DEBUG_LOG" 2>&1 || true
      else
        debug_echo "DEBUG: obabel binary not found in '$OBABEL_ENV'"
      fi
    else
      debug_echo "DEBUG: could not activate OpenBabel env '$OBABEL_ENV'"
    fi
  fi
  # Inform user where debug was written
  echo "Debug log: $DEBUG_LOG"
fi

# Load conda
export PS1=""
source /gpfs/software/Anaconda3/etc/profile.d/conda.sh

# -----------------------
# Phase A: SMILES -> 3D SDF (RDKit)
# -----------------------
echo "Phase A: RDKit 3D generation started: $(date)"
conda activate "$RDKIT_ENV"

idx=0
success_count=0
while IFS=$'\t' read -r smi name || [[ -n "$smi" ]]; do
  [[ -z "$smi" ]] && continue
  ((idx++))
  
  # Use provided name, or fall back to index-based naming
  file_id="${name:-mol_${idx}}"
  
  sdf_file="${OUT3D}/${file_id}_3d.sdf"
  
  echo "  [$idx/$SMILES_COUNT] Processing: $file_id"
  
  if [[ -n "$name" ]]; then
    # Pass name to Python script via inline Python
    python3 << PYEOF
from rdkit import Chem
from rdkit.Chem import AllChem

idx = $idx
smi = "$smi"
out_sdf = "$sdf_file"
name = "$name"

mol = Chem.MolFromSmiles(smi)
if mol is None:
    print(f"[{idx}] RDKit parse failed")
    exit(3)

mol = Chem.AddHs(mol)

params = AllChem.ETKDGv3()
params.randomSeed = idx % 2147483647
params.useRandomCoords = True

if AllChem.EmbedMolecule(mol, params) != 0:
    print(f"[{idx}] Embed failed")
    exit(4)

try:
    if AllChem.MMFFHasAllMoleculeParams(mol):
        AllChem.MMFFOptimizeMolecule(mol, mmffVariant="MMFF94s", maxIters=2000)
    else:
        AllChem.UFFOptimizeMolecule(mol, maxIters=2000)
except Exception as e:
    print(f"[{idx}] Minimization failed: {e}")
    exit(5)

mol.SetProp("_Name", name)
mol.SetProp("SMILES", smi)

w = Chem.SDWriter(out_sdf)
w.write(mol)
w.close()
PYEOF
  else
    # No name provided, use default index-based naming
    python3 << PYEOF
from rdkit import Chem
from rdkit.Chem import AllChem

idx = $idx
smi = "$smi"
out_sdf = "$sdf_file"

mol = Chem.MolFromSmiles(smi)
if mol is None:
    print(f"[{idx}] RDKit parse failed")
    exit(3)

mol = Chem.AddHs(mol)

params = AllChem.ETKDGv3()
params.randomSeed = idx % 2147483647
params.useRandomCoords = True

if AllChem.EmbedMolecule(mol, params) != 0:
    print(f"[{idx}] Embed failed")
    exit(4)

try:
    if AllChem.MMFFHasAllMoleculeParams(mol):
        AllChem.MMFFOptimizeMolecule(mol, mmffVariant="MMFF94s", maxIters=2000)
    else:
        AllChem.UFFOptimizeMolecule(mol, maxIters=2000)
except Exception as e:
    print(f"[{idx}] Minimization failed: {e}")
    exit(5)

mol.SetProp("_Name", f"mol_{idx}")
mol.SetProp("SMILES", smi)

w = Chem.SDWriter(out_sdf)
w.write(mol)
w.close()
PYEOF
  fi
done < "$SMI"

find "$OUT3D" -name "*_3d.sdf" -size +0c | sort > "${SMI_DIR}/3d_success.list"
echo "Phase A finished: $(date)"
echo "3D SDF success count: $(wc -l < "${SMI_DIR}/3d_success.list") / $SMILES_COUNT"

# -----------------------
# Phase B: 3D SDF -> PDBQT (Open Babel, Gasteiger charges)
# -----------------------
echo "Phase B: Open Babel PDBQT generation started: $(date)"
conda activate "$OBABEL_ENV"

sdf_count=0
while IFS= read -r sdf_path; do
  ((sdf_count++))
  basename_sdf=$(basename "$sdf_path")
  basename_base="${basename_sdf%.sdf}"
  
  pdbqt_file="${OUTPDBQT}/${basename_base}.pdbqt"
  
  echo "  [$sdf_count/$(wc -l < "${SMI_DIR}/3d_success.list")] Converting: $basename_sdf"
  
  obabel "$sdf_path" -O "$pdbqt_file" --partialcharge gasteiger || true
done < "${SMI_DIR}/3d_success.list"

find "$OUTPDBQT" -name "*_3d.pdbqt" -size +0c | sort > "${SMI_DIR}/pdbqt_success.list"
echo "Phase B finished: $(date)"
echo "PDBQT success count: $(wc -l < "${SMI_DIR}/pdbqt_success.list") / $(wc -l < "${SMI_DIR}/3d_success.list")"

# -----------------------
# Summary
# -----------------------
echo "=========================================="
echo "Job finished : $(date)"
echo "Output dir   : $SMI_DIR"
echo "3D SDF dir   : $OUT3D"
echo "PDBQT dir    : $OUTPDBQT"
echo "3D success   : ${SMI_DIR}/3d_success.list ($(wc -l < "${SMI_DIR}/3d_success.list") files)"
echo "PDBQT success: ${SMI_DIR}/pdbqt_success.list ($(wc -l < "${SMI_DIR}/pdbqt_success.list") files)"
echo "=========================================="
