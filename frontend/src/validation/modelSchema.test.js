import { describe, expect, it } from "vitest";
import { toPayload } from "../utils/mappers";
import { modelSchema } from "./modelSchema";

const valid = {
  name: "iris-classifier",
  description: "",
  framework: "ONNX",
  task: "Klasyfikacja",
  version: "1.0.0",
  accuracy: "0.95",
  size_mb: "1,5",
  status: "draft",
};

const check = (overrides) => modelSchema.safeParse({ ...valid, ...overrides });

describe("modelSchema", () => {
  it("akceptuje poprawne dane (także przecinek jako separator)", () => {
    expect(check({}).success).toBe(true);
  });

  it("pozwala zostawić dokładność i rozmiar puste", () => {
    expect(check({ accuracy: "", size_mb: "" }).success).toBe(true);
  });

  it("wymaga nazwy i zadania", () => {
    expect(check({ name: "" }).success).toBe(false);
    expect(check({ name: " a " }).success).toBe(false);
    expect(check({ task: "" }).success).toBe(false);
  });

  it("odrzuca zbyt długie teksty", () => {
    expect(check({ name: "a".repeat(101) }).success).toBe(false);
    expect(check({ description: "a".repeat(501) }).success).toBe(false);
  });

  it("wymaga wersji w formacie X.Y.Z", () => {
    expect(check({ version: "" }).success).toBe(false);
    expect(check({ version: "1.0" }).success).toBe(false);
    expect(check({ version: "v1.0.0" }).success).toBe(false);
  });

  it("sprawdza zakres dokładności i format liczb", () => {
    expect(check({ accuracy: "1.5" }).success).toBe(false);
    expect(check({ accuracy: "abc" }).success).toBe(false);
    expect(check({ accuracy: "-0.1" }).success).toBe(false);
    expect(check({ accuracy: "1" }).success).toBe(true);
    expect(check({ size_mb: "-3" }).success).toBe(false);
    expect(check({ size_mb: "0x10" }).success).toBe(false);
  });

  it("wymaga wyboru frameworka i statusu z listy", () => {
    expect(check({ framework: "" }).success).toBe(false);
    expect(check({ framework: "Nieznany" }).success).toBe(false);
    expect(check({ status: "inny" }).success).toBe(false);
  });
});

describe("toPayload", () => {
  it("zamienia pola na typy zgodne z API", () => {
    const payload = toPayload({ ...valid, description: "  ", accuracy: "0,95", size_mb: "" });
    expect(payload.description).toBeNull();
    expect(payload.accuracy).toBe(0.95);
    expect(payload.size_mb).toBeNull();
  });
});
