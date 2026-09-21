# Efficient Solvers for SLOPE in R, Python, Julia, and C++

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
- Mathurin Massias (Inria, ENS de Lyon, CNRS)
- Jonas Wallin (Lund University)

### What is SLOPE?

SLOPE solves the following optimization problem:

$$
\text{minimize}_{\beta_0, \beta} \quad F(\beta_0, \beta) + \alpha J(\beta; \lambda)
$$

where:

- $F$ is a smooth convex loss function (e.g., from GLMs)
- $J(\beta; \lambda)$ is the sorted L1 norm: $J(\beta; \lambda) = \sum_j \lambda_j |\beta(j)|$
- $\lambda$ is a non-increasing sequence of penalty weights
- $|\beta(1)| \geq |\beta(2)| \geq \ldots \geq |\beta(p)|$ are the sorted absolute coefficients

SLOPE generalizes both the lasso (constant $\lambda$) and OSCAR (linearly decreasing $\lambda$),
with the unique property of clustering coefficients by setting them to equal
magnitudes.

## Repository Structure

This repository is organized into several key components:

- **Benchmarks** (`benchmark_slope/`, `benchmark_slope_path/`): Two Benchopt
  benchmarks for comparing SLOPE solvers: one for single-penalty problems and
  one for full path fitting
- **Results** (`results/`): Benchmark outputs with performance comparisons
  across solvers
- **Analysis Code** (`code/`, `slopeutils/`): R and Python scripts for
  reproducing figures and analyses from the paper
- **Manuscript** (`main.tex`, `main.pdf`, `tex/`): LaTeX source and compiled
  paper

<details>
<summary>Directory tree</summary>

```
.
├── benchmark_slope/            # Benchopt benchmark for single-penalty problems
│   ├── datasets/               # Benchmark datasets
│   ├── solvers/                # Solver implementations
│   ├── objective.py            # Benchmark objective definition
│   └── README.rst
├── benchmark_slope_path/       # Benchopt benchmark for path fitting
│   ├── datasets/
│   ├── solvers/
│   ├── objective.py
│   └── README.md
├── code/                       # Analysis and visualization scripts
│   ├── plot_benchmark_path.py  # Benchmark plotting scripts
│   ├── plot_benchmark_real.py  # for real data
│   ├── plot_benchmark_simul.py # for simulated data
│   ├── plot_thresholding.py    # SLOPE thresholding illustration
│   ├── example.R               # Usage examples for paper
│   ├── example.py
│   ├── example.jl
│   ├── example.cpp
│   ├── CMakeLists.txt          # Build definition for the C++ example
│   └── real-data.R             # Real data analysis for paper
├── data/                       # Data used by the examples
│   └── diabetes.csv
├── images/                     # Generated figures from paper
│   ├── benchmark_path_real.pdf
│   ├── benchmark_single_simulated.pdf
│   └── ...
├── results/                    # Benchmark results
│   ├── path_0831/              # Path-fitting benchmark results
│   └── single_0831/            # Single-penalty benchmark results
├── slopeutils/                 # Utility functions
│   ├── merge_parquet.py
│   └── plot_utils.py
├── tex/                        # LaTeX macros
│   └── macros.tex
├── bench_config_single.yml     # Benchopt configuration for single-penalty
├── bench_config_path.yml       # Benchopt configuration for path-fitting
├── devenv.nix                  # Reproducible development environment
├── devenv.lock                 # Locked Nix inputs
├── Project.toml                # Julia environment for the Julia example
├── Manifest.toml               # Locked Julia dependencies
├── Taskfile.yml                # Task automation
├── main.tex                    # Paper LaTeX source
├── main.bib                    # Bibliography
└── README.md
```

</details>

## Cloning the Repository

The two benchmarks are included as git submodules, so clone the repository
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

## Running Benchmarks

