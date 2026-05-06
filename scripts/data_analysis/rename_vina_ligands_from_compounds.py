#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# =============================================================================
# Script: rename_vina_ligands_from_compounds.py
# Purpose:
#   Rename the first ligand column in a Vina wide-analysis CSV using metadata
#   from the compounds_with_pdb_flat_selected_PPT.csv table.
#
# Input ligand format:
#   CompoundName_PDB_CCD
#
# Output ligand format:
#   CompoundName_CCD_PDB_PrimaryUniProtEntryName_PrimaryGeneSymbol
# =============================================================================

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


COMPOUNDS_COLUMNS = [
    "Compound_Name",
    "ChEMBL_ID",
    "CCD",
    "PDB_ID",
    "PDB_ID_DUPLICATE",
    "Primary_UniProt_Entry_Name",
    "Primary_Gene_Symbol",
    "Primary_UniProt_ID",
    "Primary_Protein_Name",
]

DELIMITER_MAP = {
    "comma": ",",
    "tab": "\t",
    "semicolon": ";",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Rename Vina ligand identifiers using compound/PDB/CCD matches from "
            "a compounds flat file."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-i", "--input", required=True, help="Path to the analysis CSV file.")
    parser.add_argument(
        "-c",
        "--compounds",
        required=True,
        help="Path to the headerless compounds_with_pdb_flat_selected_PPT.csv file.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help=(
            "Path to the output CSV. If omitted, a sibling "
            "'*_renamed_ligands_20260328.csv' file is created."
        ),
    )
    parser.add_argument(
        "--input-delimiter",
        choices=["auto", "comma", "tab", "semicolon"],
        default="auto",
        help="Delimiter used in the analysis input file.",
    )
    parser.add_argument(
        "--compounds-delimiter",
        choices=["auto", "comma", "tab", "semicolon"],
        default="auto",
        help="Delimiter used in the compounds file.",
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


def read_sample(path: Path) -> str:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return handle.read(4096)


def normalize_token(value: str) -> str:
    return value.strip().upper()


def clean_output_token(value: str) -> str:
    text = value.strip()
    if not text or text == "0":
        return "NA"
    return text.replace(" ", "-").replace("/", "-")


def parse_input_ligand(value: str) -> tuple[str, str, str]:
    parts = value.strip().split("_")
    if len(parts) < 3:
        raise ValueError(
            f"Cannot parse ligand identifier '{value}'. Expected format Compound_PDB_CCD."
        )
    compound_name = parts[0].strip()
    pdb_id = parts[1].strip()
    ccd = parts[2].strip()
    return compound_name, pdb_id, ccd


def load_compounds_map(compounds_path: Path, delimiter: str) -> dict[tuple[str, str, str], dict[str, str]]:
    mapping: dict[tuple[str, str, str], dict[str, str]] = {}
    with compounds_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle, delimiter=delimiter)
        for line_number, row in enumerate(reader, start=1):
            if not row or not any(cell.strip() for cell in row):
                continue
            if len(row) < len(COMPOUNDS_COLUMNS):
                raise ValueError(
                    f"Compounds file row {line_number} has {len(row)} columns; "
                    f"expected at least {len(COMPOUNDS_COLUMNS)}."
                )
            record = {
                column_name: row[index].strip()
                for index, column_name in enumerate(COMPOUNDS_COLUMNS)
            }
            key = (
                normalize_token(record["Compound_Name"]),
                normalize_token(record["PDB_ID"]),
                normalize_token(record["CCD"]),
            )
            mapping[key] = record
    if not mapping:
        raise ValueError(f"No compounds rows loaded from: {compounds_path}")
    return mapping


def build_output_ligand(input_ligand: str, record: dict[str, str]) -> str:
    compound_name, pdb_id, ccd = parse_input_ligand(input_ligand)
    return "_".join(
        [
            clean_output_token(compound_name),
            clean_output_token(ccd),
            clean_output_token(pdb_id),
            clean_output_token(record["Primary_UniProt_Entry_Name"]),
            clean_output_token(record["Primary_Gene_Symbol"]),
        ]
    )


def default_output_path(input_path: Path) -> Path:
    return input_path.with_name(f"{input_path.stem}_renamed_ligands_20260328.csv")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    input_path = Path(args.input)
    compounds_path = Path(args.compounds)
    if not input_path.is_file():
        parser.error(f"Input analysis file not found: {input_path}")
    if not compounds_path.is_file():
        parser.error(f"Compounds file not found: {compounds_path}")

    input_delimiter = sniff_delimiter(read_sample(input_path), args.input_delimiter)
    compounds_delimiter = sniff_delimiter(read_sample(compounds_path), args.compounds_delimiter)
    output_delimiter = DELIMITER_MAP[args.output_delimiter]

    compounds_map = load_compounds_map(compounds_path, compounds_delimiter)

    with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=input_delimiter)
        if not reader.fieldnames:
            raise ValueError("Analysis input file has no header.")

        fieldnames = list(reader.fieldnames)
        ligand_column = fieldnames[0]
        output_rows: list[dict[str, str]] = []
        missing_keys: list[str] = []

        for row in reader:
            original_ligand = row.get(ligand_column, "").strip()
            compound_name, pdb_id, ccd = parse_input_ligand(original_ligand)
            key = (
                normalize_token(compound_name),
                normalize_token(pdb_id),
                normalize_token(ccd),
            )
            record = compounds_map.get(key)
            output_ligand = (
                original_ligand if record is None else build_output_ligand(original_ligand, record)
            )
            if record is None:
                missing_keys.append(original_ligand)

            output_row = dict(row)
            output_row[ligand_column] = output_ligand
            output_rows.append(output_row)

    output_path = Path(args.output) if args.output else default_output_path(input_path)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter=output_delimiter)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"[OK] Wrote {len(output_rows)} rows to: {output_path}")
    if missing_keys:
        unique_missing = sorted(set(missing_keys))
        print(
            f"[WARN] No compounds match for {len(unique_missing)} ligand identifiers. "
            "Those rows kept their original LIGAND values.",
            file=sys.stderr,
        )
        for ligand in unique_missing[:20]:
            print(f"[WARN] Missing: {ligand}", file=sys.stderr)
        if len(unique_missing) > 20:
            print(
                f"[WARN] ... and {len(unique_missing) - 20} more unmatched ligands.",
                file=sys.stderr,
            )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(1)
