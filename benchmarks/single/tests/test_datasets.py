import json
from pathlib import Path

import numpy as np
import pytest
from artifacts import read_dataset, write_dataset
from datasets.correlated import make_correlated_data
from scipy import sparse


@pytest.mark.parametrize("density", [1.0, 0.2])
def test_generator_matches_the_original_benchopt_data(density):
    expected = np.load(Path(__file__).parent / "fixtures" / f"simulated-{density}.npz")
    X, y, _ = make_correlated_data(
        8, 6, rho=0.6, density=0.5, X_density=density, random_state=27
    )
    assert sparse.issparse(X) == (density < 1)
    # Numerical libraries can round generated data differently across platforms.
    np.testing.assert_allclose(
        X.toarray() if sparse.issparse(X) else X,
        expected["X"],
        rtol=1e-13,
        atol=1e-14,
    )
    np.testing.assert_allclose(y, expected["y"], rtol=1e-13, atol=1e-14)


@pytest.mark.parametrize("sparse_input", [False, True])
def test_artifacts_preserve_values_and_sparse_representation(tmp_path, sparse_input):
    X = np.array([[1.0, 0], [0, 2], [3, 0]])
    if sparse_input:
        X = sparse.csc_array(X)
    y = np.arange(3.0)
    data = write_dataset(X, y, tmp_path)
    (tmp_path / "data.json").write_text(json.dumps(data.data))
    actual, target = read_dataset(tmp_path)
    assert sparse.issparse(actual) == sparse_input
    np.testing.assert_array_equal(
        actual.toarray() if sparse_input else actual, X.toarray() if sparse_input else X
    )
    np.testing.assert_array_equal(target, y)


@pytest.mark.parametrize("family", ["libsvm", "breheny"])
@pytest.mark.parametrize("sparse_input", [False, True])
def test_real_dataset_preprocessing_matches_existing_rules(
    monkeypatch, family, sparse_input
):
    from importlib import import_module

    from sklearn.feature_selection import VarianceThreshold
    from sklearn.preprocessing import MaxAbsScaler, StandardScaler

    if family == "breheny":
        pytest.importorskip("rpy2")
    module = import_module(f"datasets.{family}")
    X = np.array([[1.0, 0, 1], [2, 0, 0], [3, 0, 3]])
    if sparse_input:
        X = sparse.csc_array(X)
    y = np.arange(3.0)
    monkeypatch.setattr(
        module,
        "_fetch_libsvm" if family == "libsvm" else "fetch_breheny",
        lambda dataset: (X, y),
    )
    actual = module.Dataset(dataset="fixture", standardize=True).get_data()
    selected = VarianceThreshold().fit_transform(X)
    expected = (MaxAbsScaler() if sparse_input else StandardScaler()).fit_transform(
        selected
    )
    np.testing.assert_allclose(
        actual["X"].toarray() if sparse_input else actual["X"],
        expected.toarray() if sparse_input else expected,
    )
    np.testing.assert_array_equal(actual["y"], y)
