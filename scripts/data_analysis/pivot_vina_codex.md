

Generate ligand matrix script
No tasks in progress


## Me:
make all your responces with ## ## Codex:
 
H:\My Drive\VSCode_Github\virtual_docking\scripts\data_analysis 
Φτιάξε μου ένα script πιθανόν τα Python, όπου θα έχει header βέβαια με όλα αυτά τα χαρακτηριστικά που έχουμε πει. Να περιλαμβάνεις author, version, ημερομηνία, usage example, help και όλα αυτά και ό,τι χρειάζεται να παίρνεις από το argument, το αρχείο κτλ. όπου θα διαβάζει ένα αρχείο σαν αυτό σε αυτή τη λίστα και θα δημιουργεί ένα αρχείο με... Επειδή η λίστα αυτή περιλαμβάνει έως εννέα επαναλήψεις του ίδιου συνδυασμού ligand της διάφορης στήλης, να βάλει την ίδια πρώτη στήλη σε μια σειρά, όπου θα έχει, ας πούμε, με βάση την στήλη 2, που είναι το μοντέλο. Έτσι, η πρώτη στήλη, μετά η στήλη 2 κτλ. με το μοντέλο 1, μετά πιο δίπλα δεξιά στην ίδια σειρά το μοντέλο 2, 3, 4, έτσι ώστε ο κάθε ligand να εμφανιστεί ως μία γραμμή, όχι ως πολλαπλές μέχρι εννέα γραμμές. Πες μου αν κατάλαβες αυτό που λέω.



## Codex:
Θα το χειριστώ σαν αίτημα για νέο script μέσα στο virtual_docking/scripts/data_analysis που διαβάζει λίστα τύπου Vina, κάνει pivot τα επαναλαμβανόμενα models του ίδιου ligand σε μία γραμμή και γράφει νέο αρχείο. Πρώτα διαβάζω ένα δείγμα από το .lst και κοιτάζω το ύφος/header που χρησιμοποιούμε ήδη στα scripts σας, ώστε να το φτιάξω στο ίδιο στυλ.

Ran Get-Content -Path 'H:\My Drive\VSCode_Github\FDA\docking\run\output\pdbqt_20260320_vina.lst' -TotalCount 30 for 30s


Ran rg -n --glob '*.py' --glob '*.sh' "author|Author|version|Usage|usage|Created|Date" 'H:\My Drive\VSCode_Github\virtual_docking\scripts\data_analysis' for 30s


Ran Get-ChildItem -Path 'H:\My Drive\VSCode_Github\virtual_docking\scripts\data_analysis' -File | Select-Object -ExpandProperty FullName for 30s


## Codex:
Το πρώτο read απέτυχε από το sandbox του terminal, όχι από τα αρχεία μας. Ξανατρέχω τα ίδια reads με έγκριση ώστε να δω το δείγμα εισόδου και να γράψω το script σωστά, χωρίς να μαντέψω το format.

Ran Get-ChildItem -Path 'H:\My Drive\VSCode_Github\virtual_docking\scripts\data_analysis' -File | Select-Object -ExpandProperty FullName for 1s


Ran Get-Content -Path 'H:\My Drive\VSCode_Github\FDA\docking\run\output\pdbqt_20260320_vina.lst' -TotalCount 30 for 2s


Ran rg -n --glob '*.py' --glob '*.sh' "author|Author|version|Usage|usage|Created|Date" 'H:\My Drive\VSCode_Github\virtual_docking\scripts\data_analysis' for 3s


## Codex:
Βρήκα το header style των scripts, αλλά το συγκεκριμένο .lst δεν είναι στο path που έδωσες αυτούσιο. Ψάχνω τώρα το πραγματικό αρχείο με αυτό το όνομα μέσα στο workspace και μετά φτιάχνω το Python script πάνω στο ακριβές layout του.

Ran Get-ChildItem -Path 'H:\My Drive\VSCode_Github' -Recurse -File -Filter 'pdbqt_20260320_vina.lst' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName for 10s


