# Efficient Solvers for SLOPE in R, Python, Julia, and C++

[![arXiv](https://img.shields.io/badge/arXiv-2511.02430-b31b1b.svg)](https://arxiv.org/abs/2511.02430)
[![Test Reproducibility](https://github.com/jolars/slope-package-paper/actions/workflows/test-reproducibility.yml/badge.svg)](https://github.com/jolars/slope-package-paper/actions/workflows/test-reproducibility.yml)

This repository contains the research paper **"Efficient Solvers for SLOPE in R,
Python, Julia, and C++"** and associated reproducibility materials, including
benchmarks and analysis code.

## Paper Summary

The paper presents a suite of packages across multiple programming languages (R,
Python, Julia, and C++) for efficiently solving the Sorted L-One Penalized
Estimation (SLOPE) problem. SLOPE is a type of regularized regression that uses
a sorted ℓ₁ norm penalty, which allows it to perform variable selection and
coefficient clustering simultaneously.

### Authors

- Johan Larsson (University of Copenhagen)
- Małgorzata Bogdan (University of Wrocław)
- Krystyna Grzesiak (University of Wrocław)
- Mathurin Massias (Inria, ENS de Lyon, CNRS)
- Jonas Wallin (Lund University)

### What is SLOPE?

SLOPE solves the following optimization problem:

```
minimize F(β₀, β) + α J(β; λ)
```

where:

- F is a smooth convex loss function (e.g., from GLMs)
- J(β, λ) is the sorted ℓ₁ norm: J(β; λ) = Σⱼ λⱼ \|β(j)\|
- λ is a non-increasing sequence of penalty weights
- \|β(1)\| ≥ \|β(2)\| ≥ ... ≥ \|β(p)\| are the sorted absolute coefficients

SLOPE generalizes both the lasso (constant λ) and OSCAR (linearly decreasing λ),
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
<summary>📁 <b>Full directory tree</b></summary>

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
│   ├── path_0623/              # Path-fitting benchmark results
│   └── single_0612/            # Single-penalty benchmark results
├── slopeutils/                 # Utility functions
│   ├── merge_parquet.py
│   └── plot_utils.py
├── tex/                        # LaTeX macros
│   └── macros.tex
├── bench_config_single.yml     # Benchopt configuration for single-penalty
├── bench_config_path.yml       # Benchopt configuration for path-fitting
├── flake.nix                   # Nix flake for reproducible environment
├── Project.toml                # Julia environment for the Julia example
├── Manifest.toml
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
```

If you have already cloned the repository without `--recurse-submodules`, you
can fetch the submodules afterwards with:

```bash
git submodule update --init --recursive
```

## Running Benchmarks

We provide two separate benchmarks for comparing SLOPE solvers, one for
single-penalty problems and one for fitting the full SLOPE path. The benchmarks
use [Benchopt](https://benchopt.github.io/), a benchmarking framework for
optimization algorithms.

### Installing Benchopt

The recommended way to use Benchopt is within a
[conda](https://anaconda.org/anaconda/conda) environment. Make sure you first
have a functioning version of conda. Then, create and activate a new conda
environment and install benchopt in it:

```bash
conda create -n benchopt -c conda-forge python=3.12
conda activate benchopt
pip install -U benchopt
```

### Running the Benchmarks

After having installed Benchopt, you need to install all the required
dependencies of the benchmarks. For a quick test to verify the setup, you can
install the dependencies for the example configuration by running the following
lines:

```bash
benchopt install ./benchmark_slope --config benchmark_slope/example_config.yml
benchopt install ./benchmark_slope_path --config benchmark_slope_path/example_config.yml
```

To run the benchmarks with the example configuration, you then run:

```bash
benchopt run ./benchmark_slope --config benchmark_slope/example_config.yml
benchopt run ./benchmark_slope_path --config benchmark_slope_path/example_config.yml
```

To reproduce the results from the paper, use the full benchmark configurations:

```bash
benchopt install ./benchmark_slope  --config bench_config_single.yml
benchopt install ./benchmark_slope_path  --config bench_config_path.yml

benchopt run ./benchmark_slope  --config bench_config_single.yml
benchopt run ./benchmark_slope_path  --config bench_config_path.yml
```

Note that it's possible that there are installation issues with some of the
solvers due to the complexity of their dependencies and continuous upgrades. For
full reproducibility, we therefore recommend that you instead use the provided
Nix flake environment, which provides a stable snapshot of all dependencies used
in the benchmarks at the time of running them. See
[Nix Environment](#nix-environment) below for more details.

You can also bypass the installation step (`benchopt install`) and manually
install the required dependencies if you prefer.

Note that the full benchmarks may take several hours to complete. You can
alternatively configure solvers and data sets either interactively on the
command line or by writing and referencing your own YAML configuration files.
See the [Benchopt documentation](https://benchopt.github.io/) for more details.

## Compiling the Paper

To compile the LaTeX source of the paper, ensure you have a LaTeX distribution
installed, then run:

```bash
latexmk -pdf -interaction=nonstopmode main.tex
```

## Code in Paper

The scripts in `code/` are lightweight examples for generating figures and
demonstrating package usage. They are not intended to be strict, byte-for-byte
reproducibility pipelines. For a fully reproducible environment, use the Nix
setup in the next section.

Run these from the repository root. Output figures are written to `images/` (the
directory is created automatically if missing).

### R Example

To run the R examples, you need to have `SLOPE`, `knitr`, `here`, and `lars`
installed:

```r
install.packages(c("SLOPE", "knitr", "here", "lars"))
```

Then, you can run the example script:

```r
Rscript code/example.R
```

### Python Example

For Python, you need `sortedl1`, `matplotlib`, and `scikit-learn` installed:

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
[libslope](https://github.com/jolars/libslope) (version 6.5.0 was used for the
paper), Eigen 3.4 or later, and CMake 3.15 or later. If libslope is not already
installed on your system, you can build and install it from source with:

```bash
git clone --depth 1 --branch v6.5.0 https://github.com/jolars/libslope.git
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

The Nix environment described in [Nix Environment](#nix-environment) provides
libslope and builds the example for you, in which case you only have to run
`slope-example`.

### Plots

Code for generating the plots in the paper are provided in `code/plot_*.py`
files. In addition to the dependencies mentioned in
[Python Example](#python-example), you also need `pandas`, `numpy`, `scipy`, and
`pyarrow` (to read the benchmark results, which are stored as Parquet files)
installed to run these:

```bash
pip install pandas numpy scipy pyarrow
```

You can then run the plotting scripts with:

```bash
python code/plot_benchmark_path.py
python code/plot_benchmark_real.py
python code/plot_benchmark_simul.py
python code/plot_thresholding.py
```

## Real Data Analysis Example

In `code/real-data.R`, we provide an extended example using the R `SLOPE`
package, which is described in Section 6 in the paper. In addition to `SLOPE`
and `here` from the [R Example](#r-example), this requires the dependencies
`caret`, `pROC`, `glmnet`, and `MLmetrics`:

```r
install.packages(c("caret", "pROC", "glmnet", "MLmetrics"))
```

Then, you can run the real data analysis script with:

```r
Rscript code/real-data.R
```

## Nix Environment

A Nix flake is provided for setting up a reproducible development environment.
To enter the Nix shell, run:

```bash
nix develop
```

Each of the benchmark directories also contain `flake.nix` files that correspond
to the exact dependencies used when running the benchmarks.

If you have [direnv](https://direnv.net/) installed, we provide `.envrc` files
for automatic environment loading, and you only have to enter the directories to
activate the corresponding Nix shell.

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
