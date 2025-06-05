#!/bin/sh

#PBS -W group_list=ku_00308 -A ku_00308
#PBS -m n
#PBS -l nodes=1:thinnode:ppn=20
#PBS -l mem=128gb
#PBS -l walltime=02:00:00

echo Working directory is $PBS_O_WORKDIR
cd $PBS_O_WORKDIR

NPROCS=`wc -l < $PBS_NODEFILE`
echo This job has allocated $NPROCS nodes

source $PBS_O_WORKDIR/pbs_config.sh

# Calculate which solver, dataset, and objective to use based on array index
SOLVER_INDEX=$((PBS_ARRAYID % ${#SOLVERS[@]}))
DATASET_INDEX=$(( (PBS_ARRAYID / ${#SOLVERS[@]}) % ${#DATASETS[@]} ))
OBJECTIVE_INDEX=$(( PBS_ARRAYID / (${#SOLVERS[@]} * ${#DATASETS[@]}) ))

# Get the actual solver, dataset, and objective names
SOLVER=${SOLVERS[$SOLVER_INDEX]}
DATASET=${DATASETS[$DATASET_INDEX]}
OBJECTIVE=${OBJECTIVES[$OBJECTIVE_INDEX]}

echo "Running benchmark with:"
echo "  Solver: $SOLVER"
echo "  Dataset: $DATASET"
echo "  Objective: $OBJECTIVE"

module purge
module load tools
module load apptainer/1.4.0
module load fuse-overlayfs/1.14

echo "Run the benchmark"
apptainer run \
  --underlay \
  --bind $RESULTS_DIR:/opt/app/outputs,$PBS_O_WORKDIR/scratch:/opt/app/__cache__ \
  container_single.sif \
  "$SOLVER" "$DATASET" "$OBJECTIVE"

echo "Benchmark completed for solver: $SOLVER, dataset: $DATASET, and objective: $OBJECTIVE"