Ran Get-Content -Path 'H:\My Drive\VSCode_Github\virtual_docking\scripts\data_analysis\aggregate_results.sh' -TotalCount 120 for 1s


Ran Get-Content -Path 'H:\My Drive\VSCode_Github\virtual_docking\scripts\data_analysis\extract_vina_results.sh' -TotalCount 140 for 1s


## Codex:
Έχω ήδη το ακριβές header convention και το column schema από το extract_vina_results.sh: LIGAND,MODEL,VINA_SCORE,RMSD_LB,RMSD_UB,INTER_PLUS_INTRA,INTER,INTRA,UNBOUND. Κάνω ένα τελευταίο scan για παρόμοια .lst/.csv outputs, ώστε το νέο εργαλείο να αντέχει και header και χωρίς header, και μετά το γράφω.

Ran Get-ChildItem -Path 'H:\My Drive\VSCode_Github' -Recurse -File -Include *.lst,*.csv -ErrorAction SilentlyContinue | Where-Object { $_.Name -match 'vina|pdbqt' } | Select-Object -First 40 -ExpandProperty FullName for 1m 22s


Ran Get-Content -Path 'H:\My Drive\VSCode_Github\virtual_docking\scripts\data_analysis\estimate_size.sh' -TotalCount 80


## Codex:
Προχωράω στο edit. Θα φτιάξω ένα αυτόνομο Python CLI με πλήρες header/help, auto-detect του separator και “wide” output όπου κάθε LIGAND γίνεται μία γραμμή και τα πεδία κάθε MODEL απλώνονται δεξιά ως _1, _2, _3 κτλ.

