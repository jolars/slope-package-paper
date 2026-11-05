# Single-penalty SLOPE benchmark

This native [Metewand](https://github.com/jolars/metewand) benchmark compares
the ten solver configurations and nine datasets used by the paper. The full
experiment selects three regularization values, giving 270 candidates before
applicability exclusions. The [path
benchmark](../path/README.md) also uses Metewand.

The shared [`config.yml`](config.yml) defines `full`, `smoke`, and `example`
experiments. `full` is the default; the smaller experiments reuse the same
workers, scientific contract, and profile policies. Numerical-library thread
limits are declared in the worker environment, including OpenMP and BLAS limits
of one thread.

Run these commands from the paper repository root. The pinned Devenv environment
includes the CLI, Python bindings, scientific dependencies, and R for reading
Breheny's data:

```sh
devenv shell
benchmark-single
```

`benchmark-single` creates a run beneath `benchmarks/single/outputs/`. To choose a
destination or resume an existing run:

```sh
benchmark-single --output-dir benchmarks/single/outputs/comparison
benchmark-single --output-dir benchmarks/single/outputs/comparison --resume
```

Use `--resume --retry` to retain earlier evidence and explicitly retry failed
measurements. Data materializations are cached beneath
`${SLOPE_BENCHMARK_DATA_DIR:-.benchmark-data}/metewand`.

For a small comparison, use a Python environment with Metewand's Python package,
NumPy, SciPy, scikit-learn, Numba, sortedl1, and tick installed:

```sh
mkdir -p benchmarks/single/outputs
metewand check --manifest benchmarks/single/config.yml --experiment example --workers
metewand plan --manifest benchmarks/single/config.yml --experiment example
metewand run --manifest benchmarks/single/config.yml --experiment example \
  --output-dir benchmarks/single/outputs/example
```

The smoke experiment additionally uses skglm,
slope-path, and slopescreening and covers dense and sparse designs. It runs
through `benchmark-smoke`, alongside the native path benchmark. The shared
[`validate.py`](../validate.py) checks worker references, runs a comparison, exercises resume and inspection,
and retains a complete JSON export:

```sh
python benchmarks/validate.py --output-dir benchmarks/single/outputs/smoke
```

## Scientific and timing choices

The port preserves the upstream normalized squared-loss objective,
Benjamini–Hochberg penalty weights, dataset generation, standardization, and
solver algorithms. Simulations retain explicit random state 27. The generator
comes from Benchopt 1.9.1 and includes its BSD license. `ORIGINS.json` records
the upstream revision, original source hashes, and solver references. The port
also corrects skglm iteration limits by setting `model.solver.max_iter`; the
upstream assignment to `model.max_iter` did not control the solver.

Each materializer writes dense NumPy arrays or a sparse CSC matrix, plus the
response vector. Implementations receive verified copies of the same data.
Results contain `beta.npy`, with the intercept first. A separate evaluator
checks dimensions, finite values, and the intercept, then recomputes the
objective and dual certificate. It rejects relative gaps below `-1e-10` and uses
the unrounded relative gap to decide whether the `1e-7` target is reached.
Reported metrics use twelve decimal places for stable reference checking.

PGD, ADMM, and Newt-ALM expose streaming profiles from one solver trajectory.
The remaining methods run from clean state at successive iteration limits or,
for sortedl1, tolerances. Iteration checkpoints are `0, 1, 2, 4, ...`; the zero
point records the initial coefficients. The finite schedules and the shared
30-second active-time limit bound collection. Unsupported sparse inputs remain
visible as applicability exclusions.

Timing uses `execute_only` after explicit warm-up. Imports, dataset loading,
weight construction, solver construction, and JIT compilation happen before
measurement. Work inside each solver call, including spectral calculations and
factorization, remains timed. Streaming active time excludes checkpoint
evaluation and publication pauses and includes snapshot serialization. Fresh
sequence points retain their individual executor wall times. These coordinates
and the framework's additional timing evidence remain separate in exports. The
profile time budget accumulates measured work across fresh-sequence points. Runs
remain serial; repetitions use the same materialized input.

Worker sources use nonrecursive globs for the adapter files and explicit
patterns for solver and dataset modules. Outputs can remain beneath the
benchmark directory because those patterns do not capture `outputs/`.

The analytic reference uses an identity design with two pooled coefficients.
Tests construct its normal quantiles and KKT certificate independently. Dataset
fixtures also check equality with the original Benchopt generator.

## Export and plot

```sh
metewand export --output-dir benchmarks/single/outputs/comparison \
  --format json --destination benchmarks/single/outputs/comparison-export
python code/plot_benchmark_simul.py \
  --results benchmarks/single/outputs/comparison-export --output /tmp/simulated.pdf
python code/plot_benchmark_real.py \
  --results benchmarks/single/outputs/comparison-export --output /tmp/real.pdf
```

Add `--require-complete` to export when every applicable comparison must have
reached its target. Without it, committed observations remain exportable after
timeouts or convergence misses. Plotting prefers a selected trajectory. If no
stream was accepted, it shows one latest attempt's retained valid checkpoints
with a dashed line. It keeps repetitions separate and warns about incomplete
comparisons. Failure and applicability evidence remain in the loaded table's
metadata. Existing plotting defaults continue to read the saved Benchopt
results.

## Developing Metewand alongside the benchmark

The environment pins one Metewand revision for both the CLI and Python package.
To build from a local checkout without changing the pin:

```sh
devenv --option slopeBenchmark.metewandSource:path /home/jola/projects/metewand shell
```

Alternatively, build the CLI in the Metewand checkout and install its Python
package in your scientific environment. Workers do not inherit an ambient
`PYTHONPATH`.
