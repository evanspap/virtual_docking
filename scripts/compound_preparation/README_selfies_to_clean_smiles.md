# SELFIES → Clean SMILES

Author: Evangelos Papadopoulos
Version: 1.8.0
Date: 2026-02-11

---

## Overview

This tool converts AI-generated **SELFIES** strings into chemically sanitized **closed-shell SMILES** using RDKit.

The primary motivation was handling generative-model outputs that contained:

* Explicit radical carbons (e.g., `[C]`, `[CH]` with radical electrons)
* Under-specified valence states
* Invalid bonding states after decoding

The goal is **not to modify chemical topology**, but to:

* Remove true radical electrons
* Recompute implicit hydrogens
* Perform full RDKit sanitization

The script is designed for small libraries (~20–100 molecules).

---

## Why This Tool Was Needed

Generative AI models may output SELFIES that decode into SMILES with:

* Radical electrons
* Under-valent carbons
* Chemically unstable intermediates

Example problematic structure:

```
NCC1N=CCCC=CC[CH]OCC2=NCC1c1ccccc12
```

DataWarrior may display a radical dot because the carbon has:

* 2 bonds
* 1 hydrogen
* Valence = 3

This is chemically a radical species.

The script removes radical electrons and allows RDKit to recompute implicit hydrogens.

---

## Design Philosophy (v1.8.0)

Earlier versions attempted aggressive valence enforcement (C, N, O, S).

This caused potential corruption of:

* Sulfoxides (S=O)
* Sulfones
* Phosphates
* Charged ammonium species
* Hypervalent sulfur/phosphorus

Therefore, the final design philosophy is:

✔ Repair only true radical electrons
✔ Do NOT globally force valence rules
✔ Let RDKit recompute implicit hydrogens
✔ Preserve bonding topology

This makes the pipeline chemically safer.

---

## What the Script Does

1. Decode SELFIES → SMILES
2. Load molecule without strict sanitization
3. Remove radical electrons (`SetNumRadicalElectrons(0)`)
4. Allow implicit hydrogen recomputation
5. Run full RDKit `SanitizeMol`
6. Output canonical SMILES

---

## What the Script Does NOT Do

* It does not modify bond orders
* It does not fix incorrect connectivity
* It does not force carbon valence to 4 globally
* It does not alter sulfur/phosphorus valence states

If a molecule remains chemically invalid after radical removal,
then the generative model likely produced incorrect bonding topology.

---

## Usage

```bash
python selfies_to_clean_smiles.py input.selfies > output.smi
```

Output format:

```
smiles
SMILES_1
SMILES_2
...
```

Processing summary is printed to stderr.

---

## Example Workflow

```bash
# Extract SELFIES column from CSV
cut -d',' -f4 input.csv > input.selfies

# Convert to sanitized SMILES
python selfies_to_clean_smiles.py input.selfies > clean.smi
```

---

## Recommended Next Steps (Optional Enhancements)

For production pipelines, consider adding:

* Valence violation reporting
* Radical detection reporting
* Molecular weight filtering
* Lipinski rule filtering
* PAINS filtering
* Docking readiness checks

---

## Summary

This tool provides a conservative, chemically safe method for:

SELFIES → Radical-free, sanitized SMILES

without introducing topology distortions.

It is suitable for generative chemistry post-processing pipelines.

License: MIT License