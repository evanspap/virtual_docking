# Docking Run Setup (SLURM + MPI)

## Overview

This document describes the **general sequence** used to run large-scale AutoDock Vina docking on an HPC system using **SLURM** + **MPI (mpi4py)**.

### Quick Summary Overview

#### A. Target Preparation (Receptor Setup)

**Step 1:** Prepare the **receptor PDBQT** file and create the **Vina `.conf`** configuration file.

The `.conf` file defines:
- Path to the receptor PDBQT file
- Docking box center coordinates (`center_x`, `center_y`, `center_z`)
- Docking box size (`size_x`, `size_y`, `size_z`)
- AutoDock Vina parameters (exhaustiveness, num_modes, etc.)

**Example structure:**
```
conf/<project>/<target>.conf
```

See the [Receptor Configuration Files](#receptor-configuration-files-conf) section for detailed setup.

---

#### B. Compound Preparation (SMILES → PDBQT)

Convert ligands from SMILES strings to PDBQT format suitable for docking.

Reference: [(Readme_smiles_pdbqt)](https://github.com/evanspap/virtual_docking/blob/main/smiles_pdbqt/README_smiles_to_pdbqt.md "Smiles to pdbqt")

**Option B1: Single-Node (Local/Laptop)**
For small datasets or local development:

```bash
python scripts/compound_preparation/run_smiles_to_pdbqt_single_node.py <input.smi>
```

- Converts SMILES strings to 3D SDF structures (RDKit + MMFF/UFF)
- Converts SDF to PDBQT with Gasteiger charges (Open Babel)
- **Best for:** Small datasets (< 10,000 compounds), single processor, local testing
- **Outputs:** `SDF_Structures_3D/`, `PDBQT_OBABEL/`, `3d_success.list`, `pdbqt_success.list`

**Option B2: HPC Multi-Node (SLURM + Parallel)**
For large compound libraries on HPC clusters:

```bash
sbatch scripts/compound_preparation/run_smiles_to_pdbqt.sbatch <input.smi>
```

- Parallelized conversion using all available CPU cores
- Efficient handling of large datasets (10K - 1M+ compounds)
- **Best for:** Large-scale production runs on HPC systems
- **Resources:** Configurable via `#SBATCH` directives (CPUs, memory, time)
- **Outputs:** Same as single-node version


---

#### C. Docking Command Generation

Create a **`param_file`** with docking parameters, then generate the command file.

**Step 1:** Create a parameter file (`param_file`) containing:
- Paths to receptor `.conf` files
- Input ligand directory
- Output directory
- Naming conventions
- Vina-specific parameters

**Step 2:** Generate the **command file** `input_*.cmd` (one docking command per ligand):

```bash
python scripts/vina_commands_v1.3.py <param_file> > input_<...>.cmd
```

---

#### D. Docking Execution

Execute the docking commands. Choose based on your environment:

**Option D1: Single-Node Docking (Local/Laptop)**
Execute docking commands sequentially on a single machine:

```bash
python scripts/docking_execution/execute_commands.py <input_*.cmd> <output.log> [--verbose]
```

- Reads command file and executes each docking command sequentially
- Captures all output and errors to a single log file
- **Best for:** Small docking runs (< 1,000 ligands), local testing, laptops
- **Outputs:** Docking results + execution summary in log file

**Option D2: HPC Multi-Node Docking (SLURM + MPI)**
Distribute docking across many nodes and cores:

**Step 1:** Generate the **SLURM sbatch** job file from the cmd file:

```bash
./scripts/setupRun_simplified.sh <root> <partition> <nodes> <tpn> <time> <input_cmd_file>
```

This creates `run_cmdfile_mpirun.sbatch` in the same run directory.

**Step 2:** Launch the docking run on SLURM:

```bash
sbatch run_cmdfile_mpirun.sbatch
```

- Uses MPI-based dispatcher (`mpi_batched_runner.py`) for dynamic load balancing
- Automatically batches commands to reduce scheduling overhead
- **Best for:** Large docking campaigns (10K - 1M+ ligands) on HPC systems
- **Resources:** Distributed across multiple nodes and cores via SLURM

---

#### E. Results Analysis

Once docking completes, parse the docking output files and create a summary CSV with binding affinity scores and top-ranked poses:

```bash
python ./scripts/parse_vina_out_multi.py --header --top 2 ./output/<project>/<target>/*.out > ./output/<project>/<target>_results.csv
```

This script reads all `.out` files from the docking output directory and extracts:
- Binding affinity scores
- Top N poses (e.g., `--top 2` for the best 2 poses)
- Ligand identifiers
- RMSD values and other pose metrics
- **Works with both:** single-node and HPC results

---

## Scope

This guide covers:

* Folder and project layout
* Definition of the **root folder**
* Receptor configuration (`.conf` files)
* **Parameter file** conventions for command generation
* Command-file generation (`input_*.cmd`)
* Run setup using `setupRun_simplified.sh`
* SLURM `sbatch` generation and execution
* MPI execution model
* Monitoring and logs
* Chunking strategy (current state and planned improvement)

---

## Terminology

| Term              | Meaning                                                                                                               |
| ----------------- | --------------------------------------------------------------------------------------------------------------------- |
| **Root folder**   | Top-level docking project directory (contains `scripts/`, `conf/`, `output/`, `runs/`)                                |
| **Run directory** | Folder for one specific docking campaign (contains `param_file`, `input_*.cmd`, `run_cmdfile_mpirun.sbatch`, `logs/`) |
| **Vina conf**     | Target config file (`.conf`) defining receptor, docking box, and Vina knobs                                           |
| **Param file**    | Generator config used to *produce* the command file (not required at runtime once cmd file exists)                    |
| **Command file**  | Text file with **one docking command per line** (`input_*.cmd`)                                                       |
| **Sbatch file**   | SLURM submission script created by `setupRun_simplified.sh` (`run_cmdfile_mpirun.sbatch`)                             |
| **Dispatcher**    | MPI Python script that distributes commands to ranks (e.g., `mpi_run_cmdfile.py`)                                     |
| **Chunking**      | Grouping multiple docking commands per MPI rank                                                                       |

---

## Key Files and I/O (what reads what, what writes what)

### `conf/<project>/<target>.conf`

* **Input:** receptor PDBQT path; docking box (`center_*`, `size_*`)
* **Used by:** every command line in `input_*.cmd`
* **Output:** none (configuration only)

### `runs/<project>/<library>/<target>/param_file`

* **Input:** paths (conf, ligands), output directory, naming, Vina knobs used by generator
* **Used by:** `scripts/vina_commands_v1.3.py`
* **Output:** none directly (drives cmd generation)

### `runs/<project>/<library>/<target>/input_<...>.cmd`

* **Generated by:** `python scripts/vina_commands_v1.3.py <param_file> > input_*.cmd`
* **Read by:** `mpi_run_cmdfile.py` (via `mpirun` inside sbatch)
* **Writes (per ligand):**

  * `<OUTPUT_DIR>/<ligand>.out` (stdout / table / timestamps)
  * `<OUTPUT_DIR>/<ligand>.err` (stderr)
  * `<OUTPUT_DIR>/<ligand>.pdbqt` (poses)

### `runs/<project>/<library>/<target>/run_cmdfile_mpirun.sbatch`

* **Generated by:** `./scripts/setupRun_simplified.sh ... <input_cmd_file>`
* **Read by:** SLURM (`sbatch`)
* **Writes:** SLURM logs under `runs/.../logs/`

### `runs/<project>/<library>/<target>/logs/`

* **Written by:** SLURM (`#SBATCH -o/-e`)
* **Contains:** job-level stdout/stderr (MPI runner messages, environment setup, etc.)

----------------- | ------------------------------------------------------------------------------------------ |
| **Root folder**   | Top-level docking project directory (contains `scripts/`, `output/`, `runs/`, etc.)        |
| **Run directory** | Folder for one specific docking campaign (contains `input_*.cmd`, `run_*.sbatch`, `logs/`) |
| **Command file**  | Text file with **one docking command per line**                                            |
| **Dispatcher**    | MPI Python script that distributes commands to ranks                                       |
| **Chunking**      | Grouping multiple docking commands per MPI rank                                            |

---

## Root Folder Definition

The **root folder** is the base of the docking pipeline. All scripts, templates, and paths are defined relative to it.

Example:

```
/gpfs/scratch/<user>/mmsegs_pockets/docking/
```

Expected structure:

```
docking/
├── scripts/
│   ├── vina_commands_v1.3.py
│   ├── setupRun_simplified.sh
│   ├── run_template_cmdfile_mpirun.sbatch
│   ├── mpi_run_cmdfile.py
│   ├── mpi_batched_runner.py        # legacy (batch-size supported)
│   └── parse_vina_out_multi.py      # analysis
├── conf/
├── compounds/
├── output/
└── runs/
```

---

## Receptor Configuration Files (`.conf`)

Each docking target requires a Vina configuration file, typically stored under:

```
conf/<project>/<target>.conf
```

Typical contents:

```
receptor = receptor.pdbqt
center_x = ...
center_y = ...
center_z = ...
size_x   = ...
size_y   = ...
size_z   = ...
exhaustiveness = 32
num_modes = 4
```

These `.conf` files are referenced directly in the command file (`input_*.cmd`).

---

## Parameter File (for command generation)

The `param_file` is the **single source of truth** for *command generation*.
It should capture all paths and knobs needed to produce a correct `input_*.cmd`.

**Important:** The param file is **not required at runtime** once `input_*.cmd` exists.

### Recommended location

Store the param file in the run directory:

```
runs/<project>/<library>/<target>/param_file
```

### Minimum required concepts (must be present)

* **Vina config path** (`.conf`) for the target docking box
* **Ligand PDBQT directory** (or a ligand list)
* **Output directory** (where `.out/.err/.pdbqt` will be written)
* **Naming convention / run tag** (so output files are deterministic)
* **Vina knobs** not captured in `.conf` (if applicable)

### param_file Minimal template (example)

```ini
indir=/gpfs/scratch/epapadopoulo/mmsegs_pockets/docking/compounds/nci_sdf/pdbqt_good_new
outdir=/gpfs/scratch/epapadopoulo/mmsegs_pockets/docking/output/template/p1_300k_nci_r1/
trg=template_p1
cfg=/gpfs/scratch/epapadopoulo/mmsegs_pockets/docking/conf/template_p1.conf
exhaustiveness=8
num_modes=4

```

> Note: the exact keys depend on the generator version you use. The template above documents the required *concepts*.

---

## Generating the Command File (`input_*.cmd`)

Generate the command file from a param file:

```bash
python /gpfs/scratch/<user>/mmsegs_pockets/docking/scripts/vina_commands_v1.3.py \
  /gpfs/scratch/<user>/mmsegs_pockets/docking/runs/<project>/<library>/<target>/param_file \
  > /gpfs/scratch/<user>/mmsegs_pockets/docking/runs/<project>/<library>/<target>/input_<library>_<target>.cmd
```

### Sanity checks

```bash
wc -l input_<library>_<target>.cmd
head input_<library>_<target>.cmd
```

### What the cmd file *must* do

Each line should be a **fully self-contained** docking job that writes per-ligand outputs:

* `*.out` (includes `Start:` / `End:` timestamps)
* `*.err`
* `*.pdbqt`

--- (`input_*.cmd`)

### Goal

Produce a file containing **one complete shell command per line**, typically including:

* `echo "Start: $(date)" >> <ligand>.out`
* `vina --config ... --ligand ... --out ... --cpu 1 ... >> <ligand>.out 2> <ligand>.err`
* `echo "End: $(date)" >> <ligand>.out`

This makes parsing easier later (duration estimation) and ensures each ligand has its own logs.

### Generator script

Common generator:

* `scripts/vina_commands_v1.3.py`

### Recommended run pattern (param → cmd)

From the root folder (or anywhere), generate the command file using a param file:

```bash
python /gpfs/scratch/<user>/mmsegs_pockets/docking/scripts/vina_commands_v1.3.py \
  /gpfs/scratch/<user>/mmsegs_pockets/docking/runs/<project>/<library>/<target>/param_file \
  > /gpfs/scratch/<user>/mmsegs_pockets/docking/runs/<project>/<library>/<target>/input_<library>_<target>.cmd
```

### Sanity checks

```bash
wc -l input_<library>_<target>.cmd
head -n 2 input_<library>_<target>.cmd
```

---

## Generating the Run Directory (SLURM sbatch)

Use:

```bash
scripts/setupRun_simplified.sh \
  <root_folder> \
  <partition> \
  <nodes> \
  <tasks_per_node> \
  <walltime> \
  <input_cmd_file>
```

Example:

```bash
./scripts/setupRun_simplified.sh \
  /gpfs/scratch/<user>/mmsegs_pockets/docking \
  long-28core 4 28 48:00:00 \
  /gpfs/scratch/<user>/mmsegs_pockets/docking/runs/wgan/GA/input_GA_2zht.cmd
```

This generates in the **run directory** (same directory as the cmd file):

* `run_cmdfile_mpirun.sbatch`
* a local copy of `mpi_run_cmdfile.py`
* `logs/`

---

## SLURM Job Script

Key properties of the generated `sbatch` file:

* Submit from the run directory
* Uses:

  ```
  mpirun -np $SLURM_NTASKS python -m mpi4py mpi_run_cmdfile.py input_*.cmd
  ```
* Loads modules, typically:

  * slurm
  * openmpi
  * mpi4py
  * autodock-vina
* Good practice:

  * `mkdir -p logs`
  * `export OMP_NUM_THREADS=1`

---

## Submitting and Monitoring

Submit:

```bash
cd <run_dir>
sbatch run_cmdfile_mpirun.sbatch
```

Monitor:

```bash
squeue -u $USER
```

Inspect SLURM logs:

```bash
ls -lt logs | head

tail -n 80 logs/vina_cmdfile_<JOBID>.out

tail -n 80 logs/vina_cmdfile_<JOBID>.err
```

Validate per-ligand output activity:

```bash
find /gpfs/scratch/<user>/mmsegs_pockets/docking/output/<project>/<library>/<target> \
  -name "*.out" -mmin -5 | head
```

---

## Chunking (Important Note)

### Why chunking matters

For large runs (e.g., 10+ nodes / 280+ ranks), chunking:

* reduces dispatch overhead
* reduces filesystem pressure
* improves throughput stability

### Current state

* The legacy runner (`mpi_batched_runner.py`) supports `--batch N`.
* The simplified dispatcher (`mpi_run_cmdfile.py`) typically executes one command per rank in a strided pattern.

### Recommended improvement

Introduce a single runtime knob (e.g., `--chunk-size N`) in the dispatcher and pass it from the sbatch script.

This should be treated as a **runtime scheduling parameter**, not a setup parameter.

---

## Author

Evangelos Papadopoulos
Dana-Farber Cancer Institute / HMS (Harvard Medical School)/ Stony Brook University
