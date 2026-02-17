#!/usr/bin/env python3
# ==============================================================================
# Script Name: smiles_to_svg_batch.py
# Version:     1.4.0
# Date:        2026-02-12
# Author:      Evangelos Papadopoulos
#
# ==============================================================================
# DESCRIPTION
# ------------------------------------------------------------------------------
# Batch conversion of SMILES strings from a CSV file into 2D molecular images
# (SVG or PNG) using RDKit.
#
# Designed for:
#   - Computational drug discovery pipelines
#   - Docking hit visualization
#   - Manuscript figure preparation
#   - GitHub molecule galleries
#   - Large-scale compound libraries
#
# ==============================================================================
# SUPPORTED OUTPUT FORMATS
# ------------------------------------------------------------------------------
# 1. SVG (default)
#    - Vector graphics
#    - Publication quality
#    - Infinitely scalable
#    - Recommended for manuscripts, posters, GitHub gallery
#
# 2. PNG
#    - Raster format
#    - Suitable for PowerPoint, reports, email sharing
#    - Resolution controlled by --width and --height
#
# Default:
#    --format svg
#
# ==============================================================================
# FEATURES
# ------------------------------------------------------------------------------
# - SVG / PNG export
# - Optional molecule title (--add_title)
# - Optional label column (--label_col)
# - Automatic filename sanitization
# - Zero-padded indexing fallback
# - Logging of invalid SMILES
# - Parallel processing (--parallel N)
# - Grid image export (--grid N)
# - Verbose / Quiet modes
# - Full manual flag (--manual)
# - Version flag (--version)
#
# ==============================================================================
# LABEL BEHAVIOR
# ------------------------------------------------------------------------------
# --label_col <column_name>
#
# If provided:
#   - Value from this column is rendered as legend under molecule
#   - Applies to both individual images and grid image
#
# If not provided:
#   - No label is rendered (unless --add_title with --name_col)
#
# ==============================================================================
# CHANGELOG
# ------------------------------------------------------------------------------
# v1.0.0 - Initial batch SVG export
# v1.1.0 - Added PNG support
# v1.2.0 - Added parallel processing & grid export
# v1.3.0 - Unified full header preservation
# v1.3.1 - Proper CLI architecture
# v1.4.0 - Added --label_col for molecule labeling
# ==============================================================================

import os
import sys
import argparse
import pandas as pd
from multiprocessing import Pool, cpu_count
from rdkit import Chem
from rdkit.Chem import Draw

VERSION = "1.4.0"
SUPPORTED_FORMATS = ["svg", "png"]


# ------------------------------------------------------------------------------
# Utility Functions
# ------------------------------------------------------------------------------

def sanitize_filename(name):
    return "".join(c if c.isalnum() or c in "_-" else "_" for c in str(name))

def generate_filename(name, index, total_digits):
    if name:
        return sanitize_filename(name)
    return f"mol_{str(index).zfill(total_digits)}"

def render_task(args):
    row, idx, settings = args
    smiles = row.get(settings["smiles_col"])
    name = row.get(settings["name_col"])
    label = row.get(settings["label_col"]) if settings["label_col"] else None

    if pd.isna(smiles):
        return ("invalid", idx, smiles)

    mol = Chem.MolFromSmiles(str(smiles))
    if mol is None:
        return ("invalid", idx, smiles)

    Chem.rdDepictor.Compute2DCoords(mol)

    filename = generate_filename(name, idx, settings["digits"])
    outpath = os.path.join(settings["outdir"], f"{filename}.{settings['format']}")

    legend_text = None
    if settings["label_col"] and label is not None:
        legend_text = str(label)
    elif settings["add_title"] and name:
        legend_text = str(name)

    try:
        if settings["format"] == "svg":
            drawer = Draw.MolDraw2DSVG(settings["width"], settings["height"])
            drawer.DrawMolecule(mol, legend=legend_text)
            drawer.FinishDrawing()
            with open(outpath, "w") as f:
                f.write(drawer.GetDrawingText())
        else:
            img = Draw.MolToImage(
                mol,
                size=(settings["width"], settings["height"]),
                legend=legend_text
            )
            img.save(outpath)

        return ("success", idx, None)

    except Exception as e:
        return ("error", idx, str(e))


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

def main():

    parser = argparse.ArgumentParser(
        description="Batch convert SMILES in CSV to SVG/PNG images using RDKit."
    )

    parser.add_argument("csv_file", nargs="?", help="Input CSV file")
    parser.add_argument("--smiles_col", default="canonical_smiles")
    parser.add_argument("--name_col", default=None)
    parser.add_argument("--label_col", default=None,
                        help="Column to use as label under molecule")
    parser.add_argument("--outdir", default="images")
    parser.add_argument("--format", choices=SUPPORTED_FORMATS, default="svg")
    parser.add_argument("--width", type=int, default=400)
    parser.add_argument("--height", type=int, default=400)
    parser.add_argument("--add_title", action="store_true")
    parser.add_argument("--parallel", type=int, default=1)
    parser.add_argument("--grid", type=int)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--version", action="store_true",
                        help="Print script version and exit")
    parser.add_argument("--manual", action="store_true",
                        help="Print full header documentation and exit")

    args = parser.parse_args()

    if args.version:
        print(f"smiles_to_svg_batch.py version {VERSION}")
        sys.exit(0)

    if args.manual:
        with open(__file__, "r") as f:
            header_lines = []
            for line in f:
                if line.strip().startswith("import"):
                    break
                header_lines.append(line)
        print("".join(header_lines))
        sys.exit(0)

    if not args.csv_file:
        parser.print_help()
        sys.exit(1)

    if not os.path.exists(args.csv_file):
        print(f"ERROR: File not found: {args.csv_file}")
        sys.exit(1)

    df = pd.read_csv(args.csv_file)

    os.makedirs(args.outdir, exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    total = len(df)
    digits = len(str(total))

    settings = {
        "smiles_col": args.smiles_col,
        "name_col": args.name_col,
        "label_col": args.label_col,
        "outdir": args.outdir,
        "format": args.format,
        "width": args.width,
        "height": args.height,
        "add_title": args.add_title,
        "digits": digits
    }

    tasks = [(row, idx, settings) for idx, row in df.iterrows()]

    if args.parallel > 1:
        with Pool(min(args.parallel, cpu_count())) as pool:
            results = pool.map(render_task, tasks)
    else:
        results = list(map(render_task, tasks))

    success = sum(1 for r in results if r[0] == "success")
    failed = total - success

    with open("logs/smiles_errors.log", "w") as log:
        for r in results:
            if r[0] != "success":
                log.write(f"Row {r[1]}: {r[0]} -> {r[2]}\n")

    if not args.quiet:
        print("\nConversion Completed")
        print("=" * 40)
        print(f"Total molecules: {total}")
        print(f"Successfully rendered: {success}")
        print(f"Failed: {failed}")
        print("=" * 40)

    # Grid export
    if args.grid:
        mols = []
        legends = []
        for _, row in df.iterrows():
            mol = Chem.MolFromSmiles(str(row.get(args.smiles_col)))
            if mol:
                mols.append(mol)
                if args.label_col:
                    legends.append(str(row.get(args.label_col)))
                elif args.add_title and args.name_col:
                    legends.append(str(row.get(args.name_col)))
                else:
                    legends.append("")

        img = Draw.MolsToGridImage(
            mols,
            molsPerRow=args.grid,
            subImgSize=(args.width, args.height),
            legends=legends
        )
        img.save(os.path.join(args.outdir, "grid.png"))


if __name__ == "__main__":
    main()
