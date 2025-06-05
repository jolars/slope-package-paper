#!/bin/bash

TIMESTAMP=$(date +%m%d_%H%M%S)

RESULTS_DIR="$PWD/results/$TIMESTAMP"
LOGS_DIR="$PWD/logs/$TIMESTAMP"
mkdir -p "$RESULTS_DIR" "$LOGS_DIR"

source pbs_config.sh

# Calculate total number of combinations (subtract 1 for 0-based indexing)
TOTAL_COMBINATIONS=$(( ${#SOLVERS[@]} * ${#DATASETS[@]} * ${#OBJECTIVES[@]} - 1 ))

qsub -t 0-${TOTAL_COMBINATIONS}%8 -N "benchslope_${TIMESTAMP}" \
    -e "$LOGS_DIR" -o "$LOGS_DIR" \
    -v RESULTS_DIR="$RESULTS_DIR" \
    pbs_worker.sh

echo "Submitted job with array range 0-${TOTAL_COMBINATIONS}"
echo "Results will be stored in: $RESULTS_DIR"
echo "Logs will be stored in: $LOGS_DIR"
