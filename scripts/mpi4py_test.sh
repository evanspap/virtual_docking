#!/bin/bash
# Version: 1.1
# Date: 2025-09-22
#
# Description:
#   Runs a quick mpi4py hello world test in the debug partition.
#   Requests 1 node with 2 tasks for 5 minutes, runs mpirun,
#   and prints results directly to stdout.
#
# Usage:
#   bash mpi4py_live_test.sh
#

module purge
module load slurm
module load mpi4py

# Request node and run job in one go
srun -p debug-28core -N 1 --ntasks-per-node=2 -t 00:05:00 \
    mpirun -np 2 python -u - <<'PYCODE'
from mpi4py import MPI
comm = MPI.COMM_WORLD
print(f"Hello from rank {comm.Get_rank()} of {comm.Get_size()} on {MPI.Get_processor_name()}")
PYCODE

