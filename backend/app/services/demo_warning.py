"""Presentation adapter for P04-03-S; no historical input or model adjustment."""

from __future__ import annotations

import hashlib
import json
from datetime import timedelta
from typing import Any

from backend.app.schemas import WarningDemoRequest
from defistress_v2.contracts import canonical_json_bytes
from defistress_v2.terra_pit import (
    AssetUnit,
    DatasetVintage,
    EvidenceOrigin,
    Measurement,
    SourceFrequency,
    SourceProvenance,
    TemporalObservation,
    TerraChainId,
    TimeInterval,
    UtcInstant,
    ValueStatus,
    VerificationLevel,
)
from defistress_v2.terra_warning import DecisionContext, ModelId, WarningInputs, evaluate, toy_config
from defistress_v2.terra_warning.contracts import SCHEMA

SOURCE_COMMIT = "ecddfc5c09da841c9929fde712ead3a4053150b4"


def _bar(asset: str, start: UtcInstant, price: str, delay_minutes: int) -> TemporalObservation:
    end = UtcInstant(start.value + timedelta(hours=1))
    ready = UtcInstant(end.value + timedelta(minutes=delay_minutes))
    name = f"demo-{asset}-{start.value:%Y%m%dT%H}"
    raw = f"SYNTHETIC:{asset}:{start.to_canonical()}:{price}:{delay_minutes}".encode()
    return TemporalObservation(
        name, TerraChainId("columbus-5"), start, TimeInterval(start, end),
        DatasetVintage(f"{name}-v1", ready, ready, ready),
        Measurement(ValueStatus.AVAILABLE, price, AssetUnit(asset, "USD", f"USD/{asset}"), f"complete-{name}"),
        SourceProvenance(
            f"synthetic-{asset.lower()}", SOURCE_COMMIT, hashlib.sha256(raw).hexdigest(),
            VerificationLevel.FULL_BYTES_VERIFIED, EvidenceOrigin.SYNTHETIC,
        ),
        SourceFrequency.HOURLY_AGGREGATE,
    )


def run_warning_demo(request: WarningDemoRequest) -> dict[str, Any]:
    cutoff = UtcInstant(request.cutoff)
    current = UtcInstant(cutoff.value - timedelta(hours=1))
    previous = UtcInstant(cutoff.value - timedelta(hours=2))
    ust = () if request.ust_price is None else (_bar("UST", current, request.ust_price, request.ust_delay_minutes),)
    luna = tuple(
        _bar("LUNA", start, price, 0) for start, price in (
            (previous, request.luna_previous_price), (current, request.luna_current_price),
        ) if price is not None
    )
    inputs = WarningInputs(ust, luna)
    context = DecisionContext(cutoff, cutoff, cutoff)
    config = toy_config()
    models = {}
    for label, model_id in (("B0", ModelId.B0), ("B1", ModelId.B1), ("B2", ModelId.B2), ("B3", ModelId.B3)):
        result = evaluate(model_id, inputs, context, config)
        model = json.loads(canonical_json_bytes(result, schema_version=SCHEMA))["payload"]
        model["output_hash"] = result.output_hash
        models[label] = model
    return {
        "status": "COMPLETE", "mode": "SYNTHETIC_WARNING", "origin": "SYNTHETIC",
        "execution_status": "MODEL_EXECUTED", "source": "USER_SUPPLIED_SYNTHETIC_VALUES",
        "assumptions": request.model_dump(mode="json"), "models": models,
        "scientific_status": "SYNTHETIC_CONTROLS_ONLY_HISTORICAL_BACKTEST_NOT_AUTHORIZED",
    }
