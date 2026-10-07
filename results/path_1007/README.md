# Solution-path benchmarks, October 7, 2026

These results use the updated benchmark submodule and root Devenv environment.
Tick's curves were removed from the original run because tick does not provide
native SLOPE path fitting. The retained curves are unchanged. To reproduce the
selected solver set, run:

```bash
benchmark-path --no-plot --seed 0 --output slope-path-2026-10-07
```

The command disables the result cache and uses a 30-second timeout and one
repetition. The run sets `BLIS_NUM_THREADS`, `MKL_NUM_THREADS`,
`NUMEXPR_NUM_THREADS`, `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, and
`VECLIB_MAXIMUM_THREADS` to 1, and `OMP_DYNAMIC` to `FALSE`.

`benchmark-environment.txt` records package versions, source revisions,
hardware, and thread settings. `config.yml` and `devenv.lock` preserve the run's
configuration and locked inputs. `benchmark-data.sha256` records the cached
input data checksums.

The result file contains 33 solver, dataset, and objective combinations.
Benchopt skipped SolutionPath's three Rhee2006
cases because its adapter does not support sparse design matrices. There were
no runtime errors or divergence flags. Of the retained runs, 25 reached the
configured time limit. `summary.json` records
these outcomes and the coverage of each solver.
