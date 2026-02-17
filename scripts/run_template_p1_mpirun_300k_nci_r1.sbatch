#!/bin/bash
#
#========================================================================
# Author        : Evangelos Papadopoulos
# Version       : 1.0
# Date          : 2025-09-22
#
# Description:
#   Generic SLURM batch script template to run AutoDock Vina docking jobs
#   in parallel using MPI (mpi4py). It supports substitution of job name,
#   partition, node count, tasks per node, runtime, working directory,
#   input file, and batch size. The mpi_batched_runner.py script handles
#   distributing ligand docking tasks across workers.
#
# Usage:
#   sbatch run_template.sbatch
#
# Example:
#   sbatch run_carm1_p1_mpirun_300k_nci_r1.sbatch
#
# Notes:
#   - This script assumes you have loaded the required modules:
#       module load slurm
#       module load autodock-vina/1.2.5
#   - mpi4py must also be available via modules (or installed system-wide).
#   - OMP_NUM_THREADS is set to 1 to prevent OpenMP oversubscription.
# ========================================================================

#SBATCH -J template_p1_300k_nci_r1
#SBATCH -p PARTITION_PLACEHOLDER
#SBATCH -N NNODES_PLACEHOLDER
#SBATCH --ntasks-per-node=TPN_PLACEHOLDER
#SBATCH -t TIME_PLACEHOLDER
#SBATCH -o logs/%x_%j.out
#SBATCH -e logs/%x_%j.err

# --- Environment setup ---
module purge
module load slurm
module load mpi4py
module load autodock-vina/1.2.5

export OMP_NUM_THREADS=1
cd /gpfs/scratch/epapadopoulo/mmsegs_pockets/docking/runs/template/p1_300k_nci_r1

# --- Calculate number of tasks ---
NTASKS=$(( SLURM_NNODES * SLURM_NTASKS_PER_NODE ))

# --- Run ---
echo "Running: mpirun -np ${NTASKS} python -u mpi_batched_runner.py --input INPUTFILE_PLACEHOLDER --batch BATCHSIZE_PLACEHOLDER"

mpirun -np ${NTASKS} python -u /gpfs/scratch/epapadopoulo/mmsegs_pockets/docking/scripts/mpi_batched_runner.py\
    --input input.txt --batch 15

