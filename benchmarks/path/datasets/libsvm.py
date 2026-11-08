from libsvmdata import fetch_libsvm
from scipy import sparse
from sklearn.feature_selection import VarianceThreshold
from sklearn.preprocessing import MaxAbsScaler, StandardScaler


class Dataset:
    name = "libsvm"

    def __init__(self, dataset="YearPredictionMSD", standardize=True):
        self.dataset = dataset
        self.standardize = standardize

    def get_data(self):
        import os
        if os.environ.get("SLOPE_BENCHMARK_OFFLINE") == "1":
            from .prepared import libsvm
            X, y = libsvm(self.dataset)
        else:
            X, y = fetch_libsvm(self.dataset)

        if self.standardize:
            X = VarianceThreshold().fit_transform(X)

            if sparse.issparse(X):
                X = MaxAbsScaler().fit_transform(X).tocsc()
            else:
                X = StandardScaler().fit_transform(X)

        return {"X": X, "y": y}
