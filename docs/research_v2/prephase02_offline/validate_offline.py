"""Read-only Phase 01 evidence guard and isolated synthetic negative controls."""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[3]
PHASE = BASE / "docs/research_v2/phase01b"
REGISTERED = (26045352, 26038152, 26030952)
POOLS = {"P3000": ("0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8", 3000),
         "P500": ("0x88e6a0c2dd26fee b64f039a2c41296fcb3f5640".replace(" ", ""), 500)}
EXPECTED_HASH = {
    26045352: "0x4dffe3bdf7bbaf24fd1e3b6c3f4795687dccfd3189cbfb61f4dbaf926722220a",
    26038152: "0xbb108203815f257e9f9b023f92a30e67d946799355ceffc4bef0e0e16a1e87bd",
    26030952: "0xeeb12db7f31e86507bb4be7a1a2953d19c11165c99a75ebc7aa589d65d0b9625",
}


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def validate_identity(chain: int, block: int, block_hash: str) -> bool:
    return chain == 1 and block in REGISTERED and block_hash.lower() == EXPECTED_HASH[block]


def validate_pool(address: str, fee: int, pool_id: str, token0: str, token1: str,
                  usdc: str, weth: str) -> bool:
    return (pool_id in POOLS and (address.lower(), fee) == POOLS[pool_id]
            and token0.lower() == usdc.lower() and token1.lower() == weth.lower())


def units(raw: int, decimals: int, expected_decimals: int) -> bool:
    return isinstance(raw, int) and not isinstance(raw, bool) and raw >= 0 and decimals == expected_decimals


def canonical_equal(expected: object, actual: object) -> bool:
    def normal(value):
        if isinstance(value, (tuple, list)):
            return [normal(x) for x in value]
        if isinstance(value, dict):
            return {k: normal(v) for k, v in value.items()}
        return value
    return normal(expected) == normal(actual)


def complete_fields(expected: dict, observed: dict) -> bool:
    return set(expected) == set(observed) and all(v is not None for v in observed.values())


def tick_band(ticks: list[dict], lower: int, upper: int, spacing: int) -> bool:
    values = [t["index"] for t in ticks]
    return (spacing > 0 and lower <= upper and len(values) == len(set(values))
            and all(lower <= i <= upper and i % spacing == 0 for i in values)
            and all(t["gross"] >= abs(t["net"]) for t in ticks)
            and all(t["gross"] > 0 and t["bitmap_initialized"] for t in ticks))


def liquidity_consistent(active: int, total: int) -> bool:
    return isinstance(active, int) and isinstance(total, int) and 0 <= active <= total


def oracle_valid(source: str, expected_source: str, round_id: int, timestamp: int,
                 block_timestamp: int, spot_substituted: bool = False) -> bool:
    return (source.lower() == expected_source.lower() and not spot_substituted
            and isinstance(round_id, int) and round_id > 0
            and 0 < timestamp <= block_timestamp)


def borrower_complete(reserve_ids: list[int], required: list[int],
                      debt_raw: dict[int, int], hf_wad: int | None) -> bool:
    return (len(reserve_ids) == len(set(reserve_ids)) and set(required).issubset(reserve_ids)
            and all(k in debt_raw and isinstance(debt_raw[k], int) and debt_raw[k] >= 0
                    for k in required)
            and isinstance(hf_wad, int) and hf_wad >= 0)


def file_record(root: Path, row: dict) -> dict:
    relative = Path(row["path"])
    if relative.is_absolute() or ".." in relative.parts:
        return {"path": str(relative), "status": "FAIL", "reason": "PATH_ESCAPE"}
    target = root / relative
    if not target.is_file():
        return {"path": str(relative), "status": "BLOCKED", "reason": "FILE_MISSING"}
    raw = target.read_bytes()
    valid = len(raw) == row["size_bytes"] and digest(raw) == row["sha256"]
    if valid and "uncompressed_sha256" in row:
        try:
            decoded = gzip.decompress(raw)
            valid = (digest(decoded) == row["uncompressed_sha256"]
                     and len(decoded) == row["uncompressed_size"])
        except (OSError, EOFError):
            valid = False
    return {"path": str(relative), "status": "PASS" if valid else "FAIL",
            "reason": "BYTE_HASH_AND_SIZE" if valid else "DIGEST_MISMATCH"}


