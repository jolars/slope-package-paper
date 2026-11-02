import json
from copy import deepcopy

import pytest

from slopeutils.results import load_benchmark_results


def snapshot():
    parameters = {
        "dataset": {"n_samples": 40, "n_features": 20, "X_density": 1.0},
        "problem": {"reg": 0.1, "q": 0.2, "fit_intercept": False},
        "implementation": {"acceleration": "fista", "prox": "prox_fast_stack"},
    }
    row = {
        "candidate_id": "c",
        "attempt_id": "original",
        "observation_id": "observation",
        "parameters": parameters,
        "implementation": "pgd-fista",
        "implementation_repetition": 0,
        "measurement_index": 0,
        "retry_index": 0,
        "valid": True,
        "warmup": False,
        "selected": True,
        "completion": "reached",
        "timing_scope": "execute_only",
        "metrics": {"value": 1.0, "duality_gap": 1e-8, "rel_duality_gap": 1e-8},
        "timed_wall_time_ns": 2000,
        "active_time_ns": 1000,
        "profile": {"delivery": "streaming_profile", "check_index": 2},
    }
    return {
        "schema_version": 1,
        "candidates": [{"id": "c", "parameters": parameters}],
        "observations": [row],
        "completeness": {"complete": True},
    }


def write(tmp_path, value):
    path = tmp_path / "results.json"
    path.write_text(json.dumps(value))
    return path


def test_streams_use_active_time_and_keep_the_selected_trajectory(tmp_path):
    data = snapshot()
    failed = deepcopy(data["observations"][0])
    failed.update(attempt_id="failed-retry", retry_index=1, selected=False)
    data["observations"].append(failed)
    frame = load_benchmark_results(write(tmp_path, data))
    assert len(frame) == 1
    assert frame.iloc[0]["attempt_id"] == "original"
    assert frame.iloc[0]["time"] == 1e-6
    assert frame.iloc[0]["solver_name"].startswith("PGD[acceleration=fista")


def test_partial_stream_uses_one_latest_attempt(tmp_path):
    data = snapshot()
    data["completeness"]["complete"] = False
    original = data["observations"][0]
    original["selected"] = False
    latest = deepcopy(original)
    latest.update(attempt_id="retry", retry_index=1)
    data["observations"].append(latest)
    with pytest.warns(UserWarning, match="incomplete"):
        frame = load_benchmark_results(write(tmp_path, data))
    assert frame["attempt_id"].tolist() == ["retry"]
    assert frame["partial"].tolist() == [True]


def test_fresh_points_retain_distinct_attempts_and_use_wall_time(tmp_path):
    data = snapshot()
    first = data["observations"][0]
    first["profile"] = {
        "delivery": "fresh_sequence",
        "schedule_index": 0,
        "observation_control": {"initial": True},
    }
    later = deepcopy(first)
    later.update(attempt_id="later", observation_id="later-observation")
    later["profile"] = {
        "delivery": "fresh_sequence",
        "schedule_index": 1,
        "observation_control": {"iterations": 1},
    }
    data["observations"].append(later)
    frame = load_benchmark_results(write(tmp_path, data))
    assert len(frame) == 2
    assert frame["time"].tolist() == [2e-6, 2e-6]
    assert frame["stop_val"].tolist() == [0, 1]


def test_censored_fresh_profile_marks_accepted_intermediate_points_as_partial(tmp_path):
    data = snapshot()
    data["observations"][0]["profile"] = {
        "delivery": "fresh_sequence",
        "schedule_index": 0,
    }
    data["profiles"] = [
        {"candidate_id": "c", "measurement_index": 0, "status": "censored"}
    ]
    data["completeness"]["complete"] = False
    with pytest.warns(UserWarning, match="incomplete"):
        frame = load_benchmark_results(write(tmp_path, data))
    assert frame["partial"].tolist() == [True]


@pytest.mark.parametrize(
    "method,label",
    [("solution-path", "SolutionPath"), ("pgd-fista", "PGD"), ("rslope", "rSLOPE")],
)
def test_path_exports_keep_path_parameters_and_maximum_gap(tmp_path, method, label):
    data = snapshot()
    row = data["observations"][0]
    row["implementation"] = method
    row["parameters"]["problem"] = {"path_length": 50, "q": 0.2, "fit_intercept": False}
    row["parameters"]["dataset"] = {
        "dataset": "brca1",
        "path_length": 50,
        "q": 0.2,
        "fit_intercept": False,
        "standardize": True,
    }
    row["parameters"]["implementation"] = {}
    row["metrics"] = {"value": 1.0, "max_rel_duality_gap": 1e-8}
    row["profile"] = {
        "delivery": "fresh_sequence",
        "schedule_index": 2,
        "observation_control": {"tolerance": 0.01},
    }
    frame = load_benchmark_results(write(tmp_path, data))
    assert frame.iloc[0]["objective_name"].startswith("SLOPE_Path[")
    assert frame.iloc[0]["path_length"] == 50
    assert "reg" not in frame
    assert frame.iloc[0]["solver_name"] == label
    assert frame.iloc[0]["objective_max_rel_duality_gap"] == 1e-8
    assert frame.iloc[0]["time"] == 2e-6
    assert frame.iloc[0]["stop_val"] == 0.01
