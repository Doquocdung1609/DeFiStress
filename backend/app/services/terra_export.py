from __future__ import annotations

import csv
import io
import json
import zipfile
from typing import Any


def build_terra_export(replay: dict[str, Any]) -> bytes:
    result = replay
    metadata = result["metadata"]
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        _json(archive, "manifest.json", metadata)
        archive.writestr(
            "README.md",
            "# DeFiStress Lab Terra replay export\n\n"
            "This package is a historical replay artifact, not a claim of prospective prediction.\n"
            f"Dataset status: {result['dataset']['status']}\n",
        )
        _json(archive, "data_sources.json", metadata["data_source_manifest"])
        _json(
            archive,
            "cutoff.json",
            {
                "calibration_start": metadata["calibration_start"],
                "calibration_end": metadata["calibration_end"],
                "cutoff_timestamp": metadata["cutoff_timestamp"],
                "evaluation_start": metadata["evaluation_start"],
                "evaluation_end": metadata["evaluation_end"],
                "leakage_check_status": metadata["leakage_check_status"],
            },
        )
        _json(archive, "parameters.json", metadata["scenario_parameters"])
        _json(archive, "model_definition.json", result["model"])
        archive.writestr("simulation_timeseries.csv", _csv(result["simulated_timeseries"]))
        archive.writestr("ground_truth_timeseries.csv", _csv(result["ground_truth_timeseries"]))
        archive.writestr("validation_metrics.csv", _csv([result["validation_metrics"]]))
        archive.writestr("agent_events.csv", _csv(result.get("agent_events", [])))
        archive.writestr("benchmark_results.csv", _csv(result.get("benchmark_results", [])))
        _json(archive, "quality_report.json", result["dataset"]["quality_report"])
        for name, chart in _charts(result).items():
            archive.writestr(f"charts/{name}.png", chart)
    return buffer.getvalue()


def _json(archive: zipfile.ZipFile, name: str, payload: Any) -> None:
    archive.writestr(name, json.dumps(payload, indent=2, sort_keys=True))


def _csv(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    flattened = [
        {
            key: json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else value
            for key, value in row.items()
        }
        for row in rows
    ]
    columns = sorted({key for row in flattened for key in row})
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=columns)
    writer.writeheader()
    writer.writerows(flattened)
    return stream.getvalue()


def _charts(result: dict[str, Any]) -> dict[str, bytes]:
    import matplotlib

    matplotlib.use("Agg")
    from matplotlib import pyplot as plt

    actual_by_time = {row["timestamp"]: row for row in result["ground_truth_timeseries"]}
    simulated = result["simulated_timeseries"]
    output: dict[str, bytes] = {}
    for field, title, ylabel in (
        ("ust_price", "UST actual vs simulated", "USD per UST"),
        ("luna_price", "LUNA actual vs simulated", "USD per LUNA"),
        ("luna_supply", "LUNA supply actual vs simulated", "LUNA"),
    ):
        figure, axis = plt.subplots(figsize=(9, 4.5), dpi=120)
        x = list(range(len(simulated)))
        axis.plot(x, [actual_by_time[row["timestamp"]][field] for row in simulated], label="Ground truth")
        axis.plot(x, [row[field] for row in simulated], label="Simulated")
        axis.set_title(title)
        axis.set_xlabel("Evaluation hour")
        axis.set_ylabel(ylabel)
        axis.grid(alpha=0.2)
        axis.legend()
        stream = io.BytesIO()
        figure.tight_layout()
        figure.savefig(stream, format="png")
        plt.close(figure)
        output[field] = stream.getvalue()
    return output
