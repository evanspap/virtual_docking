#!/usr/bin/env python3
"""
------------------------------------------------------------
 Script: parse_vina_out.py
 Author: Evangelos Papadopoulos
 Version: 2.0
 Control Number: CAD-VINA-2025-09-09
 Date: 2025-09-09

 Function:
    Parse AutoDock Vina .out files, extract docking results,
    compute average affinities (all and top-X), and estimate
    the runtime duration (seconds) from Start/End timestamps.
    Outputs results in CSV format.

 Usage:
    python parse_vina_out.py <vina_output_file> [--header] [--top X]

 Example:
    python parse_vina_out.py CID315384_cad_p1.out --header --top 2

 Output:
    CSV line with columns:
    Ligand, avg_affinity_all, avg_affinity_topX,
    mode_i, affinity_i, rmsd_lb_i, rmsd_ub_i, ..., duration_seconds
------------------------------------------------------------
"""

import sys
import os
from datetime import datetime

def parse_vina_output(filename):
    ligand_id = os.path.basename(filename).split('_')[0]
    data_started = False
    results = []
    current_block = []

    start_time, end_time = None, None

    with open(filename, 'r') as f:
        for line in f:
            line = line.rstrip()

            if line.startswith("Start:"):
                try:
                    start_time = datetime.strptime(line.split("Start:")[1].strip(),
                                                   "%a %b %d %I:%M:%S %p %Z %Y")
                except Exception:
                    pass

            if line.startswith("End:"):
                try:
                    end_time = datetime.strptime(line.split("End:")[1].strip(),
                                                 "%a %b %d %I:%M:%S %p %Z %Y")
                except Exception:
                    pass

            if "mode" in line and "affinity" in line:
                data_started = True
                current_block = []
                continue
            if data_started:
                if line.strip() == "" or line.startswith("-----"):
                    continue
                if line.startswith("End") or line.startswith("Start") or line.startswith("AutoDock Vina"):
                    data_started = False
                    if current_block:
                        results = current_block  # overwrite with latest block
                    continue
                parts = line.split()
                if len(parts) >= 4 and parts[0].isdigit():
                    mode, affinity, rmsd_lb, rmsd_ub = parts[:4]
                    current_block.append((int(mode), float(affinity), float(rmsd_lb), float(rmsd_ub)))

    if data_started and current_block:
        results = current_block

    # compute duration
    duration = None
    if start_time and end_time:
        duration = int((end_time - start_time).total_seconds())

    return ligand_id, results, duration

def format_output(ligand_id, results, top_n, duration):
    affinities = [affinity for _, affinity, _, _ in results]
    avg_all = sum(affinities) / len(affinities) if affinities else 0
    top_avg = sum(sorted(affinities)[:top_n]) / min(top_n, len(affinities)) if affinities else 0

    flat_values = [ligand_id, round(avg_all, 3), round(top_avg, 3)]
    for mode, affinity, rmsd_lb, rmsd_ub in results:
        flat_values.extend([mode, affinity, rmsd_lb, rmsd_ub])
    flat_values.append(duration if duration is not None else "NA")
    return ', '.join(map(str, flat_values))

def print_header(max_modes=9):
    header = ["Ligand", "avg_affinity_all", "avg_affinity_topX"]
    for i in range(1, max_modes + 1):
        header.extend([
            f"mode_{i}",
            f"affinity_{i}(Kcal/mol)",
            f"rmsd_lb_{i}",
            f"rmsd_ub_{i}"
        ])
    header.append("duration_seconds")
    print(', '.join(header))

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    show_header = '--header' in sys.argv
    top_n = 3
    for i, arg in enumerate(sys.argv):
        if arg == '--top' and i + 1 < len(sys.argv):
            try:
                top_n = int(sys.argv[i + 1])
            except ValueError:
                print("Error: Invalid value for --top. Must be an integer.")
                sys.exit(1)

    vina_file = next((arg for arg in sys.argv[1:] if not arg.startswith('--')), None)

    if not vina_file or not os.path.isfile(vina_file):
        print(f"Error: file not found or not specified: {vina_file}")
        sys.exit(1)

    ligand_id, results, duration = parse_vina_output(vina_file)

    if show_header:
        print_header(max_modes=len(results))

    print(format_output(ligand_id, results, top_n, duration))

if __name__ == '__main__':
    main()

