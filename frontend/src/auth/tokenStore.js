const KEY = "model-manager-token";

// Token trzymamy w localStorage, żeby sesja przetrwała odświeżenie strony.
// Każdy dostęp jest w try/catch, bo przeglądarka może blokować localStorage.
export const tokenStore = {
  get() {
    try {
      return localStorage.getItem(KEY);
    } catch {
      return null;
    }
  },
  set(token) {
    try {
      localStorage.setItem(KEY, token);
    } catch {
      // brak dostępu do pamięci przeglądarki
    }
  },
  clear() {
    try {
      localStorage.removeItem(KEY);
    } catch {
      // brak dostępu do pamięci przeglądarki
    }
  },
};