def run_offline() -> dict:
    reg = json.loads((PHASE / "SAMPLE_REGISTRATION.json").read_text(encoding="utf-8"))
    alchemy = json.loads((PHASE / "alchemy_crosscheck/VERIFIED_CI_EVIDENCE.json").read_text())
    provenance = json.loads((PHASE / "EVIDENCE_PROVENANCE.json").read_text())
    checks = []
    checks.append({"id": "REG-CHAIN", "status": "PASS" if reg["chain_id"] == 1 else "FAIL"})
    checks.append({"id": "REG-BLOCKS", "status": "PASS" if (
        tuple(b["number"] for b in reg["blocks"]) == REGISTERED and
        all(validate_identity(reg["chain_id"], b["number"], b["expected_hash"]) for b in reg["blocks"])
    ) else "FAIL"})
    checks.append({"id": "REG-POOLS", "status": "PASS" if all(
        (p["address"].lower(), p["fee"]) == POOLS[p["id"]] for p in reg["pools"]
    ) and len(reg["pools"]) == 2 else "FAIL"})
    checks.append({"id": "REG-DECIMALS", "status": "PASS" if
                   (reg["tokens"]["USDC"]["decimals"], reg["tokens"]["WETH"]["decimals"]) == (6, 18)
                   else "FAIL"})
    checks.append({"id": "REG-V1", "status": "PASS" if
                   reg["v1_tag"] == "v1.0.0-scientific-baseline" else "FAIL"})
    checks.append({"id": "ALCHEMY-SUMMARY", "status": "PASS" if (
        alchemy["summary"]["agreeing"] == alchemy["summary"]["total_field_comparisons"] == 174
        and alchemy["summary"]["missing"] == alchemy["summary"]["mismatch"] == 0
        and alchemy["verdicts"]["independent_backend"] == "UNVERIFIED"
        and not alchemy["verdicts"]["phase02_authorized"]
        and all(b["hash"] == EXPECTED_HASH[b["number"]] for b in alchemy["blocks"])
    ) else "FAIL"})
    # Source manifest covers original full collection and separate borrower-repair records.
    for manifest_path in ("evidence/full/collection_manifest.json",
                          "evidence/borrower_repair/collection_manifest.json"):
        manifest_file = PHASE / manifest_path
        if not manifest_file.is_file():
            checks.append({"id": manifest_path, "status": "BLOCKED", "reason": "MANIFEST_MISSING"})
            continue
        manifest = json.loads(manifest_file.read_text())
        origin = manifest_file.parent
        for row in manifest["files"]:
            checks.append(file_record(origin, row))
    provenance_files = provenance.get("files", [])
    checks.append({"id": "PROVENANCE-SIZE", "status": "PASS" if
                   len(provenance_files) == provenance["file_count"] else "FAIL"})
    # A historical SHA256 in the repository is an index, not a way to replay unpersisted Alchemy values.
    checks.append({"id": "ALCHEMY-VALUE-REPLAY", "status": "BLOCKED",
                   "reason": "NOT_REPLAYABLE_FROM_PERSISTED_SUMMARY"})
    checks.append({"id": "BACKEND-INDEPENDENCE", "status": "BLOCKED",
                   "reason": "NO_REQUEST_LEVEL_DISTINCT_BACKEND_ATTESTATION"})
    # An unrelated scientific gate cannot turn successful local byte checks into L1 BLOCKED.
    integrity = [x for x in checks if x["id"] not in ("ALCHEMY-VALUE-REPLAY", "BACKEND-INDEPENDENCE")]
    status = "FAIL" if any(x["status"] == "FAIL" for x in integrity) else (
        "BLOCKED" if any(x["status"] == "BLOCKED" for x in integrity) else "PASS")
    return {"schema": "defistress-prephase02-offline-v1", "source_commit":
            "2e0ec142c475f8d1362f90c4ca8d2f0718e41f77",
            "L1_INTEGRITY": status, "L2_CONTRACTS": "REQUIRES_TEST_EXECUTION",
            "GATE_A": "BLOCKED_BACKEND_INDEPENDENCE",
            "GATE_B": "PASS_REGISTERED_CORE_SCOPE",
            "PHASE02_AUTHORIZATION": "NOT_AUTHORIZED",
            "checks": checks, "counts": {s: sum(x["status"] == s for x in checks)
                                        for s in ("PASS", "FAIL", "BLOCKED")}}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run_offline()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"L1": report["L1_INTEGRITY"], "counts": report["counts"],
                      "GATE_A": report["GATE_A"], "GATE_B": report["GATE_B"]}))
    return 1 if report["L1_INTEGRITY"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
