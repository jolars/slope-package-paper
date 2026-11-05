"""Exercise the public Metewand workflow and retain command receipts."""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metewand", default="metewand")
    parser.add_argument("--manifest", default="benchmarks/single/config.yml")
    parser.add_argument("--experiment", default="smoke")
    parser.add_argument("--metric", default="rel_duality_gap")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    executable = shutil.which(args.metewand) or args.metewand
    if sys.platform == "win32" and not Path(executable).exists():
        executable += ".exe"
    executable = str(Path(executable).resolve())
    output = Path(args.output_dir).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    receipts = output.parent / (output.name + "-validation")
    receipts.mkdir()

    def invoke(name, *arguments, allow_failure=False):
        if arguments[0] in {"check", "plan", "run"}:
            arguments = (*arguments, "--experiment", args.experiment)
        completed = subprocess.run(
            [executable, *arguments, "--output", "json"],
            capture_output=True,
            text=True,
            check=False,
        )
        (receipts / f"{name}.json").write_text(completed.stdout)
        (receipts / f"{name}.stderr").write_text(completed.stderr)
        if completed.returncode and not allow_failure:
            raise RuntimeError(
                f"{name} failed ({completed.returncode}); inspect {receipts / (name + '.json')}.\n"
                f"{completed.stderr[:1000]}"
            )
        return json.loads(completed.stdout)

    manifest = str(Path(args.manifest).resolve())
    invoke("check", "check", "--manifest", manifest, "--workers")
    invoke("plan", "plan", "--manifest", manifest)
    invoke("run", "run", "--manifest", manifest, "--output-dir", str(output))
    invoke("status", "status", "--output-dir", str(output))
    invoke(
        "resume", "run", "--manifest", manifest, "--output-dir", str(output), "--resume"
    )
    destination = receipts / "export"
    invoke(
        "export",
        "export",
        "--output-dir",
        str(output),
        "--format",
        "json",
        "--require-complete",
        "--destination",
        str(destination),
    )
    snapshot = json.loads((destination / "results.json").read_text())
    assert snapshot["completeness"]["complete"]
    measured = [
        row for row in snapshot["observations"] if row["selected"] and not row["warmup"]
    ]
    assert measured and all(row["timed_wall_time_ns"] > 0 for row in measured)
    for candidate in snapshot["candidates"]:
        rows = [row for row in measured if row["candidate_id"] == candidate["id"]]
        if not rows:
            assert any(
                row["candidate_id"] == candidate["id"] and not row["applicable"]
                for row in snapshot["applicability"]
            )
            continue
        assert any(row["completion"] == "reached" for row in rows)
        print(
            f"{candidate['implementation']} / {candidate['dataset']}: "
            f"{len(rows)} points, gap {rows[-1]['metrics'][args.metric]:.3g}"
        )
    invoke(
        "explain", "explain", measured[0]["observation_id"], "--output-dir", str(output)
    )
    print(f"Validated export: {destination / 'results.json'}")


if __name__ == "__main__":
    main()
