"""Prepare pinned benchmark data and derive local or OCI manifests."""

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import urllib.request

import yaml


ROOT = Path(__file__).resolve().parent
DATASETS = {
    "brca1": "brca1.rds",
    "Rhee2006": "Rhee2006.rds",
    "Koussounadis2014": "Koussounadis2014.rds",
    "rcv1.binary": "rcv1_train.binary.bz2",
    "real-sim": "real-sim.bz2",
    "YearPredictionMSD": "YearPredictionMSD.bz2",
}


def inventory():
    value = json.loads((ROOT / "data-sources.json").read_text())
    if value["schema_version"] != 1:
        raise ValueError("Unsupported data-source inventory version")
    return value["files"]


def verify(path, expected):
    with Path(path).open("rb") as stream:
        actual = hashlib.file_digest(stream, "sha256").hexdigest()
    if actual != expected:
        raise ValueError(f"Prepared data changed: {path}")


def prepare_data(directory, files=None, check=False):
    sources = inventory()
    selected = sources if not files else {name: sources[name] for name in files}
    raw = Path(directory) / "raw"
    if not check:
        raw.mkdir(parents=True, exist_ok=True)
    for name, source in selected.items():
        destination = raw / name
        if destination.exists() or check:
            verify(destination, source["sha256"])
            continue
        with tempfile.NamedTemporaryFile(dir=raw, prefix=".download-", delete=False) as stream:
            temporary = Path(stream.name)
            try:
                with urllib.request.urlopen(source["url"], timeout=120) as response:
                    shutil.copyfileobj(response, stream)
                stream.flush()
                os.fsync(stream.fileno())
                verify(temporary, source["sha256"])
                os.replace(temporary, destination)
            finally:
                temporary.unlink(missing_ok=True)


def derive_manifest(suite, experiment, directory, image=None):
    if image and not re.fullmatch(r"[^\s]+@sha256:[0-9a-f]{64}", image):
        raise ValueError("Use the immutable image reference from container-image.txt")
    source = ROOT / suite / "config.yml"
    manifest = copy.deepcopy(yaml.safe_load(source.read_text()))
    names = [experiment] if isinstance(experiment, str) else experiment
    selected = [item for item in manifest["experiments"] if item["name"] in names]
    if {item["name"] for item in selected} != set(names):
        raise ValueError("Unknown benchmark experiment")
    manifest["experiments"] = selected
    manifest["default-experiment"] = selected[0]["name"]
    datasets = {name for item in selected for name in item.get("datasets", [])}
    manifest["datasets"] = {name: value for name, value in manifest["datasets"].items() if name in datasets}
    experiment = "_".join(item["name"] for item in selected)
    environment = manifest["environments"]["local"]
    environment.setdefault("environment-variables", {})["SLOPE_BENCHMARK_OFFLINE"] = "1"
    if image:
        workers = list(manifest["implementations"].values())
        workers.extend(dataset for dataset in manifest["datasets"].values() if "function" in dataset or "runner" in dataset)
        for problem in manifest["problems"].values():
            workers.append(problem["evaluator"])
            if "preparation" in problem:
                workers.append(problem["preparation"])
        for worker in workers:
            worker.setdefault("environment", "local")
        environment["kind"] = "oci"
        environment["image"] = image
    sources = inventory()
    needed = {}
    for dataset in manifest["datasets"].values():
        name = dataset.get("parameters", {}).get("dataset", {}).get("default")
        if name not in DATASETS:
            continue
        filename = DATASETS[name]
        raw = Path(directory) / "raw" / filename
        try:
            verify(raw, sources[filename]["sha256"])
        except FileNotFoundError as error:
            raise FileNotFoundError("Run benchmark-data-prepare before using real datasets") from error
        needed[filename] = sources[filename]
        dataset["sources"] = list(dataset["sources"]) + [
            f"prepared-data/{filename}", "prepared-data/manifest.json"
        ]
    if needed:
        prepared = source.parent / "prepared-data"
        prepared.mkdir(exist_ok=True)
        for filename, record in needed.items():
            target = prepared / filename
            if not target.exists():
                with tempfile.NamedTemporaryFile(dir=prepared, delete=False) as stream:
                    temporary = Path(stream.name)
                try:
                    shutil.copyfile(Path(directory) / "raw" / filename, temporary)
                    verify(temporary, record["sha256"])
                    os.replace(temporary, target)
                finally:
                    temporary.unlink(missing_ok=True)
            verify(target, record["sha256"])
        # Keep the full inventory so switching experiments does not change a pin.
        (prepared / "manifest.json").write_text(json.dumps({"schema_version": 1, "files": sources}, sort_keys=True) + "\n")
    destination = source.parent / f".metewand-{experiment}-{'oci' if image else 'local'}.yml"
    rendered = yaml.safe_dump(manifest, sort_keys=False)
    if not destination.exists() or destination.read_text() != rendered:
        destination.write_text(rendered)
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare-data")
    prepare.add_argument("--file", action="append", choices=sorted(DATASETS.values()))
    prepare.add_argument("--check", action="store_true")
    generate = commands.add_parser("manifest")
    generate.add_argument("--suite", choices=("single", "path"), required=True)
    generate.add_argument("--experiment", action="append")
    generate.add_argument("--run-args", nargs=argparse.REMAINDER, default=[])
    generate.add_argument("--image")
    for command in (prepare, generate):
        command.add_argument("--data-dir", default=os.environ.get("SLOPE_BENCHMARK_DATA_DIR", ".benchmark-data"))
    args = parser.parse_args()
    if args.command == "prepare-data":
        prepare_data(args.data_dir, args.file, args.check)
    else:
        experiments = list(args.experiment or [])
        arguments = iter(args.run_args)
        for argument in arguments:
            if argument == "--experiment":
                experiments.append(next(arguments))
        print(derive_manifest(args.suite, experiments or ["full"], args.data_dir, args.image))


if __name__ == "__main__":
    main()
