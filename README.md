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
  benchmarks for comparing SLOPE solvers: Metewand for single-penalty problems and
  Benchopt for full path fitting
- **Results** (`results/`): Benchmark outputs with performance comparisons
  across solvers
- **Analysis Code** (`code/`, `slopeutils/`): R and Python scripts for
  reproducing figures and analyses from the paper
- **Manuscript** (`main.tex`, `main.pdf`, `tex/`, `els-cas-templates/`): LaTeX
  source, compiled paper, and the Elsevier CAS templates

<details>
<summary>Directory tree</summary>

```
.
├── benchmark_slope/            # Metewand benchmark for single-penalty problems
│   ├── datasets/               # Benchmark datasets
│   ├── solvers/                # Solver implementations
│   ├── objective.py            # Independent objective evaluation
│   └── README.md
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
│   ├── path_1007/              # Path-fitting benchmark results
│   └── single_1007/            # Single-penalty benchmark results
├── slopeutils/                 # Utility functions
│   ├── merge_parquet.py
│   └── plot_utils.py
├── tex/                        # LaTeX macros
│   └── macros.tex
├── bench_config_single.yml     # Metewand configuration for single-penalty
├── bench_config_path.yml       # Benchopt configuration for path-fitting
├── devenv.nix                  # Reproducible development environment
├── devenv.lock                 # Locked Nix inputs
├── Project.toml                # Julia environment for the Julia example
├── Manifest.toml               # Locked Julia dependencies
├── Taskfile.yml                # Task automation
├── main.tex                    # Paper LaTeX source
├── main.bib                    # Bibliography
├── els-cas-templates/          # Elsevier CAS classes, samples, and documentation
└── README.md
```

</details>

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

## CSDA Submission

Run `task csda` to compile the manuscript and cover letter and prepare five
upload files under `_build/csda/`:

- `cover-letter.pdf`: The cover letter.
- `main.pdf`: The manuscript.
- `abstract.txt`: The manuscript abstract as a single ASCII text paragraph.
- `supplementary-code-YYYYMMDD.tar.gz`: The examples, analysis and plotting
  scripts, benchmark sources, configurations, results used by the figures,
  bundled data, and pinned software environment.
- `latex-source-YYYYMMDD.tar.gz`: The flat LaTeX source, bibliography, figures,
  journal templates, and C++ example for Editorial Manager.

The code archive includes the native benchmark, the initialized path benchmark,
and the Metewand source pin and patch. It records source versions in
`source-versions.txt`. It copies tracked files from the
working tree, including local edits, and excludes caches and downloaded data.

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

## Compiling the Paper

To compile the LaTeX source of the paper, ensure you have a LaTeX distribution
installed, then run from the repository root:

```bash
latexmk -pdf -interaction=nonstopmode main.tex
```

The `.latexmkrc` file makes LaTeX and BibTeX use the Elsevier CAS files in
`els-cas-templates/`. The directory also contains the original sample files and
documentation for comparison.

## Code in Paper

The scripts in `code/` are lightweight examples for generating figures and
demonstrating package usage. They are not intended to be strict, byte-for-byte
reproducibility scripts. Follow the installation instructions for each
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
figures without running the benchmarks. To plot a new run, change `results_dir`
in the relevant script to a directory containing that run's Parquet files. The
scripts combine all Parquet files in that directory.

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
package, which is described in Section 6 in the paper. Install these packages in
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

The reusable benchmark repositories describe their dependencies without fixing a
complete environment. The paper repository owns the reproducible workflow. Its native sources and
path submodule revision fix the benchmark code, while Devenv fixes the software
closure used to execute it. The generated OCI image carries that same
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

The author-created materials in this repository use two licenses:

- **Preprint and documentation:** Author-released preprint versions, their
  LaTeX source, corresponding PDFs, original figures, and author-created
  documentation use [CC BY 3.0](LICENSE-PAPER). Previously released versions
  remain licensed under CC BY 3.0. This license does not automatically cover
  a later accepted manuscript or the final published article.
- **Software code** (Python, R, benchmarks): [GPL-3.0](LICENSE-CODE).

Third-party materials, including the Elsevier CAS templates, retain their own
licenses. See [LICENSE](LICENSE) for the full scope of this notice.
