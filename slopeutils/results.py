"""Read historical tables and independently evaluated Metewand profiles."""

import json
import warnings
from pathlib import Path

import pandas as pd

from .merge_parquet import merge_parquet_files


def _label(name, parameters):
    settings = ",".join(f"{key}={value}" for key, value in sorted(parameters.items()))
    return f"{name}[{settings}]" if settings else name


def load_benchmark_results(path):
    path = Path(path)
    snapshot_path = path / "results.json" if path.is_dir() else path
    if snapshot_path.suffix != ".json" or not snapshot_path.exists():
        frame = merge_parquet_files(str(path))
        if frame is None:
            raise ValueError(f"No benchmark results found in {path}")
        frame["partial"] = False
        frame["implementation_rep"] = 0
        frame["trajectory_id"] = "legacy"
        return frame

    snapshot = json.loads(snapshot_path.read_text())
    if snapshot.get("schema_version") != 1:
        raise ValueError("Unsupported Metewand analysis schema")
    candidates = {candidate["id"]: candidate for candidate in snapshot["candidates"]}
    observations = [
        item
        for item in snapshot["observations"]
        if item.get("valid") and not item.get("warmup") and item.get("metrics")
    ]
    groups = {}
    for item in observations:
        key = (
            item["candidate_id"],
            item.get("implementation_repetition"),
            item.get("measurement_index"),
        )
        groups.setdefault(key, []).append(item)

    rows = []
    for items in groups.values():
        delivery = (items[0].get("profile") or {}).get("delivery")
        if delivery == "streaming_profile":
            accepted = [item for item in items if item.get("selected")]
            chosen = max(
                accepted or items,
                key=lambda item: (item.get("retry_index", 0), item["attempt_id"]),
            )
            items = [
                item for item in items if item["attempt_id"] == chosen["attempt_id"]
            ]
        else:
            points = {}
            for item in items:
                index = (item.get("profile") or {}).get("schedule_index", 0)
                points.setdefault(index, []).append(item)
            items = [
                max(
                    point,
                    key=lambda item: (
                        bool(item.get("selected")),
                        item.get("retry_index", 0),
                    ),
                )
                for point in points.values()
            ]

        for item in items:
            candidate = candidates[item["candidate_id"]]
            parameters = item.get("parameters") or candidate["parameters"]
            dataset, problem, implementation = (
                parameters[key] for key in ("dataset", "problem", "implementation")
            )
            if "n_features" in dataset:
                family = "Simulated"
            else:
                family = (
                    "breheny"
                    if dataset["dataset"]
                    in {"brca1", "Rhee2006", "Koussounadis2014", "Scheetz2006"}
                    else "libsvm"
                )
            method = item.get("implementation") or candidate["implementation"]
            solver = {
                "pgd": "PGD",
                "pgd-fista": "PGD",
                "pgd-bb": "PGD",
                "pgd-anderson": "PGD",
                "admm": "ADMM",
                "sortedl1": "sortedl1",
                "tick": "tick",
                "skglm": "skglm",
                "slope-path": "SlopePath",
                "solution-path": "SolutionPath",
                "rslope": "rSLOPE",
                "newt-alm": "Newt-ALM",
                "safe-pgd": "PGD_safe_screening",
            }[method]
            profile = item.get("profile") or {}
            control = profile.get("observation_control") or {}
            time_ns = (
                item.get("active_time_ns")
                if delivery == "streaming_profile"
                else item.get("timed_wall_time_ns")
            )
            if time_ns is None:
                raise ValueError(
                    f"Observation {item['observation_id']} lacks its timing coordinate"
                )
            unfinished = any(
                profile["candidate_id"] == item["candidate_id"]
                and profile.get("measurement_index") == item.get("measurement_index")
                and profile["status"] != "accepted"
                for profile in snapshot.get("profiles", [])
            )
            partial = unfinished or not item.get("selected", False)
            rows.append(
                {
                    "data_name": _label(family, dataset),
                    "objective_name": _label(
                        "SLOPE_Path" if "path_length" in problem else "SLOPE", problem
                    ),
                    "solver_name": _label(solver, implementation),
                    **{
                        key: problem[key]
                        for key in ("reg", "path_length")
                        if key in problem
                    },
                    "idx_rep": item.get("measurement_index", 0),
                    "implementation_rep": item.get("implementation_repetition", 0),
                    "stop_val": profile.get(
                        "check_index",
                        control.get("iterations", control.get("tolerance", 0)),
                    ),
                    "time": time_ns / 1e9,
                    "partial": partial,
                    "trajectory_id": item["attempt_id"]
                    if delivery == "streaming_profile"
                    else "fresh_sequence",
                    "candidate_id": item["candidate_id"],
                    "attempt_id": item["attempt_id"],
                    "completion": item.get("completion"),
                    "timing_scope": item.get("timing_scope"),
                    **{
                        f"objective_{name}": value
                        for name, value in item["metrics"].items()
                    },
                }
            )
    if not rows:
        raise ValueError("The Metewand export contains no valid measured observations")
    frame = pd.DataFrame(rows)
    frame.attrs.update(
        {
            key: snapshot.get(key)
            for key in ("attempts", "applicability", "profiles", "completeness")
        }
    )
    if not snapshot.get("completeness", {}).get("complete", False):
        warnings.warn(
            "The Metewand comparison is incomplete; retained partial curves are marked.",
            stacklevel=2,
        )
    return frame
