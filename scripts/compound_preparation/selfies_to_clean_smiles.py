#!/usr/bin/env python3
"""
===

Script Name : selfies_to_clean_smiles.py
Author      : Evangelos Papadopoulos
Version     : 1.9.0
Date        : 2026-02-11

=====================================================================
DESCRIPTION
-----------

This script converts SELFIES strings (e.g., generated from AI models)
into chemically sanitized CLOSED-SHELL SMILES strings.

⚠️ Important philosophy change (v1.8.0):
We DO NOT globally enforce valence for N, O, S, P, etc.
We ONLY repair true radicals.

Strategy (v1.8.0 core):
• Decode SELFIES → SMILES
• Remove radical electrons
• Allow RDKit to recompute implicit hydrogens
• Full sanitization

We avoid blanket valence enforcement because:
- Sulfoxides (S=O), sulfones, phosphates, etc.
- Charged nitrogen species
- Hypervalent sulfur or phosphorus

would otherwise be chemically corrupted.

---

Enhancements in v1.9.0:

```
✔ Radical repair (true radical electrons removed)
✔ Safe thiol repair (neutral sulfur with valence=1 → +H)
✔ Minimal canonical SMILES output
```

Safe thiol repair is intentionally conservative:
- Applies ONLY to neutral sulfur
- Applies ONLY when explicit valence = 1
- Does NOT affect sulfoxides, sulfones, or charged sulfur

This preserves chemical topology while correcting
common generative-model artifacts such as:
- O[S]
- C[S]

=====================================================================
USAGE
-----

python selfies_to_clean_smiles.py input.selfies > output.smi

=====================================================================
CHANGELOG
---------

v1.9.0

* Added safe thiol repair (S valence=1 → +H)
* Added minimal canonical SMILES output
* Preserved conservative radical-only philosophy

v1.8.0

* Removed global valence forcing for N/O/S
* Now repairs ONLY true radical electrons
* Safer for sulfur oxides, phosphates, charged species

v1.7.0

* Extended valence normalization to N, O, and S

License: MIT License
=====================================================================
"""

import sys
import argparse
import selfies as sf
from rdkit import Chem
from rdkit import RDLogger

RDLogger.DisableLog('rdApp.*')


def print_manual_and_exit():
    print(__doc__)
    sys.exit(1)


def repair_molecule(smiles):
    """
    Perform:
      1. Radical repair
      2. Safe thiol repair
      3. Full sanitization
    """
    try:
        mol = Chem.MolFromSmiles(smiles, sanitize=False)
        if mol is None:
            return None

        # -------------------------
        # 1️⃣ Radical repair
        # -------------------------
        for atom in mol.GetAtoms():
            if atom.GetNumRadicalElectrons() > 0:
                atom.SetNumRadicalElectrons(0)

        # Allow implicit hydrogens
        for atom in mol.GetAtoms():
            atom.SetNoImplicit(False)

        mol.UpdatePropertyCache(strict=False)

        # -------------------------
        # 2️⃣ Safe thiol repair
        # -------------------------
        for atom in mol.GetAtoms():
            if atom.GetAtomicNum() == 16:  # Sulfur
                if atom.GetFormalCharge() == 0:
                    explicit_valence = atom.GetExplicitValence()

                    # Neutral sulfur with valence 1 (e.g., O[S] or C[S])
                    if explicit_valence == 1:
                        atom.SetNumExplicitHs(atom.GetNumExplicitHs() + 1)
                        atom.SetNoImplicit(True)

        mol.UpdatePropertyCache(strict=False)

        # -------------------------
        # 3️⃣ Full sanitization
        # -------------------------
        Chem.SanitizeMol(mol)

        # Minimal canonical SMILES
        return Chem.MolToSmiles(mol, canonical=True)

    except Exception:
        return None


