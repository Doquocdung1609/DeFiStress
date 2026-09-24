import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const dashboard = readFileSync(new URL("../app/components/terra/TerraDashboard.tsx", import.meta.url), "utf8");

describe("Terra presentation dashboard", () => {
  it("renders the three primary research layers in plain English", () => {
    expect(dashboard).toContain("Historical Fit");
    expect(dashboard).toContain("Early Warning");
    expect(dashboard).toContain("Stress Test");
    expect(dashboard).toContain("What actually happened?");
    expect(dashboard).toContain("not a probability estimate");
  });

  it("keeps fixture cohorts out of the historical evidence page", () => {
    const historicalStart = dashboard.indexOf("function DemoHistoricalData");
    const historicalEnd = dashboard.indexOf("function HistoricalFitScreen");
    const historicalPage = dashboard.slice(historicalStart, historicalEnd);
    expect(historicalPage).not.toContain("Fixture cohort");
    expect(historicalPage).toContain("MISSING EARLIER");
  });
});
