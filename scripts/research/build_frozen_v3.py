from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path("data/processed/research_final/frozen_v3")
DOC_ROOT = Path("docs/research_final")
CANONICAL = Path("data/processed/mainnet/aave_uniswap_snapshot_26045352.json")
CORRECTED = Path("data/processed/research_final/validation_audit/corrected_run_v2")
LEVEL3 = Path("data/processed/research_final/level3_extension")
REPAIR = Path("data/processed/research_final/level3_p1_targeted_repair")
TERRA = Path("data/processed/research_final/terra/audit")
TERRA_EARLY_WARNING_AUDIT = Path(
    "data/processed/research_final/validation_audit/phase5_terra_early_warning_audit.json"
)
EXPECTED_CANONICAL_SHA = "553e93a345642dd4ef655dbcd883c12180d83327e9c9b917ff83c58dd9a3af99"
MODEL_VERSION = "0.1.0-aave-v3.10-metric-semantics"
FREEZE_STATUS = "P1_NUMERICAL_READY — AWAITING_P2_CITATION_RECONCILIATION"
LITERATURE_FILES_RESERVED = [
    "docs/research_final/APA_REFERENCES_VERIFIED.md",
    "docs/research_final/LITERATURE_VERIFIED.md",
    "docs/research_final/P2_VERSION_RECONCILIATION.md",
    "docs/research_final/REFERENCE_EVIDENCE_MATRIX.md",
    "docs/research_final/TERMINOLOGY_VI.md",
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"Refusing to write empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _result(
    result_id: str,
    value: Any,
    unit: str,
    population: str,
    conditions: str,
    source_version: str,
    source_path: Path,
    limitation: str,
    *,
    rq: str | None = None,
    evidence_type: str = "SIMULATED",
) -> dict[str, Any]:
    return {
        "result_id": result_id,
        "rq": rq,
        "value": value,
        "unit": unit,
        "population": population,
        "conditions": conditions,
        "evidence_type": evidence_type,
        "source_version": source_version,
        "model_version": None if evidence_type == "OBSERVED" else MODEL_VERSION,
        "source_path": source_path.as_posix(),
        "source_sha256": _sha(source_path),
        "interpretation_limit": limitation,
    }


def _finite(value: Any) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(_finite(item) for item in value.values())
    if isinstance(value, list):
        return all(_finite(item) for item in value)
    return True


def _metric_value(results: list[dict[str, Any]], result_id: str) -> Any:
    return next(item["value"] for item in results if item["result_id"] == result_id)


def _make_figures(
    root: Path,
    depth_counts: Counter[int],
    mc_rows: list[dict[str, str]],
    capital_rows: list[dict[str, str]],
    arb_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    figure_root = root / "figures"
    figure_root.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"figure.dpi": 150, "font.size": 9})

    figures: list[dict[str, Any]] = []
    path = figure_root / "F01_deterministic_depth_distribution.png"
    fig, ax = plt.subplots(figsize=(5.6, 3.5))
    xs = sorted(depth_counts)
    ax.bar([str(x) for x in xs], [depth_counts[x] for x in xs], color="#28666e")
    ax.set(xlabel="Độ sâu cascade quan sát", ylabel="Số tổ hợp", title="Lưới tất định mở rộng (60 tổ hợp)")
    for index, x in enumerate(xs):
        ax.text(index, depth_counts[x] + 0.6, str(depth_counts[x]), ha="center")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    figures.append(
        {
            "figure_id": "F01",
            "path": path.as_posix(),
            "result_ids": ["RQ1_GRID60_DEPTH0", "RQ1_GRID60_DEPTH1", "RQ1_GRID60_DEPTH2"],
            "caption_vi": {
                "noi_dung_do": "Phân bố độ sâu cascade trong lưới tất định mở rộng.",
                "loai_du_lieu": "Mô phỏng, không phải giao dịch lịch sử.",
                "mau_so_don_vi": "60 tổ hợp; trục tung là số tổ hợp.",
                "co_the_ket_luan": "Bốn tổ hợp đạt depth 2 trong miền stress đã khai báo.",
                "khong_the_ket_luan": "Không suy ra xác suất khủng hoảng hay độ sâu tối đa ngoài lưới.",
            },
        }
    )

    severe = [row for row in mc_rows if row["label"] == "Severe" and int(row["target_runs"]) <= 10_000]
    path = figure_root / "F02_severe_mc_prefix_convergence.png"
    fig, ax = plt.subplots(figsize=(5.6, 3.5))
    ax.plot(
        [int(row["actual_runs"]) for row in severe],
        [100 * float(row["depth_ge_2_frequency"]) for row in severe],
        marker="o",
        color="#7b2cbf",
    )
    ax.set(xlabel="Số đường mô phỏng trong prefix", ylabel="Tần suất depth ≥ 2 (%)", title="Severe Monte Carlo")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    figures.append(
        {
            "figure_id": "F02",
            "path": path.as_posix(),
            "result_ids": ["RQ1_MC_SEVERE_DEPTH2_COUNT", "RQ1_MC_SEVERE_DEPTH2_FREQUENCY"],
            "caption_vi": {
                "noi_dung_do": "Tần suất lấy mẫu depth ≥ 2 theo các checkpoint prefix Severe.",
                "loai_du_lieu": "Mô phỏng Monte Carlo đã khóa checkpoint.",
                "mau_so_don_vi": "200, 1.000, 5.000 và 10.000 đường; đơn vị phần trăm.",
                "co_the_ket_luan": "Checkpoint 10.000 có 280 đường depth ≥ 2 (2,8%).",
                "khong_the_ket_luan": "Tần suất trong mô hình không phải xác suất khủng hoảng thực tế.",
            },
        }
    )

    path = figure_root / "F03_liquidator_capital_constraint.png"
    fig, ax = plt.subplots(figsize=(5.6, 3.5))
    ax.bar(
        [f"{100 * float(row['capital_ratio']):.0f}%" for row in capital_rows],
        [float(row["total_liquidated_debt"]) for row in capital_rows],
        color=["#b23a48" if row["constraint_status"] == "BINDING" else "#3a7d44" for row in capital_rows],
    )
    ax.set(xlabel="Vốn / nhu cầu tham chiếu", ylabel="USDC debt đã thanh lý", title="Ràng buộc vốn người thanh lý")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    figures.append(
        {
            "figure_id": "F03",
            "path": path.as_posix(),
            "result_ids": ["RQ3_CAPITAL_25_LIQUIDATED", "RQ3_CAPITAL_100_LIQUIDATED"],
            "caption_vi": {
                "noi_dung_do": "Nợ được thực thi thanh lý khi thay đổi vốn người thanh lý.",
                "loai_du_lieu": "Mô phỏng counterfactual trên snapshot cố định.",
                "mau_so_don_vi": "Bốn mức vốn; nợ tính bằng USDC token quantity.",
                "co_the_ket_luan": "Mức 25% và 50% bị ràng buộc; 100% và 200% không bị ràng buộc trong thử nghiệm.",
                "khong_the_ket_luan": "Không đại diện cơ chế tái sử dụng vốn hay thị trường liquidator ngoài mô hình.",
            },
        }
    )

    path = figure_root / "F04_arbitrage_impact_and_residual_spread.png"
    fig, ax = plt.subplots(figsize=(5.6, 3.5))
    labels = [f"{row['capacity']:.0f}%" for row in arb_rows]
    width = 0.36
    xx = range(len(labels))
    ax.bar([x - width / 2 for x in xx], [100 * row["impact"] for row in arb_rows], width, label="Tác động ngay sau bán")
    ax.bar([x + width / 2 for x in xx], [100 * row["spread"] for row in arb_rows], width, label="Spread sau arbitrage")
    ax.set_xticks(list(xx), labels)
    ax.set(xlabel="Năng lực arbitrage", ylabel="Phần trăm", title="Tác động tức thời và độ lệch còn lại")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    figures.append(
        {
            "figure_id": "F04",
            "path": path.as_posix(),
            "result_ids": ["RQ4_IMMEDIATE_PRICE_IMPACT", "RQ4_SPREAD_ARB0", "RQ4_SPREAD_ARB100"],
            "caption_vi": {
                "noi_dung_do": "So sánh tác động giá ngay sau bán với spread còn lại sau arbitrage.",
                "loai_du_lieu": "Mô phỏng một kịch bản −20%, haircut 40%.",
                "mau_so_don_vi": "Ba mức năng lực arbitrage; đơn vị phần trăm giá tham chiếu.",
                "co_the_ket_luan": "Arbitrage làm giảm spread sau bán trong thiết kế này nhưng không đổi tác động tức thời.",
                "khong_the_ket_luan": "Không chứng minh tốc độ hoặc năng lực arbitrage thực tế trên Mainnet.",
            },
        }
    )
    return figures


