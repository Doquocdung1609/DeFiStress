from __future__ import annotations

import json
from urllib.parse import urlparse

from backend.app.config import get_settings
from backend.app.db import Repository
from backend.app.services.real_snapshot import create_real_snapshot


def main() -> None:
    settings = get_settings()
    if not settings.eth_rpc_url:
        raise SystemExit("ETH_RPC_URL is required; no synthetic fallback is used by this command.")
    try:
        snapshot = create_real_snapshot(settings)
    except Exception as exc:
        message = _redacted_error(str(exc), settings)
        raise SystemExit(f"Snapshot creation failed ({type(exc).__name__}): {message}") from None
    stored = Repository(settings.database_url).save_snapshot(snapshot)
    print()
    print(stored["mode"])
    print(stored["label"])
    print(f"Block: {stored['block_number']}")
    print(json.dumps({"id": stored["id"], "block": stored["block_number"], "mode": stored["mode"]}, indent=2))


def _redacted_error(message: str, settings: object) -> str:
    secrets = [
        getattr(settings, "graph_api_key", ""),
        getattr(settings, "eth_rpc_url", ""),
        getattr(settings, "eth_archive_rpc_url", ""),
    ]
    redacted = message
    for secret in secrets:
        if secret:
            redacted = redacted.replace(secret, "[REDACTED]")
    for raw_url in secrets[1:]:
        if not raw_url:
            continue
        parsed = urlparse(raw_url)
        if parsed.path and parsed.path != "/":
            redacted = redacted.replace(parsed.path, "/[REDACTED]")
        if parsed.query:
            redacted = redacted.replace(parsed.query, "[REDACTED]")
    return redacted


if __name__ == "__main__":
    main()
