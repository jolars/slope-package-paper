import numpy as np
from modules import path_solver
from scipy import sparse

from .base import SolverBase


class Solver(SolverBase):
    name = "SlopePath"

    def set_objective(self, X, y, alphas, fit_intercept):
        self.X, self.y, self.alphas = X, y, alphas * X.shape[0]
        self.fit_intercept = fit_intercept

    def skip(self, X, y, alphas, fit_intercept):
        if fit_intercept:
            return True, f"{self.name} does not handle intercept fitting"

        if sparse.issparse(X):
            return True, f"{self.name} does not handle sparse design matrices"

        return False, None

    def run(self, it):
        sol, _, _ = path_solver(
            self.X,
            self.y,
            self.alphas,
            k_max=it,
            rtol_pattern=1e-10,
            atol_pattern=1e-10,
            rtol_gamma=1e-10,
            split_max=1e1,
            log=0,
        )

        self.w = np.hstack((np.array([0.0]), sol))

    def get_result(self):
        return {"beta": self.w}
