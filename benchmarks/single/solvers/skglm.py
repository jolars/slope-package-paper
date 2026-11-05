import warnings

import numpy as np
from skglm import GeneralizedLinearEstimator
from skglm.datafits import Quadratic
from skglm.penalties import SLOPE
from skglm.solvers import FISTA
from sklearn.exceptions import ConvergenceWarning

from .base import SolverBase


class Solver(SolverBase):
    name = "skglm"

    def set_objective(self, X, y, alphas, fit_intercept):
        self.X, self.y, self.lambdas = X, y, alphas
        self.fit_intercept = fit_intercept

        warnings.filterwarnings("ignore", category=ConvergenceWarning)
        warnings.filterwarnings("ignore", category=FutureWarning)
        self.model = GeneralizedLinearEstimator(
            Quadratic(), SLOPE(alphas), FISTA(opt_strategy="fixpoint", tol=1e-20)
        )

        # Cache Numba compilation
        self.run(1)

    def run(self, n_iter):
        if n_iter == 0:
            self.coef = np.zeros(self.X.shape[1] + 1)
        else:
            self.model.solver.max_iter = n_iter
            self.model.fit(self.X, self.y)

            coef = self.model.coef_.flatten()

            if self.fit_intercept:
                self.coef = np.hstack((np.atleast_1d(self.model.intercept_), coef))
            else:
                self.coef = np.hstack(([0.0], coef))

    def skip(self, X, y, alphas, fit_intercept):
        if fit_intercept:
            return True, f"{self.name} does not handle intercept fitting"

        return False, None

    def get_result(self):
        return {"beta": self.coef}
