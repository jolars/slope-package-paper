from math import inf as INFINITY
from typing import ClassVar

import numpy as np
from sortedl1 import Slope

from .base import SolverBase


class Solver(SolverBase):
    name = "sortedl1"
    parameters: ClassVar[dict] = {
        "cd_type": ["cyclical", "permuted"],
    }

    def set_objective(self, X, y, alphas, fit_intercept):
        self.X, self.y, self.lambdas = X, y, alphas
        self.fit_intercept = fit_intercept

        self.model = Slope(
            lam=self.lambdas,
            alpha=1.0,
            fit_intercept=self.fit_intercept,
            max_iter=1_000_000,
            hybrid_cd_type=self.cd_type,
        )

    def run(self, tol):
        if tol == INFINITY:
            self.coef = np.zeros(self.X.shape[1] + 1)
        else:
            self.model.tol = tol
            self.model.fit(self.X, self.y)

            coef = self.model.coef_.flatten()

            if self.fit_intercept:
                self.coef = np.hstack((np.atleast_1d(self.model.intercept_), coef))
            else:
                self.coef = np.hstack(([0.0], coef))

    def get_result(self):
        return {"beta": self.coef}