def build(
    root: Path = ROOT,
    *,
    starting_head: str,
    implementation_commit: str,
    artifact_bundle_commit: str,
) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)
    (root / "tables").mkdir(exist_ok=True)
    (root / "figures").mkdir(exist_ok=True)

    corrected_summary = _load(CORRECTED / "aave" / "research_summary.json")
    hf = corrected_summary["canonical_snapshot"]["health_factor_validation"]
    grid32 = _rows(CORRECTED / "aave" / "shock_liquidity_grid.csv")
    grid60 = _rows(LEVEL3 / "deep_stress" / "deterministic_grid.csv")
    mc_rows = _rows(LEVEL3 / "tables" / "monte_carlo_stage_summary.csv")
    capital_rows = _rows(CORRECTED / "rq_completion" / "rq3_capital_constraint.csv")
    delay_rows = _rows(CORRECTED / "rq_completion" / "rq3_reaction_delay.csv")
    usdc_rows = _rows(CORRECTED / "rq_completion" / "rq5_usdc_depeg.csv")
    lt_rows = _rows(CORRECTED / "rq_completion" / "rq6_liquidation_threshold.csv")
    bonus_rows = _rows(CORRECTED / "rq_completion" / "rq6_liquidation_bonus.csv")
    ltv_rows = _rows(CORRECTED / "rq_completion" / "rq6_ltv_capital_efficiency.csv")
    det_rows = _rows(CORRECTED / "aave" / "deterministic_scenarios.csv")
    census = _load(REPAIR / "historical" / "census_reconciliation.json")
    linkage = _load(REPAIR / "historical" / "linkage_route_audit.json")
    checkpoints = _load(REPAIR / "monte_carlo" / "checkpoint_validation.json")
    strict_oos = _load(TERRA_EARLY_WARNING_AUDIT)

    canonical_hash = _sha(CANONICAL)
    if canonical_hash != EXPECTED_CANONICAL_SHA:
        raise ValueError("Canonical Mainnet snapshot hash changed")
    if len(grid32) != 32 or len(grid60) != 60:
        raise ValueError("Expected the preserved 32-cell grid and extended 60-cell grid")
    depth32 = Counter(int(row["cascade_depth"]) for row in grid32)
    depth60 = Counter(int(row["cascade_depth"]) for row in grid60)
    if depth32 != Counter({1: 20, 0: 12}) or depth60 != Counter({1: 38, 0: 18, 2: 4}):
        raise ValueError("Cascade grid counts do not match the locked evidence")

    severe10k = next(row for row in mc_rows if row["label"] == "Severe" and row["target_runs"] == "10000")
    arb_source = {row["scenario_name"]: row for row in det_rows}
    arb_rows = [
        {
            "capacity": capacity,
            "impact": float(arb_source[name]["max_intrawave_liquidation_price_impact"]),
            "spread": float(arb_source[name]["max_post_arbitrage_spread"]),
        }
        for capacity, name in [(0.0, "No Arbitrage"), (50.0, "PROFESSOR_DEMO"), (100.0, "Strong Arbitrage")]
    ]
    usdc_by_price = {float(row["usdc_price_usd"]): row for row in usdc_rows}
    lt_by_value = {float(row["liquidation_threshold"]): row for row in lt_rows}
    bonus_by_value = {float(row["liquidation_bonus"]): row for row in bonus_rows}
    ltv_by_value = {float(row["ltv_policy"]): row for row in ltv_rows}

    observed_limit = "Không suy rộng cohort ứng viên thành độ phủ toàn thị trường."
    model_limit = "Kết quả có điều kiện trên snapshot, cohort và miền tham số đã khai báo; không phải dự báo Mainnet."
    results = [
        _result("AAVE_SNAPSHOT_BLOCK", 26_045_352, "Ethereum block", "same-block Mainnet snapshot", "chain_id=1", "Original", CANONICAL, observed_limit, evidence_type="OBSERVED"),
        _result("AAVE_VERIFIED_BORROWERS", 454, "borrowers", "top 500 Graph-discovered debt candidates", "positive RPC-verified debt", "Original", CANONICAL, observed_limit, evidence_type="OBSERVED"),
        _result("AAVE_WETH_USDC_COHORT", 109, "positions", "verified borrowers", "WETH collateral enabled and USDC debt > 0", "Original", CANONICAL, "Đây là cohort mục tiêu, không phải toàn Aave.", evidence_type="OBSERVED"),
        _result("AAVE_HF_MAX_ABS_ERROR", hf["max_absolute_error"], "HF units", "454 verified borrowers", "canonical price state", "P0 corrected v2", CORRECTED / "aave" / "research_summary.json", "Sai số tuyệt đối lớn chịu ảnh hưởng của HF rất lớn; phải đọc cùng sai số tương đối.", evidence_type="DERIVED"),
        _result("AAVE_HF_MAX_REL_ERROR", hf["max_relative_error_ratio"], "ratio", "454 verified borrowers", "canonical price state", "P0 corrected v2", CORRECTED / "aave" / "research_summary.json", "Không phải sai số dưới stress counterfactual.", evidence_type="DERIVED"),
        _result("RQ1_GRID32_MAX_DEPTH", max(depth32), "waves", "32 deterministic cells", "shock −5%…−40%; haircut 0/25/50/75%", "P0 corrected v2", CORRECTED / "aave" / "shock_liquidity_grid.csv", "Lưới cũ không gồm haircut 90/95% và shock −50%.", rq="RQ1"),
        _result("RQ1_GRID60_DEPTH0", depth60[0], "cells", "60 deterministic cells", "prespecified extended grid", "Level-3", LEVEL3 / "deep_stress" / "deterministic_grid.csv", model_limit, rq="RQ1"),
        _result("RQ1_GRID60_DEPTH1", depth60[1], "cells", "60 deterministic cells", "prespecified extended grid", "Level-3", LEVEL3 / "deep_stress" / "deterministic_grid.csv", model_limit, rq="RQ1"),
        _result("RQ1_GRID60_DEPTH2", depth60[2], "cells", "60 deterministic cells", "prespecified extended grid", "Level-3", LEVEL3 / "deep_stress" / "deterministic_grid.csv", "Bốn cell sử dụng tail haircuts 90/95%, là giả định counterfactual chưa quan sát.", rq="RQ1"),
        _result("RQ1_MC_SEVERE_DEPTH2_COUNT", int(severe10k["depth_ge_2_successes"]), "paths", "10,000 Severe paths", "seed=20260914; max_waves=100; horizon=120", "Level-3 targeted repair", REPAIR / "monte_carlo" / "checkpoint_validation.json", "Checkpoint được xác minh, không chạy lại 10.000 đường trong P1.", rq="RQ1"),
        _result("RQ1_MC_SEVERE_DEPTH2_FREQUENCY", float(severe10k["depth_ge_2_frequency"]), "ratio", "10,000 Severe paths", "same as count", "Level-3 targeted repair", REPAIR / "monte_carlo" / "checkpoint_validation.json", "Tần suất mô hình, không phải xác suất khủng hoảng thực tế.", rq="RQ1"),
        _result("RQ1_MC_SEVERE_DEPTH3_COUNT", int(severe10k["depth_ge_3_successes"]), "paths", "10,000 Severe paths", "same as count", "Level-3 targeted repair", REPAIR / "monte_carlo" / "checkpoint_validation.json", "Không quan sát không đồng nghĩa bất khả thi.", rq="RQ1"),
        _result("RQ2_CANONICAL_DEPTH_2PCT", corrected_summary["canonical_snapshot"]["uniswap"]["depth_usdc_2pct"], "USDC", "canonical WETH/USDC 0.3% pool", "executable depth within 2%", "P0 corrected v2", CORRECTED / "aave" / "research_summary.json", "Một pool và một block, không đại diện toàn thanh khoản ETH.", rq="RQ2", evidence_type="OBSERVED"),
        _result("RQ2_DEPTH2_HAIRCUT90_COUNT", sum(int(row["cascade_depth"]) == 2 and float(row["liquidity_haircut_pct"]) == 90 for row in grid60), "cells", "60 deterministic cells", "haircut=90%", "Level-3", LEVEL3 / "deep_stress" / "deterministic_grid.csv", "Haircut 90% chưa được xác nhận bằng độ sâu lịch sử.", rq="RQ2"),
        _result("RQ2_DEPTH2_HAIRCUT95_COUNT", sum(int(row["cascade_depth"]) == 2 and float(row["liquidity_haircut_pct"]) == 95 for row in grid60), "cells", "60 deterministic cells", "haircut=95%", "Level-3", LEVEL3 / "deep_stress" / "deterministic_grid.csv", "Haircut 95% chưa được xác nhận bằng độ sâu lịch sử.", rq="RQ2"),
        _result("RQ3_DELAY_SEVERITY_CHANGE", 0.0, "USDC", "delay sweep 0/1/2/4 steps", "−20% shock; haircut 40%", "P0 corrected v2", CORRECTED / "rq_completion" / "rq3_reaction_delay.csv", "Delay chỉ trì hoãn thời điểm xử lý trong range này; không phải time-to-recovery.", rq="RQ3"),
        _result("RQ3_CAPITAL_25_LIQUIDATED", float(capital_rows[0]["total_liquidated_debt"]), "USDC token quantity", "109-position WETH/USDC cohort", "capital=25% reference demand", "P0 corrected v2", CORRECTED / "rq_completion" / "rq3_capital_constraint.csv", model_limit, rq="RQ3"),
        _result("RQ3_CAPITAL_100_LIQUIDATED", float(capital_rows[2]["total_liquidated_debt"]), "USDC token quantity", "109-position WETH/USDC cohort", "capital=100% reference demand", "P0 corrected v2", CORRECTED / "rq_completion" / "rq3_capital_constraint.csv", model_limit, rq="RQ3"),
        _result("RQ4_IMMEDIATE_PRICE_IMPACT", arb_rows[1]["impact"], "ratio", "Professor Demo liquidation sale", "−20% shock; haircut 40%", "P0 corrected v2", CORRECTED / "aave" / "deterministic_scenarios.csv", "Đây là tác động ngay sau bán, không phải spread sau arbitrage.", rq="RQ4"),
        _result("RQ4_SPREAD_ARB0", arb_rows[0]["spread"], "ratio", "same scenario", "arbitrage capacity=0%", "P0 corrected v2", CORRECTED / "aave" / "deterministic_scenarios.csv", "Độ lệch mô phỏng sau arbitrage, không phải quote lịch sử.", rq="RQ4"),
        _result("RQ4_SPREAD_ARB100", arb_rows[2]["spread"], "ratio", "same scenario", "arbitrage capacity=100%", "P0 corrected v2", CORRECTED / "aave" / "deterministic_scenarios.csv", "Zero trong mô hình là tái định vị hoàn toàn theo quy tắc agent.", rq="RQ4"),
        _result("RQ5_HF_LT1_USDC_090", int(usdc_by_price[0.9]["borrowers_hf_below_1_00"]), "borrowers", "109-position WETH/USDC cohort", "USDC price=0.90 USD; debt valuation only", "P0 corrected v2", CORRECTED / "rq_completion" / "rq5_usdc_depeg.csv", "Không có liquidity/redemption/settlement channel.", rq="RQ5"),
        _result("RQ5_HF_LT1_USDC_100", int(usdc_by_price[1.0]["borrowers_hf_below_1_00"]), "borrowers", "109-position WETH/USDC cohort", "USDC price=1.00 USD", "P0 corrected v2", CORRECTED / "rq_completion" / "rq5_usdc_depeg.csv", "Không có liquidity/redemption/settlement channel.", rq="RQ5"),
        _result("RQ5_HF_LT1_USDC_110", int(usdc_by_price[1.1]["borrowers_hf_below_1_00"]), "borrowers", "109-position WETH/USDC cohort", "USDC price=1.10 USD; debt valuation only", "P0 corrected v2", CORRECTED / "rq_completion" / "rq5_usdc_depeg.csv", "Không có liquidity/redemption/settlement channel.", rq="RQ5"),
        _result("RQ5_LIQUIDATED_DEBT_TOKEN_QTY", float(usdc_by_price[1.1]["total_liquidated_debt_usdc"]), "USDC token quantity", "109-position WETH/USDC cohort", "USDC price=1.10 USD", "P0 corrected v2", CORRECTED / "rq_completion" / "rq5_usdc_depeg.csv", "Phải phân biệt token quantity với USD-equivalent.", rq="RQ5"),
        _result("RQ5_LIQUIDATED_DEBT_USD", float(usdc_by_price[1.1]["total_liquidated_debt_usd"]), "USD equivalent", "109-position WETH/USDC cohort", "USDC price=1.10 USD", "P0 corrected v2", CORRECTED / "rq_completion" / "rq5_usdc_depeg.csv", "Định giá theo giả định USDC=1.10 USD.", rq="RQ5"),
        _result("RQ6_LTV0755_CAPACITY", float(ltv_by_value[0.755]["aggregate_max_borrowing_capacity_usd"]), "USD", "109-position frozen cohort", "counterfactual LTV=75.5%", "P0 corrected v2", CORRECTED / "rq_completion" / "rq6_ltv_capital_efficiency.csv", "Ex-ante capacity, không phải liquidation trigger.", rq="RQ6"),
        _result("RQ6_LTV0825_CAPACITY", float(ltv_by_value[0.825]["aggregate_max_borrowing_capacity_usd"]), "USD", "109-position frozen cohort", "counterfactual LTV=82.5%", "P0 corrected v2", CORRECTED / "rq_completion" / "rq6_ltv_capital_efficiency.csv", "Ex-ante capacity, không phải liquidation trigger.", rq="RQ6"),
        _result("RQ6_LT083_UNLIQUIDATED", float(lt_by_value[0.83]["unliquidated_debt"]), "USDC token quantity", "109-position frozen cohort", "WETH LT override=83%", "P0 corrected v2", CORRECTED / "rq_completion" / "rq6_liquidation_threshold.csv", "Dùng scenario LT; legacy recorded-LT field chỉ để đối chiếu.", rq="RQ6"),
        _result("RQ6_LT0855_UNLIQUIDATED", float(lt_by_value[0.855]["unliquidated_debt"]), "USDC token quantity", "109-position frozen cohort", "WETH LT override=85.5%", "P0 corrected v2", CORRECTED / "rq_completion" / "rq6_liquidation_threshold.csv", "Dùng scenario LT; other-collateral LT không bị ghi đè.", rq="RQ6"),
        _result("RQ6_BONUS103_SEIZED", float(bonus_by_value[1.03]["collateral_seized_weth"]), "WETH", "executed liquidation in test scenario", "bonus=3%", "P0 corrected v2", CORRECTED / "rq_completion" / "rq6_liquidation_bonus.csv", "Policy counterfactual, không phải executed Mainnet liquidation.", rq="RQ6"),
        _result("RQ6_BONUS107_SEIZED", float(bonus_by_value[1.07]["collateral_seized_weth"]), "WETH", "executed liquidation in test scenario", "bonus=7%", "P0 corrected v2", CORRECTED / "rq_completion" / "rq6_liquidation_bonus.csv", "Policy counterfactual, không phải executed Mainnet liquidation.", rq="RQ6"),
        _result("HIST_RPC_CENSUS_EVENTS", census["rpc_census_count"], "LiquidationCall events", "Aave V3 Pool, 2026-09-01…07 UTC", "independent RPC log census", "Level-3 targeted repair", REPAIR / "historical" / "census_reconciliation.json", "Một tuần tiền đăng ký; không phải toàn bộ lịch sử Aave.", evidence_type="OBSERVED"),
        _result("HIST_GRAPH_MATCHED_EVENTS", census["matched_count"], "events", "same week", "Graph candidates reverified by RPC", "Level-3 targeted repair", REPAIR / "historical" / "census_reconciliation.json", "Graph bỏ sót một event trong RPC census.", evidence_type="OBSERVED"),
        _result("HIST_DIRECT_TRANSFER_PATHS", linkage["tier_counts"]["DIRECT_TRANSFER_PATH_VERIFIED"], "events", "27 Graph-matched events", "ordered exact-amount WETH transfer path", "Level-3 targeted repair", REPAIR / "historical" / "linkage_route_audit.json", "Bằng chứng tuyến tài sản không tự chứng minh nhân quả thị trường.", evidence_type="OBSERVED"),
        _result("HIST_SAME_TX_COOCCURRENCE", linkage["tier_counts"]["SAME_TRANSACTION_CO_OCCURRENCE"], "events", "27 Graph-matched events", "same transaction without verified direct transfer path", "Level-3 targeted repair", REPAIR / "historical" / "linkage_route_audit.json", "Không gọi là direct transfer hoặc causal transmission.", evidence_type="OBSERVED"),
        _result("HIST_SAME_BLOCK_ASSOCIATION", linkage["tier_counts"]["SAME_BLOCK_ASSOCIATION"], "events", "27 Graph-matched events", "same block", "Level-3 targeted repair", REPAIR / "historical" / "linkage_route_audit.json", "Temporal association only.", evidence_type="OBSERVED"),
        _result("HIST_TIME_WINDOW_ASSOCIATION", linkage["tier_counts"]["TIME_WINDOW_ASSOCIATION"], "events", "27 Graph-matched events", "nearby in time", "Level-3 targeted repair", REPAIR / "historical" / "linkage_route_audit.json", "Weakest evidence tier; no direct linkage.", evidence_type="OBSERVED"),
        _result("TERRA_PRE_DEPEG_HIGH_ALERT_HOURS", strict_oos["modes"]["CUTOFF_SAFE"]["pre_initial_depeg_high_alert_hours"], "hours", "1,630 pre-initial-depeg hours", "cutoff-safe indicator", "Original Terra locked", TERRA_EARLY_WARNING_AUDIT, "Negative finding; no genuine out-of-sample forecast claim.", evidence_type="DERIVED"),
        _result("TERRA_INITIAL_DEPEG_HIGH_LEAD", strict_oos["modes"]["CUTOFF_SAFE"]["lead_times"]["ust_below_0_995"]["high"]["lead_time_hours"], "hours", "UST < 0.995 event", "cutoff-safe HIGH threshold", "Original Terra locked", TERRA_EARLY_WARNING_AUDIT, "Negative means warning after event; design choices were event-informed.", evidence_type="DERIVED"),
        _result("MC_INDEPENDENT_PATHS_VALIDATED", checkpoints["independent_batch_unique_path_count"], "paths", "locked Level-3 checkpoints", "identity and nested-prefix audit", "Level-3 targeted repair", REPAIR / "monte_carlo" / "checkpoint_validation.json", "Historical execution duration for legacy 10k is unavailable; no rerun in P1.", evidence_type="DERIVED"),
    ]

    evidence = [
        {"evidence_id": "EV_CANONICAL_SNAPSHOT", "type": "OBSERVED", "path": CANONICAL.as_posix(), "sha256": canonical_hash, "scope": "Aave/Uniswap same-block state"},
        {"evidence_id": "EV_CORRECTED_V2", "type": "SIMULATED", "path": (CORRECTED / "manifest.json").as_posix(), "sha256": _sha(CORRECTED / "manifest.json"), "scope": "P0 numerical semantics and RQ sweeps"},
        {"evidence_id": "EV_LEVEL3", "type": "SIMULATED_AND_OBSERVED", "path": (LEVEL3 / "manifest.json").as_posix(), "sha256": _sha(LEVEL3 / "manifest.json"), "scope": "60-cell grid, checkpoints, historical study"},
        {"evidence_id": "EV_TARGETED_REPAIR", "type": "OBSERVED_AND_AUDITED", "path": (REPAIR / "manifest.json").as_posix(), "sha256": _sha(REPAIR / "manifest.json"), "scope": "28-event census, evidence tiers, checkpoint audit"},
        {"evidence_id": "EV_TERRA_LOCKED", "type": "OBSERVED_AND_DERIVED", "path": (TERRA / "reproducibility_manifest.json").as_posix(), "sha256": _sha(TERRA / "reproducibility_manifest.json"), "scope": "Terra historical extension"},
    ]
    evidence_ids = {item["evidence_id"] for item in evidence}
    result_ids = {item["result_id"] for item in results}
    if len(result_ids) != len(results):
        raise ValueError("Duplicate result_id")

    claims = [
        {"claim_id": "CL_AAVE_SCOPE", "status": "PASS — VERIFIED", "statement_vi": "Snapshot chính có 454 borrower RPC-verified và cohort WETH/USDC 109.", "result_ids": ["AAVE_VERIFIED_BORROWERS", "AAVE_WETH_USDC_COHORT"], "evidence_ids": ["EV_CANONICAL_SNAPSHOT"], "table_ids": ["T02"], "figure_ids": [], "boundary_vi": observed_limit},
        {"claim_id": "CL_RQ1", "status": "LIMITED — REPORT WITH CAVEAT", "statement_vi": "Lưới 60 ô có bốn cell depth 2; Severe có 280/10.000 đường depth ≥2 và không có depth ≥3.", "result_ids": ["RQ1_GRID60_DEPTH2", "RQ1_MC_SEVERE_DEPTH2_COUNT", "RQ1_MC_SEVERE_DEPTH3_COUNT"], "evidence_ids": ["EV_LEVEL3", "EV_TARGETED_REPAIR"], "table_ids": ["T03", "T04"], "figure_ids": ["F01", "F02"], "boundary_vi": "Không gọi tần suất mô hình là xác suất thực tế; cap 100 không phải depth đạt được."},
        {"claim_id": "CL_RQ2", "status": "LIMITED — REPORT WITH CAVEAT", "statement_vi": "Thanh khoản thấp làm giảm sức hấp thụ và trong tail haircuts 90/95% xuất hiện depth 2.", "result_ids": ["RQ2_CANONICAL_DEPTH_2PCT", "RQ2_DEPTH2_HAIRCUT90_COUNT", "RQ2_DEPTH2_HAIRCUT95_COUNT"], "evidence_ids": ["EV_CORRECTED_V2", "EV_LEVEL3"], "table_ids": ["T05"], "figure_ids": ["F01"], "boundary_vi": "Tail haircuts là counterfactual, một pool, một snapshot."},
        {"claim_id": "CL_RQ3", "status": "LIMITED — REPORT WITH CAVEAT", "statement_vi": "Vốn 25/50% bị ràng buộc; 100/200% không bị ràng buộc; delay 0–4 chỉ đổi thời điểm trong miền thử.", "result_ids": ["RQ3_CAPITAL_25_LIQUIDATED", "RQ3_CAPITAL_100_LIQUIDATED", "RQ3_DELAY_SEVERITY_CHANGE"], "evidence_ids": ["EV_CORRECTED_V2"], "table_ids": ["T06"], "figure_ids": ["F03"], "boundary_vi": "Phân biệt vốn, công suất, reaction delay và recovery."},
        {"claim_id": "CL_RQ4", "status": "LIMITED — REPORT WITH CAVEAT", "statement_vi": "Arbitrage giảm spread còn lại nhưng không thay đổi tác động giá tức thời của cùng lượng bán.", "result_ids": ["RQ4_IMMEDIATE_PRICE_IMPACT", "RQ4_SPREAD_ARB0", "RQ4_SPREAD_ARB100"], "evidence_ids": ["EV_CORRECTED_V2"], "table_ids": ["T07"], "figure_ids": ["F04"], "boundary_vi": "Agent đơn giản; không phải fork execution hay historical causal estimate."},
        {"claim_id": "CL_RQ5", "status": "LIMITED — REPORT WITH CAVEAT", "statement_vi": "Trong kênh định giá nợ đơn thuần, USDC tăng giá làm HF yếu hơn; token quantity khác USD-equivalent.", "result_ids": ["RQ5_HF_LT1_USDC_090", "RQ5_HF_LT1_USDC_100", "RQ5_HF_LT1_USDC_110", "RQ5_LIQUIDATED_DEBT_TOKEN_QTY", "RQ5_LIQUIDATED_DEBT_USD"], "evidence_ids": ["EV_CORRECTED_V2"], "table_ids": ["T08"], "figure_ids": [], "boundary_vi": "Chưa mô hình hóa liquidity, settlement hoặc redemption của USDC."},
        {"claim_id": "CL_RQ6", "status": "LIMITED — REPORT WITH CAVEAT", "statement_vi": "LTV chi phối năng lực vay ex ante; LT chi phối HF/liquidation boundary; bonus chi phối collateral seized và lợi nhuận mô hình.", "result_ids": ["RQ6_LTV0755_CAPACITY", "RQ6_LTV0825_CAPACITY", "RQ6_LT083_UNLIQUIDATED", "RQ6_BONUS103_SEIZED", "RQ6_BONUS107_SEIZED"], "evidence_ids": ["EV_CORRECTED_V2"], "table_ids": ["T09"], "figure_ids": [], "boundary_vi": "Policy counterfactual trên frozen cohort; không dự báo tái underwrite."},
        {"claim_id": "CL_HISTORICAL", "status": "LIMITED — REPORT WITH CAVEAT", "statement_vi": "RPC census có 28 event; Graph khớp 27; các tier là 1 direct path, 2 same-tx, 23 same-block, 1 time-window.", "result_ids": ["HIST_RPC_CENSUS_EVENTS", "HIST_GRAPH_MATCHED_EVENTS", "HIST_DIRECT_TRANSFER_PATHS", "HIST_SAME_TX_COOCCURRENCE", "HIST_SAME_BLOCK_ASSOCIATION", "HIST_TIME_WINDOW_ASSOCIATION"], "evidence_ids": ["EV_TARGETED_REPAIR"], "table_ids": ["T10"], "figure_ids": [], "boundary_vi": "Không tuyên bố chuỗi nhân quả lịch sử."},
        {"claim_id": "CL_TERRA_NEGATIVE", "status": "LIMITED — REPORT WITH CAVEAT", "statement_vi": "Terra cutoff-safe không có HIGH alert trước initial depeg và không hỗ trợ claim forecast out-of-sample.", "result_ids": ["TERRA_PRE_DEPEG_HIGH_ALERT_HOURS", "TERRA_INITIAL_DEPEG_HIGH_LEAD"], "evidence_ids": ["EV_TERRA_LOCKED"], "table_ids": ["T11"], "figure_ids": [], "boundary_vi": "Giữ nguyên kết quả âm và giới hạn tần suất quan sát."},
    ]

    rq_details = [
        {"rq": "RQ1", "question_vi": "Ngưỡng và điều kiện xuất hiện thanh lý dây chuyền là gì?", "method_vi": "Đối chiếu lưới P0 32 ô với lưới mở rộng 60 ô và checkpoint Severe 10.000 đường.", "data_vi": "Snapshot block 26.045.352; 454 borrower xác minh; cohort 109; state Aave/Uniswap cùng block.", "experiment_vi": "Shock −5%…−50%, haircut tới 95%, cap tới 100 wave và horizon tới 120 step; không ép Wave 2.", "result_vi": "Lưới 32 ô: 12 depth 0, 20 depth 1, không depth 2. Lưới 60 ô: 18/38/4 ở depth 0/1/2. Severe: 280/10.000 depth ≥2; 0 depth ≥3.", "interpretation_vi": "Wave 2 chỉ xuất hiện trong tail liquidity assumptions; kiểm toán trực tiếp xác nhận borrower Wave 2 mới đủ điều kiện sau wave trước.", "limitation_vi": "Haircut 90/95% chưa có độ sâu Mainnet lịch sử; frequency mô hình không phải xác suất thực.", "conclusion_vi": "Có bằng chứng model-conditional cho depth 2, chưa có bằng chứng cho depth ≥3 hoặc ngưỡng phổ quát.", "status": "LIMITED — REPORT WITH CAVEAT", "claim_ids": ["CL_RQ1"]},
        {"rq": "RQ2", "question_vi": "Thanh khoản thị trường ảnh hưởng cascade như thế nào?", "method_vi": "So sánh executable depth và shock×haircut, đọc lượng WETH bán, price impact, residual spread và wave depth.", "data_vi": "Uniswap V3 WETH/USDC 0,3% tại cùng snapshot block; depth 2% khoảng 1,668 triệu USDC.", "experiment_vi": "Haircut 0–95%; shock −5%…−50%; các cell khác giữ theo grid đã khai báo.", "result_vi": "Bốn cell depth 2 đều ở haircut 90/95%; haircut làm giảm sức hấp thụ giao dịch và tăng biến dạng giá trong tail.", "interpretation_vi": "Thanh khoản là bộ đệm hấp thụ forced sale; suy giảm depth có thể tạo eligibility mới ở wave sau.", "limitation_vi": "Một pool, liquidity tĩnh/counterfactual; không có routing đa venue.", "conclusion_vi": "Thanh khoản quyết định mức khuếch đại trong mô hình nhưng tail thresholds chưa được xác nhận lịch sử.", "status": "LIMITED — REPORT WITH CAVEAT", "claim_ids": ["CL_RQ2"]},
        {"rq": "RQ3", "question_vi": "Chi phí và giới hạn năng lực người thanh lý đóng vai trò gì?", "method_vi": "Tách sweeps vốn, capacity/gas và reaction delay.", "data_vi": "Cohort 109 vị thế trên snapshot cố định; nhu cầu vốn tham chiếu 9.063,255437 USDC.", "experiment_vi": "Vốn 25/50/100/200%; delay 0/1/2/4 step; các sweep capacity/gas hiện có.", "result_vi": "25/50% vốn chặn execution; 100/200% cho cùng 9.063,255437 USDC thanh lý. Delay không đổi severity trong range.", "interpretation_vi": "Funding stock, throughput và latency là ba ràng buộc khác nhau; time-to-position-processing không phải time-to-recovery.", "limitation_vi": "Capital cộng dồn không tái sử dụng; execution agent đơn giản.", "conclusion_vi": "Vốn binding trong miền thấp; bằng chứng cho delay/gas/capacity còn âm hoặc không binding trong miền thử.", "status": "LIMITED — REPORT WITH CAVEAT", "claim_ids": ["CL_RQ3"]},
        {"rq": "RQ4", "question_vi": "Arbitrage có ổn định giá sau forced sale không?", "method_vi": "So sánh immediate liquidation price impact với post-arbitrage residual spread ở capacity 0/50/100%.", "data_vi": "Kịch bản −20%, haircut 40%, cùng lượng forced sale 4,408546 WETH.", "experiment_vi": "Thay đổi duy nhất năng lực arbitrage.", "result_vi": "Immediate impact giữ ở 0,108794%; residual spread giảm từ 0,108794% (0%) xuống 0,054397% (50%) và xấp xỉ 0 (100%).", "interpretation_vi": "Agent arbitrage tái neo giá sau bán, không xóa impact phát sinh tại thời điểm execution.", "limitation_vi": "Không có competition, latency thực, gas strategy hoặc fork SwapRouter execution.", "conclusion_vi": "Ổn định hậu arbitrage được hỗ trợ trong mô hình; không phải bằng chứng hiệu quả arbitrage ngoài đời.", "status": "LIMITED — REPORT WITH CAVEAT", "claim_ids": ["CL_RQ4"]},
        {"rq": "RQ5", "question_vi": "Mất neo USDC tác động thế nào khi USDC là debt asset?", "method_vi": "Giữ token debt quantity, định giá USDC từ 0,90 đến 1,10 USD và tính lại HF/liquidation metrics.", "data_vi": "109 vị thế WETH collateral + USDC debt.", "experiment_vi": "Debt-valuation channel only; không thêm liquidity/redemption/settlement.", "result_vi": "Số HF<1 là 1/1/3 tại USDC 0,90/1,00/1,10. 9.063,255437 USDC token tương đương 9.969,580981 USD tại giá 1,10.", "interpretation_vi": "USDC tăng giá làm nghĩa vụ nợ USD lớn hơn; giảm giá làm nghĩa vụ USD nhỏ hơn trong kênh cô lập này.", "limitation_vi": "Không mô hình hóa khả năng thanh toán, thanh khoản hay confidence của stablecoin.", "conclusion_vi": "Chỉ kết luận về kênh định giá nợ, không về toàn bộ cơ chế depeg.", "status": "LIMITED — REPORT WITH CAVEAT", "claim_ids": ["CL_RQ5"]},
        {"rq": "RQ6", "question_vi": "Đánh đổi giữa LTV, liquidation threshold và liquidation bonus là gì?", "method_vi": "Ba counterfactual tách biệt: LTV capacity, LT HF boundary, bonus execution economics.", "data_vi": "Frozen cohort 109 vị thế; other-collateral parameters được giữ riêng.", "experiment_vi": "LTV 75,5–82,5%; LT 81–88%; bonus 3–7%.", "result_vi": "Tăng LTV làm capacity tổng tăng 50,798 lên 53,676 triệu USD; LT đổi eligibility/unliquidated debt theo scenario; bonus 3→7% làm WETH seized tăng 4,324574→4,492519.", "interpretation_vi": "LTV là ràng buộc cấp tín dụng ex ante; LT là trigger solvency; bonus là incentive/transfer khi execution.", "limitation_vi": "Không có phản ứng tái underwrite hay hành vi borrower sau policy change.", "conclusion_vi": "Ba tham số không thể dùng thay thế nhau; mỗi tham số tạo một trade-off khác.", "status": "LIMITED — REPORT WITH CAVEAT", "claim_ids": ["CL_RQ6"]},
    ]

    precedence = {
        "rule": "For a duplicated metric, use the highest applicable rank; preserved lower versions remain audit evidence.",
        "versions": [
            {"rank": 1, "version": "Original", "role": "locked raw/canonical evidence"},
            {"rank": 2, "version": "P0 corrected v2", "role": "corrected numerical semantics and RQ sweeps"},
            {"rank": 3, "version": "Level-3", "role": "extended 60-cell/13k-path/historical evidence"},
            {"rank": 4, "version": "Level-3 targeted repair", "role": "28-event census, tier repair, checkpoint audit"},
            {"rank": 5, "version": "Frozen v3", "role": "registry and synthesis only; no model retuning"},
        ],
    }
    superseded = {
        "rule": "Superseded means excluded from current synthesis, not deleted.",
        "items": [
            {"old": "27 events as complete weekly set", "replacement": "28 RPC-census events; 27 Graph-matched", "reason": "independent Pool census found one Graph omission"},
            {"old": "3 DIRECT_TRANSACTION_LINK", "replacement": "1 direct transfer path + 2 same-transaction co-occurrences", "reason": "ordered exact-amount transfer audit"},
            {"old": "no Wave 2 in all experiments", "replacement": "no Wave 2 in 32-cell P0 grid; four depth-2 cells in 60-cell grid", "reason": "extended prespecified tail grid"},
            {"old": "max_price_impact as a single ambiguous metric", "replacement": "max_intrawave_liquidation_price_impact and max_post_arbitrage_spread", "reason": "P0 metric-semantics correction"},
            {"old": "reaction delay reported as recovery", "replacement": "position-processing delay separated from threshold-based recovery", "reason": "P0 timing-semantics correction"},
            {"old": "unliquidated debt under recorded LT during LT override", "replacement": "scenario-LT unliquidated debt", "reason": "P0 LT override correction"},
        ],
        "preserved_versioned_reports": [
            "docs/research_final/LEVEL3_HISTORICAL_EVENT_STUDY.md",
            "docs/research_final/LEVEL3_COMMANDER_REVIEW_PACKET.md",
        ],
    }

    figures = _make_figures(root, depth60, mc_rows, capital_rows, arb_rows)
    table_registry = [
        {"table_id": "T01", "path": "tables/version_precedence.csv", "purpose": "Data version precedence"},
        {"table_id": "T02", "path": "tables/core_facts.csv", "purpose": "Canonical scope and validation"},
        {"table_id": "T03", "path": "tables/rq1_deterministic_depth.csv", "purpose": "32 vs 60 grid"},
        {"table_id": "T04", "path": "tables/rq1_monte_carlo.csv", "purpose": "Severe checkpoints"},
        {"table_id": "T05", "path": "tables/rq2_liquidity.csv", "purpose": "Liquidity absorption and depth"},
        {"table_id": "T06", "path": "tables/rq3_constraints.csv", "purpose": "Capital and delay"},
        {"table_id": "T07", "path": "tables/rq4_arbitrage.csv", "purpose": "Immediate impact vs residual spread"},
        {"table_id": "T08", "path": "tables/rq5_usdc_valuation.csv", "purpose": "USDC token and USD units"},
        {"table_id": "T09", "path": "tables/rq6_policy.csv", "purpose": "LTV/LT/bonus separation"},
        {"table_id": "T10", "path": "tables/historical_evidence.csv", "purpose": "Historical census and evidence tiers"},
        {"table_id": "T11", "path": "tables/terra_limitations.csv", "purpose": "Terra negative findings"},
        {"table_id": "T12", "path": "tables/old_to_new.csv", "purpose": "Superseded result mapping"},
    ]

    _write_csv(root / "tables" / "version_precedence.csv", precedence["versions"])
    core_ids = ["AAVE_SNAPSHOT_BLOCK", "AAVE_VERIFIED_BORROWERS", "AAVE_WETH_USDC_COHORT", "AAVE_HF_MAX_ABS_ERROR", "AAVE_HF_MAX_REL_ERROR"]
    _write_csv(root / "tables" / "core_facts.csv", [{"result_id": rid, "value": _metric_value(results, rid), "unit": next(r["unit"] for r in results if r["result_id"] == rid)} for rid in core_ids])
    _write_csv(root / "tables" / "rq1_deterministic_depth.csv", [{"grid": 32, "depth": d, "count": depth32.get(d, 0), "source_version": "P0 corrected v2"} for d in range(3)] + [{"grid": 60, "depth": d, "count": depth60.get(d, 0), "source_version": "Level-3"} for d in range(3)])
    _write_csv(root / "tables" / "rq1_monte_carlo.csv", [{key: row[key] for key in ["actual_runs", "depth_ge_2_successes", "depth_ge_2_frequency", "depth_ge_2_wilson_lower", "depth_ge_2_wilson_upper", "depth_ge_3_successes", "label", "max_observed_cascade_depth", "seed"]} for row in mc_rows])
    _write_csv(root / "tables" / "rq2_liquidity.csv", [{"liquidity_haircut_pct": h, "depth2_cells": sum(int(row["cascade_depth"]) == 2 and float(row["liquidity_haircut_pct"]) == h for row in grid60), "assumption_status": "OBSERVED_BASELINE" if h <= 75 else "UNOBSERVED_COUNTERFACTUAL_TAIL"} for h in [0, 25, 50, 75, 90, 95]])
    _write_csv(root / "tables" / "rq3_constraints.csv", [{"experiment": "capital", "level": row["capital_ratio"], "status": row["constraint_status"], "total_liquidated_debt_usdc": row["total_liquidated_debt"], "processing_delay_seconds": 0} for row in capital_rows] + [{"experiment": "delay", "level": row["delay_steps"], "status": "NOT_BINDING_IN_TESTED_RANGE", "total_liquidated_debt_usdc": row["total_liquidated_debt"], "processing_delay_seconds": row["delay_seconds"]} for row in delay_rows])
    _write_csv(root / "tables" / "rq4_arbitrage.csv", [{"arbitrage_capacity_pct": row["capacity"], "immediate_price_impact_ratio": row["impact"], "post_arbitrage_spread_ratio": row["spread"]} for row in arb_rows])
    _write_csv(root / "tables" / "rq5_usdc_valuation.csv", [{"usdc_price_usd": price, "borrowers_hf_below_1": row["borrowers_hf_below_1_00"], "liquidated_debt_usdc_token": row["total_liquidated_debt_usdc"], "liquidated_debt_usd_equivalent": row["total_liquidated_debt_usd"]} for price, row in sorted(usdc_by_price.items())])
    _write_csv(root / "tables" / "rq6_policy.csv", [{"parameter": "LTV", "value": value, "outcome": row["aggregate_max_borrowing_capacity_usd"], "outcome_unit": "USD max borrowing capacity"} for value, row in sorted(ltv_by_value.items())] + [{"parameter": "LT", "value": value, "outcome": row["unliquidated_debt"], "outcome_unit": "USDC token quantity, scenario-LT"} for value, row in sorted(lt_by_value.items())] + [{"parameter": "bonus", "value": value - 1, "outcome": row["collateral_seized_weth"], "outcome_unit": "WETH seized"} for value, row in sorted(bonus_by_value.items())])
    _write_csv(root / "tables" / "historical_evidence.csv", [{"metric": "RPC census", "count": 28, "interpretation": "complete checked Pool-log set for preregistered week"}, {"metric": "Graph matched", "count": 27, "interpretation": "candidate-discovery recall within checked week"}, *[{"metric": key, "count": value, "interpretation": "association tier; not causal proof"} for key, value in linkage["tier_counts"].items()]])
    _write_csv(root / "tables" / "terra_limitations.csv", [{"finding": "pre_initial_depeg_high_alert_hours", "value": 0, "unit": "hours", "interpretation": "negative early-warning finding"}, {"finding": "initial_depeg_high_lead", "value": -45, "unit": "hours", "interpretation": "warning after initial depeg"}, {"finding": "out_of_sample_forecast_supported", "value": False, "unit": "boolean", "interpretation": "event-informed design; no held-out training protocol"}])
    _write_csv(root / "tables" / "old_to_new.csv", superseded["items"])

    _write_json(root / "results_registry.json", {"schema_version": "frozen-v3.0", "results": results})
    _write_json(root / "claim_ledger.json", {"claims": claims})
    _write_json(root / "rq_answer_matrix.json", {"research_questions": rq_details})
    _write_json(root / "evidence_source_matrix.json", {"sources": evidence, "table_registry": table_registry, "figure_registry": figures})
    _write_json(root / "version_precedence.json", precedence)
    _write_json(root / "superseded_results.json", superseded)
    _write_json(root / "figures" / "figure_registry.json", {"figures": figures})

    table_ids = {item["table_id"] for item in table_registry}
    figure_ids = {item["figure_id"] for item in figures}
    checks = {
        "canonical_snapshot_hash_locked": canonical_hash == EXPECTED_CANONICAL_SHA,
        "original_32_cell_grid_preserved": len(grid32) == 32 and depth32 == Counter({1: 20, 0: 12}),
        "extended_60_cell_grid_verified": len(grid60) == 60 and depth60 == Counter({1: 38, 0: 18, 2: 4}),
        "severe_10k_checkpoint_verified_without_rerun": int(severe10k["actual_runs"]) == 10_000 and int(severe10k["depth_ge_2_successes"]) == 280 and checkpoints["accounting_correction"]["large_paths_executed_in_this_repair_invocation"] == 0,
        "historical_28_vs_27_reconciled": census["rpc_census_count"] == 28 and census["matched_count"] == 27 and len(census["rpc_only"]) == 1,
        "historical_tiers_repaired": linkage["tier_counts"] == {"DIRECT_TRANSFER_PATH_VERIFIED": 1, "SAME_TRANSACTION_CO_OCCURRENCE": 2, "SAME_BLOCK_ASSOCIATION": 23, "TIME_WINDOW_ASSOCIATION": 1},
        "unique_result_ids": len(result_ids) == len(results),
        "all_claim_result_ids_resolve": all(set(claim["result_ids"]) <= result_ids for claim in claims),
        "all_claim_evidence_ids_resolve": all(set(claim["evidence_ids"]) <= evidence_ids for claim in claims),
        "all_claim_table_ids_resolve": all(set(claim["table_ids"]) <= table_ids for claim in claims),
        "all_claim_figure_ids_resolve": all(set(claim["figure_ids"]) <= figure_ids for claim in claims),
        "all_values_finite": _finite(results),
        "terra_negative_findings_retained": _metric_value(results, "TERRA_PRE_DEPEG_HIGH_ALERT_HOURS") == 0 and _metric_value(results, "TERRA_INITIAL_DEPEG_HIGH_LEAD") == -45.0,
        "no_large_research_rerun": True,
        "literature_files_reserved_for_p2": all(Path(path).as_posix() not in {item["source_path"] for item in results} for path in LITERATURE_FILES_RESERVED),
    }
    if not all(checks.values()):
        raise ValueError(f"Frozen v3 quality gate failed: {[key for key, value in checks.items() if not value]}")

    validation = {
        "status": FREEZE_STATUS,
        "checks": checks,
        "counts": {"results": len(results), "claims": len(claims), "research_questions": len(rq_details), "tables": len(table_registry), "figures": len(figures)},
        "large_research_rerun": False,
        "p2_citation_reconciliation": "PENDING_COMMANDER_APPROVAL_AND_MERGE_OF_PR_9_MINIMAL_DELTA",
        "scientific_content_lock_declared": False,
    }
    _write_json(root / "validation_summary.json", validation)

    rq_md = ["# Ma trận trả lời sáu câu hỏi nghiên cứu — Frozen v3", "", f"Trạng thái: **{FREEZE_STATUS}**", "", "Nguồn định lượng ưu tiên: Original → P0 corrected v2 → Level-3 → Level-3 targeted repair → Frozen v3.", ""]
    for item in rq_details:
        rq_md.extend([f"## {item['rq']} — {item['question_vi']}", "", f"**Phương pháp.** {item['method_vi']}", "", f"**Dữ liệu.** {item['data_vi']}", "", f"**Thí nghiệm.** {item['experiment_vi']}", "", f"**Kết quả.** {item['result_vi']}", "", f"**Giải thích.** {item['interpretation_vi']}", "", f"**Giới hạn.** {item['limitation_vi']}", "", f"**Kết luận.** {item['conclusion_vi']}", "", f"**Trạng thái:** `{item['status']}`; claim ID: `{item['claim_ids'][0]}`.", ""])
    rq_md.extend(["## Phần mở rộng không thay thế sáu RQ", "", "Terra 2022 là kiểm chứng lịch sử mở rộng và giữ kết quả âm về early warning. Mạng lưới nhiều lớp là phân tích truyền dẫn mở rộng; centrality trong sub-network không đại diện tầm quan trọng toàn DeFi.", ""])
    (DOC_ROOT / "RQ_ANSWER_MATRIX.md").write_text("\n".join(rq_md), encoding="utf-8")

    freeze_report = f"""# Báo cáo khóa bằng chứng định lượng Frozen v3

Trạng thái: **{FREEZE_STATUS}**

Starting HEAD: `{starting_head}`  
Implementation commit: `{implementation_commit}`  
Artifact bundle commit: xem `manifest.json` (được điền trong bước đóng gói provenance).

## Quy tắc nguồn chuẩn

`Original → P0 corrected v2 → Level-3 → Level-3 targeted repair → Frozen v3`.

Frozen v3 là lớp registry/synthesis; không retune mô hình và không ghi đè artifact cũ. Canonical snapshot block 26.045.352 giữ SHA-256 `{canonical_hash}`.

## Sự thật đã khóa

- 454 borrower được RPC xác minh; cohort WETH collateral-enabled + USDC debt có 109 vị thế. Tỷ lệ xác minh ứng viên không phải market coverage.
- Lưới cũ 32 ô: depth 0/1/2 = 12/20/0. Lưới mở rộng 60 ô: 18/38/4.
- Severe Monte Carlo: 280/10.000 đường depth ≥2 (2,8%); 0 depth ≥3. 100 wave là cap, không phải độ sâu đạt được.
- Cửa sổ 01–07/09/2026: 28 `LiquidationCall` trong RPC census; 27 Graph-matched; một RPC-only event.
- Trong 27 Graph-matched: 1 direct transfer path, 2 same-transaction co-occurrences, 23 same-block, 1 time-window. Không suy diễn causal chain.
- P0 tách immediate price impact khỏi post-arbitrage spread, processing delay khỏi recovery, và scenario-LT unliquidated debt khỏi legacy recorded-LT comparison.

## Ngữ nghĩa metric bắt buộc

`bad_debt` là model-based uncovered debt estimate, không mặc định là realized financial loss. `unliquidated_debt` là nợ đủ điều kiện nhưng chưa được thực thi trong điều kiện kịch bản. `liquidation_at_risk` là exposure đủ điều kiện trước giới hạn execution. `cascade_depth` đếm positive liquidation waves. `cascade_amplification` so tổng nợ thanh lý với direct-shock liquidation. `time_to_recovery_seconds` chỉ có nghĩa khi residual spread thực sự vượt tolerance. Monte Carlo tail quantity là composite modeled quantity, không gọi là realized loss hay market expected shortfall.

## Terra và phần mở rộng mạng

Terra cutoff-safe có 0 HIGH alert trong 1.630 giờ trước initial depeg; HIGH threshold đến muộn 45 giờ so với UST<0,995. Không có claim out-of-sample forecasting. Không có dữ liệu DEX liquidity hoặc LFG intervention quan sát đầy đủ. Network analysis chỉ là sub-network Aave–Uniswap/structural extension.

## Citation P2

Năm file literature của PR #9 không được sửa trong P1 này. Citation cuối chỉ được hòa giải sau khi Commander duyệt minimal delta của P2. Vì vậy không tuyên bố `SCIENTIFIC_CONTENT_LOCK`.
"""
    (DOC_ROOT / "EVIDENCE_FREEZE_REPORT.md").write_text(freeze_report, encoding="utf-8")

    packet = f"""# P1 Commander Review Packet — Frozen v3

Trạng thái đề nghị kiểm duyệt: **{FREEZE_STATUS}**. Chỉ Commander quyết định P1 PASS/REWORK.

## Phạm vi thực thi

- Starting HEAD: `{starting_head}`.
- Không chạy lại 10.000 Monte Carlo; xác minh manifest/checkpoint và 13.000 identity độc lập.
- Không sửa canonical snapshot, corrected_run_v2, level3_extension, level3_p1_targeted_repair hoặc Terra locked package.
- Không sửa năm file literature/citation do PR #9 quản lý.
- Không tạo Word final và không đóng Issue #3.

## Ưu tiên phiên bản

| Rank | Version | Vai trò |
|---:|---|---|
| 1 | Original | raw/canonical evidence |
| 2 | P0 corrected v2 | numerical semantics và RQ sweeps |
| 3 | Level-3 | 60-cell, checkpoint, historical extension |
| 4 | Level-3 targeted repair | census/tier/checkpoint audit |
| 5 | Frozen v3 | registry/synthesis duy nhất |

## Sáu RQ

| RQ | Trạng thái | Kết luận ngắn |
|---|---|---|
| RQ1 | LIMITED | Depth 2 xuất hiện ở 4/60 cell và 280/10.000 Severe paths; không depth ≥3. |
| RQ2 | LIMITED | Liquidity absorption yếu hơn gắn với tail depth 2; 90/95% là giả định chưa quan sát. |
| RQ3 | LIMITED | Vốn thấp binding; capacity/gas/delay không binding trong range đã thử. |
| RQ4 | LIMITED | Arbitrage giảm residual spread, không xóa immediate sale impact. |
| RQ5 | LIMITED | Chỉ hỗ trợ debt-valuation channel; token quantity tách USD-equivalent. |
| RQ6 | LIMITED | LTV, LT và bonus có vai trò khác nhau, không được nhập nhằng. |

## Điều kiện còn chờ

1. Commander review Frozen v3 và quyết định P1 PASS/REWORK.
2. PR #9 cập nhật minimal delta cho census 28, tier 1/2/23/1, controls/checkpoints/HF; Commander duyệt và merge.
3. Sau đó mới reconciliation citation cuối và cân nhắc `SCIENTIFIC_CONTENT_LOCK`.
"""
    (DOC_ROOT / "P1_COMMANDER_REVIEW_PACKET.md").write_text(packet, encoding="utf-8")

    report_paths = [DOC_ROOT / "EVIDENCE_FREEZE_REPORT.md", DOC_ROOT / "RQ_ANSWER_MATRIX.md", DOC_ROOT / "P1_COMMANDER_REVIEW_PACKET.md"]
    frozen_text = "\n".join(path.read_text(encoding="utf-8") for path in [*root.rglob("*.json"), *root.rglob("*.csv"), *report_paths])
    if re.search(r"0x[a-fA-F0-9]{40}\b", frozen_text):
        raise ValueError("Raw wallet/contract address found in frozen package")
    if re.search(r"(?i)(api[_-]?key|authorization)\s*[:=]\s*['\"]?[A-Za-z0-9_-]{12,}", frozen_text):
        raise ValueError("Potential secret found in frozen package")

    artifact_hashes = {
        path.relative_to(root).as_posix(): _sha(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.name != "manifest.json"
    }
    manifest = {
        "schema_version": "frozen-v3.0",
        "status": FREEZE_STATUS,
        "starting_head": starting_head,
        "source_code_commit": implementation_commit,
        "artifact_bundle_commit": artifact_bundle_commit,
        "scientific_content_lock_declared": False,
        "large_research_rerun": False,
        "canonical_snapshot": {"block_number": 26_045_352, "sha256": canonical_hash, "verified_borrowers": 454, "weth_usdc_cohort": 109},
        "input_hashes": {item["evidence_id"]: item["sha256"] for item in evidence},
        "artifact_hashes": artifact_hashes,
        "report_hashes": {path.as_posix(): _sha(path) for path in report_paths},
        "reserved_p2_files_untouched": LITERATURE_FILES_RESERVED,
        "quality_gate": checks,
        "counts": validation["counts"],
    }
    _write_json(root / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--starting-head", required=True)
    parser.add_argument("--implementation-commit", required=True)
    parser.add_argument("--artifact-bundle-commit", required=True)
    args = parser.parse_args()
    manifest = build(
        args.root,
        starting_head=args.starting_head,
        implementation_commit=args.implementation_commit,
        artifact_bundle_commit=args.artifact_bundle_commit,
    )
    print(json.dumps({"status": manifest["status"], "counts": manifest["counts"], "quality_gate": manifest["quality_gate"]}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
