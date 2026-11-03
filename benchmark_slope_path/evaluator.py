"""Check every point of a path independently of the solver's stopping rule."""

import numpy as np
from metewand import Evaluation, serve_evaluator

try:
    from .artifacts import read_objective, read_result
except ImportError:
    from artifacts import read_objective, read_result


def evaluate(context):
    target = context.semantics["one_shot_completion"]["max_rel_duality_gap"]
    objective = read_objective(context, target)
    result = read_result(context.result_dir)
    coefs, intercepts = result["coefs"], result["intercepts"]
    if coefs.shape != (
        objective.n_features,
        objective.actual_path_length,
    ) or intercepts.shape != (objective.actual_path_length,):
        return Evaluation({}, "invalid")
    if not np.all(np.isfinite(coefs)) or not np.all(np.isfinite(intercepts)):
        return Evaluation({}, "invalid")
    if not objective.fit_intercept and np.any(intercepts != 0):
        return Evaluation({}, "invalid")
    metrics = objective.evaluate_result(**result)
    if not all(np.isfinite(value) for value in metrics.values()):
        return Evaluation({}, "invalid")
    if (
        metrics["min_rel_duality_gap"]
        < context.semantics["validity"]["relative_gap_floor"]
    ):
        return Evaluation({}, "invalid")
    verdict = "reached" if metrics["max_rel_duality_gap"] <= target else "not_reached"
    return Evaluation({name: float(value) for name, value in metrics.items()}, verdict)


if __name__ == "__main__":
    serve_evaluator(evaluate)
