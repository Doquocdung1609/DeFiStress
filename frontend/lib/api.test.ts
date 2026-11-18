import { describe, expect, it } from "vitest";
import { apiErrorMessage, money, percent } from "./api";

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

describe("API validation errors", () => {
  it("names the invalid field and explains the problem", () => {
    expect(apiErrorMessage({ detail: [{ loc: ["body", "ust_price"], msg: "Value error, price must be positive" }] }, 422))
      .toContain("ust_price: Value error, price must be positive");
  });
});

