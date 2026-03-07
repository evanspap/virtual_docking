#!/usr/bin/env python3
"""
Generate AutoDock Vina docking commands from a parameter file.

Author: Evangelos Papadopoulos
Version: 1.5
Control: Internal
Date: 2026-03-07

Changes:
- v1.5: Create .conf.run lazily per config used; added --test to limit printed commands; log changes in header.
- v1.4: Added outdir/pdbqt and outdir/out; create .conf.run with absolute receptor path.

Required parameters in the file:
    compound   = <pdbqt file or directory>
    target_cfg = <conf/cfg file or directory>
    outdir     = <output directory>

Optional:
    exhaustiveness = <int>
    num_modes      = <int>

Behavior:
- If paths are relative, they are resolved relative to the parameter file location.
- If compound is a directory, all *.pdbqt files in that directory are used (non-recursive).
- If target_cfg is a directory, all *.conf/*.cfg files in that directory are used (non-recursive).
- For each compound/target_cfg combination, a Vina command is printed to stdout.
- Output names are derived from the compound filename and target_cfg basename.
- Output files are organized under outdir/pdbqt and outdir/out.
- Configs are copied to *.conf.run/*.cfg.run with absolute receptor paths.

Usage:
    python vina_commands_v1.4.py <param_file> [--test N]
"""

import os
import sys
import re
import argparse

PDBQT_EXT = ".pdbqt"
CFG_EXTS = {".conf", ".cfg"}


def build_arg_parser():
    parser = argparse.ArgumentParser(
        description="Generate AutoDock Vina commands from a parameter file."
    )
    parser.add_argument("param_file", help="Path to parameter file")
    parser.add_argument(
        "--test",
        type=int,
        default=None,
        help="Limit number of commands printed (e.g., --test 2)",
    )
    return parser


def parse_params(param_path):
    params = {}
    with open(param_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, val = map(str.strip, line.split("=", 1))
            if val and (val[0] == val[-1]) and val.startswith(("'", '"')):
                val = val[1:-1]
            params[key] = val
    return params


def resolve_path(path, base_dir):
    if os.path.isabs(path):
        return path
    return os.path.normpath(os.path.join(base_dir, path))


def collect_compounds(compound_path):
    if os.path.isfile(compound_path):
        if not compound_path.lower().endswith(PDBQT_EXT):
            raise ValueError(f"compound file '{compound_path}' is not {PDBQT_EXT}")
        return [compound_path], os.path.dirname(compound_path), True
    if os.path.isdir(compound_path):
        compounds = []
        for name in os.listdir(compound_path):
            path = os.path.join(compound_path, name)
            if not os.path.isfile(path):
                continue
            if name.lower().endswith(PDBQT_EXT):
                compounds.append(path)
        if not compounds:
            raise ValueError(f"no {PDBQT_EXT} files found in '{compound_path}'")
        return sorted(compounds), compound_path, False
    raise ValueError(f"compound path '{compound_path}' not found")


def collect_targets(target_cfg_path):
    if os.path.isfile(target_cfg_path):
        return [target_cfg_path], True
    if os.path.isdir(target_cfg_path):
        targets = []
        for name in os.listdir(target_cfg_path):
            path = os.path.join(target_cfg_path, name)
            if not os.path.isfile(path):
                continue
            ext = os.path.splitext(name)[1].lower()
            if ext in CFG_EXTS:
                targets.append(path)
        if not targets:
            raise ValueError(f"no config files ({', '.join(sorted(CFG_EXTS))}) found in '{target_cfg_path}'")
        return sorted(targets), False
    raise ValueError(f"target_cfg path '{target_cfg_path}' not found")


def prepare_conf_run(cfg_path):
    cfg_dir = os.path.dirname(cfg_path)
    run_path = cfg_path + ".run"
    with open(cfg_path, "r") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        m = re.match(r"^(\s*receptor\s*=\s*)(.+?)\s*$", line)
        if not m:
            new_lines.append(line)
            continue
        prefix, val = m.group(1), m.group(2)
        val = val.strip().strip('"').strip("'")
        if os.path.isabs(val):
            new_val = val
        else:
            new_val = os.path.normpath(os.path.join(cfg_dir, val))
        new_lines.append(f"{prefix}{new_val}\n")

    with open(run_path, "w") as f:
        f.writelines(new_lines)

    return run_path


def compound_tag(compound_path, compound_root, single_compound):
    base = os.path.splitext(os.path.basename(compound_path))[0]
    if single_compound:
        return base
    rel = os.path.relpath(compound_path, compound_root)
    rel_no_ext = os.path.splitext(rel)[0]
    safe = rel_no_ext.replace(os.sep, "__")
    return safe


def main():
    parser = build_arg_parser()
    args = parser.parse_args()

    param_file = args.param_file
    test_limit = args.test if args.test and args.test > 0 else None

    if not os.path.isfile(param_file):
        print(f"ERROR: param_file '{param_file}' not found.")
        sys.exit(1)

    params = parse_params(param_file)
    if "target_cfg" in params:
        target_cfg_key = "target_cfg"
    elif "cfg" in params:
        target_cfg_key = "cfg"
    else:
        target_cfg_key = None

    missing = [k for k in ("compound", "outdir") if k not in params]
    if not target_cfg_key:
        missing.append("target_cfg")
    if missing:
        print(f"ERROR: missing parameter(s) {', '.join(missing)} in param_file.")
        sys.exit(1)

    base_dir = os.path.dirname(os.path.abspath(param_file))
    compound_path = resolve_path(params["compound"], base_dir)
    target_cfg_path = resolve_path(params[target_cfg_key], base_dir)
    outdir = resolve_path(params["outdir"], base_dir)

    exhaustiveness = params.get("exhaustiveness")
    num_modes = params.get("num_modes")

    if not os.path.isdir(outdir):
        print(f"ERROR: output directory '{outdir}' not found.")
        sys.exit(1)

    pdbqt_dir = os.path.join(outdir, "pdbqt")
    outlog_dir = os.path.join(outdir, "out")
    os.makedirs(pdbqt_dir, exist_ok=True)
    os.makedirs(outlog_dir, exist_ok=True)

    try:
        compounds, compound_root, single_compound = collect_compounds(compound_path)
        targets, _single_target = collect_targets(target_cfg_path)
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    conf_run_map = {}

    def get_conf_run(path):
        if path not in conf_run_map:
            conf_run_map[path] = prepare_conf_run(path)
        return conf_run_map[path]

    printed = 0
    for lig_path in compounds:
        lig_tag = compound_tag(lig_path, compound_root, single_compound)
        for cfg_path in targets:
            trg = os.path.splitext(os.path.basename(cfg_path))[0]
            out_path = os.path.join(pdbqt_dir, f"{lig_tag}_{trg}.pdbqt")
            out_redirect = os.path.join(outlog_dir, f"{lig_tag}_{trg}.out")
            err_redirect = os.path.join(outlog_dir, f"{lig_tag}_{trg}.err")
            if os.path.exists(out_path):
                continue

            conf_run = get_conf_run(cfg_path)
            vina_opts = f"--config \"{conf_run}\" --ligand \"{lig_path}\" --out \"{out_path}\" --cpu 1 --spacing 0.1"
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
            printed += 1
            if test_limit and printed >= test_limit:
                return


if __name__ == "__main__":
    main()
