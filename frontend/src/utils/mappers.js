export const EMPTY_VALUES = {
  name: "",
  description: "",
  framework: "",
  task: "",
  version: "",
  accuracy: "",
  size_mb: "",
  status: "draft",
};

// Model z API -> wartości pól formularza (same teksty)
export function toFormValues(model) {
  return {
    name: model.name ?? "",
    description: model.description ?? "",
    framework: model.framework ?? "",
    task: model.task ?? "",
    version: model.version ?? "",
    accuracy: model.accuracy == null ? "" : String(model.accuracy),
    size_mb: model.size_mb == null ? "" : String(model.size_mb),
    status: model.status ?? "draft",
  };
}

function toNumberOrNull(value) {
  const text = String(value).trim().replace(",", ".");
  if (text === "") return null;
  const number = Number(text);
  // Niepoprawny tekst wysyłamy bez zmian, żeby serwer zwrócił błąd walidacji
  return Number.isNaN(number) ? text : number;
}

// Wartości formularza -> dane wysyłane do API
export function toPayload(values) {
  return {
    name: values.name.trim(),
    description: values.description.trim() || null,
    framework: values.framework,
    task: values.task.trim(),
    version: values.version.trim(),
    accuracy: toNumberOrNull(values.accuracy),
    size_mb: toNumberOrNull(values.size_mb),
    status: values.status,
  };
}
