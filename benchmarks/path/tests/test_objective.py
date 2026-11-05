import json
from pathlib import Path
from statistics import NormalDist
from types import SimpleNamespace

import numpy as np
import pytest

from benchmarks.path.artifacts import (
    read_objective,
    write_dataset,
    write_preparation,
    write_result,
)
from benchmarks.path.evaluator import evaluate
from benchmarks.path.objective import Objective
from benchmarks.path.solvers.pgd import Solver


def test_intercept_dual_point_is_centered():
    objective = Objective(path_length=1, fit_intercept=True)
    objective.set_data(np.array([[-1.0], [1.0]]), np.ones(2), np.ones(1), np.ones(1))
    metrics = objective.evaluate_result(np.zeros((1, 1)), np.array([0.75]))
    assert metrics["max_abs_duality_gap"] == 0.03125
    solver = Solver()
    solver.set_objective(**objective.get_objective())
    assert solver._primal_dual_gap(np.zeros(1), 0.75, np.ones(1)) == 0.03125


def test_analytic_pooled_path_and_independent_certificate():
    root = Path(__file__).parents[1] / "reference"
    context = SimpleNamespace(
        dataset_dir=root / "dataset",
        problem_dir=root / "problem",
        problem_parameters={"path_length": 5, "q": 0.2, "fit_intercept": False},
    )
    objective = read_objective(context)
    raw = np.array([NormalDist().inv_cdf(1 - j * 0.2 / 6) for j in range(1, 4)])
    np.testing.assert_allclose(objective.lambdas, raw)
    result = np.load(root / "result" / "coefs.npy")
    primals = []
    for i, alpha in enumerate(objective.alphas):
        weights = objective.lambdas * alpha
        shifted = objective.y - 3 * weights
        expected = np.maximum([shifted[:2].mean(), shifted[:2].mean(), shifted[2]], 0)
        np.testing.assert_allclose(result[:, i], expected, atol=1e-14)
        certificate = (objective.y - expected) / 3
        np.testing.assert_allclose(sum(certificate[:2]), sum(weights[:2]), atol=1e-14)
        primals.append(sum((objective.y - expected) ** 2) / 6 + weights @ expected)
    metrics = objective.evaluate_result(result, np.zeros(len(objective.alphas)))
    assert abs(metrics["max_rel_duality_gap"]) < 1e-10
    np.testing.assert_allclose(metrics["value"], np.mean(primals))


def make_context(tmp_path):
    dataset_dir, result_dir = tmp_path / "data", tmp_path / "result"
    dataset_dir.mkdir()
    result_dir.mkdir()
    objective = Objective(path_length=5, q=0.2)
    objective.set_data(np.eye(3), np.array([3.2, 3.1999, 1.0]))
    dataset = write_dataset(objective.X, objective.y, dataset_dir)
    problem_dir = tmp_path / "problem"
    problem_dir.mkdir()
    prepared = write_preparation(objective, problem_dir)
    (problem_dir / "data.json").write_text(json.dumps(prepared.data))
    (dataset_dir / "data.json").write_text(json.dumps(dataset.data))
    context = SimpleNamespace(
        dataset_dir=dataset_dir,
        problem_dir=problem_dir,
        result_dir=result_dir,
        problem_parameters={"path_length": 5, "q": 0.2, "fit_intercept": False},
        semantics={
            "validity": {"relative_gap_floor": -1e-10},
            "one_shot_completion": {"max_rel_duality_gap": 1e-7},
        },
    )
    return context, objective


@pytest.mark.parametrize(
    "gap,verdict",
    [
        (2e-7, "not_reached"),
        (1e-7, "reached"),
        (np.nextafter(1e-7, np.inf), "not_reached"),
        (np.nextafter(1e-7, 0), "reached"),
        (5e-8, "reached"),
    ],
)
def test_completion_uses_the_maximum_unrounded_gap(tmp_path, monkeypatch, gap, verdict):
    context, objective = make_context(tmp_path)
    write_result(**objective.get_one_result(), directory=context.result_dir)
    monkeypatch.setattr(
        Objective,
        "evaluate_result",
        lambda self, **result: {"max_rel_duality_gap": gap, "min_rel_duality_gap": 0},
    )
    evaluation = evaluate(context)
    assert evaluation.verdict == verdict
    assert evaluation.metrics["max_rel_duality_gap"] == gap


@pytest.mark.parametrize("invalid", ["shape", "intercept_shape", "nan", "intercept"])
def test_invalid_paths_have_no_fabricated_metrics(tmp_path, invalid):
    context, objective = make_context(tmp_path)
    result = objective.get_one_result()
    if invalid == "shape":
        result["coefs"] = result["coefs"][:, :-1]
    elif invalid == "intercept_shape":
        result["intercepts"] = result["intercepts"][:, None]
    elif invalid == "nan":
        result["coefs"][0, -1] = np.nan
    else:
        result["intercepts"][0] = 1
    write_result(**result, directory=context.result_dir)
    evaluation = evaluate(context)
    assert evaluation.verdict == "invalid"
    assert evaluation.metrics == {}


def test_negative_gap_at_any_path_point_is_invalid(tmp_path, monkeypatch):
    context, objective = make_context(tmp_path)
    write_result(**objective.get_one_result(), directory=context.result_dir)
    monkeypatch.setattr(
        Objective,
        "evaluate_result",
        lambda self, **result: {"max_rel_duality_gap": 1e-8, "min_rel_duality_gap": -1},
    )
    assert evaluate(context).verdict == "invalid"


@pytest.mark.parametrize("target", [0, -1, np.inf, np.nan])
def test_target_must_be_finite_and_positive(target):
    with pytest.raises(ValueError, match="strictly positive"):
        Objective(target_rel_duality_gap=target)


def test_zero_primal_has_a_zero_relative_gap():
    objective = Objective(path_length=1)
    objective.set_data(np.eye(2), np.zeros(2), np.ones(1), np.ones(2))
    assert (
        objective.evaluate_result(**objective.get_one_result())["max_rel_duality_gap"]
        == 0
    )
