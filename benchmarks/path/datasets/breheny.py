import os
import urllib.request

import appdirs
import numpy as np
from rpy2 import robjects
from rpy2.robjects import default_converter, numpy2ri
from rpy2.robjects.conversion import localconverter
from scipy import sparse
from scipy.sparse import csc_array
from sklearn.feature_selection import VarianceThreshold
from sklearn.preprocessing import MaxAbsScaler, StandardScaler


def fetch_breheny(dataset: str):
    if os.environ.get("SLOPE_BENCHMARK_OFFLINE") == "1":
        from .prepared import raw_path
        path = str(raw_path(dataset + ".rds"))
    else:
        base_dir = appdirs.user_cache_dir("benchmark_slope_path")

        path = os.path.join(base_dir, dataset + ".rds")

        # download raw data unless it is stored in data folder already
        if not os.path.isfile(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            url = (
                f"https://github.com/IowaBiostat/data-sets/raw/main/{dataset}/{dataset}.rds"
            )
            urllib.request.urlretrieve(url, path)

    read_rds = robjects.r["readRDS"]

    # `numpy2ri.activate()` is deprecated (and raises in recent rpy2), so use a
    # local converter to turn the R arrays into numpy arrays instead.
    np_cv_rules = default_converter + numpy2ri.converter
    with localconverter(np_cv_rules):
        data = read_rds(path)
        X = np.asarray(data[0])
        y = np.asarray(data[1])

    density = np.sum(X != 0) / X.size

    if density <= 0.2:
        X = csc_array(X)

    return X, y


class Dataset:
    name = "breheny"

    def __init__(self, dataset="brca1", standardize=True):
        self.dataset = dataset
        self.standardize = standardize

    def get_data(self):
        X, y = fetch_breheny(self.dataset)

        if self.standardize:
            X = VarianceThreshold().fit_transform(X)

            if sparse.issparse(X):
                X = MaxAbsScaler().fit_transform(X).tocsc()
            else:
                X = StandardScaler().fit_transform(X)

        return {"X": X, "y": y}
