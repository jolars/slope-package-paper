"""Read pinned raw inputs from the materializer's declared sources."""

import bz2
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy import sparse
from sklearn.datasets import load_svmlight_file


def raw_path(filename):
    directory = Path(__file__).resolve().parents[1] / "prepared-data"
    try:
        manifest = json.loads((directory / "manifest.json").read_text())
        path = directory / filename
        with path.open("rb") as stream:
            actual = hashlib.file_digest(stream, "sha256").hexdigest()
        expected = manifest["files"][filename]["sha256"]
        if manifest["schema_version"] != 1 or actual != expected:
            raise ValueError(f"Prepared dataset changed: {filename}")
        return path
    except FileNotFoundError as error:
        raise FileNotFoundError("Run benchmark-data-prepare and use its generated manifest") from error


def libsvm(dataset):
    settings = {
        "rcv1.binary": ("rcv1_train.binary.bz2", 47236),
        "real-sim": ("real-sim.bz2", 20958),
        "YearPredictionMSD": ("YearPredictionMSD.bz2", 90),
    }
    filename, features = settings[dataset]
    with bz2.open(raw_path(filename), "rb") as stream:
        X, y = load_svmlight_file(stream, n_features=features)
    if len(X.data) >= 0.5 * X.shape[0] * X.shape[1]:
        X = X.toarray(order="F")
    else:
        X = sparse.csc_matrix(X)
        X.sort_indices()
    return X, np.asarray(y)
