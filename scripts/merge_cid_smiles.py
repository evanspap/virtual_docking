#!/usr/bin/env python3
"""
===============================================================================
 Script Name : merge_cid_smiles.py
 Version     : 1.3
 Author      : Evangelos Papadopoulos
 Date        : 2025-09-09

 Description :
   This script merges two files:
     1. A CID–SMILES mapping file (tab-delimited, header: CID, SMILES).
     2. A docking results file (CSV with leading CID column).

   It outputs a new CSV file where the second column is the corresponding
   SMILES string from the CID–SMILES file.

   The header from the docking results is preserved, with "SMILES" inserted
   as the second column.
   
 Usage:
   python merge_cid_smiles.py <cid_smiles.tsv> <sorted_input.csv> <output.csv>

 Example:
   python merge_cid_smiles.py \
       /gpfs/scratch/.../cid_smiles.tsv \
       sorted_EP300.csv \
       sorted_EP300_out.csv

===============================================================================
"""

import sys
import csv

def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    cid_smiles_file, docking_file, output_file = sys.argv[1:4]

    print(f"Running: merge_cid_smiles.py {cid_smiles_file} {docking_file} {output_file}")

    # Load CID→SMILES mapping
    cid2smiles = {}
    with open(cid_smiles_file) as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            cid = row["CID"].strip()
            smiles = row["SMILES"].strip()
            cid2smiles[cid] = smiles

    with open(docking_file) as fin, open(output_file, "w", newline="") as fout:
        reader = csv.reader(fin)
        writer = csv.writer(fout)

        header = next(reader)
        # Insert SMILES column after Ligand
        new_header = [header[0], "SMILES"] + header[1:]
        writer.writerow(new_header)

        for row in reader:
            if not row:
                continue
            cid = row[0].strip()
            smiles = cid2smiles.get(cid, "NA")
            writer.writerow([cid, smiles] + row[1:])

if __name__ == "__main__":
    main()

