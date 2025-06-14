#!/bin/bash

SOLVERS=(
  "PGD[prox=prox_fast_stack,acceleration=fista]"
  # "PGD[prox=prox_fast_stack,acceleration=bb]"
  # "PGD[prox=prox_fast_stack,acceleration=anderson]"
  "ADMM[adaptive_rho=True,rho=100]"
  "rSLOPE"
  "sortedl1"
  "skglm"
  "SlopePath"
  # "Newt-ALM"
  "PGD_safe_screening[accelerated=True]"
)

DATASETS=(
  "Simulated[X_density=1.0,n_features=100,n_samples=2000,rho=0.5,n_signals=50]"
  "Simulated[X_density=1.0,n_features=2000,n_samples=100,rho=0.5,n_signals=10]"
  # "Simulated[X_density=0.001,n_features=200000,n_samples=2000,rho=0.0,n_signals=50]"
  "breheny[dataset=bcTCGA,standardize=True]"
  # "libsvm[dataset=YearPredictionMSD,standardize=True]"
  # "breheny[dataset=Rhee200,standardize=True]"
)

OBJECTIVES=(
  "SLOPE[fit_intercept=True,q=0.2,reg=0.5]"
  "SLOPE[fit_intercept=True,q=0.2,reg=0.1]"
  # "SLOPE[fit_intercept=True,q=0.2,reg=0.01]"
)
