#!/usr/bin/env python3
import sys
from rdkit import Chem
from rdkit.Chem import AllChem

def main():
    if len(sys.argv) != 4:
        print("usage: smiles_line_to_3d.py <idx> <smiles> <out.sdf>", file=sys.stderr)
        return 2

    idx = int(sys.argv[1])
    smi = sys.argv[2]
    out_sdf = sys.argv[3]

    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        print(f"[{idx}] RDKit parse failed", file=sys.stderr)
        return 3

    mol = Chem.AddHs(mol)

    params = AllChem.ETKDGv3()
    params.randomSeed = idx % 2147483647
    params.useRandomCoords = True

    if AllChem.EmbedMolecule(mol, params) != 0:
        print(f"[{idx}] Embed failed", file=sys.stderr)
        return 4

    try:
        if AllChem.MMFFHasAllMoleculeParams(mol):
            AllChem.MMFFOptimizeMolecule(mol, mmffVariant="MMFF94s", maxIters=2000)
        else:
            AllChem.UFFOptimizeMolecule(mol, maxIters=2000)
    except Exception as e:
        print(f"[{idx}] Minimization failed: {e}", file=sys.stderr)
        return 5

    mol.SetProp("_Name", f"mol_{idx}")
    mol.SetProp("SMILES", smi)

    w = Chem.SDWriter(out_sdf)
    w.write(mol)
    w.close()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
