#!/bin/bash
#SBATCH --job-name=parallel-per-node
#SBATCH --output=parallel_node_%j_%t.out
#SBATCH --error=parallel_node_%j_%t.err
#SBATCH --nodes=49
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=28
#SBATCH --time=8:00:00
#SBATCH --partition=large-28core

module load gnu-parallel/6.0

srun -c "$SLURM_CPUS_PER_TASK" --cpu-bind=none bash -c '
  export OMP_NUM_THREADS=1
  TOTAL_LINES=$(wc -l < input.txt)
  TASKS=${SLURM_NNODES}
  LINES_PER_TASK=$(( (TOTAL_LINES + TASKS - 1) / TASKS ))

  CMD_RANGE_START=$((SLURM_PROCID * LINES_PER_TASK + 1))
  CMD_RANGE_END=$((CMD_RANGE_START + LINES_PER_TASK - 1))
  if [ "$CMD_RANGE_END" -gt "$TOTAL_LINES" ]; then
    CMD_RANGE_END="$TOTAL_LINES"
  fi

  echo "Running on $(hostname) (SLURM_PROCID=$SLURM_PROCID)"
  echo "Processing lines $CMD_RANGE_START to $CMD_RANGE_END (of $TOTAL_LINES total)"

  sed -n "${CMD_RANGE_START},${CMD_RANGE_END}p" input.txt > node_chunk_${SLURM_PROCID}.txt
  cat node_chunk_${SLURM_PROCID}.txt | parallel --jobs ${SLURM_CPUS_PER_TASK} --verbose
'

