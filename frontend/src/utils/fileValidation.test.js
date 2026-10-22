import { describe, expect, it } from "vitest";
import { formatBytes } from "./format";
import { validateModelFile } from "./fileValidation";

const file = (name, size = 10) => ({ name, size });

describe("validateModelFile", () => {
  it("akceptuje dozwolone rozszerzenia, niezależnie od wielkości liter", () => {
    ["model.pkl", "model.joblib", "MODEL.ONNX", "a.b.pt", "net.pth", "net.h5", "w.safetensors"].forEach((name) => {
      expect(validateModelFile(file(name)), name).toBeNull();
    });
  });

  it("odrzuca niedozwolone typy i nazwy bez rozszerzenia", () => {
    ["virus.exe", "skrypt.py", "archiwum.pkl.zip", "bez-rozszerzenia", ".pkl", ""].forEach((name) => {
      expect(validateModelFile(file(name)), name).toMatch(/Niedozwolony typ pliku/);
    });
  });

  it("odrzuca pusty plik", () => {
    expect(validateModelFile(file("model.pkl", 0))).toBe("Plik jest pusty");
  });

  it("odrzuca zbyt duży plik, ale przyjmuje plik równy limitowi", () => {
    const limit = 200 * 1024 * 1024;
    expect(validateModelFile(file("model.pkl", limit))).toBeNull();
    expect(validateModelFile(file("model.pkl", limit + 1))).toBe("Plik jest za duży (maksymalnie 200 MB)");
  });
});

describe("formatBytes", () => {
  it("formatuje rozmiary w jednostkach", () => {
    expect(formatBytes(0)).toBe("0 B");
    expect(formatBytes(512)).toBe("512 B");
    expect(formatBytes(1024)).toBe("1.0 KB");
    expect(formatBytes(1536)).toBe("1.5 KB");
    expect(formatBytes(3 * 1024 * 1024)).toBe("3.0 MB");
    expect(formatBytes(5 * 1024 ** 3)).toBe("5.0 GB");
  });

  it("brak wartości pokazuje jako myślnik", () => {
    expect(formatBytes(null)).toBe("—");
    expect(formatBytes(undefined)).toBe("—");
  });
});
