#!/usr/bin/env python3
"""
===============================================================================
Script Name : prepare_receptors.py
Author      : Evangelos Papadopoulos
Date        : 2026-02-23
Version     : 2.0
===============================================================================

DESCRIPTION
-----------
End-to-end preparation pipeline for AutoDock Vina receptors.

For each input PDB:
    1. Run Reduce (-Build) to add polar hydrogens
    2. Run mk_prepare_receptor.py (Meeko) to generate PDBQT
    3. Validate output files

Supports:
    - Single PDB file
    - Directory input
    - Optional glob filtering
    - Dry run mode
    - Manual display

-------------------------------------------------------------------------------

USAGE
-----
Single file:
    python prepare_receptors.py input.pdb

Directory:
    python prepare_receptors.py ./pdb_directory

Directory with filter:
    python prepare_receptors.py ./pdb_directory --pattern "*_b_filter.pdb"

Dry run:
    python prepare_receptors.py ./pdb_directory -n

Custom output directory:
    python prepare_receptors.py ./pdb_directory -o ./pdbqt

Manual:
    python prepare_receptors.py --manual
===============================================================================
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime


VERSION = "2.0"


# =============================================================================
# Utility Functions
# =============================================================================

def run_command(cmd, dry_run=False):
    print(f"\n[CMD] {' '.join(cmd)}")
    if dry_run:
        return True

    result = subprocess.run(cmd)
    return result.returncode == 0


def validate_file(path):
    if not path.exists():
        return False
    if path.stat().st_size == 0:
        return False
    return True


# =============================================================================
# Main Pipeline
# =============================================================================

def process_pdb(pdb_path, outdir, dry_run=False):

    pdb_path = Path(pdb_path)
    base = pdb_path.stem

    reduce_out = pdb_path.parent / f"{base}_reduce.pdb"
    pdbqt_base = Path(outdir) / base

    print(f"\n===================================================")
    print(f"Processing: {pdb_path}")
    print(f"Timestamp : {datetime.now()}")
    print(f"===================================================")

    # Step 1 — Reduce
    reduce_cmd = ["reduce", "-BUILD", str(pdb_path)]
    if not dry_run:
        with open(reduce_out, "w") as f:
            result = subprocess.run(reduce_cmd, stdout=f)
        success = result.returncode == 0
    else:
        print(f"[DRY RUN] reduce -BUILD {pdb_path} > {reduce_out}")
        success = True

    if not success:
        print("ERROR: Reduce failed.")
        return False

    if not dry_run and not validate_file(reduce_out):
        print("ERROR: Reduce output invalid.")
        return False

    print("✔ Reduce successful.")

    # Step 2 — Meeko
    meeko_cmd = [
        "mk_prepare_receptor.py",
        "--read_pdb", str(reduce_out),
        "--allow_bad_res",
        "-o", str(pdbqt_base),
        "-p"
    ]

    success = run_command(meeko_cmd, dry_run)

    if not success:
        print("ERROR: mk_prepare_receptor failed.")
        return False

    pdbqt_file = Path(f"{pdbqt_base}.pdbqt")

    if not dry_run and not validate_file(pdbqt_file):
        print("ERROR: PDBQT not created or empty.")
        return False

    print("✔ PDBQT successfully created.")
    return True


# =============================================================================
# CLI
# =============================================================================

def main():

    parser = argparse.ArgumentParser(
        description="End-to-end Reduce + Meeko receptor preparation pipeline.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "input",
        nargs="?",
        help="Input PDB file or directory."
    )

    parser.add_argument(
        "-o", "--outdir",
        default="./pdbqt",
        help="Output directory for PDBQT files (default: ./pdbqt)"
    )

    parser.add_argument(
        "--pattern",
        default="*.pdb",
        help="Glob pattern when input is directory (default: *.pdb)"
    )

    parser.add_argument(
        "-n", "--dry-run",
        action="store_true",
        help="Print commands without executing."
    )

    parser.add_argument(
        "--manual",
        action="store_true",
        help="Show full manual."
    )

    args = parser.parse_args()

    if args.manual:
        print(__doc__)
        sys.exit(0)

    if not args.input:
        parser.print_help()
        sys.exit(1)

    input_path = Path(args.input)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    pdb_files = []

    if input_path.is_file():
        pdb_files.append(input_path)

    elif input_path.is_dir():
        pdb_files = list(input_path.glob(args.pattern))
        if not pdb_files:
            print("No PDB files found with pattern:", args.pattern)
            sys.exit(1)
    else:
        print("Invalid input path.")
        sys.exit(1)

    print(f"\nFound {len(pdb_files)} PDB file(s).")

    failures = 0

    for pdb in pdb_files:
        ok = process_pdb(pdb, outdir, args.dry_run)
        if not ok:
            failures += 1

    print("\n===================================================")
    print(f"Finished. Success: {len(pdb_files)-failures} | Failed: {failures}")
    print("===================================================\n")


if __name__ == "__main__":
    main()