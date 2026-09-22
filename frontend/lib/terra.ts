import type { TerraManifest } from "./api";

export function terraStatusLabel(status: TerraManifest["status"]): string {
  return ({
    REAL_HISTORICAL: "REAL HISTORICAL DATA",
    FIXTURE: "FIXTURE",
    PARTIAL: "PARTIAL DATA",
    UNAVAILABLE: "UNAVAILABLE",
    QUALITY_WARNING: "QUALITY WARNING",
  } as const)[status];
}

export function isHistoricalEvidence(status: TerraManifest["status"]): boolean {
  return status === "REAL_HISTORICAL";
}
