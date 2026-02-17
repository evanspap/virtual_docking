#!/usr/bin/env python3
"""
run_smiles_to_pdbqt_single_node.py

Summary:
Single-node, procedural (non-parallel) conversion of SMILES to PDBQT files.
Designed for small datasets or local development on a single processor.

Converts a plain SMILES list (one SMILES per line) into:
  (1) 3D SDF files via RDKit (ETKDGv3 + MMFF/UFF)
  (2) PDBQT files via Open Babel with Gasteiger partial charges

Requirements:
    - Python 3.x
    - RDKit installed in the Python environment
    - Open Babel command-line tool (obabel) accessible in system PATH   

Usage:
  python run_smiles_to_pdbqt_single_node.py <input.smi>

Example:
  python run_smiles_to_pdbqt_single_node.py small_compounds.smi

Input:
  - A .smi file where each line contains a SMILES string (no header).
  - Format options:
      (A) Single column (SMILES only):
          CC(C)Cc1ccc(cc1)C(C)C(=O)O
          CN1CCC[C@H]1c2cccnc2
          O=C(O)c1ccccc1
      (B) Two columns (SMILES + NAME, tab-separated):
          CC(C)Cc1ccc(cc1)C(C)C(=O)O    ibuprofen
          CN1CCC[C@H]1c2cccnc2          compound_A123
          O=C(O)c1ccccc1                aspirin
  - Expected behavior:
      * Each line is read as a SMILES string (and optional name).
      * Columns are separated by tab or whitespace.
      * Empty lines are skipped.
      * No header line expected (data starts on line 1).
      * If names are provided (column 2), they are used in output filenames.
      * If no names are provided, sequential index numbers are used.

Outputs:
  - SDF_Structures_3D/mol_<idx>_3d.sdf
  - PDBQT_OBABEL/mol_<idx>_3d.pdbqt
  - 3d_success.list
  - pdbqt_success.list

Output structure:
/path/to/
        ├── compounds.smi
        ├── SDF_Structures_3D/
        │   ├── compound_name_3d.sdf
        │   └── ...
        ├── PDBQT_OBABEL/
        │   ├── compound_name_3d.pdbqt
        │   └── ...
        ├── 3d_success.list
        └── pdbqt_success.list

Author: Evangelos Papadopoulos
Version: 1.0 (Python single-node variant)
Date: 2026-02-03
license: MIT

"""


import argparse
import logging
import os
import shlex
import subprocess
import sys
from datetime import datetime

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem
except Exception:
    Chem = None
    AllChem = None


def setup_logger(logfile_path=None, debug=False):
    logger = logging.getLogger("smiles2pdbqt")
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S")

    # stdout handler (INFO+)
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.DEBUG if debug else logging.INFO)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    # file handler (all debug info)
    if logfile_path:
        fh = logging.FileHandler(logfile_path)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger


def read_smiles_file(path):
    entries = []
    with open(path, "r", encoding="utf-8") as fh:
        for i, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            smi = parts[0]
            name = parts[1] if len(parts) > 1 else None
            entries.append((i, smi, name))
    return entries


def make_3d_from_smiles(idx, smi, out_sdf, name=None, logger=None):
    if logger is None:
        logger = logging.getLogger("smiles2pdbqt")
    if Chem is None or AllChem is None:
        logger.error("RDKit not available in this Python interpreter.")
        return False, "rdkit_missing"
    try:
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            return False, "rdkit_parse_failed"
        mol = Chem.AddHs(mol)

        params = AllChem.ETKDGv3()
        params.randomSeed = idx % 2147483647
        params.useRandomCoords = True

        if AllChem.EmbedMolecule(mol, params) != 0:
            return False, "embed_failed"

        try:
            if AllChem.MMFFHasAllMoleculeParams(mol):
                AllChem.MMFFOptimizeMolecule(mol, mmffVariant="MMFF94s", maxIters=2000)
            else:
                AllChem.UFFOptimizeMolecule(mol, maxIters=2000)
        except Exception as e:
            logger.debug("minimization exception: %s", e)
            return False, f"minimization_failed:{e}"

        mol.SetProp("_Name", name if name else f"mol_{idx}")
        mol.SetProp("SMILES", smi)

        w = Chem.SDWriter(out_sdf)
        w.write(mol)
        w.close()
        return True, None
    except Exception as e:
        logger.exception("Unexpected RDKit error for idx %s", idx)
        return False, f"exception:{e}"