We provide two separate benchmarks for comparing SLOPE solvers, one for
single-penalty problems and one for fitting the full SLOPE path. The benchmarks
use [Benchopt](https://benchopt.github.io/), a benchmarking framework for
optimization algorithms.

Start with the Conda instructions below. To use the pinned package versions
from this repository, use the [published container](#oci-container) or
[Devenv](#using-devenv).

### Using Conda

Create a Conda environment and install Benchopt:

```bash
conda create -n benchopt -c conda-forge python=3.12
conda activate benchopt
pip install benchopt
```

Then install the benchmark dependencies and run the example configuration:

```bash
benchopt install ./benchmark_slope --config benchmark_slope/example_config.yml
benchopt run ./benchmark_slope --config benchmark_slope/example_config.yml
```

For the path benchmark, replace `benchmark_slope` with `benchmark_slope_path` in
both commands. For the full benchmarks, use `bench_config_single.yml` or
`bench_config_path.yml` as the configuration in both commands, and add
`--no-cache --timeout 30` to `benchopt run`. Full runs can take several hours.

Results are written to `benchmark_slope/outputs/` and
`benchmark_slope_path/outputs/`, respectively. See [Plots](#plots) for how to
plot these results or regenerate figures from the results included here.

This installation uses current Conda and PyPI packages. You can choose solvers
and data sets on the command line or in your own YAML configuration files.
See the [Benchopt documentation](https://benchopt.github.io/) for more details.

### OCI Container

Use the published container to run the benchmarks with Docker. Replace
`v1.0.0` with the release tag you want:

```bash
docker run --name slope-benchmarks -it ghcr.io/jolars/slope-package-benchmarks:v1.0.0
```

Inside the container, run `benchmark-single` or `benchmark-path`. The image
includes the pinned benchmark environment, source code, and configurations.
It does not include the tools for compiling the paper or generating figures.

Data and results remain in the named container after you exit. Copy them out
with `docker cp` before removing the container. Each release includes a
`container-image.txt` asset with the immutable image reference.

<details>
<summary>Building and publishing the container</summary>

To build the image locally from the same pinned environment:

```bash
devenv container build shell
devenv container run shell
```

Publishing a GitHub release tests the environment, builds the image, and
publishes it to the GitHub Container Registry with release and source commit
tags. A maintainer must make the package public in GitHub's package settings
after the first publication.

</details>

### Using Devenv

Devenv provides the pinned environment described in
[Reproducible Environment](#reproducible-environment). First, [install Nix and
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

These commands use `bench_config_single.yml` and `bench_config_path.yml`, pass a
30-second timeout to Benchopt, disable Benchopt's result cache, and do not
invoke `benchopt install`. Both configurations use
a solver-independent relative-duality-gap target of `1e-7`, after which Benchopt
stops sampling the corresponding convergence curve. The benchmark plotting
scripts display only evaluations taking no more than 30 seconds. Thread-count
environment variables are left unset, so numerical libraries use their default
threading behavior.

Downloaded data is kept under `.benchmark-data/`; set `SLOPE_BENCHMARK_DATA_DIR`
to use another location. Record the environment and data hashes after each
benchmark run with:

```bash
benchmark-environment > benchmark-environment.txt
benchmark-data-checksums > benchmark-data.sha256
```

## Compiling the Paper

To compile the LaTeX source of the paper, ensure you have a LaTeX distribution
installed, then run:

```bash
latexmk -pdf -interaction=nonstopmode main.tex
```

## Code in Paper

The scripts in `code/` are lightweight examples for generating figures and
demonstrating package usage. They are not intended to be strict, byte-for-byte
reproducibility pipelines. Follow the installation instructions for each
language below. Package versions are listed in
[Reproducible Environment](#reproducible-environment).

In the Devenv shell, skip the R and Python package installation commands below.
Output figures are written to `images/` (the directory is created automatically
if missing).

### R Example

Install the R dependencies in an R session:

```r
install.packages(c("SLOPE", "knitr", "tinytex", "here", "lars"))
```

The script crops one of the figures with `knitr::plot_crop()`, which needs
`pdfcrop` (part of TeX Live) and Ghostscript. If these are missing, the script
still runs, but leaves the figure uncropped.

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

If you use Devenv, the example is already built; run `slope-example` directly.

### Plots

The benchmark plotting scripts in `code/plot_benchmark_*.py` use the results in
`results/path_0831/` and `results/single_0831/`, so you can regenerate the
figures without running the benchmarks. To plot a new run, change `results_dir`
in the relevant script to a directory containing that run's Parquet files. The
scripts combine all Parquet files in that directory.

Install these packages in addition to the dependencies in
[Python Example](#python-example):

```bash
pip install pandas numpy scipy pyarrow
```

The plots typeset their text with LaTeX (`text.usetex` in Matplotlib), so you
also need a LaTeX installation that provides `mathtools`, `lmodern`, `bm`, and
`siunitx`, together with `cm-super`, `dvipng`, and Ghostscript. On Debian and
Ubuntu, for instance, these are available in the `texlive-latex-recommended`,
`texlive-latex-extra`, `texlive-science`, `texlive-fonts-recommended`,
`lmodern`, `cm-super`, `dvipng`, and `ghostscript` packages.

You can then run the plotting scripts with:

```bash
python code/plot_benchmark_path.py
python code/plot_benchmark_real.py
python code/plot_benchmark_simul.py
python code/plot_thresholding.py
```

## Real Data Analysis Example

In `code/real-data.R`, we provide an extended example using the R `SLOPE`
package, which is described in Section 6 in the paper. Install these packages
in an R session, in addition to the dependencies in [R
Example](#r-example):

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

The reusable benchmark repositories describe their dependencies without fixing a
complete environment. The paper repository owns the reproducible workflow: its
submodule revisions fix the benchmark code, while the root Devenv fixes the
software closure used to execute it. The generated OCI image carries that same
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

## License

This repository is dual-licensed:

- **Paper and Documentation** (LaTeX files, PDFs, markdown, images):
  [CC-BY-3.0](LICENSE-PAPER)
- **Software Code** (Python, R, benchmarks): [GPL-3.0](LICENSE-CODE)

See [LICENSE](LICENSE) for the complete dual license notice.
