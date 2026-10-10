const API_URL = import.meta.env.VITE_API_URL ?? "/api";

export const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";

export class ApiError extends Error {
  constructor(message, { status = 0, fieldErrors = [] } = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.fieldErrors = fieldErrors;
  }
}

function messageForStatus(status) {
  if (status === 400) return "Nieprawidłowe dane.";
  if (status === 404) return "Nie znaleziono zasobu.";
  if (status >= 500) return "Błąd serwera. Spróbuj ponownie później.";
  return `Nieoczekiwany błąd (kod ${status}).`;
}

// Jedyne miejsce wykonujące zapytania HTTP do back-endu
export async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...options,
      headers: options.body ? { "Content-Type": "application/json" } : undefined,
    });
  } catch {
    throw new ApiError("Brak połączenia z serwerem. Sprawdź sieć i spróbuj ponownie.");
  }

  if (response.status === 204) return null;

  let data = null;
  try {
    data = await response.json();
  } catch {
    // odpowiedź bez treści JSON
  }

  if (!response.ok) {
    throw new ApiError(data?.detail ?? messageForStatus(response.status), {
      status: response.status,
      fieldErrors: data?.errors ?? [],
    });
  }
  return data;
}
