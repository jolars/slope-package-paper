"""Run clean path fits at successive tolerances or exact-path iteration limits."""

import sys
from importlib import import_module, metadata

import numpy as np
from artifacts import read_objective, write_result
from metewand import serve_implementation


def make_solver(context):
    objective = read_objective(context)
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
    solver._initial_result = objective.get_one_result()
    return solver


def warmup(solver, context):
    solver.run(1 if sys.argv[1] == "solution_path" else 0.1)


def execute(solver, context):
    control = context.observation_control
    if control.get("initial", False):
        result = solver._initial_result
    else:
        solver.run(control.get("iterations", control.get("tolerance")))
        result = solver.get_result()
    return write_result(**result, directory=context.output_dir)


def statistics(output, context):
    versions = {}
    for package in (
        "numpy",
        "scipy",
        "scikit-learn",
        "numba",
        "sortedl1",
        "slopepath",
        "rpy2",
        "metewand",
    ):
        try:
            versions[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            pass
    return {"packages": versions}


if __name__ == "__main__":
    serve_implementation(
        prepare=prepare,
        warmup=warmup,
        execute=execute,
        reset=lambda state, context: None,
        check_applicability=applicability,
        statistics=statistics,
    )
