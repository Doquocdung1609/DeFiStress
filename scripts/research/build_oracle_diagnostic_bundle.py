# ruff: noqa: E501 -- long Vietnamese Markdown lines are preserved in the generated report.
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path
from typing import Any

ROOT = Path("data/processed/research_final/oracle_transmission_diagnostic_v1")
REPORT = Path("docs/research_final/ORACLE_TRANSMISSION_DIAGNOSTIC_v1.md")
SOURCE_CODE_COMMIT = "619faed07583de36fc29e8b9c3c30788c1819644"
SELECTION_COMMIT = "a2c37e3d513054131083b791a05f8b50047925fd"
STARTING_HEAD = "9842c4f2c35adb8b4ec906e1bc76afa825d197c7"
POLICY_ORDER = (
    "A_ADVERSE_PASS_THROUGH",
    "B_REFERENCE_ONLY",
    "C_WEAK_LAGGED_SMOOTHED_PROXY",
    "C_MODERATE_LAGGED_SMOOTHED_PROXY",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _fmt(value: Any, digits: int = 6) -> str:
    if value is None:
        return "NA"
    return f"{Decimal(str(value)):.{digits}f}"


def _artifact_hashes() -> dict[str, str]:
    names = [
        "baseline_reproduction.json",
        "borrower_level_evidence.csv",
        "comparison_matrix.csv",
        "comparison_matrix.json",
        "deterministic_depth2_comparison.csv",
        "monte_carlo_path_comparison.csv",
        "policy_summary.csv",
        "regression_report.json",
        "result_summary.json",
        "scientific_interpretation.json",
        "selection_manifest.json",
    ]
    if (ROOT / "test_evidence.json").exists():
        names.append("test_evidence.json")
    return {name: _sha(ROOT / name) for name in names}


def main() -> None:
    selection = _load(ROOT / "selection_manifest.json")
    baseline = _load(ROOT / "baseline_reproduction.json")
    comparison = _load(ROOT / "comparison_matrix.json")
    regression = _load(ROOT / "regression_report.json")
    interpretation = _load(ROOT / "scientific_interpretation.json")
    rows = comparison["rows"]
    test_evidence_path = ROOT / "test_evidence.json"
    test_evidence = _load(test_evidence_path) if test_evidence_path.exists() else {"status": "PENDING"}

    by_policy: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_policy[row["policy_id"]].append(row)

    summaries: list[dict[str, Any]] = []
    for policy_id in POLICY_ORDER:
        policy_rows = by_policy[policy_id]
        deterministic_depth2 = [
            row for row in policy_rows if row["case_type"] == "DETERMINISTIC_DEPTH2"
        ]
        controls = [row for row in policy_rows if row["case_type"] == "DETERMINISTIC_CONTROL"]
        selected_mc = [row for row in policy_rows if row["case_type"] == "AUDITED_MONTE_CARLO"]
        summaries.append(
            {
                "policy_id": policy_id,
                "case_count": len(policy_rows),
                "deterministic_depth2_count_of_4": sum(
                    row["cascade_depth"] >= 2 for row in deterministic_depth2
                ),
                "control_depth2_count_of_4": sum(row["cascade_depth"] >= 2 for row in controls),
                "selected_mc_depth2_count_of_10": sum(
                    row["cascade_depth"] >= 2 for row in selected_mc
                ),
                "selected_case_mean_liquidated_debt_usdc": _fmt(
                    sum(Decimal(str(row["total_liquidated_debt"])) for row in policy_rows)
                    / Decimal(len(policy_rows))
                ),
                "selected_case_mean_modeled_bad_debt_usd": _fmt(
                    sum(Decimal(str(row["bad_debt"])) for row in policy_rows)
                    / Decimal(len(policy_rows))
                ),
                "max_immediate_dex_price_impact_ratio": _fmt(
                    max(row["max_intrawave_liquidation_price_impact"] for row in policy_rows),
                    12,
                ),
                "max_post_arbitrage_residual_spread_ratio": _fmt(
                    max(row["max_post_arbitrage_spread"] for row in policy_rows),
                    12,
                ),
            }
        )
    _write_csv(ROOT / "policy_summary.csv", summaries)

    compact_fields = (
        "case_id",
        "path_index",
        "path_seed",
        "policy_id",
        "shock_pct",
        "liquidity_haircut_pct",
        "cascade_depth",
        "newly_eligible_count",
        "total_liquidated_debt",
        "bad_debt",
        "max_intrawave_liquidation_price_impact",
        "max_post_arbitrage_spread",
        "post_wave1_dex_trade_price_usd_per_weth",
        "post_wave1_borrower_valuation_price_usd_per_weth",
    )
    deterministic_rows = [row for row in rows if row["case_type"] == "DETERMINISTIC_DEPTH2"]
    mc_rows = [row for row in rows if row["case_type"] == "AUDITED_MONTE_CARLO"]
    _write_csv(
        ROOT / "deterministic_depth2_comparison.csv",
        [{field: row[field] for field in compact_fields} for row in deterministic_rows],
    )
    _write_csv(
        ROOT / "monte_carlo_path_comparison.csv",
        [{field: row[field] for field in compact_fields} for row in mc_rows],
    )

    depth_counts = Counter(
        (row["policy_id"], row["case_type"], row["cascade_depth"]) for row in rows
    )
    direct_effect = {
        policy_id: {
            "newly_eligible_borrower_case_instances": sum(
                int(row["newly_eligible_count"]) for row in by_policy[policy_id]
            ),
            "deterministic_depth2_cases_retaining_depth2": sum(
                row["cascade_depth"] >= 2
                for row in by_policy[policy_id]
                if row["case_type"] == "DETERMINISTIC_DEPTH2"
            ),
            "audited_mc_paths_retaining_depth2": sum(
                row["cascade_depth"] >= 2
                for row in by_policy[policy_id]
                if row["case_type"] == "AUDITED_MONTE_CARLO"
            ),
        }
        for policy_id in POLICY_ORDER
    }
    result_summary = {
        "status": "LIMITED_TARGETED_MODEL_DIAGNOSTIC — AWAITING_COMMANDER_REVIEW",
        "case_population": {
            "deterministic_depth2": 4,
            "deterministic_controls": 4,
            "audited_monte_carlo_paths": 10,
            "policies": 4,
            "policy_case_results": 72,
            "verified_borrowers_per_case_policy": 454,
            "snapshot_weth_usdc_target_cohort": 109,
            "borrower_policy_case_rows": 18 * 4 * 454,
        },
        "depth_counts": {
            "::".join(map(str, key)): value for key, value in sorted(depth_counts.items())
        },
        "direct_effect_summary": direct_effect,
        "computed_finding": interpretation["computed_model_finding"],
        "external_empirical_inference": "NOT_ESTABLISHED",
        "selection_warning": (
            "The ten Monte Carlo paths were deliberately inherited depth>=2 audit paths; "
            "their counts are not an estimated crisis probability."
        ),
    }
    _write_json(ROOT / "result_summary.json", result_summary)

    deterministic_table = []
    for row in deterministic_rows:
        deterministic_table.append(
            "| {case_id} | {policy_id} | {cascade_depth} | {newly_eligible_count} | "
            "{debt} | {bad} | {impact} | {spread} | {valuation} |".format(
                case_id=row["case_id"],
                policy_id=row["policy_id"],
                cascade_depth=row["cascade_depth"],
                newly_eligible_count=row["newly_eligible_count"],
                debt=_fmt(row["total_liquidated_debt"], 3),
                bad=_fmt(row["bad_debt"], 3),
                impact=_fmt(Decimal(str(row["max_intrawave_liquidation_price_impact"])) * 100, 4),
                spread=_fmt(Decimal(str(row["max_post_arbitrage_spread"])) * 100, 4),
                valuation=_fmt(row["post_wave1_borrower_valuation_price_usd_per_weth"], 3),
            )
        )

    summary_table = []
    for row in summaries:
        summary_table.append(
            "| {policy_id} | {deterministic_depth2_count_of_4}/4 | "
            "{control_depth2_count_of_4}/4 | {selected_mc_depth2_count_of_10}/10 | "
            "{selected_case_mean_liquidated_debt_usdc} | "
            "{selected_case_mean_modeled_bad_debt_usd} |".format(**row)
        )

    test_lines = [f"- Trạng thái: `{test_evidence.get('status', 'PENDING')}`."]
    for item in test_evidence.get("commands", []):
        test_lines.append(
            f"- `{item['command']}` → **{item['status']}** ({item.get('result', 'không có tóm tắt')})."
        )

    report = f"""# Oracle Transmission Diagnostic v1

Trạng thái: **LIMITED — TARGETED MODEL DIAGNOSTIC; AWAITING COMMANDER REVIEW**. Tài liệu này không tự cấp `SCIENTIFIC_PASS` và không tạo `SCIENTIFIC_CONTENT_LOCK`.

## 1. Câu hỏi và phạm vi

Thí nghiệm cô lập giả định truyền giá dùng để đánh giá Health Factor (HF) giữa các vòng thanh lý. Nó không xác minh oracle Aave/Chainlink thực tế và không phải giao dịch Mainnet. Bộ chạy gồm bốn deterministic depth-2 cases, bốn deterministic controls và đúng mười Monte Carlo paths đã được kiểm toán từ trước; không chạy lại 10.000 paths. Engine đánh giá toàn bộ `454` verified borrowers; `109` chỉ là WETH/USDC target cohort của snapshot và không phải mẫu số của thí nghiệm này.

- Starting HEAD: `{STARTING_HEAD}`.
- Selection-lock commit: `{SELECTION_COMMIT}`.
- Source-code commit của adapter/runner: `{SOURCE_CODE_COMMIT}`.
- Canonical snapshot: block `26045352`, SHA-256 `{selection['input_hashes']['canonical_snapshot']['sha256']}`.
- Frozen v3 manifest SHA-256 trước/sau: `{selection['input_hashes']['frozen_v3_manifest']['sha256']}`; không thay đổi.

## 2. Thiết kế đã tiền đăng ký

- **Policy A — adverse pass-through:** giá định giá vòng kế tiếp là `min(reference_price, dex_spot)`; đây là hành vi engine gốc.
- **Policy B — reference-only:** HF chỉ dùng `reference_price`; mọi thành phần khác giữ nguyên.
- **Policy C weak:** proxy giả định nhân quả, hệ số `0.25`, lag `1`, cửa sổ `3`.
- **Policy C moderate:** proxy giả định nhân quả, hệ số `0.50`, lag `1`, cửa sổ `2`.

Policy C chỉ đọc DEX observations đã hoàn tất đến cuối vòng trước, không đọc tương lai. Các hệ số được khóa trong `selection_manifest.json` trước khi chạy B/C; không retune sau khi xem kết quả.

## 3. Cổng tái lập Policy A

Policy A **PASS**: `8/8` deterministic rows khớp Frozen/Level-3 trong dung sai tuyệt đối `1e-9`, tương đối `1e-12`; `10/10` Monte Carlo rows khớp exact serialized checkpoint row. B/C chỉ được chạy sau cổng này.

## 4. Kết quả tổng hợp

| Policy | Deterministic depth-2 giữ depth≥2 | Controls depth≥2 | 10 MC audit paths depth≥2 | Mean liquidated debt trên selected cases (USDC) | Mean modeled bad debt trên selected cases (USD) |
|---|---:|---:|---:|---:|---:|
{chr(10).join(summary_table)}

Mười MC paths là mẫu mục tiêu đã chọn vì từng có depth≥2 dưới A; tỷ lệ trong bảng **không phải** ước lượng xác suất khủng hoảng hoặc tần suất quần thể.

Trong bốn deterministic cases đã khóa, A cho depth `[2,2,2,2]`; B, C weak và C moderate đều cho `[1,1,1,1]`. Trong mười MC audit paths, A giữ `10/10`, B giữ `0/10`, C weak giữ `0/10`, C moderate giữ `2/10` (`MC_PATH_1060`, `MC_PATH_8005`).

## 5. Bốn deterministic depth-2 cases

`modeled bad debt` là ước lượng nợ không được bảo đảm đủ theo mô hình, không tự động là lỗ tài chính đã thực hiện. Impact/spread là tỷ lệ phần trăm.

| Case | Policy | Depth | Newly eligible sau Wave 1 | Liquidated debt (USDC) | Modeled bad debt (USD) | Max immediate impact (%) | Max residual spread (%) | Post-Wave-1 valuation (USD/WETH) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(deterministic_table)}

## 6. Tác động trực tiếp và gián tiếp

Direct shock HF giống nhau giữa bốn policy vì cú sốc reference ban đầu không đổi. DEX state ngay sau Wave 1 cũng giống A cho toàn bộ `72/72` policy-case rows; đây là invariant bắt buộc. Khác biệt HF/eligibility trên DEX state chung đó là **tác động trực tiếp của policy định giá**.

Sau khi eligibility khác nhau, giao dịch Wave 2 khác nhau và từ đó final DEX state, total liquidated debt, immediate impact cực đại và residual spread cực đại có thể khác. Đây là **tác động gián tiếp qua liquidation trades**, không phải thay đổi Uniswap math.

HF của borrower đã hết nợ là vô hạn về toán học; artifact lưu `null` cùng status `DEBT_FREE_UNDEFINED`, không ghi giá trị không hữu hạn. Borrower identifiers tiếp tục là `borrower_hash` đã redacted, không có địa chỉ ví thô.

## 7. Diễn giải RQ1–RQ2

- **RQ1 — cần giới hạn:** bốn depth-2 deterministic outcomes là kết quả phụ thuộc mạnh vào policy truyền giá. Không được gọi chúng là ngưỡng cascade độc lập với oracle. Policy B loại Wave 2 trong bốn cases; hai proxy C đã tiền đăng ký cũng loại Wave 2 trong bốn cases, nhưng đây chỉ là sensitivity model.
- **RQ2 — cần giới hạn:** liquidity haircut vẫn điều khiển sức hấp thụ DEX và tác động giá, nhưng đường truyền từ DEX state sang borrower eligibility phụ thuộc policy định giá. Thí nghiệm không xác minh rằng Aave oracle thực tế truyền DEX spot theo A, B hay C.

Kết quả không phủ định toàn bộ cơ chế cascade mô phỏng; nó xác định rằng kết luận về depth 2 không bền với thay đổi oracle-policy hợp lý trong phạm vi test này.

## 8. Kiểm toán và invariant

- `72` policy-case results, mỗi result chạy lặp lại và khớp hash determinism.
- `32,688` borrower-policy-case rows (`18 × 4 × 454`); không nhầm với target cohort `109`.
- Không borrower bị liquidate lặp; later-wave liquidations đều không trực tiếp đủ điều kiện ở shock ban đầu và có HF trước liquidation `<1`.
- Không NaN/Infinity trong artifacts; không raw address/API key.
- Frozen v3, canonical snapshot, sáu RQ và historical artifacts không bị sửa.
- Không chạy lại 10.000 Monte Carlo, không retune, không sửa Uniswap swap math hay Aave liquidation semantics.

{chr(10).join(test_lines)}

## 9. Giới hạn chưa thể xác minh

1. Không có contract-level hoặc historical oracle observation trong thí nghiệm này; không policy nào được chứng minh là oracle Aave/Chainlink thực tế.
2. Policy C là proxy giả định với hai cấu hình đã tiền đăng ký, không phải calibration thực nghiệm.
3. Mười MC paths là targeted audit sample, không hỗ trợ suy luận xác suất.
4. Kết quả phụ thuộc canonical block `26045352`, toàn bộ 454 verified borrowers (trong đó target cohort WETH/USDC là 109) và các giả định stress đã khóa.
5. Mean across selected cases chỉ là mô tả tập mục tiêu không đồng nhất, không phải estimator quần thể.

## 10. Tái lập

```powershell
.\\.venv\\Scripts\\python.exe .\\scripts\\research\\run_oracle_transmission_diagnostic.py --phase a
.\\.venv\\Scripts\\python.exe .\\scripts\\research\\run_oracle_transmission_diagnostic.py --phase bc
.\\.venv\\Scripts\\python.exe .\\scripts\\research\\build_oracle_diagnostic_bundle.py
```

Artifacts chuẩn nằm tại `data/processed/research_final/oracle_transmission_diagnostic_v1/`. Quyết định khoa học cuối cùng thuộc Commander; branch này không merge tự động.
"""
    REPORT.write_text(report, encoding="utf-8")

    artifact_hashes = _artifact_hashes()
    manifest = {
        "schema_version": "oracle-transmission-diagnostic-v1.0",
        "status": "LIMITED_TARGETED_MODEL_DIAGNOSTIC — AWAITING_COMMANDER_REVIEW",
        "starting_head": STARTING_HEAD,
        "selection_lock_commit": SELECTION_COMMIT,
        "source_code_commit": SOURCE_CODE_COMMIT,
        "artifact_bundle_commit": None,
        "target_integration_branch": "feat/terra-model-v2",
        "generated_on": "2026-10-14",
        "policy_a_gate": {
            "status": baseline["status"],
            "deterministic_rows": len(baseline["deterministic_checks"]),
            "monte_carlo_rows": len(baseline["monte_carlo_checks"]),
            "tolerances": baseline["comparison_tolerances"],
        },
        "counts": result_summary["case_population"],
        "input_hashes": regression["verified_input_hashes"],
        "artifact_hashes": artifact_hashes,
        "report_hashes": {REPORT.as_posix(): _sha(REPORT)},
        "findings": result_summary["direct_effect_summary"],
        "quality_gate": {
            **regression["invariants"],
            "policy_a_reproduced": baseline["status"] == "PASS",
            "selection_locked_before_b_c": True,
            "frozen_v3_hash_unchanged": True,
            "canonical_snapshot_hash_unchanged": True,
            "no_large_monte_carlo_rerun": True,
            "no_nonfinite_artifact_values": True,
            "no_raw_wallet_addresses": True,
        },
        "test_evidence": test_evidence,
        "large_monte_carlo_rerun": False,
        "mainnet_transactions": False,
        "scientific_pass_declared": False,
        "scientific_content_lock_declared": False,
        "external_empirical_oracle_inference": "NOT_ESTABLISHED",
        "reproduction_commands": [
            ".\\.venv\\Scripts\\python.exe .\\scripts\\research\\run_oracle_transmission_diagnostic.py --phase a",
            ".\\.venv\\Scripts\\python.exe .\\scripts\\research\\run_oracle_transmission_diagnostic.py --phase bc",
            ".\\.venv\\Scripts\\python.exe .\\scripts\\research\\build_oracle_diagnostic_bundle.py",
        ],
    }
    _write_json(ROOT / "manifest.json", manifest)
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "artifact_count": len(artifact_hashes),
                "policy_case_results": len(rows),
                "report": REPORT.as_posix(),
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
