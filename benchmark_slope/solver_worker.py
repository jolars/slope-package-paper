"""Adapt native solver calls to clean executions and cooperative profiles."""

import sys
from importlib import import_module, metadata

import numpy as np
from artifacts import read_dataset, write_result
from metewand import serve_implementation, stream_callback
from objective import Objective

CALLBACK_SOLVERS = {"python_pgd", "admm", "newt_alm"}


def make_solver(context):
    X, y = read_dataset(context.dataset_dir)
    objective = Objective(**context.problem_parameters)
    objective.set_data(X, y)
    solver = import_module(f"solvers.{sys.argv[1]}").Solver(**context.parameters)
    return solver, objective


def applicability(context):
    solver, objective = make_solver(context)
    excluded, reason = solver.skip(**objective.get_objective())
    return {
        "outcome": "not_applicable" if excluded else "applicable",
        "code": "unsupported_input" if excluded else "supported_input",
        "reason": reason or "The solver supports this configuration.",
    }


def prepare(context):
    np.random.seed(context.seed % 2**32)
    solver, objective = make_solver(context)
    solver.set_objective(**objective.get_objective())
    solver._benchmark_n_features = objective.n_features
    return solver


def execute(solver, context):
    control = context.observation_control
    if control.get("initial", False):
        beta = np.zeros(solver._benchmark_n_features + 1)
    else:
        solver.run(control.get("iterations", control.get("tolerance")))
        beta = solver.get_result()["beta"]
    return write_result(beta, context.output_dir)


def warmup(solver, context):
    if sys.argv[1] in CALLBACK_SOLVERS:
        calls = 0

        def one_update():
            nonlocal calls
            calls += 1
            return calls <= 1

        solver.run(one_update)
    else:
        solver.run(0.1 if sys.argv[1] in {"sortedl1", "rslope"} else 1)


def execute_stream(solver, context):
    with stream_callback(
        context.stream,
        lambda: write_result(solver.get_result()["beta"], context.stream.output_dir),
        work_field="iterations",
    ) as checkpoint:
        solver.run(checkpoint)


def statistics(output, context):
    packages = [
        "numpy",
        "scipy",
        "scikit-learn",
        "numba",
        "sortedl1",
        "tick",
        "skglm",
        "slopepath",
        "slopescreening",
        "metewand",
    ]
    versions = {}
    for package in packages:
        try:
            versions[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            pass
    return {"packages": versions}


if __name__ == "__main__":
    callbacks = {
        "prepare": prepare,
        "warmup": warmup,
        "reset": lambda state, context: None,
        "check_applicability": applicability,
        "statistics": statistics,
    }
    if sys.argv[1] in CALLBACK_SOLVERS:
        callbacks["execute_stream"] = execute_stream
    else:
        callbacks["execute"] = execute
    serve_implementation(**callbacks)
