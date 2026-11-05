"""Value-preserving NumPy artifacts shared by independent workers."""

from pathlib import Path

import numpy as np
from metewand import Dataset, Result, read_json
from metewand.arrays import read_array, write_array
from scipy import sparse


def write_dataset(X, y, directory):
    directory = Path(directory)
    is_sparse = sparse.issparse(X)
    design = sparse.csc_matrix(X) if is_sparse else np.asarray(X)
    files = [
        write_array(directory, "X", design),
        write_array(directory, "y", np.asarray(y).reshape(-1)),
    ]
    return Dataset(
        {"sparse": is_sparse, "n_samples": X.shape[0], "n_features": X.shape[1]},
        files,
    )


def read_dataset(directory):
    directory = Path(directory)
    metadata = read_json(directory / "data.json")
    if metadata["sparse"]:
        X = read_array(directory, "X.npz").tocsc()
    else:
        X = read_array(directory, "X.npy")
    y = read_array(directory, "y.npy")
    if X.shape != (metadata["n_samples"], metadata["n_features"]) or y.shape != (
        X.shape[0],
    ):
        raise ValueError("Dataset dimensions disagree with their metadata")
    return X, y


def write_result(beta, directory):
    artifact = write_array(directory, "beta", beta)
    return Result({"coefficients": "beta.npy"}, [artifact])


def read_result(directory):
    return read_array(directory, "beta.npy")
