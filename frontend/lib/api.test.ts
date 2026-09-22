import { describe, expect, it } from "vitest";
import { money, percent } from "./api";

describe("formatters", () => {
  it("formats finite metrics", () => {
    expect(money(1200)).toContain("1,200");
    expect(percent(0.125)).toBe("12.50%");
  });

  it("does not render NaN", () => {
    expect(money(Number.NaN)).toBe("—");
    expect(percent(null)).toBe("—");
  });
});

