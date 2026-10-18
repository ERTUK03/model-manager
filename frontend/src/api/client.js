import { tokenStore } from "../auth/tokenStore";

const API_URL = import.meta.env.VITE_API_URL ?? "/api";

// Zdarzenie wysyłane, gdy serwer odrzuci token (np. wygasł). Nasłuchuje go AuthContext
export const UNAUTHORIZED_EVENT = "auth:unauthorized";

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
  if (status === 401) return "Sesja wygasła. Zaloguj się ponownie.";
  if (status === 403) return "Brak uprawnień do wykonania tej operacji.";
  if (status === 404) return "Nie znaleziono zasobu.";
  if (status === 409) return "Konflikt danych.";
  if (status >= 500) return "Błąd serwera. Spróbuj ponownie później.";
  return `Nieoczekiwany błąd (kod ${status}).`;
}

// Jedyne miejsce wykonujące zapytania HTTP do back-endu.
// Opcja auth: false pomija nagłówek z tokenem (logowanie i rejestracja).
export async function request(path, { auth = true, ...options } = {}) {
  const headers = {};
  if (options.body) headers["Content-Type"] = "application/json";
  const token = auth ? tokenStore.get() : null;
  if (token) headers.Authorization = `Bearer ${token}`;

  let response;
  try {
    response = await fetch(`${API_URL}${path}`, { ...options, headers });
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
    if (response.status === 401 && token) {
      tokenStore.clear();
      window.dispatchEvent(new Event(UNAUTHORIZED_EVENT));
    }
    throw new ApiError(data?.detail ?? messageForStatus(response.status), {
      status: response.status,
      fieldErrors: data?.errors ?? [],
    });
  }
  return data;
}
