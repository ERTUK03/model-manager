import { describe, expect, it } from "vitest";
import { shortVersion } from "./format";

describe("shortVersion", () => {
  it("skraca pełny skrót commita do 7 znaków", () => {
    expect(shortVersion("0123456789abcdef0123456789abcdef01234567")).toBe("0123456");
  });

  it("zostawia inne wartości bez zmian", () => {
    expect(shortVersion("dev")).toBe("dev");
    expect(shortVersion("abc1234")).toBe("abc1234");
    expect(shortVersion("v1.2.3")).toBe("v1.2.3");
  });
});
