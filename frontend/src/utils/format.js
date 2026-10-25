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

export function formatBytes(bytes) {
  if (typeof bytes !== "number") return "—";
  const units = ["B", "KB", "MB", "GB"];
  let value = bytes;
  let unit = 0;
  while (value >= 1024 && unit < units.length - 1) {
    value /= 1024;
    unit += 1;
  }
  return unit === 0 ? `${value} B` : `${value.toFixed(1)} ${units[unit]}`;
}

// Pełny skrót commita (40 znaków) skracamy do 7, inne wartości (np. "dev") zostają bez zmian
export function shortVersion(version) {
  return /^[0-9a-f]{40}$/i.test(version) ? version.slice(0, 7) : version;
}
