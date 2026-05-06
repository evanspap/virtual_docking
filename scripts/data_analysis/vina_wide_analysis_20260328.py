#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# =============================================================================
# Script: vina_wide_analysis_20260328.py
# Purpose:
#   Read a wide-format Vina table (one row per ligand, one block of columns per
#   model) and append summary statistics as a separate analysis output.
#
# Expected input columns:
#   LIGAND, MODEL_1, VINA_SCORE_1, ..., INTER_PLUS_INTRA_1, INTER_1, INTRA_1,
#   ... repeated for additional model suffixes.
#
# Output:
#   A new CSV file preserving the original wide columns and appending:
#   VINA_SCORE_MEAN_TOP3, VINA_SCORE_SD_TOP3, VINA_SCORE_MEAN_ALL,
#   VINA_SCORE_SD_ALL, and the same for INTER_PLUS_INTRA, INTER, INTRA.
#
# Notes:
#   TOP3 uses the first three available model values in numeric model order.
#   ALL uses all available model values present in each row.
#   Standard deviation is population SD.
#
# Author: Evangelos Papadopoulos
# Version: 1.1
# Date: 2026-03-28
# =============================================================================

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from statistics import pstdev


SUMMARY_COLUMNS = [
    "VINA_SCORE",
    "INTER_PLUS_INTRA",
    "INTER",
    "INTRA",
]
SUMMARY_GROUPS = [
    ("TOP3", 3),
    ("ALL", None),
]
DELIMITER_MAP = {
    "comma": ",",
    "tab": "\t",
    "semicolon": ";",
}
MODEL_COLUMN_RE = re.compile(r"^(?P<name>[A-Z0-9_]+)_(?P<model>\d+)$")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Append Vina mean and standard deviation summary columns to a wide-format table."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-i", "--input", required=True, help="Path to the input wide CSV file.")
    parser.add_argument(
        "-o",
        "--output",
        help="Path to the output analysis CSV. If omitted, a sibling '_analysis_20260328.csv' file is created.",
    )
    parser.add_argument(
        "--input-delimiter",
        choices=["auto", "comma", "tab", "semicolon"],
        default="auto",
        help="Delimiter used in the input file.",
    )
    parser.add_argument(
        "--output-delimiter",
        choices=["comma", "tab", "semicolon"],
        default="comma",
        help="Delimiter used in the output file.",
    )
    return parser


def sniff_delimiter(sample: str, requested: str) -> str:
    if requested != "auto":
        return DELIMITER_MAP[requested]

    counts = {
        ",": sample.count(","),
        "\t": sample.count("\t"),
        ";": sample.count(";"),
    }
    best_delimiter, best_count = max(counts.items(), key=lambda item: item[1])
    return best_delimiter if best_count > 0 else ","


def parse_float(value: str) -> float | None:
    text = value.strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def format_float(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.6f}"


def summarize_values(values: list[float]) -> tuple[float | None, float | None]:
    if not values:
        return (None, None)
    mean_value = sum(values) / len(values)
    sd_value = 0.0 if len(values) == 1 else pstdev(values)
    return (mean_value, sd_value)


def detect_models(fieldnames: list[str], metric: str) -> list[int]:
    models: list[int] = []
    for fieldname in fieldnames:
        match = MODEL_COLUMN_RE.match(fieldname)
        if not match:
            continue
        if match.group("name") != metric:
            continue
        models.append(int(match.group("model")))
    return sorted(set(models))


def build_summary_fieldnames() -> list[str]:
    fieldnames: list[str] = []
    for metric in SUMMARY_COLUMNS:
        for group_name, _ in SUMMARY_GROUPS:
            fieldnames.append(f"{metric}_MEAN_{group_name}")
            fieldnames.append(f"{metric}_SD_{group_name}")
    return fieldnames


def default_output_path(input_path: Path) -> Path:
    return input_path.with_name(f"{input_path.stem}_analysis_20260328.csv")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.is_file():
        parser.error(f"Input file not found: {input_path}")

    with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
        sample = handle.read(4096)

    input_delimiter = sniff_delimiter(sample, args.input_delimiter)
    output_delimiter = DELIMITER_MAP[args.output_delimiter]

    with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=input_delimiter)
        if not reader.fieldnames:
            raise ValueError("Input file has no header.")

        fieldnames = list(reader.fieldnames)
        metric_models = {metric: detect_models(fieldnames, metric) for metric in SUMMARY_COLUMNS}
        summary_fieldnames = build_summary_fieldnames()

        output_fieldnames = list(fieldnames)
        for fieldname in summary_fieldnames:
            if fieldname not in output_fieldnames:
                output_fieldnames.append(fieldname)

        output_rows: list[dict[str, str]] = []
        for row in reader:
            output_row = dict(row)
            for metric in SUMMARY_COLUMNS:
                values_all = [
                    parsed
                    for model in metric_models[metric]
                    for parsed in [parse_float(row.get(f"{metric}_{model}", ""))]
                    if parsed is not None
                ]
                for _, group_limit in SUMMARY_GROUPS:
                    if group_limit is None:
                        selected_values = values_all
                        suffix = "ALL"
                    else:
                        selected_values = values_all[:group_limit]
                        suffix = "TOP3"

                    mean_value, sd_value = summarize_values(selected_values)
                    output_row[f"{metric}_MEAN_{suffix}"] = format_float(mean_value)
                    output_row[f"{metric}_SD_{suffix}"] = format_float(sd_value)
            output_rows.append(output_row)

    output_path = Path(args.output) if args.output else default_output_path(input_path)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fieldnames, delimiter=output_delimiter)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"[OK] Wrote {len(output_rows)} ligands to: {output_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(1)
