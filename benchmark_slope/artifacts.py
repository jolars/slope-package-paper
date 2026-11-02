"""Value-preserving NumPy artifacts shared by independent workers."""

from pathlib import Path

import numpy as np
from metewand import Artifact, Dataset, Result, read_json
from scipy import sparse


def write_dataset(X, y, directory):
    directory = Path(directory)
    is_sparse = sparse.issparse(X)
    filename = "X.npz" if is_sparse else "X.npy"
    if is_sparse:
        sparse.save_npz(directory / filename, sparse.csc_matrix(X), compressed=False)
    else:
        np.save(directory / filename, X, allow_pickle=False)
    np.save(directory / "y.npy", np.asarray(y).reshape(-1), allow_pickle=False)
    return Dataset(
        {"sparse": is_sparse, "n_samples": X.shape[0], "n_features": X.shape[1]},
        [
            Artifact(filename, "application/octet-stream"),
            Artifact("y.npy", "application/octet-stream"),
        ],
    )


def read_dataset(directory):
    directory = Path(directory)
    metadata = read_json(directory / "data.json")
    if metadata["sparse"]:
        X = sparse.load_npz(directory / "X.npz").tocsc()
    else:
        X = np.load(directory / "X.npy", allow_pickle=False)
    y = np.load(directory / "y.npy", allow_pickle=False)
    if X.shape != (metadata["n_samples"], metadata["n_features"]) or y.shape != (
        X.shape[0],
    ):
        raise ValueError("Dataset dimensions disagree with their metadata")
    return X, y


def write_result(beta, directory):
    np.save(Path(directory) / "beta.npy", beta, allow_pickle=False)
    return Result(
        {"coefficients": "beta.npy"}, [Artifact("beta.npy", "application/octet-stream")]
    )


def read_result(directory):
    return np.load(Path(directory) / "beta.npy", allow_pickle=False)
