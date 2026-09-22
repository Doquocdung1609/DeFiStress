from __future__ import annotations

import json

from backend.app.config import get_settings
from backend.app.db import Repository
from backend.app.services.real_snapshot import create_real_snapshot


def main() -> None:
    settings = get_settings()
    if not settings.eth_rpc_url:
        raise SystemExit("ETH_RPC_URL is required; no synthetic fallback is used by this command.")
    snapshot = create_real_snapshot(settings)
    stored = Repository(settings.database_url).save_snapshot(snapshot)
    print(json.dumps({"id": stored["id"], "block": stored["block_number"], "mode": stored["mode"]}, indent=2))


if __name__ == "__main__":
    main()
