"""Preserve data, the shared alpha grid, and path coefficients across workers."""

from pathlib import Path

import numpy as np
from metewand import Dataset, Result, read_json
from metewand.arrays import read_array, write_array
from scipy import sparse

try:
    from .objective import Objective
except ImportError:
    from objective import Objective

GRID_PARAMETERS = ("path_length", "q", "fit_intercept")


def write_dataset(X, y, directory):
    is_sparse = sparse.issparse(X)
    design = sparse.csc_matrix(X) if is_sparse else np.asarray(X)
    files = [
        write_array(directory, "X", design),
        write_array(directory, "y", np.asarray(y).reshape(-1)),
    ]
    return Dataset(
        {"sparse": is_sparse, "n_samples": X.shape[0], "n_features": X.shape[1]}, files
    )


def write_preparation(objective, directory):
    return Dataset(
        {
            "problem_parameters": {
                name: getattr(objective, name) for name in GRID_PARAMETERS
            }
        },
        [
            write_array(directory, name, value)
            for name, value in (
                ("alphas", objective.alphas),
                ("lambdas", objective.lambdas),
            )
        ],
    )


def read_dataset(directory):
    directory = Path(directory)
    metadata = read_json(directory / "data.json")
    X = (
        read_array(directory, "X.npz").tocsc()
        if metadata["sparse"]
        else read_array(directory, "X.npy")
    )
    y = read_array(directory, "y.npy")
    if X.shape != (metadata["n_samples"], metadata["n_features"]) or y.shape != (
        X.shape[0],
    ):
        raise ValueError("Dataset dimensions disagree with their metadata")
    return X, y


def read_objective(context, target_rel_duality_gap=1e-7):
    directory = Path(context.problem_dir)
    metadata = read_json(directory / "data.json")
    objective = Objective(
        **context.problem_parameters, target_rel_duality_gap=target_rel_duality_gap
    )
    if metadata["problem_parameters"] != {
        name: getattr(objective, name) for name in GRID_PARAMETERS
    }:
        raise ValueError(
            "The materialized path grid does not match the requested problem"
        )
    X, y = read_dataset(context.dataset_dir)
    alphas, lambdas = (
        read_array(directory, f"{name}.npy") for name in ("alphas", "lambdas")
    )
    if (
        alphas.ndim != 1
        or not 0 < len(alphas) <= objective.path_length
        or lambdas.shape != (X.shape[1],)
    ):
        raise ValueError("The materialized penalty grid has invalid dimensions")
    if (
        not np.all(np.isfinite(alphas))
        or not np.all(np.isfinite(lambdas))
        or np.any(alphas <= 0)
        or np.any(lambdas <= 0)
    ):
        raise ValueError("The materialized penalty weights must be finite and positive")
    if np.any(np.diff(alphas) > 0) or np.any(np.diff(lambdas) > 0):
        raise ValueError("The materialized penalty grid must be nonincreasing")
    objective.set_data(X, y, alphas, lambdas)
    return objective


def write_result(coefs, intercepts, directory):
    files = [
        write_array(directory, name, value)
        for name, value in (("coefs", coefs), ("intercepts", intercepts))
    ]
    return Result({"coefficients": "coefs.npy", "intercepts": "intercepts.npy"}, files)


def read_result(directory):
    return {
        name: read_array(directory, f"{name}.npy") for name in ("coefs", "intercepts")
    }
