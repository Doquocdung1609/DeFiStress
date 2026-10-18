# V1 Release Blockers — Current G1 Evidence

**Target:** `V1_RELEASE_G1_FINAL_EVIDENCE_READY_FOR_COMMANDER_REVIEW`.

Current disposition: {'REL-01': 'PASS_FULL_SUITE_NO_DESELECTION', 'REL-02': 'PASS_NEW_WINDOWS_TARGET', 'REL-03': 'RESOLVED_HISTORICAL_GENERATOR_IDENTIFIED', 'REL-04': 'PASS_COMPLETE_BYTES_SCOPED'}. Reviewed [run39125232234](https://github.com/Doquocdung1609/DeFiStress/actions/runs/39125232234), head `aaa010889e857c7042c3a209c88b8e8de1c8d6cc`.

Full evidence, exact hashes, counts, scope and remaining limitations: [G1 final report](g1/G1_FINAL_EVIDENCE_REPORT.md), [machine result](g1/G1_FINAL_RESULT.json). This supersedes the earlier scheduling-only checkpoint; that checkpoint remains in Git history.

Changes are limited to CI scheduling/target environment/checkout-byte provisioning, exact historical DOCX fixtures, release tools and evidence. All226 pytest tests are retained. No assertion/deselection/engine/scientific-artifact edit is used to create green CI. PR19 is not merged automatically; PR26 is the current scoped proposal.

No tag, release, merge, Scientific Content Lock change or Phase01 implementation. Native Windows environment testing does not certify Docker deployment, and full-byte checks do not establish a new independent scientific replay.
