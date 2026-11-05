import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from scipy import sparse
from sortedl1 import Slope

from benchmarks.path.artifacts import (
    read_objective,
    write_dataset,
    write_preparation,
)
from benchmarks.path.datasets.simulated import Dataset
from benchmarks.path.objective import Objective


@pytest.mark.parametrize("density", [1.0, 0.2])
@pytest.mark.parametrize("intercept", [False, True])
def test_simulations_and_grids_match_the_original_benchmark(density, intercept):
    fixtures = Path(__file__).parent / "fixtures"
    expected = np.load(fixtures / f"simulated-{density}.npz")
    values = Dataset(
        n_samples=8, n_features=6, n_signals=3, rho=0.6, X_density=density
    ).get_data()
    X, y = values["X"], values["y"]
    np.testing.assert_array_equal(
        X.toarray() if sparse.issparse(X) else X, expected["X"]
    )
    np.testing.assert_array_equal(y, expected["y"])
    objective = Objective(path_length=5, q=0.2, fit_intercept=intercept)
    objective.set_data(X, y)
    grid = np.load(fixtures / f"grid-{density}-{intercept}.npz")
    np.testing.assert_array_equal(objective.alphas, grid["alphas"])
    np.testing.assert_array_equal(objective.lambdas, grid["lambdas"])


@pytest.mark.parametrize("sparse_input", [False, True])
def test_shared_grid_roundtrip_never_refits_the_path(
    tmp_path, monkeypatch, sparse_input
):
    X, y = np.eye(3), np.array([3.2, 3.1999, 1.0])
    if sparse_input:
        X = sparse.csc_array(X)
    objective = Objective(path_length=5, q=0.2)
    objective.set_data(X, y)
    objective.set_data(X, y, objective.alphas[:3], objective.lambdas)
    dataset_dir, problem_dir = tmp_path / "data", tmp_path / "problem"
    dataset_dir.mkdir()
    problem_dir.mkdir()
    dataset = write_dataset(X, y, dataset_dir)
    (dataset_dir / "data.json").write_text(json.dumps(dataset.data))
    prepared = write_preparation(objective, problem_dir)
    (problem_dir / "data.json").write_text(json.dumps(prepared.data))

    def fail(*args, **kwargs):
        raise AssertionError("Workers must use the already materialized grid")

    monkeypatch.setattr(Slope, "path", fail)
    context = SimpleNamespace(
        dataset_dir=dataset_dir,
        problem_dir=problem_dir,
        problem_parameters={"path_length": 5, "q": 0.2, "fit_intercept": False},
    )
    actual = read_objective(context)
    assert sparse.issparse(actual.X) == sparse_input
    np.testing.assert_array_equal(actual.alphas, objective.alphas)
    np.testing.assert_array_equal(actual.lambdas, objective.lambdas)
    assert actual.actual_path_length == objective.actual_path_length < 5
    context.problem_parameters["path_length"] = 10
    with pytest.raises(ValueError, match="does not match"):
        read_objective(context)
