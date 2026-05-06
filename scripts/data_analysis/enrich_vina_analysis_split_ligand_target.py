#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# =============================================================================
# Script: enrich_vina_analysis_split_ligand_target.py
# Purpose:
#   Split the first LIGAND column of a Vina analysis CSV into compound/target
#   components and append metadata columns using a primary enriched TSV plus an
#   optional fallback TSV for missing ligand CCD values.
# =============================================================================

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


EXTRA_COLUMNS = [
    "Ligand_CCD",
    "Target_Name",
    "Target_PDB",
    "Target_CCD",
    "Target_Primary_UniProt_ID",
    "Target_Primary_UniProt_Entry_Name",
    "Target_Primary_Gene_Symbol",
]

DELIMITER_MAP = {
    "comma": ",",
    "tab": "\t",
    "semicolon": ";",
}

REQUIRED_COMPOUND_COLUMNS = [
    "Compound_Name",
    "CCD",
    "PDB_ID",
    "UniProt_IDs",
    "UniProt_Entry_Names",
    "Gene_Symbols",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Split the first ligand column into compound and target fields and "
            "append metadata from an enriched TSV, with optional ligand CCD fallback TSV."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-i", "--input", required=True, help="Path to the analysis CSV file.")
    parser.add_argument(
        "-c",
        "--compounds",
        required=True,
        help="Primary compounds TSV, typically compounds_with_pdb_flat_uniprot_enriched.tsv.",
    )
    parser.add_argument(
        "--ligand-ccd-fallback",
        help="Optional fallback TSV used only for missing Ligand_CCD values.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help=(
            "Path to the output CSV. If omitted, a sibling "
            "'*_split_target_metadata_hybrid_20260401.csv' file is created."
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
        default="tab",
        help="Delimiter used in the primary compounds file.",
    )
    parser.add_argument(
        "--fallback-delimiter",
        choices=["auto", "comma", "tab", "semicolon"],
        default="tab",
        help="Delimiter used in the fallback compounds file.",
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
    counts = {",": sample.count(","), "\t": sample.count("\t"), ";": sample.count(";")}
    best_delimiter, best_count = max(counts.items(), key=lambda item: item[1])
    return best_delimiter if best_count > 0 else ","


def read_sample(path: Path) -> str:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return handle.read(4096)


def normalize_token(value: str) -> str:
    return value.strip().upper()


def clean_value(value: str) -> str:
    text = value.strip()
    if not text or text == "0":
        return ""
    return text


def take_first_semicolon_value(value: str) -> str:
    text = clean_value(value)
    if not text:
        return ""
    return text.split(";")[0].strip()


def parse_input_ligand(value: str) -> tuple[str, str, str]:
    parts = value.strip().split("_")
    if len(parts) < 3:
        raise ValueError(f"Cannot parse ligand identifier '{value}'. Expected format Compound_PDB_CCD.")
    return parts[0].strip(), parts[1].strip(), parts[2].strip()


def validate_compound_columns(fieldnames: list[str]) -> None:
    missing = [column for column in REQUIRED_COMPOUND_COLUMNS if column not in fieldnames]
    if missing:
        raise ValueError(f"Compounds file is missing required columns: {', '.join(missing)}")


def load_compound_ccd_map(compounds_path: Path, delimiter: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    with compounds_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        if not reader.fieldnames:
            raise ValueError(f"Compounds file has no header: {compounds_path}")
        validate_compound_columns(list(reader.fieldnames))
        for row in reader:
            compound_name = normalize_token(row.get("Compound_Name", ""))
            if not compound_name:
                continue
            ligand_ccd = clean_value(row.get("CCD", ""))
            existing = mapping.get(compound_name)
            if existing is None:
                mapping[compound_name] = ligand_ccd
            elif ligand_ccd and existing != ligand_ccd:
                raise ValueError(
                    f"Compound {row.get('Compound_Name', '').strip()} has multiple ligand CCD values: {existing} vs {ligand_ccd}"
                )
    return mapping


def load_compound_ccd_variant_map(compounds_path: Path, delimiter: str) -> dict[str, set[str]]:
    mapping: dict[str, set[str]] = {}
    with compounds_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        if not reader.fieldnames:
            raise ValueError(f"Compounds file has no header: {compounds_path}")
        validate_compound_columns(list(reader.fieldnames))
        for row in reader:
            compound_name = normalize_token(row.get("Compound_Name", ""))
            ligand_ccd = clean_value(row.get("CCD", ""))
            if not compound_name or not ligand_ccd:
                continue
            mapping.setdefault(compound_name, set()).add(ligand_ccd)
    return mapping


def resolve_ligand_ccd(
    compound_key: str,
    primary_map: dict[str, str],
    fallback_exact_map: dict[str, str],
    fallback_variant_map: dict[str, set[str]],
) -> tuple[str, bool]:
    ligand_ccd = primary_map.get(compound_key, "")
    if ligand_ccd:
        return ligand_ccd, False

    ligand_ccd = fallback_exact_map.get(compound_key, "")
    if ligand_ccd:
        return ligand_ccd, True

    variant_matches = [
        next(iter(sorted(ccds)))
        for name, ccds in fallback_variant_map.items()
        if name.startswith(f"{compound_key} ")
    ]
    variant_matches = sorted(set(match for match in variant_matches if match))
    if len(variant_matches) == 1:
        return variant_matches[0], True
    if len(variant_matches) > 1:
        raise ValueError(
            f"Compound {compound_key} matched multiple fallback CCD variants: {', '.join(variant_matches)}"
        )
    return "", False


def load_target_map(compounds_path: Path, delimiter: str) -> dict[tuple[str, str], dict[str, str]]:
    mapping: dict[tuple[str, str], dict[str, str]] = {}
    with compounds_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        if not reader.fieldnames:
            raise ValueError(f"Compounds file has no header: {compounds_path}")
        validate_compound_columns(list(reader.fieldnames))
        for row in reader:
            pdb_id = clean_value(row.get("PDB_ID", ""))
            ccd = clean_value(row.get("CCD", ""))
            if not pdb_id or not ccd:
                continue
            key = (normalize_token(pdb_id), normalize_token(ccd))
            if key not in mapping:
                mapping[key] = {
                    "Target_Primary_UniProt_ID": take_first_semicolon_value(row.get("UniProt_IDs", "")),
                    "Target_Primary_UniProt_Entry_Name": take_first_semicolon_value(row.get("UniProt_Entry_Names", "")),
                    "Target_Primary_Gene_Symbol": take_first_semicolon_value(row.get("Gene_Symbols", "")),
                }
    return mapping


def default_output_path(input_path: Path) -> Path:
    return input_path.with_name(f"{input_path.stem}_split_target_metadata_hybrid_20260401.csv")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    input_path = Path(args.input)
    compounds_path = Path(args.compounds)
    fallback_path = Path(args.ligand_ccd_fallback) if args.ligand_ccd_fallback else None
    if not input_path.is_file():
        parser.error(f"Input analysis file not found: {input_path}")
    if not compounds_path.is_file():
        parser.error(f"Primary compounds file not found: {compounds_path}")
    if fallback_path and not fallback_path.is_file():
        parser.error(f"Fallback compounds file not found: {fallback_path}")

    input_delimiter = sniff_delimiter(read_sample(input_path), args.input_delimiter)
    compounds_delimiter = sniff_delimiter(read_sample(compounds_path), args.compounds_delimiter)
    output_delimiter = DELIMITER_MAP[args.output_delimiter]

    primary_ligand_ccd_map = load_compound_ccd_map(compounds_path, compounds_delimiter)
    target_map = load_target_map(compounds_path, compounds_delimiter)

    fallback_ligand_ccd_map: dict[str, str] = {}
    fallback_ligand_ccd_variants: dict[str, set[str]] = {}
    if fallback_path:
        fallback_delimiter = sniff_delimiter(read_sample(fallback_path), args.fallback_delimiter)
        fallback_ligand_ccd_map = load_compound_ccd_map(fallback_path, fallback_delimiter)
        fallback_ligand_ccd_variants = load_compound_ccd_variant_map(fallback_path, fallback_delimiter)

    with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=input_delimiter)
        if not reader.fieldnames:
            raise ValueError("Analysis input file has no header.")

        fieldnames = list(reader.fieldnames)
        ligand_column = fieldnames[0]
        output_fieldnames = list(fieldnames)
        insert_at = 1
        for column in EXTRA_COLUMNS:
            if column not in output_fieldnames:
                output_fieldnames.insert(insert_at, column)
                insert_at += 1

        output_rows: list[dict[str, str]] = []
        missing_ligands: list[str] = []
        missing_targets: list[str] = []
        fallback_hits = 0

        for row in reader:
            original_ligand = row.get(ligand_column, "").strip()
            compound_name, target_pdb, target_ccd = parse_input_ligand(original_ligand)
            target_name = f"{target_pdb}_{target_ccd}"
            compound_key = normalize_token(compound_name)

            ligand_ccd, used_fallback = resolve_ligand_ccd(
                compound_key,
                primary_ligand_ccd_map,
                fallback_ligand_ccd_map,
                fallback_ligand_ccd_variants,
            )
            if used_fallback:
                fallback_hits += 1

            target_record = target_map.get((normalize_token(target_pdb), normalize_token(target_ccd)))

            output_row = dict(row)
            output_row[ligand_column] = clean_value(compound_name)
            output_row["Ligand_CCD"] = ligand_ccd
            output_row["Target_Name"] = clean_value(target_name)
            output_row["Target_PDB"] = clean_value(target_pdb)
            output_row["Target_CCD"] = clean_value(target_ccd)
            output_row["Target_Primary_UniProt_ID"] = ""
            output_row["Target_Primary_UniProt_Entry_Name"] = ""
            output_row["Target_Primary_Gene_Symbol"] = ""

            if not ligand_ccd:
                missing_ligands.append(compound_name)

            if target_record is None:
                missing_targets.append(target_name)
            else:
                output_row["Target_Primary_UniProt_ID"] = target_record["Target_Primary_UniProt_ID"]
                output_row["Target_Primary_UniProt_Entry_Name"] = target_record["Target_Primary_UniProt_Entry_Name"]
                output_row["Target_Primary_Gene_Symbol"] = target_record["Target_Primary_Gene_Symbol"]

            output_rows.append(output_row)

    output_path = Path(args.output) if args.output else default_output_path(input_path)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fieldnames, delimiter=output_delimiter)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"[OK] Wrote {len(output_rows)} rows to: {output_path}")
    if fallback_ligand_ccd_map:
        print(f"[OK] Filled {fallback_hits} rows with Ligand_CCD from fallback TSV")
    if missing_ligands:
        unique_missing = sorted(set(missing_ligands))
        print(f"[WARN] No ligand CCD match for {len(unique_missing)} compounds.", file=sys.stderr)
        for compound in unique_missing[:20]:
            print(f"[WARN] Missing ligand CCD: {compound}", file=sys.stderr)
        if len(unique_missing) > 20:
            print(f"[WARN] ... and {len(unique_missing) - 20} more unmatched compounds.", file=sys.stderr)
    if missing_targets:
        unique_missing = sorted(set(missing_targets))
        print(f"[WARN] No target metadata match for {len(unique_missing)} target names.", file=sys.stderr)
        for target in unique_missing[:20]:
            print(f"[WARN] Missing target: {target}", file=sys.stderr)
        if len(unique_missing) > 20:
            print(f"[WARN] ... and {len(unique_missing) - 20} more unmatched targets.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(1)
