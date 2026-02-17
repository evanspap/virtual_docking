#!/bin/bash
#SBATCH -J template_p1_docktype
#SBATCH -p large-28core
#SBATCH -N 72
#SBATCH --ntasks-per-node=28
#SBATCH -t 08:00:00
#SBATCH -o logs/%x_%j.out
#SBATCH -e logs/%x_%j.err

# Clean environment
module purge
module load slurm
module load openmpi
module load mpi4py
module load autodock-vina/1.2.5

export OMP_NUM_THREADS=1
cd /gpfs/scratch/epapadopoulo/mmsegs_pockets/docking/setup/runs/template/p1_docktype:

# Use mpirun instead of srun
mpirun -np ${SLURM_NTASKS} python -u /gpfs/scratch/epapadopoulo/mmsegs_pockets/docking/scripts/mpi_batched_runner.py \
    --input input.txt --batch 30

