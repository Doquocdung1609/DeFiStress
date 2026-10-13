from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from backend.app.config import Settings

OUTPUT = Path("data/processed/research_final/level3_extension/fork/validation.json")
SOURCE_COMMIT = "423bcfd4ebf910ef73b94d9deaf7cf746d8ed71c"
CANONICAL_BLOCK = 26_045_352
CANONICAL_HASH = "4dffe3bdf7bbaf24fd1e3b6c3f4795687dccfd3189cbfb61f4dbaf926722220a"


def _version(command: str) -> str | None:
    executable = shutil.which(command)
    if executable is None:
        return None
    completed = subprocess.run(
        [executable, "--version"], capture_output=True, text=True, check=False, timeout=10
    )
    return (completed.stdout or completed.stderr).splitlines()[0].strip()


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit("Refusing to overwrite existing Level-2 fork evidence")
    settings = Settings()
    prerequisites = {
        "eth_archive_rpc_url_configured": bool(settings.eth_archive_rpc_url),
        "forge": _version("forge"),
        "anvil": _version("anvil"),
        "cast": _version("cast"),
        "harness_sha256": hashlib.sha256(
            Path("contracts/validation/test/ForkValidation.t.sol").read_bytes()
        ).hexdigest(),
    }
    missing = [
        name
        for name, value in prerequisites.items()
        if name in {"eth_archive_rpc_url_configured", "forge", "anvil"} and not value
    ]
    status = "UNAVAILABLE" if missing else "READY_NOT_EXECUTED"
    payload = {
        "status": status,
        "source_commit": SOURCE_COMMIT,
        "chain_id": 1,
        "canonical_block": CANONICAL_BLOCK,
        "canonical_block_hash": CANONICAL_HASH,
        "execution_scope": "LOCAL_EPHEMERAL_MAINNET_FORK_ONLY",
        "prerequisites": prerequisites,
        "missing_prerequisites": missing,
        "transactions_executed": 0,
        "liquidation_call_executed": False,
        "swap_router_execution_executed": False,
        "quoter_v2_boundary": (
            "Existing eth_call evidence validates the canonical initial state only; it is not "
            "counterfactual post-shock fork execution."
        ),
        "reason": (
            "Foundry/Anvil executables are absent, so no contract-level fork transaction can be "
            "truthfully labeled PASS. Archive RPC remains available for read-only historical evidence."
            if missing
            else "Prerequisites are present, but an explicit funded historical sample is still required."
        ),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
