import numpy as np
import pytest
from datasets.correlated import make_correlated_data
from objective import Objective
from scipy import sparse


def test_skglm_iteration_limits_change_the_computation():
    pytest.importorskip("skglm")
    from solvers.skglm import Solver

    X, y, _ = make_correlated_data(
        40, 30, rho=0.2, density=5 / 30, X_density=0.2, random_state=27
    )
    assert sparse.issparse(X)
    objective = Objective(reg=0.1, q=0.2)
    objective.set_data(X, y)
    solver = Solver()
    solver.set_objective(**objective.get_objective())
    solver.run(1)
    first = solver.get_result()["beta"].copy()
    solver.run(1024)
    last = solver.get_result()["beta"]
    assert not np.allclose(first, last)
    assert objective.evaluate_result(first)["rel_duality_gap"] > 1e-3
    assert objective.evaluate_result(last)["rel_duality_gap"] < 1e-7
