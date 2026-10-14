# Level-2 Local Mainnet-Fork Validation

Trạng thái: **UNAVAILABLE**

Archive RPC đã được cấu hình và historical read-only evidence chạy được. Tuy nhiên máy thực thi không có `forge`, `anvil` hoặc `cast`. Vì vậy:

- số local-fork transaction thực thi: **0**;
- Aave `liquidationCall` trên fork: **không chạy**;
- SwapRouter02 execution trên fork: **không chạy**;
- không có contract trace/gas/repay/seize output để gắn nhãn PASS.

Harness hiện hữu `contracts/validation/test/ForkValidation.t.sol` có SHA-256 `4f79818ad9fd891abb73e00d3eacafc2784adc49f36e660b4eceacd6e6cc44c4` và chỉ nhắm local ephemeral fork. Không có Mainnet transaction, private key hay funding thật được dùng.

Baseline QuoterV2 `eth_call` từ P0 vẫn chỉ xác minh canonical initial state. Nó không phải counterfactual post-shock transaction execution và không thay thế Gate Level-2.

Điều kiện còn thiếu để chạy:

1. Foundry `forge` và `anvil` đáng tin cậy;
2. historical liquidatable borrower/funded holder phù hợp tại exact block;
3. local-only fork command với archive RPC;
4. capture trace, debt repaid, collateral seized, ticks/liquidity, gas và sai số so model.

Evidence: `data/processed/research_final/level3_extension/fork/validation.json`.
