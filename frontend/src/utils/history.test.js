import { describe, expect, it } from "vitest";
import { describeChanges, formatAuthor, formatChangeValue } from "./history";

describe("formatChangeValue", () => {
  it("formatuje wartości zależnie od pola", () => {
    expect(formatChangeValue("status", "published")).toBe("Opublikowany");
    expect(formatChangeValue("accuracy", 0.95)).toBe("95.0%");
    expect(formatChangeValue("size_mb", 12.5)).toBe("12.5 MB");
    expect(formatChangeValue("version", "1.2.0")).toBe("1.2.0");
  });

  it("puste wartości pokazuje jako myślnik", () => {
    expect(formatChangeValue("accuracy", null)).toBe("—");
    expect(formatChangeValue("description", "")).toBe("—");
    expect(formatChangeValue("task", undefined)).toBe("—");
  });

  it("nieznany status wyświetla bez zmian", () => {
    expect(formatChangeValue("status", "inny")).toBe("inny");
  });
});

describe("describeChanges", () => {
  it("zwraca zmiany w stałej kolejności pól z czytelnymi etykietami", () => {
    const result = describeChanges({
      status: { from: "draft", to: "published" },
      version: { from: "1.0.0", to: "1.1.0" },
      name: { from: "iris", to: "iris-v2" },
    });
    expect(result.map((c) => c.label)).toEqual(["Nazwa", "Wersja", "Status"]);
    expect(result[2]).toMatchObject({ from: "Szkic", to: "Opublikowany" });
  });

  it("opisuje dodanie, zamianę i usunięcie pliku", () => {
    const [added] = describeChanges({ file_name: { from: null, to: "model.pkl" } });
    expect(added).toMatchObject({ label: "Plik", from: "—", to: "model.pkl" });
    const [removed] = describeChanges({ file_name: { from: "model.pkl", to: null } });
    expect(removed).toMatchObject({ from: "model.pkl", to: "—" });
  });

  it("pomija nieznane pola i obsługuje brak zmian", () => {
    expect(describeChanges({ hasło: { from: "a", to: "b" } })).toEqual([]);
    expect(describeChanges(null)).toEqual([]);
  });
});

describe("formatAuthor", () => {
  it("podaje adres autora lub komunikat zastępczy", () => {
    expect(formatAuthor("admin@example.com")).toBe("admin@example.com");
    expect(formatAuthor(null)).toBe("nieznany użytkownik");
  });
});
