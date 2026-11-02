"""The normalized squared-loss objective evaluated over a fixed SLOPE path."""

import numpy as np
from numpy.linalg import norm
from sortedl1 import Slope


class Objective:
    name = "SLOPE_Path"

    def __init__(
        self,
        path_length=100,
        q=0.1,
        fit_intercept=False,
        target_rel_duality_gap=1e-7,
    ):
        if not np.isfinite(target_rel_duality_gap) or target_rel_duality_gap <= 0:
            raise ValueError(
                "target_rel_duality_gap must be finite and strictly positive"
            )
        if path_length < 1:
            raise ValueError("path_length must be strictly positive")
        self.path_length = path_length
        self.q = q
        self.fit_intercept = fit_intercept
        self.target_rel_duality_gap = target_rel_duality_gap

    def set_data(self, X, y, alphas=None, lambdas=None):
        self.X, self.y = X, y
        self.n_samples, self.n_features = X.shape
        if alphas is None or lambdas is None:
            model = Slope(fit_intercept=self.fit_intercept, q=self.q)
            _, _, alphas, lambdas = model.path(X, y, path_length=self.path_length)
        self.alphas, self.lambdas = alphas, lambdas
        self.actual_path_length = len(alphas)

    def get_one_result(self):
        return {
            "coefs": np.zeros((self.n_features, self.actual_path_length)),
            "intercepts": np.zeros(self.actual_path_length),
        }

    def evaluate_result(self, coefs, intercepts):
        primals = np.empty(self.actual_path_length)
        duals = np.empty(self.actual_path_length)
        n = self.n_samples
        for i, alpha in enumerate(self.alphas):
            coef = coefs[:, i]
            weights = self.lambdas * alpha
            residual = self.y - self.X @ coef - intercepts[i]
            primals[i] = (
                residual @ residual / (2 * n) + weights @ np.sort(np.abs(coef))[::-1]
            )
            theta = residual.copy()
            if self.fit_intercept:
                # An unpenalized intercept imposes sum(theta) = 0 in the dual.
                theta -= np.mean(theta)
            theta /= max(1, self._dual_norm_slope(theta, weights))
            duals[i] = (norm(self.y) ** 2 - norm(self.y - theta * n) ** 2) / (2 * n)
        gaps = primals - duals
        with np.errstate(divide="ignore", invalid="ignore"):
            relative_gaps = gaps / primals
        # A zero response has a zero primal and dual at the exact solution.
        relative_gaps[(primals == 0) & (gaps == 0)] = 0
        return {
            "value": np.mean(primals),
            "max_rel_duality_gap": np.max(relative_gaps),
            "min_rel_duality_gap": np.min(relative_gaps),
            "max_abs_duality_gap": np.max(gaps),
            "mean_rel_duality_gaps": np.mean(relative_gaps),
            "mean_abs_duality_gaps": np.mean(gaps),
            "target_rel_duality_gap": self.target_rel_duality_gap,
        }

    def get_objective(self):
        return {
            "X": self.X,
            "y": self.y,
            "fit_intercept": self.fit_intercept,
            "alphas": self.alphas,
            "lambdas": self.lambdas,
        }

    def _dual_norm_slope(self, theta, lambdas):
        gradient = np.sort(np.abs(self.X.T @ theta))[::-1]
        return np.max(np.cumsum(gradient) / np.cumsum(lambdas))
