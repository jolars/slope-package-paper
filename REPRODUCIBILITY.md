# Reproducing Efficient Solvers for SLOPE in R, Python, Julia, and C++

[![arXiv](https://img.shields.io/badge/arXiv-2511.02430-b31b1b.svg)](https://arxiv.org/abs/2511.02430)
[![Test
Reproducibility](https://github.com/jolars/slope-package-paper/actions/workflows/test-reproducibility.yml/badge.svg)](https://github.com/jolars/slope-package-paper/actions/workflows/test-reproducibility.yml)

This repository contains the research paper **"Efficient Solvers for SLOPE in R,
Python, Julia, and C++"** and associated reproducibility materials, including
benchmarks and analysis code.

## Paper Summary

The paper presents a suite of packages across multiple programming languages (R,
Python, Julia, and C++) for efficiently solving the Sorted L-One Penalized
Estimation (SLOPE) problem. SLOPE is a type of regularized regression that uses
a sorted L1 norm penalty, which allows it to perform variable selection and
coefficient clustering simultaneously.

### Authors

- Johan Larsson (University of Copenhagen)
- Małgorzata Bogdan (University of Wrocław)
- Krystyna Grzesiak (University of Wrocław)
- Mathurin Massias (Inria, ENS de Lyon, CNRS, Université Claude Bernard Lyon 1)
- Jonas Wallin (Lund University)

### What is SLOPE?

SLOPE solves the following optimization problem:

$$
\text{minimize}_{\beta_0, \beta} \quad F(\beta_0, \beta) + \alpha J(\beta; \lambda)
$$

where:

- $F$ is a smooth convex loss function (e.g., from GLMs)
- $J(\beta; \lambda)$ is the sorted L1 norm:
  $J(\beta; \lambda) = \sum_j \lambda_j |\beta(j)|$
- $\lambda$ is a non-increasing sequence of penalty weights
- $|\beta(1)| \geq |\beta(2)| \geq \ldots \geq |\beta(p)|$ are the sorted
  absolute coefficients

SLOPE generalizes both the lasso (constant $\lambda$) and OSCAR (linearly
decreasing $\lambda$), with the unique property of clustering coefficients by
setting them to equal magnitudes.

## Repository Structure

This repository is organized into several key components:

- **Benchmarks** (`benchmark_slope/`, `benchmark_slope_path/`): Two
  benchmarks for comparing SLOPE solvers: Metewand for single-penalty problems
  and Benchopt for full path fitting
- **Results** (`results/`): Benchmark outputs with performance comparisons
  across solvers
- **Analysis Code** (`code/`, `slopeutils/`): R and Python scripts for
  reproducing figures and analyses from the paper
- **Manuscript** (`main.qmd`, `_quarto.yml`, `main.bib`): Quarto source,
  journal metadata, and bibliography


## Cloning the Repository

The path benchmark is included as a git submodule, so clone the repository
recursively:

```bash
git clone --recurse-submodules https://github.com/jolars/slope-package-paper.git
cd slope-package-paper
```

If you have already cloned the repository without `--recurse-submodules`, you
can fetch the submodules from the repository root with:

```bash
git submodule update --init --recursive
```

Run all commands below from the repository root.

## Computo Submission

The maintained manuscript is `main.qmd`, with metadata in `_quarto.yml`.
[Computo](https://computo-journal.org/site/guidelines-authors.html) requires
both HTML and PDF versions, a public GitHub repository, and reproducible
computation. Install the official format extension once:

```bash
quarto add --no-prompt computorg/computo-quarto-extension
```

Inside the Devenv shell, run:

```bash
task computo
```

This renders both formats and prepares `main.pdf`, `main.html`, the HTML
support files, and a plain-text `abstract.txt` under `_build/computo/`. Submit
the PDF and repository URL through Computo's OpenReview venue. Set the
repository's **Settings > Pages > Build and deployment** source to **GitHub
Actions** so the journal workflow can publish the HTML version for reviewers.
The expected site is <https://jolars.github.io/slope-package-paper/>.

`task paper-preview` starts an HTML preview, and `task paper-preview-pdf`
previews the journal PDF. `task arxiv` builds a source archive and verifies it
with XeLaTeX in an isolated staging directory. Its staged preprint omits the
journal review watermark and line numbers.

## Running Benchmarks

The single-penalty benchmark uses [Metewand](https://github.com/jolars/metewand).
The solution-path benchmark still uses [Benchopt](https://benchopt.github.io/).
The pinned [Devenv environment](#using-devenv) and [container](#oci-container)
provide both workflows:

```bash
benchmark-single
benchmark-path
```

The full single-penalty configuration is `bench_config_single.yml`. It preserves
all ten solver configurations and nine datasets and collects independently
evaluated convergence curves. `benchmark-single` writes new runs beneath
`benchmark_slope/outputs/`, with materialized data cached under `.benchmark-data/`.
See the [native benchmark guide](benchmark_slope/README.md) for smaller runs,
resuming, exports, plotting, timing boundaries, and local Metewand development.

### Path benchmark with Conda

The path benchmark can also install its dependencies through Benchopt:

```bash
conda create -n benchopt -c conda-forge python=3.12
conda activate benchopt
pip install benchopt
benchopt install ./benchmark_slope_path --config benchmark_slope_path/example_config.yml
benchopt run ./benchmark_slope_path --config benchmark_slope_path/example_config.yml
```

Use `bench_config_path.yml` and add `--no-cache --timeout 30` for the full path
comparison. Its results remain under `benchmark_slope_path/outputs/`.

### OCI Container

Use the published container to run the benchmarks with Docker. Replace `v1.0.0`
with the release tag you want:

```bash
docker run --name slope-benchmarks -it ghcr.io/jolars/slope-package-benchmarks:v1.0.0
```

Inside the container, run `benchmark-single` or `benchmark-path`. The image
includes the pinned benchmark environment, source code, and configurations. It
does not include the tools for compiling the paper or generating figures.

Data and results remain in the named container after you exit. Copy them out
with `docker cp` before removing the container. Each release includes a
`container-image.txt` asset with the immutable image reference.

#### Building the container locally

To build the image locally from the same pinned environment:

```bash
devenv container build shell
devenv container run shell
```

### Using Devenv

Devenv provides the pinned environment described in [Reproducible
Environment](#reproducible-environment). First, [install Nix and
Devenv](https://devenv.sh/getting-started/#installation), then check the
environment and enter the shell:

```bash
devenv test
devenv shell
```

`devenv test` checks the package versions and runs small benchmark
configurations. To run the full benchmarks in the shell:

```bash
benchmark-single
benchmark-path
```

These commands use `bench_config_single.yml` and `bench_config_path.yml`.
Metewand collects single-penalty profiles with a 30-second active-time budget.
The path command retains its 30-second Benchopt timeout and disables the
Benchopt result cache. Neither command installs dependencies during a run.

Downloaded data is kept under `.benchmark-data/`. Set `SLOPE_BENCHMARK_DATA_DIR`
to use another location. You can record the environment and data hashes after each
benchmark run with:

```bash
benchmark-environment > benchmark-environment.txt
benchmark-data-checksums > benchmark-data.sha256
```

## Rendering the Paper

Use the pinned environment from the repository root:

```bash
devenv shell
quarto render
```

Rendering executes the R, Python, Julia, and C++ examples and regenerates the
figures from the committed benchmark results. It does not run the full benchmark
suites. A clean render needs all example dependencies and can take several
minutes, especially while Julia compiles packages for the first time.

The official Computo workflow is retained unchanged. Its `setup-render-ci.sh`
hook initializes the path benchmark submodule and activates the same Nix-pinned
R/Python environment used locally. Julia follows the exact version in
`Manifest.toml`. The journal manages Quarto, TinyTeX, and its format extension.
Nix binary substitutions reduce setup time, but the journal's dependency cache
does not retain the Nix store between runners.

## Code in Paper

The scripts in `code/` are lightweight examples for generating figures and
demonstrating package usage. The manuscript executes these same scripts during rendering. Follow the installation instructions for each
language below. Package versions are listed in [Reproducible
Environment](#reproducible-environment).

If you are using the Devenv shell, skip the R and Python package installation
commands below. Output figures are written to `images/`.

### R Example

Install the R dependencies in an R session:

```r
install.packages(c("SLOPE", "knitr", "tinytex", "here", "lars"))
```

Run the example from your terminal:

```bash
Rscript code/example.R
```

### Python Example

Install the Python dependencies:

```bash
pip install sortedl1 matplotlib scikit-learn
```

You can then run the example script with:

```bash
python code/example.py
```

### Julia Example

For Julia, we provide the dependencies in [`Project.toml`](./Project.toml).
First instantiate the environment:

```bash
julia --project=. -e 'using Pkg; Pkg.instantiate()'
```

Then run the example with:

```bash
julia --project=. code/example.jl
```

### C++ Example

The C++ example in [`code/example.cpp`](./code/example.cpp) requires
[libslope](https://github.com/jolars/libslope) (version 6.5.4 is used for the
paper), Eigen 3.4 or later, and CMake 3.15 or later. If libslope is not already
installed on your system, you can build and install it from source with:

```bash
git clone --depth 1 --branch v6.5.4 https://github.com/jolars/libslope.git
cmake -S libslope -B libslope/build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF
cmake --build libslope/build
cmake --install libslope/build
```

The last step needs `sudo` if you install into a system-wide prefix. Then build
and run the example:

```bash
cmake -S code -B build
cmake --build build
./build/slope-example
```

If you use Devenv, the example is already built and you can run `slope-example`
directly.

### Plots

The benchmark plotting scripts in `code/plot_benchmark_*.py` use the results in
`results/path_1007/` and `results/single_1007/`, so you can regenerate the
figures without running the benchmarks. For a new single-penalty run, pass
`--results` with a Metewand JSON export or a directory of Benchopt Parquet
files to `code/plot_benchmark_real.py` or `code/plot_benchmark_simul.py`.
For the path benchmark, change `results_dir` in `code/plot_benchmark_path.py`
to the directory containing the run's Parquet files.

Install these packages in addition to the dependencies in [Python
Example](#python-example):

```bash
pip install pandas numpy scipy pyarrow
```

The plots typeset their text with LaTeX (`text.usetex` in Matplotlib), so you
also need a LaTeX installation that provides `mathtools`, `lmodern`, `bm`, and
`siunitx`, together with `cm-super`, `dvipng`, and Ghostscript.

You can then run the plotting scripts with:

```bash
python code/plot_benchmark_path.py
python code/plot_benchmark_real.py
python code/plot_benchmark_simul.py
python code/plot_thresholding.py
```

## Real Data Analysis Example

In `code/real-data.R`, we provide an extended example using the R `SLOPE`
package, which is described in the real-data application section of the paper. Install these packages in
an R session, in addition to the dependencies in [R Example](#r-example):

```r
install.packages(c("caret", "pROC", "glmnet"))
```

Run the analysis from your terminal:

```bash
Rscript code/real-data.R
```

## Reproducible Environment

The root [Devenv](https://devenv.sh/) configuration provides the package
versions used for the benchmarks, paper examples, and analysis. Its committed
`devenv.lock` pins the Nix inputs, `devenv.nix` defines the environment and
benchmark commands, `nix/benchmark-python-packages.nix` fixes external Python
sources by version or Git revision and content hash, and `Manifest.toml` locks
the Julia environment.

  | Implementation    | Version |
  | ----------------- | ------: |
  | R `SLOPE`         |   2.1.1 |
  | Python `sortedl1` |  1.11.3 |
  | Julia `SLOPE.jl`  |   1.3.1 |
  | C++ `libslope`    |   6.5.4 |

The paper repository owns the reproducible workflow. Its native sources and
path submodule revision fix the benchmark code, while Devenv fixes the software
closure used to execute it. `nix/metewand.nix` and `nix/metewand.patch` provide
the pinned Metewand build. The generated OCI image carries that same
closure to other Linux hosts.

## Citation

Here is a BibLaTeX entry for citing the paper:

```bibtex
@online{larsson2025d,
  title       = {Efficient Solvers for {SLOPE} in {R}, {Python}, {Julia}, and
                 {C}++},
  date        = {2025-11-04},
  url         = {http://arxiv.org/abs/2511.02430},
  doi         = {10.48550/arXiv.2511.02430},
  eprint      = {2511.02430},
  author      = {Larsson, Johan and Bogdan, Malgorzata and Grzesiak, Krystyna and
                 Massias, Mathurin and Wallin, Jonas},
  urldate     = {2025-11-05},
  eprintclass = {stat},
  eprinttype  = {arXiv},
  keywords    = {Computer Science - Mathematical Software,Computer Science -
                 Software Engineering,slope,software,Statistics -
                 Computation,Statistics - Machine Learning},
  pubstate    = {prepublished}
}
```

## Figure Provenance

| Figures | Producer | Inputs |
| --- | --- | --- |
| Diabetes paths, relaxed SLOPE, and R cross-validation | `code/example.R` | `lars::diabetes`, fixed cross-validation seed |
| Python diabetes paths and cross-validation | `code/example.py` | scikit-learn diabetes data, fixed cross-validation seed |
| Julia diabetes paths and cross-validation | `code/example.jl` | `data/diabetes.csv`, fixed seed |
| Glioma clusters and ROC curves | `code/real-data.R` | `SLOPE::glioma`, seed 222, stratified 70% training split |
| Thresholding illustration | `code/plot_thresholding.py` | Deterministic synthetic example |
| Single-solution benchmark grids | `code/plot_benchmark_real.py`, `code/plot_benchmark_simul.py` | `results/single_1007/*.parquet` |
| Path benchmark grid | `code/plot_benchmark_path.py` | `results/path_1007/*.parquet` |

All plotting scripts export PDF and SVG. The glioma figure uses the training
regularization path and marks the step chosen by cross-validation. Reported
AUCs, selected-variable counts, and cluster counts are computed during rendering.

The benchmark result directories include the configurations, source/environment
records, data checksums, and summary tables for the published runs. Full reruns
can take hours and will vary in timing with the hardware. The normal manuscript
render uses these saved measurements while rebuilding their visualizations.

## License

The new Computo manuscript and its original figures use [CC BY 4.0](LICENSE-PAPER).
Earlier preprints retain their [CC BY 3.0](LICENSE-PREPRINT) grants. Software
remains [GPL-3.0](LICENSE-CODE). See [LICENSE](LICENSE) for scope.
