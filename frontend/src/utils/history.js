import { FIELD_LABELS, STATUS_LABELS } from "../constants";
import { formatAccuracy, formatSize } from "./format";

export function formatChangeValue(field, value) {
  if (value === null || value === undefined || value === "") return "—";
  if (field === "status") return STATUS_LABELS[value] ?? String(value);
  if (field === "accuracy") return formatAccuracy(value);
  if (field === "size_mb") return formatSize(value);
  return String(value);
}

// Zmiany z API ({pole: {from, to}}) -> lista do wyświetlenia, w stałej kolejności pól
export function describeChanges(changes) {
  if (!changes) return [];
  return Object.keys(FIELD_LABELS)
    .filter((field) => field in changes)
    .map((field) => ({
      field,
      label: FIELD_LABELS[field],
      from: formatChangeValue(field, changes[field].from),
      to: formatChangeValue(field, changes[field].to),
    }));
}

export function formatAuthor(email) {
  return email ?? "nieznany użytkownik";
}
