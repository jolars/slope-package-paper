# Efficient Solvers for SLOPE in R, Python, Julia, and C++
Johan Larsson, Małgorzata Bogdan, Krystyna Grzesiak, Mathurin
Massias, Jonas Wallin
2026-10-26

### Citation

Submitted to Computo.

### Badges

[![build and publish](https://github.com/jolars/slope-package-paper/actions/workflows/build.yml/badge.svg)](https://github.com/jolars/slope-package-paper/actions/workflows/build.yml) [![reviews](https://img.shields.io/badge/review-report-blue)](https://github.com/jolars/slope-package-paper/issues?q=is%3Aopen+is%3Aissue+label%3Areview) [![SWH](https://archive.softwareheritage.org/badge/origin/https://github.com/jolars/slope-package-paper)](https://archive.softwareheritage.org/browse/origin/?origin_url=https://github.com/jolars/slope-package-paper) [![DOI:10.5072/computo.0000](https://img.shields.io/badge/DOI-10.5072%2Fcomputo.0000-034E79.svg)](https://doi.org/10.5072/computo.0000) [![Creative Commons License](https://i.creativecommons.org/l/by/4.0/80x15.png)](http://creativecommons.org/licenses/by/4.0/)

### Authors’ affiliations

- Johan Larsson (University of Copenhagen)
- Małgorzata Bogdan (University of Wrocław)
- Krystyna Grzesiak (University of Wrocław)
- Mathurin Massias (Inria, ENS de Lyon, CNRS, Université Claude Bernard Lyon 1)
- Jonas Wallin (Lund University)

### Abstract

We present a suite of packages in R, Python, Julia, and C++ that
efficiently solve the Sorted L-One Penalized Estimation (SLOPE) problem.
The packages feature a highly efficient hybrid coordinate descent
algorithm that fits generalized linear models (GLMs) and supports a
variety of loss functions, including Gaussian, binomial, Poisson, and
multinomial logistic regression. Our implementation is designed to be
fast, memory-efficient, and flexible. The packages support a variety of
data structures (dense, sparse, and out-of-memory matrices) and are
designed to efficiently fit the full SLOPE path as well as handle
cross-validation of SLOPE models, including the relaxed SLOPE. We
present examples of how to use the packages and benchmarks that
demonstrate the performance of the packages on both real and simulated
data and show that our packages generally outperform existing
implementations of SLOPE in terms of speed.
