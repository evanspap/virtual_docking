#!/bin/bash
# ----------------------------------------------------------
# Script: run_template_cmdfile_mpirun.sbatch
# Author: Evangelos Papadopoulos
# Date: 2026-01-22
# Version: 1.2
#
# Title:
#   Run a command-file (one command per line) using MPI ranks.
#
# Summary:
#   SLURM sbatch template that launches an mpi4py-based dispatcher.
#   Each MPI rank executes docking commands from a cmd file (one per line).
#
#   Production-safe HPC notes:
#   - Avoid `set -u`: non-interactive batch shells often have unset variables (e.g., PS1).
#   - Avoid `module purge`: can trigger conda/module deactivation issues on some clusters.
#   - Unload `openbabel` explicitly if present: it can bring conda/env side effects.
#
# Usage:
#   # After placeholders are substituted by setupRun_simplified.sh:
#   sbatch <generated sbatch file>
#
# Expected in the same directory (run directory):
#   - mpi_run_cmdfile.py
#   - CMD_FILE_PLACEHOLDER  (cmd filename, e.g. input_*.cmd)
#
# Produces:
#   - logs/<jobname>_<jobid>.out
#   - logs/<jobname>_<jobid>.err
#
# The cmd file lines may include shell operators (&&, redirects, etc.).
#
# Placeholders to be substituted:
#   PARTITION_PLACEHOLDER, NNODES_PLACEHOLDER, TPN_PLACEHOLDER,
#   TIME_PLACEHOLDER, CMD_FILE_PLACEHOLDER
#
# Root Folder Definition (context)
# --------------------------------
# This sbatch file is generated from:
#   <root_folder>/scripts/run_template_cmdfile_mpirun.sbatch
# where <root_folder> is the docking pipeline root (see setupRun_simplified.sh).
#
# Runtime Working Directory
# -------------------------
# The generated sbatch file is placed in the same directory as the cmd file.
# This template anchors CMD_FILE to the directory of the sbatch script itself,
# so it works even if `sbatch` is invoked from a different directory.
# ----------------------------------------------------------

#SBATCH -J vina_CMDNAME_PLACEHOLDER
#SBATCH -o logs/%x_%j.out
#SBATCH -e logs/%x_%j.err
#SBATCH --partition=PARTITION_PLACEHOLDER
#SBATCH --nodes=NNODES_PLACEHOLDER
#SBATCH --ntasks-per-node=TPN_PLACEHOLDER
#SBATCH --time=TIME_PLACEHOLDER
#SBATCH --exclusive

# IMPORTANT: do not use `-u` here (nounset)
set -eo pipefail

# Ensure the SLURM log directory exists (required by #SBATCH -o/-e paths)
mkdir -p logs

# Absolute cmd-file path, anchored to the directory where this sbatch script lives.
# This prevents failures when `sbatch` is invoked from outside the run directory.

# Always anchor to submission directory (SLURM-safe)
cd "${SLURM_SUBMIT_DIR}"

CMD_FILE="${SLURM_SUBMIT_DIR}/CMD_FILE_PLACEHOLDER"


echo "Start: $(date)"
echo "Host:  $(hostname)"
echo "PWD:   $(pwd)"
echo "CMD:   ${CMD_FILE}"
echo "NODES=${SLURM_JOB_NUM_NODES} NTASKS=${SLURM_NTASKS} TPN=${SLURM_NTASKS_PER_NODE}"

# Environment setup
# -----------------
# Do NOT module purge; instead unload known-conflicting modules if needed.
module unload openbabel >/dev/null 2>&1 || true

module load slurm
module load openmpi
module load mpi4py
module load autodock-vina/1.2.5

# Prevent OpenMP oversubscription (Vina uses --cpu 1 in cmd lines)
export OMP_NUM_THREADS=1

# Safety checks
test -s "${CMD_FILE}" || { echo "ERROR: missing/empty cmd file: ${CMD_FILE}"; exit 2; }
test -f "mpi_run_cmdfile.py" || { echo "ERROR: missing mpi_run_cmdfile.py in $(pwd)"; exit 2; }

echo "vina:   $(which vina || true)"
echo "python: $(which python || true)"
echo "mpirun: $(which mpirun || true)"

# Launch distributed execution
# CRITICAL: --bind-to core and --map-by ppr:${SLURM_NTASKS_PER_NODE}:node ensure MPI ranks
# are properly distributed across ALL allocated nodes (not just the first node).
# This was the bug in the simplified version: without these directives, all 224 processes
# would try to start on the submission node, leaving other nodes idle.
mpirun -np "${SLURM_NTASKS}" --bind-to core --map-by "ppr:${SLURM_NTASKS_PER_NODE}:node" \
  python -m mpi4py mpi_run_cmdfile.py "${CMD_FILE}"

echo "End: $(date)"

