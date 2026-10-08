import type { SnapshotSummary } from "./api";

export type SnapshotSelectionDecision = {
  snapshot: SnapshotSummary | null;
  staleSavedId: boolean;
  shouldCreateFixture: boolean;
  requiresMainnetChoice: boolean;
  reason: "SAVED" | "LATEST_REAL" | "LATEST_CACHED" | "FIXTURE_FALLBACK" | "MAINNET_READY" | "NO_SOURCE";
};

type SelectionStorage = Pick<Storage, "setItem">;

export function persistSnapshotSelection(storage: SelectionStorage, snapshotId: string): void {
  storage.setItem("defi-snapshot-id", snapshotId);
}

export function shouldShowFixtureBanner(mode: SnapshotSummary["mode"] | null): boolean {
  return mode === "FIXTURE";
}

export function shouldShowMainnetBanner(mode: SnapshotSummary["mode"] | null): boolean {
  return mode === "REAL_MAINNET" || mode === "CACHED_MAINNET";
}

function newest(snapshots: SnapshotSummary[], mode: SnapshotSummary["mode"]): SnapshotSummary | null {
  return (
    snapshots
      .filter((snapshot) => snapshot.mode === mode)
      .sort((left, right) => {
        const byBlock = right.block_number - left.block_number;
        if (byBlock !== 0) return byBlock;
        const byRetrievedAt = Date.parse(right.retrieved_at) - Date.parse(left.retrieved_at);
        return byRetrievedAt || right.id.localeCompare(left.id);
      })[0] ?? null
  );
}

export function resolveSnapshotSelection(
  snapshots: SnapshotSummary[],
  savedId: string | null,
  canCreateRealSnapshot: boolean,
): SnapshotSelectionDecision {
  const saved = savedId ? snapshots.find((snapshot) => snapshot.id === savedId) ?? null : null;
  if (saved) {
    return {
      snapshot: saved,
      staleSavedId: false,
      shouldCreateFixture: false,
      requiresMainnetChoice: false,
      reason: "SAVED",
    };
  }
  const staleSavedId = Boolean(savedId);
  const real = newest(snapshots, "REAL_MAINNET");
  if (real) {
    return {
      snapshot: real,
      staleSavedId,
      shouldCreateFixture: false,
      requiresMainnetChoice: false,
      reason: "LATEST_REAL",
    };
  }
  const cached = newest(snapshots, "CACHED_MAINNET");
  if (cached) {
    return {
      snapshot: cached,
      staleSavedId,
      shouldCreateFixture: false,
      requiresMainnetChoice: false,
      reason: "LATEST_CACHED",
    };
  }
  if (canCreateRealSnapshot) {
    return {
      snapshot: null,
      staleSavedId,
      shouldCreateFixture: false,
      requiresMainnetChoice: true,
      reason: "MAINNET_READY",
    };
  }
  const fixture = newest(snapshots, "FIXTURE");
  return {
    snapshot: fixture,
    staleSavedId,
    shouldCreateFixture: fixture === null,
    requiresMainnetChoice: false,
    reason: fixture ? "FIXTURE_FALLBACK" : "NO_SOURCE",
  };
}
