#!/bin/bash
#
# run_smiles_to_pdbqt.sbatch
#
# Converts a plain SMILES list (one SMILES per line) into:
#   (1) 3D SDF files via RDKit (ETKDGv3 + MMFF/UFF)
#   (2) PDBQT files via Open Babel with Gasteiger partial charges
#
# Usage:
#   sbatch run_smiles_to_pdbqt.sbatch <input.smi>
#
# Example:
#   sbatch run_smiles_to_pdbqt.sbatch WGAN_GA_novel_unique_filtered_compounds_18768_noheader.smi
#
# Input:
#   - A .smi file where each line is a SMILES string (no header).
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
# Version: 2.0
# Date: 2026-01-19
#

#SBATCH --job-name=smiles2pdbqt
#SBATCH --partition=short-40core
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=40
#SBATCH --mem=0
#SBATCH --time=4:00:00
#SBATCH --output=smiles2pdbqt.%j.out
#SBATCH --error=smiles2pdbqt.%j.err

set -euo pipefail

# -----------------------
# Argument parsing
# -----------------------
if [[ $# -lt 1 ]]; then
  echo "ERROR: No SMILES file provided."
  echo
  echo "Usage:"
  echo "  sbatch run_smiles_to_pdbqt.sbatch <input.smi>"
  echo
  echo "Example:"
  echo "  sbatch run_smiles_to_pdbqt.sbatch WGAN_GA_novel_unique_filtered_compounds_18768_noheader.smi"
  exit 1
fi

SMI="$1"

# -----------------------
# User configuration
# -----------------------
# RDKit env is path-based on your system (as confirmed)
RDKIT_ENV="/gpfs/home/epapadopoulo/my_rdkit_env"

# Open Babel conda env name (as confirmed)
OBABEL_ENV="openbabel"

CORES="${SLURM_CPUS_PER_TASK:-40}"

OUT3D="SDF_Structures_3D"
OUTPDBQT="PDBQT_OBABEL"
LOG3D="logs_3d"
LOGP="logs_pdbqt"

# -----------------------
# Pre-flight checks
# -----------------------
if [[ ! -f "$SMI" ]]; then
  echo "ERROR: Input SMILES file not found: $SMI" >&2
  exit 10
fi

mkdir -p "$OUT3D" "$OUTPDBQT" "$LOG3D" "$LOGP"

echo "=========================================="
echo "Job started : $(date)"
echo "Working dir : $(pwd)"
echo "Input file  : $SMI"
echo "SMILES lines: $(wc -l < "$SMI")"
echo "Cores       : $CORES"
echo "=========================================="

# Load conda
export PS1=""
source /gpfs/software/Anaconda3/etc/profile.d/conda.sh

# GNU parallel check
if ! command -v parallel >/dev/null 2>&1; then
  echo "ERROR: GNU parallel not found in PATH." >&2
  exit 11
fi

# -----------------------
# Helper Python script (RDKit SMILES -> 3D SDF)
# -----------------------
cat > smiles_line_to_3d.py << 'PYEOF'
#!/usr/bin/env python3
import sys
from rdkit import Chem
from rdkit.Chem import AllChem

def main():
    if len(sys.argv) != 4:
        print("usage: smiles_line_to_3d.py <idx> <smiles> <out.sdf>", file=sys.stderr)
        return 2

    idx = int(sys.argv[1])
    smi = sys.argv[2]
    out_sdf = sys.argv[3]

    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        print(f"[{idx}] RDKit parse failed", file=sys.stderr)
        return 3

    mol = Chem.AddHs(mol)

    params = AllChem.ETKDGv3()
    params.randomSeed = idx % 2147483647
    params.useRandomCoords = True

    if AllChem.EmbedMolecule(mol, params) != 0:
        print(f"[{idx}] Embed failed", file=sys.stderr)
        return 4

    try:
        if AllChem.MMFFHasAllMoleculeParams(mol):
            AllChem.MMFFOptimizeMolecule(mol, mmffVariant="MMFF94s", maxIters=2000)
        else:
            AllChem.UFFOptimizeMolecule(mol, maxIters=2000)
    except Exception as e:
        print(f"[{idx}] Minimization failed: {e}", file=sys.stderr)
        return 5

    mol.SetProp("_Name", f"mol_{idx}")
    mol.SetProp("SMILES", smi)

    w = Chem.SDWriter(out_sdf)
    w.write(mol)
    w.close()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
PYEOF

chmod +x smiles_line_to_3d.py

# -----------------------
# Phase A: SMILES -> 3D SDF (RDKit)
# -----------------------
echo "Phase A: RDKit 3D generation started: $(date)"
conda activate "$RDKIT_ENV"

awk 'NF>0 {print NR "\t" $0}' "$SMI" > smiles_indexed.tsv

cat smiles_indexed.tsv \
| parallel -j "$CORES" --colsep '\t' \
  "python ./smiles_line_to_3d.py {1} {2} ./${OUT3D}/mol_{1}_3d.sdf \
   > ./${LOG3D}/mol_{1}.out 2> ./${LOG3D}/mol_{1}.err || true"

find "./$OUT3D" -name "mol_*_3d.sdf" -size +0c | sort > 3d_success.list
echo "3D SDF success count: $(wc -l < 3d_success.list)"
echo "Phase A finished: $(date)"

# -----------------------
# Phase B: 3D SDF -> PDBQT (Open Babel, Gasteiger charges)
# -----------------------
echo "Phase B: Open Babel PDBQT generation started: $(date)"
conda activate "$OBABEL_ENV"

cat 3d_success.list \
| parallel -j "$CORES" \
  "f={}; b=\$(basename {} .sdf); \
   obabel {} -O ./${OUTPDBQT}/\${b}.pdbqt --partialcharge gasteiger \
   > ./${LOGP}/\${b}.out 2> ./${LOGP}/\${b}.err || true"

find "./$OUTPDBQT" -name "mol_*_3d.pdbqt" -size +0c | sort > pdbqt_success.list
echo "PDBQT success count: $(wc -l < pdbqt_success.list)"
echo "Phase B finished: $(date)"

# -----------------------
# Summary
# -----------------------
echo "=========================================="
echo "Job finished : $(date)"
echo "3D SDF dir   : $OUT3D"
echo "PDBQT dir    : $OUTPDBQT"
echo "3D logs      : $LOG3D"
echo "PDBQT logs   : $LOGP"
echo "3D success   : 3d_success.list"
echo "PDBQT success: pdbqt_success.list"
echo "=========================================="

