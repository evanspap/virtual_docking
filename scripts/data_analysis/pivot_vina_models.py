#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# =============================================================================
# Script: pivot_vina_models.py
# Purpose:
#   Read a Vina result table in long format and convert it to wide format so
#   each ligand appears only once, with one block of columns per MODEL.
#
# Expected input columns:
#   LIGAND, MODEL, VINA_SCORE, RMSD_LB, RMSD_UB, INTER_PLUS_INTRA,
#   INTER, INTRA, UNBOUND
#
# Input notes:
#   The script accepts comma-separated, tab-separated, semicolon-separated,
#   or whitespace-delimited files.
#   Headered and headerless inputs are both supported.
#
# Output:
#   A delimited text file where each ligand is a single row and each model is
#   expanded into columns such as:
#   LIGAND, MODEL_1, VINA_SCORE_1, ..., UNBOUND_1, MODEL_2, VINA_SCORE_2, ...
#
# Author: Evangelos Papadopoulos
# Version: 1.0
# Date: 2026-03-24
#
# Usage:
#   python pivot_vina_models.py -i input.lst -o output_wide.csv
#
# Examples:
#   python pivot_vina_models.py -i pdbqt_20260320_vina.lst
#   python pivot_vina_models.py -i pdbqt_20260320_vina.lst -o pdbqt_20260320_vina_wide.csv
#   python pivot_vina_models.py -i results.csv --input-delimiter comma --output-delimiter tab
#
# Help:
#   python pivot_vina_models.py --help
# =============================================================================

from __future__ import annotations

import argparse
import csv
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Iterable


DEFAULT_COLUMNS = [
    "LIGAND",
    "MODEL",
    "VINA_SCORE",
    "RMSD_LB",
    "RMSD_UB",
    "INTER_PLUS_INTRA",
    "INTER",
    "INTRA",
    "UNBOUND",
]

VALUE_COLUMNS = [column for column in DEFAULT_COLUMNS if column != "LIGAND"]
DELIMITER_MAP = {
    "comma": ",",
    "tab": "\t",
    "semicolon": ";",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Convert long-format AutoDock Vina results into a wide table with "
            "one row per ligand and one block of columns per model."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Path to the input Vina list/table file.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help=(
            "Path to the output file. If omitted, a sibling file ending with "
            "'_wide.csv' is created."
        ),
    )
    parser.add_argument(
        "--input-delimiter",
        choices=["auto", "comma", "tab", "semicolon", "whitespace"],
        default="auto",
        help="Delimiter used in the input file.",
    )
    parser.add_argument(
        "--output-delimiter",
        choices=["comma", "tab", "semicolon"],
        default="comma",
        help="Delimiter used in the output file.",
    )
    parser.add_argument(
        "--no-header",
        action="store_true",
        help="Treat the input file as headerless even if the first row looks like a header.",
    )
    parser.add_argument(
        "--max-models",
        type=int,
        default=None,
        help="Limit the output to models up to this number.",
    )
    return parser


def sniff_delimiter(sample: str, requested: str) -> str | None:
    if requested != "auto":
        if requested == "whitespace":
            return None
        return DELIMITER_MAP[requested]

    counts = {
        ",": sample.count(","),
        "\t": sample.count("\t"),
        ";": sample.count(";"),
    }
    best_delimiter, best_count = max(counts.items(), key=lambda item: item[1])
    if best_count > 0:
        return best_delimiter
    return None


def normalize_header(tokens: Iterable[str]) -> list[str]:
    return [token.strip().upper() for token in tokens]


def looks_like_header(row: list[str]) -> bool:
    normalized = normalize_header(row)
    return len(normalized) >= 2 and normalized[0] == "LIGAND" and normalized[1] == "MODEL"


def split_line(line: str, delimiter: str | None) -> list[str]:
    stripped = line.strip()
    if not stripped:
        return []
    if delimiter is None:
        return stripped.split()
    return next(csv.reader([stripped], delimiter=delimiter))


def read_rows(path: Path, delimiter: str | None, force_no_header: bool) -> tuple[list[str], list[list[str]]]:
    rows: list[list[str]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for raw_line in handle:
            parsed = split_line(raw_line, delimiter)
            if parsed:
                rows.append([field.strip() for field in parsed])

    if not rows:
        raise ValueError(f"Input file is empty: {path}")

    first_row = rows[0]
    if force_no_header:
        return DEFAULT_COLUMNS, rows

    if looks_like_header(first_row):
        return normalize_header(first_row), rows[1:]

    return DEFAULT_COLUMNS, rows


def coerce_model_key(value: str) -> tuple[int, str]:
    text = value.strip()
    try:
        return (0, f"{int(text):09d}")
    except ValueError:
        return (1, text)


def pivot_rows(header: list[str], rows: list[list[str]], max_models: int | None) -> tuple[list[str], list[list[str]]]:
    if len(header) < len(DEFAULT_COLUMNS):
        raise ValueError(
            "Input must contain at least these columns: "
            + ", ".join(DEFAULT_COLUMNS)
        )

    header_index = {name: idx for idx, name in enumerate(header)}
    missing = [name for name in DEFAULT_COLUMNS if name not in header_index]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    ligands: OrderedDict[str, dict[str, dict[str, str]]] = OrderedDict()
    seen_models: set[str] = set()

    for row_number, row in enumerate(rows, start=2):
        if len(row) < len(header):
            row = row + [""] * (len(header) - len(row))

        ligand = row[header_index["LIGAND"]].strip()
        model = row[header_index["MODEL"]].strip()

        if not ligand:
            raise ValueError(f"Row {row_number}: empty LIGAND value.")
        if not model:
            raise ValueError(f"Row {row_number}: empty MODEL value.")

        if max_models is not None:
            try:
                if int(model) > max_models:
                    continue
            except ValueError:
                pass

        ligand_bucket = ligands.setdefault(ligand, OrderedDict())
        model_bucket = ligand_bucket.setdefault(model, {})

        for column in VALUE_COLUMNS:
            model_bucket[column] = row[header_index[column]].strip()

        seen_models.add(model)

    sorted_models = sorted(seen_models, key=coerce_model_key)

    output_header = ["LIGAND"]
    for model in sorted_models:
        for column in VALUE_COLUMNS:
            output_header.append(f"{column}_{model}")

    output_rows: list[list[str]] = []
    for ligand, model_map in ligands.items():
        output_row = [ligand]
        for model in sorted_models:
            values = model_map.get(model, {})
            for column in VALUE_COLUMNS:
                output_row.append(values.get(column, ""))
        output_rows.append(output_row)

    return output_header, output_rows


def default_output_path(input_path: Path) -> Path:
    return input_path.with_name(f"{input_path.stem}_wide.csv")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.is_file():
        parser.error(f"Input file not found: {input_path}")

    with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
        sample = handle.read(4096)

    delimiter = sniff_delimiter(sample, args.input_delimiter)
    header, rows = read_rows(input_path, delimiter, args.no_header)
    output_header, output_rows = pivot_rows(header, rows, args.max_models)

    output_path = Path(args.output) if args.output else default_output_path(input_path)
    output_delimiter = DELIMITER_MAP[args.output_delimiter]

    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter=output_delimiter)
        writer.writerow(output_header)
        writer.writerows(output_rows)

    print(f"[OK] Wrote {len(output_rows)} ligands to: {output_path}")
    if len(output_header) > 1:
        preview = ", ".join(output_header[1:1 + min(8, len(output_header) - 1)])
        print(f"[OK] Example output columns: {preview}")
    else:
        print("[OK] No model columns written.")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(1)
