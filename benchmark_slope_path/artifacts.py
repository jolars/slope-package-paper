"""Preserve data, the shared alpha grid, and path coefficients across workers."""

from pathlib import Path

import numpy as np
from metewand import Artifact, Dataset, Result, read_json
from scipy import sparse

try:
    from .objective import Objective
except ImportError:
    from objective import Objective

GRID_PARAMETERS = ("path_length", "q", "fit_intercept")


def write_dataset(X, y, objective, directory):
    directory = Path(directory)
    is_sparse = sparse.issparse(X)
    filename = "X.npz" if is_sparse else "X.npy"
    if is_sparse:
        sparse.save_npz(directory / filename, sparse.csc_matrix(X), compressed=False)
    else:
        np.save(directory / filename, X, allow_pickle=False)
    arrays = {
        "y": np.asarray(y).reshape(-1),
        "alphas": objective.alphas,
        "lambdas": objective.lambdas,
    }
    for name, value in arrays.items():
        np.save(directory / f"{name}.npy", value, allow_pickle=False)
    return Dataset(
        {
            "sparse": is_sparse,
            "n_samples": X.shape[0],
            "n_features": X.shape[1],
            "problem_parameters": {
                name: getattr(objective, name) for name in GRID_PARAMETERS
            },
        },
        [
            Artifact(name, "application/octet-stream")
            for name in [filename, "y.npy", "alphas.npy", "lambdas.npy"]
        ],
    )


def read_objective(context, target_rel_duality_gap=1e-7):
    directory = Path(context.dataset_dir)
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
    X = (
        sparse.load_npz(directory / "X.npz").tocsc()
        if metadata["sparse"]
        else np.load(directory / "X.npy", allow_pickle=False)
    )
    y, alphas, lambdas = (
        np.load(directory / f"{name}.npy", allow_pickle=False)
        for name in ("y", "alphas", "lambdas")
    )
    if X.shape != (metadata["n_samples"], metadata["n_features"]) or y.shape != (
        X.shape[0],
    ):
        raise ValueError("Dataset dimensions disagree with their metadata")
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
    for name, value in (("coefs", coefs), ("intercepts", intercepts)):
        np.save(Path(directory) / f"{name}.npy", value, allow_pickle=False)
    return Result(
        {"coefficients": "coefs.npy", "intercepts": "intercepts.npy"},
        [
            Artifact(f"{name}.npy", "application/octet-stream")
            for name in ("coefs", "intercepts")
        ],
    )


def read_result(directory):
    return {
        name: np.load(Path(directory) / f"{name}.npy", allow_pickle=False)
        for name in ("coefs", "intercepts")
    }
