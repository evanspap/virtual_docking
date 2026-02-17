#!/bin/bash
#SBATCH -J mpi4py_test
#SBATCH -p debug-28core
#SBATCH -N 1
#SBATCH --ntasks-per-node=2
#SBATCH -t 00:05:00
#SBATCH -o mpi4py_test_%j.out
#SBATCH -e mpi4py_test_%j.err

module purge
module load slurm
module load mpi4py

echo "Job $SLURM_JOBID running on $SLURM_NODELIST with $SLURM_NTASKS tasks"

mpirun -np $SLURM_NTASKS python -u mpi_hello.py

