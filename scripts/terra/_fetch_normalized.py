from __future__ import annotations

import csv
import io
import json
import os
from argparse import ArgumentParser
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import httpx


def _safe_endpoint(value: str) -> str:
    parts = urlsplit(value)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def _row_count(content: bytes, content_type: str) -> int | None:
    text = content.decode("utf-8-sig", errors="replace")
    if "json" in content_type.lower() or text.lstrip().startswith(("[", "{")):
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            return None
        rows = payload.get("observations") if isinstance(payload, dict) else payload
        return len(rows) if isinstance(rows, list) else None
    try:
        return sum(1 for _ in csv.DictReader(io.StringIO(text)))
    except csv.Error:
        return None


def run(source: str, description: str, env_var: str) -> None:
    parser = ArgumentParser(description=description)
    parser.add_argument("--start", default="2022-05-01T00:00:00Z")
    parser.add_argument("--end", default="2022-05-13T23:59:59Z")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--endpoint", help=f"Normalized historical endpoint. Defaults to {env_var}.")
    parser.add_argument(
        "--bearer-env",
        help="Optional environment variable containing a bearer token. The token is never written to the manifest.",
    )
    parser.add_argument("--resume", action="store_true", help="Do not overwrite an existing raw download.")
    parser.add_argument("--timeout", type=float, default=60.0)
    args = parser.parse_args()

    if args.output.exists():
        if args.resume:
            print(args.output)
            return
        raise SystemExit(f"Refusing to overwrite raw historical data: {args.output}")

    endpoint = args.endpoint or os.getenv(env_var, "")
    if not endpoint:
        raise SystemExit(
            f"No endpoint configured. Set {env_var} in .env/environment or pass --endpoint. "
            "Alternatively import a verified CSV/JSON/Parquet dataset directly."
        )

    headers: dict[str, str] = {"Accept": "application/json, text/csv;q=0.9, */*;q=0.8"}
    if args.bearer_env:
        token = os.getenv(args.bearer_env, "")
        if not token:
            raise SystemExit(f"{args.bearer_env} is not set.")
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = httpx.get(
            endpoint,
            params={"start": args.start, "end": args.end},
            headers=headers,
            timeout=args.timeout,
            follow_redirects=True,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise SystemExit(f"Historical provider request failed: {exc}") from exc

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(response.content)

    content_type = response.headers.get("content-type", "")
    manifest = {
        "source": source,
        "status": "DOWNLOADED_UNVERIFIED",
        "evidence_policy": (
            "A successful download is not automatically REAL_HISTORICAL. "
            "Validate provenance/schema first, then import with the appropriate status."
        ),
        "requested_window": {"start": args.start, "end": args.end},
        "endpoint": _safe_endpoint(endpoint),
        "http_status": response.status_code,
        "content_type": content_type,
        "row_count_if_detected": _row_count(response.content, content_type),
        "retrieved_at": datetime.now(UTC).isoformat(),
        "expected_schema": "docs/data/terra_hourly_state.csv",
        "raw_file": str(args.output),
    }
    manifest_path = args.output.with_suffix(args.output.suffix + ".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(args.output)
    print(manifest_path)


if __name__ == "__main__":
    raise SystemExit("Use one of the source-specific fetch scripts.")
