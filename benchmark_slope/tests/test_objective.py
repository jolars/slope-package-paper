from statistics import NormalDist
from types import SimpleNamespace

import numpy as np
import pytest
from artifacts import write_dataset, write_result
from evaluator import evaluate
from objective import Objective


def test_intercept_dual_point_is_centered():
    objective = Objective(fit_intercept=True)
    objective.X = np.array([[-1.0], [1.0]])
    objective.y = np.ones(2)
    objective.alphas = np.ones(1)
    assert objective.evaluate_result(np.array([0.75, 0.0]))["duality_gap"] == 0.03125


def test_analytic_pooled_solution_and_independent_certificate():
    X, y = np.eye(3), np.array([3.2, 3.19, 1.0])
    raw = np.array([NormalDist().inv_cdf(1 - j * 0.2 / 6) for j in range(1, 4)])
    weights = 0.1 * max(np.cumsum(y) / (3 * np.cumsum(raw))) * raw
    shifted = y - 3 * weights
    pooled = shifted[:2].mean()
    beta = np.array([0, pooled, pooled, shifted[2]])
    subgradient = (y - beta[1:]) / 3
    np.testing.assert_allclose(sum(subgradient[:2]), sum(weights[:2]), atol=1e-14)
    assert np.all(subgradient[:2] >= weights[1])
    assert np.all(subgradient[:2] <= weights[0])
    objective = Objective(q=0.2, reg=0.1)
    objective.set_data(X, y)
    metrics = objective.evaluate_result(beta)
    assert abs(metrics["rel_duality_gap"]) < 1e-14
    np.testing.assert_allclose(
        metrics["value"], sum((y - beta[1:]) ** 2) / 6 + weights @ beta[1:]
    )


def make_context(tmp_path):
    import json

    dataset_dir, result_dir = tmp_path / "data", tmp_path / "result"
    dataset_dir.mkdir()
    result_dir.mkdir()
    dataset = write_dataset(np.eye(3), np.array([3.2, 3.19, 1.0]), dataset_dir)
    (dataset_dir / "data.json").write_text(json.dumps(dataset.data))
    return SimpleNamespace(
        dataset_dir=dataset_dir,
        result_dir=result_dir,
        problem_parameters={"q": 0.2, "reg": 0.1, "fit_intercept": False},
        semantics={
            "validity": {"relative_gap_floor": -1e-10},
            "one_shot_completion": {"rel_duality_gap": 1e-7},
        },
    )


@pytest.mark.parametrize(
    "beta", [np.zeros(3), np.full(4, np.nan), np.array([1.0, 0, 0, 0])]
)
def test_invalid_coefficients_have_no_fabricated_metrics(tmp_path, beta):
    context = make_context(tmp_path)
    write_result(beta, context.result_dir)
    result = evaluate(context)
    assert result.verdict == "invalid"
    assert result.metrics == {}


def test_completion_uses_the_declared_target(tmp_path):
    context = make_context(tmp_path)
    write_result(np.zeros(4), context.result_dir)
    assert evaluate(context).verdict == "not_reached"
    context.semantics["one_shot_completion"]["rel_duality_gap"] = 2
    assert evaluate(context).verdict == "reached"


def test_negative_gap_beyond_roundoff_is_invalid(tmp_path, monkeypatch):
    context = make_context(tmp_path)
    write_result(np.zeros(4), context.result_dir)
    monkeypatch.setattr(
        Objective,
        "evaluate_result",
        lambda self, beta: {
            "value": 1.0,
            "duality_gap": -1.0,
            "rel_duality_gap": -1.0,
            "target_rel_duality_gap": 1e-7,
        },
    )
    assert evaluate(context).verdict == "invalid"


def test_target_relative_duality_gap_must_be_positive():
    with pytest.raises(ValueError, match="strictly positive"):
        Objective(target_rel_duality_gap=0)
