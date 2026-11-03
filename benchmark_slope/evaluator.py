"""Evaluate solver coefficients independently of their convergence claims."""

import numpy as np
from artifacts import read_dataset, read_result
from metewand import Evaluation, serve_evaluator
from objective import Objective


def evaluate(context):
    X, y = read_dataset(context.dataset_dir)
    beta = read_result(context.result_dir)
    target = context.semantics["one_shot_completion"]["rel_duality_gap"]
    objective = Objective(**context.problem_parameters, target_rel_duality_gap=target)
    objective.set_data(X, y)
    if beta.shape != (X.shape[1] + 1,) or not np.all(np.isfinite(beta)):
        return Evaluation({}, "invalid")
    if not objective.fit_intercept and beta[0] != 0:
        return Evaluation({}, "invalid")
    metrics = objective.evaluate_result(beta)
    if not all(np.isfinite(value) for value in metrics.values()):
        return Evaluation({}, "invalid")
    floor = context.semantics["validity"]["relative_gap_floor"]
    if metrics["rel_duality_gap"] < floor:
        return Evaluation({}, "invalid")
    verdict = "reached" if metrics["rel_duality_gap"] <= target else "not_reached"
    return Evaluation({name: float(value) for name, value in metrics.items()}, verdict)


if __name__ == "__main__":
    serve_evaluator(evaluate=evaluate)
