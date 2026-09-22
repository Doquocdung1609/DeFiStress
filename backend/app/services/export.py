from __future__ import annotations

import csv
import io
import json
import platform
import subprocess
import zipfile
from typing import Any

from backend.app.db import Repository


def build_experiment_zip(repository: Repository, run_id: str) -> bytes:
    run = repository.get_run(run_id)
    if not run or run["status"] != "COMPLETE" or not run["result"]:
        raise KeyError("completed run not found")
    scenario = repository.get_scenario(run["scenario_id"])
    if not scenario:
        raise KeyError("scenario not found")
    snapshot = repository.get_snapshot(scenario["snapshot_id"])
    if not snapshot:
        raise KeyError("snapshot not found")
    result = run["result"]
    manifest = {
        "run_id": run_id,
        "snapshot_id": snapshot["id"],
        "block_number": snapshot["block_number"],
        "block_hash": snapshot["block_hash"],
        "snapshot_mode": snapshot["mode"],
        "scenario": scenario["config"],
        "random_seed": run["seed"],
        "model_version": run["model_version"],
        "git_commit": _git_commit(),
        "runtime": {"python": platform.python_version()},
        "source_manifest": snapshot["source_manifest"],
    }
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        _json(archive, "manifest.json", manifest)
        _json(archive, "snapshot_summary.json", _snapshot_summary(snapshot))
        _json(archive, "scenario.json", scenario["config"])
        _json(archive, "metrics.json", result.get("metrics", {}))
        _json(
            archive,
            "validation.json",
            {"status": "NOT_INCLUDED", "reason": "Run export does not imply fork validation."},
        )
        archive.writestr("events.csv", _csv(result.get("events", [])))
        archive.writestr("positions.csv", _csv(snapshot.get("borrowers", [])))
        archive.writestr("timeseries.csv", _csv(result.get("timeseries", [])))
        archive.writestr(
            "README.txt",
            "DeFiStress Lab reproducible experiment export.\n"
            "Re-run with the immutable snapshot, scenario JSON, model version, and random seed in manifest.json.\n"
            f"Data mode: {snapshot['mode']}\n",
        )
        for name, data in _charts(result).items():
            archive.writestr(f"charts/{name}.png", data)
    return buffer.getvalue()


def _snapshot_summary(snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": snapshot["id"],
        "mode": snapshot["mode"],
        "label": snapshot["label"],
        "chain_id": snapshot["chain_id"],
        "block_number": snapshot["block_number"],
        "block_hash": snapshot["block_hash"],
        "block_timestamp": snapshot["block_timestamp"],
        "coverage": snapshot["coverage"],
        "data_quality_flags": snapshot["data_quality_flags"],
    }


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.SubprocessError):
        return "UNCOMMITTED"


def _json(archive: zipfile.ZipFile, name: str, payload: Any) -> None:
    archive.writestr(name, json.dumps(payload, indent=2, sort_keys=True))


def _csv(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    flat_rows = [
        {key: json.dumps(value) if isinstance(value, (dict, list)) else value for key, value in row.items()}
        for row in rows
    ]
    columns = sorted({key for row in flat_rows for key in row})
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(flat_rows)
    return stream.getvalue()


def _charts(result: dict[str, Any]) -> dict[str, bytes]:
    import matplotlib

    matplotlib.use("Agg")
    from matplotlib import pyplot as plt

    series = result.get("timeseries", [])
    outputs: dict[str, bytes] = {}
    chart_specs = {
        "price": (("reference_price", "dex_price"), "Price", "USDC per WETH"),
        "liquidations": (("liquidation_volume", "forced_weth_sell"), "Liquidations", "Volume"),
        "bad_debt": (("bad_debt",), "Bad debt", "USDC"),
    }
    for name, (keys, title, ylabel) in chart_specs.items():
        figure, axis = plt.subplots(figsize=(8, 4.5), dpi=120)
        x = [point.get("step", index) for index, point in enumerate(series)]
        for key in keys:
            axis.plot(x, [point.get(key, 0) for point in series], marker="o", label=key.replace("_", " ").title())
        axis.set_title(title)
        axis.set_xlabel("Simulation step")
        axis.set_ylabel(ylabel)
        axis.grid(alpha=0.2)
        if len(keys) > 1:
            axis.legend()
        stream = io.BytesIO()
        figure.tight_layout()
        figure.savefig(stream, format="png")
        plt.close(figure)
        outputs[name] = stream.getvalue()
    figure, axis = plt.subplots(figsize=(8, 4.5), dpi=120)
    mc = result.get("monte_carlo", {}).get("distributions", {}).get("bad_debt", [])
    axis.hist(mc or [0], bins=min(30, max(1, len(mc) // 5)))
    axis.set_title("Monte Carlo bad debt distribution" if mc else "Monte Carlo not run")
    axis.set_xlabel("Bad debt USDC")
    stream = io.BytesIO()
    figure.tight_layout()
    figure.savefig(stream, format="png")
    plt.close(figure)
    outputs["monte_carlo"] = stream.getvalue()
    return outputs
