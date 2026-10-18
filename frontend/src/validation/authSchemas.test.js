import { describe, expect, it } from "vitest";
import { loginSchema } from "./authSchemas";

const check = (overrides) => loginSchema.safeParse({ email: "jan@example.com", password: "Haslo1234", ...overrides });

describe("loginSchema", () => {
  it("akceptuje poprawne dane", () => {
    expect(check({}).success).toBe(true);
  });

  it("wymaga adresu e-mail w poprawnym formacie", () => {
    expect(check({ email: "" }).success).toBe(false);
    expect(check({ email: "jan" }).success).toBe(false);
    expect(check({ email: "jan@" }).success).toBe(false);
    expect(check({ email: "jan@example" }).success).toBe(false);
    expect(check({ email: "ja n@example.com" }).success).toBe(false);
  });

  it("usuwa spacje wokół adresu e-mail", () => {
    const result = check({ email: "  jan@example.com " });
    expect(result.success).toBe(true);
    expect(result.data.email).toBe("jan@example.com");
  });

  it("wymaga hasła", () => {
    expect(check({ password: "" }).success).toBe(false);
  });
});
