# Single-penalty benchmarks, October 7, 2026

This run uses `bench_config_single.yml`, including tick 0.8.0.2, with the
updated benchmark submodule and root Devenv environment.

```bash
benchmark-single --no-plot --seed 0 --output slope-single-2026-10-07-tick
```

The command disables the result cache and uses a 30-second timeout and one
repetition. The run sets `BLIS_NUM_THREADS`, `MKL_NUM_THREADS`,
`NUMEXPR_NUM_THREADS`, `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, and
`VECLIB_MAXIMUM_THREADS` to 1, and `OMP_DYNAMIC` to `FALSE`.

`benchmark-environment.txt` records package versions, source revisions,
hardware, and thread settings. `config.yml` and `devenv.lock` preserve the run's
configuration and locked inputs. `benchmark-data.sha256` records the cached
input data checksums.

The result file contains 245 solver, dataset, and objective combinations,
including all 27 tick cases. Benchopt skipped 24 combinations because SlopePath
and safe screening do not support sparse design matrices. It flagged ADMM with
`rho=100` as diverged on YearPredictionMSD at `reg=0.5` and omitted that curve.
Another 100 runs reached the configured time limit, including 19 tick runs.
`summary.json` records these outcomes and the coverage of each solver.