Rejected
pivot_vina_models.py
+280
-0
pivot_vina_models.py
+280
-0

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
    print(f"[OK] Models expanded into columns: {', '.join(output_header[1:1 + min(8, len(output_header) - 1)])}" if len(output_header) > 1 else "[OK] No model columns written.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(1)
## Codex:
Το write μέσω patch χτύπησε πάλι στο ίδιο Windows sandbox setup issue, όχι στο περιεχόμενο του script. Θα το ξανακάνω αμέσως με το σχετικό path μέσα στο workspace για να περάσει καθαρά.

Rejected
pivot_vina_models.py
+285
-0
pivot_vina_models.py
+285
-0

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
## Codex:
Το apply_patch δεν λειτουργεί καθόλου στο τρέχον Windows sandbox session, οπότε κάνω controlled fallback με Set-Content για να μη μείνουμε μπλοκαρισμένοι. Μετά θα το ελέγξω με --help και ένα μικρό δοκιμαστικό input.

Ran @' #!/usr/bin/env python3 # -*- coding: utf-8 -*- # # ============================================================================= # Script: pivot_vina_models.py # Purpose: # Read a Vina result table in long format and convert it to wide format so # each ligand appears only once, with one block of columns per MODEL. # # Expected input columns: # LIGAND, MODEL, VINA_SCORE, RMSD_LB, RMSD_UB, INTER_PLUS_INTRA, # INTER, INTRA, UNBOUND # # Input notes: # The script accepts comma-separated, tab-separated, semicolon-separated, # or whitespace-delimited files. # Headered and headerless inputs are both supported. # # Output: # A delimited text file where each ligand is a single row and each model is # expanded into columns such as: # LIGAND, MODEL_1, VINA_SCORE_1, ..., UNBOUND_1, MODEL_2, VINA_SCORE_2, ... # # Author: Evangelos Papadopoulos # Version: 1.0 # Date: 2026-03-24 # # Usage: # python pivot_vina_models.py -i input.lst -o output_wide.csv # # Examples: # python pivot_vina_models.py -i pdbqt_20260320_vina.lst # python pivot_vina_models.py -i pdbqt_20260320_vina.lst -o pdbqt_20260320_vina_wide.csv # python pivot_vina_models.py -i results.csv --input-delimiter comma --output-delimiter tab # # Help: # python pivot_vina_models.py --help # ============================================================================= from __future__ import annotations import argparse import csv import sys from collections import OrderedDict from pathlib import Path from typing import Iterable DEFAULT_COLUMNS = [ "LIGAND", "MODEL", "VINA_SCORE", "RMSD_LB", "RMSD_UB", "INTER_PLUS_INTRA", "INTER", "INTRA", "UNBOUND", ] VALUE_COLUMNS = [column for column in DEFAULT_COLUMNS if column != "LIGAND"] DELIMITER_MAP = { "comma": ",", "tab": "\t", "semicolon": ";", } def build_parser() -> argparse.ArgumentParser: parser = argparse.ArgumentParser( description=( "Convert long-format AutoDock Vina results into a wide table with " "one row per ligand and one block of columns per model." ), formatter_class=argparse.ArgumentDefaultsHelpFormatter, ) parser.add_argument( "-i", "--input", required=True, help="Path to the input Vina list/table file.", ) parser.add_argument( "-o", "--output", help=( "Path to the output file. If omitted, a sibling file ending with " "'_wide.csv' is created." ), ) parser.add_argument( "--input-delimiter", choices=["auto", "comma", "tab", "semicolon", "whitespace"], default="auto", help="Delimiter used in the input file.", ) parser.add_argument( "--output-delimiter", choices=["comma", "tab", "semicolon"], default="comma", help="Delimiter used in the output file.", ) parser.add_argument( "--no-header", action="store_true", help="Treat the input file as headerless even if the first row looks like a header.", ) parser.add_argument( "--max-models", type=int, default=None, help="Limit the output to models up to this number.", ) return parser def sniff_delimiter(sample: str, requested: str) -> str | None: if requested != "auto": if requested == "whitespace": return None return DELIMITER_MAP[requested] counts = { ",": sample.count(","), "\t": sample.count("\t"), ";": sample.count(";"), } best_delimiter, best_count = max(counts.items(), key=lambda item: item[1]) if best_count > 0: return best_delimiter return None def normalize_header(tokens: Iterable[str]) -> list[str]: return [token.strip().upper() for token in tokens] def looks_like_header(row: list[str]) -> bool: normalized = normalize_header(row) return len(normalized) >= 2 and normalized[0] == "LIGAND" and normalized[1] == "MODEL" def split_line(line: str, delimiter: str | None) -> list[str]: stripped = line.strip() if not stripped: return [] if delimiter is None: return stripped.split() return next(csv.reader([stripped], delimiter=delimiter)) def read_rows(path: Path, delimiter: str | None, force_no_header: bool) -> tuple[list[str], list[list[str]]]: rows: list[list[str]] = [] with path.open("r", encoding="utf-8-sig", newline="") as handle: for raw_line in handle: parsed = split_line(raw_line, delimiter) if parsed: rows.append([field.strip() for field in parsed]) if not rows: raise ValueError(f"Input file is empty: {path}") first_row = rows[0] if force_no_header: return DEFAULT_COLUMNS, rows if looks_like_header(first_row): return normalize_header(first_row), rows[1:] return DEFAULT_COLUMNS, rows def coerce_model_key(value: str) -> tuple[int, str]: text = value.strip() try: return (0, f"{int(text):09d}") except ValueError: return (1, text) def pivot_rows(header: list[str], rows: list[list[str]], max_models: int | None) -> tuple[list[str], list[list[str]]]: if len(header) < len(DEFAULT_COLUMNS): raise ValueError( "Input must contain at least these columns: " + ", ".join(DEFAULT_COLUMNS) ) header_index = {name: idx for idx, name in enumerate(header)} missing = [name for name in DEFAULT_COLUMNS if name not in header_index] if missing: raise ValueError(f"Missing required columns: {', '.join(missing)}") ligands: OrderedDict[str, dict[str, dict[str, str]]] = OrderedDict() seen_models: set[str] = set() for row_number, row in enumerate(rows, start=2): if len(row) < len(header): row = row + [""] * (len(header) - len(row)) ligand = row[header_index["LIGAND"]].strip() model = row[header_index["MODEL"]].strip() if not ligand: raise ValueError(f"Row {row_number}: empty LIGAND value.") if not model: raise ValueError(f"Row {row_number}: empty MODEL value.") if max_models is not None: try: if int(model) > max_models: continue except ValueError: pass ligand_bucket = ligands.setdefault(ligand, OrderedDict()) model_bucket = ligand_bucket.setdefault(model, {}) for column in VALUE_COLUMNS: model_bucket[column] = row[header_index[column]].strip() seen_models.add(model) sorted_models = sorted(seen_models, key=coerce_model_key) output_header = ["LIGAND"] for model in sorted_models: for column in VALUE_COLUMNS: output_header.append(f"{column}_{model}") output_rows: list[list[str]] = [] for ligand, model_map in ligands.items(): output_row = [ligand] for model in sorted_models: values = model_map.get(model, {}) for column in VALUE_COLUMNS: output_row.append(values.get(column, "")) output_rows.append(output_row) return output_header, output_rows def default_output_path(input_path: Path) -> Path: return input_path.with_name(f"{input_path.stem}_wide.csv") def main() -> int: parser = build_parser() args = parser.parse_args() input_path = Path(args.input) if not input_path.is_file(): parser.error(f"Input file not found: {input_path}") with input_path.open("r", encoding="utf-8-sig", newline="") as handle: sample = handle.read(4096) delimiter = sniff_delimiter(sample, args.input_delimiter) header, rows = read_rows(input_path, delimiter, args.no_header) output_header, output_rows = pivot_rows(header, rows, args.max_models) output_path = Path(args.output) if args.output else default_output_path(input_path) output_delimiter = DELIMITER_MAP[args.output_delimiter] with output_path.open("w", encoding="utf-8", newline="") as handle: writer = csv.writer(handle, delimiter=output_delimiter) writer.writerow(output_header) writer.writerows(output_rows) print(f"[OK] Wrote {len(output_rows)} ligands to: {output_path}") if len(output_header) > 1: preview = ", ".join(output_header[1:1 + min(8, len(output_header) - 1)]) print(f"[OK] Example output columns: {preview}") else: print("[OK] No model columns written.") return 0 if __name__ == "__main__": try: raise SystemExit(main()) except Exception as exc: # pragma: no cover print(f"[ERROR] {exc}", file=sys.stderr) raise SystemExit(1) '@ | Set-Content -Path 'H:\My Drive\VSCode_Github\virtual_docking\scripts\data_analysis\pivot_vina_models.py' -Encoding UTF8 for 2m 57s


## Codex:
Το script γράφτηκε. Τώρα το ελέγχω πρακτικά με --help και με ένα μικρό synthetic Vina table, για να επιβεβαιώσω ότι όντως γυρίζει πολλαπλές γραμμές του ίδιου ligand σε μία wide γραμμή.

Ran @' LIGAND,MODEL,VINA_SCORE,RMSD_LB,RMSD_UB,INTER_PLUS_INTRA,INTER,INTRA,UNBOUND LigA,1,-8.1,0.0,0.0,-10.0,-9.0,-1.0,2.0 LigA,2,-7.9,1.5,2.1,-9.7,-8.8,-0.9,2.0 LigB,1,-6.5,0.0,0.0,-7.2,-6.8,-0.4,1.2 '@ | Set-Content -Path 'H:\My Drive\VSCode_Github\virtual_docking\scripts\data_analysis\_pivot_test_input.csv' -Encoding UTF8 for 15s


Ran python 'H:\My Drive\VSCode_Github\virtual_docking\scripts\data_analysis\pivot_vina_models.py' --help for 9s


Ran Get-Content -Path 'H:\My Drive\VSCode_Github\virtual_docking\scripts\data_analysis\pivot_vina_models.py' -TotalCount 40 for 1s


## Codex:
Το CLI βγήκε σωστά. Τρέχω τώρα το end-to-end test πάνω στο μικρό δείγμα και θα επιβεβαιώσω και το σχήμα του παραγόμενου output.

Ran python 'H:\My Drive\VSCode_Github\virtual_docking\scripts\data_analysis\pivot_vina_models.py' -i 'H:\My Drive\VSCode_Github\virtual_docking\scripts\data_analysis\_pivot_test_input.csv' -o 'H:\My Drive\VSCode_Github\virtual_docking\scripts\data_analysis\_pivot_test_output.csv' for 14s


Ran Get-Content -Path 'H:\My Drive\VSCode_Github\virtual_docking\scripts\data_analysis\_pivot_test_output.csv' for 1s


## Codex:
Το run πέτυχε και δήλωσε ότι έγραψε 2 ligands, αλλά το δεύτερο read δεν βρήκε το αρχείο στο ίδιο path, οπότε κάνω ένα γρήγορο locate στο folder για να δω αν το PowerShell το έγραψε με διαφορετικό normalization/path handling.

Ran Get-ChildItem -Path 'H:\My Drive\VSCode_Github\virtual_docking\scripts\data_analysis' -File | Where-Object { $_.Name -like '_pivot_test_*' -or $_.Name -eq 'pivot_vina_models.py' } | Select-Object Name,FullName,Length for 16s


Ran Get-ChildItem -Path 'H:\My Drive\VSCode_Github' -Recurse -File -Filter '_pivot_test_output.csv' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName for 8s


## Codex:
Το output υπάρχει κανονικά, άρα ήταν παροδικό path/read hiccup. Κάνω το τελευταίο read για να επιβεβαιώσω ότι η διάταξη των στηλών είναι ακριβώς όπως τη θες.

Ran Get-Content -Path 'H:\My Drive\VSCode_Github\virtual_docking\scripts\data_analysis\_pivot_test_output.csv'


Worked for 10m 54s
## Codex:
Ναι, το κατάλαβα σωστά: θέλεις από ένα long-format αρχείο όπου το ίδιο LIGAND εμφανίζεται μέχρι 9 φορές, μία για κάθε MODEL, να φτιάχνουμε wide-format output όπου κάθε ligand εμφανίζεται μόνο μία φορά και τα πεδία των MODEL 1, 2, 3... απλώνονται δεξιά στην ίδια γραμμή.

Έφτιαξα το script pivot_vina_models.py στο virtual_docking/scripts/data_analysis. Παίρνει input/output από arguments, έχει πλήρες header με author/version/date/usage/examples/help, κάνει auto-detect separator, δουλεύει με header ή χωρίς, και γράφει output τύπου:
LIGAND,MODEL_1,VINA_SCORE_1,...,UNBOUND_1,MODEL_2,VINA_SCORE_2,...

Χρήση:

python "H:\My Drive\VSCode_Github\virtual_docking\scripts\data_analysis\pivot_vina_models.py" -i "INPUT.lst"
Αν θέλεις συγκεκριμένο output path:

python "H:\My Drive\VSCode_Github\virtual_docking\scripts\data_analysis\pivot_vina_models.py" -i "INPUT.lst" -o "OUTPUT_wide.csv"
Το έλεγξα με δοκιμαστικό αρχείο και έβγαλε σωστά μία γραμμή ανά ligand. Το μόνο που δεν μπόρεσα να κάνω ήταν να το τρέξω πάνω στο δικό σου πραγματικό pdbqt_20260320_vina.lst, γιατί δεν βρέθηκε στο workspace στο path που φάνηκε από το tab. Αν μου δώσεις το ακριβές path ή αν θέλεις, στο επόμενο βήμα το τρέχω εγώ πάνω στο κανονικό αρχείο σου.


1 file changed
Undo

Review
scripts/data_analysis/pivot_vina_models.py




GPT-5.4

Medium

IDE context


Local

Default permissions
