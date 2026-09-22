import { describe, expect, it } from "vitest";

import { isHistoricalEvidence, terraStatusLabel } from "./terra";

describe("Terra scientific data labels", () => {
  it("never formats a fixture as historical evidence", () => {
    expect(terraStatusLabel("FIXTURE")).toBe("FIXTURE");
    expect(isHistoricalEvidence("FIXTURE")).toBe(false);
  });

  it("uses explicit labels for partial and unavailable data", () => {
    expect(terraStatusLabel("PARTIAL")).toBe("PARTIAL DATA");
    expect(terraStatusLabel("UNAVAILABLE")).toBe("UNAVAILABLE");
  });
});
