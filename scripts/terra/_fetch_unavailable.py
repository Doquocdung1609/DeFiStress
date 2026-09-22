from __future__ import annotations

import json
from argparse import ArgumentParser
from datetime import UTC, datetime
from pathlib import Path


def run(source: str, description: str) -> None:
    parser = ArgumentParser(description=description)
    parser.add_argument("--start", default="2022-05-01T00:00:00Z")
    parser.add_argument("--end", default="2022-05-13T23:59:59Z")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--endpoint", help="Archival/indexed endpoint. Credentials should be supplied via environment.")
    parser.add_argument(
        "--resume", action="store_true", help="Reuse an existing manifest without overwriting raw data."
    )
    parser.add_argument("--rate-limit-per-second", type=float, default=2.0)
    args = parser.parse_args()
    if args.output.exists():
        if args.resume:
            print(args.output)
            return
        raise SystemExit(f"Refusing to overwrite raw acquisition manifest: {args.output}")
    payload = {
        "source": source,
        "status": "UNAVAILABLE",
        "reason": "No authenticated historical adapter is configured; no data was fabricated.",
        "requested_window": {"start": args.start, "end": args.end},
        "endpoint_configured": bool(args.endpoint),
        "rate_limit_per_second": args.rate_limit_per_second,
        "retrieved_at": datetime.now(UTC).isoformat(),
        "expected_schema": "docs/data/terra_hourly_state.csv",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    raise SystemExit("Historical endpoint unavailable; wrote an explicit UNAVAILABLE manifest.")
