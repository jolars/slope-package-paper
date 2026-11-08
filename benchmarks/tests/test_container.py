import hashlib
import importlib.util
import json
from pathlib import Path

import pytest
import yaml


spec = importlib.util.spec_from_file_location("benchmark_container", Path(__file__).parents[1] / "container.py")
container = importlib.util.module_from_spec(spec)
spec.loader.exec_module(container)


def test_preparation_rejects_changed_data_without_repairing_it(tmp_path, monkeypatch):
    raw = tmp_path / "raw"
    raw.mkdir()
    path = raw / "data"
    path.write_bytes(b"changed")
    monkeypatch.setattr(container, "inventory", lambda: {"data": {"url": "https://example.invalid/data", "sha256": hashlib.sha256(b"original").hexdigest()}})
    monkeypatch.setattr(container.urllib.request, "urlopen", lambda *a, **k: pytest.fail("Verification must not fetch"))
    with pytest.raises(ValueError, match="changed"):
        container.prepare_data(tmp_path)
    assert path.read_bytes() == b"changed"


def test_smoke_manifest_preserves_science_and_needs_no_real_data(tmp_path, monkeypatch):
    root = tmp_path / "benchmarks"
    (root / "single").mkdir(parents=True)
    source = Path(__file__).parents[1] / "single/config.yml"
    (root / "single/config.yml").write_bytes(source.read_bytes())
    monkeypatch.setattr(container, "ROOT", root)
    monkeypatch.setattr(container, "inventory", lambda: {})
    image = "registry.example/worker@sha256:" + "a" * 64
    output = container.derive_manifest("single", "smoke", tmp_path / "data", image)
    original = yaml.safe_load(source.read_text())
    generated = yaml.safe_load(output.read_text())
    for worker in original["implementations"].values():
        worker.setdefault("environment", "local")
    for problem in original["problems"].values():
        problem["evaluator"].setdefault("environment", "local")
        if "preparation" in problem:
            problem["preparation"].setdefault("environment", "local")
    assert generated["implementations"] == original["implementations"]
    assert generated["problems"] == original["problems"]
    assert generated["execution-policies"] == original["execution-policies"]
    assert generated["observation-policies"] == original["observation-policies"]
    assert generated["experiments"] == [item for item in original["experiments"] if item["name"] == "smoke"]
    assert generated["environments"]["local"]["image"] == image
    assert generated["environments"]["local"]["environment-variables"]["OMP_NUM_THREADS"] == "1"
    assert not (root / "single/prepared-data").exists()


def test_bad_download_never_publishes_a_completed_file(tmp_path, monkeypatch):
    import io
    monkeypatch.setattr(container, "inventory", lambda: {"data": {"url": "https://example.invalid/data", "sha256": hashlib.sha256(b"original").hexdigest()}})
    monkeypatch.setattr(container.urllib.request, "urlopen", lambda *a, **k: io.BytesIO(b"truncated"))
    with pytest.raises(ValueError, match="changed"):
        container.prepare_data(tmp_path)
    assert list((tmp_path / "raw").iterdir()) == []
