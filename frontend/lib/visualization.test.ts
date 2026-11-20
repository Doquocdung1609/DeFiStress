import { describe, expect, it } from "vitest";

import {
  exitFillPercent,
  formatFinancial,
  formatHealthFactor,
  healthFactorStatus,
  parseFiniteAmount,
  warningStatus,
} from "./visualization";

describe("Health Factor display", () => {
  it("preserves the under-one liquidation boundary while formatting", () => {
    expect(formatHealthFactor(0.9999)).toBe("0.999");
    expect(formatHealthFactor(1)).toBe("1.000");
    expect(formatHealthFactor(1.23456)).toBe("1.235");
  });

  it("keeps missing and invalid factors unknown", () => {
    expect(formatHealthFactor(null)).toBe("—");
    expect(formatHealthFactor(Number.NaN)).toBe("—");
    expect(healthFactorStatus(undefined)).toBe("unknown");
  });

  it("uses the stated boundary and existing illustrative low-buffer threshold", () => {
    expect(healthFactorStatus(0.9)).toBe("liquidation-threshold");
    expect(healthFactorStatus(1)).toBe("liquidation-threshold");
    expect(healthFactorStatus(1.1)).toBe("low-buffer");
    expect(healthFactorStatus(1.2)).toBe("relative-buffer");
  });
});

describe("warning presentation", () => {
  it.each(["NORMAL", "WATCH", "HIGH", "ABSTAIN"] as const)("shows the %s label and description", (level) => {
    const result = warningStatus(level);
    expect(result.label).toBe(level);
    expect(result.description.length).toBeGreaterThan(0);
  });

  it("does not turn unrecognized or absent values into NORMAL", () => {
    expect(warningStatus("UNSEEN").label).toBe("UNSEEN");
    expect(warningStatus("").label).toBe("UNKNOWN");
  });
});

describe("financial display helpers", () => {
  it("retains cents, small values, negatives and missing values", () => {
    expect(formatFinancial("465.6")).toContain("465.60");
    expect(formatFinancial("0.000001")).toContain("0.000001");
    expect(formatFinancial("-134.4")).toContain("134.40");
    expect(formatFinancial(null)).toBe("—");
    expect(formatFinancial("not-a-number")).toBe("—");
  });

  it("shows partial fills and treats missing or zero totals as not verifiable", () => {
    expect(exitFillPercent("600", "400")).toBe(60);
    expect(exitFillPercent("1000", "0")).toBe(100);
    expect(exitFillPercent("0", "1000")).toBe(0);
    expect(exitFillPercent(null, "1000")).toBeNull();
    expect(exitFillPercent(" ", "1000")).toBeNull();
    expect(exitFillPercent("0", "0")).toBeNull();
    expect(parseFiniteAmount("-1")).toBeNull();
  });
});
