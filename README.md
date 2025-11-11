# The SLOPE Package Suite

[![arXiv](https://img.shields.io/badge/arXiv-2511.02430-b31b1b.svg)](https://arxiv.org/abs/2511.02430)

This repository contains the research paper **"Efficient Solvers for SLOPE in R, Python, Julia, and C++"** and associated benchmarking code.

## Paper Summary

The paper presents a suite of packages across multiple programming languages (R, Python, Julia, and C++) for efficiently solving the Sorted L-One Penalized Estimation (SLOPE) problem. SLOPE is a type of regularized regression that uses a sorted ℓ₁ norm penalty, which allows it to perform variable selection and coefficient clustering simultaneously.

### Key Contributions

- **Multi-language Implementation**: High-performance SLOPE solvers available in R, Python, Julia, and C++
- **Hybrid Algorithm**: Implementation of a state-of-the-art hybrid coordinate descent algorithm that combines proximal gradient descent with coordinate descent on collapsed cluster structures
- **Generalized Linear Models**: Support for multiple GLM families including Gaussian, binomial, Poisson, and multinomial logistic regression
- **Flexible Data Structures**: Efficient handling of dense, sparse, and out-of-memory matrices
- **Full Path Fitting**: Efficient computation of the entire regularization path
- **Cross-validation Support**: Built-in support for model selection via cross-validation, including relaxed SLOPE

### What is SLOPE?

SLOPE solves the following optimization problem:

```
minimize F(β₀, β) + α J_λ(β)
```

where:

- F is a smooth convex loss function (e.g., from GLMs)
- J*λ is the sorted ℓ₁ norm: J*λ(β) = Σⱼ λⱼ |β\_(j)|
- λ is a non-increasing sequence of penalty weights
- |β*(1)| ≥ |β*(2)| ≥ ... ≥ |β\_(p)| are the sorted absolute coefficients

SLOPE generalizes both the lasso (constant λ) and OSCAR (linearly decreasing λ), with the unique property of clustering coefficients by setting them to equal magnitudes.

### Performance

The benchmarks demonstrate that the packages significantly outperform existing SLOPE implementations in terms of computational speed, making SLOPE practical for large-scale applications.

## Repository Structure

This repository is organized into several key components:

- **Benchmarks** (`benchmark_slope/`, `benchmark_slope_path/`): Two Benchopt benchmarks for comparing SLOPE solvers—one for single-penalty problems and one for full path fitting
- **Results** (`results/`): Benchmark outputs with performance comparisons across solvers
- **Analysis Code** (`code/`, `scripts/`, `slopeutils/`): R and Python scripts for reproducing figures and analyses from the paper
- **Manuscript** (`main.tex`, `main.pdf`, `tex/`): LaTeX source and compiled paper
- **Reproducibility Infrastructure**: Apptainer container definitions, PBS cluster scripts, and Nix flake for reproducible environments

<details>
<summary>📁 <b>Full directory tree</b></summary>

```
.
├── benchmark_slope/           # Benchopt benchmark for single-penalty problems
│   ├── datasets/              # Benchmark datasets
│   ├── solvers/               # Solver implementations
│   ├── objective.py           # Benchmark objective definition
│   └── README.rst
├── benchmark_slope_path/      # Benchopt benchmark for path fitting
│   ├── datasets/
│   ├── solvers/
│   ├── objective.py
│   └── README.md
├── code/                      # Analysis and visualization scripts
│   ├── example.R              # Usage examples
│   └── real-data.R            # Real data analysis
├── images/                    # Generated figures from paper
│   ├── benchmark_path_real.pdf
│   ├── benchmark_single_real.pdf
│   ├── benchmark_single_simulated.pdf
│   └── ...
├── results/                   # Benchmark results
│   ├── path_0613/
│   ├── path_0623/
│   └── single_0612/
├── scripts/                   # Python plotting scripts
│   ├── plot_benchmark_path.py
│   ├── plot_benchmark_real.py
│   └── plot_benchmark_simul.py
├── slopeutils/                # Utility functions
│   ├── merge_parquet.py
│   └── plot_utils.py
├── tex/                       # LaTeX macros and sections
│   └── macros.tex
├── apptainer_single.def       # Container for single-penalty benchmark
├── apptainer_path.def         # Container for path-fitting benchmark
├── container_single.sif       # Built container image
├── container_path.sif         # Built container image
├── pbs_config.sh              # PBS cluster configuration
├── pbs_submit.sh              # PBS job submission scripts
├── pbs_worker.sh              # PBS worker scripts
├── flake.nix                  # Nix flake for reproducible environment
├── Taskfile.yml               # Task automation
├── main.tex                   # Paper LaTeX source
├── main.pdf                   # Compiled paper
├── main.bib                   # Bibliography
└── README.md
```

</details>

## Running Benchmarks

The benchmarks use [Benchopt](https://benchopt.github.io/), a benchmarking framework for optimization algorithms. Each benchmark directory contains its own README with specific instructions.

### Single-Penalty Benchmark

```bash
cd benchmark_slope
# Follow instructions in benchmark_slope/README.rst
```

### Path-Fitting Benchmark

```bash
cd benchmark_slope_path
# Follow instructions in benchmark_slope_path/README.md
```

### Using Containers

For reproducible results, use the provided Apptainer containers:

```bash
apptainer run container_single.sif
# or
apptainer run container_path.sif
```

## Authors

- Johan Larsson (University of Copenhagen)
- Małgorzata Bogdan (University of Wrocław)
- Krystyna Grzesiak (University of Wrocław)
- Mathurin Massias (Inria, ENS de Lyon, CNRS)
- Jonas Wallin (Lund University)

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

See `LICENSE.md` for details.
