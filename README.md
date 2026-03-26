# Efficient Solvers for SLOPE in R, Python, Julia, and C++

[![arXiv](https://img.shields.io/badge/arXiv-2511.02430-b31b1b.svg)](https://arxiv.org/abs/2511.02430)

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
- J(β, λ) is the sorted ℓ₁ norm: J(β; λ) = Σⱼ λⱼ |β(j)|
- λ is a non-increasing sequence of penalty weights
- |β(1)| ≥ |β(2)| ≥ ... ≥ |β(p)| are the sorted absolute coefficients

SLOPE generalizes both the lasso (constant λ) and OSCAR (linearly decreasing λ),
with the unique property of clustering coefficients by setting them to equal
magnitudes.

## Repository Structure

This repository is organized into several key components:

- **Benchmarks** (`benchmark_slope/`, `benchmark_slope_path/`): Two Benchopt
  benchmarks for comparing SLOPE solvers—one for single-penalty problems and one
  for full path fitting
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
│   ├── plot_benchmark_simul.py # for real data
│   ├── example.R               # Usage examples for paper
│   └── real-data.R             # Real data analysis for paper
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
├── Taskfile.yml                # Task automation
├── main.tex                    # Paper LaTeX source
├── main.bib                    # Bibliography
└── README.md
```

</details>

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
in the benchmarks at the time of running them. See [Nix
Environment](#nix-environment) below for more details.

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
latexmk -interaction=nonstopmode main.tex
```

## Code in Paper

R and Python scripts for reproducing the figures and analyses in the paper are
located in the `code/` directory. You can run these scripts after ensuring that
the required dependencies are installed.

## Nix Environment {#nix-environment}

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
  title = {Efficient Solvers for {{SLOPE}} in {{R}}, {{Python}}, {{Julia}}, and {{C}}++},
  author = {Larsson, Johan and Bogdan, Malgorzata and Grzesiak, Krystyna and Massias, Mathurin and Wallin, Jonas},
  date = {2025-11-04},
  eprint = {2511.02430},
  eprinttype = {arXiv},
  eprintclass = {stat},
  doi = {10.48550/arXiv.2511.02430},
  url = {http://arxiv.org/abs/2511.02430},
  urldate = {2025-11-05},
  pubstate = {prepublished},
  keywords = {Computer Science - Mathematical Software,Computer Science - Software Engineering,slope,software,Statistics - Computation,Statistics - Machine Learning}
}
```

## License

This repository is dual-licensed:

- **Paper and Documentation** (LaTeX files, PDFs, markdown, images):
  [CC-BY-3.0](LICENSE-PAPER)
- **Software Code** (Python, R, benchmarks): [GPL-3.0](LICENSE-CODE)

See [LICENSE](LICENSE) for the complete dual license notice.
