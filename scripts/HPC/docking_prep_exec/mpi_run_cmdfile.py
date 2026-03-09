#!/usr/bin/env python3
# ----------------------------------------------------------
# Script: mpi_run_cmdfile.py
# Author: Evangelos Papadopoulos
# Date: 2026-01-19
# Version: 1.0
#
# Title:
#   MPI dispatcher for command-file execution.
#
# Summary:
#   Reads a command file (one shell command per line) and distributes
#   execution across MPI ranks using strided assignment:
#       rank r runs lines r, r+size, r+2*size, ...
#
# Usage:
#   python -m mpi4py mpi_run_cmdfile.py <cmd_file>
#
# Example:
#   mpirun -np 4 python -m mpi4py mpi_run_cmdfile.py input_GA_2zht.cmd
#
# Documentation:
#   - Each line is executed via /bin/bash ("shell=True"), so the line may contain:
#       redirects (>, >>, 2>), &&, variables, subshells $(...), etc.
#   - Blank lines are ignored.
#   - Exit codes are reported per command; non-zero does NOT abort the whole run
#     (so a single ligand failure does not kill the full batch).
# ----------------------------------------------------------

import sys
import subprocess
from mpi4py import MPI


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python -m mpi4py mpi_run_cmdfile.py <cmd_file>", flush=True)
        return 2

    cmd_file = sys.argv[1]
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Read commands
    try:
        with open(cmd_file, "r", encoding="utf-8") as f:
            cmds = [ln.rstrip("\n") for ln in f if ln.strip()]
    except FileNotFoundError:
        if rank == 0:
            print(f"ERROR: cmd_file not found: {cmd_file}", flush=True)
        return 2

    n = len(cmds)
    if rank == 0:
        print(f"[MPI] ranks={size} commands={n} file={cmd_file}", flush=True)

    failures = 0

    for idx in range(rank, n, size):
        cmd = cmds[idx]
        tag = f"[rank {rank}] line {idx+1}/{n}"
        print(f"{tag} START", flush=True)

        p = subprocess.run(cmd, shell=True, executable="/bin/bash")
        if p.returncode != 0:
            failures += 1
            print(f"{tag} FAIL rc={p.returncode}", flush=True)
        else:
            print(f"{tag} DONE", flush=True)

    # Gather failure counts
    total_failures = comm.reduce(failures, op=MPI.SUM, root=0)
    comm.Barrier()

    if rank == 0:
        if total_failures:
            print(f"[MPI] finished with failures={total_failures}", flush=True)
        else:
            print("[MPI] finished successfully (no failures)", flush=True)

    # Do not fail the job by default; return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

