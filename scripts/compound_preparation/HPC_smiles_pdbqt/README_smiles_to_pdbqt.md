# SMILES → 3D SDF → PDBQT  
## Ligand Preparation Pipeline (RDKit + OpenBabel, SLURM/HPC)

This repository documents a **practical, tested pipeline** for converting large SMILES libraries
into **PDBQT ligand files** suitable for downstream use.

Scope of this repository:
-  ligand preparation
- RDKit is used for 3D coordinate generation
- PDBQT generation is done with **OpenBabel**

---

## 1. Software Stack (What Is Actually Used)

### Required tools
- **RDKit** – SMILES → 3D SDF
- **OpenBabel** – SDF → PDBQT
- **SLURM** – job scheduling on HPC

---

## 2. Conda Environments

Two independent environments are recommended.

### RDKit environment (3D generation only)
```bash
conda create -n rdkit_env -c conda-forge python=3.10 rdkit
conda activate rdkit_env
```

### OpenBabel environment (PDBQT conversion)
```bash
conda create -n openbabel -c conda-forge python=3.10 openbabel
conda activate openbabel
```

Keeping these environments separate avoids dependency conflicts.

---

## 3. Directory Structure

```
project_root/
│
├── compounds/
│   ├── library.smi
│   ├── SDF_Structures_3D/
│   │   └── mol_XXXX_3d.sdf
│   └── PDBQT_OBABEL/
│       └── mol_XXXX_3d.pdbqt
│
├── scripts/
│   ├── smiles_line_to_3d.py
│   └── run_smiles_to_pdbqt.sbatch
│
│
└── README.md
```

---

## 4. Script: `smiles_line_to_3d.py`

### Purpose
Convert **one SMILES line** into a **3D SDF file** using RDKit.

### Usage
```bash
conda activate rdkit_env
python smiles_line_to_3d.py <index> "<SMILES>" <output.sdf>
```

### Example
```bash
python smiles_line_to_3d.py 1 "CCO" mol_1_3d.sdf
```

### What the script does
- Parses SMILES
- Adds hydrogens
- Generates 3D coordinates (ETKDG)
- Optimizes geometry (MMFF)
- Writes a single-molecule SDF

---

## 5. Script: `run_smiles_to_pdbqt.sbatch`

This is the **main production script** used on the HPC cluster.

### Purpose
Process a full SMILES library and generate:
- 3D SDF files
- Corresponding PDBQT ligand files

### Invocation
```bash
sbatch run_smiles_to_pdbqt.sbatch library.smi
```

### What happens internally
1. Reads SMILES file line by line
2. Generates 3D SDF files using RDKit
3. Converts each SDF to PDBQT using OpenBabel
4. Runs in parallel on allocated SLURM cores

⚠️ Currently both steps are handled in **one script**.

---

## 6. OpenBabel Conversion (Exact Command Used)

The following command is used for each ligand:

```bash
obabel input.sdf -O output.pdbqt --partialcharge gasteiger
```

This produces:
- Correct PDBQT atom types
- Gasteiger partial charges
- Rotatable bond definitions

---

## 7. Monitoring Progress

### Count generated 3D SDF files
```bash
find SDF_Structures_3D -type f -name "mol_*_3d.sdf" | wc -l
```

### Count generated PDBQT files
```bash
find PDBQT_OBABEL -type f -name "mol_*_3d.pdbqt" | wc -l
```

### Check SLURM job status
```bash
squeue -u $USER
```

---

## 8. Output Validation

### Inspect a generated PDBQT
```bash
head PDBQT_OBABEL/mol_1_3d.pdbqt
```

Expected contents:
- ROOT / BRANCH records
- ATOM records
- Partial charges

---

## 9. Design Decisions

- OpenBabel chosen for PDBQT robustness
- RDKit isolated to 3D coordinate generation
- File-based workflow for easy restarts
- One-ligand-per-file for fault tolerance

---

## 10. Planned Improvements

- Split pipeline into two SLURM jobs:
  1. SMILES → 3D SDF
  2. 3D SDF → PDBQT
- Add checkpointing between stages
- Optional ligand filtering

---

## 11. Summary

This repository documents a **clean, reproducible ligand preparation pipeline**:

- ✔ Large SMILES libraries
- ✔ HPC / SLURM compatible
- ✔ RDKit + OpenBabel only
- ✔ No docking assumptions
- ✔ No Meeko dependency