def obabel_to_pdbqt(sdf_path, pdbqt_path, logger=None):
    if logger is None:
        logger = logging.getLogger("smiles2pdbqt")
    cmd = ["obabel", sdf_path, "-O", pdbqt_path, "--partialcharge", "gasteiger"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if proc.returncode != 0:
            logger.debug("obabel stdout: %s", proc.stdout)
            logger.debug("obabel stderr: %s", proc.stderr)
            return False, f"obabel_failed:{proc.returncode}:{proc.stderr.strip()}"
        return True, None
    except FileNotFoundError:
        return False, "obabel_not_found"
    except Exception as e:
        logger.exception("Unexpected obabel error")
        return False, f"exception:{e}"


def main():
    # If called without arguments, print the module docstring
    if len(sys.argv) == 1:
        print(__doc__)
        return

    p = argparse.ArgumentParser()
    p.add_argument("smifile", help="Input SMILES file (one SMILES per line, optional second column name)")
    p.add_argument("--debug", action="store_true", help="Write debug log file in input dir and verbose output")
    p.add_argument("--log", help="Path to write debug log (overrides default)")
    args = p.parse_args()

    smifile = args.smifile
    if not os.path.isfile(smifile):
        print(f"ERROR: input file not found: {smifile}", file=sys.stderr)
        sys.exit(10)

    smi_dir = os.path.abspath(os.path.dirname(smifile))
    smi_basename = os.path.basename(smifile)

    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    default_log = os.path.join(smi_dir, f"run_smiles_to_pdbqt.{timestamp}.debug.log") if args.debug else None
    logfile = args.log or default_log

    logger = setup_logger(logfile, debug=args.debug)

    logger.info("Starting SMILES -> PDBQT conversion")
    logger.info("Input file: %s", smifile)
    logger.info("Input dir: %s", smi_dir)

    OUT3D = os.path.join(smi_dir, "SDF_Structures_3D")
    OUTPDBQT = os.path.join(smi_dir, "PDBQT_OBABEL")
    os.makedirs(OUT3D, exist_ok=True)
    os.makedirs(OUTPDBQT, exist_ok=True)

    entries = read_smiles_file(smifile)
    total = len(entries)
    logger.info("SMILES entries: %d", total)

    # Phase A
    logger.info("Phase A: RDKit 3D generation started at %s", datetime.now().isoformat())
    success_3d = []
    fail_3d = []

    for idx, smi, name in entries:
        file_id = name if name else f"mol_{idx}"
        sdf_path = os.path.join(OUT3D, f"{file_id}_3d.sdf")
        logger.info("[%d/%d] Generating 3D SDF: %s", idx, total, file_id)
        ok, reason = make_3d_from_smiles(idx, smi, sdf_path, name=name, logger=logger)
        if ok:
            success_3d.append(sdf_path)
        else:
            fail_3d.append((idx, smi, file_id, reason))
            logger.warning("3D generation failed for %s: %s", file_id, reason)

    # write 3d_success.list
    success_3d_list = os.path.join(smi_dir, "3d_success.list")
    with open(success_3d_list, "w", encoding="utf-8") as fh:
        for pth in success_3d:
            fh.write(pth + "\n")

    logger.info("Phase A finished: %d succeeded, %d failed", len(success_3d), len(fail_3d))

    # Phase B
    logger.info("Phase B: Open Babel PDBQT generation started at %s", datetime.now().isoformat())
    success_pdbqt = []
    fail_pdbqt = []

    for i, sdf_path in enumerate(success_3d, start=1):
        basename = os.path.basename(sdf_path)
        base = os.path.splitext(basename)[0]
        pdbqt_path = os.path.join(OUTPDBQT, f"{base}.pdbqt")
        logger.info("[%d/%d] Converting to PDBQT: %s", i, len(success_3d), basename)
        ok, reason = obabel_to_pdbqt(sdf_path, pdbqt_path, logger=logger)
        if ok:
            success_pdbqt.append(pdbqt_path)
        else:
            fail_pdbqt.append((sdf_path, reason))
            logger.warning("PDBQT conversion failed for %s: %s", basename, reason)

    # write pdbqt_success.list
    pdbqt_success_list = os.path.join(smi_dir, "pdbqt_success.list")
    with open(pdbqt_success_list, "w", encoding="utf-8") as fh:
        for pth in success_pdbqt:
            fh.write(pth + "\n")

    # Summary
    logger.info("==========================================")
    logger.info("Job finished : %s", datetime.now().isoformat())
    logger.info("3D SDF dir   : %s", OUT3D)
    logger.info("PDBQT dir    : %s", OUTPDBQT)
    logger.info("3D success   : %s (%d files)", success_3d_list, len(success_3d))
    logger.info("PDBQT success: %s (%d files)", pdbqt_success_list, len(success_pdbqt))
    logger.info("3D failed    : %d", len(fail_3d))
    logger.info("PDBQT failed : %d", len(fail_pdbqt))
    logger.info("==========================================")

    # Also print concise summary to stdout
    print("==========================================")
    print(f"Job finished : {datetime.now().isoformat()}")
    print(f"3D SDF dir   : {OUT3D}")
    print(f"PDBQT dir    : {OUTPDBQT}")
    print(f"3D success   : {success_3d_list} ({len(success_3d)} files)")
    print(f"PDBQT success: {pdbqt_success_list} ({len(success_pdbqt)} files)")
    print(f"3D failed    : {len(fail_3d)}")
    print(f"PDBQT failed : {len(fail_pdbqt)}")
    print("==========================================")

    # exit code: 0 if all OK, 1 otherwise
    if len(fail_3d) == 0 and len(fail_pdbqt) == 0:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
