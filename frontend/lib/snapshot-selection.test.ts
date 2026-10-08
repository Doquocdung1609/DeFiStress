import { describe, expect, it } from "vitest";

import type { SnapshotSummary } from "./api";
import {
  persistSnapshotSelection,
  resolveSnapshotSelection,
  shouldShowFixtureBanner,
  shouldShowMainnetBanner,
} from "./snapshot-selection";

function summary(
  id: string,
  mode: SnapshotSummary["mode"],
  blockNumber: number,
  retrievedAt = "2026-09-24T00:00:00Z",
): SnapshotSummary {
  return {
    id,
    mode,
    label: mode,
    chain_id: 1,
    block_number: blockNumber,
    block_hash: "0".repeat(64),
    block_timestamp: "2026-09-24T00:00:00Z",
    retrieved_at: retrievedAt,
    coverage: {},
    selected_uniswap_pool: {},
    quality_flag_count: 0,
  };
}

describe("snapshot selection", () => {
  const fixture = summary("fixture-main-v1", "FIXTURE", 22_000_000);
  const olderReal = summary("real-old", "REAL_MAINNET", 26_045_000);
  const latestReal = summary("real-new", "REAL_MAINNET", 26_045_352);
  const cached = summary("cached-real", "CACHED_MAINNET", 26_045_300);

  it("selects the newest REAL_MAINNET when no selection is saved", () => {
    expect(resolveSnapshotSelection([fixture, olderReal, latestReal], null, true).snapshot?.id).toBe("real-new");
  });

  it("respects a valid saved REAL_MAINNET even when a newer snapshot exists", () => {
    expect(resolveSnapshotSelection([latestReal, olderReal], "real-old", true).snapshot?.id).toBe("real-old");
  });

  it("respects a deliberately saved Fixture selection", () => {
    expect(resolveSnapshotSelection([fixture, latestReal], fixture.id, true).snapshot?.mode).toBe("FIXTURE");
  });

  it("clears the stale-selection path by choosing the newest Mainnet snapshot", () => {
    const decision = resolveSnapshotSelection([olderReal, latestReal], "missing-real", true);
    expect(decision.snapshot?.id).toBe("real-new");
    expect(decision.staleSavedId).toBe(true);
  });

  it("waits for an explicit action when Mainnet is ready but no Mainnet snapshot exists", () => {
    const decision = resolveSnapshotSelection([fixture], "missing-real", true);
    expect(decision.snapshot).toBeNull();
    expect(decision.requiresMainnetChoice).toBe(true);
    expect(decision.shouldCreateFixture).toBe(false);
  });

  it("uses Fixture only when no Mainnet source can be created", () => {
    expect(resolveSnapshotSelection([fixture], null, false).snapshot?.mode).toBe("FIXTURE");
    expect(resolveSnapshotSelection([], null, false).shouldCreateFixture).toBe(true);
  });

  it("keeps a stored REAL_MAINNET selection when live health later goes offline", () => {
    const decision = resolveSnapshotSelection([latestReal, fixture], latestReal.id, false);
    expect(decision.snapshot?.mode).toBe("REAL_MAINNET");
  });

  it("uses retrieved_at as the deterministic tie-breaker", () => {
    const first = summary("real-first", "REAL_MAINNET", 100, "2026-09-24T00:00:00Z");
    const second = summary("real-second", "REAL_MAINNET", 100, "2026-09-25T00:00:00Z");
    expect(resolveSnapshotSelection([first, cached, second], null, true).snapshot?.id).toBe("real-second");
  });

  it("shows the Fixture warning only for Fixture", () => {
    expect(shouldShowFixtureBanner("FIXTURE")).toBe(true);
    expect(shouldShowFixtureBanner("REAL_MAINNET")).toBe(false);
    expect(shouldShowFixtureBanner("CACHED_MAINNET")).toBe(false);
  });

  it("shows Mainnet evidence for real and cached Mainnet snapshots", () => {
    expect(shouldShowMainnetBanner("REAL_MAINNET")).toBe(true);
    expect(shouldShowMainnetBanner("CACHED_MAINNET")).toBe(true);
    expect(shouldShowMainnetBanner("FIXTURE")).toBe(false);
  });

  it("persists the user's selected snapshot ID", () => {
    const writes: Array<[string, string]> = [];
    persistSnapshotSelection({ setItem: (key, value) => writes.push([key, value]) }, "real-new");
    expect(writes).toEqual([["defi-snapshot-id", "real-new"]]);
  });
});
