#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
======================================================================
MPI Batched Command Runner (dynamic master/worker)
======================================================================

Purpose
-------
Distribute and execute a very large list of shell commands (e.g., AutoDock Vina)
across many nodes and cores using MPI. Uses *dynamic scheduling* so workers that
finish early get more work. Supports batching so each rank runs multiple
commands sequentially per assignment to reduce overhead.

Usage
-----
mpirun -n <NUM_RANKS> python -u mpi_batched_runner.py --input input.txt --batch 10
srun  -N 24 -n 672 -p medium-28core --mpi=openmpi \
      python -u mpi_batched_runner.py --input input.txt --batch 10

Options
-------
--input <file>   : File with one shell command per line
--batch <int>    : How many commands per work unit (default=10)
--limit <int>    : Process only this many commands (for testing)
--shuffle        : Shuffle commands before distributing
--dry-run        : Print commands but do not execute
"""

import argparse, os, random, signal, subprocess, sys, time
from typing import List, Tuple
from mpi4py import MPI

TAG_READY, TAG_START, TAG_DONE, TAG_EXIT = 1, 2, 3, 4

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", "-i", required=True, help="Input file with one shell command per line")
    p.add_argument("--batch", "-b", type=int, default=10, help="Commands per batch")
    p.add_argument("--limit", type=int, default=0, help="If >0, cap number of commands")
    p.add_argument("--shuffle", action="store_true", help="Shuffle commands")
    p.add_argument("--dry-run", action="store_true", help="Print but don’t execute")
    p.add_argument("--timeout", type=int, default=0, help="Timeout per command (s, 0=none)")
    return p.parse_args()

def load_commands(path, limit=0) -> List[str]:
    cmds = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"): continue
            cmds.append(s)
            if limit and len(cmds) >= limit: break
    return cmds

def run_command(cmd: str, dry_run=False, timeout=0) -> Tuple[int, float]:
    print(f"Running: {cmd}", flush=True)
    if dry_run: return 0, 0.0
    t0 = time.time()
    try:
        rc = subprocess.run(cmd, shell=True, timeout=timeout or None).returncode
    except subprocess.TimeoutExpired:
        rc = 124
    dt = time.time() - t0
    return rc, dt

def master(comm, size, args):
    all_cmds = load_commands(args.input, args.limit)
    if args.shuffle: random.shuffle(all_cmds)
    total = len(all_cmds)
    idx, done, fail = 0, 0, 0
    batch = max(1, args.batch)

    print(f"Master: {total} commands, batch={batch}, workers={size-1}", flush=True)
    t0 = time.time()

    while done < total:
        status = MPI.Status()
        _ = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
        src, tag = status.Get_source(), status.Get_tag()

        if tag == TAG_READY:
            if idx < total:
                end = min(idx + batch, total)
                comm.send(all_cmds[idx:end], dest=src, tag=TAG_START)
                idx = end
            else:
                comm.send(None, dest=src, tag=TAG_EXIT)
        elif tag == TAG_DONE:
            done += _["processed"]; fail += _["failed"]
            print(f"Progress: {done}/{total} done, {fail} failed", flush=True)

    for w in range(1, size):
        comm.send(None, dest=w, tag=TAG_EXIT)

    print(f"Master finished: {total} commands, {fail} failed, elapsed {time.time()-t0:.1f}s", flush=True)

def worker(comm, args):
    while True:
        comm.send(None, dest=0, tag=TAG_READY)
        status = MPI.Status()
        payload = comm.recv(source=0, tag=MPI.ANY_TAG, status=status)
        if status.Get_tag() == TAG_START:
            processed = failed = 0
            for cmd in payload:
                rc, _ = run_command(cmd, args.dry_run, args.timeout)
                processed += 1
                if rc != 0: failed += 1
            comm.send({"processed": processed, "failed": failed}, dest=0, tag=TAG_DONE)
        else:
            break

def main():
    args = parse_args()
    comm = MPI.COMM_WORLD
    if comm.Get_rank() == 0:
        master(comm, comm.Get_size(), args)
    else:
        worker(comm, args)

if __name__ == "__main__":
    main()

