export function formatAccuracy(value) {
  return typeof value === "number" ? `${(value * 100).toFixed(1)}%` : "—";
}

export function formatSize(value) {
  return typeof value === "number" ? `${value} MB` : "—";
}

export function formatDate(value) {
  if (!value) return "—";
  return new Date(value).toLocaleString("pl-PL", { dateStyle: "medium", timeStyle: "short" });
}
