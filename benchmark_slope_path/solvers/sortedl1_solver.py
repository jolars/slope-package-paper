from typing import ClassVar

import numpy as np
from sortedl1 import Slope

from .base import SolverBase


class Solver(SolverBase):
    name = "sortedl1"
    parameters: ClassVar[dict] = {
        "cd_type": ["permuted", "cyclical"],
    }

    def set_objective(self, X, y, fit_intercept, alphas, lambdas):
        self.n_samples, self.n_features = X.shape
        self.X, self.y, self.fit_intercept, self.alphas, self.lambdas = (
            X,
            y,
            fit_intercept,
            alphas,
            lambdas,
        )

        self.model = Slope(
            lam=self.lambdas,
            fit_intercept=self.fit_intercept,
            max_iter=1_000_000,
            solver="hybrid",
            hybrid_cd_type=self.cd_type,
            update_clusters=True,
        )

    def run(self, tol):
        if tol == np.inf:
            self.coefs = np.zeros((self.n_features, len(self.alphas)))
            self.intercepts = np.zeros(len(self.alphas))
        else:
            self.model.tol = tol
            coefs, intercepts, _, _ = self.model.path(
                self.X, self.y, alphas=self.alphas
            )

            self.coefs = coefs[:, 0, :]
            self.intercepts = intercepts[0, :]

    def get_result(self):
        return {"coefs": self.coefs, "intercepts": self.intercepts}