def main():
    if len(sys.argv) < 2:
        print_manual_and_exit()

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("input_file")

    try:
        args = parser.parse_args()
    except Exception:
        print_manual_and_exit()

    total = 0
    success = 0
    failed = 0

    try:
        infile = open(args.input_file, "r")
    except Exception:
        print("ERROR: Cannot open input file.")
        print_manual_and_exit()

    with infile:
        print("smiles")

        for line in infile:
            selfie = line.strip()

            if not selfie:
                continue

            if selfie.lower() == "selfies":
                continue

            if selfie.startswith('"') and selfie.endswith('"'):
                selfie = selfie[1:-1]

            total += 1

            try:
                smiles = sf.decoder(selfie)
            except Exception:
                failed += 1
                continue

            fixed = repair_molecule(smiles)

            if fixed:
                print(fixed)
                success += 1
            else:
                failed += 1

    print("\n===== Processing Summary =====", file=sys.stderr)
    print(f"Total SELFIES processed : {total}", file=sys.stderr)
    print(f"Successfully sanitized  : {success}", file=sys.stderr)
    print(f"Failed conversions      : {failed}", file=sys.stderr)
    print("================================\n", file=sys.stderr)


if __name__ == "__main__":
    main()
import sys
import argparse
import selfies as sf
from rdkit import Chem
from rdkit import RDLogger

RDLogger.DisableLog('rdApp.*')


def print_manual_and_exit():
    print(__doc__)
    sys.exit(1)


def repair_molecule(smiles):
    """
    Perform:
      1. Radical repair
      2. Safe thiol repair
      3. Full sanitization
    """
    try:
        mol = Chem.MolFromSmiles(smiles, sanitize=False)
        if mol is None:
            return None

        # -------------------------
        # 1️⃣ Radical repair
        # -------------------------
        for atom in mol.GetAtoms():
            if atom.GetNumRadicalElectrons() > 0:
                atom.SetNumRadicalElectrons(0)

        # Allow implicit hydrogens
        for atom in mol.GetAtoms():
            atom.SetNoImplicit(False)

        mol.UpdatePropertyCache(strict=False)

        # -------------------------
        # 2️⃣ Safe thiol repair
        # -------------------------
        for atom in mol.GetAtoms():
            if atom.GetAtomicNum() == 16:  # Sulfur
                if atom.GetFormalCharge() == 0:
                    explicit_valence = atom.GetExplicitValence()

                    # Neutral sulfur with valence 1 (e.g., O[S] or C[S])
                    if explicit_valence == 1:
                        atom.SetNumExplicitHs(atom.GetNumExplicitHs() + 1)
                        atom.SetNoImplicit(True)

        mol.UpdatePropertyCache(strict=False)

        # -------------------------
        # 3️⃣ Full sanitization
        # -------------------------
        Chem.SanitizeMol(mol)

        # Minimal canonical SMILES
        return Chem.MolToSmiles(mol, canonical=True)

    except Exception:
        return None


def main():
    if len(sys.argv) < 2:
        print_manual_and_exit()

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("input_file")

    try:
        args = parser.parse_args()
    except Exception:
        print_manual_and_exit()

    total = 0
    success = 0
    failed = 0

    try:
        infile = open(args.input_file, "r")
    except Exception:
        print("ERROR: Cannot open input file.")
        print_manual_and_exit()

    with infile:
        print("smiles")

        for line in infile:
            selfie = line.strip()

            if not selfie:
                continue

            if selfie.lower() == "selfies":
                continue

            if selfie.startswith('"') and selfie.endswith('"'):
                selfie = selfie[1:-1]

            total += 1

            try:
                smiles = sf.decoder(selfie)
            except Exception:
                failed += 1
                continue

            fixed = repair_molecule(smiles)

            if fixed:
                print(fixed)
                success += 1
            else:
                failed += 1

    print("\n===== Processing Summary =====", file=sys.stderr)
    print(f"Total SELFIES processed : {total}", file=sys.stderr)
    print(f"Successfully sanitized  : {success}", file=sys.stderr)
    print(f"Failed conversions      : {failed}", file=sys.stderr)
    print("================================\n", file=sys.stderr)


if __name__ == "__main__":
    main()