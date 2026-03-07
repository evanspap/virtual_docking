#!/usr/bin/env python3
"""
Generate AutoDock Vina docking commands with timestamps and separate error logs.

Author: Evangelos Papadopoulos
Version: 1.3
Control: Internal
Date: 2025-09-15

This script reads a parameter file containing at least:
    indir = <input_directory>
    outdir = <output_directory>
    trg = <target_tag>
    cfg = <config_file>

Optional:
    exhaustiveness = <int>
    num_modes = <int>

It scans all *.pdbqt files in indir, checks whether the corresponding
output file (<outdir>/<basename>_<trg>.pdbqt) already exists, and for each
missing output, prints the Vina command to stdout redirected to an output log file.

Changes from v1.2:
- Accepts `exhaustiveness` and `num_modes` from the param file.
- Adds them to the Vina command if provided.

Usage:
    python vina_commands.py <param_file>

Example:
    python vina_commands.py /path/to/param_file
"""

import sys
import os

def print_usage():
    print(__doc__)
    sys.exit(1)

def parse_params(param_path):
    params = {}
    with open(param_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            key, val = map(str.strip, line.split('=', 1))
            if val and (val[0] == val[-1]) and val.startswith(("'", '"')):
                val = val[1:-1]
            params[key] = val
    return params

def main():
    if len(sys.argv) != 2:
        print_usage()

    param_file = sys.argv[1]

    if not os.path.isfile(param_file):
        print(f"ERROR: param_file '{param_file}' not found.")
        sys.exit(1)

    params = parse_params(param_file)
    try:
        indir = params['indir']
        outdir = params['outdir']
        trg = params['trg']
        cfg = params['cfg']
    except KeyError as e:
        print(f"ERROR: missing parameter '{e.args[0]}' in param_file.")
        sys.exit(1)

    exhaustiveness = params.get('exhaustiveness')
    num_modes = params.get('num_modes')

    for name, path in [('input directory', indir), ('output directory', outdir)]:
        if not os.path.isdir(path):
            print(f"ERROR: {name} '{path}' not found.")
            sys.exit(1)
    if not os.path.isfile(cfg):
        print(f"ERROR: config file '{cfg}' not found.")
        sys.exit(1)

    for ligand in sorted(os.listdir(indir)):
        if not ligand.endswith('.pdbqt'):
            continue
        lig_path = os.path.join(indir, ligand)
        base = os.path.splitext(ligand)[0]
        out_path = os.path.join(outdir, f"{base}_{trg}.pdbqt")
        out_redirect = os.path.join(outdir, f"{base}_{trg}.out")
        err_redirect = os.path.join(outdir, f"{base}_{trg}.err")
        if os.path.exists(out_path):
            continue

        # Build vina options
        vina_opts = f"--config \"{cfg}\" --ligand \"{lig_path}\" --out \"{out_path}\" --cpu 1 --spacing 0.1"
        if exhaustiveness:
            vina_opts += f" --exhaustiveness {exhaustiveness}"
        if num_modes:
            vina_opts += f" --num_modes {num_modes}"

        cmd = (
            f"echo \"Start: $(date)\" >> \"{out_redirect}\" && "
            f"vina {vina_opts} >> \"{out_redirect}\" 2>\"{err_redirect}\" && "
            f"echo \"End: $(date)\" >> \"{out_redirect}\""
        )
        print(cmd)

if __name__ == '__main__':
    main()

