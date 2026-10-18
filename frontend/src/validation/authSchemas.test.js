import { describe, expect, it } from "vitest";
import { loginSchema, registerSchema } from "./authSchemas";

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

const checkRegister = (overrides) =>
  registerSchema.safeParse({
    email: "jan@example.com",
    password: "Haslo1234",
    confirmPassword: "Haslo1234",
    ...overrides,
  });

describe("registerSchema", () => {
  it("akceptuje poprawne dane", () => {
    expect(checkRegister({}).success).toBe(true);
  });

  it("wymaga poprawnego adresu e-mail", () => {
    expect(checkRegister({ email: "" }).success).toBe(false);
    expect(checkRegister({ email: "jan@example" }).success).toBe(false);
  });

  it("wymaga hasła z minimum 8 znaków, literą i cyfrą", () => {
    const weak = ["Kr0tkie", "tylkolitery", "12345678", ""];
    weak.forEach((password) => {
      expect(checkRegister({ password, confirmPassword: password }).success, password).toBe(false);
    });
    expect(checkRegister({ password: "Zażółć123", confirmPassword: "Zażółć123" }).success).toBe(true);
  });

  it("odrzuca zbyt długie hasło", () => {
    const long = "a1".repeat(65);
    expect(checkRegister({ password: long, confirmPassword: long }).success).toBe(false);
  });

  it("wymaga zgodności haseł i wskazuje pole potwierdzenia", () => {
    const result = checkRegister({ confirmPassword: "Inne12345" });
    expect(result.success).toBe(false);
    expect(result.error.issues[0].path).toEqual(["confirmPassword"]);
  });
});
