#!/bin/bash
# ----------------------------------------------------------
# Script: setupRun_simplified.sh
# Author: Evangelos Papadopoulos
# Date: 2026-01-22
# Version: 1.3
#
# Title:
#   Setup simplified MPI SLURM sbatch run for an existing Vina command file.
#
# Summary:
#   Prepares a production-safe SLURM MPI run for an already-generated
#   AutoDock Vina command list (cmd file: input_*.cmd).
#
#   IMPORTANT:
#   This script DOES NOT generate docking commands.
#   It assumes the command file already exists (one command per line),
#   typically produced by:
#       python vina_commands_v*.py
#
#   This script performs ONLY orchestration and wiring:
#     - infers run_dir = dirname(cmd_file)
#     - copies mpi_run_cmdfile.py into run_dir
#     - generates an sbatch file in run_dir from a template
#       via placeholder substitution
#     - names the sbatch file to include the identifier after `input_`
#       so each sbatch clearly corresponds to its cmd file
#     - injects the same identifier into the SLURM job name (-J),
#       making logs/%x_%j.out self-descriptive
#
# Usage:
#   ./scripts/setupRun_simplified.sh \
#       <scripts_dir> <partition> <nodes> <tasks_per_node> <time> <cmd_file> [--dry-run]
#
# Example:
#   ./scripts/setupRun_simplified.sh \
#       /gpfs/projects/DengYasarGroup/GENOVA/Docking_BACE1/scripts \
#       long-28core 8 28 48:00:00 \
#       /gpfs/projects/DengYasarGroup/GENOVA/Docking_BACE1/output/wgan/GA/input_GA_B1_2ZHR_aln6UJ0_3.cmd
#
# Scripts Directory Definition
# ----------------------------
# <scripts_dir> is the absolute path to the directory containing shared
# pipeline helper scripts and templates. It MUST contain:
#
#   scripts/
#     ├─ run_template_cmdfile_mpirun.sbatch
#     └─ mpi_run_cmdfile.py
#
# Output Location Policy
# ----------------------
#   run_dir = dirname(<cmd_file>)
#
#   All generated artifacts are placed directly in run_dir:
#     - mpi_run_cmdfile.py
#     - run_cmdfile_<RUN_ID>.sbatch
#     - logs/
#
# Rationale:
#   Co-locating the cmd file, sbatch file, MPI runner, and logs ensures:
#     - correct and predictable execution context
#     - no reliance on submission working directory
#     - clean, self-contained, reproducible docking runs
#
# Safety & HPC Notes
# ------------------
#   - Safe for non-interactive SLURM batch environments
#   - No conda activation/deactivation is attempted here
#   - Environment handling (modules, OpenMP, conflicts) is delegated
#     entirely to the sbatch template
#   - Designed to work correctly even when `sbatch` is invoked from
#     outside the run directory
#
# ----------------------------------------------------------



set -euo pipefail

if [ $# -lt 6 ]; then
  echo "Usage:"
  echo "  $0 <scripts_dir> <partition> <nodes> <tasks_per_node> <time> <cmd_file> [--dry-run]"
  exit 1
fi

SCRIPTS_DIR=$1
PARTITION=$2
NODES=$3
TPN=$4
TIME=$5
CMD_FILE=$6
DRYRUN=false

if [ "${7:-}" == "--dry-run" ]; then
  DRYRUN=true
fi

# Validate inputs
if [ ! -f "$CMD_FILE" ]; then
  echo "ERROR: cmd file not found: $CMD_FILE"
  exit 2
fi

TEMPLATE_SBATCH="$SCRIPTS_DIR/run_template_cmdfile_mpirun.sbatch"
SRC_RUNNER="$SCRIPTS_DIR/mpi_run_cmdfile.py"

if [ ! -f "$TEMPLATE_SBATCH" ]; then
  echo "ERROR: missing sbatch template: $TEMPLATE_SBATCH"
  exit 3
fi

if [ ! -f "$SRC_RUNNER" ]; then
  echo "ERROR: missing mpi runner: $SRC_RUNNER"
  exit 4
fi

# Resolve run directory and identifiers
RUN_DIR="$(cd "$(dirname "$CMD_FILE")" && pwd)"
CMD_BASENAME="$(basename "$CMD_FILE")"

# Extract identifier after 'input_' and before '.cmd'
CMD_ID="${CMD_BASENAME#input_}"
CMD_ID="${CMD_ID%.cmd}"

SBATCH_NAME="run_cmdfile_${CMD_ID}.sbatch"
DST_SBATCH="$RUN_DIR/$SBATCH_NAME"
DST_RUNNER="$RUN_DIR/mpi_run_cmdfile.py"

JOBNAME="vina_${CMD_ID}"

# Commands
CMD_MKLOGS="mkdir -p \"$RUN_DIR/logs\""
CMD_CPRUNNER="cp \"$SRC_RUNNER\" \"$DST_RUNNER\""
CMD_CPSBATCH="cp \"$TEMPLATE_SBATCH\" \"$DST_SBATCH\""

CMD_SED_SBATCH="sed -i \
  -e \"s|PARTITION_PLACEHOLDER|$PARTITION|g\" \
  -e \"s|NNODES_PLACEHOLDER|$NODES|g\" \
  -e \"s|TPN_PLACEHOLDER|$TPN|g\" \
  -e \"s|TIME_PLACEHOLDER|$TIME|g\" \
  -e \"s|CMD_FILE_PLACEHOLDER|$CMD_BASENAME|g\" \
  -e \"s|CMDNAME_PLACEHOLDER|$CMD_ID|g\" \
  \"$DST_SBATCH\""

if $DRYRUN; then
  echo "[DRY-RUN] $CMD_MKLOGS"
  echo "[DRY-RUN] $CMD_CPRUNNER"
  echo "[DRY-RUN] $CMD_CPSBATCH"
  echo "[DRY-RUN] $CMD_SED_SBATCH"
  echo
  echo "[DRY-RUN] Submission:"
  echo "  cd \"$RUN_DIR\""
  echo "  sbatch $SBATCH_NAME"
else
  eval "$CMD_MKLOGS"
  eval "$CMD_CPRUNNER"
  chmod u+x "$DST_RUNNER"
  eval "$CMD_CPSBATCH"
  eval "$CMD_SED_SBATCH"

  echo "Prepared:"
  echo "  Run dir: $RUN_DIR"
  echo "  Cmd:     $CMD_BASENAME"
  echo "  Runner:  $DST_RUNNER"
  echo "  Sbatch:  $DST_SBATCH"
  echo "  JobName: $JOBNAME"
  echo "  Logs:    $RUN_DIR/logs/"
  echo
  echo "Run:"
  echo "  cd \"$RUN_DIR\""
  echo "  sbatch $SBATCH_NAME"
fi
