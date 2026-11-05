"""Bind adapter parameters without a dependency on the benchmark runner."""

from typing import ClassVar


class SolverBase:
    parameters: ClassVar[dict] = {}

    def __init__(self, **parameters):
        unknown = parameters.keys() - self.parameters.keys()
        if unknown:
            raise ValueError(f"Unknown solver parameters: {sorted(unknown)}")
        for name, values in self.parameters.items():
            setattr(self, name, parameters.get(name, values[0]))

    def skip(self, X, y, fit_intercept, alphas, lambdas):
        return False, None
