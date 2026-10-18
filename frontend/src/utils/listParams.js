import { FRAMEWORKS, STATUSES } from "../constants";

export const PAGE_SIZES = [10, 25, 50];
export const DEFAULT_PAGE_SIZE = 10;
export const DEFAULT_SORT = "created_at:desc";

export const SORT_OPTIONS = [
  { value: "created_at:desc", label: "Najnowsze" },
  { value: "created_at:asc", label: "Najstarsze" },
  { value: "updated_at:desc", label: "Ostatnio zmienione" },
  { value: "name:asc", label: "Nazwa A–Z" },
  { value: "name:desc", label: "Nazwa Z–A" },
  { value: "accuracy:desc", label: "Dokładność: od najwyższej" },
  { value: "accuracy:asc", label: "Dokładność: od najniższej" },
];

function positiveInt(value, fallback) {
  const number = Number.parseInt(value, 10);
  return Number.isInteger(number) && number >= 1 ? number : fallback;
}

// Adres strony -> parametry listy. Błędne wartości z paska adresu zastępujemy domyślnymi
export function parseListParams(searchParams) {
  const framework = searchParams.get("framework");
  const status = searchParams.get("status");
  const sort = searchParams.get("sort");
  const size = positiveInt(searchParams.get("size"), DEFAULT_PAGE_SIZE);
  return {
    search: (searchParams.get("q") ?? "").trim().slice(0, 100),
    framework: FRAMEWORKS.includes(framework) ? framework : "",
    status: STATUSES.includes(status) ? status : "",
    sort: SORT_OPTIONS.some((option) => option.value === sort) ? sort : DEFAULT_SORT,
    page: positiveInt(searchParams.get("page"), 1),
    pageSize: PAGE_SIZES.includes(size) ? size : DEFAULT_PAGE_SIZE,
  };
}

// Parametry listy -> adres strony (bez wartości domyślnych, żeby adres był krótki)
export function toUrlParams(params) {
  const url = new URLSearchParams();
  if (params.search) url.set("q", params.search);
  if (params.framework) url.set("framework", params.framework);
  if (params.status) url.set("status", params.status);
  if (params.sort !== DEFAULT_SORT) url.set("sort", params.sort);
  if (params.page > 1) url.set("page", String(params.page));
  if (params.pageSize !== DEFAULT_PAGE_SIZE) url.set("size", String(params.pageSize));
  return url;
}

// Parametry listy -> zapytanie do API (nazwy zgodne z backend/app/schemas/ml_model.py)
export function toApiQuery(params) {
  const [sort, order] = params.sort.split(":");
  const query = new URLSearchParams({ sort, order, page: String(params.page), page_size: String(params.pageSize) });
  if (params.search) query.set("search", params.search);
  if (params.framework) query.set("framework", params.framework);
  if (params.status) query.set("status", params.status);
  return query.toString();
}

export function hasActiveFilters(params) {
  return Boolean(params.search || params.framework || params.status);
}
