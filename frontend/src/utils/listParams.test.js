import { describe, expect, it } from "vitest";
import { hasActiveFilters, parseListParams, toApiQuery, toUrlParams } from "./listParams";

const parse = (query) => parseListParams(new URLSearchParams(query));

describe("parseListParams", () => {
  it("zwraca wartości domyślne dla pustego adresu", () => {
    expect(parse("")).toEqual({
      search: "",
      framework: "",
      status: "",
      sort: "created_at:desc",
      page: 1,
      pageSize: 10,
    });
  });

  it("odczytuje poprawne parametry", () => {
    expect(parse("q=iris&framework=ONNX&status=draft&sort=name:asc&page=3&size=25")).toEqual({
      search: "iris",
      framework: "ONNX",
      status: "draft",
      sort: "name:asc",
      page: 3,
      pageSize: 25,
    });
  });

  it("zastępuje błędne wartości domyślnymi", () => {
    const params = parse("framework=Nieznany&status=x&sort=password:asc&page=-2&size=7");
    expect(params).toMatchObject({ framework: "", status: "", sort: "created_at:desc", page: 1, pageSize: 10 });
    expect(parse("page=abc").page).toBe(1);
    expect(parse("page=0").page).toBe(1);
  });

  it("przycina spacje i zbyt długie wyszukiwanie", () => {
    expect(parse("q=%20iris%20").search).toBe("iris");
    expect(parse(`q=${"a".repeat(150)}`).search).toHaveLength(100);
  });
});

describe("toUrlParams", () => {
  it("pomija wartości domyślne", () => {
    expect(toUrlParams(parse("")).toString()).toBe("");
    expect(toUrlParams({ ...parse(""), page: 1 }).toString()).toBe("");
  });

  it("zachowuje wybrane parametry (odczyt i zapis są odwracalne)", () => {
    const original = "q=iris&framework=ONNX&status=draft&sort=name%3Aasc&page=3&size=25";
    const roundTrip = toUrlParams(parse(original));
    expect(parse(roundTrip.toString())).toEqual(parse(original));
  });
});

describe("toApiQuery", () => {
  it("zawsze wysyła sortowanie i paginację", () => {
    expect(toApiQuery(parse(""))).toBe("sort=created_at&order=desc&page=1&page_size=10");
  });

  it("dodaje filtry i koduje znaki specjalne", () => {
    const query = new URLSearchParams(toApiQuery({ ...parse("framework=ONNX&sort=name:asc&page=2"), search: "100% zażółć" }));
    expect(query.get("search")).toBe("100% zażółć");
    expect(query.get("framework")).toBe("ONNX");
    expect(query.get("sort")).toBe("name");
    expect(query.get("order")).toBe("asc");
    expect(query.get("page")).toBe("2");
  });

  it("nie wysyła pustych filtrów", () => {
    const query = new URLSearchParams(toApiQuery(parse("")));
    expect(query.has("search") || query.has("framework") || query.has("status")).toBe(false);
  });
});

describe("hasActiveFilters", () => {
  it("rozpoznaje aktywne filtry", () => {
    expect(hasActiveFilters(parse(""))).toBe(false);
    expect(hasActiveFilters(parse("sort=name:asc&page=2"))).toBe(false);
    expect(hasActiveFilters(parse("q=iris"))).toBe(true);
    expect(hasActiveFilters(parse("status=draft"))).toBe(true);
  });
});
