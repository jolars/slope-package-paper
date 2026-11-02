# Solution-path SLOPE benchmark

This native [Metewand](https://github.com/jolars/metewand) benchmark compares
sortedl1, SolutionPath, ADMM with rho 100, and FISTA on the full SLOPE path.
The full manifest preserves the paper's three datasets (BRCA1,
Koussounadis2014, and Rhee2006), requested path lengths 50, 100, and 200,
q = 0.2, and no intercept. This gives 36 candidates.

Run these commands from the paper repository root in the pinned Devenv shell:

```sh
devenv shell
benchmark-path
```

Choose a destination or resume an existing run with:

```sh
benchmark-path --output-dir benchmark_slope_path/outputs/comparison
benchmark-path --output-dir benchmark_slope_path/outputs/comparison --resume
```

Add `--resume --retry` to explicitly retry failed measurements while retaining
earlier evidence. Data and grids are cached beneath
`${SLOPE_BENCHMARK_DATA_DIR:-.benchmark-data}/metewand`.

The smaller example needs Metewand's CLI and Python package, NumPy, SciPy,
scikit-learn, Numba, sortedl1, and the slope-path package pinned in
`nix/benchmark-python-packages.nix`:

```sh
mkdir -p benchmark_slope_path/outputs
metewand check --manifest benchmark_slope_path/example_config.yml --workers
metewand plan --manifest benchmark_slope_path/example_config.yml
metewand run --manifest benchmark_slope_path/example_config.yml \
  --output-dir benchmark_slope_path/outputs/example
```

`benchmark-smoke` additionally checks sparse inputs, intercept fitting, and
the optional R SLOPE adapter. It records SolutionPath's exclusions for sparse
designs and intercepts. The R adapter requires rpy2 and R with SLOPE and Matrix,
which the pinned environment supplies. The shared validator exercises worker
references, execution, status, resume, complete export, and observation inspection:

```sh
python benchmark_slope/validate.py --manifest bench_config_smoke_path.yml \
  --metric max_rel_duality_gap --output-dir benchmark_slope_path/outputs/smoke
```

## Scientific and timing choices

The port preserves the normalized squared-loss objective, Benjamini–Hochberg
weights, simulation seed 27, preprocessing, solver algorithms, warm starts
within each path, and exact-path interpolation. `ORIGINS.json` records the
original repository revision, source hashes, and method references. The
simulation generator comes from Benchopt 1.9.1 with its BSD license.
The optional R adapter uses SLOPE 2.1.1's `tol` argument and separate
intercepts. Its old tolerance arguments are deprecated and ignored by that
version.

Each materializer writes the design, response, alpha grid, and penalty weights.
It constructs the grid using the same sortedl1 path call as the original
benchmark, retaining any early truncation. All methods and the evaluator load
the same arrays. Grid construction happens once before measurement. Coupled
manifest cases set `path_length`, `q`, and `fit_intercept` for both the dataset
and problem; keep these settings in agreement when editing a manifest. Workers
reject a grid whose settings disagree with the requested problem.

Results contain `coefs.npy` with shape features by actual path length and
`intercepts.npy` with one entry per alpha. The independent evaluator checks
dimensions, finite values, zero intercepts when disabled, and the dual
certificate at every point. A relative gap below `-1e-10` at any alpha makes
the path invalid. Completion requires the maximum unrounded relative duality
gap to be at most `1e-7`. Reported metrics are rounded to twelve decimal places.

All methods use fresh-sequence profiles. Each point fits the complete path
from clean state at a tighter tolerance, or a larger iteration limit for
SolutionPath. The initial point contains zero coefficients. Fits preserve
warm starts between consecutive alphas. Timing uses `execute_only`: imports,
data and grid loading, solver construction, and explicit warm-up happen before
measurement. Spectral calculations, factorizations, and exact-path interpolation
remain inside the timed call. Each point retains its individual wall time,
and the profile accumulates timed work against a 30-second budget. Runs are
serial, and finite schedules bound collection.

Tests compare simulations and grids with fixtures from the original benchmark,
check an analytic identity-design path and its KKT certificates, and verify
convergence across dense, sparse, and intercept configurations.

## Export and plot

```sh
metewand export --output-dir benchmark_slope_path/outputs/comparison \
  --format json --destination benchmark_slope_path/outputs/comparison-export
python code/plot_benchmark_path.py \
  --results benchmark_slope_path/outputs/comparison-export --output /tmp/path.pdf
```

Add `--require-complete` when every applicable candidate must reach its target.
Otherwise, committed observations remain exportable after timeouts or
convergence misses. Plots keep repetitions separate and mark partial curves
with dashed lines. The default still reads the historical Benchopt tables in
`results/path_1007/`.

See the [single-penalty guide](../benchmark_slope/README.md#developing-metewand-alongside-the-benchmark)
for building both suites against a local Metewand checkout.
