#!/bin/bash

SOLVERS=(
  "rSLOPE"
  "sortedl1"
  "SolutionPath"
)

DATASETS=(
  "Simulated[X_density=1.0,n_features=200,n_samples=100,rho=0.2,n_signals=10]"
  "breheny[dataset=brca1,standardize=True]"
)

OBJECTIVES=(
  "SLOPE_Path[fit_intercept=False,q=0.2,path_length=20]"
  "SLOPE_Path[fit_intercept=False,q=0.2,path_length=50]"
  "SLOPE_Path[fit_intercept=False,q=0.2,path_length=100]"
)
