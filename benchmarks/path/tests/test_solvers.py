from importlib import import_module

import numpy as np
import pytest

from benchmarks.path.datasets.simulated import Dataset
from benchmarks.path.objective import Objective


@pytest.mark.parametrize(
    "module,parameters,control",
    [
        ("sortedl1_solver", {"cd_type": "permuted"}, 1e-10),
        ("pgd", {"acceleration": "fista"}, 1e-10),
        ("admm", {"rho": 100}, 1e-9),
        ("solution_path", {}, 10000),
        ("rslope", {}, 1e-10),
    ],
)
@pytest.mark.parametrize(
    "density,intercept", [(1.0, False), (0.2, False), (1.0, True), (0.2, True)]
)
def test_native_solvers_reach_the_shared_path_target(
    module, parameters, control, density, intercept
):
    if module == "rslope":
        packages = pytest.importorskip("rpy2.robjects.packages")
        if not packages.isinstalled("SLOPE"):
            pytest.skip("The optional R SLOPE package is unavailable")
    values = Dataset(
        n_samples=40, n_features=20, n_signals=5, rho=0.2, X_density=density
    ).get_data()
    objective = Objective(path_length=5, q=0.2, fit_intercept=intercept)
    objective.set_data(**values)
    solver = import_module(f"benchmarks.path.solvers.{module}").Solver(
        **parameters
    )
    skipped, reason = solver.skip(**objective.get_objective())
    if skipped:
        assert module == "solution_path" and (density < 1 or intercept)
        assert reason
        return
    solver.set_objective(**objective.get_objective())
    solver.run(control)
    metrics = objective.evaluate_result(**solver.get_result())
    assert metrics["min_rel_duality_gap"] >= -1e-10
    assert metrics["max_rel_duality_gap"] <= 1e-7


def test_solution_path_interpolates_without_reordering_alphas():
    from benchmarks.path.solvers.solution_path import Solver

    solver = Solver()
    solver.n_features = 2
    solver.alphas = np.array([4, 3, 2, 1, 0.5])
    actual = solver._interpolate_coefs([3, 1], [np.array([0.0, 2]), np.array([4.0, 6])])
    np.testing.assert_array_equal(actual, [[0, 0, 2, 4, 4], [2, 2, 4, 6, 6]])
