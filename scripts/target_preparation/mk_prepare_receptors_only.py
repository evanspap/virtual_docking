#!/usr/bin/env python3
"""
===============================================================================
Script Name : mk_prepare_receptors_only.py
Author      : Evangelos Papadopoulos
Date        : 2026-02-23
Version     : 1.0
===============================================================================

DESCRIPTION
-----------
Run only the Meeko receptor preparation step (mk_prepare_receptor.py) to
generate PDBQT receptor files from input PDB files (typically *_reduce.pdb).

This is useful when Reduce has already been run successfully and you want to:
  - rerun only the PDBQT generation step
  - debug Meeko failures separately
  - resume batch processing with skip-existing

USAGE
-----
Single file:
    python mk_prepare_receptors_only.py input_reduce.pdb

Directory:
    python mk_prepare_receptors_only.py ./reduce_pdb_dir

Directory with filter:
    python mk_prepare_receptors_only.py ./reduce_pdb_dir --pattern "*_reduce.pdb"

Batch altloc handling:
    python mk_prepare_receptors_only.py ./reduce_pdb_dir --default-altloc A
===============================================================================
"""

import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime


VERSION = "1.0"


def run_command(cmd, dry_run=False):
    print(f"\n[CMD] {' '.join(cmd)}")
    if dry_run:
        return True
    result = subprocess.run(cmd)
    return result.returncode == 0


def validate_file(path):
    return path.exists() and path.stat().st_size > 0


def infer_output_stem(input_pdb: Path) -> str:
    # Convert "..._reduce.pdb" -> "..."
    stem = input_pdb.stem
    if stem.endswith("_reduce"):
        return stem[:-7]
    return stem


def process_pdb(pdb_path, outdir, dry_run=False, default_altloc=None, skip_existing=False):
    pdb_path = Path(pdb_path)
    outdir = Path(outdir)
    out_stem = infer_output_stem(pdb_path)
    pdbqt_base = outdir / out_stem
    pdbqt_file = outdir / f"{out_stem}.pdbqt"

    print(f"\n===================================================")
    print(f"Processing: {pdb_path}")
    print(f"Timestamp : {datetime.now()}")
    print(f"Output    : {pdbqt_file}")
    print(f"===================================================")

    if skip_existing and pdbqt_file.exists() and pdbqt_file.stat().st_size > 0:
        print(f"[SKIP] PDBQT already exists: {pdbqt_file}")
        return True

    meeko_cmd = [
        "mk_prepare_receptor.py",
        "--read_pdb", str(pdb_path),
        "--allow_bad_res",
        "-o", str(pdbqt_base),
        "-p",
    ]
    if default_altloc:
        meeko_cmd.extend(["--default_altloc", str(default_altloc)])

    success = run_command(meeko_cmd, dry_run)
    if not success:
        print("ERROR: mk_prepare_receptor failed.")
        return False

    if not dry_run and not validate_file(pdbqt_file):
        print("ERROR: PDBQT not created or empty.")
        return False

    print("✔ PDBQT successfully created.")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Run Meeko mk_prepare_receptor.py only (PDB -> PDBQT).",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("input", nargs="?", help="Input PDB file or directory.")
    parser.add_argument(
        "-o", "--outdir",
        default="./pdbqt",
        help="Output directory for PDBQT files (default: ./pdbqt)",
    )
    parser.add_argument(
        "--pattern",
        default="*.pdb",
        help="Glob pattern when input is directory (default: *.pdb)",
    )
    parser.add_argument(
        "--default-altloc",
        default=None,
        help="Default alternate location identifier for Meeko (e.g., A).",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip entries if final .pdbqt already exists.",
    )
    parser.add_argument(
        "-n", "--dry-run",
        action="store_true",
        help="Print commands without executing.",
    )
    args = parser.parse_args()

    if not args.input:
        parser.print_help()
        sys.exit(1)

    input_path = Path(args.input)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    if input_path.is_file():
        pdb_files = [input_path]
    elif input_path.is_dir():
        pdb_files = list(input_path.glob(args.pattern))
        if not pdb_files:
            print("No PDB files found with pattern:", args.pattern)
            sys.exit(1)
    else:
        print("Invalid input path.")
        sys.exit(1)

    pdb_files = sorted(pdb_files)
    print(f"\nFound {len(pdb_files)} PDB file(s).")

    failures = 0
    for i, pdb in enumerate(pdb_files, start=1):
        pct = (i / len(pdb_files)) * 100.0
        print(f"[{i}/{len(pdb_files)} | {pct:.1f}%] {pdb.name}")
        ok = process_pdb(
            pdb,
            outdir,
            dry_run=args.dry_run,
            default_altloc=args.default_altloc,
            skip_existing=args.skip_existing,
        )
        if not ok:
            failures += 1

    print("\n===================================================")
    print(f"Finished. Success: {len(pdb_files)-failures} | Failed: {failures}")
    print("===================================================\n")


if __name__ == "__main__":
    main()
