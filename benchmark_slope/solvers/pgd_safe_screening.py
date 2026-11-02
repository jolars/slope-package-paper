from typing import ClassVar

import numpy as np
from scipy import sparse
from slopescreening.solver.parameters import SlopeParameters
from slopescreening.solver.slope import slope_gp

from .base import SolverBase


class Solver(SolverBase):
    name = "PGD_safe_screening"

    parameters: ClassVar[dict] = {
        "accelerated": [True, False],
    }

    def set_objective(self, X, y, alphas, fit_intercept):
        self.X, self.y, self.alphas = X, y, alphas
        self.fit_intercept = fit_intercept

        self.param = SlopeParameters()
        self.param.accelerated = self.accelerated
        self.param.gap_stopping = 0
        self.param.eval_gap_it = 10
        self.param.verbose = False

    def skip(self, X, y, alphas, fit_intercept):
        if fit_intercept:
            return True, f"{self.name} does not handle intercept fitting"

        if sparse.issparse(X):
            return True, f"{self.name} does not handle sparse design matrices"

        return False, None

    def run(self, it):
        self.param.max_it = it

        self.coef_ = slope_gp(
            self.y, self.X, 1.0, self.alphas * len(self.y), self.param
        )["sol"]

    def get_result(self):
        beta = np.hstack((np.array([0.0]), self.coef_))
        return {"beta": beta}
